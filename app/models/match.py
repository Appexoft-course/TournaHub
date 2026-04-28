
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base
 
 
class Match(Base):
    __tablename__ = "matches"
 
    id = Column(Integer, primary_key=True, index=True)
    game_type = Column(String(100), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    score_1 = Column(Integer, default=0)
    score_2 = Column(Integer, default=0)
    team_1 = Column(Integer, nullable=True)
    team_2 = Column(Integer, nullable=True)
    winner = Column(Integer, nullable=True)
    loser = Column(Integer, nullable=True)
 
    mvp_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    mvp = relationship("User", foreign_keys=[mvp_id])
 
