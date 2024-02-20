from fastapi import FastAPI

from .router import router
from .database import engine, get_db
from .models import Base, build_default_entries

app = FastAPI(title="Auth App")

Base.metadata.create_all(bind=engine)
build_default_entries(next(get_db()))

app.include_router(router)