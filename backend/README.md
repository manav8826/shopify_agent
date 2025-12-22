# ShopifyAI Backend 🧠

The intelligence core of the ShopifyAI platform. Built with **FastAPI** and **LangChain**.

## Setup & Installation

1.  **Environment**:
    Ensure you have Python 3.10+ installed.
    ```bash
    python -m venv myenv
    # Windows
    myenv\Scripts\activate
    # Linux/Mac
    source myenv/bin/activate
    ```

2.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    Create a `.env` file in this directory:
    ```ini
    SHOPIFY_STORE_URL="https://your-store.myshopify.com"
    SHOPIFY_ACCESS_TOKEN="shpat_..."
    GROQ_API_KEY="gsk_..."
    GEMINI_API_KEY="AIza..."
    ```

## Architecture

### The Agent (`AgentService`)
The heart of the backend is a **ReAct** (Reason+Act) agent.
- **System Prompt**: Defines the persona (Business Intelligence Analyst) and strict rules (no hallucinations, usage of specific tools).
- **Tools**:
    - `get_shopify_data`: Fetches raw JSON from Shopify endpoints (`orders`, `products`, etc).
    - `python_repl_ast`: Executes Python pandas code to analyze the data.
- **Ghost Data Pattern**: To optimize token usage, large datasets fetched by `get_shopify_data` are **injected directly** into the `python_repl_ast` local scope. The LLM only sees a summary ("Fetched 250 records") and writes code assuming the variable `shopify_data` exists.

### API Endpoints

- `POST /api/chat`: Main interaction point.
    - Input: `{ "message": "Show me total revenue", "session_id": "uuid" }`
    - Output: `{ "response": "Total revenue is $500", "thought_process": "..." }`
- `GET /api/sessions`: List active chat sessions.
- `GET /api/sessions/{id}/history`: Retrieve chat history.

## Development

### Running Locally
```bash
uvicorn app.main:app --reload
```
Swagger UI is available at `http://localhost:8000/docs`.

### Testing
We use `pytest` for all testing.
```bash
# Run all tests
pytest

# Run with output
pytest -s

# Run specific file
pytest tests/api/test_routes.py
```

### Code Quality
Maintain code quality with these commands:
```bash
# Formatting
black .

# Linting
flake8 .

# Type Checking
mypy .
```

## Deployment (Railway/Render)

1.  **Build Command**: `pip install -r requirements.txt`
2.  **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3.  **Environment**: Add all `.env` variables to the dashboard.