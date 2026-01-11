import os
import uuid
import hashlib
import json
import time
from io import BytesIO
from typing import List, Optional
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Header, BackgroundTasks
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from PIL import Image
from rembg import remove
from sklearn.cluster import KMeans
import numpy as np
from app.database import get_db
from app.models import User, Sock, Match
from app.schemas import SockResponse, SockMatch, MatchCreate, MatchResponse
from app.auth import get_current_user
from app.embedding import get_embedding_service, EmbeddingService
from app.config import get_settings
from app.logging_config import setup_logging, log_with_context, log_error

router = APIRouter(prefix="/singles", tags=["singles"])
settings = get_settings()
logger = setup_logging(service_name="singles", level="INFO")

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)


def extract_color_palette(image: Image.Image, num_colors: int = 5) -> List[str]:
    """
    Extract dominant and distinctive colors from an image with transparent background.
    Captures both common colors and important accent colors.
    Returns a list of hex color codes.
    """
    try:
        # Convert to RGB if needed (handling RGBA)
        if image.mode == 'RGBA':
            # Get only non-transparent pixels
            pixels = []
            for x in range(image.width):
                for y in range(image.height):
                    pixel = image.getpixel((x, y))
                    # Only include pixels with significant alpha (not transparent)
                    if pixel[3] > 128:  # Alpha channel > 128 (50% opacity)
                        pixels.append(pixel[:3])  # Take only RGB, ignore alpha
            
            if not pixels:
                return []
            
            # Convert to numpy array
            pixels_array = np.array(pixels)
        else:
            # If not RGBA, convert to RGB
            image_rgb = image.convert('RGB')
            pixels_array = np.array(image_rgb).reshape(-1, 3)
        
        # Extract more colors initially to capture accent colors
        initial_colors = min(15, len(pixels_array))
        if len(pixels_array) < initial_colors:
            initial_colors = max(1, len(pixels_array))
        
        kmeans = KMeans(n_clusters=initial_colors, random_state=42, n_init=10)
        kmeans.fit(pixels_array)
        
        # Get the colors with their frequencies
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_
        label_counts = Counter(labels)
        
        def color_distance(c1, c2):
            """Calculate Euclidean distance between two colors."""
            return np.sqrt(np.sum((c1 - c2) ** 2))
        
        def color_saturation(color):
            """Calculate color saturation (how vibrant/distinct it is)."""
            r, g, b = color / 255.0
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            if max_val == 0:
                return 0
            return (max_val - min_val) / max_val
        
        # Create list of colors with metadata
        color_data = []
        for i in range(len(colors)):
            color = colors[i]
            frequency = label_counts[i]
            saturation = color_saturation(color)
            # Score combines frequency and saturation to capture both common and vibrant colors
            # Boost saturation importance to catch accent colors
            score = (frequency ** 0.7) * (1 + saturation * 2)
            color_data.append({
                'color': color,
                'frequency': frequency,
                'saturation': saturation,
                'score': score
            })
        
        # Sort by score (balances frequency and distinctiveness)
        color_data.sort(key=lambda x: x['score'], reverse=True)
        
        # Ensure highly saturated colors (accent colors) are prioritized
        # Separate high saturation colors and prioritize them
        high_sat_colors = [d for d in color_data if d['saturation'] > 0.4]
        low_sat_colors = [d for d in color_data if d['saturation'] <= 0.4]
        
        # Select diverse colors - avoid very similar colors
        selected_colors = []
        min_distance = 30  # Reduced threshold to allow more color variation
        
        # First pass: Add high saturation (vibrant) colors to ensure accent colors are included
        for data in high_sat_colors:
            color = data['color']
            # Check if this color is sufficiently different from already selected colors
            is_distinct = True
            for selected in selected_colors:
                if color_distance(color, selected) < min_distance:
                    is_distinct = False
                    break
            
            if is_distinct:
                selected_colors.append(color)
            
            # Stop if we have enough colors
            if len(selected_colors) >= num_colors:
                break
        
        # Second pass: Fill remaining slots with less saturated (base) colors
        for data in low_sat_colors:
            if len(selected_colors) >= num_colors:
                break
                
            color = data['color']
            # Check if this color is sufficiently different from already selected colors
            is_distinct = True
            for selected in selected_colors:
                if color_distance(color, selected) < min_distance:
                    is_distinct = False
                    break
            
            if is_distinct:
                selected_colors.append(color)
        
        # Convert to hex codes
        hex_colors = []
        for color in selected_colors:
            r, g, b = color.astype(int)
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            hex_colors.append(hex_color)
        
        return hex_colors
    except Exception as e:
        print(f"Failed to extract color palette: {str(e)}")
        return []


