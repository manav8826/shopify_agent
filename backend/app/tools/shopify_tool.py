from typing import Optional, Type, List, Dict, Any, ClassVar
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.services.shopify_client import ShopifyClient
from app.utils.exceptions import ShopifyError

class GetShopifyDataInput(BaseModel):
    """Input model for get_shopify_data."""
    resource: str = Field(
        ..., 
        description="The resource to fetch. Must be one of: 'orders', 'products', 'customers'."
    )
    limit: int = Field(
        50, 
        ge=1, 
        le=250, 
        description="Number of results to return per page. Max 250."
    )
    filters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Dictionary of filter parameters (e.g., {'status': 'open'})."
    )

class GetShopifyDataTool(BaseTool):
    """
    Tool for fetching data from Shopify Admin REST API via GET requests.
    Supports 'orders', 'products', and 'customers'.
    Handles pagination and rate limiting automatically.
    """
    name: str = "get_shopify_data"
    description: str = (
        "Useful for retrieving data from a Shopify store. "
        "Inputs: resource (orders/products/customers), limit (max 250), filters (dict). "
        "Returns a list of records."
    )
    args_schema: Type[BaseModel] = GetShopifyDataInput
    
    # Allowed resources whitelist
    ALLOWED_RESOURCES: ClassVar[set] = {'orders', 'products', 'customers'}

    def _run(self, resource: str, limit: int = 50, filters: Optional[Dict[str, Any]] = None) -> Any:
        """Synchronous run not implemented (async only)."""
        raise NotImplementedError("Use run_async instead.")

    async def _arun(
        self, 
        resource: str, 
        limit: int = 50, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute the Shopify API request asynchronously.
        """
        # 1. Validate Resource
        if resource not in self.ALLOWED_RESOURCES:
            return f"Error: Resource '{resource}' is not supported. Allowed: {', '.join(self.ALLOWED_RESOURCES)}"

        # 2. Sanitize Filters (Simple pass-through for now, but good hook for validation)
        params = filters or {}
        params['limit'] = limit

        client = ShopifyClient()
        try:
            results = await client.get_resource(resource, params=params)
            return results
        except ShopifyError as e:
            return f"Shopify Error: {str(e)}"
        except Exception as e:
            return f"Unexpected Error: {str(e)}"
        finally:
            await client.close()
