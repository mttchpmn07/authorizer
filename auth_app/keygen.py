import secrets
import string

from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from typing import Union, Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import crud

SECRET_KEY = "b1358619ed784f3e2672e1bef403cc28dfba8b20ba7aceb1c5cd7417916939bd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, uname: str, password: str):
    if not (user := crud.get_db_user_by_uname(db, uname)):
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_random_key(length: int = 15) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

def create_unique_random_key(db: Session) -> str:
    key = create_random_key()
    while crud.get_db_user_by_key(db, key):
        key = create_random_key()
    return key

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt(token: str) -> Optional[str]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uname: str = payload.get("sub")
        if uname is None:
            raise credentials_exception
        return uname
    except JWTError:
        raise credentials_exception