def process_background_removal(sock_id: int, file_path: str, upload_dir: str):
    """Background task to remove background from uploaded sock image."""
    start_time = time.time()
    try:
        # Generate filename for background-removed version
        unique_filename_no_bg = f"{uuid.uuid4()}_no_bg.png"
        file_path_no_bg = os.path.join(upload_dir, unique_filename_no_bg)
        
        # Create background-removed version
        with open(file_path, "rb") as img_file:
            input_image = Image.open(img_file)
            output_image = remove(input_image)
            
            # Crop the image to the bounding box of non-transparent pixels
            bbox = output_image.getbbox()
            if bbox:
                output_image = output_image.crop(bbox)
            
            output_image.save(file_path_no_bg, "PNG")
        
        # Extract color palette from the background-removed image
        color_palette = extract_color_palette(output_image, num_colors=5)
        color_palette_json = json.dumps(color_palette) if color_palette else None
        
        # Update the database with the background-removed image path and color palette
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            sock = db.query(Sock).filter(Sock.id == sock_id).first()
            if sock:
                sock.image_no_bg_path = file_path_no_bg
                sock.color_palette = color_palette_json
                db.commit()
                duration_ms = (time.time() - start_time) * 1000
                log_with_context(logger, "info", "Background removal completed", 
                    sock_id=sock_id, 
                    colors_found=len(color_palette) if color_palette else 0,
                    duration_ms=round(duration_ms, 2),
                    event="background_removal_success")
        finally:
            db.close()
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_error(logger, "Background removal failed", exc=e, 
            sock_id=sock_id, 
            duration_ms=round(duration_ms, 2),
            event="background_removal_error")


