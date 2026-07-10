from pathlib import Path

from app.domain.model_analysis import ModelAnalysis
from app.domain.slicing_profile import UserChoices
from app.services.profile_engine import build_profile


def _analysis() -> ModelAnalysis:
    return ModelAnalysis(
        source_path=Path("sample.stl"),
        file_type="STL",
        dimensions_mm=(50.0, 50.0, 20.0),
        volume_mm3=1000.0,
        surface_area_mm2=500.0,
        triangle_count=12,
        is_watertight=None,
        fits_printer=True,
    )


def test_builds_pla_common_normal_profile() -> None:
    profile = build_profile(
        UserChoices(
            material="PLA",
            strength="Uso comum",
            quality="Normal",
            priority="equilibrio",
            supports_allowed=True,
        ),
        _analysis(),
    )

    assert profile.nozzle_temp_c == 210
    assert profile.bed_temp_c == 60
    assert profile.layer_height_mm == 0.20
    assert profile.walls == 3
    assert profile.infill_percent == 15


def test_strength_priority_increases_walls_and_infill() -> None:
    profile = build_profile(
        UserChoices(
            material="PLA",
            strength="Resistente",
            quality="Normal",
            priority="resistencia",
            supports_allowed=True,
        ),
        _analysis(),
    )

    assert profile.walls == 5
    assert profile.infill_percent == 33

