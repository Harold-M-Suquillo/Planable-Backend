from app.Database.database import Database
from app.main import app
import pytest
from app.config import settings
from fastapi.testclient import TestClient
from app.Schemas import token

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
        """ DELETE FROM users;
            DELETE FROM projects;
            DELETE FROM works_on;
            DELETE FROM tickets;
        """
    )
    Database.conn.commit()
    yield TestClient(app)
    Database.cursor.execute(""" DELETE FROM users; """)
    Database.conn.commit()



def test_create_project(client):
    pass

def test_get_projects(client):
    pass

def test_get_project(client):
    pass

def test_add_user_to_project(client):
    pass

def test_remove_user_to_project(client):
    pass

def test_update_project(client):
    pass

def test_delete_project(client):
    pass



