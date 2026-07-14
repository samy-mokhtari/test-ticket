# Ticket API

A small REST API for managing support tickets, built with FastAPI,
SQLAlchemy, Pydantic, and SQLite.

The application supports ticket creation, listing, retrieval, full updates,
and closure. Data is stored in an in-memory SQLite database and is therefore
reset whenever the application process stops.

## Features

- FastAPI REST API
- Pydantic request and response validation
- SQLAlchemy 2.x persistence layer
- In-memory SQLite database
- Automatic Swagger UI and ReDoc documentation
- Pytest test suite with a minimum coverage threshold of 80%
- Ruff linting, formatting, and PEP 8 checks
- Pre-commit hooks
- Docker and Docker Compose development environment

## Requirements

### Recommended

- Docker
- Docker Compose

### Local installation

- Python 3.10 or newer
- Git

## Quick start with Docker

Clone the repository:

```bash
git clone https://github.com/samy-mokhtari/test-ticket
cd test-ticket
```

Build and start the API:

```bash
docker compose up --build
```

The API is then available at:

- API base URL: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI schema: `http://localhost:8000/openapi.json`
- Health check: `http://localhost:8000/health`

Stop the application:

```bash
docker compose down
```

> The database is stored in memory. All tickets are deleted when the
> application container or process stops.

## Local installation

Create a virtual environment.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents script execution for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Start the API:

```bash
python -m uvicorn app.main:app --reload
```

## API endpoints

| Method | Endpoint | Description | Success |
|---|---|---|---:|
| `POST` | `/tickets/` | Create a ticket | `201` |
| `GET` | `/tickets/` | List all tickets | `200` |
| `GET` | `/tickets/{ticket_id}` | Retrieve a ticket | `200` |
| `PUT` | `/tickets/{ticket_id}` | Fully update a ticket | `200` |
| `PATCH` | `/tickets/{ticket_id}/close` | Close a ticket | `200` |
| `GET` | `/health` | Check API health | `200` |

Ticket statuses are:

- `open`
- `stalled`
- `closed`

## Usage examples

### Create a ticket

```bash
curl -X POST "http://localhost:8000/tickets/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cannot access customer portal",
    "description": "The customer portal returns an unexpected error."
  }'
```

Example response:

```json
{
  "id": 1,
  "title": "Cannot access customer portal",
  "description": "The customer portal returns an unexpected error.",
  "status": "open",
  "created_at": "2026-07-14T12:00:00"
}
```

The `status` field is optional during creation and defaults to `open`.

### List tickets

```bash
curl "http://localhost:8000/tickets/"
```

An empty database returns:

```json
[]
```

### Retrieve a ticket

```bash
curl "http://localhost:8000/tickets/1"
```

A missing ticket returns:

```json
{
  "detail": "Ticket not found"
}
```

with HTTP status `404`.

### Update a ticket

```bash
curl -X PUT "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customer portal unavailable",
    "description": "Resolution is waiting for the external provider.",
    "status": "stalled"
  }'
```

`PUT` performs a full update. The request must contain `title`,
`description`, and `status`. The `id` and `created_at` fields cannot be
modified.

### Close a ticket

```bash
curl -X PATCH "http://localhost:8000/tickets/1/close"
```

Closing an already closed ticket is idempotent and still returns a successful
response with the `closed` status.

## Validation and errors

The API returns:

- `404 Not Found` when a requested ticket does not exist
- `422 Unprocessable Entity` when request data is invalid

Examples of invalid data include:

- a missing required field
- an empty title or description
- a title longer than 255 characters
- an unsupported status
- an unexpected field
- a non-integer ticket identifier

## Running the tests

The Pytest configuration is stored in `pyproject.toml`. The test command
includes a coverage report and fails when total coverage is below 80%.

### Locally

```bash
pytest
```

Run a specific test module:

```bash
pytest tests/test_ticket_creation.py -v
```

Generate an HTML coverage report:

```bash
pytest --cov-report=html
```

The report is generated in `htmlcov/index.html`.

### With Docker

```bash
docker compose run --rm api pytest
```

## Code quality

Run Ruff linting:

```bash
ruff check .
```

Verify formatting:

```bash
ruff format --check .
```

Apply safe automatic fixes:

```bash
ruff check . --fix
```

Format the code:

```bash
ruff format .
```

The project configures Ruff with:

- pycodestyle errors and warnings
- a 79-character code line limit
- a 72-character documentation line limit
- PEP 8 naming checks
- import sorting
- Pyflakes checks
- common bug-pattern checks
- Python syntax modernization checks

Run all pre-commit hooks manually:

```bash
pre-commit run --all-files
```

Install the hooks after a local clone:

```bash
pre-commit install
```

### Code quality with Docker

```bash
docker compose run --rm api ruff check .
docker compose run --rm api ruff format --check .
```

## Project structure

```text
.
├── app/
│   ├── __init__.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── routers/
│       ├── __init__.py
│       └── tickets.py
├── tests/
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_models.py
│   ├── test_openapi.py
│   ├── test_schemas.py
│   ├── test_smoke.py
│   ├── test_ticket_closure.py
│   ├── test_ticket_creation.py
│   ├── test_ticket_retrieval.py
│   └── test_ticket_updates.py
├── .dockerignore
├── .gitignore
├── .pre-commit-config.yaml
├── compose.yaml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Architecture

The code is separated by responsibility:

- `main.py` creates and configures the FastAPI application.
- `database.py` configures the SQLAlchemy engine and session dependency.
- `models.py` defines the SQLAlchemy ticket model and status enum.
- `schemas.py` defines Pydantic input, output, and error models.
- `crud.py` contains database operations without HTTP-specific logic.
- `routers/tickets.py` defines the HTTP endpoints and error handling.
- `tests/` contains unit and API integration tests.

## Technical decisions

### In-memory SQLite and `StaticPool`

An in-memory SQLite database normally exists for the lifetime of a single
connection. `StaticPool` ensures that application sessions reuse the same
connection and therefore share the same temporary database.

`check_same_thread=False` allows the SQLite connection to be used across the
threads involved in FastAPI request handling.

This setup is appropriate for the scope of this technical exercise. It is not
intended as a production database configuration.

### Synchronous SQLAlchemy

The application uses synchronous SQLAlchemy because the scope is small and
SQLite is used locally in memory. An asynchronous persistence layer would add
complexity without providing a meaningful benefit for this use case.

### Separate Pydantic schemas

The API uses distinct schemas for:

- ticket creation
- full ticket updates
- ticket responses
- documented error responses

This prevents clients from setting generated fields such as `id` and
`created_at`.

### Full `PUT` update

`PUT /tickets/{ticket_id}` requires all modifiable fields. This reflects a
complete replacement of the editable ticket data.

The dedicated closure endpoint provides the required partial status
transition:

```text
PATCH /tickets/{ticket_id}/close
```

### Idempotent closure

Closing a ticket that is already closed succeeds and leaves it closed. This
makes the operation safe to repeat after a client timeout or retry.

### No migration tool

The database is recreated in memory at every application start, so schema
migrations would not provide value for this project.

## Resetting the data

Because the database is in memory, restart the application to clear all
tickets.

With Docker:

```bash
docker compose restart api
```

Locally, stop Uvicorn and start it again.

## Final verification

Run the complete local quality check:

```bash
pytest
ruff check .
ruff format --check .
pre-commit run --all-files
```

Run the equivalent checks in Docker:

```bash
docker compose build
docker compose run --rm api pytest
docker compose run --rm api ruff check .
docker compose run --rm api ruff format --check .
```
