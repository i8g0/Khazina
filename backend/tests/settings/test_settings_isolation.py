"""Settings module isolation boundary tests."""

from __future__ import annotations

import ast
from pathlib import Path


def _collect_imports(module_path: Path) -> set[str]:
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_settings_service_does_not_import_frozen_ai_execution() -> None:
    root = Path(__file__).resolve().parents[2] / "app" / "settings"
    forbidden_prefixes = (
        "app.ai.client",
        "app.ai.services.orchestrator",
        "app.ai.prompts.composer",
        "app.business.engines",
    )
    for path in root.rglob("*.py"):
        imports = _collect_imports(path)
        for forbidden in forbidden_prefixes:
            assert forbidden not in imports, f"{path.name} imports forbidden {forbidden}"
