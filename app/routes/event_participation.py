from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db import get_db
from app.models import Event, EventAttendee, User
from app.services.auth import decode_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


# ------------------------
# 🔹 Join Event (Users Only)
# ------------------------
@router.post("/events/{event_id}/join")
def join_event(event_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows users to sign up for an event."""
    payload = decode_access_token(token)
    user = db.query(User).filter(User.username == payload.get("sub")).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user credentials")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if len(event.attendees) >= event.max_attendees:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is full")

    existing_registration = db.query(EventAttendee).filter_by(event_id=event_id, user_id=user.id).first()
    if existing_registration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered for this event")

    registration = EventAttendee(event_id=event_id, user_id=user.id)

    try:
        db.add(registration)
        db.commit()
        return {"message": "Successfully registered for the event"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Registration failed: {str(e)}")


# ------------------------
# 🔹 Leave Event (Users Only)
# ------------------------
@router.delete("/events/{event_id}/leave")
def leave_event(event_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows users to cancel their registration for an event."""
    payload = decode_access_token(token)
    user = db.query(User).filter(User.username == payload.get("sub")).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user credentials")

    registration = db.query(EventAttendee).filter_by(event_id=event_id, user_id=user.id).first()
    if not registration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not registered for this event")

    try:
        db.delete(registration)
        db.commit()
        return {"message": "Successfully unregistered from the event"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unregistration failed: {str(e)}")
