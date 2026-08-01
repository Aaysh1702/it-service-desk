from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta  
import models
import schemas
from database import engine, get_db

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IT Service Desk API",
    description="ITIL-aligned ticketing system",
    version="1.0.0"
)

# --- SLA Helper Function ---
def calculate_sla(priority: str) -> datetime:
    now = datetime.utcnow()
    if priority == "Critical":
        return now + timedelta(hours=2)
    elif priority == "High":
        return now + timedelta(hours=4)
    elif priority == "Medium":
        return now + timedelta(hours=24)
    else:  # Low priority default
        return now + timedelta(hours=48)

# --- User Routes ---
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Ticket Routes ---
@app.post("/tickets/", response_model=schemas.TicketResponse)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    # Verify the user exists first
    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Calculate the SLA deadline
    sla_deadline = calculate_sla(ticket.priority)
    
    # Inject SLA deadline into the dictionary before saving to DB
    ticket_data = ticket.model_dump()
    db_ticket = models.Ticket(**ticket_data, sla_due_at=sla_deadline)
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@app.get("/tickets/", response_model=List[schemas.TicketResponse])
def read_all_tickets(db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).all()
    return tickets