import pytest
import pandas as pd
from datetime import datetime, timedelta
import pytz
from app.services.shopify_service import ShopifyService

@pytest.fixture
def sample_orders():
    # Helper to create timezone-aware timestamp
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
            "created_at": now_minus(10), # 10 days ago (older)
            "total_price": "200.00",
            "customer": {"id": 101, "email": "alice@test.com"}, # Repeat customer
            "billing_address": {"city": "New York"},
            "line_items": [
                {"title": "Product A", "quantity": 1, "price": "100.00"},
                {"title": "Product C", "quantity": 1, "price": "100.00"}
            ]
        }
    ]

def test_parse_orders_data(sample_orders):
    df = ShopifyService.parse_orders_data(sample_orders)
    
    assert not df.empty
    assert len(df) == 3
    assert 'email' in df.columns
    assert df.iloc[0]['city'] == "New York"
    assert df.iloc[0]['total_price'] == 100.0

def test_parse_orders_empty():
    df = ShopifyService.parse_orders_data([])
    assert df.empty

def test_calculate_aov_all_time(sample_orders):
    df = ShopifyService.parse_orders_data(sample_orders)
    result = ShopifyService.calculate_aov(df)
    
    # Total: 100+50+200 = 350. Count: 3. AOV = 116.67
    assert "$116.67" in result

def test_calculate_aov_filtered(sample_orders):
    df = ShopifyService.parse_orders_data(sample_orders)
    # Last 7 days includes orders 1 and 2 (150 total / 2 orders) = 75.00
    # Order 3 is 10 days old
    result = ShopifyService.calculate_aov(df, days=7)
    
    assert "$75.00" in result
    assert "last 7 days" in result

def test_calculate_aov_empty():
    result = ShopifyService.calculate_aov(pd.DataFrame())
    assert "No order data" in result

def test_get_top_products(sample_orders):
    df = ShopifyService.parse_orders_data(sample_orders)
    result = ShopifyService.get_top_products(df)
    
    # Product A: 1 (Order 1) + 1 (Order 3) = 2
    # Product B: 2 (Order 2) = 2
    # Product C: 1 (Order 3) = 1
    # Sorting: Top might be A or B depending on secondary sort or stable sort, 
    # but "Product A" and "Product B" should be top.
    
    assert "Product A" in result
    assert "Product B" in result
    # Only A and B have 2 units. C has 1.
    
def test_analyze_revenue_by_city(sample_orders):
    df = ShopifyService.parse_orders_data(sample_orders)
    result = ShopifyService.analyze_revenue_by_city(df)
    
    # NY: 100 + 200 = 300
    # Chicago: 50
    assert "New York" in result
    assert "$300.00" in result
    assert "Chicago" in result
    assert "$50.00" in result

def test_find_repeat_customers(sample_orders):
    df = ShopifyService.parse_orders_data(sample_orders)
    result = ShopifyService.find_repeat_customers(df)
    
    # Alice (id 101) appears twice
    assert "Found **1** repeat customers" in result

def test_find_repeat_customers_none(sample_orders):
    # Keep only order 1 and 2 (different customers)
    df = ShopifyService.parse_orders_data(sample_orders[:2])
    result = ShopifyService.find_repeat_customers(df)
    
    assert "Found **0** repeat customers" in result
