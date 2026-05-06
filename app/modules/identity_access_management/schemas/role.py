from pydantic import BaseModel, field_validator

from app.modules.identity_access_management.models.role import Role


class CreateRoleRequest(BaseModel):
    """Payload usado para criar uma nova role."""

    name: str
    description: str

    @field_validator("name", "description")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        """Rejeita campos em branco antes de chegar na camada de servico."""
        if not value or not value.strip():
            raise ValueError("Value must not be blank")
        return value.strip()


class RoleResponse(BaseModel):
    """Representacao publica de uma role retornada pela API."""

    name: str
    description: str

    @classmethod
    def from_model(cls, role: Role) -> "RoleResponse":
        """Constroi um DTO de resposta a partir de um modelo persistido de role."""
        return cls(name=role.name, description=role.description)
