from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class SockResponse(BaseModel):
    id: int
    user_sequence_id: int
    image_path: str
    is_matched: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SockMatch(BaseModel):
    sock_id: int
    similarity: float
    
    class Config:
        from_attributes = True


class MatchCreate(BaseModel):
    sock1_id: int
    sock2_id: int


class MatchResponse(BaseModel):
    id: int
    user_sequence_id: int
    sock1_id: int
    sock2_id: int
    matched_at: datetime
    sock1: SockResponse
    sock2: SockResponse
    
    class Config:
        from_attributes = True
