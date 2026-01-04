import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Header
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Sock, Match
from app.schemas import SockResponse, SockMatch, MatchCreate, MatchResponse
from app.auth import get_current_user
from app.embedding import get_embedding_service, EmbeddingService
from app.config import get_settings

router = APIRouter(prefix="/singles", tags=["singles"])
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
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get the image file for a specific sock. Supports token via query param for web or Authorization header."""
    from app.auth import get_user_from_token
    
    current_user = None
    
    # Try query parameter token first (for web img tags)
    if token:
        current_user = get_user_from_token(token, db)
    # Try Authorization header (for mobile/API requests)
    elif authorization and authorization.startswith("Bearer "):
        token_from_header = authorization.replace("Bearer ", "")
        current_user = get_user_from_token(token_from_header, db)
    
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


@router.get("/{sock_id}/search", response_model=List[SockMatch])
async def search_by_sock_id(
    sock_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    limit: int = 10
):
    """Search for similar socks using an existing sock's embedding."""
    # Get the source sock
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
    
    # Get the embedding
    query_embedding = embedding_service.embedding_from_bytes(sock.embedding)
    
    # Get all unmatched socks from the current user (excluding this one)
    socks = db.query(Sock).filter(
        Sock.owner_id == current_user.id,
        Sock.is_matched == False,
        Sock.id != sock_id
    ).all()
    
    # Calculate similarities
    matches = []
    for other_sock in socks:
        sock_embedding = embedding_service.embedding_from_bytes(other_sock.embedding)
        similarity = embedding_service.calculate_similarity(query_embedding, sock_embedding)
        matches.append(SockMatch(sock_id=other_sock.id, similarity=similarity))
    
    # Sort by similarity (highest first) and limit results
    matches.sort(key=lambda x: x.similarity, reverse=True)
    
    return matches[:limit]


@router.delete("/{sock_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sock(
    sock_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a sock and its image file."""
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
            detail="Not authorized to delete this sock"
        )
    
    # Check if sock is matched
    if sock.is_matched:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a matched sock. Delete the match first."
        )
    
    # Delete the image file if it exists
    if os.path.exists(sock.image_path):
        try:
            os.remove(sock.image_path)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Failed to delete image file {sock.image_path}: {str(e)}")
    
    # Delete the sock from database
    db.delete(sock)
    db.commit()
    
    return None
