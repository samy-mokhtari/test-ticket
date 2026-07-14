from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI
from sqlalchemy import Table

from app.database import Base, engine
from app.models import Ticket
from app.routers.tickets import router as tickets_router


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
    description="REST API for managing support tickets.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(tickets_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return the current health status of the API."""
    return {"status": "ok"}
