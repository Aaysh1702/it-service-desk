from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- User Schemas ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    model_config = {"from_attributes": True}

# --- Ticket Schemas ---
class TicketCreate(BaseModel):
    title: str
    description: str
    category: str
    priority: str = "Medium"
    user_id: int  # We need to know who is creating the ticket

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    user_id: int
    created_at: datetime
    sla_due_at: Optional[datetime] = None  
    
    model_config = {"from_attributes": True}

class TicketUpdate(BaseModel):
    status: str
    assigned_to_id: Optional[int] = None