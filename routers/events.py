from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, utils
from ..utils import get_db

router = APIRouter(prefix="/events")


@router.post("", response_model=schemas.Event)
def create_event(
    event: schemas.EventCreate,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):

    return crud.create_event(db=db, event=event, user_id=current_user.user_id)


@router.put("", response_model=schemas.Event)
def modify_event(
    event_modify: schemas.EventModify,
    event_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):

    db_event = crud.get_event(db, event_uuid)
    if not db_event or db_event.organizer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Event not found")

    return crud.modify_event(db=db, event_uuid=event_uuid, event_modify=event_modify)


@router.delete("/{event_uuid}", response_model=schemas.Event)
def delete_event(
    event_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):

    db_event = crud.get_event(db, event_uuid)
    if not db_event or db_event.organizer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Event not found")

    crud.delete_participants_from_event(db, event_uuid, skip=skip, limit=limit)

    return crud.delete_event(db, event_uuid)


@router.get("", response_model=list[schemas.Event])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@router.get("/{event_uuid}", response_model=schemas.Event)
def read_event(event_uuid: str, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_uuid=event_uuid)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@router.get("/{event_uuid}/guests", response_model=list[schemas.Guest])
def read_guests_from_event(
    event_uuid: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_guests_from_event(db, event_uuid, skip=skip, limit=limit)