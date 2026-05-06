from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.identity_access_management.models.user_role import user_roles_table

if TYPE_CHECKING:
    from app.modules.identity_access_management.models.user import User


class Role(Base):
    """Role de autorizacao persistida."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    users: Mapped[set["User"]] = relationship(
        secondary=user_roles_table,
        back_populates="roles",
        collection_class=set,
    )
