# ShopifyAI 🤖

**An Intelligent Agent for Shopify Store Analytics**

![ShopifyAI Banner](/frontend/public/logo.png)

## Overview

ShopifyAI is a powerful conversational agent that allows store owners to query their Shopify data using natural language. Built with **FastAPI**, **LangChain**, and **React**, it connects directly to your Shopify store to answer complex questions about orders, products, customers, and revenue.

### Key Features
- **Natural Language Queries**: "How much revenue did I make last week?"
- **Advanced Code Analysis**: The agent writes and executes Python code to perform precise calculations.
- **Ghost Data Optimization**: Efficiently handles large datasets (fetched via API, analyzed in memory) without token overflow.
- **Visualizations**: Supports tables and potentially charts (roadmap) for data presentation.
- **Secure & Isolated**: Tools run within a controlled environment.

## Architecture

```mermaid
graph TD
    User[User (Frontend)] <-->|Rest API| Backend[FastAPI Backend]
    Backend <-->|LangChain| Agent[ReAct Agent]
    Agent <-->|Tool Call| Shopify[Shopify Admin API]
    Agent <-->|Execution| REPL[Python REPL]
    Shopify -->|JSON Data| REPL
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Shopify Admin API Access Token

### 1. Backend Setup
1.  Navigate to `backend`:
    ```bash
    cd backend
    ```
2.  Install credentials:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure `.env` (see `.env.example` or provided credentials).
4.  Run the server:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

### 2. Frontend Setup
1.  Navigate to `frontend`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start development server:
    ```bash
    npm run dev
    ```
    Access the app at `http://localhost:5173`.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SHOPIFY_STORE_URL` | Your Shopify store URL (e.g., `shop.myshopify.com`) |
| `SHOPIFY_ACCESS_TOKEN` | Admin API Access Token (Orders read scope required) |
| `GROQ_API_KEY` | API Key for Groq (Llama 3 Model) |
| `GEMINI_API_KEY` | API Key for Google Gemini (Backup Model) |

## Testing
Run the full test suite in the `backend` directory:
```bash
pytest
```

## Known Limitations
- **Rate Limits**: The Shopify API (leaky bucket) and LLM providers have rate limits. The agent handles these gracefully but large bulk queries may pause execution.
- **Read-Only**: The agent cannot modify store data (create orders/products) for safety.
