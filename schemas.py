from datetime import datetime

from pydantic import BaseModel, ConfigDict

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


class EventModify(BaseModel):
    name: str | None = None
    description: str | None = None
    start_time: datetime | None = None
    location: str | None = None
    menu: str | None = None
    decision_deadline: datetime | None = None


class Event(EventBase):
    event_id: int
    organizer_id: int
    uuid: str

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class GuestBase(BaseModel):
    name: str
    surname: str
    email: str
    phone: str


class GuestAnswear(BaseModel):
    answer: bool
    menu: str
    comments: str


class GuestCreate(GuestBase):
    event_uuid: str


class Guest(GuestBase):
    uuid: str
    answer: bool | None
    menu: str | None

    model_config = ConfigDict(from_attributes=True)
