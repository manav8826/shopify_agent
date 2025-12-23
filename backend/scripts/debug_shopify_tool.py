import asyncio
import sys
import os

# Add backend to path so imports work
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.shopify_client import ShopifyClient

async def debug_tool():
    print("Initializing ShopifyClient...")
    client = ShopifyClient()
    
    try:
        print("Fetching orders (limit=250)...")
        # Simulate exactly what the agent does: no status filter initially, relying on our new default
        results = await client.get_resource("orders", params={"limit": 250})
        
        print(f"\n--- RESULTS ---")
        print(f"Total count returned: {len(results)}")
        
        if results:
            # Check unique IDs
            ids = [r['id'] for r in results]
            unique_ids = set(ids)
            print(f"Unique IDs: {len(unique_ids)}")
            
            # Calculate Revenue
            total_revenue = sum(float(o.get('total_price', 0)) for o in results)
            print(f"Calculated Revenue: ${total_revenue:,.2f}")
            
            # First item sample
            print(f"Sample Order ID: {results[0].get('id')}, Price: {results[0].get('total_price')}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(debug_tool())
