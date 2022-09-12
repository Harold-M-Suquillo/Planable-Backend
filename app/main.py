from fastapi import FastAPI, Request, status
from app.Routers import authentication, projects, tickets
from app.Database.database import Database
from app.config import settings
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

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
def startup_event():
    Database.connect(
        settings.database_hostname,
        settings.database_name,
        settings.database_username,
        settings.database_password)
    print("Database Connection opened")

# Close Database Connection
@app.on_event("shutdown")
def shutdown_event():
    Database.disconnect()
    print("Database Connection closed")


# Modify the Pydantic error response to only return message 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Get the original 'detail' list of errors
    details = exc.errors()
    # Use a list as we might raise multiple errors
    modified_details = []
    # Replace 'msg' with 'message' for each error
    for error in details:
        modified_details.append(error["msg"])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": modified_details}),
    )


# Route path used to test health of app
@app.get("/")
def root():
    return {"msg": "Hello World"}


# Add paths to app
app.include_router(authentication.router)
app.include_router(projects.router)
app.include_router(tickets.router)

