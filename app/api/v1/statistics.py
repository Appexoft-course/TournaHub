from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.statistics_service import (
    get_user_statistics,
    get_all_users_statistics,
    get_leaderboard,
)

router = APIRouter()


@router.get("/users/{user_id}")
def user_stats(user_id: int, db: Session = Depends(get_db)):
    return get_user_statistics(db, user_id)


@router.get("/users")
def all_users_stats(db: Session = Depends(get_db)):
    return get_all_users_statistics(db)


@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    return get_leaderboard(db)