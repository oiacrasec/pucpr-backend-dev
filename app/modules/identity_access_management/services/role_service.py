from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError
from app.modules.identity_access_management.domain.role_name import RoleName
from app.modules.identity_access_management.models.role import Role
from app.modules.identity_access_management.repositories.role_repository import (
    RoleRepository,
)


class RoleService:
    """Orquestra as regras de criacao e listagem de roles."""

    def __init__(self, role_repository: RoleRepository, session: Session) -> None:
        self._role_repository = role_repository
        self._session = session

    def create_role(self, name: str, description: str) -> Role:
        """Cria uma role com nome normalizado em uppercase e validacao de unicidade."""
        normalized_name = RoleName(name).normalized()
        if self._role_repository.find_by_name(normalized_name) is not None:
            raise BadRequestError(f"Role {normalized_name} already exists.")

        role = Role(name=normalized_name, description=description.strip())
        self._role_repository.add(role)
        self._commit()
        return role

    def list_roles(self) -> list[Role]:
        """Lista roles ordenadas por nome."""
        return self._role_repository.list_all()

    def _commit(self) -> None:
        """Confirma a transacao atual e desfaz a sessao em caso de falha."""
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
