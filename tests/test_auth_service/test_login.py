import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.schemas.user import UserLogin

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.auth_service import AuthService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_db):
    return AuthService(db=mock_db)

@pytest.mark.asyncio
async def test_login_success(auth_service, mock_db):
    user_mock = MagicMock(
        id=1,
        email="test@test.com",
        password="hashed_password",
        oauth_provider=None
    )

    data = UserLogin(
        email="test@test.com",
        password="123456"
    )

    with patch("app.services.auth_service.get_user_by_email", AsyncMock(return_value=user_mock)), \
         patch("app.services.auth_service.verify_password", return_value=True), \
         patch("app.services.auth_service.create_token", return_value="access123"), \
         patch("app.services.auth_service.create_refresh_token", return_value="refresh123"), \
         patch("app.services.auth_service.hash_password", return_value="hashed_refresh"):

        result = await auth_service.login_user(data)

        assert result["access_token"] == "access123"
        assert result["refresh_token"] == "refresh123"
        assert result["token_type"] == "bearer"

        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, mock_db):
    data = UserLogin(
        email="missing@test.com",
        password="123456"
    )

    with patch("app.services.auth_service.get_user_by_email", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as ex:
            await auth_service.login_user(data)

        assert ex.value.status_code == 401
        assert "User not registered" in ex.value.detail


@pytest.mark.asyncio
async def test_login_google_user_blocked(auth_service, mock_db):
    user_mock = MagicMock(
        id=1,
        email="google@test.com",
        password=None,
        oauth_provider="google"
    )

    data = UserLogin(
        email="google@test.com",
        password="123456"
    )

    with patch("app.services.auth_service.get_user_by_email", AsyncMock(return_value=user_mock)):
        with pytest.raises(HTTPException) as ex:
            await auth_service.login_user(data)

        assert ex.value.status_code == 400
        assert "Google" in ex.value.detail


@pytest.mark.asyncio
async def test_login_invalid_password(auth_service, mock_db):
    user_mock = MagicMock(
        id=1,
        email="test@test.com",
        password="hashed_password",
        oauth_provider=None
    )

    data = UserLogin(
        email="test@test.com",
        password="wrong_password"
    )

    with patch("app.services.auth_service.get_user_by_email", AsyncMock(return_value=user_mock)), \
         patch("app.services.auth_service.verify_password", return_value=False):

        with pytest.raises(HTTPException) as ex:
            await auth_service.login_user(data)

        assert ex.value.status_code == 401
        assert "Invalid password" in ex.value.detail