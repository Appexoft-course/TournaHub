
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
 
from app.db.base import Base
 
 
class User(Base):
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    rating = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    favorite_games = Column(ARRAY(String), nullable=True)
    team = Column(Integer, nullable=True)
    elo = Column(Integer, default=1000)
    wins = Column(Integer, default=0)
    loses = Column(Integer, default=0)
 
    friendships = relationship("Friendship", foreign_keys="Friendship.user_id", back_populates="user")
    friend_of = relationship("Friendship", foreign_keys="Friendship.friend_id", back_populates="friend")
 
