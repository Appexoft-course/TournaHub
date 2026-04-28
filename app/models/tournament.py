from sqlalchemy import Column, DateTime, Integer, String, Text

 
from app.db.base import Base
 
 
class Tournament(Base):
    __tablename__ = "tournaments"
 
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    game_type = Column(String(100), nullable=False)
    team_id = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    min_elo = Column(Integer, default=0)
    max_elo = Column(Integer, default=9999)
    description = Column(Text, nullable=True)
    max_players = Column(Integer, nullable=False)
 
