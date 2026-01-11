from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token
from app.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user
)
from app.config import get_settings
from app.logging_config import setup_logging, log_with_context, log_error

router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()
logger = setup_logging(service_name="auth_router", level="INFO")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class GoogleAuthRequest(BaseModel):
    id_token: str
    terms_accepted: bool = False
    terms_version: str = "1.0"
    privacy_accepted: bool = False
    privacy_version: str = "1.0"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        log_with_context(logger, "warning", "Registration failed - email already exists", email=user_data.email, event="registration_failed", reason="email_exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create new user with hashed password and accepted terms
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            terms_accepted=True,
            terms_accepted_at=datetime.utcnow(),
            terms_version="1.0",
            privacy_accepted=True,
            privacy_accepted_at=datetime.utcnow(),
            privacy_version="1.0"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        log_with_context(logger, "info", "User registered successfully", email=user_data.email, user_id=new_user.id, event="registration_success")
        return new_user
    except Exception as exc:
        log_error(logger, "Registration failed with exception", exc=exc, email=user_data.email, event="registration_error")
        raise


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and receive an access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        log_with_context(logger, "warning", "Login failed", email=form_data.username, event="login_failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token (terms will be checked in app after login)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(db, user.id)
    
    log_with_context(logger, "info", "User logged in successfully", email=user.email, user_id=user.id, event="login_success")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


class AcceptTermsRequest(BaseModel):
    email: str
    password: str
    terms_version: str = "1.0"
    privacy_version: str = "1.0"


@router.post("/accept-terms", response_model=Token)
def accept_terms(terms_data: AcceptTermsRequest, db: Session = Depends(get_db)):
    """Accept terms for existing user and get access token."""
    # Authenticate user
    user = authenticate_user(db, terms_data.email, terms_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update terms acceptance
    user.terms_accepted = True
    user.terms_accepted_at = datetime.utcnow()
    user.terms_version = terms_data.terms_version
    user.privacy_accepted = True
    user.privacy_accepted_at = datetime.utcnow()
    user.privacy_version = terms_data.privacy_version
    
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/google", response_model=Token)
def google_auth(auth_data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google ID token."""
    try:
        # Verify the Google ID token
        # Try to verify with web client ID first, then Android client ID
        idinfo = None
        last_error = None
        
        for client_id in [settings.google_client_id, settings.google_android_client_id]:
            try:
                idinfo = id_token.verify_oauth2_token(
                    auth_data.id_token,
                    requests.Request(),
                    client_id
                )
                break  # Successfully verified
            except ValueError as e:
                last_error = e
                continue  # Try next client ID
        
        if idinfo is None:
            raise ValueError(f'Token has wrong audience, expected one of [{settings.google_client_id}, {settings.google_android_client_id}]')
        
        # Get user email from token
        email = idinfo.get('email')
        if not email:
            log_with_context(logger, "warning", "Google auth failed - no email", event="google_auth_failed", reason="no_email")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Find or create user
        user = db.query(User).filter(User.email == email).first()
        is_new_user = user is None
        
        if not user:
            # Create new user with empty password (OAuth user)
            # Terms acceptance will be checked after login in the app
            user = User(
                email=email,
                hashed_password="",
                terms_accepted=auth_data.terms_accepted if auth_data.terms_accepted else False,
                terms_accepted_at=datetime.utcnow() if auth_data.terms_accepted else None,
                terms_version=auth_data.terms_version if auth_data.terms_accepted else None,
                privacy_accepted=auth_data.privacy_accepted if auth_data.privacy_accepted else False,
                privacy_accepted_at=datetime.utcnow() if auth_data.privacy_accepted else None,
                privacy_version=auth_data.privacy_version if auth_data.privacy_accepted else None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            log_with_context(logger, "info", "New user created via Google auth", email=email, user_id=user.id, event="google_registration_success")
        else:
            # For existing users, update terms if provided (but don't require)
            if auth_data.terms_accepted and not user.terms_accepted:
                user.terms_accepted = True
                user.terms_accepted_at = datetime.utcnow()
                user.terms_version = auth_data.terms_version
            
            if auth_data.privacy_accepted and not user.privacy_accepted:
                user.privacy_accepted = True
                user.privacy_accepted_at = datetime.utcnow()
                user.privacy_version = auth_data.privacy_version
            
            if auth_data.terms_accepted or auth_data.privacy_accepted:
                db.commit()
                db.refresh(user)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Create refresh token
        refresh_token = create_refresh_token(db, user.id)
        
            log_with_context(logger, "info", "Google auth successful", email=email, user_id=user.id, is_new_user=is_new_user, event="google_auth_success")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except ValueError as e:
        # Invalid token
            log_error(logger, "Google auth failed - invalid token", exc=e, event="google_auth_error", reason="invalid_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        # Other errors
            log_error(logger, "Google auth failed with exception", exc=e, event="google_auth_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/accept-terms-for-current-user")
def accept_terms_for_current_user(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept terms and privacy policy for the currently logged-in user.
    This is used when a user logs in but hasn't accepted the terms yet.
    """
    terms_version = request.get('terms_version', '1.0')
    privacy_version = request.get('privacy_version', '1.0')
    
    # Update user's terms acceptance
    current_user.terms_accepted = True
    current_user.terms_accepted_at = datetime.utcnow()
    current_user.terms_version = terms_version
    current_user.privacy_accepted = True
    current_user.privacy_accepted_at = datetime.utcnow()
    current_user.privacy_version = privacy_version
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Terms accepted successfully"}


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    token_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh an access token using a refresh token.
    Returns a new access token and refresh token.
    """
    # Verify the refresh token
    user = verify_refresh_token(db, token_request.refresh_token)
    
    if not user:
        log_with_context(logger, "warning", "Token refresh failed - invalid token", event="token_refresh_failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Create new refresh token (rotate refresh tokens for security)
    new_refresh_token = create_refresh_token(db, user.id)
    
    log_with_context(logger, "info", "Token refreshed successfully", email=user.email, user_id=user.id, event="token_refresh_success")
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

