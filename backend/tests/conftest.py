import pytest
from datetime import datetime, timedelta
import pytz

@pytest.fixture
def sample_orders_data():
    """
    Shared fixture for sample order data used in analytics and agent tests.
    """
    def now_minus(days):
        return (datetime.utcnow() - timedelta(days=days)).replace(tzinfo=pytz.UTC).isoformat()
        
    return [
        {
            "id": 1,
            "created_at": now_minus(1), # Yesterday
            "total_price": "100.00",
            "customer": {"id": 101, "email": "alice@test.com"},
            "billing_address": {"city": "New York"},
            "line_items": [
                {"title": "Product A", "quantity": 1, "price": "100.00"}
            ]
        },
        {
            "id": 2,
            "created_at": now_minus(5), # 5 days ago
            "total_price": "50.00",
            "customer": {"id": 102, "email": "bob@test.com"},
            "billing_address": {"city": "Chicago"},
            "line_items": [
                {"title": "Product B", "quantity": 2, "price": "25.00"}
            ]
        },
        {
            "id": 3,
            "created_at": now_minus(10), # 10 days ago
            "total_price": "200.00",
            "customer": {"id": 101, "email": "alice@test.com"},
            "billing_address": {"city": "New York"},
            "line_items": [
                {"title": "Product A", "quantity": 1, "price": "100.00"},
                {"title": "Product C", "quantity": 1, "price": "100.00"}
            ]
        }
    ]
