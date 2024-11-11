from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from . import crud, models, schemas, utils
from .database import engine
from .routers import events, guests, users
from .utils import get_db, verify_password


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router)
app.include_router(events.router)
app.include_router(guests.router)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/change_password", response_model=schemas.UserBase)
def change_password(
    user_change_password: schemas.UserChangePassword,
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):
    db_user = crud.get_user_by_email(db, current_user.email)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_password(user_change_password.old_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Wrong password"
        )

    return crud.change_password(
        db=db,
        new_password=user_change_password.new_password,
        user_id=current_user.user_id,
    )


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
