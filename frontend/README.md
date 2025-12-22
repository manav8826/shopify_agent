# ShopifyAI Frontend 💻

A modern, responsive chat interface built with **React**, **Vite**, and **TypeScript**.

## Setup

1.  **Install**:
    ```bash
    npm install
    ```

2.  **Run Development**:
    ```bash
    npm run dev
    ```
    Runs on port `5173` by default.

## Architecture

### Components
- `App.tsx`: Main layout and router.
- `ChatInterface.tsx`: The primary view containing the message list and input.
- `MessageBubble.tsx`: Renders individual messages (User vs AI). Supports Markdown rendering.
- `Sidebar.tsx`: Manages chat sessions (history) and "New Chat" functionality.

### State Management
- Uses standard React `useState` and `useEffect` hooks.
- Fetches data from the backend APIs (`/api/chat`, `/api/sessions`).

## Build & Deploy

### Vercel / Netlify
1.  **Build Command**: `npm run build`
2.  **Output Directory**: `dist`
3.  **Environment**: Nothing special needed for static build, but ensure the backend URL is correctly configured (defaults to local, update `vite.config.ts` proxy or use `.env` for production API URL).

To configure production API URL:
Create `.env.production`:
```
VITE_API_URL=https://your-backend-url.com
```
