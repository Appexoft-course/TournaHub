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

        # ── Турнірна сітка ───────────────────────────────────────────────────────

    async def start_bracket(self, tournament_id: int, player_ids: list[int]):
        import random
        from app.crud.tournament import (
            get_tournament_by_id,
            create_bracket_match,
            delete_bracket_matches,
        )

        tournament = await get_tournament_by_id(self.db, tournament_id)
        if not tournament:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")

        if tournament.status != "created":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start bracket: tournament status is '{tournament.status}'"
            )

        if len(player_ids) != 16:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Exactly 16 players required, got {len(player_ids)}"
            )

        # Видаляємо старі матчі якщо є
        await delete_bracket_matches(self.db, tournament_id)

        # Рандомний порядок гравців
        shuffled = player_ids.copy()
        random.shuffle(shuffled)

        # Створюємо 15 матчів: раунд 1=8, раунд 2=4, раунд 3=2, раунд 4=1
        for round_num in range(1, 5):
            match_count = 8 // (2 ** (round_num - 1))
            for mi in range(match_count):
                p1_id, p2_id = None, None
                if round_num == 1:
                    p1_id = shuffled[mi * 2]
                    p2_id = shuffled[mi * 2 + 1]

                await create_bracket_match(
                    db=self.db,
                    tournament_id=tournament_id,
                    round=round_num,
                    match_index=mi,
                    slot_top_id=f"R{round_num}_M{mi}_TOP",
                    slot_bottom_id=f"R{round_num}_M{mi}_BOT",
                    player1_id=p1_id,
                    player2_id=p2_id,
                )

        tournament.status = "started"
        await self.db.commit()
        await self.db.refresh(tournament)

        self.logger.info(f"Bracket started: tournament id={tournament_id}, players shuffled")
        return tournament

    async def set_match_winner(self, tournament_id: int, match_id: int, slot_id: str):
        from app.crud.tournament import (
            get_tournament_by_id,
            get_match_by_id,
            get_next_round_match,
        )
        from app.models.match import MatchStatus

        tournament = await get_tournament_by_id(self.db, tournament_id)
        if not tournament:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")

        match = await get_match_by_id(self.db, match_id=match_id, tournament_id=tournament_id)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

        if match.status == MatchStatus.completed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match already completed")

        if not match.player1_id or not match.player2_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Match does not have both players yet"
            )

        # Визначаємо переможця по slot_id
        if slot_id == match.slot_top_id:
            winner_id = match.player1_id
        elif slot_id == match.slot_bottom_id:
            winner_id = match.player2_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"slot_id '{slot_id}' does not belong to this match. "
                       f"Valid: '{match.slot_top_id}' or '{match.slot_bottom_id}'"
            )

        match.bracket_winner_id = winner_id
        match.status = MatchStatus.completed

        # Просуваємо переможця у наступний раунд
        next_round = match.round + 1
        if next_round <= 4:
            next_match = await get_next_round_match(
                db=self.db,
                tournament_id=tournament_id,
                round=next_round,
                match_index=match.match_index // 2,
            )
            if next_match:
                # Парний match_index → TOP (player1), непарний → BOT (player2)
                if match.match_index % 2 == 0:
                    next_match.player1_id = winner_id
                else:
                    next_match.player2_id = winner_id

        # Фінал зіграно — закриваємо турнір
        if match.round == 4:
            tournament.status = "finished"

        await self.db.commit()
        await self.db.refresh(match)

        self.logger.info(f"Match id={match_id} winner set: slot_id={slot_id}, winner_id={winner_id}")
        return match

    async def get_bracket(self, tournament_id: int):
        from app.crud.tournament import get_tournament_by_id
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from app.models.match import Match

        result = await self.db.execute(
            select(Tournament)
            .options(
                selectinload(Tournament.matches).selectinload(Match.player1),
                selectinload(Tournament.matches).selectinload(Match.player2),
                selectinload(Tournament.matches).selectinload(Match.bracket_winner),
            )
            .where(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()

        if not tournament:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")

        round_names = {1: "1/8 фіналу", 2: "Чвертьфінал", 3: "Півфінал", 4: "Фінал"}
        rounds: dict[int, list] = {1: [], 2: [], 3: [], 4: []}

        for match in tournament.matches:
            rounds[match.round].append({
                "match_id": match.id,
                "match_index": match.match_index,
                "slot_top_id": match.slot_top_id,
                "slot_bottom_id": match.slot_bottom_id,
                "player1": {"id": match.player1.id, "name": match.player1.name} if match.player1 else None,
                "player2": {"id": match.player2.id, "name": match.player2.name} if match.player2 else None,
                "winner": {"id": match.bracket_winner.id, "name": match.bracket_winner.name} if match.bracket_winner else None,
                "status": match.status,
            })

        return {
            "tournament_id": tournament_id,
            "name": tournament.name,
            "status": tournament.status,
            "rounds": {
                str(r): {"name": round_names[r], "matches": rounds[r]}
                for r in range(1, 5)
            },
        }