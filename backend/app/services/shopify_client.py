import logging
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log, RetryError

from app.core.config import settings
from app.utils.exceptions import ShopifyError, ShopifyRateLimitError, ShopifyAuthError, ShopifyNetworkError

# Configure structured logging
logger = logging.getLogger("shopify_client")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ShopifyClient:
    """
    Async client for Shopify Admin REST API.
    Handles authentication, rate limiting, and pagination.
    """

    def __init__(self):
        self.base_url = f"https://{settings.SHOPIFY_STORE_URL}/admin/api/{settings.SHOPIFY_API_VERSION}"
        self.headers = {
            "X-Shopify-Access-Token": settings.SHOPIFY_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=10.0)

    async def close(self):
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=32),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True  # Ensure the underlying exception is raised after retries exhaustion
    )
    async def _make_request(self, url: str, params: Optional[Dict] = None) -> httpx.Response:
        """
        Internal method to make requests with retries.
        """
        try:
            response = await self.client.get(url, params=params)
            
            if response.status_code == 401 or response.status_code == 403:
                raise ShopifyAuthError(f"Authentication failed: {response.text}")
            
            if response.status_code == 429:
                # 429 is handled by retry decorator
                logger.warning("Rate limit hit, retrying...")
                response.raise_for_status()

            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                 # This will be retried by tenacity
                 raise e
            logger.error(f"HTTP error occurred: {e}")
            raise ShopifyError(f"HTTP Error: {e}")
        except httpx.RequestError as e:
            logger.error(f"Network error occurred: {e}")
            raise ShopifyNetworkError(f"Network Error: {e}")

    async def get_resource(self, resource: str, params: Optional[Dict] = None, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch all records for a resource with pagination.
        
        Args:
            resource: 'orders', 'products', or 'customers'
            params: Query parameters (e.g., limit, status)
            max_pages: Maximum number of pages to fetch (default: 10)
        
        Returns:
            List[Dict]: Flattened list of all records.
        """
        url = f"{self.base_url}/{resource}.json"
        all_results = []
        page_count = 0
        current_url = url
        current_params = params or {}
        
        # Ensure limit is set
        if 'limit' not in current_params:
            current_params['limit'] = 250
            
        # FORCE 'status=any' for orders to capture Open, Closed, and Cancelled
        if resource == 'orders' and 'status' not in current_params:
            logger.info("Enforcing status='any' for orders to fetch correct revenue.")
            current_params['status'] = 'any'

        while current_url and page_count < max_pages:
            page_count += 1
            logger.info(f"Fetching page {page_count} of {resource}")
            
            try:
                # If we have a direct link URL (next page), params are built-in
                if page_count > 1:
                    response = await self._make_request(current_url)
                else:
                     response = await self._make_request(current_url, params=current_params)

                data = response.json()
                
                # Extract list from wrapper key (e.g. {'orders': [...]})
                if resource in data:
                     all_results.extend(data[resource])
                else:
                    # Fallback or error if structure is unexpected
                    logger.warning(f"Unexpected response structure for {resource}")
                
                # Parse Link header for pagination
                link_header = response.headers.get("Link")
                next_link = None
                
                if link_header:
                    links = link_header.split(',')
                    for link in links:
                        if 'rel="next"' in link:
                            # Format: <https://...>; rel="next"
                            next_link = link.split(';')[0].strip('<> ')
                            break
                
                if next_link:
                    logger.info(f"DEBUG: Found next page link: {next_link}")
                else:
                    logger.info("DEBUG: No next page link found.")
                    
                current_url = next_link
                
                if not current_url:
                    break
                    
            except httpx.HTTPStatusError as e:
                # ... existing error handling ...
                if e.response.status_code == 429:
                    raise ShopifyRateLimitError(f"Rate limit exceeded after max retries: {e}")
                raise ShopifyError(f"Shopify API Error: {e}")
            except Exception as e:
                logger.error(f"Failed to fetch page {page_count} of {resource}: {e}")
                raise

        # Deduplicate results by ID to prevent overlap/duplicates
        logger.info(f"DEBUG: Pre-dedup count: {len(all_results)}")
        if all_results and 'id' in all_results[0]:
            unique_results = {str(item['id']): item for item in all_results}
            deduped_list = list(unique_results.values())
            logger.info(f"DEBUG: Fetched {len(all_results)} raw records. Deduped to: {len(deduped_list)} unique records.")
            return deduped_list
            
        return all_results
