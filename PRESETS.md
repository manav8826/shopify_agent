# Presets & Examples 📝

This guide lists the capabilities of the ShopifyAI agent and sample interactions.

## 1. Capabilities

- **Order Analysis**: Revenue calculations, order counts, date filtering.
- **Product Insights**: Best sellers, inventory checks.
- **Customer Segmentation**: Repeat buyers, location analysis.

## 2. Sample Questions & Expected Outputs

### Revenue
**Q**: "How much revenue did we make in the last 7 days?"
**Expected Output**:
> "The total revenue for the last 7 days (Dec 15 - Dec 22) is **$12,450**. This comes from 142 orders."
*(Internal Logic: Fetches orders with `created_at_min`, sums `total_price` in Python)*

### Best Sellers
**Q**: "What are the top 3 selling products?"
**Expected Output**:
> "Here are your top 3 selling products by quantity:
> 1.  **Classic T-Shirt** - 45 sold
> 2.  **Denim Jeans** - 32 sold
> 3.  **Leather Belt** - 28 sold"

### Customer Insights
**Q**: "Who are my top returning customers?"
**Expected Output**:
> "Based on order history, these customers have ordered most frequently:
> - **John Doe**: 5 orders
> - **Jane Smith**: 3 orders"

## 3. API Documentation Links

- **Shopify Admin API**: [https://shopify.dev/docs/api/admin-rest](https://shopify.dev/docs/api/admin-rest)
- **FastAPI Backend**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)