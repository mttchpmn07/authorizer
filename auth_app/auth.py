from jose import JWTError, ExpiredSignatureError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, SecurityScopes, OAuth2AuthorizationCodeBearer 
from typing import Union, Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from . import crud, exceptions
from .config import get_settings

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="token", tokenUrl="token", refreshUrl="token/refresh")
token_auth_scheme = HTTPBearer()
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

    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=get_settings().algorithm)
    return encoded_jwt

def create_refresh_token(data: dict, private_key, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()

    # Set a longer expiration for refresh tokens, e.g., 7 days
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    # For a refresh token, you might limit the data it contains. Typically, you might include a user identifier and nothing else.
    # It's common to remove other claims that are present in the access token to minimize the refresh token's scope of use.
    to_encode.update({"user_id": to_encode.get("user_id"), "exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=get_settings().algorithm)  # Adjust the algorithm as needed
    return encoded_jwt

def decode_jwt(token: str, public_key) -> Optional[str]:
    try:
        payload = jwt.decode(token, public_key, algorithms=[get_settings().algorithm])        
        if not (uname := payload.get("sub")):
            raise exceptions.raise_unauthorized("Could not validate credentials")
        print(payload.get("exp"))
        return uname
    except ExpiredSignatureError:
        raise exceptions.raise_unauthorized("Token has expired")
    except JWTError:
        raise exceptions.raise_unauthorized("Could not validate credentials")

def validate_jwt(token: str, public_key):
    try:
        jwt.decode(token, public_key, algorithms=[get_settings().algorithm])
    except ExpiredSignatureError:
        raise exceptions.raise_unauthorized("Token has expired")
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
    encoded_jwt = jwt.encode(to_encode, get_settings().secret_key, algorithm=get_settings().algorithm)
    return encoded_jwt

def decode_jwt(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[get_settings().algorithm])
        if not (uname := payload.get("sub")):
            raise exceptions.raise_unauthorized("Could not validate credentials")
        return uname
    except JWTError:
        raise exceptions.raise_unauthorized("Could not validate credentials")
"""