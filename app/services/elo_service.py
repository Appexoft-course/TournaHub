import math
from sqlalchemy.orm import Session
from models import User


def get_users(session: Session, id_1_winner: int, id_2_beaten: int):
    user1 = session.query(User).filter(User.id == id_1_winner).first()
    user2 = session.query(User).filter(User.id == id_2_beaten).first()
    return user1, user2


def calculate_elo(user1, user2):
    difference = user1.elo - user2.elo
    new_elo_1 = user1.elo + math.floor(difference / 10) + 10
    new_elo_2 = max(0, user2.elo - math.floor(difference / 10) - 10)
    return new_elo_1, new_elo_2


def update_users(session: Session, user1, user2, new_elo_1, new_elo_2):
    user1.elo = new_elo_1
    user2.elo = new_elo_2
    user1.wins += 1
    user2.loses += 1
    session.commit()
    return new_elo_1, new_elo_2







    
