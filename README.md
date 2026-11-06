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

   If you use [uv](https://docs.astral.sh/uv/) instead of pip, create the environment with `uv venv` and install with `uv pip install -r requirements.txt`.

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

### Project members

| Method | Path                                       | Auth | Access                  | Description                                  |
|--------|--------------------------------------------|------|-------------------------|----------------------------------------------|
| POST   | `/projects/{project_id}/members`           | Yes  | Owner                   | Add a user to the project as a `member`      |
| GET    | `/projects/{project_id}/members`           | Yes  | Member                  | List the project's members, with user details |
| DELETE | `/projects/{project_id}/members/{user_id}` | Yes  | Owner, or the member themselves | Remove a member, or leave the project |

**Add a member**

Request body:

```json
{ "user_id": 5 }
```

- The new member always gets the role `member`. Any `role` or `project_id` sent in the body is ignored; the project comes from the URL.
- `404 User not found`: the user doesn't exist.
- `409 Conflict`: the user is already a member of the project.

**Member response** (returned by `POST` and, as a list, by `GET`):

```json
{
  "id": 2,
  "project_id": 1,
  "role": "member",
  "user": { "id": 5, "name": "Sara", "email": "sara@example.com", "created_at": "2026-11-02T14:20:12" }
}
```

**Remove a member**

`{user_id}` is the ID of the user to remove, not the membership `id`.

- The owner can remove any member.
- A member can remove only themselves, which means leaving the project. Removing someone else returns `403 Forbidden`.
- The owner can't be removed, not even by themselves: `400 Bad Request`.
- `404 Member not found`: the user is not a member of the project.
- Their tasks in this project become unassigned. Tasks in other projects don't change.
- Returns `204 No Content` on success.

### Tasks

Tasks belong to a project. Deleting a project deletes its tasks.

| Method | Path                           | Auth | Access | Description                                   |
|--------|--------------------------------|------|--------|-----------------------------------------------|
| POST   | `/projects/{project_id}/tasks` | Yes  | Member | Create a task in the project                  |
| GET    | `/projects/{project_id}/tasks` | Yes  | Member | List the project's tasks, one page at a time, optionally filtered by status |
| GET    | `/projects/{project_id}/tasks/{task_id}` | Yes | Member | Get a task by ID |
| PATCH  | `/projects/{project_id}/tasks/{task_id}` | Yes | Owner, task creator or assignee | Update a task (only the fields you send) |
| DELETE | `/projects/{project_id}/tasks/{task_id}` | Yes | Owner or task creator | Delete a task |

**Create a task**

Request body (only `title` is required):

```json
{ "title": "Design login page", "description": "Optional details", "assignee_id": 5 }
```

- `title`: 1 to 200 characters.
- New tasks always start with the status `todo`. Any `status` sent in the body is ignored.
- The task's creator (`created_by_id`) is the logged-in user.
- `assignee_id` is optional. If sent, that user must be a member of the project, otherwise `400 Assignee must be a member of the project`.

**List tasks**

Tasks are returned one page at a time, oldest first.

| Query parameter | Default | Allowed values | Description |
|-----------------|---------|----------------|-------------|
| `page`          | `1`     | `1` or higher  | The page to return |
| `page_size`     | `20`    | `1` to `100`   | Tasks per page |
| `status`        | none    | `todo`, `in_progress`, `done` | Return only tasks with this status |

A value outside these ranges returns `422`. For example, `GET /projects/1/tasks?status=done&page=2&page_size=10` returns the second page of 10 done tasks.

```json
{ "items": [ ... ], "total": 25, "page": 1, "page_size": 20 }
```

- `items`: the tasks on this page. Each one is a task response, shown below.
- `total`: the number of tasks that match across all pages. With `status`, only tasks with that status are counted.
- A page past the end returns `200` with an empty `items` list.

**Update a task**

All fields are optional. Only the fields you send are changed, and an empty body `{}` changes nothing.

```json
{ "title": "New title", "description": "...", "status": "in_progress", "assignee_id": 5 }
```

- Who can update: the project owner, the task's creator, or its current assignee. Any other member gets `403 Forbidden`.
- `title`: if sent, 1 to 200 characters. It can't be `null` (`422`).
- `status`: `todo`, `in_progress` or `done`.
- `assignee_id`: leave it out to keep the current assignee, send `null` to unassign the task, or send a user ID to reassign it. That user must be a member of the project, otherwise `400`.

**Delete a task**

- Only the project owner or the task's creator can delete a task. Any other member gets `403 Forbidden`, including the assignee.
- Returns `204 No Content` on success.

For `GET`, `PATCH` and `DELETE` on a single task, `404 Task not found` means the task doesn't exist or belongs to a different project than the one in the URL.

**Task response** (returned by `POST`, `PATCH` and `GET` on a single task, and inside `items` when listing tasks):

```json
{
  "id": 1,
  "project_id": 1,
  "title": "Design login page",
  "description": null,
  "status": "todo",
  "created_by_id": 2,
  "created_at": "2026-11-03T13:20:00",
  "assignee": { "id": 5, "name": "Sara", "email": "sara@example.com", "created_at": "2026-11-02T14:20:12" }
}
```

`assignee` is `null` when the task is unassigned.

## Request logging

`app/middleware.py` wraps every request. It adds two response headers and logs one line per request.

| Header | Value |
|--------|-------|
| `X-Request-ID` | A new unique ID for this request |
| `X-Process-Time` | How long the request took, in milliseconds |

```
INFO:app.middleware:GET /health status=200 duration=0.32ms request_id=fcc66c7120a841a49d04106370f24fbc
```

- All normal responses get both headers, including `401`, `403`, `404` and `422`.
- If an endpoint crashes, the log line shows `status=500` and the traceback is printed. See [Crash responses](#crash-responses) for what the client receives.
- Only the method and path are logged. Headers, request bodies and query strings are never logged, because they can contain tokens or passwords.
- When you run `uvicorn`, you also see its own access line for each request, such as `"GET /health HTTP/1.1" 200 OK`.

## Crash responses

If the server crashes on an unexpected error, `handle_crash` in `app/exception_handlers.py` returns `500` with this body:

```json
{ "detail": "Internal server error", "request_id": "8f7799e3826d483caa15a2ac4e350982" }
```

- The same ID is in the `X-Request-ID` header and in the server log, so a user can send you the ID and you can search the log for their exact crash.
- This response doesn't have `X-Process-Time`, because it is built outside the middleware.
- The error message is never sent to the client. It only appears in the server log.
- Normal errors such as `401`, `403`, `404` and `422` don't go through this handler.

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

## Running tests

> **Note:** The test setup (`pytest.ini`, `tests/conftest.py`, `tests/test_health.py` and `tests/test_db_setup.py`) was written with AI assistance and has not been reviewed by me yet. Tests for the project and member endpoints are still to do.

With the virtual environment active, run from the project root:

```bash
pytest -v
```

Tests run against a fresh in-memory SQLite database for each test, so `task_manager.db` is never touched. `tests/conftest.py` provides these fixtures:

| Fixture | Gives a test |
|---------|--------------|
| `db` | A database session on the empty test database |
| `client` | A `TestClient` whose endpoints use the test database |
| `make_user(name)` | A new user with the email `{name}@test.com` |
| `make_project(owner)` | A new project, including the owner's membership |
| `auth_headers(user)` | An `Authorization` header with a valid token for that user |

Useful options:

| Command | What it does |
|---------|--------------|
| `pytest -x` | Stop at the first failure |
| `pytest -k remove` | Run only tests whose name contains "remove" |
| `pytest --lf` | Rerun only the tests that failed last time |
| `pytest -s` | Show `print()` output |

## Project structure

```
app/
├── main.py            # FastAPI app, logging setup, middleware, crash handler and router registration
├── middleware.py      # Request logging and timing
├── exception_handlers.py  # JSON response for server crashes
├── config.py          # Settings loaded from .env
├── database.py        # Engine, SessionLocal, Base
├── dependencies/      # FastAPI dependencies (e.g. get_db)
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic request/response schemas
├── repositories/      # Database queries
├── services/          # Business logic
└── routers/           # API endpoints
alembic/               # Migration scripts
tests/                 # pytest tests; shared fixtures in conftest.py
```
