from typing import TYPE_CHECKING
import uuid
from sqlalchemy import String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from applytrack.db.base import Base

if TYPE_CHECKING:
    from .profile import Profile
    from .application import Application

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False)
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="user")
