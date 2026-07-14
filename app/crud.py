from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ticket
from app.schemas import TicketCreate


def create_ticket(
    session: Session,
    ticket_data: TicketCreate,
) -> Ticket:
    """Create and persist a ticket."""
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        status=ticket_data.status,
    )

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return ticket


def list_tickets(
    session: Session,
) -> list[Ticket]:
    """Return all tickets ordered by identifier."""
    statement = select(Ticket).order_by(Ticket.id)

    return list(session.scalars(statement).all())


def get_ticket(
    session: Session,
    ticket_id: int,
) -> Ticket | None:
    """Return a ticket by identifier, if it exists."""
    return session.get(Ticket, ticket_id)
