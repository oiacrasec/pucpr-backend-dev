from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity_access_management.models.user_avatar import UserAvatar


class UserAvatarRepository:
    """Repositorio de metadados de avatar."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_user_id(self, user_id: int) -> Optional[UserAvatar]:
        """Busca o avatar ativo de um usuario."""
        return self._session.scalar(select(UserAvatar).where(UserAvatar.user_id == user_id))

    def add(self, avatar: UserAvatar) -> UserAvatar:
        """Persiste e sincroniza metadados do avatar."""
        self._session.add(avatar)
        self._session.flush()
        return avatar

    def delete(self, avatar: UserAvatar) -> None:
        """Marca o avatar para remocao."""
        self._session.delete(avatar)
