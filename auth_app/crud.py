from sqlalchemy.orm import Session

from . import models, schemas

def create_db_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        uname=user.uname, 
        password=user.password,
        disabled=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_db_user_by_uname(db: Session, uname: str) -> models.User:
    return (
        db.query(models.User)
        .filter(models.User.uname == uname)
        .first()
    )

def disable_db_user(db: Session, uname: str) -> models.User:
    if not (user_db := get_db_user_by_uname(db, uname)):
        return
    user_db.disabled = True
    db.commit()
    db.refresh(user_db)
    return user_db

def enable_db_user(db: Session, uname: str) -> models.User:
    if not (user_db := get_db_user_by_uname(db, uname)):
        return
    user_db.disabled = False
    db.commit()
    db.refresh(user_db)
    return user_db

def get_scopes_dict(db: Session) -> dict:
    scopes = db.query(models.Scope).all()
    scopes_dict = {scope.name: scope for scope in scopes}
    return scopes_dict

def add_refresh_token(db: Session, token: str) -> models.WhitelistedToken:
    db_token = models.WhitelistedToken(token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_refresh_token(db: Session, token: str) -> models.WhitelistedToken:
    return (
        db.query(models.WhitelistedToken)
        .filter(models.WhitelistedToken.token == token)
        .first()
    )

def remove_refresh_token(db: Session, token: str):
    db_token = (
        db.query(models.WhitelistedToken)
        .filter(models.WhitelistedToken.token == token)
        .first()
    )
    if not db_token:
        return
    db.delete(db_token)
    db.commit()