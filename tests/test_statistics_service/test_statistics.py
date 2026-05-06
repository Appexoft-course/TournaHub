import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.statistics_service import (
    build_user_statistics,
    calculate_winrate,
    get_all_users_statistics,
    get_leaderboard,
    get_user_statistics,
)


class FakeScalars:
    def __init__(self, users):
        self.users = users

    def all(self):
        return self.users


class FakeResult:
    def __init__(self, users=None, single_user=None):
        self.users = users or []
        self.single_user = single_user

    def scalars(self):
        return FakeScalars(self.users)

    def scalar_one_or_none(self):
        return self.single_user


class FakeDB:
    def __init__(self, users=None, single_user=None):
        self.users = users or []
        self.single_user = single_user

    async def execute(self, statement):
        return FakeResult(users=self.users, single_user=self.single_user)


def create_user(
    user_id=1,
    name="Test User",
    email="test@example.com",
    wins=0,
    loses=0,
    elo=1000,
):
    return SimpleNamespace(
        id=user_id,
        name=name,
        email=email,
        wins=wins,
        loses=loses,
        elo=elo,
    )


def test_calculate_winrate_with_matches():
    winrate = calculate_winrate(wins=3, loses=1)

    assert winrate == 75.0


def test_calculate_winrate_without_matches():
    winrate = calculate_winrate(wins=0, loses=0)

    assert winrate == 0


def test_build_user_statistics_returns_expected_structure():
    user = create_user(wins=4, loses=1, elo=1032)

    statistics = build_user_statistics(user)

    assert statistics == {
        "user_id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "wins": 4,
        "loses": 1,
        "total_matches": 5,
        "winrate": 80.0,
        "elo": 1032,
    }


def test_build_user_statistics_does_not_include_removed_rating_field():
    user = create_user()

    statistics = build_user_statistics(user)

    assert "rating" not in statistics


def test_get_user_statistics_returns_user_data():
    user = create_user(user_id=10, wins=2, loses=2)
    db = FakeDB(single_user=user)

    statistics = asyncio.run(get_user_statistics(db, user_id=10))

    assert statistics["user_id"] == 10
    assert statistics["total_matches"] == 4
    assert statistics["winrate"] == 50.0


def test_get_user_statistics_raises_404_when_user_not_found():
    db = FakeDB(single_user=None)

    with pytest.raises(HTTPException) as error:
        asyncio.run(get_user_statistics(db, user_id=999))

    assert error.value.status_code == 404
    assert error.value.detail == "User not found"


def test_get_all_users_statistics_returns_list():
    users = [
        create_user(user_id=1, wins=3, loses=0),
        create_user(user_id=2, wins=1, loses=2),
    ]
    db = FakeDB(users=users)

    statistics = asyncio.run(get_all_users_statistics(db))

    assert len(statistics) == 2
    assert statistics[0]["user_id"] == 1
    assert statistics[1]["user_id"] == 2


def test_get_leaderboard_adds_places():
    users = [
        create_user(user_id=1, name="First", elo=1200),
        create_user(user_id=2, name="Second", elo=1100),
    ]
    db = FakeDB(users=users)

    leaderboard = asyncio.run(get_leaderboard(db, limit=10))

    assert leaderboard[0]["place"] == 1
    assert leaderboard[0]["name"] == "First"
    assert leaderboard[1]["place"] == 2
    assert leaderboard[1]["name"] == "Second"