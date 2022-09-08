from typing import Optional
from pydantic import BaseModel, EmailStr, constr


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
    password: constr(regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", max_length=15)
    username: constr(min_length=3)

# Test token
class TokenData(BaseModel):
    auth: str
    usr: str





