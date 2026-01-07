from datetime import datetime, timedelta
from typing import Optional
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import TokenData

settings = get_settings()

# Password hashing with argon2 (includes salt automatically)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt (includes salt)."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user


def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Get user from a token string without raising exceptions."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
        user = db.query(User).filter(User.email == email).first()
        return user
    except JWTError:
        return None


def create_refresh_token(db: Session, user_id: int) -> str:
    """Create a refresh token and store it in the database."""
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    token_hash = pwd_context.hash(token)
    
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    db_token = RefreshToken(
        token_hash=token_hash,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return token


def validate_refresh_token(db: Session, token: str) -> Optional[User]:
    """Validate a refresh token and return the associated user."""
    # Find all refresh tokens and check each one (since we're hashing them)
    refresh_tokens = db.query(RefreshToken).filter(
        RefreshToken.expires_at > datetime.utcnow()
    ).all()
    
    for db_token in refresh_tokens:
        if pwd_context.verify(token, db_token.token_hash):
            # Update last_used_at
            db_token.last_used_at = datetime.utcnow()
            db.commit()
            return db_token.user
    
    return None


def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoke a specific refresh token."""
    refresh_tokens = db.query(RefreshToken).all()
    
    for db_token in refresh_tokens:
        if pwd_context.verify(token, db_token.token_hash):
            db.delete(db_token)
            db.commit()
            return True
    
    return False


def revoke_all_user_tokens(db: Session, user_id: int) -> None:
    """Revoke all refresh tokens for a user."""
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.commit()
