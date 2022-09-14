from fastapi import APIRouter, status, HTTPException, Depends
from app import utils
from typing import List, Optional, Literal
from app.Database.database import Database
from app.Schemas import ticket
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
@router.get('/', response_model=List[ticket.TicketResponse])
def get_tickets(
    current_user: dict = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
    project: Optional[str] = None,
    role: Optional[Literal['Project Manager', 'Developer']] = 'Developer'):

    # if user is provides project check that they are apart of project
    if project:
        Database.cursor.execute(
            """
                SELECT role
                FROM works_on
                WHERE username=%s AND project_id=%s;
            """,
            (current_user.user, project)
        )
        works_on = Database.cursor.fetchone()
        if not works_on:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Project Not Found"])

    Database.cursor.execute(
        """
            SELECT t.id, t.name, t.priority, t.assigned_user, t.type, t.project, t.status, t.created_at
            FROM tickets AS t INNER JOIN (SELECT project_id FROM works_on WHERE username=%s AND role=%s) AS p
                ON t.project = p.project_id
            WHERE t.name LIKE %s AND %s IS NULL or t.project=%s
            ORDER by t.created_at
            OFFSET %s
            LIMIT %s;
        """,
        (current_user.user, role, '%'+search+'%', project, project, skip, limit)
    )
    tickets = Database.cursor.fetchall()
    return tickets

# Get a ticket by id
@router.get('/{id}', response_model=ticket.TicketResponse)
def get_ticket(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    # Try to grab the ticket
    Database.cursor.execute(
        """
            SELECT id, name, priority, assigned_user, type, project, status, created_at
            FROM tickets WHERE id=%s;
        """,
        (id,)
    )
    ticket_response = Database.cursor.fetchone()
    # Case 1) The ticket does not exist -> Error
    if not ticket_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Ticket not Found"])

    # Case 2) The ticket is not assigned to the user -> Error
    if ticket_response['assigned_user'] != current_user.user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=["Ticket is not assigned to current user"])
    # Case 3) The user is qualified to get the ticket
    return ticket_response


# Create a new ticket
# Only a project manager can create a ticket
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ticket.TicketResponse)
def create_ticket(new_ticket: ticket.Ticket, current_user: dict = Depends(oauth2.get_current_user_restrict_demo_user)):
    # Check to see if the Project Manager for the project
    Database.cursor.execute(
        """
            SELECT role
            FROM works_on
            WHERE username=%s AND project_id=%s;
        """,
        (current_user.user, new_ticket.project)
    )
    project_role = Database.cursor.fetchone()
    if not project_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=["Project not found"])

    if project_role['role'] != utils.PROJECT_MANAGER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=["Unauthorized to add a new Ticket"])

    # tickets table have check constraints
    try:
        Database.cursor.execute(
            """
                INSERT INTO tickets(name, priority, assigned_user, type, project, status)
                VALUES(%s, %s, %s, %s, %s, %s)
                RETURNING name, priority, assigned_user, type, project, status, created_at, id;
            """,
            (new_ticket.name, new_ticket.priority, new_ticket.assigned_user, new_ticket.type, new_ticket.project, new_ticket.status)
        )
        new_ticket = Database.cursor.fetchone()
        Database.conn.commit()
        return new_ticket
    except utils.CHECK_VIOLAION:
        Database.conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail=["Query Parameter has an Invalid Value"])

# Update a ticket
# Only a project manager can update complete a ticket
# A user can be a able to set the ticket to review
@router.put('/{id}', response_model=ticket.TicketResponse)
def update_ticket(id: int, updated_ticket: ticket.Ticket, current_user: dict = Depends(oauth2.get_current_user_restrict_demo_user)):
    # try to get the ticket if it exists
    Database.cursor.execute(
        """
            SELECT w.project_id, role 
            FROM works_on AS w INNER JOIN
                (SELECT project from tickets WHERE id=%s) AS t
                ON t.project=w.project_id
            WHERE w.username=%s;
        """,
        (id, current_user.user)
    )
    project_role = Database.cursor.fetchone()
    print(project_role)
    # Case 1) Could not find a ticket
    if not project_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=["Ticket was not found"])
    # Case 2) User is not authorized to update ticket
    if project_role['role'] != utils.PROJECT_MANAGER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=["Unauthorized to modify ticket"])
    # Case 3) Update the ticket
    try:
        Database.cursor.execute(
            """
                UPDATE tickets
                SET name=%s, priority=%s, assigned_user=%s, type=%s, project=%s, status=%s
                WHERE id=%s
                RETURNING id, name, priority, assigned_user, type, project, status, created_at;
            """,
            (updated_ticket.name, updated_ticket.priority, updated_ticket.assigned_user, 
             updated_ticket.type, updated_ticket.project, updated_ticket.status, id)
        )
        Database.conn.commit()
        ticket_response = Database.cursor.fetchone()
        return ticket_response
    except utils.CHECK_VIOLAION:
        Database.conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail=["Query Parameter has an Invalid Value"])
    # The user migh have the authorization to modify tickets but the ticket might not exist
    except utils.FOREIGN_KEY_VIOLATION:
        Database.conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail=["Ticket does not exist"])


# Delete a Ticket
# Only a project manager can delete a ticket
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(id: int, current_user: dict = Depends(oauth2.get_current_user_restrict_demo_user)):
    # Check to see that the ticket exists
    Database.cursor.execute(""" SELECT id FROM tickets WHERE id=%s; """, (id,))
    ticket_id = Database.cursor.fetchone()
    if not ticket_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Ticket Does not Exist"])

    #try to Delete the ticket
    Database.cursor.execute(
        """
            DELETE FROM tickets
            WHERE id=%s AND project IN 
                (SELECT project_id 
                from works_on
                WHERE username=%s AND role=%s)
            RETURNING id;
        """,
        (id, current_user.user, utils.PROJECT_MANAGER)
    )
    deleted_ticket = Database.cursor.fetchone()
    if not delete_ticket:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=["Unauthorized to Delete Ticket"])


# ------- Tickets Comments ------------
# Add a ticket Comment
# Delete a ticket Comment
# Get all ticket Comments
# Get a ticket by id



# When we delete a ticket all the ticket comments should be deleted


