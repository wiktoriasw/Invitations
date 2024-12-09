from typing import Dict

from sqlalchemy.orm import Session

from .. import models, schemas, utils
from . import guests


def get_event(db: Session, event_uuid: str):
    return db.query(models.Event).filter(models.Event.uuid == event_uuid).first()


def get_event_by_id(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.event_id == event_id).first()


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
    event_guests = guests.get_guests_from_event(db, event_uuid)

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
        for key, value in update_data.items():
            setattr(db_event, key, value)
        db.commit()

    return db_event
