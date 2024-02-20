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