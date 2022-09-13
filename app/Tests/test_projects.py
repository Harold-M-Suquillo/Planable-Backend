import re
from venv import create
import pytest
from app.Schemas import project
from app.Tests.conftest import error
from app.Database.database import Database
from typing import List, Optional, Literal
from app.Schemas import token
from app.Tests.conftest import error


@pytest.mark.parametrize("name, description, status_code",[
    ("validName", "validDescription", 201),
    (None, "ValidDescription", 422),
    ("validName", None, 422)
])
def test_create_project(auth_client, name, description, status_code):
    response = auth_client.post(
        '/projects/',
        json={"name": name, "description": description}
    )
    assert response.status_code == status_code
    if response.status_code == 422:
        err = error(**response.json())
    elif response.status_code == 201:
        new_project = project.Project(**response.json())
    else:
        raise Exception("Unknown Response")


def test_get_projects(auth_client, create_projects):
    response = auth_client.get(
        '/projects/?role=Project%20Manager'
    )
    assert len(response.json()) == len(create_projects)
    for project_response in response.json():
        new_project = project.ProjectResponse(**project_response)
    assert response.status_code == 200


def test_get_project(auth_client, create_projects):

    # Get valid projects
    for id in create_projects:
        response = auth_client.get(
            f"/projects/{id}",
        )
        assert response.status_code == 200
        response_project = project.ProjectResponse(**response.json())
    
    # Get a project that does not exist
    response = auth_client.get(
        f"/projects/-3",
    )
    assert response.status_code == 404
    err = error(**response.json())

def test_add_user_to_project(auth_client, test_user, create_projects, test_user2):

    # Add an exisiting user to a non-exisiting project
    for id in [-1, -2, -3]:
        response = auth_client.post(
            '/projects/users',
            json={"user": test_user2['username'], "project_id": id}
        )
        assert response.status_code == 404
        err = error(**response.json())

    # Add a non exisitng user to an exisitng user
    for id in create_projects:
        response = auth_client.post(
            '/projects/users',
            json={"user": "-100", "project_id": id}
        )
        assert response.status_code == 404
        err = error(**response.json())

    # Add a non-exising user to a non exisitng user
    for id in [-1, -2, -3]:
        response = auth_client.post(
            '/projects/users',
            json={"user": id, "project_id": id}
        )
        assert response.status_code == 404
        err = error(**response.json())
    
    # Project Manager adding a user
    for id in create_projects:
        response = auth_client.post(
            '/projects/users',
            json={"user": test_user2['username'], "project_id": id}
        )
        assert response.status_code == 201
        user = project.New_worker(**response.json())
        

    # Developer trying to add people to project
    for id in create_projects:
        response = auth_client.post(
            '/projects/users',
            headers={"Authorization": f"Bearer {test_user2['access_token']}"},
            json={"user": test_user['username'], "project_id": id}
        )
        assert response.status_code == 401
        err = error(**response.json())


# Delete a project
def test_delete_project(auth_client, create_projects2, test_user, test_user2, test_user3): 

    # Have a User that does not work on project try to delete project
    for id in create_projects2:
        response = auth_client.delete(
            f"/projects/{id}",
            headers={"Authorization": f"Bearer {test_user3['access_token']}"}
        )
        assert response.status_code == 404
        err = error(**response.json())

    # Have a Devleoper of a project try to delete
    for id in create_projects2:
        response = auth_client.delete(
            f"/projects/{id}",
            headers={"Authorization": f"Bearer {test_user2['access_token']}"}
        )
        assert response.status_code == 401
        err = error(**response.json())

    # Have a Project Manager delete the project
    for id in create_projects2:
        response = auth_client.delete(f"/projects/{id}")
        assert response.status_code == 204

# Remove a user from project
def test_remove_user_from_project(auth_client, create_projects2, test_user, test_user2, test_user3):


    # Have a user who is not within a project try to delete
    for id in create_projects2:
        response = auth_client.delete(
            f"/projects/{id}/users/{test_user['username']}",
            headers={"Authorization": f"Bearer {test_user3['access_token']}"}
        )
        assert response.status_code == 404
        err = error(**response.json())

    # Have a Developer try to delete user
    for id in create_projects2:
        response = auth_client.delete(
            f"/projects/{id}/users/{test_user['username']}",
            headers={"Authorization": f"Bearer {test_user2['access_token']}"}
        )

        assert response.status_code == 401
        err = error(**response.json())

    # Have a project Manager try to delete a user
    for id in create_projects2:
        response = auth_client.delete(
            f"/projects/{id}/users/{test_user2['username']}"
        )
        assert response.status_code == 204

    # Try to delete a user that does not exist
    for id in create_projects2:
        response =auth_client.delete(
            f"/projects/{id}/users/{-21}"
        )
        assert response.status_code == 404
        err = error(**response.json())

def test_update_project(auth_client, create_projects2, test_user, test_user2, test_user3):
    # User not in the project trying to update project
    for id in create_projects2:
        response = auth_client.put(
            f"/projects/{id}",
            headers={"Authorization": f"Bearer {test_user3['access_token']}"},
            json={"name": "New Project Name", "description": 'New Description for project'}
        )
        assert response.status_code == 404
        err = error(**response.json())

    # Developer trying to update project
    for id in create_projects2:
        response = auth_client.put(
             f"/projects/{id}",
            headers={"Authorization": f"Bearer {test_user2['access_token']}"},
            json={"name": "New Project Name", "description": 'New Description for project'}
        )
        assert response.status_code == 401
        err = error(**response.json())

    # Project Manager tries to update project
    for id in create_projects2:
        response = auth_client.put(
            f"/projects/{id}",
            json={"name": "New Project Name", "description": "New Description for project"}
        )
        assert response.status_code == 200
        new_project = project.ProjectResponse(**response.json())
        assert new_project.name == "New Project Name"
        assert new_project.description == "New Description for project"




