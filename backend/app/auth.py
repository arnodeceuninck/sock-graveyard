from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import TokenData
from app.logging_config import setup_logging, log_with_context, log_error
import secrets

settings = get_settings()
logger = setup_logging(service_name="auth", level="INFO")

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


def create_refresh_token(db: Session, user_id: int) -> str:
    """Create a refresh token for a user."""
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    
    # Calculate expiry
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    # Store in database
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        revoked=False
    )
    db.add(refresh_token)
    db.commit()
    
    return token


def verify_refresh_token(db: Session, token: str) -> Optional[User]:
    """Verify a refresh token and return the associated user."""
    refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    
    if not refresh_token:
        return None
    
    # Check if token is revoked
    if refresh_token.revoked:
        return None
    
    # Check if token is expired
    if refresh_token.expires_at < datetime.utcnow():
        return None
    
    # Get the user
    user = db.query(User).filter(User.id == refresh_token.user_id).first()
    return user


def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoke a refresh token."""
    refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    
    if not refresh_token:
        return False
    
    refresh_token.revoked = True
    db.commit()
    return True


def revoke_all_user_refresh_tokens(db: Session, user_id: int) -> None:
    """Revoke all refresh tokens for a user."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    db.commit()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        log_with_context(logger, "warning", "Authentication failed - user not found", email=email, event="auth_failed", reason="user_not_found")
        return None
    # For OAuth users (no password), only authenticate via OAuth
    if not user.hashed_password:
        log_with_context(logger, "warning", "Authentication failed - OAuth user", email=email, event="auth_failed", reason="oauth_user")
        return None
    if not verify_password(password, user.hashed_password):
        log_with_context(logger, "warning", "Authentication failed - invalid password", email=email, event="auth_failed", reason="invalid_password")
        return None
    log_with_context(logger, "info", "User authenticated successfully", email=email, user_id=user.id, event="auth_success")
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
            log_with_context(logger, "warning", "Invalid token - missing email", event="token_validation_failed", reason="missing_email")
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        log_with_context(logger, "warning", "Invalid token - JWT error", event="token_validation_failed", reason="jwt_error")
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        log_with_context(logger, "warning", "User not found for token", email=token_data.email, event="token_validation_failed", reason="user_not_found")
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
