import asyncio
import os
from app.services.shopify_client import ShopifyClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings

async def test_shopify():
    print("Testing Shopify Connection...")
    client = ShopifyClient()
    try:
        # Try fetching products with limit 1
        data = await client.get_resource("products", params={"limit": 1})
        print(f"Shopify Success! Found {len(data)} items.")
    except Exception as e:
        print(f"Shopify FAILED: {e}")

async def test_gemini():
    print("\nTesting Gemini Connection...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            temperature=0.1,
            google_api_key=settings.GEMINI_API_KEY
        )
        resp = await llm.ainvoke([HumanMessage(content="Hello, what is 2+2?")])
        print(f"Gemini Raw Response: {resp}")
        print(f"Gemini Success! Content: {resp.content}")
    except Exception as e:
        print(f"Gemini FAILED: {e}")

async def main():
    await test_shopify()
    await test_gemini()

if __name__ == "__main__":
    asyncio.run(main())
