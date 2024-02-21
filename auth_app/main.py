from fastapi import FastAPI
from contextlib import asynccontextmanager

from .router import router
from .database import engine, engine_memory
from .database import get_db
from .models import Base, KeyValueBase
from .models import build_default_entries

# Function to initialize main database
def init_main_db():
    Base.metadata.create_all(bind=engine)
    build_default_entries(next(get_db()))
    # If you have initial data to load, do it here

# Function to initialize in-memory database
def init_memory_db():
    KeyValueBase.metadata.create_all(bind=engine_memory)
    # If you have initial data to load, do it here

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_main_db()
    init_memory_db()
    yield
    pass

app = FastAPI(title="Auth App", lifespan=lifespan)

#Base.metadata.create_all(bind=engine)
#build_default_entries(next(get_db()))

# Create the tables in the in-memory database
#KeyValueBase.metadata.create_all(bind=engine_memory)

app.include_router(router)