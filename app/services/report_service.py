from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from app.domain.model_analysis import ModelAnalysis
from app.domain.slicing_profile import SlicingProfile, UserChoices


def build_summary(
    analysis: ModelAnalysis,
    choices: UserChoices,
    profile: SlicingProfile,
) -> dict:
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_file": str(analysis.source_path),
        "analysis": {
            **asdict(analysis),
            "source_path": str(analysis.source_path),
        },
        "choices": asdict(choices),
        "profile": asdict(profile),
    }


def save_summary(summary: dict, output_dir: str | Path = "logs") -> Path:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = destination / f"kobra_s1_summary_{stamp}.json"
    output_path.write_text(
        json.dumps(to_json_safe(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def to_json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return to_json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): to_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value
