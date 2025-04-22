import os.path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.orm import Session

from .. import schemas, utils
from ..crud import events, guests
from ..utils import get_db

router = APIRouter(prefix="/events")


@router.post("", response_model=schemas.Event)
def create_event(
    event: schemas.EventCreate,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):

    return events.create_event(db=db, event=event, user_id=current_user.user_id)


@router.put("/{event_uuid}", response_model=schemas.Event)
def modify_event(
    event_modify: schemas.EventModify,
    event_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):

    db_event = events.get_event(db, event_uuid)
    if not db_event or db_event.organizer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Event not found")

    return events.modify_event(db=db, event_uuid=event_uuid, event_modify=event_modify)


@router.delete("/{event_uuid}", response_model=schemas.Event)
def delete_event(
    event_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):

    db_event = events.get_event(db, event_uuid)
    if not db_event or db_event.organizer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Event not found")

    guests.delete_participants_from_event(db, event_uuid)

    return events.delete_event(db, event_uuid)


@router.get("/public", response_model=list[schemas.Event])
def read_public_events(db: Session = Depends(get_db)):
    db_events = events.get_public_events(db)

    return db_events


@router.get("", response_model=list[schemas.Event])
def read_events(
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        db_events = events.get_event_by_organizer(db, current_user.user_id)
    else:
        db_events = events.get_events(db)

    return db_events


@router.get("/{event_uuid}", response_model=schemas.Event)
def read_event(event_uuid: str, db: Session = Depends(get_db)):
    db_event = events.get_event(db, event_uuid=event_uuid)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@router.get("/{event_uuid}/guests", response_model=list[schemas.Guest])
def read_guests_from_event(
    event_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):
    db_event = events.get_event(db, event_uuid)
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    if db_event.organizer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not an owner of this event",
        )

    return guests.get_guests_from_event(db, event_uuid)


@router.get("/{event_uuid}/stats")
def read_event_stats(
    event_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):

    db_event = events.get_event(db, event_uuid)
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    if db_event.organizer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not an owner of this event",
        )

    return events.get_event_stats(db, event_uuid)


@router.post("/{event_uuid}/background")
def upload_background(
    event_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    file: UploadFile,
    db: Session = Depends(get_db),
):
    db_event = events.get_event(db, event_uuid)
    if not db_event or db_event.organizer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Event not found")

    if file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE, detail="The file is bigger than 10 MB"
        )

    if file.content_type not in ["image/webp", "image/png", "image/jpeg"]:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE, detail="The file should be webp, png or jpg"
        )

    image = Image.open(file.file)

    width, height = image.size

    if width < 300 or height < 300:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE,
            detail="Image should be bigger than (300,300)",
        )

    file_extension = file.content_type[6:]

    background_path = "./backgrounds"
    if not os.path.isdir(background_path):
        os.mkdir(background_path)

    image.save(os.path.join(background_path, f"{event_uuid}.{file_extension}"))

    events.add_background(db, event_uuid, file_extension)

    return {
        "filename": file.filename,
        "size": file.size,
        "content_type": file.content_type,
    }


@router.delete("/{event_uuid}/background")
def delete_background(
    event_uuid: str,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):
    db_event = events.get_event(db, event_uuid)
    if not db_event or db_event.organizer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Event not found")

    file_extension = db_event.background_photo
    if not file_extension:
        raise HTTPException(
            status_code=404, detail="The event does not have a background photo"
        )

    background_path = "./backgrounds"
    file_path = os.path.join(background_path, f"{event_uuid}.{file_extension}")

    if os.path.exists(file_path):
        os.remove(file_path)

    events.delete_background(db, event_uuid)

    return {"detail": "Background deleted successfully"}
