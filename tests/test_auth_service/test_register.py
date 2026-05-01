import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from fastapi import HTTPException
from pydantic import ValidationError


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_db):
    return AuthService(db=mock_db)


@pytest.mark.asyncio
async def test_register_success(auth_service, mock_db):
    data = UserCreate(
        email="test@ex.com",
        name="asdasdasd",
        password="sad212312sad",
        description="asdasd",
        favorite_games=["chess"]
    )

    with patch("app.services.auth_service.get_user_by_email", AsyncMock(return_value=None)), \
         patch("app.services.auth_service.create_user", AsyncMock(return_value=MagicMock(id=1, email="test@ex.com"))):

        result = await auth_service.register_user(data)

        assert result["token_type"] == "bearer"
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_register_already_exists(auth_service, mock_db):
    data = UserCreate(
        email="exists@ex.com",
        name="sdasdas",
        password="asdasdasd21321"
    )

    with patch("app.services.auth_service.get_user_by_email", AsyncMock(return_value=True)):
        with pytest.raises(HTTPException) as ex:
            await auth_service.register_user(data)

        assert ex.value.status_code == 400
        assert "User already registered" in ex.value.detail


@pytest.mark.asyncio
async def test_register_short_password(auth_service, mock_db):
    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="eqdsasd@sad.com",
            name="sadasds",
            password="12"
        )

    assert "password" in str(ex.value)


@pytest.mark.asyncio
async def test_register_short_name(auth_service, mock_db):
    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="eqdsasd@sad.com",
            name="ss",
            password="sadas"
        )

    assert "name" in str(ex.value)


@pytest.mark.asyncio
async def test_register_incorrect_email(auth_service, mock_db):
    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="ass",
            name="asdas",
            password="sadasdsad"
        )

    errors = ex.value.errors()
    assert errors[0]["loc"] == ("email",)

def test_register_invalid_favorite_game():
    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="test@test.com",
            name="andrii",
            password="123456",
            favorite_games=["csgo"] 
        )

    errors = ex.value.errors()

    assert errors[0]["loc"] == ("favorite_games", 0)
    assert "Input should be" in errors[0]["msg"]

import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate


def test_register_short_description():
    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="test@test.com",
            name="andrii",
            password="123456",
            description="hi",  
            favorite_games=["chess"]
        )

    errors = ex.value.errors()

    assert errors[0]["loc"] == ("description",)
    assert "at least 3 characters" in errors[0]["msg"]



def test_register_too_long_description():
    long_text = "a" * 151 

    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="test@test.com",
            name="andrii",
            password="123456",
            description=long_text,
            favorite_games=["chess"]
        )

    errors = ex.value.errors()

    assert errors[0]["loc"] == ("description",)
    assert "at most 150 characters" in errors[0]["msg"]

def test_register_too_long_name():
    long_name = "a" * 21  

    with pytest.raises(ValidationError) as ex:
        UserCreate(
            email="test@test.com",
            name=long_name,
            password="123456",
            description="valid description",
            favorite_games=["chess"]
        )

    errors = ex.value.errors()

    assert errors[0]["loc"] == ("name",)
    assert "at most 20 characters" in errors[0]["msg"]