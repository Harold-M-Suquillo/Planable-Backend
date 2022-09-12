
from app.Database.database import Database
from app.main import app
import pytest
from app.config import settings
from fastapi.testclient import TestClient
from app.Schemas import token

# Fixture Connects to Test Database, Cleans Database before and after tests
@pytest.fixture(scope="module")
def client():
    Database.connect(
        settings.database_hostname,
        settings.database_name,
        settings.database_username,
        settings.database_password)
    Database.cursor.execute(
        """ 
        DELETE FROM users;
        DELETE FROM projects;
        DELETE FROM ticket_comments;
        DELETE FROM works_on;
        DELETE FROM tickets;
        """
    )
    Database.conn.commit()
    yield TestClient(app)
    Database.cursor.execute(
        """ 
        DELETE FROM users;
        DELETE FROM projects;
        DELETE FROM ticket_comments;
        DELETE FROM works_on;
        DELETE FROM tickets;
        """
    )
    Database.conn.commit()
    Database.disconnect()



def test_root(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_signup(client):
    # Create a new user
    response = client.post(
        '/signup',
        json={
            "email": "user10@google.com",
            "password": "abcD#123",
            "username": "user10"
        }
    )
    new_token = token.Token(**response.json())
    assert response.status_code == 201

    # User already exists
    response = client.post(
        '/signup',
        json={
            "email": "user10@google.com",
            "password": "abcD#123",
            "username": "user10"
        }
    )
    error = token.error(**response.json())
    assert response.status_code == 409
    


def test_login(client):
    # Invalid Email
    response = client.post(
        '/login',
        data = {'username': 'user100@google.com', 'password': 'abcD#123'}
    )
    
    error = token.error(**response.json())
    assert response.status_code == 403

    # Invalid Password
    response = client.post(
        '/login',
        data = {'username': 'user10@google.com', 'password': '1234'}
    )
    
    error = token.error(**response.json())
    assert response.status_code == 403

    # Successful Login
    response = client.post(
        '/login',
        data = {'username': 'user10@google.com', 'password': 'abcD#123'}
    )

    new_token = token.Token(**response.json())
    assert response.status_code == 200


def test_token(client):
    # Test a Valid Token
    response = client.post(
        '/login',
        data = {'username': 'user10@google.com', 'password': 'abcD#123'}
    )
    new_token = token.Token(**response.json())

    response = client.post(
        '/login/test-token',
        headers = { "Authorization": f"Bearer {new_token.access_token}" }
    )
    assert response.status_code == 204

    # Test an Invalid token
    response = client.post(
            '/login/test-token',
        headers = { "Authorization": "Bearer kfnlkdsnflasndfdsfndls" }
    )
    error = token.error(**response.json())
    assert response.status_code == 401










