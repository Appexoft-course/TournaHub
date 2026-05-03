import pytest
from sqlalchemy.orm import Session
from app.models.match import Match
from app.services.match_making_servisse import create_match
from datetime import datetime

def test_create_match(db_session: Session):

    game_type = "football"
    team_1 = 1
    team_2 = 2
    started_at = datetime(2026, 5, 3, 12, 0)
    end_at = datetime(2026, 5, 3, 13, 0)

    match = create_match(
        db=db_session,
        game_type=game_type,
        team_1=team_1,
        team_2=team_2,
        started_at=started_at,
        end_at=end_at,
    )


    assert isinstance(match, Match)
    assert match.game_type == "football"
    assert match.team_1 == 1
    assert match.team_2 == 2
    assert match.started_at == started_at
    assert match.end_at == end_at
