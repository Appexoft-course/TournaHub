# models/tournament.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    round = Column(Integer, nullable=False)
    slot_id = Column(Integer, nullable=False)

    player1_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])
    winner = relationship("User", foreign_keys=[winner_id])

participants = relationship(
    "TournamentParticipant", back_populates="tournament", cascade="all, delete-orphan"
)
