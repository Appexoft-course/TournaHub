from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.statistics_service import (
    get_user_statistics,
    get_all_users_statistics,
    get_leaderboard,
)

router = APIRouter()


@router.get("/users/{user_id}")
async def user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_statistics(db, user_id)


@router.get("/users")
async def all_users_stats(db: AsyncSession = Depends(get_db)):
    return await get_all_users_statistics(db)


@router.get("/leaderboard")
async def leaderboard(db: AsyncSession = Depends(get_db)):
    return await get_leaderboard(db)