"""API route registration."""
from fastapi import APIRouter

from app.api.routes import (
    auth,
    chat,
    courses,
    dashboard,
    health,
    progress,
    quizzes,
    uploads,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(uploads.router)
api_router.include_router(courses.router)
api_router.include_router(chat.router)
api_router.include_router(quizzes.router)
api_router.include_router(progress.router)
api_router.include_router(dashboard.router)

# Health endpoints are mounted at the root (outside the versioned prefix) in main.
health_router = health.router
