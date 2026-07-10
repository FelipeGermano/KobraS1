from pathlib import Path
from zipfile import ZipFile

from app.services.model_import_service import ModelImportError, analyze_model
from app.services.three_mf_service import analyze_3mf


def test_analyze_3mf_extracts_geometry_and_ignores_foreign_printer_settings(tmp_path: Path) -> None:
    path = tmp_path / "foreign.3mf"
    _write_3mf(
        path,
        metadata="""
    <metadata name="Application">Other Slicer</metadata>
    <metadata name="Printer">Anycubic Kobra 2 Pro 0.4 nozzle</metadata>
""",
    )

    analysis = analyze_3mf(path)

    assert analysis.file_type == "3MF"
    assert analysis.dimensions_mm == (10.0, 10.0, 10.0)
    assert analysis.triangle_count == 12
    assert analysis.ignored_external_settings is True
    assert any("Kobra 2 Pro" in name for name in analysis.embedded_printer_names)
    assert any(issue.code == "ignored_3mf_settings" for issue in analysis.issues)


def test_model_import_blocks_gcode(tmp_path: Path) -> None:
    gcode = tmp_path / "unsafe.gcode"
    gcode.write_text("G28\n", encoding="utf-8")

    try:
        analyze_model(gcode)
    except ModelImportError as exc:
        assert "G-code externo foi bloqueado" in str(exc)
    else:
        raise AssertionError("G-code externo deveria ser bloqueado")


def _write_3mf(path: Path, metadata: str = "") -> None:
    model = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  {metadata}
  <resources>
    <object id="1" type="model">
      <mesh>
        <vertices>
          <vertex x="0" y="0" z="0"/>
          <vertex x="10" y="0" z="0"/>
          <vertex x="10" y="10" z="0"/>
          <vertex x="0" y="10" z="0"/>
          <vertex x="0" y="0" z="10"/>
          <vertex x="10" y="0" z="10"/>
          <vertex x="10" y="10" z="10"/>
          <vertex x="0" y="10" z="10"/>
        </vertices>
        <triangles>
          <triangle v1="0" v2="2" v3="1"/>
          <triangle v1="0" v2="3" v3="2"/>
          <triangle v1="4" v2="5" v3="6"/>
          <triangle v1="4" v2="6" v3="7"/>
          <triangle v1="0" v2="1" v3="5"/>
          <triangle v1="0" v2="5" v3="4"/>
          <triangle v1="1" v2="2" v3="6"/>
          <triangle v1="1" v2="6" v3="5"/>
          <triangle v1="2" v2="3" v3="7"/>
          <triangle v1="2" v2="7" v3="6"/>
          <triangle v1="3" v2="0" v3="4"/>
          <triangle v1="3" v2="4" v3="7"/>
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1"/>
  </build>
</model>
"""
    with ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>""")
        archive.writestr("3D/3dmodel.model", model)
