from fastapi import APIRouter


api_router = APIRouter()
api_router.include_router(statistics_router, prefix="/statistics", tags=["statistics"])