from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    socks = relationship("Sock", back_populates="owner")


class Sock(Base):
    __tablename__ = "socks"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_path = Column(String, nullable=False)
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
    sock1_id = Column(Integer, ForeignKey("socks.id"), nullable=False)
    sock2_id = Column(Integer, ForeignKey("socks.id"), nullable=False)
    matched_at = Column(DateTime, default=datetime.utcnow)
    
    sock1 = relationship("Sock", foreign_keys=[sock1_id], back_populates="matches_as_sock1")
    sock2 = relationship("Sock", foreign_keys=[sock2_id], back_populates="matches_as_sock2")
