from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from app.domain.model_analysis import MeshIssue, ModelAnalysis
from app.domain.printer import KOBRA_S1, PrinterProfile


class MeshAnalysisError(ValueError):
    """Raised when geometry cannot be converted into a printable mesh."""


def analyze_mesh(
    mesh: trimesh.Trimesh,
    source_path: str | Path,
    file_type: str,
    printer: PrinterProfile = KOBRA_S1,
    metadata: dict[str, str] | None = None,
    embedded_printer_names: tuple[str, ...] = (),
    ignored_external_settings: bool = False,
) -> ModelAnalysis:
    if mesh.vertices.size == 0 or mesh.faces.size == 0:
        raise MeshAnalysisError("O modelo nao contem geometria triangular valida.")

    mesh = mesh.copy()
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()

    dimensions = _tuple3(mesh.extents)
    fits = printer.fits(dimensions)
    surface_area = float(mesh.area)
    volume = abs(float(mesh.volume)) if mesh.is_watertight else abs(_signed_volume(mesh))
    component_count = _component_count(mesh)
    degenerate_count = int(np.count_nonzero(mesh.area_faces <= 1e-9))
    non_manifold_edges = _non_manifold_edge_count(mesh)
    base_contact_area = _base_contact_area(mesh)
    support_likely = _support_likely(mesh)
    scale_suspect = _scale_suspect(dimensions)
    thin_wall_warning = min((size for size in dimensions if size > 0), default=0.0) < 0.8
    inverted_likely = bool(mesh.is_watertight and float(mesh.volume) < 0)

    issues = _build_issues(
        mesh=mesh,
        fits=fits,
        dimensions=dimensions,
        volume=volume,
        component_count=component_count,
        degenerate_count=degenerate_count,
        non_manifold_edges=non_manifold_edges,
        base_contact_area=base_contact_area,
        support_likely=support_likely,
        scale_suspect=scale_suspect,
        thin_wall_warning=thin_wall_warning,
        inverted_likely=inverted_likely,
        ignored_external_settings=ignored_external_settings,
        embedded_printer_names=embedded_printer_names,
    )

    return ModelAnalysis(
        source_path=Path(source_path),
        file_type=file_type,
        dimensions_mm=dimensions,
        volume_mm3=volume,
        surface_area_mm2=surface_area,
        triangle_count=int(len(mesh.faces)),
        component_count=component_count,
        is_watertight=bool(mesh.is_watertight),
        is_winding_consistent=bool(mesh.is_winding_consistent),
        is_volume=bool(mesh.is_volume),
        degenerate_face_count=degenerate_count,
        non_manifold_edge_count=non_manifold_edges,
        inverted_normal_likely=inverted_likely,
        thin_wall_warning=thin_wall_warning,
        base_contact_area_mm2=base_contact_area,
        support_likely=support_likely,
        scale_suspect=scale_suspect,
        fits_printer=fits,
        embedded_printer_names=embedded_printer_names,
        ignored_external_settings=ignored_external_settings,
        metadata=metadata or {},
        issues=tuple(issues),
        warnings=tuple(issue.message for issue in issues),
    )


def combine_meshes(meshes: list[trimesh.Trimesh]) -> trimesh.Trimesh:
    valid = [mesh for mesh in meshes if mesh.vertices.size and mesh.faces.size]
    if not valid:
        raise MeshAnalysisError("Nenhuma malha valida foi encontrada.")
    if len(valid) == 1:
        return valid[0]
    return trimesh.util.concatenate(valid)


def mesh_from_loaded_geometry(geometry: object) -> trimesh.Trimesh:
    if isinstance(geometry, trimesh.Scene):
        meshes = [
            item
            for item in geometry.dump(concatenate=False)
            if isinstance(item, trimesh.Trimesh)
        ]
        return combine_meshes(meshes)
    if isinstance(geometry, trimesh.Trimesh):
        return geometry
    raise MeshAnalysisError("Formato de geometria nao suportado.")


def _tuple3(values: np.ndarray) -> tuple[float, float, float]:
    return (float(values[0]), float(values[1]), float(values[2]))


def _component_count(mesh: trimesh.Trimesh) -> int:
    try:
        return max(1, len(mesh.split(only_watertight=False)))
    except BaseException:
        return 1


