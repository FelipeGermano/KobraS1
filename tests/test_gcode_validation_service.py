from pathlib import Path

from app.domain.model_analysis import ModelAnalysis
from app.domain.slicing_profile import UserChoices
from app.services.gcode_validation_service import validate_gcode
from app.services.profile_engine import build_profile


def test_validate_gcode_checks_temperatures_and_bounds(tmp_path: Path) -> None:
    gcode = tmp_path / "part.gcode"
    gcode.write_text(
        """; estimated printing time: 1h 02m
; filament used: 3.21m
M104 S210
M140 S60
G1 X10 Y10 Z0.2
G1 X120 Y120 Z20
""",
        encoding="utf-8",
    )
    profile = build_profile(
        UserChoices("PLA", "Uso comum", "Normal", "equilibrio", True),
        _analysis(),
    )

    validation = validate_gcode(gcode, profile)

    assert validation.is_valid is True
    assert validation.nozzle_temps_c == (210,)
    assert validation.bed_temps_c == (60,)
    assert validation.estimated_time == "1h 02m"
    assert validation.filament_used == "3.21m"


def test_validate_gcode_flags_wrong_temperature(tmp_path: Path) -> None:
    gcode = tmp_path / "wrong.gcode"
    gcode.write_text("M104 S250\nM140 S60\nG1 X10 Y10 Z0.2\n", encoding="utf-8")
    profile = build_profile(
        UserChoices("PLA", "Uso comum", "Normal", "equilibrio", True),
        _analysis(),
    )

    validation = validate_gcode(gcode, profile)

    assert validation.is_valid is False
    assert any("bico" in warning for warning in validation.warnings)


def _analysis() -> ModelAnalysis:
    return ModelAnalysis(
        source_path=Path("sample.stl"),
        file_type="STL",
        dimensions_mm=(50.0, 50.0, 20.0),
        volume_mm3=1000.0,
        surface_area_mm2=500.0,
        triangle_count=12,
        component_count=1,
        is_watertight=True,
        is_winding_consistent=True,
        is_volume=True,
        degenerate_face_count=0,
        non_manifold_edge_count=0,
        inverted_normal_likely=False,
        thin_wall_warning=False,
        base_contact_area_mm2=2500.0,
        support_likely=False,
        scale_suspect=False,
        fits_printer=True,
    )
