import json
from pathlib import Path
from zipfile import ZipFile

from app.domain.slicing_profile import UserChoices
from app.services.model_import_service import analyze_model
from app.services.profile_engine import build_profile
from app.services.project_export_service import export_recommended_3mf


def test_export_stl_as_3mf_with_recommended_profile(tmp_path: Path) -> None:
    source = tmp_path / "cube.stl"
    source.write_text(_cube_stl(), encoding="utf-8")
    analysis = analyze_model(source)
    choices = UserChoices(
        material="PLA",
        strength="Resistente",
        quality="Normal",
        priority="equilibrio",
        supports_allowed=True,
    )
    profile = build_profile(choices, analysis)

    output = export_recommended_3mf(
        source,
        tmp_path / "cube_kobra_s1.3mf",
        analysis,
        choices,
        profile,
    )

    exported_analysis = analyze_model(output)
    assert exported_analysis.dimensions_mm == (10.0, 10.0, 10.0)
    with ZipFile(output) as archive:
        settings = json.loads(archive.read("Metadata/project_settings.config"))
        summary = json.loads(archive.read("Metadata/kobra_s1_summary.json"))

    assert settings["printer_settings_id"] == "Anycubic Kobra S1 0.4 nozzle"
    assert settings["wall_loops"] == "4"
    assert settings["sparse_infill_density"] == "25%"
    assert settings["layer_height"] == "0.2"
    assert summary["profile"]["material"] == "PLA"


def _cube_stl() -> str:
    return """solid cube
facet normal 0 0 -1
 outer loop
  vertex 0 0 0
  vertex 0 10 0
  vertex 10 10 0
 endloop
endfacet
facet normal 0 0 -1
 outer loop
  vertex 0 0 0
  vertex 10 10 0
  vertex 10 0 0
 endloop
endfacet
facet normal 0 0 1
 outer loop
  vertex 0 0 10
  vertex 10 10 10
  vertex 0 10 10
 endloop
endfacet
facet normal 0 0 1
 outer loop
  vertex 0 0 10
  vertex 10 0 10
  vertex 10 10 10
 endloop
endfacet
facet normal -1 0 0
 outer loop
  vertex 0 0 0
  vertex 0 0 10
  vertex 0 10 10
 endloop
endfacet
facet normal -1 0 0
 outer loop
  vertex 0 0 0
  vertex 0 10 10
  vertex 0 10 0
 endloop
endfacet
facet normal 1 0 0
 outer loop
  vertex 10 0 0
  vertex 10 10 10
  vertex 10 0 10
 endloop
endfacet
facet normal 1 0 0
 outer loop
  vertex 10 0 0
  vertex 10 10 0
  vertex 10 10 10
 endloop
endfacet
facet normal 0 -1 0
 outer loop
  vertex 0 0 0
  vertex 10 0 10
  vertex 0 0 10
 endloop
endfacet
facet normal 0 -1 0
 outer loop
  vertex 0 0 0
  vertex 10 0 0
  vertex 10 0 10
 endloop
endfacet
facet normal 0 1 0
 outer loop
  vertex 0 10 0
  vertex 0 10 10
  vertex 10 10 10
 endloop
endfacet
facet normal 0 1 0
 outer loop
  vertex 0 10 0
  vertex 10 10 10
  vertex 10 10 0
 endloop
endfacet
endsolid cube
"""
