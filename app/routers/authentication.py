from fastapi import APIRouter, status, HTTPException, Depends
from app.Database.database import Database
from app import utils
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.Schemas import token
from app.Core import oauth2
router = APIRouter( tags=['Authentication'] )

@router.post('/login', response_model=token.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):


    # Query the database for user info 
    Database.cursor.execute(""" SELECT role, password, username FROM users WHERE email=%s; """, (user_credentials.username,))
    fetched_data = Database.cursor.fetchone()

    # Email not in the database
    if not fetched_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=["invalid credentials"])

    # Password not valid
    if not utils.verify(user_credentials.password, fetched_data['password']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=["invalid credentials"])

    # Credentials valid -> Create and return access token
    access_token = oauth2.create_access_token({"auth": fetched_data['role'], "user": fetched_data['username']})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# Tests to see if the token is still valid
@router.post('/login/test-token', status_code=status.HTTP_204_NO_CONTENT)
def test_token(current_user: dict = Depends(oauth2.get_current_user)):
    pass




# The user will sign up (By default authorization is set to User)
@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=token.Token)
def signup(user: token.SignUpRequest):
    try:
        # Hash the password
        hashed_password = utils.hash(user.password)
        # Try to insert into database -> by default make a auth level 'User'
        Database.cursor.execute(
            """ INSERT INTO users(username, email, password, role) 
                VALUES(%s ,%s, %s, 'User')
                RETURNING role, username
            """, 
            (user.username, user.email, hashed_password)
        )
        new_user = Database.cursor.fetchone()
        Database.conn.commit()

        # Create and return access token with id and auth 
        access_token = oauth2.create_access_token({"auth": new_user['role'], "user": new_user['username']})

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


    except utils.UNIQUE_VIOLATION as error:
        # If request fails we have to rollback the failed transaction and return error
        # Find the key that caused the violation
        key = error.pgerror
        Database.conn.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=[f"{key[key.find('(')+1 : key.find(')')]} is already linked to an account"])













