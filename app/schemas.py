from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# -- Authentication --

# Reeponse - logging in
class Token(BaseModel):
    access_token: str
    token_type: str

# Response - signup
class SignUpResponse(Token):
    pass






