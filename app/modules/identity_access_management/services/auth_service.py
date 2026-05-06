from app.core.exceptions import UnauthorizedError
from app.core.security import JwtTokenService, PasswordHasher, TokenUser
from app.modules.identity_access_management.models.user import User
from app.modules.identity_access_management.repositories.user_repository import (
    UserRepository,
)


class AuthService:
    """Orquestra os casos de uso de autenticacao do modulo de identidade."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: JwtTokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    def login(self, email: str, password: str) -> tuple[str, User]:
        """Valida credenciais e emite um token JWT de acesso."""
        user = self._user_repository.find_by_email(email)
        if user is None:
            raise UnauthorizedError(f"User {email} not found")

        if not self._password_hasher.verify(password, user.password):
            raise UnauthorizedError("Invalid password")

        token = self._token_service.create_token(
            TokenUser(
                id=user.id,
                name=user.name,
                roles=tuple(sorted(role.name for role in user.roles)),
            )
        )
        return token, user
