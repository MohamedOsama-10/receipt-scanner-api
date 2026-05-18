from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "Money Tracker"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./money_tracker.db"

    # Azure Computer Vision — handles receipt image OCR
    # Create a free resource at: https://portal.azure.com
    # Free tier: ~5,000 transactions/month (rate-limited)
    AZURE_CV_ENDPOINT: str = ""   # e.g. https://<your-resource>.cognitiveservices.azure.com
    AZURE_CV_KEY: str = ""        # 32-char key from Azure portal

    # Groq — handles text classification (fast & free)
    # Get your key at: https://console.groq.com
    GROQ_API_KEY: str = ""

    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
