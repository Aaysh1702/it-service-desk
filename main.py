from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

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

# --- User Routes ---
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Note: In a real app, we would hash the password here before saving!
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
        
    db_ticket = models.Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@app.get("/tickets/", response_model=List[schemas.TicketResponse])
def read_all_tickets(db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).all()
    return tickets