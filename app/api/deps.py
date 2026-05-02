from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import decode_token
from app.crud.auth import get_user_by_id

from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService
from app.services.tournament_service import TournamentService

security = HTTPBearer()



async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_token(credentials.credentials)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_oauth_service(db: AsyncSession = Depends(get_db)) -> OAuthService:
    return OAuthService(db)


async def get_tournament_service(db: AsyncSession = Depends(get_db)) -> TournamentService:
    return TournamentService(db)