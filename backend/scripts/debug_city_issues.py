import json
import pandas as pd
import os

def debug_city():
    # Load clean snapshot
    with open('clean_orders.json', 'r') as f:
        data = json.load(f)
    
    orders = data['orders']
    print(f"Loaded {len(orders)} orders.")
    
    # Simulate Agent's typical DataFrame creation
    df = pd.DataFrame(orders)
    
    # Check total revenue
    df['total_price'] = df['total_price'].astype(float)
    print(f"Total Revenue (Pandas Sum): ${df['total_price'].sum():,.2f}")
    
    # Simulate extraction of City
    # Strategy 1: The likely naive string extraction agent might try first if flatten isn't perfect
    def get_city_safe(addr):
        if isinstance(addr, dict):
            return addr.get('city', 'Unknown')
        return 'Unknown'

    # Check how billing_address looks
    null_addrs = df['billing_address'].isnull().sum()
    print(f"Orders with null billing_address: {null_addrs}")
    
    # Try the Agent's likely approach
    # Agent usually does: df['billing_address'].apply(lambda x: x.get('city')) if it knows it's a dict
    # But if it's None/NaN, x.get() crashes.
    
    try:
        df['city'] = df['billing_address'].apply(lambda x: x.get('city') if isinstance(x, dict) else 'Unknown')
    except Exception as e:
        print(f"Agent Logic Crash: {e}")
        df['city'] = 'ERROR'

    # Revenue by City
    city_rev = df.groupby('city')['total_price'].sum().sort_values(ascending=False)
    print("\n--- Revenue by City (Simulated) ---")
    print(city_rev)

if __name__ == "__main__":
    debug_city()
