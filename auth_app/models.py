from sqlalchemy import Boolean, Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    uname = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    disabled = Column(Boolean, default=False)
