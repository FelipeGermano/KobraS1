from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT)) / "app" / "config"
USER_CONFIG_ROOT = Path(os.environ.get("APPDATA", PROJECT_ROOT)) / "KobraS1Assistant"


def load_json_config(relative_path: str, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    user_path = USER_CONFIG_ROOT / relative_path
    bundled_path = CONFIG_ROOT / relative_path
    path = user_path if user_path.exists() else bundled_path
    if not path.exists():
        return fallback or {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json_config(relative_path: str, data: dict[str, Any]) -> Path:
    path = USER_CONFIG_ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
