from fastapi import HTTPException
from sqlalchemy import text, update
from sqlalchemy.orm import Session

from . import models, schemas, utils
from .database import engine


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_event(db: Session, event_uuid: str):
    return db.query(models.Event).filter(models.Event.uuid == event_uuid).first()


def get_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Event).offset(skip).limit(limit).all()


def create_event(db: Session, event: schemas.EventCreate, user_id: int):
    db_event = models.Event(**event.model_dump())
    db_event.organizer_id = user_id
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_uuid: str):
    db_event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()

    db.delete(db_event)
    db.commit()

    return db_event


def delete_participants_from_event(
    db: Session, event_uuid: str, skip: int = 0, limit: int = 100
):
    event_guests = get_guests_from_event(db, event_uuid, skip=skip, limit=limit)

    for guest in event_guests:
        db.delete(guest)

    db.commit()


def get_guest(db: Session, guest_uuid: str):
    return db.query(models.Guest).filter(models.Guest.uuid == guest_uuid).first()


def get_guests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Guest).offset(skip).limit(limit).all()


def get_guests_from_event(
    db: Session, event_uuid: str, skip: int = 0, limit: int = 100
):
    db_event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()
    return (
        db.query(models.Guest)
        .filter(models.Guest.event_id == db_event.event_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_event_guest(db: Session, guest: schemas.GuestCreate, event_id: int):
    g = guest.model_dump()
    del g["event_uuid"]
    g["event_id"] = event_id

    db_guest = models.Guest(**g)
    db.add(db_guest)
    db.commit()
    db.refresh(db_guest)
    return db_guest


def update_guest_answear(
    db: Session, guest_uuid: str, guest_answer: schemas.GuestAnswear
):
    db_guest = db.query(models.Guest).filter(models.Guest.uuid == guest_uuid).first()
    db_guest.answer = guest_answer.answer

    db.commit()
    db.refresh(db_guest)

    return db_guest


def reset_tables(db: Session):
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
