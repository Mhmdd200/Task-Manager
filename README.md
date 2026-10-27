# Task Manager API

A FastAPI backend for managing tasks. It uses SQLAlchemy for the ORM, Alembic for migrations, and a local SQLite database. Authentication uses JWT.

## Requirements

- Python 3.12+
- git

## Setup

All commands must be run from the project root.

1. **Clone the repository**

   ```bash
   git clone git@github.com:Mhmdd200/Task-Manager.git
   cd Task-Manager
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # macOS / Linux
   # .venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the project root

   ```env
   DATABASE_URL=sqlite:///./task_manager.db
   SECRET_KEY=replace-with-a-long-random-string
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

   Generate a secure secret key with:

   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

   `.env` is git-ignored, so your secrets are never committed. If a variable is missing, the defaults in `app/config.py` are used.

5. **Run the database migrations**

   ```bash
   alembic upgrade head
   ```

   This creates the SQLite file `task_manager.db` and all tables.

## Run the server

```bash
uvicorn app.main:app --reload
```

The API is now available at <http://127.0.0.1:8000>.

- Interactive docs (Swagger UI): <http://127.0.0.1:8000/docs>
- Alternative docs (ReDoc): <http://127.0.0.1:8000/redoc>
- Health check: <http://127.0.0.1:8000/health>

## Endpoints

| Method | Path             | Description                |
|--------|------------------|----------------------------|
| GET    | `/health`        | Health check               |
| POST   | `/auth/register` | Register a new user        |
| POST   | `/auth/login`    | Log in and get a JWT token |

## Database migrations

After changing a model in `app/models/`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

To undo the last migration:

```bash
alembic downgrade -1
```

## Project structure

```
app/
├── main.py            # FastAPI app and router registration
├── config.py          # Settings loaded from .env
├── database.py        # Engine, SessionLocal, Base
├── dependencies/      # FastAPI dependencies (e.g. get_db)
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic request/response schemas
├── repositories/      # Database queries
├── services/          # Business logic
└── routers/           # API endpoints
alembic/               # Migration scripts
```
