from sqlalchemy import create_engine, event
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

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
