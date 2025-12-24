from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as api_router
from app.db.database import engine, Base
# Import models to ensure they are registered with Base
from app.models import database_models 

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shopify Analyst Agent API",
    description="Backend for Shopify AI Agent",
    version="0.1.0",
    debug=settings.DEBUG
)

# Configure CORS
# Allow requests from localhost:5173 (React default) and potentially others
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "shopify_connected": bool(settings.SHOPIFY_ACCESS_TOKEN and settings.SHOPIFY_STORE_URL)
    }

@app.get("/")
async def root():
    return {"message": "Shopify Analyst Agent API is running. Go to /docs for Swagger UI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
