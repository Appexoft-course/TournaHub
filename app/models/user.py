
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.tournament_participant import tournament_participants 
 
from app.db.base import Base
 
 
class User(Base):
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    favorite_games = Column(ARRAY(String), nullable=True)
    elo = Column(Integer, default=400)
    wins = Column(Integer, default=0)
    loses = Column(Integer, default=0)
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, unique=True, nullable=True)
    refresh_token = Column(String, nullable=True)
 
    friendships = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id",
        back_populates="user"
    )
    friend_of = relationship("Friendship", foreign_keys="Friendship.friend_id", back_populates="friend")
    tournaments = relationship(
        "Tournament",
        secondary=tournament_participants,
        back_populates="participants"
    )
    
    __allow_unmapped__ = True
