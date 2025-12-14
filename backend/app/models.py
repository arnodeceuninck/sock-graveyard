from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    socks = relationship("Sock", back_populates="owner", cascade="all, delete-orphan")


class Sock(Base):
    __tablename__ = "socks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_path = Column(String, nullable=False)
    preprocessed_image_path = Column(String)
    
    # Vector embedding (512 dimensions for CLIP ViT-B-32)
    embedding = Column(Vector(512))
    
    # Extracted features
    dominant_color = Column(String)  # Hex color code
    pattern_type = Column(String)  # e.g., "solid", "striped", "dotted"
    texture_features = Column(Text)  # JSON string of texture features
    
    # Metadata
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_matched = Column(Boolean, default=False)
    matched_with_id = Column(Integer, ForeignKey("socks.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="socks")
    matched_with = relationship("Sock", remote_side=[id], foreign_keys=[matched_with_id])
    
    def __repr__(self):
        return f"<Sock(id={self.id}, user_id={self.user_id}, is_matched={self.is_matched})>"
