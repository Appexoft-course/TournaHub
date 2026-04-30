from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.tournament_participant import TournamentParticipant

class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    tournament_id = Column(Integer, ForeignKey("tournaments.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="tournament_participations")
    tournament = relationship("Tournament", back_populates="participants")
