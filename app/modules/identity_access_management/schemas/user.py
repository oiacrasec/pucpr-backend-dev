import re

from pydantic import BaseModel, EmailStr, field_validator

from app.modules.identity_access_management.models.user import User


PASSWORD_PATTERN = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"


class CreateUserRequest(BaseModel):
    """Payload usado para criar uma nova conta de usuario."""

    email: EmailStr
    password: str
    name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Aplica a politica de complexidade de senha documentada."""
        if not re.fullmatch(PASSWORD_PATTERN, value):
            raise ValueError("Password does not satisfy the complexity policy")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Rejeita nomes em branco antes de chegar na camada de servico."""
        if not value or not value.strip():
            raise ValueError("Value must not be blank")
        return value.strip()


class UpdateUserRequest(BaseModel):
    """Payload usado para atualizar o nome publico de um usuario."""

    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Rejeita nomes em branco antes de chegar na camada de servico."""
        if not value or not value.strip():
            raise ValueError("Value must not be blank")
        return value.strip()


class UserResponse(BaseModel):
    """Representacao publica de um usuario retornada pela API."""

    id: int
    email: EmailStr
    name: str

    @classmethod
    def from_model(cls, user: User) -> "UserResponse":
        """Constroi um DTO de resposta a partir de um modelo persistido de usuario."""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
        )
