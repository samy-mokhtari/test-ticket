from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TicketStatus(str, Enum):
    """Possible lifecycle statuses for a ticket."""

    OPEN = "open"
    STALLED = "stalled"
    CLOSED = "closed"


def _ticket_status_values(
    _: type[Enum],
) -> list[str]:
    """Return the ticket status values stored in the database."""
    return [status.value for status in TicketStatus]


def _utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class Ticket(Base):
    """Database representation of a support ticket."""

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[TicketStatus] = mapped_column(
        SqlEnum(
            TicketStatus,
            name="ticket_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=_ticket_status_values,
        ),
        nullable=False,
        default=TicketStatus.OPEN,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
    )
