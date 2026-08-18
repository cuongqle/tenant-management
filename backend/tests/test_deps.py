import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.deps import get_or_404


def test_get_or_404_returns_entity() -> None:
    entity_id = uuid.uuid4()
    entity = object()
    repository = MagicMock()
    repository.get_by_id.return_value = entity

    assert get_or_404(repository, entity_id, detail="Missing") is entity
    repository.get_by_id.assert_called_once_with(entity_id)


def test_get_or_404_raises_when_missing() -> None:
    repository = MagicMock()
    repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_or_404(repository, uuid.uuid4(), detail="Organization not found")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Organization not found"
