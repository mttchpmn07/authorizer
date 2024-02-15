from sqlalchemy.orm import Session

from . import keygen, models, schemas

def create_db_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        uname=user.uname, 
        key=keygen.create_unique_random_key(db),
        password=user.password,
        disabled=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_db_user_by_key(db: Session, key: str) -> models.User:
    return (
        db.query(models.User)
        .filter(models.User.key == key)
        .first()
    )

def get_db_user_by_uname(db: Session, uname: str) -> models.User:
    return (
        db.query(models.User)
        .filter(models.User.uname == uname)
        .first()
    )

def disable_db_user(db: Session, key: str) -> models.User:
    if not (user_db := get_db_user_by_key(db, key)):
        return
    user_db.disabled = True
    db.commit()
    db.refresh(user_db)
    return user_db

def enable_db_user(db: Session, key: str) -> models.User:
    if not (user_db := get_db_user_by_key(db, key)):
        return
    user_db.disabled = False
    db.commit()
    db.refresh(user_db)
    return user_db