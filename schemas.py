from datetime import datetime

from pydantic import BaseModel

## NIEDZ 15.09


class EventBase(BaseModel):
    name: str
    description: str | None = None
    start_time: datetime
    location: str
    menu: str
    decision_deadline: datetime


class EventCreate(EventBase):
    pass


class Event(EventBase):
    event_id: int
    organizer_id: int
    uuid: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_id: int
    events: list[Event] = []

    class Config:
        from_attributes = True


class GuestBase(BaseModel):
    name: str
    surname: str
    email: str
    phone: str


class GuestAnswear(BaseModel):
    answer: bool


class GuestCreate(GuestBase):
    event_uuid: str


class Guest(GuestBase):
    uuid: str
    answer: bool | None

    class Config:
        from_attributes = True
