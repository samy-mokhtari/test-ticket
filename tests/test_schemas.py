from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import Ticket, TicketStatus
from app.schemas import TicketCreate, TicketRead, TicketUpdate


def test_ticket_create_uses_open_status_by_default() -> None:
    ticket = TicketCreate(
        title="Login failure",
        description="The user cannot log in.",
    )

    assert ticket.status is TicketStatus.OPEN


def test_ticket_create_strips_surrounding_whitespace() -> None:
    ticket = TicketCreate(
        title="  Login failure  ",
        description="  The user cannot log in.  ",
    )

    assert ticket.title == "Login failure"
    assert ticket.description == "The user cannot log in."


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("title", "   "),
        ("description", "\t"),
    ],
)
def test_ticket_create_rejects_blank_text_fields(
    field_name: str,
    invalid_value: str,
) -> None:
    data = {
        "title": "Login failure",
        "description": "The user cannot log in.",
    }
    data[field_name] = invalid_value

    with pytest.raises(ValidationError):
        TicketCreate.model_validate(data)


def test_ticket_create_rejects_title_longer_than_255_characters() -> None:
    data = {
        "title": "a" * 256,
        "description": "The user cannot log in.",
    }

    with pytest.raises(ValidationError) as error:
        TicketCreate.model_validate(data)

    assert error.value.errors()[0]["type"] == "string_too_long"
    assert error.value.errors()[0]["loc"] == ("title",)


def test_ticket_create_rejects_invalid_status() -> None:
    data = {
        "title": "Login failure",
        "description": "The user cannot log in.",
        "status": "pending",
    }

    with pytest.raises(ValidationError) as error:
        TicketCreate.model_validate(data)

    assert error.value.errors()[0]["type"] == "enum"
    assert error.value.errors()[0]["loc"] == ("status",)


def test_ticket_create_rejects_extra_fields() -> None:
    data = {
        "title": "Login failure",
        "description": "The user cannot log in.",
        "priority": "urgent",
    }

    with pytest.raises(ValidationError):
        TicketCreate.model_validate(data)


def test_ticket_update_requires_all_modifiable_fields() -> None:
    data = {
        "title": "Updated title",
        "description": "Updated description.",
    }

    with pytest.raises(ValidationError) as error:
        TicketUpdate.model_validate(data)

    missing_fields = {
        item["loc"]
        for item in error.value.errors()
        if item["type"] == "missing"
    }

    assert ("status",) in missing_fields


def test_ticket_read_is_created_from_database_model() -> None:
    created_at = datetime.now(timezone.utc)
    database_ticket = Ticket(
        id=1,
        title="Login failure",
        description="The user cannot log in.",
        status=TicketStatus.STALLED,
        created_at=created_at,
    )

    ticket = TicketRead.model_validate(database_ticket)

    assert ticket.id == 1
    assert ticket.title == "Login failure"
    assert ticket.description == "The user cannot log in."
    assert ticket.status is TicketStatus.STALLED
    assert ticket.created_at == created_at
