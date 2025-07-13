"""Routes API version 1."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, waste, statistics, notifications

# Router principal pour la version 1 de l'API
api_router = APIRouter()

# Inclure les routes des différents modules
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    waste.router,
    prefix="/waste",
    tags=["Waste Records"]
)

api_router.include_router(
    statistics.router,
    prefix="/statistics",
    tags=["Statistics"]
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)