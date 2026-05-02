from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password



async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email.lower())
    )
    return result.scalars().first()

async def create_user(db:AsyncSession,data:UserCreate) -> User:
    user = User(
        name = data.name,
        email = data.email,
        description = data.description,
        password = hash_password(data.password),
        favorite_games = data.favorite_games
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User




async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalars().first()