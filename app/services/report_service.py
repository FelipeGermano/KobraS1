from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

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
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path

