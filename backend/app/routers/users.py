from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.auth import get_current_active_user
from app.database import get_db
from app.models import User as UserModel
from app.schemas import User
from app.logging_config import get_logger

logger = get_logger()
router = APIRouter()


@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get user by ID"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
