from datetime import datetime

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models import Ticket, TicketStatus


def test_ticket_model_has_expected_columns() -> None:
    expected_columns = {
        "id",
        "title",
        "description",
        "status",
        "created_at",
    }

    assert set(Ticket.__table__.columns.keys()) == expected_columns


def test_ticket_is_persisted_with_default_values(
    db_session: Session,
) -> None:
    ticket = Ticket(
        title="Cannot access customer portal",
        description="The portal returns an unexpected error.",
    )

    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    stored_status = db_session.scalar(
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
    db_session: Session,
) -> None:
    ticket = Ticket(
        title="Example ticket",
        description="Example ticket description.",
        status=status,
    )

    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    assert ticket.status is status


def test_database_starts_empty(
    db_session: Session,
) -> None:
    statement = select(func.count()).select_from(Ticket)

    assert db_session.scalar(statement) == 0
