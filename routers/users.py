from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..crud import events, guests, users
from ..utils import get_db

router = APIRouter(prefix="/users")


@router.post("", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = users.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return users.create_user(db=db, user=user)


@router.get("", response_model=list[schemas.User])
def read_users(
    _: Annotated[schemas.User, Depends(utils.get_admin_user)],
    db: Session = Depends(get_db),
):

    db_users = users.get_users(db)
    return db_users


@router.get("/me")
def read_users_me(
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)]
) -> schemas.User:
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    _: Annotated[schemas.User, Depends(utils.get_admin_user)],
    user_id: int,
    db: Session = Depends(get_db),
):
    db_user = users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/{user_uuid}/role")
def change_role(
    current_user: Annotated[schemas.User, Depends(utils.get_admin_user)],
    user_uuid: str,
    role: schemas.UserChangeRole,
    db: Session = Depends(get_db),
):
    if current_user.uuid == user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin can't change their own role",
        )

    users.change_role_by_user_uuid(db, role, user_uuid)


@router.delete("/{user_uuid}")
def delete_user(
    current_user: Annotated[schemas.User, Depends(utils.get_current_user)],
    user_uuid: str,
    db: Session = Depends(get_db),
):
    db_user = users.get_user_by_uuid(db, user_uuid)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != "admin" and current_user.user_id != db_user.user_id:
        raise HTTPException(status_code=401, detail="You don't have permission")
    
    if current_user.role == "admin" and current_user.user_id == db_user.user_id:
        raise HTTPException(status_code=401, detail="Admin can't remove theirselves")

    db_events = events.get_event_by_organizer(db, db_user.user_id)

    for event in db_events:
        events.delete_event(db, event.uuid)

    users.delete_user(db, db_user.user_id)

    return {
        "detail": f"User <{user_uuid}> and their events have been deleted successfully"
    }
