from fastapi import FastAPI
from database import engine
import models

# tables in SQLite automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IT Service Desk API",
    description="ITIL-aligned ticketing system",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Service Desk API is running. Go to /docs for the UI."}