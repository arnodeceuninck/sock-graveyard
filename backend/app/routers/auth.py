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
    get_current_user
)
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()


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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
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
    
    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and receive an access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
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
    
    return {"access_token": access_token, "token_type": "bearer"}


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
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/google", response_model=Token)
def google_auth(auth_data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google ID token."""
    try:
        # Verify the Google ID token
        # Accept tokens from both web and Android clients
        idinfo = id_token.verify_oauth2_token(
            auth_data.id_token,
            requests.Request(),
            settings.google_client_id
        )
        
        # Verify the token is for our app
        if idinfo['aud'] not in [settings.google_client_id, settings.google_android_client_id]:
            raise ValueError('Invalid audience.')
        
        # Get user email from token
        email = idinfo.get('email')
        if not email:
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
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        # Other errors
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

