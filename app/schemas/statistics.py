from typing import Optional

from pydantic import BaseModel


class UserStatisticsResponse(BaseModel):
    user_id: int
    name: str
    email: Optional[str] = None
    wins: int
    loses: int
    total_matches: int
    winrate: float
    elo: int


class LeaderboardUserResponse(UserStatisticsResponse):
    place: int