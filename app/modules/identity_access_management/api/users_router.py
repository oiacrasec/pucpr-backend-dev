from __future__ import annotations

from typing import Optional, Union

from fastapi import APIRouter, Depends, Response, status

from app.modules.identity_access_management.api.dependencies import get_user_service
from app.modules.identity_access_management.domain.sort_direction import SortDirection
from app.modules.identity_access_management.policies.access import require_admin, require_self_or_admin
from app.modules.identity_access_management.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
)
from app.modules.identity_access_management.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(
    sortDir: str = "ASC",
    role: Optional[str] = None,
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    """Lista usuarios publicamente, com filtro opcional por role exata."""
    users = (
        service.list_users_by_role(role)
        if role is not None
        else service.list_users(SortDirection.from_query(sortDir))
    )
    return [UserResponse.from_model(user) for user in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    request: CreateUserRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Cria uma nova conta de usuario."""
    user = service.create_user(request.email, request.password, request.name)
    return UserResponse.from_model(user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> UserResponse:
    """Busca um usuario pelo identificador."""
    return UserResponse.from_model(service.get_user(user_id))


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    _: object = Depends(require_self_or_admin),
    service: UserService = Depends(get_user_service),
) -> Union[UserResponse, Response]:
    """Atualiza o nome do usuario alvo quando o autor e o proprio usuario ou admin."""
    updated_user = service.update_name(user_id, request.name)
    if updated_user is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return UserResponse.from_model(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    _: object = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> Response:
    """Remove uma conta de usuario preservando pelo menos um admin no sistema."""
    service.delete_user(user_id)
    return Response(status_code=status.HTTP_200_OK)


@router.put("/{user_id}/roles/{role_name}", status_code=status.HTTP_200_OK)
def add_role_to_user(
    user_id: int,
    role_name: str,
    _: object = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> Response:
    """Concede uma role a um usuario e preserva o comportamento legado 200/204."""
    added = service.add_role(user_id, role_name)
    if not added:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_200_OK)
