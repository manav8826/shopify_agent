# Deployment Guide

This guide describes how to deploy the Shopify Agent.

## 1. Backend (Render)

1.  **Create Service**: Go to [Render Dashboard](https://dashboard.render.com/) -> New + -> **Web Service**.
2.  **Repo**: Connect your repository.
3.  **Settings**:
    *   **Root Directory**: `backend`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables**:
    *   `SHOPIFY_ACCESS_TOKEN`: [Your Token]
    *   `SHOPIFY_STORE_URL`: [Your Store URL]
    *   `GROQ_API_KEY`: [Your API Key]
    *   `APP_ENV`: `production`

## 2. Frontend (Vercel)

1.  **Create Project**: Go to [Vercel Dashboard](https://vercel.com/dashboard) -> **Add New Project**.
2.  **Repo**: Import the same repository.
3.  **Settings**:
    *   **Framework Preset**: `Vite`
    *   **Root Directory**: `frontend`
4.  **Environment Variables**:
    *   `VITE_API_BASE_URL`: The URL of your deployed Render backend (e.g., `https://shopify-agent-backend.onrender.com/api`).
        *   *Note: Ensure you include `/api` at the end if your backend routes require it, or just the base URL if the client appends it. Our client expects the full base path `.../api`.*

## Troubleshooting

-   **CORS**: The backend is configured to allow `*` (all origins) by default. If you see CORS errors, ensure your Backend URL in Vercel is correct.
-   **Routing**: If refreshing the page gives a 404, ensure `vercel.json` exists in the frontend root.
