from pydantic import BaseModel
from typing import Annotated, Union

class UserBase(BaseModel):
    uname: str

class UserCreate(UserBase):
    password: str

class UserAuth(UserBase):
    password: str

class User(UserBase):
    key: str
    email: Union[str, None] = None
    disabled: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None