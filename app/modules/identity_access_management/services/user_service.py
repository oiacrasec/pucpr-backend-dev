from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.security import PasswordHasher
from app.modules.identity_access_management.domain.role_name import RoleName
from app.modules.identity_access_management.domain.sort_direction import SortDirection
from app.modules.identity_access_management.models.user import User
from app.modules.identity_access_management.repositories.role_repository import (
    RoleRepository,
)
from app.modules.identity_access_management.repositories.user_repository import (
    UserRepository,
)


class UserService:
    """Orquestra casos de uso de usuario e aplica regras de negocio."""

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        session: Session,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._session = session
        self._password_hasher = password_hasher

    def create_user(self, email: str, password: str, name: str) -> User:
        """Cria um usuario se o e-mail ainda nao estiver em uso."""
        if self._user_repository.find_by_email(email) is not None:
            raise BadRequestError("User already exists")

        user = User(
            email=email,
            password=self._password_hasher.hash(password),
            name=name.strip(),
        )
        self._user_repository.add(user)
        self._commit()
        return user

    def list_users(self, sort_direction: SortDirection) -> list[User]:
        """Lista usuarios ordenados por nome conforme a direcao informada."""
        return self._user_repository.list_all(sort_direction)

    def list_users_by_role(self, role_name: str) -> list[User]:
        """Lista usuarios filtrados por correspondencia exata de role."""
        return self._user_repository.find_by_role(role_name)

    def get_user(self, user_id: int) -> User:
        """Carrega um usuario por identificador ou dispara erro de nao encontrado."""
        user = self._user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return user

    def update_name(self, user_id: int, name: str) -> Optional[User]:
        """Atualiza o nome de exibicao do usuario ou retorna `None` sem alteracao."""
        user = self.get_user(user_id)
        if user.name == name:
            return None

        user.name = name.strip()
        self._commit()
        return user

    def delete_user(self, user_id: int) -> None:
        """Remove um usuario protegendo a ultima conta admin."""
        user = self.get_user(user_id)
        if user.is_admin and len(self._user_repository.find_by_role("ADMIN")) == 1:
            raise BadRequestError("Cannot delete the last admin")

        self._user_repository.delete(user)
        self._commit()

    def add_role(self, user_id: int, role_name: str) -> bool:
        """Concede uma role a um usuario e informa se houve nova atribuicao."""
        user = self.get_user(user_id)
        normalized_role_name = RoleName(role_name).normalized()
        if any(role.name == normalized_role_name for role in user.roles):
            return False

        role = self._role_repository.find_by_name(normalized_role_name)
        if role is None:
            raise BadRequestError(f"Role {normalized_role_name} not found")

        user.roles.add(role)
        self._commit()
        return True

    def _commit(self) -> None:
        """Confirma a transacao atual e desfaz a sessao em caso de falha."""
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
