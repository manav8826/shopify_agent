import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class ShopifyService:
    """
    Stateless service for parsing and analyzing Shopify data using Pandas.
    """

    @staticmethod
    def parse_orders_data(orders: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert a list of order dictionaries to a Cleaned DataFrame.
        Extracts: id, created_at, total_price, customer_id, city, line_items.
        """
        if not orders:
            return pd.DataFrame()

        data = []
        for order in orders:
            # Safely extract nested fields
            customer = order.get('customer', {}) or {}
            address = order.get('billing_address', {}) or {}
            
            data.append({
                'id': order.get('id'),
                'created_at': pd.to_datetime(order.get('created_at')),
                'total_price': float(order.get('total_price', 0.0)),
                'customer_id': customer.get('id'),
                'email': customer.get('email'),
                'city': address.get('city', 'Unknown'),
                'line_items': order.get('line_items', [])
            })
        
        return pd.DataFrame(data)

    @staticmethod
    def calculate_aov(orders_df: pd.DataFrame, days: Optional[int] = None) -> str:
        """
        Calculate Average Order Value, optionally filtered by the last N days.
        Returns a formatted string.
        """
        if orders_df.empty:
            return "No order data available to calculate AOV."
        
        df = orders_df.copy()
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            # Ensure created_at is timezone-naive or aware matching the mock. 
            # Shopify returns UTC ISO strings which pd.to_datetime handles.
            # We'll normalize to UTC for safety if needed, but simple comparison usually works if both are tz-aware or both naive.
            # For simplicity in this logic, assuming the dataframe has proper datetime objects.
            if df['created_at'].dt.tz is not None:
                # Make current time aware if the DF is aware
                import pytz
                cutoff = cutoff.replace(tzinfo=pytz.UTC)
            
            df = df[df['created_at'] >= cutoff]
            
        if df.empty:
            return f"No orders found in the last {days} days."
            
        total_revenue = df['total_price'].sum()
        order_count = len(df)
        aov = total_revenue / order_count if order_count > 0 else 0
        
        return f"The Average Order Value (AOV) {'for the last ' + str(days) + ' days ' if days else ''}is **${aov:.2f}** (based on {order_count} orders)."

    @staticmethod
    def get_top_products(orders_df: pd.DataFrame, limit: int = 5) -> str:
        """
        Get top products by quantity sold.
        """
        if orders_df.empty or 'line_items' not in orders_df.columns:
            return "No data available to determine top products."
            
        # Explode line items
        # We need to parse the line_items col which is a list of dicts
        all_items = []
        for _, row in orders_df.iterrows():
            for item in row['line_items']:
                all_items.append({
                    'product_title': item.get('title', 'Unknown Product'),
                    'quantity': item.get('quantity', 0),
                    'price': float(item.get('price', 0.0))
                })
                
        if not all_items:
             return "No product items found in the orders."
             
        items_df = pd.DataFrame(all_items)
        
        # Group by title
        top_products = items_df.groupby('product_title')['quantity'].sum().sort_values(ascending=False).head(limit)
        
        return ShopifyService.create_summary_table(
            top_products.reset_index(), 
            headers=["Product", "Units Sold"]
        )

    @staticmethod
    def analyze_revenue_by_city(orders_df: pd.DataFrame) -> str:
        """
        Group revenue by city.
        """
        if orders_df.empty or 'city' not in orders_df.columns:
             return "No data to analyze revenue by city."
             
        city_revenue = orders_df.groupby('city')['total_price'].sum().sort_values(ascending=False)
        
        # Format as table
        df_reset = city_revenue.reset_index()
        df_reset['total_price'] = df_reset['total_price'].apply(lambda x: f"${x:,.2f}")
        
        return ShopifyService.create_summary_table(
            df_reset,
            headers=["City", "Total Revenue"]
        )

    @staticmethod
    def find_repeat_customers(orders_df: pd.DataFrame) -> str:
        """
        Identify customers with more than 1 order.
        """
        if orders_df.empty or 'customer_id' not in orders_df.columns:
             return "No data to analyze repeat customers."
             
        # Filter out null customer IDs (guest checkouts without tracking?)
        df = orders_df.dropna(subset=['customer_id'])
        
        customer_counts = df['customer_id'].value_counts()
        repeat_customers = customer_counts[customer_counts > 1]
        
        count = len(repeat_customers)
        total_customers = len(customer_counts)
        rate = (count / total_customers * 100) if total_customers > 0 else 0
        
        return f"Found **{count}** repeat customers ({rate:.1f}% of total identified customers)."

    @staticmethod
    def create_summary_table(df: pd.DataFrame, headers: List[str]) -> str:
        """
        Convert a DataFrame to a Markdown table string.
        """
        if df.empty:
            return "No data to display."
            
        markdown_table = f"| {' | '.join(headers)} |\n"
        markdown_table += f"| {' | '.join(['---'] * len(headers))} |\n"
        
        for _, row in df.iterrows():
            row_str = " | ".join(str(val) for val in row)
            markdown_table += f"| {row_str} |\n"
            
        return markdown_table
