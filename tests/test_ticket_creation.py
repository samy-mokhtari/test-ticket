from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Ticket, TicketStatus


def test_create_ticket_returns_created_ticket(
    client: TestClient,
) -> None:
    payload = {
        "title": "Cannot access customer portal",
        "description": "The customer portal returns an error.",
    }

    response = client.post(
        "/tickets/",
        json=payload,
    )

    assert response.status_code == 201

    response_data = response.json()

    assert set(response_data) == {
        "id",
        "title",
        "description",
        "status",
        "created_at",
    }
    assert isinstance(response_data["id"], int)
    assert response_data["id"] > 0
    assert response_data["title"] == payload["title"]
    assert response_data["description"] == payload["description"]
    assert response_data["status"] == "open"

    created_at = datetime.fromisoformat(
        response_data["created_at"].replace("Z", "+00:00")
    )

    assert isinstance(created_at, datetime)


def test_create_ticket_is_persisted(
    client: TestClient,
    db_session: Session,
) -> None:
    payload = {
        "title": "Cannot access customer portal",
        "description": "The customer portal returns an error.",
    }

    response = client.post(
        "/tickets/",
        json=payload,
    )

    ticket_id = response.json()["id"]
    stored_ticket = db_session.get(Ticket, ticket_id)

    assert stored_ticket is not None
    assert stored_ticket.title == payload["title"]
    assert stored_ticket.description == payload["description"]
    assert stored_ticket.status is TicketStatus.OPEN


def test_create_ticket_accepts_explicit_status(
    client: TestClient,
) -> None:
    payload = {
        "title": "Waiting for external provider",
        "description": "The resolution depends on another provider.",
        "status": "stalled",
    }

    response = client.post(
        "/tickets/",
        json=payload,
    )

    assert response.status_code == 201
    assert response.json()["status"] == "stalled"


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("title", "   "),
        ("description", "\t"),
    ],
)
def test_create_ticket_rejects_blank_text_fields(
    client: TestClient,
    field_name: str,
    invalid_value: str,
) -> None:
    payload = {
        "title": "Cannot access customer portal",
        "description": "The customer portal returns an error.",
    }
    payload[field_name] = invalid_value

    response = client.post(
        "/tickets/",
        json=payload,
    )

    assert response.status_code == 422

    error_locations = {
        tuple(error["loc"]) for error in response.json()["detail"]
    }

    assert ("body", field_name) in error_locations


def test_create_ticket_rejects_invalid_status(
    client: TestClient,
) -> None:
    payload = {
        "title": "Cannot access customer portal",
        "description": "The customer portal returns an error.",
        "status": "pending",
    }

    response = client.post(
        "/tickets/",
        json=payload,
    )

    assert response.status_code == 422

    error_locations = {
        tuple(error["loc"]) for error in response.json()["detail"]
    }

    assert ("body", "status") in error_locations


def test_create_ticket_rejects_extra_fields(
    client: TestClient,
) -> None:
    payload = {
        "title": "Cannot access customer portal",
        "description": "The customer portal returns an error.",
        "priority": "urgent",
    }

    response = client.post(
        "/tickets/",
        json=payload,
    )

    assert response.status_code == 422

    error_locations = {
        tuple(error["loc"]) for error in response.json()["detail"]
    }

    assert ("body", "priority") in error_locations
