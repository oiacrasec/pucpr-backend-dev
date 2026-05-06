from __future__ import annotations

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import JwtTokenService, TokenUser
from app.modules.identity_access_management.api.dependencies import get_token_service


bearer_scheme = HTTPBearer(auto_error=False)


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    token_service: JwtTokenService = Depends(get_token_service),
) -> Optional[TokenUser]:
    """Retorna o usuario autenticado quando houver token bearer na requisicao."""
    if credentials is None:
        return None
    return token_service.decode_token(credentials.credentials)


def get_current_user(
    current_user: Optional[TokenUser] = Depends(get_optional_current_user),
) -> TokenUser:
    """Exige um usuario autenticado valido na requisicao atual."""
    if current_user is None:
        raise UnauthorizedError("Authentication is required")
    return current_user


def require_admin(current_user: TokenUser = Depends(get_current_user)) -> TokenUser:
    """Exige que o usuario autenticado possua a role ADMIN."""
    if not current_user.is_admin:
        raise ForbiddenError("Admin role is required")
    return current_user


def require_self_or_admin(
    user_id: int,
    current_user: TokenUser = Depends(get_current_user),
) -> TokenUser:
    """Exige que o usuario alvo seja o autor ou que o autor seja admin."""
    if current_user.id != user_id and not current_user.is_admin:
        raise ForbiddenError("Update is not allowed")
    return current_user
