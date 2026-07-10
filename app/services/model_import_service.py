from __future__ import annotations

from pathlib import Path

from app.domain.model_analysis import ModelAnalysis
from app.domain.printer import KOBRA_S1, PrinterProfile
from app.services.stl_service import StlReadError, analyze_stl
from app.services.three_mf_service import ThreeMfReadError, analyze_3mf


class ModelImportError(ValueError):
    """Raised when a model file is unsupported or unsafe."""


def analyze_model(path: str | Path, printer: PrinterProfile = KOBRA_S1) -> ModelAnalysis:
    source = Path(path)
    extension = source.suffix.lower()
    if extension in {".gcode", ".gco", ".gc"}:
        raise ModelImportError("G-code externo foi bloqueado. Importe STL ou 3MF e gere um novo arquivo seguro.")
    if extension == ".stl":
        try:
            return analyze_stl(source, printer)
        except StlReadError as exc:
            raise ModelImportError(str(exc)) from exc
    if extension == ".3mf":
        try:
            return analyze_3mf(source, printer)
        except ThreeMfReadError as exc:
            raise ModelImportError(str(exc)) from exc
    raise ModelImportError("Formato nao suportado. Use arquivos STL ou 3MF.")
