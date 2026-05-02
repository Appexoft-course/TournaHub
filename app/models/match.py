from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class MatchStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
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

    # ── турнірна сітка ──────────────────────────────────────────
    tournament_id = Column(Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=True)

    # Раунд: 1=1/8 фіналу, 2=чвертьфінал, 3=півфінал, 4=фінал
    round = Column(Integer, nullable=True)

    # Індекс матчу у раунді (0-based): раунд 1 → 0..7, раунд 2 → 0..3, і тд
    match_index = Column(Integer, nullable=True)

    # Унікальні ID клітинок сітки. Формат: R{round}_M{match_index}_{TOP|BOT}
    # Приклад: "R1_M0_TOP", "R2_M3_BOT"
    slot_top_id = Column(String, nullable=True)     # верхня клітинка = player1
    slot_bottom_id = Column(String, nullable=True)  # нижня клітинка = player2

    # Гравці матчу (FK на users)
    player1_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    player2_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    bracket_winner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Статус матчу в сітці
    status = Column(Enum(MatchStatus), default=MatchStatus.pending, nullable=False)

    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])
    bracket_winner = relationship("User", foreign_keys=[bracket_winner_id])