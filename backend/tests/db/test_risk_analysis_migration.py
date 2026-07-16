"""Alembic migration chain tests for risk analysis persistence."""

from __future__ import annotations

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_risk_analysis_migration_is_head() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    head = script.get_current_head()
    assert head == "f9c2d7a31b44"


def test_risk_analysis_migration_revises_prior_head() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    revision = script.get_revision("f9c2d7a31b44")
    assert revision is not None
    assert revision.down_revision == "e8a1c4f03d21"
