import secrets
import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.tournament import CreateTournament
from app.core.logging import setup_logging
from app.crud.tournament import create_tournament

class TournamentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = setup_logging()


    async def create(self,data:CreateTournament,owner_id:str):
        tour = await create_tournament(self.db,data,owner_id)

        return tour