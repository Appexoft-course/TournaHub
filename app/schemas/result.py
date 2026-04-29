from pydantic import BaseModel


class MatchResultUpdate(BaseModel):
    score_1: int
    score_2: int
    mvp_id: int | None = None