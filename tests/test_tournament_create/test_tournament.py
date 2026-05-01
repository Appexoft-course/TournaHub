import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from pydantic import ValidationError

from app.services.tournament_service import TournamentService
from app.schemas.tournament import CreateTournament, GameEnum


def make_user(**kwargs):
    user = MagicMock()
    user.id = kwargs.get("id", 1)
    user.wins = kwargs.get("wins", 10)
    user.is_active = kwargs.get("is_active", True)
    return user


def make_data(**kwargs):
    now = datetime.now(timezone.utc)
    return CreateTournament(
        name=kwargs.get("name", "Test Tournament"),
        game_type=kwargs.get("game_type", [GameEnum.chess]),
        started_at=kwargs.get("started_at", now + timedelta(days=1)),
        end_at=kwargs.get("end_at", now + timedelta(days=2)),
        min_elo=kwargs.get("min_elo", 0),
        max_elo=kwargs.get("max_elo", 9999),
        description=kwargs.get("description", "Test description"),
        max_players=kwargs.get("max_players", 8),
        participant_ids=kwargs.get("participant_ids", []),
    )


@pytest.fixture
def service():
    db = AsyncMock()
    return TournamentService(db)


@pytest.fixture
def mock_get_user(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("app.services.tournament_service.get_user_by_id", mock)
    return mock


@pytest.fixture
def mock_create_tournament(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("app.services.tournament_service.create_tournament", mock)
    return mock


# --- User checks ---

@pytest.mark.asyncio
async def test_create_user_not_found(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.create(make_data(), owner_id=1)

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_create_user_blocked(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user(is_active=False)

    with pytest.raises(HTTPException) as exc:
        await service.create(make_data(), owner_id=1)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Your account is blocked"


@pytest.mark.asyncio
async def test_create_not_enough_wins(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user(wins=5)

    with pytest.raises(HTTPException) as exc:
        await service.create(make_data(), owner_id=1)

    assert exc.value.status_code == 403
    assert "10 wins" in exc.value.detail


# --- Date checks ---

@pytest.mark.asyncio
async def test_create_started_at_in_past(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user()
    now = datetime.now(timezone.utc)
    data = make_data(started_at=now - timedelta(days=1))

    with pytest.raises(HTTPException) as exc:
        await service.create(data, owner_id=1)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Tournament start date cannot be in the past"


@pytest.mark.asyncio
async def test_create_end_at_before_started_at(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user()
    now = datetime.now(timezone.utc)
    data = make_data(
        started_at=now + timedelta(days=2),
        end_at=now + timedelta(days=1),
    )

    with pytest.raises(HTTPException) as exc:
        await service.create(data, owner_id=1)

    assert exc.value.status_code == 400
    assert exc.value.detail == "End date must be after start date"


# --- ELO checks ---

@pytest.mark.asyncio
async def test_create_invalid_elo_range(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user()
    data = make_data(min_elo=1000, max_elo=500)

    with pytest.raises(HTTPException) as exc:
        await service.create(data, owner_id=1)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Minimum ELO must be less than maximum ELO"


# --- Max players checks ---

@pytest.mark.asyncio
async def test_create_max_players_too_low(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user()

    with pytest.raises(ValidationError) as exc:
        make_data(max_players=1)

    assert "greater than or equal to 2" in str(exc.value)


@pytest.mark.asyncio
async def test_create_max_players_too_high(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user()

    with pytest.raises(ValidationError) as exc:
        make_data(max_players=17)

    assert "less than or equal to 16" in str(exc.value)


# --- Participants checks ---

@pytest.mark.asyncio
async def test_create_too_many_participants(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user()
    data = make_data(max_players=2, participant_ids=[2, 3, 4])

    with pytest.raises(HTTPException) as exc:
        await service.create(data, owner_id=1)

    assert exc.value.status_code == 400
    assert "exceeds maximum" in exc.value.detail


@pytest.mark.asyncio
async def test_create_owner_in_participants(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user(id=1)
    data = make_data(participant_ids=[1, 2])

    with pytest.raises(HTTPException) as exc:
        await service.create(data, owner_id=1)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Owner cannot be a participant of the tournament"


# --- Success ---

@pytest.mark.asyncio
async def test_create_success(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user()
    tournament = MagicMock()
    tournament.id = 1
    tournament.name = "Test Tournament"
    mock_create_tournament.return_value = tournament

    result = await service.create(make_data(), owner_id=1)

    assert result.id == 1
    assert result.name == "Test Tournament"
    mock_create_tournament.assert_called_once()


@pytest.mark.asyncio
async def test_create_db_error(service, mock_get_user, mock_create_tournament):
    mock_get_user.return_value = make_user()
    mock_create_tournament.side_effect = Exception("DB error")

    with pytest.raises(HTTPException) as exc:
        await service.create(make_data(), owner_id=1)

    assert exc.value.status_code == 500
    assert exc.value.detail == "Failed to create tournament"