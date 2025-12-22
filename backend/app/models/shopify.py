from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ShopifyResource(BaseModel):
    """Base model for Shopify resources."""
    id: int
    created_at: str

class Order(ShopifyResource):
    order_number: int
    total_price: str
    currency: str
    processed_at: Optional[str] = None
    customer: Optional[Dict[str, Any]] = None
    line_items: List[Dict[str, Any]] = []

class Product(ShopifyResource):
    title: str
    vendor: str
    product_type: str
    status: str
    variants: List[Dict[str, Any]] = []

class Customer(ShopifyResource):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    orders_count: int = 0
    total_spent: str = "0.00"
