from fastapi import Depends, Request
from typing import Annotated
from sqlalchemy.orm import Session

from . import exceptions, schemas, crud, auth
from .database import get_db

async def get_current_user(
        token: Annotated[str, Depends(auth.oauth2_scheme)], 
        db: Annotated[Session, Depends(get_db)]
) -> schemas.User:
    uname = auth.decode_jwt(token, auth.get_public_key())
    if not (user := crud.get_db_user_by_uname(db, uname)):
        exceptions.raise_unauthorized("User not found")
    return user

async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if current_user.disabled:
        exceptions.raise_bad_request("inactive user")
    return current_user

async def get_current_user_refresh(
        request: Request,
        db: Annotated[Session, Depends(get_db)]
) -> schemas.User:
    if not (refresh_token := request.cookies.get("refresh_token")):
        raise exceptions.raise_unauthorized("refresh token missing")
    uname = auth.decode_jwt(refresh_token, auth.get_public_key())
    if not (user := crud.get_db_user_by_uname(db, uname)):
        exceptions.raise_unauthorized("user not found")
    return user

async def get_current_active_user_refresh(
    current_user: Annotated[schemas.User, Depends(get_current_user_refresh)]
):
    if current_user.disabled:
        exceptions.raise_bad_request("inactive user")
    return current_user