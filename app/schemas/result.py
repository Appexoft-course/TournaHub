from pydantic import BaseModel
from typing import Optional


class MatchResultUpdate(BaseModel):
    score_1: int
    score_2: int
    mvp_id: Optional[int] = None


class MatchResultResponse(BaseModel):
    id: int
    score_1: int
    score_2: int
    winner: Optional[int]
    loser: Optional[int]
    mvp_id: Optional[int]

    class Config:
        from_attributes = True