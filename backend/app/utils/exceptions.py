class ShopifyError(Exception):
    """Base exception for Shopify API errors."""
    pass

class ShopifyAuthError(ShopifyError):
    """Raised when authentication fails (401/403)."""
    pass

class ShopifyRateLimitError(ShopifyError):
    """Raised when rate limits are exceeded after retries."""
    pass

class ShopifyNetworkError(ShopifyError):
    """Raised when network connection fails."""
    pass
