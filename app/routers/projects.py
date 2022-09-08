from fastapi import APIRouter, status, HTTPException, Depends

router = APIRouter(
    prefix='/projects',
    tags=['Projects']
)


# Get all you are a part projects
# Filter between projects you manage and ones you are a developer
# Filter the number of project you want
# filter by projects names that contain a keyword
@router.get('/')
def get_projects():
    pass

# Get a project by id
@router.get('/{id}')
def get_project():
    pass

# Create a new project
# The user creating the project is the Project Manager
@router.post('/')
def create_project():
    pass

# Update a project -> Only an admin is able to update a project
@router.put('/{id}')
def update_project():
    pass

# delete a project
@router.delete('/{id}')
def delete_project():
    pass

# Add a user to a project -> Only an admin is able to update a project
@router.post('/user/{user}')
def add_delete_user_from_project():
    pass