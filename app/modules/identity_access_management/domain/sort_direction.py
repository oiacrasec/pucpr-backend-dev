from enum import Enum

from app.core.exceptions import BadRequestError


class SortDirection(str, Enum):
    """Direcoes de ordenacao suportadas na listagem de usuarios."""

    ASC = "ASC"
    DESC = "DESC"

    @classmethod
    def from_query(cls, raw_value: str) -> "SortDirection":
        """Converte um valor de query string em uma direcao de ordenacao valida."""
        normalized = raw_value.upper()
        for value in cls:
            if value.value == normalized:
                return value
        raise BadRequestError("Invalid sort dir")
