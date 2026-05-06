from fastapi import APIRouter, Depends, status

from app.modules.identity_access_management.api.dependencies import get_role_service
from app.modules.identity_access_management.policies.access import require_admin
from app.modules.identity_access_management.schemas.role import CreateRoleRequest, RoleResponse
from app.modules.identity_access_management.services.role_service import RoleService


router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    request: CreateRoleRequest,
    _: object = Depends(require_admin),
    service: RoleService = Depends(get_role_service),
) -> RoleResponse:
    """Cria uma nova role restrita a administradores."""
    role = service.create_role(request.name, request.description)
    return RoleResponse.from_model(role)


@router.get("", response_model=list[RoleResponse])
def list_roles(
    _: object = Depends(require_admin),
    service: RoleService = Depends(get_role_service),
) -> list[RoleResponse]:
    """Lista todas as roles com acesso restrito a administradores."""
    return [RoleResponse.from_model(role) for role in service.list_roles()]
