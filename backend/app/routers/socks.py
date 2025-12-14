import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.auth import get_current_active_user, get_user_from_token
from app.config import settings
from app.database import get_db
from app.models import User as UserModel, Sock as SockModel
from app.schemas import Sock, SockCreate, SockMatchResponse, SockMatch, MatchConfirmation
from app.services.image_preprocessing import image_preprocessor
from app.services.clip_embedding import clip_service
from app.db_utils import embedding_to_db, embedding_from_db, find_similar_socks
from app.logging_config import get_logger
import numpy as np

logger = get_logger()
router = APIRouter()


@router.post("/", response_model=Sock, status_code=status.HTTP_201_CREATED)
async def upload_sock(
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Upload a sock image
    - Preprocesses the image (background removal, cropping)
    - Generates CLIP embedding
    - Extracts visual features (color, pattern, texture)
    - Stores in database
    """
    try:
        logger.info(f"User {current_user.username} uploading sock image")
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read file
        image_bytes = await file.read()
        
        # Validate file size
        if len(image_bytes) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        original_ext = os.path.splitext(file.filename)[1] or '.jpg'
        original_filename = f"{file_id}_original{original_ext}"
        processed_filename = f"{file_id}_processed.jpg"
        
        original_path = os.path.join(settings.UPLOAD_DIR, original_filename)
        processed_path = os.path.join(settings.UPLOAD_DIR, processed_filename)
        
        # Save original image
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(original_path, 'wb') as f:
            f.write(image_bytes)
        
        logger.info(f"Original image saved: {original_path}")
        
        # Preprocess image
        processed_path, error = await image_preprocessor.preprocess_image(
            image_bytes, processed_path
        )
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image preprocessing failed: {error}"
            )
        
        logger.info(f"Image preprocessed: {processed_path}")
        
        # Generate embedding
        embedding = await clip_service.generate_embedding(processed_path)
        
        if embedding is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate embedding"
            )
        
        logger.info("Embedding generated successfully")
        
        # Extract features
        features = await clip_service.extract_features(processed_path)
        
        logger.info(f"Features extracted: {features.get('pattern_type')}, {features.get('dominant_color')}")
        
        # Create sock record
        sock = SockModel(
            user_id=current_user.id,
            image_path=original_path,
            preprocessed_image_path=processed_path,
            embedding=embedding_to_db(embedding),  # Convert to DB format (JSON for SQLite, list for PostgreSQL)
            dominant_color=features.get('dominant_color'),
            pattern_type=features.get('pattern_type'),
            texture_features=features.get('texture_features'),
            description=description
        )
        
        db.add(sock)
        db.commit()
        db.refresh(sock)
        
        logger.info(f"Sock {sock.id} created successfully for user {current_user.username}")
        
        return sock
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sock upload failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload sock: {str(e)}"
        )


@router.get("/", response_model=List[Sock])
async def list_socks(
    skip: int = 0,
    limit: int = 100,
    unmatched_only: bool = False,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """List user's socks"""
    query = db.query(SockModel).filter(SockModel.user_id == current_user.id)
    
    if unmatched_only:
        query = query.filter(SockModel.is_matched == False)
    
    socks = query.offset(skip).limit(limit).all()
    
    logger.info(f"Retrieved {len(socks)} socks for user {current_user.username}")
    
    return socks


@router.get("/{sock_id}", response_model=Sock)
async def get_sock(
    sock_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get a specific sock"""
    sock = db.query(SockModel).filter(
        SockModel.id == sock_id,
        SockModel.user_id == current_user.id
    ).first()
    
    if not sock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sock not found"
        )
    
    return sock


@router.get("/{sock_id}/image")
async def get_sock_image(
    sock_id: int,
    processed: bool = False,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get sock image
    
    Supports authentication via:
    - Authorization header (Bearer token) - preferred
    - Query parameter 'token' - fallback for environments that don't support headers (e.g., web Image component)
    """
    # Try to get user from query token first, then fall back to header
    try:
        if token:
            current_user = await get_user_from_token(token, db)
        else:
            # Try to get from header
            from fastapi.security import OAuth2PasswordBearer
            oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
            from app.auth import get_current_user
            # This requires the Authorization header
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Provide token via Authorization header or 'token' query parameter."
            )
    except HTTPException:
        raise
    
    sock = db.query(SockModel).filter(
        SockModel.id == sock_id,
        SockModel.user_id == current_user.id
    ).first()
    
    if not sock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sock not found"
        )
    
    image_path = sock.preprocessed_image_path if processed else sock.image_path
    
    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )
    
    return FileResponse(image_path)


