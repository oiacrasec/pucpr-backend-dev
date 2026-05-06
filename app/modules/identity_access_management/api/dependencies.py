from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.dependencies import get_db_session, get_settings
from app.core.security import JwtTokenService, PasswordHasher
from app.modules.identity_access_management.repositories.role_repository import (
    RoleRepository,
)
from app.modules.identity_access_management.repositories.user_repository import (
    UserRepository,
)
from app.modules.identity_access_management.services.auth_service import AuthService
from app.modules.identity_access_management.services.role_service import RoleService
from app.modules.identity_access_management.services.user_service import UserService


def get_password_hasher() -> PasswordHasher:
    """Fornece o servico de hash de senha usado pelo modulo."""
    return PasswordHasher()


def get_token_service(settings: Settings = Depends(get_settings)) -> JwtTokenService:
    """Fornece o servico JWT configurado para o ambiente atual."""
    return JwtTokenService(settings)


def get_user_repository(
    session: Session = Depends(get_db_session),
) -> UserRepository:
    """Fornece o repositorio de usuarios vinculado a sessao atual de banco."""
    return UserRepository(session)


def get_role_repository(
    session: Session = Depends(get_db_session),
) -> RoleRepository:
    """Fornece o repositorio de roles vinculado a sessao atual de banco."""
    return RoleRepository(session)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: JwtTokenService = Depends(get_token_service),
) -> AuthService:
    """Monta o servico de autenticacao."""
    return AuthService(user_repository, password_hasher, token_service)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    role_repository: RoleRepository = Depends(get_role_repository),
    session: Session = Depends(get_db_session),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> UserService:
    """Monta o servico de usuarios."""
    return UserService(user_repository, role_repository, session, password_hasher)


def get_role_service(
    role_repository: RoleRepository = Depends(get_role_repository),
    session: Session = Depends(get_db_session),
) -> RoleService:
    """Monta o servico de roles."""
    return RoleService(role_repository, session)
