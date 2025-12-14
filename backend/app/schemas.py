from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Sock Schemas
class SockBase(BaseModel):
    description: Optional[str] = None


class SockCreate(SockBase):
    pass


class SockFeatures(BaseModel):
    dominant_color: Optional[str] = None
    pattern_type: Optional[str] = None
    texture_features: Optional[str] = None


class Sock(SockBase):
    id: int
    user_id: int
    image_path: str
    preprocessed_image_path: Optional[str] = None
    dominant_color: Optional[str] = None
    pattern_type: Optional[str] = None
    is_matched: bool
    matched_with_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SockMatch(BaseModel):
    sock: Sock
    similarity: float
    match_score: float


class SockMatchResponse(BaseModel):
    matches: List[SockMatch]
    total: int


class MatchConfirmation(BaseModel):
    sock_id_1: int
    sock_id_2: int


# Health Check
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
