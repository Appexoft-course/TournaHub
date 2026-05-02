from sqlalchemy.orm import Session
from app.models.match import Match

def create_match(
    db: Session,
    game_type: str,
    team_1: int,
    team_2: int,
    started_at,
    end_at,
):
  
    match = Match(
        game_type=game_type,  
        started_at=started_at, 
        end_at=end_at,      
        team_1=team_1,       
        team_2=team_2,                  
    )


    db.add(match)
    db.commit()
    db.refresh(match)
    return match
