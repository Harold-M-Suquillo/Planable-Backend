from email.policy import HTTP
from urllib import response
from fastapi import APIRouter, status, HTTPException, Depends
from app import utils
from typing import List, Optional, Literal
from app.Database.database import Database
from app.Schemas import schemas
from app.Core import oauth2
from app.Schemas import project

router = APIRouter(
    prefix='/projects',
    tags=['Projects']
)


# Get all you are a part projects
# Filter between projects you manage and ones you are a developer
# Filter the number of project you want
# filter by projects names that contain a keyword
@router.get('/', response_model=List[project.ProjectResponse])
def get_projects(
    current_user: dict = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
    role: Optional[Literal['Project Manager', 'Developer']] = 'Developer'):

    Database.cursor.execute(
        """ SELECT p.id, p.name, p.description, p.created_at
            FROM works_on AS w INNER JOIN projects AS p 
                ON w.project_id = p.id
            WHERE p.name LIKE %s AND w.username=%s AND w.role=%s
            ORDER BY p.created_at DESC
            OFFSET %s
            LIMIT %s;
        """,
        ('%'+search+'%', current_user.user, role, skip, limit)
    )
    projects = Database.cursor.fetchall()
    return projects


# Get a project by id
@router.get('/{id}', response_model=project.ProjectResponse) # -> DONE
def get_project(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    #1) Do they work on the Project and project exist? Yes -> Allow / No -> raise exception
    Database.cursor.execute(
        """ 
            SELECT project_id
            FROM works_on
            WHERE project_id=%s AND username=%s;
        """, 
        (id, current_user.user)
    )
    project_id = Database.cursor.fetchone()
    if not project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=[f"project with id {id} does not exist or you don't have access"])


    # 2) If they work on the project return project data
    Database.cursor.execute(
        """ 
            SELECT id, name, description, created_at
            FROM projects
            WHERE id=%s;
        """,
        (project_id['project_id'],)
    )
    project_data = Database.cursor.fetchone()
    return project_data


# Create a new project
# The user creating the project is the Project Manager -> DONE
@router.post('/', response_model=project.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data: project.Project, current_user: dict = Depends(oauth2.get_current_user_restrict_demo_user)):
    # 1) Add the new project to the database
    Database.cursor.execute(
        """
            INSERT INTO projects(name, description)
            VALUES(%s,%s)
            RETURNING id, name, description, created_at;
        """,
        (project_data.name,project_data.description)
    )
    project_info = Database.cursor.fetchone()

    # 2) Make the user the project manager
    Database.cursor.execute(
        """
            INSERT INTO works_on(username, project_id, role)
            VALUES(%s, %s, %s);
        """,
        (current_user.user, project_info['id'], utils.PROJECT_MANAGER)
    )
    Database.conn.commit()
    return project_info



# Update a project -> Only an admin is able to update a project
@router.put('/{id}', response_model=project.ProjectResponse)
def update_project(id: str, project: project.Project, current_user: dict = Depends(oauth2.get_current_user_restrict_demo_user)):
    # 1) Check if the user is the project manager YES -> Allow / NO -> Raise Exception
    Database.cursor.execute(
        """
            SELECT project_id, role
            FROM works_on
            WHERE project_id=%s AND username=%s;
        """,
        (id, current_user.user)
    )
    project_data = Database.cursor.fetchone()
    if not project_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=["Project not found"])
    # Check if user is not authorized to modify project
    if project_data['role'] != utils.PROJECT_MANAGER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=["Unauthorized to modify project"])

    # Modify the project as needed
    Database.cursor.execute(
        """
            UPDATE projects
            SET name=%s, description=%s
            WHERE id=%s
            RETURNING name, description, id, created_at;
        """,
        (project.name,project.description, project_data['project_id'])
    )
    Database.conn.commit()
    updated_project = Database.cursor.fetchone()
    return updated_project


# Add a user to a project -> Only an admin is able to update a project -> DONE
@router.post('/users', response_model=project.New_worker, status_code=status.HTTP_201_CREATED)
def add_user_to_project(data: project.User_works_on, current_user: dict = Depends(oauth2.get_current_user_restrict_demo_user)):
    # Query for project and role
    Database.cursor.execute(
        """
            SELECT project_id, role
            FROM works_on
            WHERE project_id=%s AND username=%s;
        """,
        (data.project_id, current_user.user)
    )
    project_info = Database.cursor.fetchone()

    # Not association to project
    if not project_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=["Project Not Found"])
    
    # Not authorized to add people
    if project_info['role'] != utils.PROJECT_MANAGER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=["Unauthorized to add new people"])
    try:
        Database.cursor.execute(
            """
                INSERT INTO works_on(username, project_id, role)
                VALUES(%s, %s, %s)
                RETURNING username AS user, project_id, role;
            """,
            (data.user, data.project_id, utils.DEVELOPER)
        )
        Database.conn.commit()
        new_developer = Database.cursor.fetchone()
        return new_developer

    except utils.UNIQUE_VIOLATION:
        Database.conn.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=["User is already apart of project"])
    except utils.FOREIGN_KEY_VIOLATION:
        Database.conn.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=["User was not found"])

# Remove a user from a project
@router.delete('/{project_id}/users/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user_from_project(project_id: str, id: str, current_user: dict = Depends(oauth2.get_current_user_restrict_demo_user)):
    # Query for the project
    Database.cursor.execute(
        """
            SELECT project_id, role
            FROM works_on
            WHERE project_id=%s AND username=%s;
        """,
        (project_id, current_user.user)
    )
    project_data = Database.cursor.fetchone()
    # Does Project exist or connection
    if not project_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=["Project Not Found"]) 

    # Check if user has authorization
    if project_data['role'] != utils.PROJECT_MANAGER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=["Unauthorized to remove users"])

    # Try to delete from the database
    Database.cursor.execute(
        """
            DELETE FROM works_on
            WHERE project_id=%s AND username=%s AND role=%s
            RETURNING username;
        """,
        (project_id, id, utils.DEVELOPER)
    )
    Database.conn.commit()
    deleted_user = Database.cursor.fetchone()
    if not deleted_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=["User not found"])

# delete a project
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_project(id: str, current_user: dict = Depends(oauth2.get_current_user_restrict_demo_user)):

    # Check if the project exists that I am apart of
    Database.cursor.execute(
        """
            SELECT project_id, role
            FROM works_on 
            WHERE project_id=%s AND username=%s;
        """,
        (id, current_user.user)
    )
    project = Database.cursor.fetchone()


    # Could not find project
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=["Could not find project"])
    
    # Check if im authorized to delete
    if project['role'] == "Project Manager":
        # Remove the project
        Database.cursor.execute(
            """
                DELETE FROM projects
                WHERE id=%s;
            """,
            (project['project_id'],)
        )
        Database.conn.commit()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=["Unauthorized to delete Project"])