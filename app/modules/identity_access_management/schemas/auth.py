from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    """Payload usado para autenticar um usuario existente."""

    email: str
    password: str

    @field_validator("email", "password")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        """Rejeita credenciais em branco antes de chegar na camada de servico."""
        if not value or not value.strip():
            raise ValueError("Value must not be blank")
        return value.strip()


class LoginResponse(BaseModel):
    """Resposta de autenticacao com token de acesso e perfil publico."""

    token: str
    user: "UserResponse"


from app.modules.identity_access_management.schemas.user import UserResponse

LoginResponse.model_rebuild()
