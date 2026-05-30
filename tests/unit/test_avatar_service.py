from __future__ import annotations

from dataclasses import dataclass

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.db.base import Base
from app.modules.identity_access_management.models import Role, User, UserAvatar
from app.modules.identity_access_management.repositories.user_avatar_repository import (
    UserAvatarRepository,
)
from app.modules.identity_access_management.repositories.user_repository import UserRepository
from app.modules.identity_access_management.services.avatar_service import AvatarService
from app.modules.identity_access_management.services.avatar_storage import StoredAvatar


@dataclass
class InMemoryStorage:
    files: dict[str, bytes]

    def upload(self, *, object_key: str, content_type: str, content: bytes) -> StoredAvatar:
        self.files[object_key] = content
        return StoredAvatar(object_key=object_key, content_type=content_type, size_bytes=len(content))

    def delete(self, object_key: str) -> None:
        self.files.pop(object_key, None)

    def get_url(self, object_key: str) -> str:
        return f"https://storage.local/{object_key}"

    def get_content(self, object_key: str) -> bytes | None:
        return self.files.get(object_key)


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True, class_=Session)
    with factory() as db_session:
        yield db_session
    engine.dispose()


def _create_user(session: Session, user_id: int = 1) -> User:
    role = Role(name="USER", description="Default role")
    user = User(id=user_id, email=f"user{user_id}@test.com", password="hashed", name="User")
    user.roles.add(role)
    session.add_all([role, user])
    session.commit()
    return user


def _build_service(session: Session, settings: Settings, files: dict[str, bytes]) -> AvatarService:
    return AvatarService(
        user_repository=UserRepository(session),
        avatar_repository=UserAvatarRepository(session),
        storage=InMemoryStorage(files),
        session=session,
        settings=settings,
    )


def test_upload_avatar_creates_metadata_and_content(session: Session) -> None:
    _create_user(session)
    settings = Settings(
        environment="test",
        database_url="sqlite+pysqlite:///:memory:",
        auto_create_schema=False,
        seed_data=False,
        jwt_secret="test-secret-with-at-least-thirty-two-characters",
        avatar_storage_backend="local",
    )
    files: dict[str, bytes] = {}
    service = _build_service(session, settings, files)

    result = service.upload_avatar(user_id=1, content_type="image/png", content=b"img")

    assert result.user_id == 1
    assert result.content_type == "image/png"
    assert result.size_bytes == 3
    assert result.url == "/api/users/1/avatar/content"
    assert len(files) == 1
    assert session.query(UserAvatar).count() == 1


def test_upload_avatar_replaces_previous_file(session: Session) -> None:
    _create_user(session)
    settings = Settings(
        environment="test",
        database_url="sqlite+pysqlite:///:memory:",
        auto_create_schema=False,
        seed_data=False,
        jwt_secret="test-secret-with-at-least-thirty-two-characters",
        avatar_storage_backend="local",
    )
    files: dict[str, bytes] = {}
    service = _build_service(session, settings, files)

    first = service.upload_avatar(user_id=1, content_type="image/png", content=b"first")
    second = service.upload_avatar(user_id=1, content_type="image/png", content=b"second")

    assert first.url == "/api/users/1/avatar/content"
    assert second.url == "/api/users/1/avatar/content"
    assert len(files) == 1
    assert next(iter(files.values())) == b"second"
    assert session.query(UserAvatar).count() == 1


def test_upload_avatar_rejects_invalid_type(session: Session) -> None:
    _create_user(session)
    settings = Settings(
        environment="test",
        database_url="sqlite+pysqlite:///:memory:",
        auto_create_schema=False,
        seed_data=False,
        jwt_secret="test-secret-with-at-least-thirty-two-characters",
        avatar_storage_backend="local",
    )
    service = _build_service(session, settings, {})

    with pytest.raises(BadRequestError):
        service.upload_avatar(user_id=1, content_type="application/pdf", content=b"not-image")


def test_delete_avatar_removes_metadata_and_content(session: Session) -> None:
    _create_user(session)
    settings = Settings(
        environment="test",
        database_url="sqlite+pysqlite:///:memory:",
        auto_create_schema=False,
        seed_data=False,
        jwt_secret="test-secret-with-at-least-thirty-two-characters",
        avatar_storage_backend="local",
    )
    files: dict[str, bytes] = {}
    service = _build_service(session, settings, files)

    service.upload_avatar(user_id=1, content_type="image/png", content=b"img")
    service.delete_avatar(user_id=1)

    assert files == {}
    assert session.query(UserAvatar).count() == 0
    with pytest.raises(NotFoundError):
        service.get_avatar(user_id=1)
