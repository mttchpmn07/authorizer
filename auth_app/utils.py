from fastapi import Depends
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
        exceptions.raise_bad_request("Inactive user")
    return current_user