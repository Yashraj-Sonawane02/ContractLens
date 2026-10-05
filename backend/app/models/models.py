from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    history = relationship("AnalysisHistory", back_populates="owner", cascade="all, delete-orphan")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(100), default="Legal Contract")
    selected_domains = Column(Text, default="[]") # JSON list of domains
    health_score = Column(Integer, default=100)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    total_clauses = Column(Integer, default=0)
    processing_time_seconds = Column(Float, default=0.0)
    
    # Encrypted Object Storage References
    file_key = Column(String(500), nullable=True)
    storage_type = Column(String(50), default="LOCAL_ENCRYPTED_AES256")
    
    # Store full analysis payload as JSON for retrieval
    analysis_result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="history")
