from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True)
    hashed_password = Column(String)

    events = relationship("Event", back_populates="organizer")


class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True)
    name = Column(String)
    start_time = Column(DateTime)
    location = Column(String)
    description = Column(String)
    menu = Column(String)
    decision_deadline = Column(DateTime)
    organizer_id = Column(Integer, ForeignKey("users.user_id"))

    organizer = relationship("User", back_populates="events")
    guests = relationship("Guest", back_populates="event")


class Guest(Base):
    __tablename__ = "guests"

    guest_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    name = Column(String)
    surname = Column(String)
    email = Column(String)
    phone = Column(String(20))
    answer = Column(Boolean)
    menu = Column(String)
    comments = Column(String)

    companion_id = Column(Integer, ForeignKey("guests.guest_id"))

    event = relationship("Event", back_populates="guests")
    # companion = relationship("Guest")
