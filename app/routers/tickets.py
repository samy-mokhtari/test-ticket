from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Ticket
from app.schemas import TicketCreate, TicketRead

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


@router.post(
    "/",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ticket",
)
def create_ticket(
    ticket_data: TicketCreate,
    session: Annotated[Session, Depends(get_db)],
) -> Ticket:
    """Create and return a new ticket."""
    return crud.create_ticket(
        session=session,
        ticket_data=ticket_data,
    )
