from fastapi import APIRouter, Depends,Request

from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    TokenResponse,
    RegisterResponse,
    RefreshRequest
)

from app.services.auth_service import AuthService

from app.api.deps import get_auth_service
from app.core.security import hash_password
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: Request,
    data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register_user(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: UserLogin,
    service: AuthService = Depends(get_auth_service)
):
    return await service.login_user(data)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    service: AuthService = Depends(get_auth_service)
):
    return await service.refresh_tokens(data.refresh_token)
