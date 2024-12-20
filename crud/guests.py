from sqlalchemy.orm import Session

from .. import models, schemas, utils


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
    companion_uuid: str,
    companion_answer: schemas.CompanionAnswear,
):
    db_companion_guest = get_guest(db, companion_uuid)

    if companion_answer.name:
        db_companion_guest.name = companion_answer.name
        
    if companion_answer.surname:
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
