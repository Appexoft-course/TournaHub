from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, create_token, create_refresh_token, hash_password, decode_refresh_token
from app.core.logging import setup_logging
from app.crud.auth import create_user, get_user_by_id,get_user_by_email
from app.schemas.user import UserCreate, UserLogin

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()

    async def register_user(self,data: UserCreate) -> dict:
        if await get_user_by_email(self.db,data.email):
            self.logger.error("User already registed")
            raise HTTPException(status_code=400, detail="User already registered")
        

        user = await create_user(self.db,data)
        access_token = create_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})
       
        user.refresh_token = hash_password(refresh_token)
        await self.db.commit()
        self.logger.info(f"User registered: {user.email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    async def login_user(self, data: UserLogin) -> dict:
        user = await get_user_by_email(self.db, data.email)

        if not user:
            self.logger.error("User not registered")
            raise HTTPException(status_code=401, detail="User not registered")

        if user.oauth_provider == "google":
            raise HTTPException(
                status_code=400,
                detail="Please login with Google"
            )


        if not verify_password(data.password, user.password):
            self.logger.error("Invalid password")
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = create_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

        user.refresh_token = hash_password(refresh_token)
        await self.db.commit()

        self.logger.info(f"User logged in: {user.email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


    async def refresh_tokens(self, token: str) -> dict:
        payload = decode_refresh_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = await get_user_by_id(self.db, int(payload["sub"]))
        if not user or not user.refresh_token:
            raise HTTPException(status_code=401, detail="User not found")

        if not verify_password(token, user.refresh_token):
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = create_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

        user.refresh_token = hash_password(refresh_token)
        await self.db.commit()
        self.logger.info(f"Tokens refreshed for user: {user.id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
