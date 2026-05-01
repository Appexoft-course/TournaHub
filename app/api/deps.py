from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

async def get_oauth_service(db:AsyncSession = Depends(get_db)) -> OAuthService:
    return OAuthService(db)