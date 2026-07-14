from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ticket
from app.schemas import TicketCreate, TicketStatus, TicketUpdate


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


def update_ticket(
    session: Session,
    ticket: Ticket,
    ticket_data: TicketUpdate,
) -> Ticket:
    """Update and persist a ticket."""
    ticket.title = ticket_data.title
    ticket.description = ticket_data.description
    ticket.status = ticket_data.status

    session.commit()
    session.refresh(ticket)

    return ticket


def close_ticket(
    session: Session,
    ticket: Ticket,
) -> Ticket:
    """Close and persist a ticket."""
    ticket.status = TicketStatus.CLOSED

    session.commit()
    session.refresh(ticket)

    return ticket
