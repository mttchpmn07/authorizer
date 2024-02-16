from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from . import schemas, crud, auth, exceptions
from .database import get_db
from .config import get_settings

router = APIRouter()

async def get_current_user(
        token: Annotated[str, Depends(auth.oauth2_scheme)], 
        db: Annotated[Session, Depends(get_db)]
) -> schemas.User:
    uname = auth.decode_jwt(token)
    if not (user := crud.get_db_user_by_uname(db, uname)):
        exceptions.raise_unauthorized("User not found")
    return user

async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if current_user.disabled:
        exceptions.raise_bad_request("Inactive user")
    return current_user

@router.get("/users/me")
async def read_users_me(current_user: Annotated[schemas.User, Depends(get_current_active_user)]):
    return current_user

@router.get("/items/")
async def read_items(token: Annotated[str, Depends(auth.oauth2_scheme)]):
    return {"token": token}

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> schemas.Token:
    if not (user := auth.authenticate_user(db, form_data.username, form_data.password)):
        exceptions.raise_unauthorized("Incorrect username or password")
    access_token_expires = timedelta(minutes=get_settings().access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.uname}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/register", response_model=schemas.User)
def register_user(
        userCreate: schemas.UserCreate, 
        db: Session = Depends(get_db)
):
    if crud.get_db_user_by_uname(db, userCreate.uname):
        exceptions.raise_bad_request(f"user already exists")
    userCreate.password = auth.get_password_hash(userCreate.password)
    if user := crud.create_db_user(db, userCreate):
        return user
    exceptions.raise_bad_request(f"error creating user")

@router.post("/disable", response_model=schemas.UserBase)
def disable_user(
        user: schemas.UserBase, 
        db: Session = Depends(get_db)
):
    if not (user := crud.get_db_user_by_uname(db, user.uname)):
        exceptions.raise_bad_request(f"user doesn't exists")
    if not (updated_user := crud.disable_db_user(db, user.uname)):
        exceptions.raise_server_error(f"failed to disable user")
    return updated_user

@router.post("/enable", response_model=schemas.UserBase)
def enable_user(
        user: schemas.UserBase, 
        db: Session = Depends(get_db)
):
    if not (user := crud.get_db_user_by_uname(db, user.uname)):
        exceptions.raise_bad_request(f"user doesn't exists")
    if not (updated_user := crud.enable_db_user(db, user.uname)):
        exceptions.raise_server_error(f"failed to disable user")
    return updated_user

@router.put("/update", response_model=schemas.User)
def update_user(userInfo: schemas.User, db: Session = Depends(get_db)):
    return f"TODO: update endpoint"

@router.post("/logout")
def logout_user(user: schemas.User, db: Session = Depends(get_db)):
    return f"TODO: logout endpoint"