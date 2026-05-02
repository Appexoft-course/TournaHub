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

    #Схеми для турнірної сітки 

class BracketPlayerOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class MatchOut(BaseModel):
    id: int
    round: int
    match_index: int
    slot_top_id: str
    slot_bottom_id: str
    player1: Optional[BracketPlayerOut] = None
    player2: Optional[BracketPlayerOut] = None
    bracket_winner: Optional[BracketPlayerOut] = None
    status: str

    class Config:
        from_attributes = True


class TournamentOut(BaseModel):
    id: int
    name: str
    status: str
    matches: List[MatchOut] = []

    class Config:
        from_attributes = True


class StartTournamentRequest(BaseModel):
    # Список з рівно 16 user.id — будуть рандомно розподілені по сітці
    player_ids: List[int]


class SetWinnerRequest(BaseModel):
    # ID клітинки переможця: "R1_M0_TOP" або "R1_M0_BOT"
    slot_id: str