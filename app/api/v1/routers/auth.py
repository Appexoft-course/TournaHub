from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    TokenResponse,
    RegisterResponse,
    RefreshRequest
)
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService
from app.api.deps import get_auth_service, get_oauth_service

router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: Request,
    data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register_user(data)


@router.post("/login")
async def login(db: AsyncSession = Depends(get_db)):
    return {"msg": "login ok"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    service: AuthService = Depends(get_auth_service)
):
    return await service.refresh_tokens(data.refresh_token)


@router.get("/google")
async def google_login(service: OAuthService = Depends(get_oauth_service)):
    state = service.generate_state()
    return RedirectResponse(service.get_google_auth_url(state))

@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(
    code: str,
    state: str,
    service: OAuthService = Depends(get_oauth_service),
):
    return await service.login_or_register(
        code=code,
        state=state,
    )