from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.core.config import Settings
from app.core.exceptions import BadRequestError


@dataclass(frozen=True)
class StoredAvatar:
    """Resultado de armazenamento para um arquivo de avatar."""

    object_key: str
    content_type: str
    size_bytes: int


class AvatarStorage(Protocol):
    """Contrato de armazenamento para arquivos de avatar."""

    def upload(self, *, object_key: str, content_type: str, content: bytes) -> StoredAvatar: ...

    def delete(self, object_key: str) -> None: ...

    def get_url(self, object_key: str) -> str: ...

    def get_content(self, object_key: str) -> bytes | None: ...


class LocalAvatarStorage:
    """Armazenamento de avatar no sistema de arquivos local."""

    def __init__(self, root_dir: str) -> None:
        self._root = Path(root_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    def upload(self, *, object_key: str, content_type: str, content: bytes) -> StoredAvatar:
        target = self._resolve(object_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return StoredAvatar(object_key=object_key, content_type=content_type, size_bytes=len(content))

    def delete(self, object_key: str) -> None:
        target = self._resolve(object_key)
        if target.exists():
            target.unlink()

    def get_url(self, object_key: str) -> str:
        return f"/api/users/me/avatar/content?key={object_key}"

    def get_content(self, object_key: str) -> bytes | None:
        target = self._resolve(object_key)
        if not target.exists():
            return None
        return target.read_bytes()

    def _resolve(self, object_key: str) -> Path:
        sanitized = object_key.strip().lstrip("/").replace("\\", "/")
        target = (self._root / sanitized).resolve()
        root = self._root.resolve()
        if root not in target.parents and target != root:
            raise BadRequestError("Invalid avatar key")
        return target


class S3AvatarStorage:
    """Armazenamento de avatar em bucket S3."""

    def __init__(self, settings: Settings) -> None:
        if not settings.avatar_s3_bucket:
            raise BadRequestError("S3 avatar bucket is not configured")
        try:
            import boto3
            from botocore.config import Config
            from botocore.exceptions import ClientError
        except ImportError as exc:
            raise RuntimeError("boto3 is required for S3 avatar backend") from exc

        self._client_error = ClientError
        self._client = boto3.client(
            "s3",
            region_name=settings.avatar_s3_region,
            endpoint_url=settings.avatar_s3_endpoint_url,
            aws_access_key_id=settings.avatar_s3_access_key_id,
            aws_secret_access_key=settings.avatar_s3_secret_access_key,
            config=Config(signature_version="s3v4"),
        )
        self._bucket = settings.avatar_s3_bucket
        self._url_expire_seconds = settings.avatar_s3_url_expire_seconds

    def upload(self, *, object_key: str, content_type: str, content: bytes) -> StoredAvatar:
        self._client.put_object(
            Bucket=self._bucket,
            Key=object_key,
            Body=content,
            ContentType=content_type,
        )
        return StoredAvatar(object_key=object_key, content_type=content_type, size_bytes=len(content))

    def delete(self, object_key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=object_key)

    def get_url(self, object_key: str) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": object_key},
            ExpiresIn=self._url_expire_seconds,
        )

    def get_content(self, object_key: str) -> bytes | None:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=object_key)
            body = response["Body"].read()
        except self._client_error as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code in {"NoSuchKey", "404"}:
                return None
            raise
        return body


def build_avatar_storage(settings: Settings) -> AvatarStorage:
    """Monta o provider de storage conforme configuracao."""
    if settings.avatar_storage_backend == "local":
        local_root = Path(settings.media_root) / settings.avatar_local_root
        return LocalAvatarStorage(str(local_root))
    return S3AvatarStorage(settings)
