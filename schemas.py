from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    name: str
    is_public: bool
    description: str | None = None
    start_time: datetime
    location: str
    menu: str
    decision_deadline: datetime
    background_photo: str | None = None


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


class UserChangeRole(BaseModel):
    role: str


class User(UserBase):
    user_id: int
    events: list[Event] = []
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str


class GuestBase(BaseModel):
    name: str
    surname: str
    email: str
    phone: str


class GuestAnswear(BaseModel):
    answer: bool
    menu: str | None = None
    comments: str | None = None


class GuestAnswearResponse(BaseModel):
    companion_uuid: str | None


class CompanionAnswear(GuestAnswear):
    name: str | None = None
    surname: str | None = None


class GuestCreate(GuestBase):
    event_uuid: str
    has_companion: bool = False


class Guest(GuestBase):
    uuid: str
    answer: bool | None
    menu: str | None

    model_config = ConfigDict(from_attributes=True)


class ForgetPasswordRequest(BaseModel):
    email: str


class ResetPasswordToken(BaseModel):
    token: str
    new_password: str
