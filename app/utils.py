from passlib.context import CryptContext
# Handles the hashing
pwd_context = CryptContext(schemas=["bycrpt"], deprecated="auto")

# Hash the password
def hash(password: str):
    return pwd_context.hash(password)

# Compare user provided password with hashed password from database
def verify(plain_password, hashed_passed):
    return pwd_context.verify(plain_password, hashed_passed)

