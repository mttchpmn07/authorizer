from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated
from sqlalchemy.orm import Session

from . import exceptions, schemas, crud, auth
from .database import get_db

async def validate_token(
        cred: Annotated[HTTPAuthorizationCredentials, Depends(auth.token_auth_scheme)]
):
    token = cred.credentials
    auth.validate_jwt(token, auth.get_public_key())

async def is_admin(
        cred: Annotated[HTTPAuthorizationCredentials, Depends(auth.token_auth_scheme)], 
):
    token = cred.credentials
    if not (payload := auth.decode_jwt(token, auth.get_public_key())):
        raise exceptions.raise_unauthorized("failed to decode access token")
    scopes: list = payload.get("scopes", [])
    # Here you would check if the required scope is in the token's scopes
    # For example, if an endpoint requires the 'admin' scope:
    if "admin" not in scopes:
        raise exceptions.raise_unauthorized("insufficient permissions")


async def get_current_user(
        cred: Annotated[HTTPAuthorizationCredentials, Depends(auth.token_auth_scheme)], 
        db: Annotated[Session, Depends(get_db)]
) -> schemas.User:
    token = cred.credentials
    if not (uname := auth.get_uname(token, auth.get_public_key())):
        raise exceptions.raise_unauthorized("failed to decode access token")
    if not (user := crud.get_db_user_by_uname(db, uname)):
        exceptions.raise_unauthorized("User not found")
    return user

async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if current_user.disabled:
        exceptions.raise_bad_request("inactive user")
    return current_user

async def get_refresh_token(
        request: Request
) -> str:
    if not (refresh_token := request.cookies.get("refresh_token")):
        raise exceptions.raise_unauthorized("failed to retrieve refresh token")
    return refresh_token

async def get_current_user_refresh(
        request: Request,
        db: Annotated[Session, Depends(get_db)],
) -> schemas.User:
    if not (refresh_token := request.cookies.get("refresh_token")):
        raise exceptions.raise_unauthorized("failed to retrieve refresh token")
    if not (uname := auth.get_uname(refresh_token, auth.get_public_key())):
        raise exceptions.raise_unauthorized("failed to decode refresh token")
    if not (user := crud.get_db_user_by_uname(db, uname)):
        exceptions.raise_unauthorized("user not found")
    return user

async def get_current_active_user_refresh(
    current_user: Annotated[schemas.User, Depends(get_current_user_refresh)]
):
    if current_user.disabled:
        exceptions.raise_bad_request("inactive user")
    return current_user