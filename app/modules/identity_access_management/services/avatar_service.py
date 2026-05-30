from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.identity_access_management.models.user_avatar import UserAvatar
from app.modules.identity_access_management.repositories.user_avatar_repository import (
    UserAvatarRepository,
)
from app.modules.identity_access_management.repositories.user_repository import UserRepository
from app.modules.identity_access_management.services.avatar_storage import AvatarStorage


ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


@dataclass(frozen=True)
class AvatarResult:
    """Resposta de dominio para operacoes de avatar."""

    user_id: int
    content_type: str
    size_bytes: int
    url: str


class AvatarService:
    """Casos de uso de upload/consulta/remocao de avatar."""

    def __init__(
        self,
        user_repository: UserRepository,
        avatar_repository: UserAvatarRepository,
        storage: AvatarStorage,
        session: Session,
        settings: Settings,
    ) -> None:
        self._user_repository = user_repository
        self._avatar_repository = avatar_repository
        self._storage = storage
        self._session = session
        self._settings = settings

    def upload_avatar(self, *, user_id: int, content_type: str, content: bytes) -> AvatarResult:
        """Valida, armazena e persiste metadados de avatar do usuario."""
        self._ensure_user_exists(user_id)
        self._validate_upload(content_type=content_type, content=content)

        extension = ALLOWED_AVATAR_CONTENT_TYPES[content_type]
        object_key = f"{user_id}/{uuid4().hex}.{extension}"
        existing = self._avatar_repository.find_by_user_id(user_id)

        stored = self._storage.upload(object_key=object_key, content_type=content_type, content=content)
        try:
            if existing is None:
                avatar = UserAvatar(
                    user_id=user_id,
                    storage_backend=self._settings.avatar_storage_backend,
                    object_key=stored.object_key,
                    content_type=stored.content_type,
                    size_bytes=stored.size_bytes,
                )
                self._avatar_repository.add(avatar)
            else:
                previous_key = existing.object_key
                existing.storage_backend = self._settings.avatar_storage_backend
                existing.object_key = stored.object_key
                existing.content_type = stored.content_type
                existing.size_bytes = stored.size_bytes
                if previous_key != stored.object_key:
                    self._storage.delete(previous_key)
            self._commit()
        except Exception:
            self._storage.delete(stored.object_key)
            raise

        return AvatarResult(
            user_id=user_id,
            content_type=stored.content_type,
            size_bytes=stored.size_bytes,
            url=self._build_avatar_url(user_id=user_id, object_key=stored.object_key),
        )

    def get_avatar(self, *, user_id: int) -> AvatarResult:
        """Retorna metadados e URL de acesso ao avatar ativo do usuario."""
        self._ensure_user_exists(user_id)
        avatar = self._avatar_repository.find_by_user_id(user_id)
        if avatar is None:
            raise NotFoundError(f"Avatar for user {user_id} not found")

        return AvatarResult(
            user_id=user_id,
            content_type=avatar.content_type,
            size_bytes=avatar.size_bytes,
            url=self._build_avatar_url(user_id=user_id, object_key=avatar.object_key),
        )

    def get_avatar_content(self, user_id: int) -> tuple[bytes, str]:
        """Retorna bytes e content-type para backend local."""
        self._ensure_user_exists(user_id)
        avatar = self._avatar_repository.find_by_user_id(user_id)
        if avatar is None:
            raise NotFoundError(f"Avatar for user {user_id} not found")
        content = self._storage.get_content(avatar.object_key)
        if content is None:
            raise NotFoundError(f"Avatar binary for user {user_id} not found")
        return content, avatar.content_type

    def delete_avatar(self, *, user_id: int) -> None:
        """Remove metadados e objeto do avatar ativo."""
        self._ensure_user_exists(user_id)
        avatar = self._avatar_repository.find_by_user_id(user_id)
        if avatar is None:
            raise NotFoundError(f"Avatar for user {user_id} not found")

        object_key = avatar.object_key
        self._avatar_repository.delete(avatar)
        self._commit()
        self._storage.delete(object_key)

    def _ensure_user_exists(self, user_id: int) -> None:
        if self._user_repository.find_by_id(user_id) is None:
            raise NotFoundError(f"User {user_id} not found")

    def _validate_upload(self, *, content_type: str, content: bytes) -> None:
        if content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
            raise BadRequestError("Unsupported avatar content type")
        if len(content) == 0:
            raise BadRequestError("Avatar payload must not be empty")
        if len(content) > self._settings.avatar_max_size_bytes:
            raise BadRequestError("Avatar payload exceeds configured max size")

    def _commit(self) -> None:
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def _build_avatar_url(self, *, user_id: int, object_key: str) -> str:
        if self._settings.avatar_storage_backend == "local":
            return f"/api/users/{user_id}/avatar/content"
        return self._storage.get_url(object_key)
