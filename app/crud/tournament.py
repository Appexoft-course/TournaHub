from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tournament import Tournament
from app.schemas.tournament import CreateTournament
from app.models.user import User
from app.models.match import Match, MatchStatus

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_tournament(db: AsyncSession, data: CreateTournament, user_id: int) -> Tournament:
    tournament = Tournament(
        owner_id=user_id,
        name=data.name,
        game_type=data.game_type,
        started_at=data.started_at,
        end_at=data.end_at,
        min_elo=data.min_elo,
        max_elo=data.max_elo,
        description=data.description,
        max_players=data.max_players,
    )

    if data.participant_ids:
        result = await db.execute(
            select(User).where(User.id.in_(data.participant_ids))
        )
        users = result.scalars().all()
        tournament.participants.extend(users)

    db.add(tournament)
    await db.commit()
    await db.refresh(tournament)
    return tournament


    # ── CRUD для турнірної сітки ─────────────────────────────────────────────────

from app.models.match import Match, MatchStatus


async def get_tournament_by_id(db: AsyncSession, tournament_id: int) -> Tournament | None:
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    return result.scalar_one_or_none()


async def create_bracket_match(
    db: AsyncSession,
    tournament_id: int,
    round: int,
    match_index: int,
    slot_top_id: str,
    slot_bottom_id: str,
    player1_id: int | None = None,
    player2_id: int | None = None,
) -> Match:
    match = Match(
        tournament_id=tournament_id,
        round=round,
        match_index=match_index,
        slot_top_id=slot_top_id,
        slot_bottom_id=slot_bottom_id,
        player1_id=player1_id,
        player2_id=player2_id,
        game_type="bracket",
        status=MatchStatus.pending,
    )
    db.add(match)
    await db.flush()  # отримуємо id без commit
    return match


async def get_match_by_id(db: AsyncSession, match_id: int, tournament_id: int) -> Match | None:
    result = await db.execute(
        select(Match).where(
            Match.id == match_id,
            Match.tournament_id == tournament_id,
        )
    )
    return result.scalar_one_or_none()


async def get_next_round_match(
    db: AsyncSession,
    tournament_id: int,
    round: int,
    match_index: int,
) -> Match | None:
    result = await db.execute(
        select(Match).where(
            Match.tournament_id == tournament_id,
            Match.round == round,
            Match.match_index == match_index,
        )
    )
    return result.scalar_one_or_none()


async def delete_bracket_matches(db: AsyncSession, tournament_id: int) -> None:
    from sqlalchemy import delete
    await db.execute(
        delete(Match).where(Match.tournament_id == tournament_id)
    )