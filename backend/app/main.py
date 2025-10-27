"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import router
from app.tools.file_manager import file_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    print("🚀 Starting Excel AI Processor...")
    print(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    print(f"📤 Export directory: {settings.EXPORT_DIR}")
    print(f"🤖 LLM Model: {settings.LLM_MODEL}")
    print(f"🔗 LLM URL: {settings.LLM_BASE_URL}")

    # Cleanup old sessions on startup
    cleaned = file_manager.cleanup_old_sessions(max_age_hours=24)
    if cleaned > 0:
        print(f"🧹 Cleaned up {cleaned} old sessions")

    yield

    # Shutdown
    print("👋 Shutting down Excel AI Processor...")


# Создаём FastAPI приложение
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
