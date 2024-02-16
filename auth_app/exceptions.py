from fastapi import Depends, FastAPI, HTTPException, status

def raise_bad_request(message):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )

def raise_user_not_found(uname: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User '{uname}' doesn't exist"
    )

def raise_unauthorized(message: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )

def raise_server_error(message: str):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=message
    )