from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User


def calculate_winrate(wins: int, loses: int) -> float:
    total_matches = wins + loses
    return round((wins / total_matches) * 100, 2) if total_matches else 0


def build_user_statistics(user: User) -> dict:
    total_matches = user.wins + user.loses

    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "wins": user.wins,
        "loses": user.loses,
        "total_matches": total_matches,
        "winrate": calculate_winrate(user.wins, user.loses),
        "elo": user.elo,
        "rating": user.rating,
    }


async def get_user_statistics(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return build_user_statistics(user)


async def get_all_users_statistics(db: AsyncSession):
    result = await db.execute(select(User))
    users = result.scalars().all()

    return [build_user_statistics(user) for user in users]


async def get_leaderboard(db: AsyncSession, limit: int = 10):
    result = await db.execute(
        select(User).order_by(User.elo.desc(), User.wins.desc()).limit(limit)
    )
    users = result.scalars().all()

    leaderboard = []

    for index, user in enumerate(users, start=1):
        user_stats = build_user_statistics(user)
        user_stats["place"] = index
        leaderboard.append(user_stats)

    return leaderboard