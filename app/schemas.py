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
        description="Short summary of the ticket.",
        examples=["Cannot access customer portal"],
    )
    description: str = Field(
        min_length=1,
        description="Detailed description of the problem.",
        examples=["The customer portal returns an unexpected error."],
    )


class TicketCreate(TicketBase):
    """Data required to create a ticket."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "title": "Cannot access customer portal",
                    "description": (
                        "The customer portal returns an unexpected error."
                    ),
                    "status": "open",
                }
            ]
        },
    )

    status: TicketStatus = Field(
        default=TicketStatus.OPEN,
        description="Initial ticket status.",
        examples=["open"],
    )


class TicketUpdate(TicketBase):
    """Data required to fully update a ticket."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "title": "Customer portal unavailable",
                    "description": (
                        "Resolution is waiting for the external provider."
                    ),
                    "status": "stalled",
                }
            ]
        },
    )

    status: TicketStatus = Field(
        description="New ticket status.",
        examples=["stalled"],
    )


class TicketRead(TicketBase):
    """Ticket data returned by the API."""

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "title": "Cannot access customer portal",
                    "description": (
                        "The customer portal returns an unexpected error."
                    ),
                    "status": "open",
                    "created_at": "2026-07-14T12:00:00Z",
                }
            ]
        },
    )

    id: int = Field(
        description="Auto-generated ticket identifier.",
        examples=[1],
    )
    status: TicketStatus = Field(
        description="Current ticket status.",
        examples=["open"],
    )
    created_at: datetime = Field(
        description="Ticket creation timestamp.",
        examples=["2026-07-14T12:00:00Z"],
    )


class ErrorResponse(BaseModel):
    """Error response returned by the API."""

    model_config = ConfigDict(extra="forbid")

    detail: str = Field(
        description="Human-readable error message.",
        examples=["Ticket not found"],
    )
