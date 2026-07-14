"""Unit tests for Bronze storage."""

from __future__ import annotations

import uuid

import pytest

from app.ingestion.exceptions import IngestionError
from app.ingestion.storage import BronzeStorage


def test_bronze_storage_round_trip(tmp_path) -> None:
    storage = BronzeStorage(tmp_path)
    org_id = uuid.uuid4()
    content = b"category,amount\nTravel,100\n"
    path, size = storage.save(org_id, "data.csv", content)
    assert size == len(content)
    assert storage.read(path) == content


def test_bronze_storage_rejects_unsupported_extension(tmp_path) -> None:
    storage = BronzeStorage(tmp_path)
    with pytest.raises(IngestionError):
        storage.save(uuid.uuid4(), "notes.txt", b"hello")
