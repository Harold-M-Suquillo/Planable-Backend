from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

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
    password: str

# Test token
class TokenData(BaseModel):
    id: Optional[str] = None





