from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity_access_management.models.role import Role


class RoleRepository:
    """Repositorio de roles baseado em SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, role: Role) -> Role:
        """Persiste uma role e executa flush das alteracoes pendentes."""
        self._session.add(role)
        self._session.flush()
        return role

    def find_by_name(self, name: str) -> Optional[Role]:
        """Carrega uma role por nome ou retorna `None` quando ausente."""
        statement = select(Role).where(Role.name == name)
        return self._session.scalar(statement)

    def list_all(self) -> list[Role]:
        """Retorna roles ordenadas alfabeticamente por nome."""
        statement = select(Role).order_by(Role.name.asc())
        return list(self._session.scalars(statement))
