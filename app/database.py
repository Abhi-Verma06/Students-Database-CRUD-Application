import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import get_settings

settings = get_settings()

# Ensure SQLite storage directory exists
if settings.DATABASE_URL.startswith("sqlite"):
    # Strip sqlite:/// to get file path if relative or absolute
    db_path_str = settings.DATABASE_URL.replace("sqlite:///", "")
    db_file = Path(db_path_str)
    if db_file.parent and not db_file.parent.exists():
        db_file.parent.mkdir(parents=True, exist_ok=True)

# Create engine with thread-check disabled for SQLite concurrency
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request
    and guarantees proper closure upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
