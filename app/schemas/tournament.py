from pydantic import BaseModel
from typing import Optional, List

class MatchSchema(BaseModel):
    id: int
    player1_id: Optional[int]
    player2_id: Optional[int]
    winner_id: Optional[int]
    next_match_id: Optional[int]

    class Config:
        orm_mode = True

class TournamentSchema(BaseModel):
    id: int
    matches: List[MatchSchema]

    class Config:
        orm_mode = True
