import json
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

# Load the JSON files
import os
print(f"DEBUG: CWD is {os.getcwd()}")
clean_path = os.path.abspath('clean_orders.json')
print(f"DEBUG: Reading from {clean_path}")

with open('store_products.json', 'r') as f:
    products_data = json.load(f)

with open('clean_orders.json', 'r') as f:
    orders_data = json.load(f)
print("DEBUG: Successfully loaded clean_orders.json")

# with open('store_customers.json', 'r') as f:
#     customers_data = json.load(f)
customers_list = [] # Hack to avoid needing customers file update for now

products_list = products_data.get('products', [])
orders_list = orders_data.get('orders', [])
# customers_list is already []

# Deduplicate Orders by ID (Matching Agent Logic)
orders_dict = {o['id']: o for o in orders_list}
orders = list(orders_dict.values())

# Deduplicate Products just in case
products_dict = {p['id']: p for p in products_list}
products = list(products_dict.values())

customers_dict = {c['id']: c for c in customers_list}
customers = list(customers_dict.values())

print(f"DEBUG: Loaded {len(orders_list)} raw orders -> {len(orders)} unique orders.")

# Set today's date (as per assignment)
TODAY = datetime(2025, 12, 21)

print("=" * 60)
print("SHOPIFY STORE DATA VERIFICATION - EXPECTED ANSWERS")
print("=" * 60)

# TEST 1: Orders last 7 days
print("\n1. How many orders did we get in the last 7 days?")
seven_days_ago = TODAY - timedelta(days=7)
recent_orders = [o for o in orders if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).replace(tzinfo=None) >= seven_days_ago]
total_revenue = sum(float(o['total_price']) for o in recent_orders)
aov = total_revenue / len(recent_orders) if recent_orders else 0
print(f"ANSWER: {len(recent_orders)} orders")
print(f"Revenue: ${total_revenue:.2f}")
print(f"AOV: ${aov:.2f}")
print(f"Date Range: {seven_days_ago.date()} to {TODAY.date()}")

# TEST 2: Top 5 selling products
print("\n2. What are our top 5 selling products?")
product_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0, 'name': ''})
for order in orders:
    for item in order.get('line_items', []):
        try:
            price = float(item.get('price', 0))
        except (ValueError, TypeError):
            price = 0.0
            
        quantity = int(item.get('quantity', 0))
        revenue = price * quantity
        
        # Use TITLE as the key because product_id is often null in this dataset
        title = item.get('title', 'Unknown')
        
        product_sales[title]['revenue'] += revenue
        product_sales[title]['quantity'] += quantity
        product_sales[title]['name'] = title #Redundant but consistent

# Sort by REVENUE to match Agent behavior (User asked for "by revenue")
top_products = sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:5]
print("ANSWER:")
for i, (pid, data) in enumerate(top_products, 1):
    print(f"{i}. {data['name']}: {data['quantity']} units, ${data['revenue']:.2f} revenue")

# TEST 3: Revenue by city
print("\n3. Show revenue by city")
city_revenue = defaultdict(float)
for order in orders:
    city = order.get('billing_address', {}).get('city', 'Unknown') if order.get('billing_address') else 'Unknown'
    city_revenue[city] += float(order.get('total_price', 0))

sorted_cities = sorted(city_revenue.items(), key=lambda x: x[1], reverse=True)
print("ANSWER:")
for city, revenue in sorted_cities[:5]:
    print(f"- {city}: ${revenue:.2f}")

# TEST 4: Repeat customers
print("\n4. Who are my repeat customers?")
customer_orders = defaultdict(int)
for order in orders:
    cid = order.get('customer', {}).get('id') if order.get('customer') else None
    if cid:
        customer_orders[cid] += 1

repeat_customers = [(cid, count) for cid, count in customer_orders.items() if count >= 2]
print(f"ANSWER: {len(repeat_customers)} repeat customers")
for cid, count in sorted(repeat_customers, key=lambda x: x[1], reverse=True)[:5]:
    customer = next((c for c in customers if c['id'] == cid), None)
    name = f"{customer['first_name']} {customer['last_name']}" if customer else "Unknown"
    print(f"- {name}: {count} orders")

# TEST 5: AOV
print("\n5. What is our Average Order Value (AOV)?")
total_revenue_all = sum(float(o['total_price']) for o in orders)
total_orders = len(orders)
aov_all = total_revenue_all / total_orders if total_orders else 0
print(f"ANSWER: ${aov_all:.2f}")
print(f"(Total Revenue: ${total_revenue_all:.2f} / {total_orders} orders)")

# TEST 6: Total products
print("\n6. How many products do we have in total?")
print(f"ANSWER: {len(products)} products")

# TEST 7: Nonexistent product
print("\n7. Orders for product 'NonexistentItem12345'")
print("ANSWER: 0 orders (product doesn't exist)")

# TEST 8: Total revenue
print("\n8. What's our total revenue?")
print(f"ANSWER: ${total_revenue_all:.2f}")

# TEST 9: Orders this month
print("\n9. How many orders this month (December)?")
dec_orders = [o for o in orders if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).month == 12 
              and datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).year == 2025]
print(f"ANSWER: {len(dec_orders)} orders in December 2025")

# TEST 10: Top revenue city
print("\n10. Which city generates the highest revenue?")
if sorted_cities:
    top_city, top_revenue = sorted_cities[0]
    print(f"ANSWER: {top_city} with ${top_revenue:.2f}")

# Save detailed report
report = {
    "test_date": TODAY.isoformat(),
    "test_1_orders_last_7_days": {
        "count": len(recent_orders),
        "revenue": f"${total_revenue:.2f}",
        "aov": f"${aov:.2f}"
    },
    "test_2_top_products": [{"name": data['name'], "quantity": data['quantity'], "revenue": f"${data['revenue']:.2f}"} 
                            for _, data in top_products],
    "test_3_revenue_by_city": {city: f"${revenue:.2f}" for city, revenue in sorted_cities},
    "test_4_repeat_customers": len(repeat_customers),
    "test_5_aov": f"${aov_all:.2f}",
    "test_6_total_products": len(products),
    "test_8_total_revenue": f"${total_revenue_all:.2f}",
    "test_9_december_orders": len(dec_orders),
    "test_10_top_city": f"{sorted_cities[0][0]}: ${sorted_cities[0][1]:.2f}" if sorted_cities else "N/A"
}

with open('expected_test_answers.json', 'w') as f:
    json.dump(report, f, indent=2)

print("\n" + "=" * 60)
print("✅ Expected answers saved to: expected_test_answers.json")
print("=" * 60)
