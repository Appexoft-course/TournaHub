from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from typing import List, Optional


class GameEnum(str, Enum):
    chess = "chess"
    fifa = "fifa"
    table_tennis = "table_tennis"


class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=3)
    email: EmailStr

    description: Optional[str] = Field(default=None, min_length=3, max_length=150)

    favorite_games: List[GameEnum] = Field(default_factory=list)

class UserLogin(BaseModel):
    email: EmailStr
    password:str = Field(min_length=3)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponce(BaseModel):
    id:int
    name:str
    email:EmailStr
    is_active:bool
    description: str
    favorite_game:str
    elo:int
    win:int
    loses:int
    oauth_provider: str | None

class RegisterResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"



class RefreshRequest(BaseModel):
    refresh_token: str