from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.db import get_db
from app.models import Event, EventAttendee, User
from app.schemas import EventCreate, EventUpdate, EventResponse, EventAttendeeResponse
from app.services.auth import decode_access_token
from typing import List
import os
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Load Master Admin Credentials
MASTER_ADMIN_USERNAME = os.getenv("MASTER_ADMIN_USERNAME", "masteradmin")


def is_admin_or_master_admin(user: User):
    """Checks if the user is an Admin or Master Admin."""
    if not user or (user.role.lower() != "admin" and user.username != MASTER_ADMIN_USERNAME):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Admins only."
        )


# ------------------------
# 🔹 Create an Event (Organizers Only)
# ------------------------
@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows event organizers to create events."""
    payload = decode_access_token(token)
    user = db.query(User).filter(User.username == payload.get("sub")).first()

    if not user or user.role.lower() != "organizer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only event organizers can create events.")

    new_event = Event(**event.dict(), organizer_id=user.id)

    try:
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return new_event
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    

# ------------------------
# 🔹 Update Event (Admins, Master Admin & Organizers)
# ------------------------
@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows event organizers, Admins, and Master Admin to update events."""
    payload = decode_access_token(token)
    user = db.query(User).filter(User.username == payload.get("sub")).first()

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Only Admins, Master Admin, or the event's creator can update
    if user.id != event.organizer_id:
        is_admin_or_master_admin(user)

    for field, value in event_update.dict(exclude_unset=True).items():
        setattr(event, field, value)

    try:
        db.commit()
        db.refresh(event)
        return event
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Update failed: {str(e)}")


# ------------------------
# 🔹 Delete Event (Admins, Master Admin & Organizers)
# ------------------------
@router.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows event organizers, Admins, and Master Admin to delete events."""
    payload = decode_access_token(token)
    user = db.query(User).filter(User.username == payload.get("sub")).first()

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Only Admins, Master Admin, or the event's creator can delete
    if user.id != event.organizer_id:
        is_admin_or_master_admin(user)

    try:
        db.delete(event)
        db.commit()
        return {"message": "Event deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Deletion failed: {str(e)}")



# ------------------------
# 🔹 Get All Events (Anyone)
# ------------------------
@router.get("/events", response_model=List[EventResponse])
def list_events(db: Session = Depends(get_db)):
    """Fetch all events with proper structure."""
    try:
        events = db.query(Event).all()

        event_responses = []
        for event in events:
            event_responses.append(EventResponse(
                id=event.id,
                title=event.title,
                description=event.description,
                location=event.location,
                date=event.date,
                status=event.status,
                organizer_id=event.organizer_id,
                max_attendees=event.max_attendees,
                attendees=[EventAttendeeResponse(user_id=att.user_id) for att in event.attendees]
            ))

        return event_responses

    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching events: {str(e)}")

# ------------------------
# 🔹 Get Event by ID (Anyone)
# ------------------------
@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Fetch a specific event with all required fields."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        location=event.location,
        date=event.date,
        status=event.status,
        organizer_id=event.organizer_id,
        max_attendees=event.max_attendees,
        attendees=[EventAttendeeResponse(user_id=att.user_id) for att in event.attendees]
    )