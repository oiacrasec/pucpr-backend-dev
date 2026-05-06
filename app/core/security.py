import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import Settings
from app.core.exceptions import UnauthorizedError


PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 390_000


@dataclass(frozen=True)
class TokenUser:
    """Dados do usuario autenticado transportados dentro do JWT."""

    id: int
    name: str
    roles: tuple[str, ...]

    @property
    def is_admin(self) -> bool:
        """Indica se o token carrega a role ADMIN."""
        return "ADMIN" in self.roles


class PasswordHasher:
    """Gera hash e verifica senhas com PBKDF2 e fallback para o legado."""

    def hash(self, password: str) -> str:
        """Cria um hash PBKDF2-SHA256 para uma senha em texto puro."""
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )
        return (
            f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}$"
            f"{base64.b64encode(salt).decode('utf-8')}$"
            f"{base64.b64encode(digest).decode('utf-8')}"
        )

    def verify(self, plain_password: str, stored_password: str) -> bool:
        """Verifica uma senha contra um hash PBKDF2 ou um valor legado em texto puro."""
        if not stored_password.startswith(f"{PBKDF2_PREFIX}$"):
            return hmac.compare_digest(plain_password, stored_password)

        _, iterations, encoded_salt, encoded_digest = stored_password.split("$", maxsplit=3)
        salt = base64.b64decode(encoded_salt.encode("utf-8"))
        expected_digest = base64.b64decode(encoded_digest.encode("utf-8"))
        candidate_digest = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return hmac.compare_digest(candidate_digest, expected_digest)


class JwtTokenService:
    """Emite e valida os tokens JWT de acesso usados pela API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_token(self, user: TokenUser) -> str:
        """Cria um JWT assinado que segue o payload de compatibilidade documentado."""
        issued_at = datetime.now(tz=timezone.utc)
        expires_in = (
            self._settings.admin_token_expire_hours
            if user.is_admin
            else self._settings.user_token_expire_hours
        )
        payload = {
            "iss": self._settings.jwt_issuer,
            "sub": str(user.id),
            "iat": int(issued_at.timestamp()),
            "exp": int((issued_at + timedelta(hours=expires_in)).timestamp()),
            self._settings.jwt_user_claim: {
                "id": user.id,
                "name": user.name,
                "roles": list(sorted(user.roles)),
            },
        }
        return jwt.encode(
            payload=payload,
            key=self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

    def decode_token(self, token: str) -> TokenUser:
        """Decodifica um JWT e materializa o claim `user` em um objeto de dominio."""
        try:
            payload = jwt.decode(
                jwt=token,
                key=self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
                issuer=self._settings.jwt_issuer,
            )
        except jwt.InvalidTokenError as exc:
            raise UnauthorizedError("Invalid or expired token") from exc

        token_user = payload.get(self._settings.jwt_user_claim)
        if not isinstance(token_user, dict):
            raise UnauthorizedError("Invalid or expired token")

        try:
            user_id = int(token_user["id"])
            name = str(token_user["name"])
            roles = tuple(sorted(str(role) for role in token_user["roles"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise UnauthorizedError("Invalid or expired token") from exc

        return TokenUser(id=user_id, name=name, roles=roles)
