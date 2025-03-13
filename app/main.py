# event_management_api/main.py
from fastapi import FastAPI
from app.routes import users, events, event_participation

app = FastAPI(title="Event Management API")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(event_participation.router, prefix="/event-participation", tags=["Event Participation"])


@app.get("/health")
def health():
    return {"message": "Welcome to the Event Management API"}
