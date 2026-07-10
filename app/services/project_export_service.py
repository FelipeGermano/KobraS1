from __future__ import annotations

import json
import zipfile
from dataclasses import asdict
from pathlib import Path
from xml.sax.saxutils import escape

import trimesh

from app.domain.model_analysis import ModelAnalysis
from app.domain.slicing_profile import SlicingProfile, UserChoices
from app.services.mesh_validation_service import mesh_from_loaded_geometry
from app.services.report_service import build_summary, to_json_safe


class ProjectExportError(ValueError):
    """Raised when a slicer project cannot be exported."""


def export_recommended_3mf(
    source_path: str | Path,
    output_path: str | Path,
    analysis: ModelAnalysis,
    choices: UserChoices,
    profile: SlicingProfile,
) -> Path:
    source = Path(source_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    settings = _build_project_settings(profile)
    summary = build_summary(analysis, choices, profile)

    if source.suffix.lower() == ".3mf":
        _copy_3mf_with_metadata(source, output, settings, summary)
    elif source.suffix.lower() == ".stl":
        _write_3mf_from_stl(source, output, settings, summary)
    else:
        raise ProjectExportError("A exportacao de projeto aceita somente STL ou 3MF.")

    return output


def _copy_3mf_with_metadata(
    source: Path,
    output: Path,
    settings: dict[str, object],
    summary: dict,
) -> None:
    try:
        with zipfile.ZipFile(source, "r") as src, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as dst:
            skipped = {"Metadata/project_settings.config", "Metadata/kobra_s1_summary.json", "Metadata/slice_info.config"}
            for item in src.infolist():
                name = item.filename
                if name in skipped:
                    continue
                dst.writestr(item, src.read(name))
            _write_metadata_files(dst, settings, summary)
    except zipfile.BadZipFile as exc:
        raise ProjectExportError(f"3MF invalido ou corrompido: {exc}") from exc


def _write_3mf_from_stl(
    source: Path,
    output: Path,
    settings: dict[str, object],
    summary: dict,
) -> None:
    try:
        loaded = trimesh.load(source, force=None, process=False)
        mesh = mesh_from_loaded_geometry(loaded)
    except BaseException as exc:
        raise ProjectExportError(f"Nao foi possivel converter STL para 3MF: {exc}") from exc

    model_xml = _mesh_to_3mf_model(mesh, source.stem)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml())
        archive.writestr("3D/3dmodel.model", model_xml)
        archive.writestr("_rels/.rels", _root_relationships_xml())
        _write_metadata_files(archive, settings, summary)


def _write_metadata_files(archive: zipfile.ZipFile, settings: dict[str, object], summary: dict) -> None:
    archive.writestr(
        "Metadata/project_settings.config",
        json.dumps(to_json_safe(settings), ensure_ascii=False, indent=2),
    )
    archive.writestr(
        "Metadata/kobra_s1_summary.json",
        json.dumps(to_json_safe(summary), ensure_ascii=False, indent=2),
    )
    archive.writestr("Metadata/slice_info.config", _slice_info_xml())


def _build_project_settings(profile: SlicingProfile) -> dict[str, object]:
    return {
        "type": "process",
        "from": "Kobra S1 Assistant",
        "name": f"Kobra S1 Assistant - {profile.material}",
        "printer_settings_id": "Anycubic Kobra S1 0.4 nozzle",
        "printer_model": "Anycubic Kobra S1",
        "printer_variant": "0.4",
        "nozzle_diameter": ["0.4"],
        "printable_area": ["0x0", "250x0", "250x250", "0x250"],
        "printable_height": "250",
        "gcode_flavor": "klipper",
        "compatible_printers": ["Anycubic Kobra S1 0.4 nozzle"],
        "filament_type": [profile.material],
        "filament_settings_id": [f"Kobra S1 Assistant {profile.material}"],
        "nozzle_temperature": [str(profile.nozzle_temp_c)],
        "nozzle_temperature_initial_layer": [str(profile.nozzle_temp_c)],
        "bed_temperature": [str(profile.bed_temp_c)],
        "bed_temperature_initial_layer": [str(profile.bed_temp_c)],
        "fan_max_speed": [str(profile.fan_percent)],
        "fan_min_speed": [str(min(profile.fan_percent, 40))],
        "layer_height": _number(profile.layer_height_mm),
        "initial_layer_print_height": _number(max(profile.layer_height_mm, 0.2)),
        "line_width": _number(profile.line_width_mm),
        "wall_loops": str(profile.walls),
        "sparse_infill_density": f"{profile.infill_percent}%",
        "sparse_infill_pattern": profile.infill_pattern.lower(),
        "top_shell_layers": str(profile.top_bottom_layers),
        "bottom_shell_layers": str(profile.top_bottom_layers),
        "enable_support": "1" if profile.supports else "0",
        "support_type": "tree(auto)" if profile.supports else "normal(auto)",
        "support_threshold_angle": "30",
        "brim_type": "auto_brim" if profile.brim else "no_brim",
        "brim_width": "5" if profile.brim else "0",
        "outer_wall_speed": str(max(30, int(profile.speed_mm_s * 0.6))),
        "inner_wall_speed": str(profile.speed_mm_s),
        "sparse_infill_speed": str(profile.speed_mm_s),
        "top_surface_speed": str(max(30, int(profile.speed_mm_s * 0.5))),
        "kobra_s1_assistant_summary": json.dumps(to_json_safe(asdict(profile)), ensure_ascii=False),
    }


def _mesh_to_3mf_model(mesh: trimesh.Trimesh, name: str) -> str:
    vertices = "\n".join(
        f'          <vertex x="{vertex[0]:.8g}" y="{vertex[1]:.8g}" z="{vertex[2]:.8g}"/>'
        for vertex in mesh.vertices
    )
    triangles = "\n".join(
        f'          <triangle v1="{face[0]}" v2="{face[1]}" v3="{face[2]}"/>'
        for face in mesh.faces
    )
    safe_name = escape(name)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <metadata name="Application">Kobra S1 Assistant</metadata>
  <resources>
    <object id="1" type="model" name="{safe_name}">
      <mesh>
        <vertices>
{vertices}
        </vertices>
        <triangles>
{triangles}
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1"/>
  </build>
</model>
"""


def _content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
  <Default Extension="config" ContentType="application/octet-stream"/>
  <Default Extension="json" ContentType="application/json"/>
</Types>
"""


def _root_relationships_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""


def _slice_info_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<config>
  <header>
    <header_item key="X-Kobra-S1-Assistant" value="recommended-profile"/>
  </header>
</config>
"""


def _number(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")
