from __future__ import annotations

import re
from pathlib import Path

from app.domain.printer import KOBRA_S1, PrinterProfile
from app.domain.slicer import GcodeValidation
from app.domain.slicing_profile import SlicingProfile


class GcodeValidationError(ValueError):
    """Raised when a G-code file cannot be read."""


def validate_gcode(
    path: str | Path,
    profile: SlicingProfile,
    printer: PrinterProfile = KOBRA_S1,
) -> GcodeValidation:
    source = Path(path)
    if not source.exists():
        raise GcodeValidationError("Arquivo G-code nao encontrado.")

    temps_nozzle: list[int] = []
    temps_bed: list[int] = []
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    estimated_time = None
    filament_used = None

    for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith(";"):
            estimated_time = _metadata_value(stripped, estimated_time, ["estimated printing time", "print_time", "time"])
            filament_used = _metadata_value(stripped, filament_used, ["filament used", "filament_used", "filament"])
            continue
        nozzle = re.search(r"\bM10[49]\s+S(\d+)", stripped)
        bed = re.search(r"\bM1(?:40|90)\s+S(\d+)", stripped)
        if nozzle:
            temps_nozzle.append(int(nozzle.group(1)))
        if bed:
            temps_bed.append(int(bed.group(1)))
        if stripped.startswith(("G0", "G1")):
            _append_axis(stripped, "X", xs)
            _append_axis(stripped, "Y", ys)
            _append_axis(stripped, "Z", zs)

    bounds = _bounds(xs, ys, zs)
    warnings = _warnings(bounds, temps_nozzle, temps_bed, profile, printer)
    return GcodeValidation(
        path=source,
        is_valid=not warnings,
        bounds_mm=bounds,
        nozzle_temps_c=tuple(sorted(set(temps_nozzle))),
        bed_temps_c=tuple(sorted(set(temps_bed))),
        estimated_time=estimated_time,
        filament_used=filament_used,
        warnings=tuple(warnings),
    )


def _append_axis(line: str, axis: str, values: list[float]) -> None:
    match = re.search(rf"\b{axis}(-?\d+(?:\.\d+)?)", line)
    if match:
        values.append(float(match.group(1)))


def _bounds(
    xs: list[float], ys: list[float], zs: list[float]
) -> tuple[float, float, float, float, float, float] | None:
    if not xs and not ys and not zs:
        return None
    return (
        min(xs or [0.0]),
        max(xs or [0.0]),
        min(ys or [0.0]),
        max(ys or [0.0]),
        min(zs or [0.0]),
        max(zs or [0.0]),
    )


def _warnings(
    bounds: tuple[float, float, float, float, float, float] | None,
    nozzle_temps: list[int],
    bed_temps: list[int],
    profile: SlicingProfile,
    printer: PrinterProfile,
) -> list[str]:
    warnings: list[str] = []
    if bounds is not None:
        min_x, max_x, min_y, max_y, min_z, max_z = bounds
        width, depth, height = printer.build_volume_mm
        purge_margin_mm = 30.0
        if (
            min_x < -5
            or min_y < -5
            or min_z < -1
            or max_x > width + purge_margin_mm
            or max_y > depth + purge_margin_mm
            or max_z > height + 1
        ):
            warnings.append("Movimentos ultrapassam o volume da Kobra S1.")
    active_nozzle_temps = [temp for temp in nozzle_temps if temp > 0]
    active_bed_temps = [temp for temp in bed_temps if temp > 0]
    if active_nozzle_temps and all(abs(temp - profile.nozzle_temp_c) > 15 for temp in active_nozzle_temps):
        warnings.append("Temperatura de bico do G-code nao corresponde ao perfil.")
    if active_bed_temps and all(abs(temp - profile.bed_temp_c) > 10 for temp in active_bed_temps):
        warnings.append("Temperatura de mesa do G-code nao corresponde ao perfil.")
    if not active_nozzle_temps:
        warnings.append("G-code sem temperatura de bico detectavel.")
    if not active_bed_temps:
        warnings.append("G-code sem temperatura de mesa detectavel.")
    return warnings


def _metadata_value(line: str, current: str | None, keys: list[str]) -> str | None:
    if current is not None:
        return current
    lower = line.lower()
    if not any(key in lower for key in keys):
        return None
    if "=" in line:
        return line.split("=", 1)[1].strip()
    if ":" in line:
        return line.split(":", 1)[1].strip()
    return line.lstrip(";").strip()
