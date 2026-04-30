from fastapi import APIRouter,Depends
from app.schemas.tournament import CreateTournament
from app.services.tournament_service import TournamentService
from app.api.deps import get_tournament_service
router = APIRouter()

from app.api.deps import get_current_user

@router.post("/create")
async def create(
    data: CreateTournament,
    service: TournamentService = Depends(get_tournament_service),
    user = Depends(get_current_user)
):
    return await service.create(data, user.id)