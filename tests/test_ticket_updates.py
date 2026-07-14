from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Ticket, TicketStatus


def _persist_ticket(
    session: Session,
) -> Ticket:
    """Create a ticket directly in the test database."""
    ticket = Ticket(
        title="Original title",
        description="Original description.",
        status=TicketStatus.OPEN,
    )

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return ticket


def test_update_ticket_returns_updated_ticket(
    client: TestClient,
    db_session: Session,
) -> None:
    ticket = _persist_ticket(db_session)
    ticket_id = ticket.id

    payload = {
        "title": "Updated title",
        "description": "Updated description.",
        "status": "stalled",
    }

    response = client.put(
        f"/tickets/{ticket_id}",
        json=payload,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == ticket_id
    assert response_data["title"] == payload["title"]
    assert response_data["description"] == payload["description"]
    assert response_data["status"] == payload["status"]

    created_at = datetime.fromisoformat(
        response_data["created_at"].replace(
            "Z",
            "+00:00",
        )
    )

    assert isinstance(created_at, datetime)


def test_update_ticket_is_persisted(
    client: TestClient,
    db_session: Session,
) -> None:
    ticket = _persist_ticket(db_session)
    ticket_id = ticket.id
    original_created_at = ticket.created_at

    payload = {
        "title": "Updated title",
        "description": "Updated description.",
        "status": "closed",
    }

    response = client.put(
        f"/tickets/{ticket_id}",
        json=payload,
    )

    assert response.status_code == 200

    db_session.expire_all()
    stored_ticket = db_session.get(Ticket, ticket_id)

    assert stored_ticket is not None
    assert stored_ticket.title == payload["title"]
    assert stored_ticket.description == payload["description"]
    assert stored_ticket.status is TicketStatus.CLOSED
    assert stored_ticket.created_at == original_created_at


def test_update_ticket_returns_not_found(
    client: TestClient,
) -> None:
    payload = {
        "title": "Updated title",
        "description": "Updated description.",
        "status": "stalled",
    }

    response = client.put(
        "/tickets/999",
        json=payload,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticket not found",
    }


@pytest.mark.parametrize(
    "missing_field",
    [
        "title",
        "description",
        "status",
    ],
)
def test_update_ticket_requires_all_modifiable_fields(
    client: TestClient,
    db_session: Session,
    missing_field: str,
) -> None:
    ticket = _persist_ticket(db_session)

    payload = {
        "title": "Updated title",
        "description": "Updated description.",
        "status": "stalled",
    }
    payload.pop(missing_field)

    response = client.put(
        f"/tickets/{ticket.id}",
        json=payload,
    )

    assert response.status_code == 422

    error_locations = {
        tuple(error["loc"]) for error in response.json()["detail"]
    }

    assert ("body", missing_field) in error_locations


def test_update_ticket_rejects_invalid_status(
    client: TestClient,
    db_session: Session,
) -> None:
    ticket = _persist_ticket(db_session)

    payload = {
        "title": "Updated title",
        "description": "Updated description.",
        "status": "pending",
    }

    response = client.put(
        f"/tickets/{ticket.id}",
        json=payload,
    )

    assert response.status_code == 422

    error_locations = {
        tuple(error["loc"]) for error in response.json()["detail"]
    }

    assert ("body", "status") in error_locations


@pytest.mark.parametrize(
    ("immutable_field", "value"),
    [
        ("id", 100),
        (
            "created_at",
            "2026-07-14T12:00:00+00:00",
        ),
    ],
)
def test_update_ticket_rejects_immutable_fields(
    client: TestClient,
    db_session: Session,
    immutable_field: str,
    value: int | str,
) -> None:
    ticket = _persist_ticket(db_session)

    payload: dict[str, str | int] = {
        "title": "Updated title",
        "description": "Updated description.",
        "status": "stalled",
    }
    payload[immutable_field] = value

    response = client.put(
        f"/tickets/{ticket.id}",
        json=payload,
    )

    assert response.status_code == 422

    error_locations = {
        tuple(error["loc"]) for error in response.json()["detail"]
    }

    assert ("body", immutable_field) in error_locations
