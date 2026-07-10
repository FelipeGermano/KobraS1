from pathlib import Path

from app.services.stl_service import analyze_stl


def test_analyze_ascii_stl_dimensions(tmp_path: Path) -> None:
    stl = tmp_path / "triangle.stl"
    stl.write_text(
        """solid test
facet normal 0 0 1
 outer loop
  vertex 0 0 0
  vertex 10 0 0
  vertex 0 20 0
 endloop
endfacet
endsolid test
""",
        encoding="utf-8",
    )

    analysis = analyze_stl(stl)

    assert analysis.dimensions_mm == (10.0, 20.0, 0.0)
    assert analysis.triangle_count == 1
    assert analysis.surface_area_mm2 == 100.0
    assert analysis.fits_printer is True


def test_model_larger_than_printer_is_flagged(tmp_path: Path) -> None:
    stl = tmp_path / "large.stl"
    stl.write_text(
        """solid test
facet normal 0 0 1
 outer loop
  vertex 0 0 0
  vertex 260 0 0
  vertex 0 20 0
 endloop
endfacet
endsolid test
""",
        encoding="utf-8",
    )

    analysis = analyze_stl(stl)

    assert analysis.fits_printer is False
    assert any("excede" in warning for warning in analysis.warnings)

