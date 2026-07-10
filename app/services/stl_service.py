from __future__ import annotations

from pathlib import Path

import trimesh

from app.domain.model_analysis import ModelAnalysis
from app.domain.printer import KOBRA_S1, PrinterProfile
from app.services.mesh_validation_service import (
    MeshAnalysisError,
    analyze_mesh,
    mesh_from_loaded_geometry,
)


class StlReadError(ValueError):
    """Raised when an STL file cannot be read."""


def analyze_stl(path: str | Path, printer: PrinterProfile = KOBRA_S1) -> ModelAnalysis:
    source = Path(path)
    if source.suffix.lower() != ".stl":
        raise StlReadError("Apenas arquivos STL sao aceitos por este importador.")
    if not source.exists():
        raise StlReadError(f"Arquivo nao encontrado: {source}")

    try:
        loaded = trimesh.load(source, force=None, process=False)
        mesh = mesh_from_loaded_geometry(loaded)
        return analyze_mesh(mesh, source, "STL", printer)
    except (MeshAnalysisError, ValueError, OSError) as exc:
        raise StlReadError(f"Nao foi possivel ler o STL: {exc}") from exc
