from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Ticket
from app.schemas import ErrorResponse, TicketCreate, TicketRead, TicketUpdate

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)

NOT_FOUND_RESPONSES: dict[
    int | str,
    dict[str, Any],
] = {
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorResponse,
        "description": ("The requested ticket does not exist."),
    }
}


def _get_ticket_or_404(
    session: Session,
    ticket_id: int,
) -> Ticket:
    """Return a ticket or raise an HTTP 404 error."""
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


@router.post(
    "/",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ticket",
    operation_id="create_ticket",
    response_description="The newly created ticket.",
)
def create_ticket(
    ticket_data: TicketCreate,
    session: Annotated[Session, Depends(get_db)],
) -> Ticket:
    """Create and return a ticket.

    The status defaults to `open` when it is omitted.
    """
    return crud.create_ticket(
        session=session,
        ticket_data=ticket_data,
    )


@router.get(
    "/",
    response_model=list[TicketRead],
    summary="List tickets",
    operation_id="list_tickets",
    response_description=("The tickets ordered by identifier."),
)
def list_tickets(
    session: Annotated[Session, Depends(get_db)],
) -> list[Ticket]:
    """Return all tickets ordered by identifier.

    An empty list is returned when no tickets exist.
    """
    return crud.list_tickets(session=session)


@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
    summary="Get a ticket",
    operation_id="get_ticket",
    response_description="The requested ticket.",
    responses=NOT_FOUND_RESPONSES,
)
def get_ticket(
    ticket_id: int,
    session: Annotated[Session, Depends(get_db)],
) -> Ticket:
    """Return a ticket by identifier.

    A `404` response is returned when the ticket does
    not exist.
    """
    return _get_ticket_or_404(
        session=session,
        ticket_id=ticket_id,
    )


@router.put(
    "/{ticket_id}",
    response_model=TicketRead,
    status_code=status.HTTP_200_OK,
    summary="Update a ticket",
    operation_id="update_ticket",
    response_description="The updated ticket.",
    responses=NOT_FOUND_RESPONSES,
)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    session: Annotated[Session, Depends(get_db)],
) -> Ticket:
    """Fully update a ticket by identifier.

    The request must contain the title, description,
    and status. The identifier and creation date
    cannot be modified.
    """
    ticket = _get_ticket_or_404(
        session=session,
        ticket_id=ticket_id,
    )

    return crud.update_ticket(
        session=session,
        ticket=ticket,
        ticket_data=ticket_data,
    )


@router.patch(
    "/{ticket_id}/close",
    response_model=TicketRead,
    status_code=status.HTTP_200_OK,
    summary="Close a ticket",
    operation_id="close_ticket",
    response_description="The closed ticket.",
    responses=NOT_FOUND_RESPONSES,
)
def close_ticket(
    ticket_id: int,
    session: Annotated[Session, Depends(get_db)],
) -> Ticket:
    """Close a ticket by identifier.

    Closing an already closed ticket is idempotent and
    still returns a successful response.
    """
    ticket = _get_ticket_or_404(
        session=session,
        ticket_id=ticket_id,
    )

    return crud.close_ticket(
        session=session,
        ticket=ticket,
    )
