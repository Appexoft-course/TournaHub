import math
from sqlalchemy.orm import Session
from models import User


def get_users(session: Session, id_winner: int, id_beaten: int):
    user1 = session.query(User).filter(User.id == id_winner).first()
    user2 = session.query(User).filter(User.id == id_beaten).first()
    return user1, user2

def classify_elo(elo: int) -> str:
    match elo:
        case range(0, 201):
            return "Beginner"
        case range(201, 400):
            return "Novice"
        case range(401, 801):
            return "Intermediate"
        case range(901, 1201):
            return "Advanced"
        case range(1201, 1501):
            return "Expert"
        case range(1501, 20001):
            return "Master"
        case _:
            return "Undefined"



def calculate_elo(user1, user2):
    difference = user1.elo - user2.elo
    new_elo_1 = user1.elo + math.floor(difference / 10) + 10 + math.floor(user1.win_streak/3)
    new_elo_2 = max(0, user2.elo - math.floor(difference / 10) - 10) 
    level_pl1 = classify_elo(new_elo_1)   
    level_pl2 = classify_elo(new_elo_2)        
    return new_elo_1, new_elo_2 ,level_pl1,level_pl2


def update_users(session: Session, user1, user2, new_elo_1, new_elo_2,level_pl1,level_pl2):
    user1.elo = new_elo_1
    user2.elo = new_elo_2
    user1.wins += 1
    user2.loses += 1
    user1.win_streak += 1
    user2.win_streak = 0
    user1.player_level = level_pl1
    user2.player_level = level_pl2
    session.commit()
    return None







    
