from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

# ------------------------------
# 🔹 User Model
# ------------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    organized_events = relationship("Event", back_populates="organizer")
    attending_events = relationship("EventAttendee", back_populates="attendee")


# ------------------------------
# 🔹 Event Model
# ------------------------------
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(String, default="Scheduled")
    organizer_id = Column(Integer, ForeignKey("users.id"))
    max_attendees = Column(Integer, nullable=True) 

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organizer = relationship("User", back_populates="organized_events")
    attendees = relationship("EventAttendee", back_populates="event", lazy="joined")


# ------------------------------
# 🔹 EventAttendee Model (Tracks Event Registrations)
# ------------------------------
class EventAttendee(Base):
    __tablename__ = "event_attendees"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="attendees")
    attendee = relationship("User", back_populates="attending_events")

    # Ensure a user cannot register for the same event twice
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="unique_event_user"),)
