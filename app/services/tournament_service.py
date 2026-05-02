from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.schemas.tournament import CreateTournament
from app.core.logging import setup_logging
from app.crud.tournament import create_tournament, get_user_by_id

MIN_WINS_TO_CREATE = 10
MAX_PLAYERS_LIMIT = 16


class TournamentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()

    async def create(self, data: CreateTournament, owner_id: int):
        user = await get_user_by_id(self.db, owner_id)
        if not user:
            self.logger.warning(f"Tournament create failed: user id={owner_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not user.is_active:
            self.logger.warning(f"Tournament create failed: user id={owner_id} is blocked")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is blocked")

        if user.wins < MIN_WINS_TO_CREATE:
            self.logger.warning(f"Tournament create failed: user id={owner_id} wins={user.wins} < {MIN_WINS_TO_CREATE}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You need at least {MIN_WINS_TO_CREATE} wins to create a tournament. Your wins: {user.wins}"
            )

        now = datetime.now(timezone.utc)

        if data.started_at and data.started_at < now:
            self.logger.warning(f"Tournament create failed: user id={owner_id} started_at in the past")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tournament start date cannot be in the past")

        if data.end_at and data.started_at and data.end_at <= data.started_at:
            self.logger.warning(f"Tournament create failed: user id={owner_id} end_at <= started_at")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End date must be after start date")

        if data.min_elo and data.max_elo and data.min_elo >= data.max_elo:
            self.logger.warning(f"Tournament create failed: invalid ELO range min={data.min_elo} max={data.max_elo}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum ELO must be less than maximum ELO")

        if data.max_players < 2:
            self.logger.warning(f"Tournament create failed: max_players={data.max_players} < 2")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tournament must have at least 2 players")

        if data.max_players > MAX_PLAYERS_LIMIT:
            self.logger.warning(f"Tournament create failed: max_players={data.max_players} > {MAX_PLAYERS_LIMIT}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tournament can have at most {MAX_PLAYERS_LIMIT} players")

        if data.participant_ids:
            if len(data.participant_ids) > data.max_players:
                self.logger.warning(f"Tournament create failed: participants count={len(data.participant_ids)} > max_players={data.max_players}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Number of participants ({len(data.participant_ids)}) exceeds maximum ({data.max_players})"
                )
            if owner_id in data.participant_ids:
                self.logger.warning(f"Tournament create failed: owner id={owner_id} is in participant_ids")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner cannot be a participant of the tournament")

        self.logger.info(f"Tournament creating: user id={owner_id} wins={user.wins} name='{data.name}'")

        try:
            tournament = await create_tournament(self.db, data, owner_id)
        except Exception as e:
            self.logger.error(f"Tournament create error: user id={owner_id} error={e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create tournament")

        self.logger.info(f"Tournament created: id={tournament.id} name='{tournament.name}' owner id={owner_id}")
        return tournament