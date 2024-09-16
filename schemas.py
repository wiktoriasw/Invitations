from pydantic import BaseModel
from datetime import datetime

## NIEDZ 15.09

class EventBase(BaseModel):
    name: str
    description: str | None = None
    start_time: datetime
    location: str
    menu: str
    decision_deadline: datetime
    organizer_id: int


class EventCreate(EventBase):
    pass

class Event(EventBase):
    event_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_id: int
    events: list[Event] = []

    class Config:
        orm_mode = True


class GuestBase(BaseModel):
    guest_id: int
    event_id: int
    name: str 
    surname: str 
    email: str
    phone: str
    answer: bool
    menu: str
    comments: str


class GuestCreate(GuestBase):
    pass


class Guest(GuestBase):
    guest_id: int

    class Config:
        orm_mode = True