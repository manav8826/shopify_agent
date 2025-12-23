import requests
import json
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

STORE_URL = os.getenv("SHOPIFY_STORE_URL", "https://clevrr-test.myshopify.com")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2025-04"

headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}

def get_data(endpoint):
    if "?" in endpoint:
        path, query = endpoint.split("?", 1)
        url = f"{STORE_URL}/admin/api/{API_VERSION}/{path}.json?{query}"
    else:
        url = f"{STORE_URL}/admin/api/{API_VERSION}/{endpoint}.json"
    
    print(f"Fetching: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# 1. Get all products
print("=== PRODUCTS ===")
products_data = get_data("products")
if products_data:
    products_list = products_data.get('products', [])
    print(f"Total products: {len(products_list)}")
    for p in products_list[:5]:
        print(f"- {p['title']}: ${p['variants'][0]['price']}")

# 2. Get all orders
print("\n=== ORDERS ===")
orders_data = get_data("orders?status=any&limit=250")
orders = orders_data.get('orders', []) if orders_data else []
if orders:
    print(f"Total orders: {len(orders)}")
    
    if orders:
        first_order = orders[0]
        if 'line_items' in first_order and first_order['line_items']:
            print(f"Sample Item Title (Order 1): {first_order['line_items'][0].get('title')}")
            
    total_revenue = sum(float(o['total_price']) for o in orders)
    print(f"Total revenue: ${total_revenue:.2f}")

# 3. Get all customers
print("\n=== CUSTOMERS ===")
customers_data = get_data("customers")
customers = customers_data.get('customers', []) if customers_data else []
if customers:
    print(f"Total customers: {len(customers)}")

# 4. Save full data to JSON files
with open('store_products.json', 'w') as f:
    json.dump(products_data, f, indent=2)
with open('store_orders.json', 'w') as f:
    json.dump(orders_data, f, indent=2)
with open('store_customers.json', 'w') as f:
    json.dump(customers_data, f, indent=2)

print("\n✅ Full data saved to JSON files")
