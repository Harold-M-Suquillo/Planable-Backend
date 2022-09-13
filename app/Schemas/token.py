from pydantic import BaseModel, EmailStr, constr
from typing import List


# Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Response - signup
class SignUpResponse(BaseModel):
    id: int
    token: Token

# Request - signup
class SignUpRequest(BaseModel):
    email: EmailStr
    password: constr(regex="^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,15}$")
    username: constr(min_length=3)

# Data Stored in JWT payload
class TokenPayload(BaseModel):
    auth: str
    user: str
