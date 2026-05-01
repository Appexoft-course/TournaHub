import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.oauth_service import OAuthService


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
def oauth_service(mock_db):
    return OAuthService(mock_db)


# -------------------------
# STATE TESTS
# -------------------------

def test_generate_and_validate_state(oauth_service):
    state = oauth_service.generate_state()

    assert isinstance(state, str)
    assert oauth_service.validate_state(state) is True

    assert oauth_service.validate_state(state) is False



def test_get_google_auth_url(oauth_service):
    state = "test_state"

    url = oauth_service.get_google_auth_url(state)

    assert "client_id" in url
    assert "redirect_uri" in url
    assert f"state={state}" in url
    assert "scope=openid+email+profile" in url



@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_exchange_code_for_token_success(mock_post, oauth_service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "test_token"}

    mock_post.return_value = mock_response

    result = await oauth_service.exchange_code_for_token("code")

    assert result["access_token"] == "test_token"


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_exchange_code_for_token_fail(mock_post, oauth_service):
    mock_response = MagicMock()
    mock_response.status_code = 400

    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        await oauth_service.exchange_code_for_token("code")




@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_get_google_user_info_success(mock_get, oauth_service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"email": "test@gmail.com"}

    mock_get.return_value = mock_response

    result = await oauth_service.get_google_user_info("token")

    assert result["email"] == "test@gmail.com"


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_get_google_user_info_fail(mock_get, oauth_service):
    mock_response = MagicMock()
    mock_response.status_code = 400

    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        await oauth_service.get_google_user_info("token")




@pytest.mark.asyncio
@patch("app.services.oauth_service.get_user_by_email")
@patch("app.services.oauth_service.OAuthService.get_google_user_info")
@patch("app.services.oauth_service.OAuthService.exchange_code_for_token")
async def test_login_register_new_user(
    mock_exchange,
    mock_userinfo,
    mock_get_user,
    oauth_service,
    mock_db
):
    oauth_service._state_store["valid_state"] = "valid"

    mock_exchange.return_value = {"access_token": "token"}
    mock_userinfo.return_value = {
        "email": "test@gmail.com",
        "name": "Test User",
        "id": "123",
    }
    mock_get_user.return_value = None

    result = await oauth_service.login_or_register("code", "valid_state")

    assert "access_token" in result
    assert "refresh_token" in result

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
@patch("app.services.oauth_service.get_user_by_email")
@patch("app.services.oauth_service.OAuthService.get_google_user_info")
@patch("app.services.oauth_service.OAuthService.exchange_code_for_token")
async def test_login_existing_user(
    mock_exchange,
    mock_userinfo,
    mock_get_user,
    oauth_service,
    mock_db
):
    oauth_service._state_store["valid_state"] = "valid"

    mock_exchange.return_value = {"access_token": "token"}
    mock_userinfo.return_value = {
        "email": "test@gmail.com",
        "name": "Test User",
        "id": "123",
    }

    existing_user = MagicMock()
    existing_user.id = "uuid"
    existing_user.email = "test@gmail.com"

    mock_get_user.return_value = existing_user

    result = await oauth_service.login_or_register("code", "valid_state")

    assert "access_token" in result
    assert "refresh_token" in result

    mock_db.add.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_state(oauth_service):
    with pytest.raises(Exception):
        await oauth_service.login_or_register("code", "invalid_state")