from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.result import MatchResultUpdate
from app.services.result_service import update_match_result

router = APIRouter()


@router.patch("/matches/{match_id}")
async def update_result(
    match_id: int,
    data: MatchResultUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_match_result(
        db=db,
        match_id=match_id,
        score_1=data.score_1,
        score_2=data.score_2,
        mvp_id=data.mvp_id,
    )