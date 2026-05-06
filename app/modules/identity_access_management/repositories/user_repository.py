from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.identity_access_management.domain.sort_direction import SortDirection
from app.modules.identity_access_management.models.role import Role
from app.modules.identity_access_management.models.user import User


class UserRepository:
    """Repositorio de usuarios baseado em SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        """Persiste um usuario e executa flush das alteracoes pendentes."""
        self._session.add(user)
        self._session.flush()
        return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Carrega um usuario por identificador incluindo suas roles."""
        statement = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        return self._session.scalar(statement)

    def find_by_email(self, email: str) -> Optional[User]:
        """Carrega um usuario por e-mail incluindo suas roles."""
        statement = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.email == email)
        )
        return self._session.scalar(statement)

    def find_by_role(self, role_name: str) -> list[User]:
        """Retorna usuarios com a role informada, ordenados por nome."""
        statement = (
            select(User)
            .join(User.roles)
            .options(selectinload(User.roles))
            .where(Role.name == role_name)
            .order_by(User.name.asc())
        )
        return list(self._session.execute(statement).scalars().unique())

    def list_all(self, sort_direction: SortDirection) -> list[User]:
        """Retorna todos os usuarios ordenados por nome."""
        order_by = User.name.asc() if sort_direction is SortDirection.ASC else User.name.desc()
        statement = select(User).options(selectinload(User.roles)).order_by(order_by)
        return list(self._session.scalars(statement))

    def delete(self, user: User) -> None:
        """Marca um usuario persistido para remocao."""
        self._session.delete(user)
