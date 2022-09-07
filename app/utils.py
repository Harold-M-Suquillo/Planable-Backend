from passlib.context import CryptContext
from psycopg2 import errors

# Handles the hashing

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password
def hash(password: str):
    return pwd_context.hash(password)

# Compare user provided password with hashed password from database
def verify(plain_password, hashed_passed):
    return pwd_context.verify(plain_password, hashed_passed)

# Unique Violation for insertion into database
UNIQUE_VIOLATION = errors.lookup('23505')