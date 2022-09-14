import pytest
from app.Schemas import ticket
from app.Tests.conftest import error

# need a user to create projects and assign them to a user
@pytest.mark.parametrize("name, priority, assigned_user, type, status, status_code", [
    ("ticket 1", "Low", "test_user2", "Bugs/Errors", "New", 201),
    (None, "Low", "test_user2", "Bugs/Errors", "New", 422),
])
def test_create_ticket(auth_client, create_projects2, name, priority, assigned_user):
    response = auth_client.post(
        '/tickets/',
        json={}
    )
    


def test_get_tickets():
    pass

def test_get_ticket():
    pass


def test_update_ticket():
    pass

def test_delete_ticket():
    pass
