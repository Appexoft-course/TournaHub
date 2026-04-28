from sqlalchemy.orm import Session

from app.models.match import Match
from app.models.user import User


def update_match_result(
    db: Session,
    match_id: int,
    score_1: int,
    score_2: int,
    mvp_id: int | None = None,
):
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise Exception("Match not found")

    match.score_1 = score_1
    match.score_2 = score_2

    if score_1 > score_2:
        match.winner = match.team_1
        match.loser = match.team_2
    elif score_2 > score_1:
        match.winner = match.team_2
        match.loser = match.team_1
    else:
        match.winner = None
        match.loser = None

    if mvp_id:
        match.mvp_id = mvp_id

    if match.winner and match.loser:
        winner = db.query(User).filter(User.id == match.winner).first()
        loser = db.query(User).filter(User.id == match.loser).first()

        if winner:
            winner.wins += 1

        if loser:
            loser.loses += 1

    db.commit()
    db.refresh(match)

    return match