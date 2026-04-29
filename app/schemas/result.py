from pydantic import BaseModel
from typing import Optional
from typing import Optional

from pydantic import BaseModel, Field


class MatchResultUpdate(BaseModel):
    score_1: int = Field(ge=0)
    score_2: int = Field(ge=0)
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