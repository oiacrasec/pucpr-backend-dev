from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.identity_access_management.models.user import User


class UserAvatar(Base):
    """Metadados do avatar ativo de um usuario."""

    __tablename__ = "user_avatars"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    storage_backend: Mapped[str] = mapped_column(String(20), nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="avatar")
