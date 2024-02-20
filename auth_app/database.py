from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

engine = create_engine(
    get_settings().db_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

engine_memory = create_engine('sqlite:///:memory:', connect_args={"check_same_thread": False})
SessionLocalMemory = sessionmaker(autocommit=False, autoflush=False, bind=engine_memory)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_token_db():
    db_memory = SessionLocalMemory()
    try:
        yield db_memory
    finally:
        db_memory.close()
