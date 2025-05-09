from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import utils
from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    uuid = Column(String, default=utils.get_uuid4)
    email = Column(String(50), unique=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

    events = relationship("Event", back_populates="organizer")


class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True)
    uuid = Column(String, default=utils.get_uuid4)
    name = Column(String)
    is_public = Column(Boolean)
    start_time = Column(DateTime)
    location = Column(String)
    description = Column(String)
    menu = Column(String)
    decision_deadline = Column(DateTime)
    organizer_id = Column(Integer, ForeignKey("users.user_id"))
    background_photo = Column(String)

    organizer = relationship("User", back_populates="events")
    guests = relationship("Guest", back_populates="event")


class Guest(Base):
    __tablename__ = "guests"

    guest_id = Column(Integer, primary_key=True)
    uuid = Column(String, default=utils.get_uuid4)
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


class ForgotPassowordToken(Base):
    __tablename__ = "forgot_password_token"

    user_id = Column(Integer, ForeignKey("users.user_id"))
    token = Column(String, primary_key=True, unique=True, default=utils.get_uuid4)
    expire_time = Column(DateTime, default=utils.get_default_expire_date)

    user = relationship("User")
