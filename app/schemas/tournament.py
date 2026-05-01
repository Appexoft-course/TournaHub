from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Annotated
from enum import Enum
from annotated_types import Ge, Le


class GameEnum(str, Enum):
    chess = "chess"
    fifa = "fifa"
    table_tennis = "table_tennis"


class CreateTournament(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    game_type: list[GameEnum]
    started_at: datetime
    end_at: datetime
    min_elo: int = Field(default=0, ge=0)
    max_elo: int = Field(default=9999, ge=0)
    description: Optional[str] = None
    max_players: Annotated[int, Ge(2), Le(16)]
    participant_ids: Optional[List[int]] = []