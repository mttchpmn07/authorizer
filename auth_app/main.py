from fastapi import FastAPI

from .router import router
from .database import engine, Base

app = FastAPI(title="Auth App")
Base.metadata.create_all(bind=engine)

app.include_router(router)