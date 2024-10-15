from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from . import crud, models, schemas, utils
from .database import engine
from .utils import get_db


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/me")
def read_users_me(
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)]
) -> schemas.User:
    return current_user


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/events", response_model=schemas.Event)
def create_event(
    event: schemas.EventCreate,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):

    return crud.create_event(db=db, event=event, user_id=current_user.user_id)


@app.delete("/events/{event_uuid}", response_model=schemas.Event)
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


@app.get("/events", response_model=list[schemas.Event])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@app.get("/events/{event_uuid}", response_model=schemas.Event)
def read_event(event_uuid: str, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_uuid=event_uuid)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@app.get("/guests", response_model=list[schemas.Guest])
def read_guests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    guests = crud.get_guests(db, skip=skip, limit=limit)
    return guests


@app.get("/guests/{guest_uuid}", response_model=schemas.Guest)
def read_guest(guest_uuid: str, db: Session = Depends(get_db)):
    db_guest = crud.get_guest(db, guest_uuid=guest_uuid)
    if db_guest is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_guest


@app.get("/events/{event_uuid}/guests", response_model=list[schemas.Guest])
def read_guests_from_event(
    event_uuid: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_guests_from_event(db, event_uuid, skip=skip, limit=limit)


@app.post("/guests", response_model=schemas.Guest)
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


@app.post("/guests/{guest_uuid}/answer", response_model=schemas.Guest)
def update_answear(
    guest_uuid: str,
    guest_answer: schemas.GuestAnswear,
    db: Session = Depends(get_db),
):
    db_guest = crud.get_guest(db, guest_uuid)

    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    return crud.update_guest_answear(db, guest_uuid, guest_answer)


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> schemas.Token:
    user = utils.authenticate_user(form_data, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = utils.create_access_token(
        data={
            "sub": user.email,
            "user_id": user.user_id,
        },
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.post("/reset_tables")
def reset_tables(db: Session = Depends(get_db)):
    crud.reset_tables(db)
