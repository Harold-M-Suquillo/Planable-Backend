import pytest
from app.Schemas import token
from app.Tests.conftest import error



def test_root(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_login(client, test_user):
    # Invalid Email
    response = client.post(
        '/login',
        data = {'username': 'invalidEmail@gmail.com', 'password': test_user["password"]}
    )
    err = error(**response.json())
    assert response.status_code == 403


    # Invalid Password
    response = client.post(
        '/login',
        data = {'username': test_user["email"], 'password': '1234'}
    )
    err = error(**response.json())
    assert response.status_code == 403


    # Successful Login
    response = client.post(
        '/login',
        data = {'username': test_user["email"], 'password': test_user["password"]}
    )
    new_token = token.Token(**response.json())
    assert response.status_code == 200


# test that A token is valid
def test_token(client, test_user):
    # Test a Valid Token
    response = client.post(
        '/login/test-token',
        headers = { "Authorization": f"Bearer {test_user['access_token']}" }
    )
    assert response.status_code == 204

    # Test an Invalid token
    response = client.post(
            '/login/test-token',
        headers = { "Authorization": "Bearer kfnlkdsnflasndfdsfndls" }
    )
    err = error(**response.json())
    assert response.status_code == 401


@pytest.mark.parametrize("email, password, username, status_code",[
    ("ValidRequest@gmail.com", "ABCabc123@", "testUser", 201),
    ("InvalidEmail", "ABCabc123@", "testUser", 422),
    ("InvalidPassword@2gmail.com", "123", "testUser", 422),
    ("InvalidUName@gmail.com", "ABCabc123@", "a", 422),
    (None, "ABCabc123@", "testUser", 422),
    ("ValidRequest@gmail.com", None, "testUser", 422),
    ("ValidRequest@gmail.com", "ABCabc123@", None, 422)
])
def test_signup(client, email, password, username, status_code):
    response = client.post(
        '/signup',
        json={
            "email": email,
            "password": password,
            "username": username
        }
    )
    assert response.status_code == status_code
    if response.status_code == 201:
        new_token = token.Token(**response.json())
    elif response.status_code == 422:
        err = error(**response.json())
    else:
        raise Exception("Unknown Result Occured")


# Test a user trying to signup with info that already exists
def test_duplicate_signup(client, test_user):
    # Username already exists
    response = client.post(
        '/signup',
        json={
            "email": test_user['email'],
            "password": "abcD#123",
            "username": "user10"
        }
    )
    err = error(**response.json())
    assert response.status_code == 409

    # email already exists
    response = client.post(
        '/signup',
        json={
            "email": "new_user@google.com",
            "password": "abcD#123",
            "username": test_user['username']
        }
    )
    err = error(**response.json())
    assert response.status_code == 409


def test_login(client, test_user):
    # Invalid Email
    response = client.post(
        '/login',
        data = {'username': 'invalidEmail@gmail.com', 'password': test_user["password"]}
    )
    err = error(**response.json())
    assert response.status_code == 403


    # Invalid Password
    response = client.post(
        '/login',
        data = {'username': test_user["email"], 'password': '1234'}
    )
    err = error(**response.json())
    assert response.status_code == 403


    # Successful Login
    response = client.post(
        '/login',
        data = {'username': test_user["email"], 'password': test_user["password"]}
    )
    new_token = token.Token(**response.json())
    assert response.status_code == 200