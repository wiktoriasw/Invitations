from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..database import engine


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_uuid(db: Session, user_uuid: str):
    return db.query(models.User).filter(models.User.uuid == user_uuid).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    db.delete(db_user)
    db.commit()

    return db_user


def change_user_role(db: Session, role: str, email: str):
    db_user = get_user_by_email(db, email)
    db_user.role = role
    db.commit()
    db.refresh(db_user)

    return db_user


def change_role_by_user_uuid(
    db: Session, user_change_role: schemas.UserChangeRole, uuid: str
):
    db_user = get_user_by_uuid(db, uuid)
    db_user.role = user_change_role.role
    db.commit()
    db.refresh(db_user)

    return db_user


def change_password(db: Session, new_password: str, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    new_password_hashed = utils.get_password_hash(new_password)
    db_user.hashed_password = new_password_hashed
    db.commit()
    db.refresh(db_user)

    return db_user


def create_reset_password_token(db: Session, email: str):
    db_user = get_user_by_email(db, email)
    token = models.ForgotPassowordToken(user_id=db_user.user_id)
    db.add(token)
    db.commit()
    db.refresh(token)

    return token


def get_reset_password_token(db: Session, token: str):
    return (
        db.query(models.ForgotPassowordToken)
        .filter(models.ForgotPassowordToken.token == token)
        .first()
    )


def use_reset_password_token(db: Session, db_token):
    db.delete(db_token)
    db.commit()


def reset_tables(db: Session):
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
