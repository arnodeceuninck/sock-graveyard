"""
Helper functions for storing and querying embeddings across different database backends

Supports both PostgreSQL (with pgvector) and SQLite (with JSON storage and numpy similarity)
"""

import json
import numpy as np
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Sock


def embedding_to_db(embedding: np.ndarray) -> any:
    """
    Convert numpy embedding to database-compatible format
    
    Args:
        embedding: Numpy array embedding
        
    Returns:
        Database-compatible embedding (pgvector Vector or JSON string)
    """
    if settings.DATABASE_URL.startswith("postgresql"):
        # PostgreSQL with pgvector - return as list
        return embedding.tolist()
    else:
        # SQLite - store as JSON string
        return json.dumps(embedding.tolist())


def embedding_from_db(db_embedding: any) -> np.ndarray:
    """
    Convert database embedding to numpy array
    
    Args:
        db_embedding: Embedding from database (Vector or JSON string)
        
    Returns:
        Numpy array
    """
    if db_embedding is None:
        return None
    
    if isinstance(db_embedding, str):
        # SQLite JSON string
        return np.array(json.loads(db_embedding))
    elif isinstance(db_embedding, list):
        # Already a list
        return np.array(db_embedding)
    else:
        # pgvector Vector type
        return np.array(db_embedding)


def find_similar_socks(
    db: Session,
    embedding: np.ndarray,
    user_id: int,
    limit: int = 10,
    threshold: float = 0.75
) -> List[Tuple[Sock, float]]:
    """
    Find similar socks using cosine similarity
    
    Works with both PostgreSQL (pgvector) and SQLite (numpy)
    
    Args:
        db: Database session
        embedding: Query embedding
        user_id: User ID to search within
        limit: Maximum number of results
        threshold: Minimum similarity threshold
        
    Returns:
        List of (Sock, similarity_score) tuples, sorted by similarity
    """
    if settings.DATABASE_URL.startswith("postgresql"):
        # Use pgvector's cosine distance operator
        from sqlalchemy import text
        
        # Convert embedding to pgvector format
        embedding_str = "[" + ",".join(map(str, embedding.tolist())) + "]"
        
        # Query using pgvector's <=> operator (cosine distance)
        query = text("""
            SELECT *, (1 - (embedding <=> :embedding::vector)) as similarity
            FROM socks
            WHERE user_id = :user_id
            AND embedding IS NOT NULL
            AND is_matched = false
            AND (1 - (embedding <=> :embedding::vector)) >= :threshold
            ORDER BY similarity DESC
            LIMIT :limit
        """)
        
        results = db.execute(
            query,
            {
                "embedding": embedding_str,
                "user_id": user_id,
                "threshold": threshold,
                "limit": limit
            }
        ).fetchall()
        
        # Convert results to (Sock, similarity) tuples
        socks_with_similarity = []
        for row in results:
            sock = db.query(Sock).filter(Sock.id == row.id).first()
            if sock:
                socks_with_similarity.append((sock, float(row.similarity)))
        
        return socks_with_similarity
    
    else:
        # SQLite: Load all socks and calculate similarity with numpy
        socks = db.query(Sock).filter(
            Sock.user_id == user_id,
            Sock.embedding.isnot(None),
            Sock.is_matched == False
        ).all()
        
        # Calculate similarities
        socks_with_similarity = []
        for sock in socks:
            sock_embedding = embedding_from_db(sock.embedding)
            if sock_embedding is not None:
                # Cosine similarity
                similarity = np.dot(embedding, sock_embedding) / (
                    np.linalg.norm(embedding) * np.linalg.norm(sock_embedding)
                )
                
                # Convert from [-1, 1] to [0, 1]
                similarity = (similarity + 1) / 2
                
                if similarity >= threshold:
                    socks_with_similarity.append((sock, float(similarity)))
        
        # Sort by similarity and limit
        socks_with_similarity.sort(key=lambda x: x[1], reverse=True)
        return socks_with_similarity[:limit]


def create_vector_index(db: Session):
    """
    Create vector similarity index for faster queries
    
    Only works with PostgreSQL + pgvector
    """
    if settings.DATABASE_URL.startswith("postgresql"):
        from sqlalchemy import text
        
        try:
            # Create IVFFlat index for faster similarity search
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS socks_embedding_idx 
                ON socks 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False
    
    return False  # SQLite doesn't support vector indexes
