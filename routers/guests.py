from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..crud import events, guests, users
from ..utils import get_db

router = APIRouter(prefix="/guests")


@router.delete("/{guest_uuid}", response_model=schemas.Guest)
def delete_guest(
    guest_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):

    db_guest = guests.get_guest(db=db, guest_uuid=guest_uuid)

    if not db_guest or db_guest.event.organizer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Event not found")

    return guests.delete_guest_from_event(db, guest_uuid)


@router.get("", response_model=list[schemas.Guest])
def read_guests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_guests = guests.get_guests(db, skip=skip, limit=limit)
    return db_guests


@router.get("/{guest_uuid}", response_model=schemas.Guest)
def read_guest(guest_uuid: str, db: Session = Depends(get_db)):
    db_guest = guests.get_guest(db, guest_uuid=guest_uuid)
    if db_guest is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_guest


@router.post("", response_model=schemas.Guest)
def create_event_guest(
    guest: schemas.GuestCreate,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):
    event = events.get_event(db, guest.event_uuid)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.user_id != event.organizer_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    companion_id = None
    if guest.has_companion:
        companion = schemas.GuestCreate(
            name="", surname="", email="", phone="", event_uuid=""
        )
        db_companion = guests.create_event_guest(db, companion, event.event_id)
        companion_id = db_companion.guest_id

    return guests.create_event_guest(db, guest, event.event_id, companion_id)


@router.post("/{guest_uuid}/answer", response_model=schemas.Guest)
def update_answear(
    guest_uuid: str,
    guest_answer: schemas.GuestAnswear,
    db: Session = Depends(get_db),
):
    db_guest = guests.get_guest(db, guest_uuid)

    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    if guests.get_primary_guest(db, db_guest.guest_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Companion cannot change their answers",
        )
    if db_guest.event.decision_deadline < datetime.now():
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE,
            detail="After the deadline you cannot update your answer",
        )
    
    if guest_answer.answer is False:
        guest_answer.menu = None
    else:
        menu = db_guest.event.menu.split(";")
        if guest_answer.menu not in menu:
            raise HTTPException(status_code=400, detail="Menu not found")

    if db_guest.answer is False and db_guest.companion_id is not None:
        db_companion = guests.get_guest_by_id(db, db_guest.companion_id)
        companion_answer = schemas.GuestAnswear(answer=False, menu="", comments="")
        guests.update_guest_answear(db, db_companion.uuid, companion_answer)

    return guests.update_guest_answear(db, guest_uuid, guest_answer)


@router.post("/{companion_uuid}/companion_answer", response_model=schemas.Guest)
def update_comapnion_data(
    companion_uuid: str,
    companion_answer: schemas.CompanionAnswear,
    db: Session = Depends(get_db),
):
    if companion_answer.answer:
        if companion_answer.name is None or companion_answer.surname is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, 'You need to provide name and surname')

    db_companion = guests.get_guest(db, companion_uuid)

    if not db_companion:
        raise HTTPException(status_code=404, detail="Companion guest not found")

    db_guest = guests.get_primary_guest(db, db_companion.guest_id)
    if db_guest.answer is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Primary guest has to answer first",
        )

    if db_guest.answer is False:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You cannot participate without primary guest",
        )

    if db_guest.event.decision_deadline < datetime.now():
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE,
            detail="After the deadline you cannot update companion answer",
        )
    if companion_answer.answer is False:
        companion_answer.menu = None
    else:
        menu = db_companion.event.menu.split(";")
        if companion_answer.menu not in menu:
            raise HTTPException(status_code=400, detail="Menu not found")

    return guests.update_companion_answer(db, companion_uuid, companion_answer)
