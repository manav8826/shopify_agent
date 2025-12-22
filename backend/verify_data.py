# Create: backend/scripts/verify_data.py

import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SHOP_NAME = os.getenv("SHOPIFY_SHOP_NAME")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2025-04")

def verify_orders_last_7_days():
    """Verify the order count for last 7 days"""
    
    # Calculate date range
    today = datetime(2025, 12, 21)
    
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }
    params = {
        "limit": 250,
        "status": "any"
    }
    
    print(f"\n🔍 Connecting to Shopify Store: {SHOP_NAME}...")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        orders = response.json()["orders"]
        total_revenue = sum(float(order["total_price"]) for order in orders)
        
        print(f"✅ TRUTH DATA (From Shopify API directly):")
        print(f"   Total Orders (All Time): {len(orders)}")
        print(f"   Total Revenue: ${total_revenue:.2f}")
        print(f"\n   (Use this number to verify the Agent's response)")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    verify_orders_last_7_days()