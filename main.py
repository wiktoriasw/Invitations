from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from . import crud, models, schemas, utils
from .database import engine
from .utils import get_db
from .routers import events, guests, users


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




    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    db: Session = Depends(get_db),
):





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
