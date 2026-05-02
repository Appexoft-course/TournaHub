from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.base import Base

tournament_participants = Table(
    "tournament_participants",
    Base.metadata,
    Column("tournament_id", Integer, ForeignKey("tournaments.id", ondelete="CASCADE")),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
)