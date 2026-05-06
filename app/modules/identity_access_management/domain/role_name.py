from dataclasses import dataclass


@dataclass(frozen=True)
class RoleName:
    """Value object usado para normalizar e comparar identificadores de role."""

    value: str

    def normalized(self) -> str:
        """Retorna a representacao canonica em uppercase do nome da role."""
        return self.value.strip().upper()
