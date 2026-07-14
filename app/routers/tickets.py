from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Ticket
from app.schemas import TicketCreate, TicketRead, TicketUpdate

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


@router.get(
    "/",
    response_model=list[TicketRead],
    summary="List tickets",
)
def list_tickets(
    session: Annotated[Session, Depends(get_db)],
) -> list[Ticket]:
    """Return all tickets."""
    return crud.list_tickets(session=session)


@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
    summary="Get a ticket",
)
def get_ticket(
    ticket_id: int,
    session: Annotated[Session, Depends(get_db)],
) -> Ticket:
    """Return a ticket by identifier."""
    ticket = crud.get_ticket(
        session=session,
        ticket_id=ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket


@router.put(
    "/{ticket_id}",
    response_model=TicketRead,
    status_code=status.HTTP_200_OK,
    summary="Update a ticket",
)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    session: Annotated[Session, Depends(get_db)],
) -> Ticket:
    """Fully update a ticket by identifier."""
    ticket = crud.get_ticket(
        session=session,
        ticket_id=ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return crud.update_ticket(
        session=session,
        ticket=ticket,
        ticket_data=ticket_data,
    )
