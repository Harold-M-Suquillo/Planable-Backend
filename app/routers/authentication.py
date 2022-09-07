from email.policy import HTTP
from urllib import response
from fastapi import APIRouter, status, HTTPException, Depends
from app.database import Database
from app import schemas, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import schemas

router = APIRouter( tags=['Authentication'] )


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):

    # Query the database for user info 
    Database.cursor.execute(""" SELECT * FROM users WHERE email=%s; """, (user_credentials.username,))
    fetched_data = Database.cursor.fetchone()

    # Email not in the database
    if not fetched_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="invalid credentials")

    # Password not valid
    if not utils.verify(user_credentials.password, fetched_data['password']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="invalid crentials")

    # Credentials valid -> Create and return access token
    access_token = oauth2.create_access_token({"user_id": fetched_data['id']})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# Tests to see if the token is still valid
@router.post('/login/test-token')
def test_token(current_user: dict = Depends(oauth2.get_current_user)):
    return current_user




# The user will sign up
@router.post('/signup',  status_code=status.HTTP_201_CREATED)
def signup(user: schemas.SignUpRequest):
    try:
        # Hash the password
        hashed_password = utils.hash(user.password)
        # Try to insert email/password into database
        Database.cursor.execute(""" INSERT INTO users(email, password) VALUES(%s, %s) RETURNING *; """, (user.email, hashed_password))
        new_user = Database.cursor.fetchone()
        Database.conn.commit()

        # Create and return access token
        access_token = oauth2.create_access_token({"user_id": new_user['id']})
        
        data = {
            "id": new_user['id'],
            "access_token": access_token
        }
        return data

    except utils.UNIQUE_VIOLATION:
        # If request fails we have to rollback the failed transaction and return error
        Database.conn.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"email [{user.email}] is already linked to an account")













