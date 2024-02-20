from fastapi import APIRouter, Depends, Response
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from . import schemas, crud, auth, exceptions

from .database import get_db
from .config import get_settings
from .utils import is_admin, get_current_user, get_current_active_user_refresh, validate_token

router = APIRouter()

@router.get("/pubkey")
async def get_pub_key():
    return {"public_key": auth.get_public_key()}

@router.post("/login")
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> schemas.Token:
    if not (user := auth.authenticate_user(db, form_data.username, form_data.password)):
        exceptions.raise_unauthorized("incorrect username or password")

    scopes = {"scopes": [scope.name for scope in user.scopes]}
    access_token_expires = timedelta(minutes=get_settings().access_token_expire_minutes)
    access_token = auth.create_access_token(
        scopes=scopes,
        data={"sub": user.uname},
        private_key=auth.get_private_key(),
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(hours=24)
    refresh_token = auth.create_refresh_token(
        data={"sub": user.uname}, private_key=auth.get_private_key(), expires_delta=refresh_token_expires
    )

    #TODO store refresh token in database

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite='Lax')    
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/token/refresh")
async def refresh_access_token(
    response: Response,
    current_user: Annotated[schemas.User, Depends(get_current_active_user_refresh)],
    db: Session = Depends(get_db)
) -> schemas.Token:
    
    user_authorized = True #TODO validate refresh token in database

    if not user_authorized:
        exceptions.raise_unauthorized("invalid refresh token")

    user = crud.get_db_user_by_uname(db=db, uname=current_user.uname)
        
    scopes = {"scopes": [scope.name for scope in user.scopes]}
    access_token_expires = timedelta(minutes=get_settings().access_token_expire_minutes)
    access_token = auth.create_access_token(
        scopes=scopes,
        data={"sub": user.uname},
        private_key=auth.get_private_key(),
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(hours=24)
    refresh_token = auth.create_refresh_token(
        data={"sub": user.uname},
        private_key=auth.get_private_key(),
        expires_delta=refresh_token_expires
    )

    #TODO replace old refresh token in databse

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite='Lax')    
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/logout")
def logout_user(
    user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #TODO: Need to remove the refresh token from the database

    return f"TODO: logout endpoint"

@router.get("/protected-endpoint")
def protected_endpoint(
    _ : Annotated[None, Depends(validate_token)]
):
    # Your endpoint logic here
    return {"message": "This is a protected endpoint"}

@router.get("/protected-admin-endpoint")
def protected_endpoint(
    _ = Depends(validate_token),
    admin = Depends(is_admin)
):
    # Your endpoint logic here
    return {"message": "This is an admin protected endpoint"}

@router.get("/manage/scopes")
def get_scopes(
    _ = Depends(is_admin())
):    
    #TODO: return list of scopes

    pass

@router.post("/manage/scopes/update")
def update_scope(
    _ = Depends(is_admin())
):    
    #TODO: update the provided scope

    pass

@router.post("/manage/scopes/create")
def update_scope(
    _ = Depends(is_admin())
):
    #TODO: create a new scope

    pass

@router.get("/manage/users")
def get_scopes(
    _ = Depends(is_admin())
):
    #TODO: return list of users

    pass

@router.post("/manage/users/update")
def update_scope(
    _ = Depends(is_admin())
):
    #TODO: update the provided user

    pass

@router.post("/manage/users/create", response_model=schemas.User)
def update_scope(
    userCreate: schemas.UserCreate,
    _ = Depends(is_admin()),
    db: Session = Depends(get_db)
):
    if crud.get_db_user_by_uname(db, userCreate.uname):
        exceptions.raise_bad_request(f"user already exists")
    
    userCreate.password = auth.get_password_hash(userCreate.password)

    if not (user := crud.create_db_user(db, userCreate)):
        exceptions.raise_bad_request(f"error creating user")
    
    return user