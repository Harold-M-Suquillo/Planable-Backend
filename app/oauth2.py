from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from app import schemas
from fastapi.security import OAuth2PasswordBearer
from app.database import Database
from app.config import settings
import time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


# Environment Variables
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Creates a JWT token
def create_access_token(data: dict):
    to_encode = data.copy()

    # Create Expiration Time and add to payload
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Encode data and create a JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# Verifies that the access token is valid, checks to see if the token is expired
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        auth: str = payload.get('auth')
        usr: str = payload.get('usr')

        if not auth or not usr:
            raise credentials_exception
        token_data = schemas.TokenData(auth=auth, usr=usr)

    except JWTError:
        raise credentials_exception
    return token_data

# Verifies that the user 
def get_current_user(token: str = Depends(oauth2_scheme)):
    # credential exception 
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Could not validate Credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    return token



