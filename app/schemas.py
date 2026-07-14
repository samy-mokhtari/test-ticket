from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import TicketStatus


class TicketBase(BaseModel):
    """Shared validated fields for ticket input models."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )
    description: str = Field(
        min_length=1,
    )


class TicketCreate(TicketBase):
    """Data required to create a ticket."""

    status: TicketStatus = TicketStatus.OPEN


class TicketUpdate(TicketBase):
    """Data required to fully update a ticket."""

    status: TicketStatus


class TicketRead(TicketBase):
    """Ticket data returned by the API."""

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        str_strip_whitespace=True,
    )

    id: int
    status: TicketStatus
    created_at: datetime
