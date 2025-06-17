"""User SQLAlchemy and Pydantic models."""
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from pydantic import BaseModel

Base = declarative_base()

class UserORM(Base):
    """SQLAlchemy ORM model for users table."""
    __tablename__ = "users"
    user: Mapped[str] = mapped_column(String(64), primary_key=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

class UserIn(BaseModel):
    """Pydantic model for user input."""
    user: str
    password: str

class UserOut(BaseModel):
    """Pydantic model for user output."""
    user: str
