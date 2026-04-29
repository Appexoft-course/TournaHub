from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.schemas.statistics import UserStatisticsResponse, LeaderboardUserResponse
from app.db.session import get_db
from app.services.statistics_service import (
    get_user_statistics,
    get_all_users_statistics,
    get_leaderboard,
)

router = APIRouter()


@router.get("/users/{user_id}", response_model=UserStatisticsResponse)
async def user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_statistics(db, user_id)


@router.get("/users", response_model=List[UserStatisticsResponse])
async def all_users_stats(db: AsyncSession = Depends(get_db)):
    return await get_all_users_statistics(db)


@router.get("/leaderboard", response_model=List[LeaderboardUserResponse])
async def leaderboard(db: AsyncSession = Depends(get_db)):
    return await get_leaderboard(db)