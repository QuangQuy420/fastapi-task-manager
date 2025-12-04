import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_DB = os.getenv("POSTGRES_DB", "task_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "task_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "task_password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,  # Turn off SQL logs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
