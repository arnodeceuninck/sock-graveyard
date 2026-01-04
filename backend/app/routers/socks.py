import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Sock, Match
from app.schemas import SockResponse, SockMatch, MatchCreate, MatchResponse
from app.auth import get_current_user
from app.embedding import get_embedding_service, EmbeddingService
from app.config import get_settings

router = APIRouter(prefix="/socks", tags=["socks"])
settings = get_settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)


@router.post("/upload", response_model=SockResponse, status_code=status.HTTP_201_CREATED)
async def upload_sock(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    """Upload a sock image and create its embedding."""
    print(f"Received file: {file.filename}, content_type: {file.content_type}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create embedding
    try:
        # Reopen file for embedding creation
        with open(file_path, "rb") as img_file:
            embedding_bytes = embedding_service.create_embedding(img_file)
    except Exception as e:
        # Clean up file if embedding fails
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding: {str(e)}"
        )
    
    # Create sock record
    new_sock = Sock(
        owner_id=current_user.id,
        image_path=file_path,
        embedding=embedding_bytes
    )
    
    db.add(new_sock)
    db.commit()
    db.refresh(new_sock)
    
    return new_sock


@router.get("/list", response_model=List[SockResponse])
def list_unmatched_socks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all unmatched socks for the current user."""
    socks = db.query(Sock).filter(
        Sock.owner_id == current_user.id,
        Sock.is_matched == False
    ).all()
    
    return socks


@router.get("/matches")
def get_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all matches for the current user."""
    from sqlalchemy.orm import joinedload
    
    # Get all matches and eagerly load the sock relationships
    matches = db.query(Match).options(
        joinedload(Match.sock1),
        joinedload(Match.sock2)
    ).all()
    
    # Filter to only include matches where both socks belong to current user
    user_matches = []
    for m in matches:
        if m.sock1 and m.sock2 and m.sock1.owner_id == current_user.id and m.sock2.owner_id == current_user.id:
            user_matches.append({
                "id": m.id,
                "sock1_id": m.sock1_id,
                "sock2_id": m.sock2_id,
                "matched_at": m.matched_at.isoformat(),
                "sock1": {
                    "id": m.sock1.id,
                    "owner_id": m.sock1.owner_id,
                    "image_path": m.sock1.image_path,
                    "is_matched": m.sock1.is_matched,
                    "created_at": m.sock1.created_at.isoformat()
                },
                "sock2": {
                    "id": m.sock2.id,
                    "owner_id": m.sock2.owner_id,
                    "image_path": m.sock2.image_path,
                    "is_matched": m.sock2.is_matched,
                    "created_at": m.sock2.created_at.isoformat()
                }
            })
    
    return user_matches


@router.get("/matches/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Verify ownership
    if match.sock1.owner_id != current_user.id or match.sock2.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this match"
        )
    
    return match


@router.get("/{sock_id}", response_model=SockResponse)
def get_sock(
    sock_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific sock."""
    sock = db.query(Sock).filter(Sock.id == sock_id).first()
    
    if not sock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sock not found"
        )
    
    # Verify ownership
    if sock.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this sock"
        )
    
    return sock


@router.get("/{sock_id}/image")
def get_sock_image(
    sock_id: int,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get the image file for a specific sock. Supports token via query param for web compatibility."""
    from app.auth import get_user_from_token, get_current_user, oauth2_scheme
    from fastapi import Request
    
    # Try to get user from query parameter token first (for web img tags)
    current_user = None
    if token:
        current_user = get_user_from_token(token, db)
    
    # If no query token, this will fail with 401 if no Authorization header
    # (for API calls that use headers)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    sock = db.query(Sock).filter(Sock.id == sock_id).first()
    
    if not sock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sock not found"
        )
    
    # Verify ownership
    if sock.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this sock"
        )
    
    # Check if file exists
    if not os.path.exists(sock.image_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )
    
    # Return file with CORS headers for web compatibility
    return FileResponse(
        sock.image_path,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.post("/search", response_model=List[SockMatch])
async def search_similar_socks(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    limit: int = 10,
    exclude_sock_id: Optional[int] = Query(None, description="Sock ID to exclude from results")
):
    """Search for similar socks based on an uploaded image."""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Create embedding for the search image
    try:
        content = await file.read()
        # Create a temporary file-like object
        from io import BytesIO
        img_file = BytesIO(content)
        query_embedding_bytes = embedding_service.create_embedding(img_file)
        query_embedding = embedding_service.embedding_from_bytes(query_embedding_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding: {str(e)}"
        )
    
    # Get all unmatched socks from the current user
    socks = db.query(Sock).filter(
        Sock.owner_id == current_user.id,
        Sock.is_matched == False
    ).all()
    
    # Calculate similarities
    matches = []
    for sock in socks:
        # Skip the excluded sock if specified
        if exclude_sock_id and sock.id == exclude_sock_id:
            continue
            
        sock_embedding = embedding_service.embedding_from_bytes(sock.embedding)
        similarity = embedding_service.calculate_similarity(query_embedding, sock_embedding)
        matches.append(SockMatch(sock_id=sock.id, similarity=similarity))
    
    # Sort by similarity (highest first) and limit results
    matches.sort(key=lambda x: x.similarity, reverse=True)
    
    return matches[:limit]


@router.post("/match", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    match_data: MatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a match between two socks."""
    # Validate both socks exist and belong to the current user
    sock1 = db.query(Sock).filter(Sock.id == match_data.sock1_id).first()
    sock2 = db.query(Sock).filter(Sock.id == match_data.sock2_id).first()
    
    if not sock1 or not sock2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both socks not found"
        )
    
    if sock1.owner_id != current_user.id or sock2.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to match these socks"
        )
    
    # Check if socks are already matched
    if sock1.is_matched or sock2.is_matched:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or both socks are already matched"
        )
    
    # Check if the same sock
    if sock1.id == sock2.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot match a sock with itself"
        )
    
    # Create the match
    new_match = Match(
        sock1_id=match_data.sock1_id,
        sock2_id=match_data.sock2_id
    )
    
    # Update both socks as matched
    sock1.is_matched = True
    sock2.is_matched = True
    
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    # Ensure relationships are loaded
    _ = new_match.sock1
    _ = new_match.sock2
    
    return new_match
