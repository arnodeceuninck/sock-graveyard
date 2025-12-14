from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.database import get_db
from app.models import User as UserModel
from app.schemas import TokenData
from app.logging_config import get_logger

logger = get_logger()

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    # Truncate to 72 bytes to comply with bcrypt limit
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        logger.warning(
            f"Password truncated during verification: "
            f"original length={len(password_bytes)} bytes ({len(plain_password)} chars), "
            f"password='{plain_password}'"
        )
        # Decode back to string after truncation, handling potential incomplete UTF-8 sequences
        password_to_use = password_bytes[:72].decode('utf-8', errors='ignore')
    else:
        password_to_use = plain_password
    return pwd_context.verify(password_to_use, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Truncate to 72 bytes to comply with bcrypt limit
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        logger.warning(
            f"Password truncated during hashing: "
            f"original length={len(password_bytes)} bytes ({len(password)} chars), "
            f"password='{password}'"
        )
        # Decode back to string after truncation, handling potential incomplete UTF-8 sequences
        password_to_use = password_bytes[:72].decode('utf-8', errors='ignore')
    else:
        password_to_use = password
    return pwd_context.hash(password_to_use)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserModel]:
    """Authenticate a user"""
    user = db.query(UserModel).filter(UserModel.username == username).first()
    
    if not user:
        logger.warning(f"Authentication failed: user {username} not found")
        return None
    
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: invalid password for user {username}")
        return None
    
    logger.info(f"User {username} authenticated successfully")
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    """Get the current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            logger.error("Token payload missing 'sub' field")
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    
    user = db.query(UserModel).filter(UserModel.username == token_data.username).first()
    
    if user is None:
        logger.error(f"User {token_data.username} not found")
        raise credentials_exception
    
    if not user.is_active:
        logger.error(f"User {token_data.username} is inactive")
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
