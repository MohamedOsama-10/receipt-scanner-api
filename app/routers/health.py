from fastapi import APIRouter
from datetime import datetime
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Quick liveness check — confirms the API is running."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }
