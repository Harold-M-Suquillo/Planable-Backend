import pytest
from typing import List
from pydantic import BaseModel
from fastapi.testclient import TestClient
from psycopg2.extras import execute_values
from app.Database.database import Database
from app.Schemas import token
from app.config import settings
from app.main import app
from app import utils

# Pydantic Model For Error format Validation
class error(BaseModel):
    detail: List[str]

# ---------- Handle Database Connection -------------
# Connect to the Database Fixture
@pytest.fixture(scope="module")
def connect():
    Database.connect(
    settings.database_hostname,
    settings.database_name,
    settings.database_username,
    settings.database_password)
    yield 
    Database.disconnect()


# Fixture Cleans up after each test and provides new client
@pytest.fixture()
def client(connect):
    Database.cursor.execute(
        """ 
            DELETE FROM users;
            DELETE FROM projects;
            DELETE FROM works_on;
            DELETE FROM tickets;
            DELETE FROM ticket_comments;
        """
    )
    Database.conn.commit()
    yield TestClient(app)
    Database.cursor.execute(
        """ 
            DELETE FROM users;
            DELETE FROM projects;
            DELETE FROM works_on;
            DELETE FROM tickets;
            DELETE FROM ticket_comments;
        """
    )
    Database.conn.commit()


# This fixture will create a new user
@pytest.fixture
def test_user(client):
    user_data = {    
        "email": "user1@google.com",
        "password": "Ab1#vv6666666", 
        "username": "user1"
    }
    response = client.post('/signup', json=user_data)
    new_token = token.Token(**response.json())
    assert response.status_code == 201
    return {
        "email": user_data["email"],
        "password": user_data["password"],
        "username": user_data["username"],
        "access_token": new_token.access_token
    }

# This fixture will create a second new user
@pytest.fixture
def test_user2(client):
    user_data = {    
        "email": "user2@google.com",
        "password": "Ab1#vv6666666", 
        "username": "user2"
    }
    response = client.post('/signup', json=user_data)
    new_token = token.Token(**response.json())
    assert response.status_code == 201
    return {
        "email": user_data["email"],
        "password": user_data["password"],
        "username": user_data["username"],
        "access_token": new_token.access_token
    }

# Fixture will create a third user
@pytest.fixture
def test_user3(client):
    user_data = {    
        "email": "user3@google.com",
        "password": "Ab1#vv6666666", 
        "username": "user3"
    }
    response = client.post('/signup', json=user_data)
    new_token = token.Token(**response.json())
    assert response.status_code == 201
    return {
        "email": user_data["email"],
        "password": user_data["password"],
        "username": user_data["username"],
        "access_token": new_token.access_token
    }


# This fixture will return a token
@pytest.fixture
def test_token(test_user):
    return {"access_token": test_user['access_token']}

# Configure the client with authorization
@pytest.fixture
def auth_client(client, test_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_token['access_token']}"
    }
    return client

# This fixture will create a projects and attach user as Project manager
@pytest.fixture
def create_projects(test_user):
    posts_data = [
        (test_user['username'], "project 1", "description of project 1"),
        (test_user['username'], "project 2", "description of project 2"),
        (test_user['username'], "project 3", "description of project 3")
    ]
    project_id = []
    for username, name, description in posts_data:
        # Add project To Database
        Database.cursor.execute(
            """
                INSERT INTO projects(name, description)
                VALUES(%s, %s)
                RETURNING id;
            """,
            (name, description)
        )
        new_project = Database.cursor.fetchone()
        project_id.append(new_project['id'])
        # Add make user work on project
        Database.cursor.execute(
            """
                INSERT INTO works_on(username, project_id, role)
                VALUES(%s, %s, %s);
            """,
            (username, new_project['id'], utils.PROJECT_MANAGER)
        )
    Database.conn.commit()
    return project_id

# Fixture will create 3 projects, add a Developer, and Project Manager
@pytest.fixture
def create_projects2(test_user, test_user2):
    posts_data = [
        (test_user['username'], "project 1", "description of project 1"),
        (test_user['username'], "project 2", "description of project 2"),
        (test_user['username'], "project 3", "description of project 3")
    ]
    project_id = []
    for username, name, description in posts_data:
        # Add project To Database
        Database.cursor.execute(
            """
                INSERT INTO projects(name, description)
                VALUES(%s, %s)
                RETURNING id;
            """,
            (name, description)
        )
        new_project = Database.cursor.fetchone()
        project_id.append(new_project['id'])
        # Add make user work on project
        Database.cursor.execute(
            """
                INSERT INTO works_on(username, project_id, role)
                VALUES(%s, %s, %s);

                INSERT INTO works_on(username, project_id, role)
                VALUES(%s, %s, %s);
            """,
            (
                username, new_project['id'], utils.PROJECT_MANAGER,
                test_user2['username'], new_project['id'], utils.DEVELOPER
            )
        )
    Database.conn.commit()
    return project_id

# Fixture will create 3 project and assign test_user as the a Manager and test_user2 as a Developer
@pytest.fixture
def create_tickets(test_user, test_user2):
    project_data = [
        ("project 1", "project 1 Description"),
        ("project 2", "project 2 Description"),
        ("project 3", "project 3 Description")
    ]
    # Assigned User and project are missing
    ticket_data = [
        {"name": "Ticket 1", "priority": "Low", "type": "Bugs/Errors", "status": "Open"},
        {"name": "Ticket 2", "priority": "None", "type": "Feature Requests", "status": "New"},
        {"name": "Ticket 3", "priority": "High", "type": "Training/Document Requests", "status": "Additional Info Required"}
    ]
    projects_id = []
    # Loop through project and add to DB also add works_on
    for name, description in project_data:
        Database.cursor.execute(
            """
                INSERT INTO projects(name, description)
                VALUES(%s, %s)
                RETURNING id;
            """,
            (name, description)
        )
        id = Database.cursor.fetchone()
        projects_id.append(id['id'])

    # Add a developer and Project Manager to the projects
    for id in projects_id:
        Database.cursor.execute(
            """
                INSERT INTO works_on(username, project_id, role)
                VALUES (%s, %s, %s), (%s, %s, %s);
            """,
            (test_user['username'], id, utils.PROJECT_MANAGER, test_user2['username'], id, utils.DEVELOPER)
        )
    tickets_id = []
    # Loop through the tickets and add to DB
    for index, id in enumerate(projects_id):
        Database.cursor.execute(
            """
                INSERT INTO tickets(name, priority, assigned_user, type, project, status)
                VALUES(%s, %s, %s, %s, %s, %s);
                RETURNING id;
            """,
            (ticket_data[index]["name"], ticket_data[index]["priority"], test_user2['username'],
             ticket_data[index]["type"], id, ticket_data[index]["status"])
        )
        ticket_id = Database.cursor.fetchone()
        tickets_id.append(ticket_id['id'])
    Database.conn.commit()
    return {
        "tickets": tickets_id,
        "projects": projects_id,
    }
