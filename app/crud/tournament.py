from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.tournament import Tournament
from app.schemas.tournament import CreateTournament


from app.models.user import User 

async def create_tournament(db: AsyncSession, data: CreateTournament, user_id: int):
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