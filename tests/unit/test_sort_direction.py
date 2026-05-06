import pytest

from app.core.exceptions import BadRequestError
from app.modules.identity_access_management.domain.sort_direction import SortDirection


def test_sort_direction_parses_known_values():
    assert SortDirection.from_query("asc") is SortDirection.ASC
    assert SortDirection.from_query("DESC") is SortDirection.DESC


def test_sort_direction_rejects_invalid_values():
    with pytest.raises(BadRequestError, match="Invalid sort dir"):
        SortDirection.from_query("SIDEWAYS")
