import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Ticket, TicketStatus


def _persist_ticket(
    session: Session,
    status: TicketStatus,
) -> Ticket:
    """Create a ticket directly in the test database."""
    ticket = Ticket(
        title="Customer portal issue",
        description="The customer cannot access the portal.",
        status=status,
    )

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return ticket


@pytest.mark.parametrize(
    "initial_status",
    [
        TicketStatus.OPEN,
        TicketStatus.STALLED,
        TicketStatus.CLOSED,
    ],
)
def test_close_ticket_sets_closed_status(
    client: TestClient,
    db_session: Session,
    initial_status: TicketStatus,
) -> None:
    ticket = _persist_ticket(
        session=db_session,
        status=initial_status,
    )
    ticket_id = ticket.id
    original_title = ticket.title
    original_description = ticket.description
    original_created_at = ticket.created_at

    response = client.patch(
        f"/tickets/{ticket_id}/close",
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == ticket_id
    assert response_data["title"] == original_title
    assert response_data["description"] == original_description
    assert response_data["status"] == "closed"

    db_session.expire_all()
    stored_ticket = db_session.get(Ticket, ticket_id)

    assert stored_ticket is not None
    assert stored_ticket.status is TicketStatus.CLOSED
    assert stored_ticket.title == original_title
    assert stored_ticket.description == original_description
    assert stored_ticket.created_at == original_created_at


def test_close_ticket_returns_not_found(
    client: TestClient,
) -> None:
    response = client.patch("/tickets/999/close")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticket not found",
    }


def test_close_ticket_rejects_invalid_identifier(
    client: TestClient,
) -> None:
    response = client.patch(
        "/tickets/not-an-integer/close",
    )

    assert response.status_code == 422

    error_locations = {
        tuple(error["loc"]) for error in response.json()["detail"]
    }

    assert ("path", "ticket_id") in error_locations
