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
