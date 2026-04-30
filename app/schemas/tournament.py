from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional,List
from enum import Enum

class GameEnum(str, Enum):
    chess = "chess"
    fifa = "fifa"
    table_tennis = "table_tennis"

class CreateTournament(BaseModel):
    name: str = Field (min_length=3)
    game_type : list[GameEnum]
    started_at: datetime
    end_at: datetime
    min_elo: int
    max_elo: int
    description:str
    max_players: int
    participant_ids: Optional[List[int]] = []

