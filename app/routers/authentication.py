from email.policy import HTTP
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
    access_token = oauth2.create_access_token({"use_id": fetched_data['id']})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post('/signup', response_model=schemas.SignUpResponse)
def signup()












