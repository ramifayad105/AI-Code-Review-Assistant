from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth
from app.routers import repos
from app.routers import webhooks
from app.routers import reviews
from app.routers import stats

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered code review assistant for GitHub pull requests",
    version="0.1.0",
)

# CORS - allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(repos.router)
app.include_router(webhooks.router)
app.include_router(reviews.router)
app.include_router(stats.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "0.1.0",
    }
