from collections.abc import Generator
from datetime import datetime

import pytest
from sqlalchemy import text

from app.database import Base, engine, session_factory
from app.models import Ticket, TicketStatus


@pytest.fixture(autouse=True)
def recreate_database_tables() -> Generator[None, None, None]:
    """Create an isolated database schema for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


def test_ticket_model_has_expected_columns() -> None:
    expected_columns = {
        "id",
        "title",
        "description",
        "status",
        "created_at",
    }

    assert set(Ticket.__table__.columns.keys()) == expected_columns


def test_ticket_is_persisted_with_default_values() -> None:
    ticket = Ticket(
        title="Cannot access customer portal",
        description="The portal returns an unexpected error.",
    )

    with session_factory() as session:
        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        stored_status = session.scalar(
            text("SELECT status FROM tickets WHERE id = :ticket_id"),
            params={"ticket_id": ticket.id},
        )

    assert isinstance(ticket.id, int)
    assert ticket.id > 0
    assert ticket.status is TicketStatus.OPEN
    assert stored_status == "open"
    assert isinstance(ticket.created_at, datetime)


@pytest.mark.parametrize(
    "status",
    list(TicketStatus),
)
def test_ticket_accepts_each_valid_status(
    status: TicketStatus,
) -> None:
    ticket = Ticket(
        title="Example ticket",
        description="Example ticket description.",
        status=status,
    )

    with session_factory() as session:
        session.add(ticket)
        session.commit()
        session.refresh(ticket)

    assert ticket.status is status
