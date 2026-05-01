from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.tournament import TournamentSchema, MatchSchema
from app.services.tournament_service import create_tournament, set_winner
from app.models.user import User
from app.models.tournament import Tournament, Match

router = APIRouter(prefix="/tournament", tags=["Tournament"])

# POST: створення турніру
@router.post("/create", response_model=TournamentSchema)
def create(players: list[int], db: Session = Depends(get_db)):
    users = db.query(User).filter(User.id.in_(players)).all()
    if len(users) > 16:
        raise HTTPException(status_code=400, detail="Максимум 16 гравців")
    tournament = create_tournament(db, users)
    return tournament

# POST: встановити переможця матчу
@router.post("/match/{match_id}/winner", response_model=MatchSchema)
def winner(match_id: int, winner_id: int, db: Session = Depends(get_db)):
    match = set_winner(db, match_id, winner_id)
    if not match:
        raise HTTPException(status_code=404, detail="Матч не знайдено")
    return match

# GET: отримати турнір по id
@router.get("/{tournament_id}", response_model=TournamentSchema)
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Турнір не знайдено")
    return tournament

# GET: отримати матч по id
@router.get("/match/{match_id}", response_model=MatchSchema)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Матч не знайдено")
    return match
