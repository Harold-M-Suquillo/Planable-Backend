from passlib.context import CryptContext
from psycopg2 import errors
from fastapi import status, HTTPException, Depends
from app import oauth2

# Unique Violation
UNIQUE_VIOLATION = errors.lookup('23505')

# Foreign Key Violation
FOREIGN_KEY_VIOLATION = errors.lookup('23503')

# Project Manger Role
PROJECT_MANAGER = 'Project Manager'

# Developer Role
DEVELOPER = 'Developer'

# Demo Role
DEMO = 'Demo'

# Handles the hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password
def hash(password: str):
    return pwd_context.hash(password)

# Compare user provided password with hashed password from database
def verify(plain_password, hashed_passed):
    return pwd_context.verify(plain_password, hashed_passed)

