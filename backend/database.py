"""
================================================================================
File: database.py
Description:
    This module handles the database configuration and connection setup for
    the Kiosk Backend API using SQLAlchemy ORM.

    It:
      • Loads environment variables from a `.env` file for secure configuration
      • Establishes a PostgreSQL connection through SQLAlchemy
      • Provides a session factory (`SessionLocal`) used by all database routes
      • Defines a shared base class (`Base`) for all ORM models
      • Includes the `get_db()` dependency, which supplies and cleans up 
        database sessions in FastAPI routes
================================================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get DATABASE_URL from environment, fallback to localhost (safe default)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin7890@localhost:5432/kioskdb")

# Debug print to verify connection string
print("🧠 DATABASE_URL =", DATABASE_URL)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    """
    Provides a SQLAlchemy session to routes.
    Automatically closes it when the request ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()