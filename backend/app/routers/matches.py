from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Sock, Match
from app.schemas import MatchCreate, MatchResponse
from app.auth import get_current_user

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("")
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


@router.get("/{match_id}", response_model=MatchResponse)
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


@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
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


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: int,
    decouple: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a match.
    - If decouple=True: Break the match and mark both socks as unmatched (socks remain)
    - If decouple=False: Delete both socks and the match (default)
    """
    import os
    from app.config import get_settings
    
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
            detail="Not authorized to delete this match"
        )
    
    if decouple:
        # Decouple: just break the match and mark socks as unmatched
        match.sock1.is_matched = False
        match.sock2.is_matched = False
        db.delete(match)
        db.commit()
    else:
        # Delete both socks and the match
        sock1 = match.sock1
        sock2 = match.sock2
        
        # Delete image files
        for sock in [sock1, sock2]:
            if os.path.exists(sock.image_path):
                try:
                    os.remove(sock.image_path)
                except Exception as e:
                    print(f"Failed to delete image file {sock.image_path}: {str(e)}")
        
        # Delete the match first (due to foreign key constraints)
        db.delete(match)
        # Then delete the socks
        db.delete(sock1)
        db.delete(sock2)
        db.commit()
    
    return None
