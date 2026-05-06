from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.result import MatchResultUpdate, MatchResultResponse
from app.services.result_service import update_match_result

router = APIRouter()


@router.patch("/matches/{match_id}", response_model=MatchResultResponse)
async def update_result(
    match_id: int,
    result_data: MatchResultUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_match = await update_match_result(
        db=db,
        match_id=match_id,
        score_1=result_data.score_1,
        score_2=result_data.score_2,
        mvp_id=result_data.mvp_id,
    )

    await manager.broadcast(
        {
            "type": "match_result_updated",
            "match_id": updated_match.id,
            "score_1": updated_match.score_1,
            "score_2": updated_match.score_2,
            "winner": updated_match.winner,
            "loser": updated_match.loser,
            "mvp_id": updated_match.mvp_id,
        }
    )

    return updated_match

@router.websocket("/ws/matches/results")
async def match_results_websocket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)