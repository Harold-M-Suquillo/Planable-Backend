from typing import Optional
from pydantic import BaseModel, EmailStr, constr
from datetime import date, datetime




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


# ----- Tickets -----
class Ticket(BaseModel):
    id: str
    name: str
    priority: str
    assigned_user: str
    type: str
    project: str
    status: str

class TicketResponse(Ticket):
    created_at: datetime

class UserTicket(BaseModel):
    user: str
    ticket_id: str
    





