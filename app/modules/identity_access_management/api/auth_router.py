from fastapi import APIRouter, Depends

from app.modules.identity_access_management.api.dependencies import get_auth_service
from app.modules.identity_access_management.schemas.auth import LoginRequest, LoginResponse
from app.modules.identity_access_management.schemas.user import UserResponse
from app.modules.identity_access_management.services.auth_service import AuthService


router = APIRouter(prefix="/users", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """Autentica um usuario e retorna o token de acesso com o perfil publico."""
    token, user = service.login(request.email, request.password)
    return LoginResponse(token=token, user=UserResponse.from_model(user))
