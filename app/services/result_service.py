from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match
from app.models.user import User


async def update_match_result(
    db: AsyncSession,
    match_id: int,
    score_1: int,
    score_2: int,
    mvp_id: int | None = None,
):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

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

    if mvp_id is not None:
        match.mvp_id = mvp_id

    if match.winner and match.loser:
        winner_result = await db.execute(select(User).where(User.id == match.winner))
        loser_result = await db.execute(select(User).where(User.id == match.loser))

        winner = winner_result.scalar_one_or_none()
        loser = loser_result.scalar_one_or_none()

    if winner:
        winner.wins += 1

    if loser:
        loser.loses += 1

    if winner and loser:
        calculate_elo(winner, loser)

def calculate_elo(winner, loser, k=32):
    expected_winner = 1 / (1 + 10 ** ((loser.elo - winner.elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner.elo - loser.elo) / 400))

    winner.elo = int(winner.elo + k * (1 - expected_winner))
    loser.elo = int(loser.elo + k * (0 - expected_loser))

    return match