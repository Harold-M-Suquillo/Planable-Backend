from typing import Optional
from pydantic import BaseModel, EmailStr, constr
from datetime import date, datetime

# ----- Authentication -----

# Response - logging in
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

# Test token
class TokenData(BaseModel):
    auth: str
    usr: str


# ----- Projects -----
class project(BaseModel):
    name: str
    description: str

# Response - get
class projectResponse(project):
    id: str
    created_at: date

class AddUserToProject(BaseModel):
    user: str
    project_id: str
