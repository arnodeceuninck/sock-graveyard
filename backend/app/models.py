from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Terms acceptance tracking
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime, nullable=True)
    terms_version = Column(String, nullable=True)  # e.g., "1.0"
    privacy_accepted = Column(Boolean, default=False)
    privacy_accepted_at = Column(DateTime, nullable=True)
    privacy_version = Column(String, nullable=True)  # e.g., "1.0"
    
    socks = relationship("Sock", back_populates="owner")


class Sock(Base):
    __tablename__ = "socks"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_sequence_id = Column(Integer, nullable=False)  # Sequential ID per user (1, 2, 3...)
    image_path = Column(String, nullable=False)
    image_no_bg_path = Column(String, nullable=True)  # Path to image with background removed
    color_palette = Column(String, nullable=True)  # JSON array of hex color codes
    embedding = Column(LargeBinary, nullable=False)  # Stored as bytes
    is_matched = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="socks")
    # Relationships for matches
    matches_as_sock1 = relationship("Match", foreign_keys="Match.sock1_id", back_populates="sock1")
    matches_as_sock2 = relationship("Match", foreign_keys="Match.sock2_id", back_populates="sock2")


class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # To track which user owns this match
    user_sequence_id = Column(Integer, nullable=False)  # Sequential ID per user (1, 2, 3...)
    sock1_id = Column(Integer, ForeignKey("socks.id"), nullable=False)
    sock2_id = Column(Integer, ForeignKey("socks.id"), nullable=False)
    matched_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="matches")
    sock1 = relationship("Sock", foreign_keys=[sock1_id], back_populates="matches_as_sock1")
    sock2 = relationship("Sock", foreign_keys=[sock2_id], back_populates="matches_as_sock2")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="refresh_tokens")
