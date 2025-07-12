"""
Database configuration and session management for PostgreSQL.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Load environment variables from .env file
load_dotenv()

# Database URL - you can set this as an environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123@localhost:5432/agentbay_db"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db() -> Generator:
    """
    Dependency to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables.
    """
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """
    Get a database session context manager.
    Use this for manual session management.
    """
    return SessionLocal()

class DatabaseManager:
    """
    Database manager for handling transactions and sessions.
    """
    
    @staticmethod
    def create_session():
        """Create a new database session."""
        return SessionLocal()
    
    @staticmethod
    def close_session(session):
        """Close a database session."""
        session.close()
    
    @staticmethod
    def commit_session(session):
        """Commit a database session."""
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
    
    @staticmethod
    def rollback_session(session):
        """Rollback a database session."""
        session.rollback()