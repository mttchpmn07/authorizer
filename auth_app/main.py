from fastapi import FastAPI

from .router import router
from .database import engine, engine_memory
from .database import get_db
from .models import Base, KeyValueBase
from .models import build_default_entries

app = FastAPI(title="Auth App")

Base.metadata.create_all(bind=engine)
build_default_entries(next(get_db()))

# Create the tables in the in-memory database
KeyValueBase.metadata.create_all(bind=engine_memory)

app.include_router(router)