from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import subprocess
import platform
import socket

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

# SLA Helper Function
def calculate_sla(priority: str) -> datetime:
    now = datetime.utcnow()
    if priority == "Critical":
        return now + timedelta(hours=2)
    elif priority == "High":
        return now + timedelta(hours=4)
    elif priority == "Medium":
        return now + timedelta(hours=24)
    else:  
        return now + timedelta(hours=48)

# Automated Troubleshooting Diagnostics 
def run_network_diagnostics() -> str:
    # 1. Ping Check (Google's DNS server)
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '8.8.8.8']
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        ping_result = "SUCCESS (8.8.8.8 is reachable)"
    except subprocess.CalledProcessError:
        ping_result = "FAILED (Network unreachable)"

    # DNS Resolution Check
    try:
        ip = socket.gethostbyname("google.com")
        dns_result = f"SUCCESS (google.com resolves to {ip})"
    except socket.error:
        dns_result = "FAILED (DNS resolution error)"

    
    return f"\n\n--- Automated Diagnostics ---\nPing Check: {ping_result}\nDNS Check: {dns_result}\n-----------------------------"

# User Routes 
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

# Ticket Routes
@app.post("/tickets/", response_model=schemas.TicketResponse)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    sla_deadline = calculate_sla(ticket.priority)
    ticket_data = ticket.model_dump()
    
    # Run diagnostics if it's a network issue
    if ticket_data.get("category", "").lower() == "network":
        diagnostic_log = run_network_diagnostics()
        ticket_data["description"] += diagnostic_log  
        
    db_ticket = models.Ticket(**ticket_data, sla_due_at=sla_deadline)
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@app.get("/tickets/", response_model=List[schemas.TicketResponse])
def read_all_tickets(db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).all()
    return tickets

@app.put("/tickets/{ticket_id}", response_model=schemas.TicketResponse)
def update_ticket(ticket_id: int, ticket_update: schemas.TicketUpdate, db: Session = Depends(get_db)):
    # existing ticket
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update the status
    db_ticket.status = ticket_update.status
    
    if ticket_update.assigned_to_id is not None:
        db_ticket.assigned_to_id = ticket_update.assigned_to_id
        
    db.commit()
    db.refresh(db_ticket)
    return db_ticket