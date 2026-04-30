from fastapi import APIRouter
from app.api.v1.routers import auth, tournament

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(tournament.router, prefix="/tournament", tags=["tournament"])
