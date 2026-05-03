import pytest
from app.services.elo_service import calculate_elo, classify_elo, update_users
from app.models.user import User

class DummyUser:
    def __init__(self, elo, wins=0, loses=0, win_streak=0, player_level="Beginner"):
        self.elo = elo
        self.wins = wins
        self.loses = loses
        self.win_streak = win_streak
        self.player_level = player_level

def test_calculate_elo_basic():
    user1 = DummyUser(elo=1200, win_streak=2)
    user2 = DummyUser(elo=1100)

    new_elo_1, new_elo_2, level1, level2 = calculate_elo(user1, user2)

    assert new_elo_1 > user1.elo
    assert new_elo_2 < user2.elo
    assert level1 in ["Expert", "Master", "Advanced"]
    assert level2 in ["Intermediate", "Novice", "Beginner"]

def test_classify_elo_levels():
    assert classify_elo(100) == "Beginner"
    assert classify_elo(300) == "Novice"
    assert classify_elo(600) == "Intermediate"
    assert classify_elo(1000) == "Advanced"
    assert classify_elo(1400) == "Expert"
    assert classify_elo(1600) == "Master"
    assert classify_elo(99999) == "Undefined"
