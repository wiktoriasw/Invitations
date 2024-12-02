from typing import Dict

from fastapi import HTTPException
from sqlalchemy import text, update
from sqlalchemy.orm import Session

from . import models, schemas, utils
from .configuration import settings
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


def change_password(db: Session, new_password: str, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    new_password_hashed = utils.get_password_hash(new_password)
    db_user.hashed_password = new_password_hashed
    db.commit()
    db.refresh(db_user)

    return db_user


def create_reset_password_token(db: Session, email: str):
    db_user = get_user_by_email(db, email)
    token = models.ForgotPassowordToken(user_id=db_user.user_id)
    db.add(token)
    db.commit()
    db.refresh(token)

    return token


def get_reset_password_token(db: Session, token: str):
    return (
        db.query(models.ForgotPassowordToken)
        .filter(models.ForgotPassowordToken.token == token)
        .first()
    )


def use_reset_password_token(db: Session, db_token):
    db.delete(db_token)
    db.commit()


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


def get_event_stats(db: Session, event_uuid: str):
    event_guests = get_guests_from_event(db, event_uuid)

    menu_answers: Dict[str, int] = {}

    answer_yes = 0
    answer_no = 0
    without_answer = 0

    for guest in event_guests:
        if guest.answer is True:
            answer_yes += 1
        elif guest.answer is False:
            answer_no += 1
        else:
            without_answer += 1

    for guest in event_guests:
        if guest.menu not in menu_answers:
            menu_answers[guest.menu] = 0

        menu_answers[guest.menu] += 1

    return {
        "sum_true": answer_yes,
        "sum_false": answer_no,
        "sum_unkown": without_answer,
        "menu_answers": menu_answers,
    }


def delete_event(db: Session, event_uuid: str):
    db_event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()

    db.delete(db_event)
    db.commit()

    return db_event


def modify_event(
    db: Session,
    event_uuid: str,
    event_modify: schemas.EventModify,
):

    db_event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()

    update_data = {
        k: v
        for k, v in event_modify.model_dump(exclude_unset=True).items()
        if v is not None
    }
    if update_data:
        db_event.update(update_data)
        db.commit()
    # db_event.name = event_modify.name
    # db_event.description = event_modify.description
    # db_event.start_time = event_modify.start_time
    # db_event.location = event_modify.location
    # db_event.menu = event_modify.menu
    # db_event.decision_deadline = event_modify.decision_deadline
    return db_event


def delete_guest_from_event(db: Session, guest_uuid: str):
    event_guest = get_guest(db, guest_uuid)
    db.delete(event_guest)
    db.commit()

    return event_guest


def delete_participants_from_event(db: Session, event_uuid: str):
    event_guests = get_guests_from_event(db, event_uuid)

    for guest in event_guests:
        db.delete(guest)

    db.commit()


def get_guest(db: Session, guest_uuid: str):
    return db.query(models.Guest).filter(models.Guest.uuid == guest_uuid).first()


def get_guest_by_id(db: Session, guest_id: int):
    return db.query(models.Guest).filter(models.Guest.guest_id == guest_id).first()


def get_guests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Guest).offset(skip).limit(limit).all()


def get_guests_from_event(db: Session, event_uuid: str):
    db_event = db.query(models.Event).filter(models.Event.uuid == event_uuid).first()
    return (
        db.query(models.Guest).filter(models.Guest.event_id == db_event.event_id).all()
    )


def create_event_guest(
    db: Session,
    guest: schemas.GuestCreate,
    event_id: int,
    companion_id: int | None = None,
):
    g = guest.model_dump()
    del g["event_uuid"]
    del g["has_companion"]

    g["event_id"] = event_id

    if companion_id:
        g["companion_id"] = companion_id

    db_guest = models.Guest(**g)
    db.add(db_guest)
    db.commit()
    db.refresh(db_guest)
    return db_guest


def update_guest_answear(
    db: Session,
    guest_uuid: str,
    guest_answer: schemas.GuestAnswear,
):
    db_guest = db.query(models.Guest).filter(models.Guest.uuid == guest_uuid).first()
    db_guest.answer = guest_answer.answer
    db_guest.menu = guest_answer.menu
    db_guest.comments = guest_answer.comments

    db.commit()
    db.refresh(db_guest)

    return db_guest


def update_companion_answer(
    db: Session,
    # guest_uuid: str,
    companion_uuid: str,
    companion_answer: schemas.CompanionAnswear,
):
    # db_primary_guest = get_primary_guest(db, guest_uuid)
    # db_companion_guest = get_guest(db_primary_guest.companion_id)
    db_companion_guest = get_guest(db, companion_uuid)

    db_companion_guest.name = companion_answer.name
    db_companion_guest.surname = companion_answer.surname

    db_companion_guest.answer = companion_answer.answer
    db_companion_guest.menu = companion_answer.menu
    db_companion_guest.comments = companion_answer.comments

    db.commit()
    db.refresh(db_companion_guest)

    return db_companion_guest


def get_primary_guest(db: Session, guest_id: int):
    db_primary_guest = (
        db.query(models.Guest).filter(models.Guest.companion_id == guest_id).first()
    )

    return db_primary_guest


def reset_tables(db: Session):
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
