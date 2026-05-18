from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers.health import router as health_router
from app.routers.scan import router as scan_router
from app.routers.expenses import router as expense_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables
    init_db()
    print(f"✅ Database initialized")
    print(f"🚀 {settings.APP_NAME} is running — docs at /docs")
    yield
    # Shutdown (nothing to clean up yet)
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered money tracker — scan receipts, track expenses, visualize spending.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for development (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router)
app.include_router(scan_router, prefix="/api/v1")
app.include_router(expense_router, prefix="/api/v1")
