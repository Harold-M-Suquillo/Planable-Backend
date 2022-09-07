from fastapi import FastAPI
from app.routers import authentication
from app.database import Database
from app.config import settings
from starlette.middleware.cors import CORSMiddleware

# Create fastAPI instance
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
	allow_headers=["*"],
)


# Connect to the database
@app.on_event("startup")
async def startup_event():
    Database.connect(
        settings.database_hostname,
        settings.database_name,
        settings.database_username,
        settings.database_password)
    print("Database Connection opened")

# Close Database Connection
@app.on_event("shutdown")
async def shutdown_event():
    Database.disconnect()
    print("Database Connection closed")

app.include_router(authentication.router)