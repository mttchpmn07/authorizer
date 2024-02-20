from sqlalchemy import func
from sqlalchemy import ForeignKey, Table, Column, DateTime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped, DeclarativeBase, Session
from typing import List

from . import auth

class Base(DeclarativeBase):
    pass

scope_associations = Table(
    "scope_associations",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("scope_id", ForeignKey("scope.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    uname: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=True)
    password: Mapped[str] = mapped_column()
    disabled: Mapped[bool] = mapped_column(default=False)
    
    scopes: Mapped[List['Scope']] = relationship(
        secondary=scope_associations,
        back_populates="users"
    )

class Scope(Base):
    __tablename__ = "scope"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str] = mapped_column(nullable=True)

    users: Mapped[List['User']] = relationship(
        secondary=scope_associations,
        back_populates="scopes"
    )

def build_default_entries(db: Session):
    # Check and add scopes if they do not exist
    default_scope = db.query(Scope).filter(Scope.name == "default").first()
    if not default_scope:
        default_scope = Scope(name="default", description="Basic user actions")
        db.add(default_scope)
    
    admin_scope = db.query(Scope).filter(Scope.name == "admin").first()
    if not admin_scope:
        admin_scope = Scope(name="admin", description="Admin level actions")
        db.add(admin_scope)
    
    db.commit()  # Commit here to ensure scopes are persisted before associating them with users
    
    # Ensure default user does not exist before adding
    if not db.query(User).filter(User.uname == "default").first():
        user = User(uname="default", password=auth.get_password_hash("default"))
        user.scopes.append(default_scope)  # Append the existing or new default scope
        db.add(user)
    
    # Ensure admin user does not exist before adding
    if not db.query(User).filter(User.uname == "admin").first():
        first_admin = User(uname="admin", password=auth.get_password_hash("default_admin"))
        first_admin.scopes.append(default_scope)
        first_admin.scopes.append(admin_scope)  # Append the existing or new admin scope
        db.add(first_admin)
    
    db.commit()

class KeyValueBase(DeclarativeBase):
    pass

# Model for the key-value store
class WhitelistedToken(KeyValueBase):
    __tablename__ = "whitelisted_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
