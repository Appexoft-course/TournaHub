from sqlalchemy.orm import Session

from app.models.user import User


def get_user_statistics(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise Exception("User not found")

    total_matches = user.wins + user.loses

    if total_matches == 0:
        winrate = 0
    else:
        winrate = round((user.wins / total_matches) * 100, 2)

    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "wins": user.wins,
        "loses": user.loses,
        "total_matches": total_matches,
        "winrate": winrate,
        "elo": user.elo,
        "rating": user.rating,
    }


def get_all_users_statistics(db: Session):
    users = db.query(User).all()

    result = []

    for user in users:
        total_matches = user.wins + user.loses

        if total_matches == 0:
            winrate = 0
        else:
            winrate = round((user.wins / total_matches) * 100, 2)

        result.append(
            {
                "user_id": user.id,
                "name": user.name,
                "wins": user.wins,
                "loses": user.loses,
                "total_matches": total_matches,
                "winrate": winrate,
                "elo": user.elo,
                "rating": user.rating,
            }
        )

    return result


def get_leaderboard(db: Session):
    users = db.query(User).order_by(User.wins.desc(), User.elo.desc()).all()

    leaderboard = []

    for index, user in enumerate(users, start=1):
        total_matches = user.wins + user.loses

        if total_matches == 0:
            winrate = 0
        else:
            winrate = round((user.wins / total_matches) * 100, 2)

        leaderboard.append(
            {
                "place": index,
                "user_id": user.id,
                "name": user.name,
                "wins": user.wins,
                "loses": user.loses,
                "total_matches": total_matches,
                "winrate": winrate,
                "elo": user.elo,
                "rating": user.rating,
            }
        )

    return leaderboard