@router.post("/search", response_model=SockMatchResponse)
async def search_similar_socks(
    sock_id: int,
    threshold: float = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Search for similar socks using vector similarity
    """
    try:
        # Get the query sock
        query_sock = db.query(SockModel).filter(
            SockModel.id == sock_id,
            SockModel.user_id == current_user.id
        ).first()
        
        if not query_sock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sock not found"
            )
        
        if query_sock.is_matched:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This sock is already matched"
            )
        
        logger.info(f"Searching for matches for sock {sock_id}")
        
        # Get all unmatched socks (excluding the query sock)
        candidate_socks = db.query(SockModel).filter(
            and_(
                SockModel.is_matched == False,
                SockModel.id != sock_id,
                SockModel.user_id == current_user.id
            )
        ).all()
        
        if not candidate_socks:
            logger.info("No candidate socks found")
            return SockMatchResponse(matches=[], total=0)
        
        # Calculate similarities
        query_embedding = embedding_from_db(query_sock.embedding)
        matches = []
        
        for candidate in candidate_socks:
            candidate_embedding = embedding_from_db(candidate.embedding)
            similarity = clip_service.calculate_similarity(query_embedding, candidate_embedding)
            
            # Apply threshold
            threshold_value = threshold if threshold is not None else settings.MATCH_THRESHOLD
            if similarity >= threshold_value:
                # Calculate match score (can be enhanced with feature matching)
                match_score = similarity
                
                matches.append(SockMatch(
                    sock=candidate,
                    similarity=similarity,
                    match_score=match_score
                ))
        
        # Sort by match score
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        # Limit results
        matches = matches[:limit]
        
        logger.info(f"Found {len(matches)} matches for sock {sock_id}")
        
        return SockMatchResponse(matches=matches, total=len(matches))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/match", status_code=status.HTTP_200_OK)
async def confirm_match(
    match: MatchConfirmation,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Confirm a match between two socks
    Both socks will be marked as matched
    """
    try:
        # Get both socks
        sock1 = db.query(SockModel).filter(
            SockModel.id == match.sock_id_1,
            SockModel.user_id == current_user.id
        ).first()
        
        sock2 = db.query(SockModel).filter(
            SockModel.id == match.sock_id_2,
            SockModel.user_id == current_user.id
        ).first()
        
        if not sock1 or not sock2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both socks not found"
            )
        
        if sock1.is_matched or sock2.is_matched:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or both socks are already matched"
            )
        
        # Update both socks
        sock1.is_matched = True
        sock1.matched_with_id = sock2.id
        
        sock2.is_matched = True
        sock2.matched_with_id = sock1.id
        
        db.commit()
        
        logger.info(f"Match confirmed: sock {match.sock_id_1} <-> sock {match.sock_id_2}")
        
        return {
            "message": "Match confirmed successfully",
            "sock_id_1": match.sock_id_1,
            "sock_id_2": match.sock_id_2
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Match confirmation failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match confirmation failed: {str(e)}"
        )


@router.delete("/{sock_id}", status_code=status.HTTP_200_OK)
async def delete_sock(
    sock_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Remove a sock from the graveyard
    If the sock was matched, unmatches the pair
    """
    try:
        sock = db.query(SockModel).filter(
            SockModel.id == sock_id,
            SockModel.user_id == current_user.id
        ).first()
        
        if not sock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sock not found"
            )
        
        # If matched, unmatch the pair
        if sock.is_matched and sock.matched_with_id:
            matched_sock = db.query(SockModel).filter(
                SockModel.id == sock.matched_with_id
            ).first()
            
            if matched_sock:
                matched_sock.is_matched = False
                matched_sock.matched_with_id = None
                logger.info(f"Unmatched sock {matched_sock.id}")
        
        # Delete image files
        try:
            if os.path.exists(sock.image_path):
                os.remove(sock.image_path)
            if sock.preprocessed_image_path and os.path.exists(sock.preprocessed_image_path):
                os.remove(sock.preprocessed_image_path)
        except Exception as e:
            logger.warning(f"Failed to delete image files: {e}")
        
        # Delete sock
        db.delete(sock)
        db.commit()
        
        logger.info(f"Sock {sock_id} deleted successfully")
        
        return {"message": "Sock deleted successfully", "sock_id": sock_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sock deletion failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sock deletion failed: {str(e)}"
        )
