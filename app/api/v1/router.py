from fastapi import APIRouter

from app.api.v1.statistics import router as statistics_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.tournament import router as tor_router
api_router = APIRouter()

api_router.include_router(
    statistics_router,
    prefix="/statistics",
    tags=["statistics"],
)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])

api_router.include_router(tor_router, prefix="/tournament", tags=["Tour"])
