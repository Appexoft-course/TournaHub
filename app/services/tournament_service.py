from sqlalchemy.orm import Session
from app.models.tournament import Tournament, Match
from app.models.user import User

def create_tournament(db: Session, players: list[User]) -> Tournament:
    tournament = Tournament()
    db.add(tournament)
    db.commit()
    db.refresh(tournament)

    match_id = 1
    round_matches = []
    for i in range(0, 16, 2):
        m = Match(
            id=match_id,
            tournament_id=tournament.id,
            player1_id=players[i].id if i < len(players) else None,
            player2_id=players[i+1].id if i+1 < len(players) else None
        )
        db.add(m)
        round_matches.append(m)
        match_id += 1

    current_round = round_matches
    while len(current_round) > 1:
        next_round = []
        for i in range(0, len(current_round), 2):
            m = Match(id=match_id, tournament_id=tournament.id)
            db.add(m)
            current_round[i].next_match_id = m.id
            current_round[i+1].next_match_id = m.id
            next_round.append(m)
            match_id += 1
        current_round = next_round

    db.commit()
    db.refresh(tournament)
    return tournament

def set_winner(db: Session, match_id: int, winner_id: int):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return None
    match.winner_id = winner_id
    if match.next_match_id:
        next_match = db.query(Match).filter(Match.id == match.next_match_id).first()
        if not next_match.player1_id:
            next_match.player1_id = winner_id
        elif not next_match.player2_id:
            next_match.player2_id = winner_id
    db.commit()
    return match