def _non_manifold_edge_count(mesh: trimesh.Trimesh) -> int:
    inverse = mesh.edges_unique_inverse
    counts = np.bincount(inverse)
    return int(np.count_nonzero(counts != 2))


def _signed_volume(mesh: trimesh.Trimesh) -> float:
    vertices = mesh.vertices
    faces = mesh.faces
    tri = vertices[faces]
    cross = np.cross(tri[:, 1], tri[:, 2])
    return float(np.einsum("ij,ij->i", tri[:, 0], cross).sum() / 6.0)


def _base_contact_area(mesh: trimesh.Trimesh) -> float:
    min_z = float(mesh.bounds[0][2])
    vertices_z = mesh.vertices[mesh.faces][:, :, 2]
    near_base = np.all(np.isclose(vertices_z, min_z, atol=0.05), axis=1)
    normals_down_or_flat = np.abs(mesh.face_normals[:, 2]) > 0.85
    base_faces = near_base & normals_down_or_flat
    return float(mesh.area_faces[base_faces].sum())


def _support_likely(mesh: trimesh.Trimesh) -> bool:
    if len(mesh.faces) == 0:
        return False
    min_z = float(mesh.bounds[0][2])
    centroids_z = mesh.triangles_center[:, 2]
    above_base = centroids_z > min_z + 0.5
    downward_faces = mesh.face_normals[:, 2] < -0.5
    overhang_area = float(mesh.area_faces[above_base & downward_faces].sum())
    return overhang_area > max(25.0, mesh.area * 0.02)


def _scale_suspect(dimensions: tuple[float, float, float]) -> bool:
    longest = max(dimensions)
    shortest_positive = min((size for size in dimensions if size > 0), default=0.0)
    return longest < 5.0 or shortest_positive > 250.0 or longest > 1000.0


def _build_issues(
    mesh: trimesh.Trimesh,
    fits: bool,
    dimensions: tuple[float, float, float],
    volume: float,
    component_count: int,
    degenerate_count: int,
    non_manifold_edges: int,
    base_contact_area: float,
    support_likely: bool,
    scale_suspect: bool,
    thin_wall_warning: bool,
    inverted_likely: bool,
    ignored_external_settings: bool,
    embedded_printer_names: tuple[str, ...],
) -> list[MeshIssue]:
    issues: list[MeshIssue] = []
    if not fits:
        issues.append(MeshIssue("model_too_large", "error", "O modelo excede o volume de impressao da Kobra S1."))
    if not mesh.is_watertight:
        issues.append(MeshIssue("open_mesh", "warning", "A malha parece aberta; o volume pode ser apenas aproximado."))
    if non_manifold_edges:
        issues.append(MeshIssue("non_manifold_edges", "warning", f"Foram detectadas {non_manifold_edges} arestas nao-manifold."))
    if degenerate_count:
        issues.append(MeshIssue("degenerate_faces", "info", f"Foram detectadas {degenerate_count} faces degeneradas."))
    if not mesh.is_winding_consistent:
        issues.append(MeshIssue("inconsistent_winding", "warning", "A orientacao de algumas faces pode estar inconsistente."))
    if inverted_likely:
        issues.append(MeshIssue("inverted_normals", "warning", "As normais podem estar invertidas."))
    if component_count > 1:
        issues.append(MeshIssue("multiple_components", "info", f"O arquivo contem {component_count} componentes separados."))
    if thin_wall_warning:
        issues.append(MeshIssue("thin_dimension", "warning", "Ha dimensao menor que 0,8 mm; confira paredes finas no fatiador."))
    if base_contact_area <= 1.0 and max(dimensions) > 5:
        issues.append(MeshIssue("small_base_contact", "warning", "A area de contato com a mesa parece pequena."))
    if support_likely:
        issues.append(MeshIssue("supports_likely", "info", "Ha faces em balanco; suportes podem ser necessarios."))
    if scale_suspect:
        issues.append(MeshIssue("scale_suspect", "warning", "A escala parece suspeita; confirme se o arquivo esta em milimetros."))
    if volume <= 0:
        issues.append(MeshIssue("zero_volume", "warning", "Volume aproximado zerado; a malha pode estar aberta ou plana."))
    if ignored_external_settings:
        printers = ", ".join(embedded_printer_names) or "impressora nao identificada"
        issues.append(MeshIssue("ignored_3mf_settings", "info", f"Configuracoes 3MF embutidas foram ignoradas ({printers})."))
    return issues
