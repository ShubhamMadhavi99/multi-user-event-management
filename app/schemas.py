from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, timezone
import re

# ------------------------------
# 🔹 User Schemas
# ------------------------------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(admin|masteradmin|organizer|attendee)$")  # Added masteradmin role

    @validator("username")
    def validate_username(cls, value):
        if " " in value:
            raise ValueError("Username cannot contain spaces.")
        return value
    
    @validator("password")
    def validate_password(cls, value):
        # Check for complexity requirements
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):  # Special characters
            raise ValueError("Password must contain at least one special character.")
        return value


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True  # Ensures compatibility with SQLAlchemy ORM


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


# ------------------------------
# 🔹 Event Schemas
# ------------------------------
class EventCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    location: str = Field(..., min_length=3, max_length=200)
    date: datetime
    status: str = Field(default="Scheduled", pattern="^(Scheduled|Ongoing|Completed|Cancelled)$")
    max_attendees: Optional[int] = Field(None, gt=0)

    @validator("date")
    def validate_date(cls, value):
        # Ensure 'value' is timezone-aware
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("Event date must be timezone-aware (use UTC).")

        # Compare with UTC now, making sure both are aware
        if value < datetime.now(timezone.utc):
            raise ValueError("Event date must be in the future.")

        return value
    
    class Config:
        orm_mode = True


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, min_length=3, max_length=200)
    date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(Scheduled|Ongoing|Completed|Cancelled)$")

    @validator("date")
    def validate_date(cls, value):
        # Ensure 'value' is timezone-aware
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("Event date must be timezone-aware (use UTC).")

        # Compare with UTC now, making sure both are aware
        if value < datetime.now(timezone.utc):
            raise ValueError("Event date must be in the future.")

        return value


class EventAttendeeResponse(BaseModel):
    user_id: int  # Ensure only user_id is returned

    class Config:
        orm_mode = True


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    location: str
    date: datetime
    status: str
    organizer_id: int
    max_attendees: Optional[int]
    attendees: List[EventAttendeeResponse] = []  # List of user IDs attending the event

    class Config:
        from_attributes = True  # Ensures compatibility with SQLAlchemy ORM


# ------------------------------
# 🔹 Event Attendee Schema
# ------------------------------
class EventAttendee(BaseModel):
    event_id: int
    user_id: int
