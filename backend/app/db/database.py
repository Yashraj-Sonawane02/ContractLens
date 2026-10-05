import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL

# PostgreSQL / SQLite Engine Configuration
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args)
else:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db_schema():
    """
    Initializes database tables and runs schema migration checks.
    Ensures missing columns like file_key and storage_type are added automatically.
    """
    Base.metadata.create_all(bind=engine)
    
    try:
        inspector = inspect(engine)
        if "analysis_history" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("analysis_history")]
            with engine.connect() as conn:
                if "file_key" not in columns:
                    conn.execute(text("ALTER TABLE analysis_history ADD COLUMN file_key VARCHAR(500)"))
                    conn.commit()
                if "storage_type" not in columns:
                    conn.execute(text("ALTER TABLE analysis_history ADD COLUMN storage_type VARCHAR(50)"))
                    conn.commit()
    except Exception as e:
        print(f"Database schema auto-migration warning: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
