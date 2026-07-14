from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from sqlalchemy import Table

from app.database import Base, engine
from app.models import Ticket
from app.routers.tickets import router as tickets_router

API_DESCRIPTION = (
    "A REST API for creating, retrieving, updating, "
    "and closing support tickets. Data is stored in "
    "an in-memory SQLite database and is lost when "
    "the application stops."
)

OPENAPI_TAGS: list[dict[str, Any]] = [
    {
        "name": "Tickets",
        "description": (
            "Create, list, retrieve, update, and close support tickets."
        ),
    },
    {
        "name": "Health",
        "description": ("Check whether the API process is running."),
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create database tables when the application starts."""
    Base.metadata.create_all(
        bind=engine,
        tables=[cast(Table, Ticket.__table__)],
    )
    yield


app = FastAPI(
    title="Ticket API",
    summary="Manage support tickets.",
    description=API_DESCRIPTION,
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
)

app.include_router(tickets_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return the current health status of the API."""
    return {"status": "ok"}
