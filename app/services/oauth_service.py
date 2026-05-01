import secrets
import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_token, create_refresh_token, hash_password
from app.core.logging import setup_logging
from app.crud.auth import get_user_by_email
from app.models.user import User
from app.core.config import settings

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class OAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()


    _state_store: dict[str, str] = {}

    def generate_state(self) -> str:
        state = secrets.token_urlsafe(32)
        self._state_store[state] = "valid"
        return state

    def validate_state(self, state: str) -> bool:
        return self._state_store.pop(state, None) is not None

    def get_google_auth_url(self, state: str) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "state": state,
            "prompt": "consent",
        }
        query = httpx.QueryParams(params)
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"

    async def exchange_code_for_token(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed token exchange")

        return response.json()

    async def get_google_user_info(self, access_token: str) -> dict:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed user info")

        return response.json()

    async def login_or_register(self, code: str, state: str) -> dict:
        self.logger.info("OAuth started")


        if not self.validate_state(state):
            self.logger.warning("Invalid OAuth state")
            raise HTTPException(status_code=400, detail="Invalid state")

        token_data = await self.exchange_code_for_token(code)
        user_info = await self.get_google_user_info(token_data["access_token"])

        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="No email from Google")

        email = email.lower()

        user = await get_user_by_email(self.db, email)

        if not user:
            user = User(
                email=email,
                name=user_info.get("name"),
                password="",
                oauth_provider="google",
                oauth_id=user_info.get("id"),
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

        access_token = create_token(user.id)
        refresh_token = create_refresh_token(user.id)

        user.refresh_token = hash_password(refresh_token)
        await self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }