import pytest
from fastapi.testclient import TestClient
from app.Database.database import Database
from app.main import app
from app.config import settings
from app.Schemas import token

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
        "email": "user10@google.com",
        "password": "Ab1#vv6666666", 
        "username": "user10"
    }
    response = client.post('/signup', json=user_data)
    new_token = token.Token(**response.json())
    assert response.status_code == 201
    return {
        "username": user_data["email"],
        "password": user_data["password"],
        "access_token": new_token.access_token
    }