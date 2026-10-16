from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

# We are creating the session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# this is used in order to make our models classes sqlalchemy orm models
class Base(DeclarativeBase):
    pass
