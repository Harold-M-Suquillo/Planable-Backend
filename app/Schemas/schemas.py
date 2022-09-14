from typing import Optional
from pydantic import BaseModel, EmailStr, constr
from datetime import date, datetime





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
    