@router.post("/upload", response_model=SockResponse, status_code=status.HTTP_201_CREATED)
async def upload_sock(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    """Upload a sock image and create its embedding."""
    start_time = time.time()
    log_with_context(logger, "info", "Sock upload started", 
        user_id=current_user.id, 
        filename=file.filename, 
        content_type=file.content_type,
        event="upload_started")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        log_with_context(logger, "warning", "Invalid file type", 
            user_id=current_user.id, 
            content_type=file.content_type,
            event="upload_failed", 
            reason="invalid_type")
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
        if os.path.exists(file_path):
            os.remove(file_path)
        log_error(logger, "Embedding creation failed", exc=e, 
            user_id=current_user.id, 
            filename=file.filename,
            event="embedding_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding: {str(e)}"
        )
    
    # Get the next sequence ID for this user
    max_sequence = db.query(func.max(Sock.user_sequence_id)).filter(
        Sock.owner_id == current_user.id
    ).scalar()
    next_sequence_id = (max_sequence or 0) + 1
    
    # Create sock record (without background-removed image initially)
    new_sock = Sock(
        owner_id=current_user.id,
        user_sequence_id=next_sequence_id,
        image_path=file_path,
        image_no_bg_path=None,  # Will be updated by background task
        embedding=embedding_bytes
    )
    
    db.add(new_sock)
    db.commit()
    db.refresh(new_sock)
    
    # Schedule background removal as a background task
    background_tasks.add_task(
        process_background_removal,
        new_sock.id,
        file_path,
        settings.upload_dir
    )
    
    duration_ms = (time.time() - start_time) * 1000
    log_with_context(logger, "info", "Sock upload successful", 
        user_id=current_user.id, 
        sock_id=new_sock.id,
        user_sequence_id=next_sequence_id,
        duration_ms=round(duration_ms, 2),
        event="upload_success")
    
    # Create response with processing status
    response_dict = {
        "id": new_sock.id,
        "user_sequence_id": new_sock.user_sequence_id,
        "image_path": new_sock.image_path,
        "is_matched": new_sock.is_matched,
        "created_at": new_sock.created_at,
        "color_palette": new_sock.color_palette,
        "is_processing_complete": False  # Processing just started
    }
    return response_dict


@router.get("/list", response_model=List[SockResponse])
def list_unmatched_socks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all unmatched socks for the current user."""
    socks = db.query(Sock).filter(
        Sock.owner_id == current_user.id,
        Sock.is_matched == False
    ).order_by(Sock.created_at.desc()).all()
    
    # Add processing status to each sock
    response_list = []
    for sock in socks:
        response_dict = {
            "id": sock.id,
            "user_sequence_id": sock.user_sequence_id,
            "image_path": sock.image_path,
            "is_matched": sock.is_matched,
            "created_at": sock.created_at,
            "color_palette": sock.color_palette,
            "is_processing_complete": sock.image_no_bg_path is not None and sock.color_palette is not None
        }
        response_list.append(response_dict)
    
    return response_list


@router.get("/{sock_id}", response_model=SockResponse)
def get_sock(
    sock_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific sock."""
    sock = db.query(Sock).filter(Sock.id == sock_id).first()
    
    if not sock:
        log_with_context(logger, "warning", "Sock not found", 
            sock_id=sock_id, 
            user_id=current_user.id,
            event="sock_not_found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sock not found"
        )
    
    # Verify ownership
    if sock.owner_id != current_user.id:
        log_with_context(logger, "warning", "Unauthorized sock access", 
            sock_id=sock_id, 
            user_id=current_user.id,
            owner_id=sock.owner_id,
            event="unauthorized_access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this sock"
        )
    
    # Create response with processing status
    response_dict = {
        "id": sock.id,
        "user_sequence_id": sock.user_sequence_id,
        "image_path": sock.image_path,
        "is_matched": sock.is_matched,
        "created_at": sock.created_at,
        "color_palette": sock.color_palette,
        "is_processing_complete": sock.image_no_bg_path is not None and sock.color_palette is not None
    }
    return response_dict


@router.get("/{sock_id}/image")
def get_sock_image(
    sock_id: int,
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    thumbnail: bool = Query(False, description="Return a thumbnail version (max 600px)"),
    quality: int = Query(85, ge=50, le=100, description="JPEG quality (50-100)"),
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
    
    # Generate ETag based on file modification time and parameters
    file_mtime = os.path.getmtime(sock.image_path)
    etag_base = f"{sock_id}-{file_mtime}-{thumbnail}-{quality}"
    etag = hashlib.md5(etag_base.encode()).hexdigest()
    
    # If thumbnail or quality adjustment requested, process image
    if thumbnail or quality < 100:
        try:
            with Image.open(sock.image_path) as img:
                # Convert to RGB if needed (for JPEG compatibility)
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                
                # Resize for thumbnail
                if thumbnail:
                    img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                
                # Save to bytes with quality setting
                output = BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                output.seek(0)
                
                return Response(
                    content=output.read(),
                    media_type="image/jpeg",
                    headers={
                        "Cache-Control": "public, max-age=86400, immutable",  # Cache for 1 day
                        "ETag": etag,
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET",
                        "Access-Control-Allow-Headers": "*",
                    }
                )
        except Exception as e:
            print(f"Error processing image: {e}")
            # Fall back to original file
            pass
    
    # Return original file with cache headers
    return FileResponse(
        sock.image_path,
        headers={
            "Cache-Control": "public, max-age=86400, immutable",  # Cache for 1 day
            "ETag": etag,
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.get("/{sock_id}/image-no-bg")
def get_sock_image_no_bg(
    sock_id: int,
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get the background-removed image file for a specific sock. Supports token via query param for web or Authorization header."""
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
    
    # Check if background-removed file exists
    if not sock.image_no_bg_path or not os.path.exists(sock.image_no_bg_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Background-removed image file not found"
        )
    
    # Generate ETag based on file modification time
    file_mtime = os.path.getmtime(sock.image_no_bg_path)
    etag = hashlib.md5(f"{sock_id}-{file_mtime}".encode()).hexdigest()
    
    # Return file with cache headers and CORS headers for web compatibility
    return FileResponse(
        sock.image_no_bg_path,
        headers={
            "Cache-Control": "public, max-age=86400, immutable",  # Cache for 1 day
            "ETag": etag,
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
    start_time = time.time()
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
    
    duration_ms = (time.time() - start_time) * 1000
    log_with_context(logger, "info", "Similarity search completed",
        sock_id=sock_id,
        user_id=current_user.id,
        candidates_checked=len(socks),
        matches_found=len(matches[:limit]),
        duration_ms=round(duration_ms, 2),
        event="similarity_search")
    
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
        log_with_context(logger, "warning", "Unauthorized sock deletion attempt",
            sock_id=sock_id,
            user_id=current_user.id,
            owner_id=sock.owner_id,
            event="unauthorized_delete")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this sock"
        )
    
    # Check if sock is matched
    if sock.is_matched:
        log_with_context(logger, "warning", "Attempt to delete matched sock",
            sock_id=sock_id,
            user_id=current_user.id,
            event="delete_matched_sock")
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
            log_error(logger, "Failed to delete image file", exc=e,
                sock_id=sock_id,
                image_path=sock.image_path,
                event="image_delete_error")
    
    # Delete the background-removed image file if it exists
    if sock.image_no_bg_path and os.path.exists(sock.image_no_bg_path):
        try:
            os.remove(sock.image_no_bg_path)
        except Exception as e:
            # Log error but continue with database deletion
            log_error(logger, "Failed to delete background-removed image", exc=e,
                sock_id=sock_id,
                image_path=sock.image_no_bg_path,
                event="bg_image_delete_error")
    
    # Delete the sock from database
    db.delete(sock)
    db.commit()
    
    log_with_context(logger, "info", "Sock deleted successfully",
        sock_id=sock_id,
        user_id=current_user.id,
        event="sock_deleted")
    
    return None
