import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from collections import defaultdict
from app.services.shopify_client import ShopifyClient

async def debug_lines():
    client = ShopifyClient()
    try:
        print("Fetching orders (limit=250, status=any)...")
        orders = await client.get_resource("orders", params={"limit": 250, "status": "any"})
        
        print(f"Fetched {len(orders)} orders.")
        
        total_rev = 0.0
        line_item_rev = 0.0
        product_revs = defaultdict(float)
        
        missing_lines = 0
        
        for o in orders:
            o_rev = float(o.get('total_price', 0))
            total_rev += o_rev
            
            lines = o.get('line_items', [])
            if not lines and o_rev > 0:
                print(f"WARNING: Order {o['id']} has ${o_rev} revenue but NO line items!")
                missing_lines += 1
            
            l_rev = 0.0
            for l in lines:
                l_price = float(l.get('price', 0))
                l_qty = int(l.get('quantity', 0))
                l_line_rev = l_price * l_qty
                l_rev += l_line_rev
                
                title = l.get('title', 'Unknown')
                product_revs[title] += l_line_rev
                
            line_item_rev += l_rev
            
        print(f"Total Order Revenue (sum of total_price): ${total_rev:,.2f}")
        print(f"Total Line Item Revenue (sum of price*qty): ${line_item_rev:,.2f}")
        print(f"Orders with missing line items: {missing_lines}")
        
        print("\n--- TOP 5 PRODUCTS (Live Fetch) ---")
        sorted_products = sorted(product_revs.items(), key=lambda x: x[1], reverse=True)[:5]
        for idx, (p, r) in enumerate(sorted_products, 1):
            print(f"{idx}. {p}: ${r:,.2f}")
            
        # SAVE SNAPSHOT for verify_test_cases.py
        import json
        with open('clean_orders.json', 'w') as f:
            json.dump({"orders": orders}, f, indent=2)
        print("\n✅ Saved clean snapshot to clean_orders.json")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(debug_lines())
