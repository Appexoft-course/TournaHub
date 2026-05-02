from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from app.models.tournament_participant import tournament_participants
from sqlalchemy.orm import relationship
from app.db.base import Base


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    game_type = Column(ARRAY(String), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    min_elo = Column(Integer, default=0)
    max_elo = Column(Integer, default=9999)
    description = Column(Text, nullable=True)
    max_players = Column(Integer, nullable=False)

    participants = relationship(
        "User",
        secondary=tournament_participants,
        back_populates="tournaments"
    )