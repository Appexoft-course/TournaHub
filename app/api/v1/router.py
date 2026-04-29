from fastapi import APIRouter

from app.api.v1.statistics import router as statistics_router

api_router = APIRouter()

api_router.include_router(
    statistics_router,
    prefix="/statistics",
    tags=["statistics"],
)