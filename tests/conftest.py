import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (imported so Base.metadata knows all the tables)
from app.database import Base, enable_sqlite_foreign_keys
from app.dependencies.database import get_db
from app.main import app
from app.repositories import project_repository, user_repository
from app.services import auth_service

engine = create_engine(
    "sqlite://",                                  # in-memory: nothing written to disk, very fast
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,                         # one shared connection, so every session sees the same in-memory DB
)
# reuse the app's listener so ondelete="CASCADE" works in tests too
event.listen(engine, "connect", enable_sqlite_foreign_keys)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

TEST_PASSWORD = "password123"
# hashing is slow on purpose, so hash once and reuse it for every test user
TEST_PASSWORD_HASH = auth_service.hash_password(TEST_PASSWORD)


# ---------- database + client ----------

@pytest.fixture
def db():
    Base.metadata.create_all(engine)    # setup: empty tables
    session = TestingSessionLocal()
    yield session                       # the test runs here
    session.close()                     # cleanup: runs even if the test fails
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    # every endpoint that uses DbSession gets the test session instead of the real DB
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------- factories ----------

@pytest.fixture
def make_user(db):
    def _make_user(name="user"):
        # the email is built from the name, so use a different name for each user in a test
        return user_repository.create(
            db,
            name=name,
            email=f"{name}@test.com",
            hashed_password=TEST_PASSWORD_HASH,
        )
    return _make_user


@pytest.fixture
def make_project(db):
    def _make_project(owner, name="project"):
        # use the repository (not Project(...)) so the owner's membership row is created too
        return project_repository.create(db, name=name, description=None, user_id=owner.id)
    return _make_project


@pytest.fixture
def auth_headers():
    # like DRF's force_authenticate: a valid token without calling /auth/login
    def _auth_headers(user):
        return {"Authorization": f"Bearer {auth_service.create_access_token(user.id)}"}
    return _auth_headers
