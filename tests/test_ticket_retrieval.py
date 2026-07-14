from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Ticket, TicketStatus

EXPECTED_TICKET_FIELDS = {
    "id",
    "title",
    "description",
    "status",
    "created_at",
}


def _persist_ticket(
    session: Session,
    title: str,
    status: TicketStatus = TicketStatus.OPEN,
) -> Ticket:
    """Create a ticket directly in the test database."""
    ticket = Ticket(
        title=title,
        description=f"Description for {title}.",
        status=status,
    )

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return ticket


def test_list_tickets_returns_empty_list(
    client: TestClient,
) -> None:
    response = client.get("/tickets/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tickets_returns_all_tickets(
    client: TestClient,
    db_session: Session,
) -> None:
    first_ticket = _persist_ticket(
        session=db_session,
        title="First ticket",
    )
    first_ticket_id = first_ticket.id

    second_ticket = _persist_ticket(
        session=db_session,
        title="Second ticket",
        status=TicketStatus.STALLED,
    )
    second_ticket_id = second_ticket.id

    response = client.get("/tickets/")

    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data) == 2
    assert [item["id"] for item in response_data] == [
        first_ticket_id,
        second_ticket_id,
    ]
    assert response_data[0]["title"] == "First ticket"
    assert response_data[0]["status"] == "open"
    assert response_data[1]["title"] == "Second ticket"
    assert response_data[1]["status"] == "stalled"
    assert set(response_data[0]) == EXPECTED_TICKET_FIELDS
    assert set(response_data[1]) == EXPECTED_TICKET_FIELDS


def test_get_ticket_returns_existing_ticket(
    client: TestClient,
    db_session: Session,
) -> None:
    ticket = _persist_ticket(
        session=db_session,
        title="Customer portal unavailable",
        status=TicketStatus.STALLED,
    )
    ticket_id = ticket.id

    response = client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200

    response_data = response.json()

    assert set(response_data) == EXPECTED_TICKET_FIELDS
    assert response_data["id"] == ticket_id
    assert response_data["title"] == ticket.title
    assert response_data["description"] == ticket.description
    assert response_data["status"] == "stalled"
    assert isinstance(response_data["created_at"], str)


def test_get_ticket_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get("/tickets/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticket not found",
    }


def test_get_ticket_rejects_invalid_identifier(
    client: TestClient,
) -> None:
    response = client.get("/tickets/not-an-integer")

    assert response.status_code == 422

    error_locations = {
        tuple(error["loc"]) for error in response.json()["detail"]
    }

    assert ("path", "ticket_id") in error_locations
