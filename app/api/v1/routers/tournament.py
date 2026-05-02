from fastapi import APIRouter,Depends
from app.schemas.tournament import CreateTournament
from app.services.tournament_service import TournamentService
from app.api.deps import get_tournament_service
from app.schemas.tournament import CreateTournament, StartTournamentRequest, SetWinnerRequest
router = APIRouter()

from app.api.deps import get_current_user

@router.post("/create")
async def create(
    data: CreateTournament,
    service: TournamentService = Depends(get_tournament_service),
    user = Depends(get_current_user)
):
    return await service.create(data, user.id)

    @router.post("/{tournament_id}/start")
async def start_bracket(
    tournament_id: int,
    data: StartTournamentRequest,
    service: TournamentService = Depends(get_tournament_service),
    user = Depends(get_current_user),
):
    return await service.start_bracket(tournament_id, data.player_ids)


@router.post("/{tournament_id}/matches/{match_id}/winner")
async def set_winner(
    tournament_id: int,
    match_id: int,
    body: SetWinnerRequest,
    service: TournamentService = Depends(get_tournament_service),
    user = Depends(get_current_user),
):
    return await service.set_match_winner(tournament_id, match_id, body.slot_id)


@router.get("/{tournament_id}/bracket")
async def get_bracket(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service),
    user = Depends(get_current_user),
):
    return await service.get_bracket(tournament_id)