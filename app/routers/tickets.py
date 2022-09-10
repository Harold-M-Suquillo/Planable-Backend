from fastapi import APIRouter, status, HTTPException, Depends


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
def get_tickets():
    pass

# Get a ticket by id
@router.get('/{id}')
def get_ticket():
    pass


# Create a new ticket
# Only a project manager can create a ticket
@router.post('/')
def create_ticket():
    pass



# Update a ticket
# Only a project manager can update complete a ticket
# A user can be a able to set the ticket to review
@router.put('/{id}')
def update_ticket():
    pass



# Add a user to a ticket
@router.post('/user/{user}')
def add_user_to_ticket():
    pass


# Only when a user has comleted a ticket can it be deleted
# Only a project manager can delete a ticket
@router.delete('/{id}')
def delete_ticket():
    pass

