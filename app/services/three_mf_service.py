from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import numpy as np
import trimesh

from app.domain.model_analysis import ModelAnalysis
from app.domain.printer import KOBRA_S1, PrinterProfile
from app.services.mesh_validation_service import MeshAnalysisError, analyze_mesh, combine_meshes


class ThreeMfReadError(ValueError):
    """Raised when a 3MF file cannot be read safely."""


def analyze_3mf(path: str | Path, printer: PrinterProfile = KOBRA_S1) -> ModelAnalysis:
    source = Path(path)
    if source.suffix.lower() != ".3mf":
        raise ThreeMfReadError("Apenas arquivos 3MF sao aceitos por este importador.")
    if not source.exists():
        raise ThreeMfReadError(f"Arquivo nao encontrado: {source}")

    try:
        with zipfile.ZipFile(source) as archive:
            model_name = _find_model_part(archive)
            root = ElementTree.fromstring(archive.read(model_name))
    except (zipfile.BadZipFile, ElementTree.ParseError, KeyError) as exc:
        raise ThreeMfReadError(f"3MF invalido ou corrompido: {exc}") from exc

    try:
        metadata = _extract_metadata(root)
        meshes_by_id = _extract_object_meshes(root)
        build_meshes = _extract_build_meshes(root, meshes_by_id)
        combined = combine_meshes(build_meshes or list(meshes_by_id.values()))
        printer_names = _detect_printer_names(root, metadata)
        ignored_settings = bool(printer_names or _has_slicer_settings(root, metadata))
        return analyze_mesh(
            combined,
            source,
            "3MF",
            printer,
            metadata=metadata,
            embedded_printer_names=printer_names,
            ignored_external_settings=ignored_settings,
        )
    except (MeshAnalysisError, ValueError) as exc:
        raise ThreeMfReadError(f"Nao foi possivel extrair geometria do 3MF: {exc}") from exc


def _find_model_part(archive: zipfile.ZipFile) -> str:
    names = archive.namelist()
    if "3D/3dmodel.model" in names:
        return "3D/3dmodel.model"
    candidates = [name for name in names if name.lower().endswith(".model")]
    if not candidates:
        raise KeyError("Nenhum arquivo .model encontrado no 3MF.")
    return candidates[0]


def _extract_metadata(root: ElementTree.Element) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for item in root.findall(".//{*}metadata"):
        name = item.attrib.get("name")
        if name:
            metadata[name] = (item.text or "").strip()
    return metadata


def _extract_object_meshes(root: ElementTree.Element) -> dict[str, trimesh.Trimesh]:
    meshes: dict[str, trimesh.Trimesh] = {}
    for obj in root.findall(".//{*}object"):
        object_id = obj.attrib.get("id")
        mesh_node = obj.find("{*}mesh")
        if not object_id or mesh_node is None:
            continue

        vertices = [
            (
                float(vertex.attrib["x"]),
                float(vertex.attrib["y"]),
                float(vertex.attrib["z"]),
            )
            for vertex in mesh_node.findall(".//{*}vertex")
        ]
        faces = [
            (
                int(triangle.attrib["v1"]),
                int(triangle.attrib["v2"]),
                int(triangle.attrib["v3"]),
            )
            for triangle in mesh_node.findall(".//{*}triangle")
        ]
        if vertices and faces:
            meshes[object_id] = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    if not meshes:
        raise MeshAnalysisError("O 3MF nao contem objetos de malha triangulada.")
    return meshes


def _extract_build_meshes(
    root: ElementTree.Element, meshes_by_id: dict[str, trimesh.Trimesh]
) -> list[trimesh.Trimesh]:
    build_meshes: list[trimesh.Trimesh] = []
    for item in root.findall(".//{*}build/{*}item"):
        object_id = item.attrib.get("objectid")
        if object_id not in meshes_by_id:
            continue
        mesh = meshes_by_id[object_id].copy()
        transform = _parse_transform(item.attrib.get("transform"))
        if transform is not None:
            mesh.apply_transform(transform)
        build_meshes.append(mesh)
    return build_meshes


def _parse_transform(value: str | None) -> np.ndarray | None:
    if not value:
        return None
    parts = [float(part) for part in value.split()]
    if len(parts) != 12:
        return None
    return np.array(
        [
            [parts[0], parts[3], parts[6], parts[9]],
            [parts[1], parts[4], parts[7], parts[10]],
            [parts[2], parts[5], parts[8], parts[11]],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


def _detect_printer_names(root: ElementTree.Element, metadata: dict[str, str]) -> tuple[str, ...]:
    haystack = " ".join(
        list(metadata.values())
        + [value for element in root.iter() for value in element.attrib.values()]
    )
    matches = sorted(set(re.findall(r"Anycubic\s+Kobra\s+[A-Za-z0-9 ]+", haystack, flags=re.IGNORECASE)))
    return tuple(matches)


def _has_slicer_settings(root: ElementTree.Element, metadata: dict[str, str]) -> bool:
    text = " ".join(list(metadata.keys()) + list(metadata.values()))
    if re.search(r"slicer|printer|machine|filament|nozzle|gcode", text, flags=re.IGNORECASE):
        return True
    setting_names = {"config", "settings", "slice", "slicer", "plate", "filament", "printer"}
    return any(_local_name(element.tag).lower() in setting_names for element in root.iter())


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
