from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        # this hands the session to the endpoint and pauses till the endpoint finishes
        yield db
    finally:
        db.close()

# this is just an alias (shortcut) so that we dont call it in every api as depends(get_db)
DbSession = Annotated[Session, Depends(get_db)]
