import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration settings.
    Reads from environment variables and .env file.
    """
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Shopify Configuration
    SHOPIFY_STORE_URL: str
    SHOPIFY_ACCESS_TOKEN: str
    SHOPIFY_API_VERSION: str = "2025-07"
    
    # Gemini Configuration
    GEMINI_API_KEY: str
    
    # Groq Configuration
    GROQ_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
