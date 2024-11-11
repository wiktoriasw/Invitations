from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
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

    return crud.create_event_guest(db=db, guest=guest, event_id=event.event_id)


@router.post("/{guest_uuid}/answer", response_model=schemas.Guest)
def update_answear(
    guest_uuid: str,
    guest_answer: schemas.GuestAnswear,
    db: Session = Depends(get_db),
):
    db_guest = crud.get_guest(db, guest_uuid)

    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    menu = db_guest.event.menu.split(";")
    if guest_answer.menu not in menu:
        raise HTTPException(status_code=400, detail="Menu not found")

    return crud.update_guest_answear(db, guest_uuid, guest_answer)
