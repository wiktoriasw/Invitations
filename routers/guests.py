from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas, utils
from ..utils import get_db

router = APIRouter(prefix="/guests")


@router.delete("/{guest_uuid}", response_model=schemas.Guest)
def delete_guest(
    guest_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):

    db_guest = crud.get_guest(db=db, guest_uuid=guest_uuid)

    if not db_guest or db_guest.event.organizer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Event not found")

    return crud.delete_guest_from_event(db, guest_uuid)


@router.get("", response_model=list[schemas.Guest])
def read_guests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    guests = crud.get_guests(db, skip=skip, limit=limit)
    return guests


@router.get("/{guest_uuid}", response_model=schemas.Guest)
def read_guest(guest_uuid: str, db: Session = Depends(get_db)):
    db_guest = crud.get_guest(db, guest_uuid=guest_uuid)
    if db_guest is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_guest


@router.post("", response_model=schemas.Guest)
def create_event_guest(
    guest: schemas.GuestCreate,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):
    event = crud.get_event(db, guest.event_uuid)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.user_id != event.organizer_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    companion_id = None
    if guest.has_companion:
        companion = schemas.GuestCreate(
            name="", surname="", email="", phone="", event_uuid=""
        )
        db_companion = crud.create_event_guest(db, companion, event.event_id)
        companion_id = db_companion.guest_id

    return crud.create_event_guest(db, guest, event.event_id, companion_id)


@router.post("/{guest_uuid}/answer", response_model=schemas.Guest)
def update_answear(
    guest_uuid: str,
    guest_answer: schemas.GuestAnswear,
    db: Session = Depends(get_db),
):
    db_guest = crud.get_guest(db, guest_uuid)

    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    if crud.get_primary_guest(db, db_guest.guest_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Companion cannot change their answers",
        )

    menu = db_guest.event.menu.split(";")
    if guest_answer.menu not in menu:
        raise HTTPException(status_code=400, detail="Menu not found")

    if db_guest.answer is False and db_guest.companion_id is not None:
        db_companion = crud.get_guest_by_id(db, db_guest.companion_id)
        companion_answer = schemas.GuestAnswear(answer=False, menu="", comments="")
        crud.update_guest_answear(db, db_companion.uuid, companion_answer)

    return crud.update_guest_answear(db, guest_uuid, guest_answer)


@router.post("/{companion_uuid}/companion_answer", response_model=schemas.Guest)
def update_comapnion_data(
    companion_uuid: str,
    companion_answer: schemas.CompanionAnswear,
    db: Session = Depends(get_db),
):
    db_companion = crud.get_guest(db, companion_uuid)

    if not db_companion:
        raise HTTPException(status_code=404, detail="Companion guest not found")

    menu = db_companion.event.menu.split(";")
    if companion_answer.menu not in menu:
        raise HTTPException(status_code=400, detail="Menu not found")

    db_guest = crud.get_primary_guest(db, db_companion.guest_id)
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
    return crud.update_companion_answer(db, companion_uuid, companion_answer)
