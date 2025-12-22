import pytest
import respx
import httpx
from httpx import Response
from app.tools.shopify_tool import GetShopifyDataTool
from app.core.config import settings

# Mock Settings to ensure tests run without real env vars
settings.SHOPIFY_STORE_URL = "test-store.myshopify.com"
settings.SHOPIFY_ACCESS_TOKEN = "test-token"
settings.SHOPIFY_API_VERSION = "2025-07"

@pytest.fixture
def shopify_tool():
    return GetShopifyDataTool()

@pytest.mark.asyncio
async def test_get_resource_success(shopify_tool):
    async with respx.mock(base_url="https://test-store.myshopify.com/admin/api/2025-07") as respx_mock:
        # Match with default limit
        respx_mock.get("/products.json", params={"limit": 50}).mock(return_value=Response(200, json={"products": [{"id": 1, "title": "Test Product"}]}))
        
        result = await shopify_tool._arun(resource="products")
        
        assert len(result) == 1
        assert result[0]["title"] == "Test Product"

@pytest.mark.asyncio
async def test_pagination(shopify_tool):
    async with respx.mock(base_url="https://test-store.myshopify.com/admin/api/2025-07") as respx_mock:
        # Page 1
        respx_mock.get("/orders.json", params={"limit": 10}).mock(return_value=Response(
            200, 
            json={"orders": [{"id": 1}]},
            headers={"Link": '<https://test-store.myshopify.com/admin/api/2025-07/orders.json?page_info=2>; rel="next"'}
        ))
        
        # Page 2
        respx_mock.get("/orders.json", params={"page_info": "2"}).mock(return_value=Response(
            200, 
            json={"orders": [{"id": 2}]}
        ))
        
        result = await shopify_tool._arun(resource="orders", limit=10)
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

@pytest.mark.asyncio
async def test_rate_limit_retry(shopify_tool):
    async with respx.mock(base_url="https://test-store.myshopify.com/admin/api/2025-07") as respx_mock:
        # Fail twice with 429, then succeed
        route = respx_mock.get("/customers.json", params={"limit": 50})
        route.side_effect = [
            Response(429),
            Response(429),
            Response(200, json={"customers": [{"id": 1}]})
        ]
        
        result = await shopify_tool._arun(resource="customers")
        
        assert len(result) == 1
        # Should have called it 3 times total
        assert route.call_count == 3

@pytest.mark.asyncio
async def test_rate_limit_max_retries_exceeded(shopify_tool):
    async with respx.mock(base_url="https://test-store.myshopify.com/admin/api/2025-07") as respx_mock:
        # Always fail 429
        respx_mock.get("/products.json", params={"limit": 50}).mock(return_value=Response(429))
        
        result = await shopify_tool._arun(resource="products")
        
        # Tool catches ShopifyRateLimitError and returns string error
        assert "Shopify Error" in result
        assert "429" in result or "Rate limit" in result

@pytest.mark.asyncio
async def test_invalid_resource(shopify_tool):
    result = await shopify_tool._arun(resource="invalid_resource")
    assert "Error: Resource 'invalid_resource' is not supported" in result

@pytest.mark.asyncio
async def test_network_error(shopify_tool):
    async with respx.mock(base_url="https://test-store.myshopify.com/admin/api/2025-07") as respx_mock:
        respx_mock.get("/orders.json", params={"limit": 50}).mock(side_effect=httpx.ConnectError("Connection failed"))
        
        result = await shopify_tool._arun(resource="orders")
        assert "Unexpected Error" in result or "Network Error" in result

@pytest.mark.asyncio
async def test_auth_error(shopify_tool):
    async with respx.mock(base_url="https://test-store.myshopify.com/admin/api/2025-07") as respx_mock:
        respx_mock.get("/orders.json", params={"limit": 50}).mock(return_value=Response(401, text="Unauthorized"))
        
        result = await shopify_tool._arun(resource="orders")
        assert "Shopify Error" in result
        assert "Authentication failed" in result
