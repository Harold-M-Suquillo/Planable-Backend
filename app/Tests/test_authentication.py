from app.Schemas import token

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
    


def test_login(client, test_user):
    # Invalid Email
    response = client.post(
        '/login',
        data = {'username': 'invalidEmail@gmail.com', 'password': test_user["password"]}
    )
    error = token.error(**response.json())
    assert response.status_code == 403


    # Invalid Password
    response = client.post(
        '/login',
        data = {'username': test_user["username"], 'password': '1234'}
    )
    error = token.error(**response.json())
    assert response.status_code == 403


    # Successful Login
    response = client.post(
        '/login',
        data = {'username': test_user["username"], 'password': test_user["password"]}
    )
    new_token = token.Token(**response.json())
    assert response.status_code == 200


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
    error = token.error(**response.json())
    assert response.status_code == 401










