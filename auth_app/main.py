import validators
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.datastructures import URL
from datetime import datetime, timedelta, timezone

from . import models, schemas, crud, keygen
from .database import SessionLocal, engine
from .config import get_settings

app = FastAPI(title="Auth App")
models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)], 
        db: Annotated[Session, Depends(get_db)]) -> schemas.User:
    uname = keygen.decode_jwt(token)
    if not (user := crud.get_db_user_by_uname(db, uname)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/users/me")
async def read_users_me(current_user: Annotated[schemas.User, Depends(get_current_active_user)]):
    return current_user

def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

def raise_not_found(request):
    message = f"User '{request.URL}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> schemas.Token:
    if not (user := keygen.authenticate_user(db, form_data.username, form_data.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=keygen.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = keygen.create_access_token(
        data={"sub": user.uname}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

@app.post("/login", response_model=schemas.User)
def login_user(
        userInfo: schemas.UserAuth,
        db: Session = Depends(get_db)
    ):
    if user := crud.get_db_user_by_uname(db, userInfo.uname):
        if user.password == userInfo.password:
            return user
        message = f"wrong password"
        raise_bad_request(message)
    else:
        message = f"user '{userInfo.uname}' not found"
        raise_bad_request(message)

@app.post("/register", response_model=schemas.User)
def register_user(
        userCreate: schemas.UserCreate, 
        db: Session = Depends(get_db)
    ):
    if crud.get_db_user_by_uname(db, userCreate.uname):
        message = f"user already exists"
        raise_bad_request(message)
    userCreate.password = keygen.get_password_hash(userCreate.password)
    if user := crud.create_db_user(db, userCreate):
        return user
    message = f"error creating user"
    raise_bad_request(message)

@app.post("/disable", response_model=schemas.UserBase)
def disable_user(
        user: schemas.UserBase, 
        db: Session = Depends(get_db)
    ):
    if not (user := crud.get_db_user_by_uname(db, user.uname)):
        message = f"user doesn't exists"
        raise_bad_request(message)
    if not (updated_user := crud.disable_db_user(db, user.key)):
        message = f"failed to disable user"
        raise_bad_request(message)
    return updated_user

@app.post("/enable", response_model=schemas.UserBase)
def enable_user(
        user: schemas.UserBase, 
        db: Session = Depends(get_db)
    ):
    if not (user := crud.get_db_user_by_uname(db, user.uname)):
        message = f"user doesn't exists"
        raise_bad_request(message)
    if not (updated_user := crud.enable_db_user(db, user.key)):
        message = f"failed to disable user"
        raise_bad_request(message)
    return updated_user

@app.put("/update", response_model=schemas.User)
def update_user(userInfo: schemas.User, db: Session = Depends(get_db)):
    return f"TODO: update endpoint"

@app.post("/logout")
def logout_user(user: schemas.User, db: Session = Depends(get_db)):
    return f"TODO: logout endpoint"
