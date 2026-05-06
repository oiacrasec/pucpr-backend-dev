from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.identity_access_management.models.user_role import user_roles_table

if TYPE_CHECKING:
    from app.modules.identity_access_management.models.role import Role


class User(Base):
    """Conta de usuario persistida com suas atribuicoes de roles."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(512), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    roles: Mapped[set["Role"]] = relationship(
        secondary=user_roles_table,
        back_populates="users",
        collection_class=set,
    )

    @property
    def is_admin(self) -> bool:
        """Indica se o usuario possui a role ADMIN no momento."""
        return any(role.name == "ADMIN" for role in self.roles)
