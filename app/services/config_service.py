from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = PROJECT_ROOT / "app" / "config"


def load_json_config(relative_path: str, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    path = CONFIG_ROOT / relative_path
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json_config(relative_path: str, data: dict[str, Any]) -> Path:
    path = CONFIG_ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
