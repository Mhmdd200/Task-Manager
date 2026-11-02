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

Endpoints marked **Auth** require a JWT in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Get a token from `POST /auth/login`. In Swagger UI, click **Authorize** and paste the token.

### General

| Method | Path      | Auth | Description  |
|--------|-----------|------|--------------|
| GET    | `/health` | —    | Health check |

### Auth

| Method | Path             | Auth | Description                     |
|--------|------------------|------|---------------------------------|
| POST   | `/auth/register` | —    | Register a new user             |
| POST   | `/auth/login`    | —    | Log in and get a JWT token      |
| GET    | `/auth/me`       | Yes  | Get the currently logged-in user |

### Users

| Method | Path     | Auth | Description    |
|--------|----------|------|----------------|
| GET    | `/users` | Yes  | List all users |
| GET    | `/users/{user_id}` | Yes  | Get a user by ID |

### Projects

| Method | Path                     | Auth | Access | Description                                     |
|--------|--------------------------|------|--------|-------------------------------------------------|
| POST   | `/projects`              | Yes  | Any user | Create a project (you become its owner)       |
| GET    | `/projects`              | Yes  | Any user | List the projects you belong to               |
| GET    | `/projects/{project_id}` | Yes  | Member | Get a project by ID                             |
| PATCH  | `/projects/{project_id}` | Yes  | Owner  | Update a project (only the fields you send)     |
| DELETE | `/projects/{project_id}` | Yes  | Owner  | Delete a project                                |

**Project permissions**

- **Member**: any user who belongs to the project. A user who is not a member gets `404 Project not found`, so outsiders can't tell whether the project exists.
- **Owner**: the user who created the project. A member who is not the owner gets `403 Forbidden`.
- A missing or invalid token returns `401 Unauthorized`.

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
