from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from typing import Union, Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from . import crud, exceptions
from .config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

def serialize_private_key(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def get_private_key():
    return serialize_private_key(private_key)

def get_public_key():
    return serialize_public_key(public_key)

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

def create_access_token(data: dict, private_key, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=get_settings().algorythm)
    return encoded_jwt

def decode_jwt(token: str, public_key) -> Optional[str]:
    try:
        payload = jwt.decode(token, public_key, algorithms=[get_settings().algorythm])
        if not (uname := payload.get("sub")):
            raise exceptions.raise_unauthorized("Could not validate credentials")
        return uname
    except JWTError:
        raise exceptions.raise_unauthorized("Could not validate credentials")
"""
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().secret_key, algorithm=get_settings().algorythm)
    return encoded_jwt

def decode_jwt(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[get_settings().algorythm])
        if not (uname := payload.get("sub")):
            raise exceptions.raise_unauthorized("Could not validate credentials")
        return uname
    except JWTError:
        raise exceptions.raise_unauthorized("Could not validate credentials")
"""