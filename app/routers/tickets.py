from fastapi import APIRouter, status, HTTPException, Depends
from app import utils
from typing import List, Optional, Literal
from app.Database.database import Database
from app.Schemas import schemas
from app.Core import oauth2

router = APIRouter(
    prefix='/tickets',
    tags = ['Tickets']
)

# auth (developer) -> Get all the tickets you have been assigned
# auth (Manager) -> all tickets assigned to project
# Filter by the num of tickets you want
# filter by offset
# filter by ticket names that contain a keyword
@router.get('/')
def get_tickets(
    current_user: dict = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
    project: Optional[str] = "",
    role: Optional[Literal['Project Manager', 'Developer']] = 'Developer'):
    # Role = Project Manager
    # Project
    # Yes -> get all tickets for that project that user is project manager to
    # No -> get all tickets for every project that user is project manager to



    # Role = Developer
    # Project
    # Yes -> get all tickets for that project that user is assigned to
    # No -> get all tickets for every project that user is assigned to






    return 10

# Get a ticket by id
@router.get('/{id}')
def get_ticket(id: str, current_user: dict = Depends(oauth2.get_current_user)):
    # Try to grab the ticket

    # Case 1) The ticket does not exist -> Error

    # Case 2) The ticket is not assigned to the user -> Error

    # Case 3) The user is qualified to get the ticket
    pass


# Create a new ticket
# Only a project manager can create a ticket
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.TicketResponse)
def create_ticket(new_ticket: schemas.Ticket, current_user: dict = Depends(oauth2.get_current_user)):
    # Check to see if the Project Manager for the project
    Database.cursor.execute(
        """
            SELECT role
            FROM works_on
            WHERE username=%s AND project_id=%s;
        """,
        (current_user.usr, new_ticket.project)
    )
    project_role = Database.cursor.fetchone()
    if not project_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=["Project not found"])
    if project_role['role'] != utils.PROJECT_MANAGER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=["Unauthorized to add a new Ticket"])

    # If they are allow them to insert
    Database.cursor.execute(
        """
            INSERT INTO tickets(name, priority, assigned_user, type, project, status)
            VALUES(%s, %s, %s, %s, %s, %s)
            RETURNING name, priority, assigned_user, type, project, status, created_at;
        """
    )
    new_ticket = Database.cursor.fetchone()
    Database.conn.commit()
    return new_ticket


# Update a ticket
# Only a project manager can update complete a ticket
# A user can be a able to set the ticket to review
@router.put('/{id}')
def update_ticket():
    pass


# Remove a user from a ticket
@router.delete('/users')
def remove_user_from_ticket():
    pass


# Delete a Ticket
# Only when a user has comleted a ticket can it be deleted
# Only a project manager can delete a ticket
@router.delete('/{id}')
def delete_ticket():
    pass

# ------- Tickets Comments ------------
# Add a ticket Comment
# Delete a ticket Comment


