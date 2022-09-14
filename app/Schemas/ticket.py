from pydantic import BaseModel
from datetime import datetime


class Ticket(BaseModel):
    name: str
    priority: str
    assigned_user: str
    type: str
    project: str
    status: str

class TicketResponse(Ticket):
    id: str
    created_at: datetime

class UserTicket(BaseModel):
    user: str
    ticket_id: str
    