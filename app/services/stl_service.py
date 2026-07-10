from __future__ import annotations

import math
import struct
from pathlib import Path

from app.domain.model_analysis import ModelAnalysis
from app.domain.printer import KOBRA_S1, PrinterProfile

Vector = tuple[float, float, float]
Triangle = tuple[Vector, Vector, Vector]


class StlReadError(ValueError):
    """Raised when an STL file cannot be read."""


def analyze_stl(path: str | Path, printer: PrinterProfile = KOBRA_S1) -> ModelAnalysis:
    source = Path(path)
    if source.suffix.lower() != ".stl":
        raise StlReadError("Apenas arquivos STL sao aceitos por este importador.")
    if not source.exists():
        raise StlReadError(f"Arquivo nao encontrado: {source}")

    triangles = _read_stl_triangles(source)
    if not triangles:
        raise StlReadError("O STL nao contem triangulos validos.")

    points = [point for triangle in triangles for point in triangle]
    mins = tuple(min(point[index] for point in points) for index in range(3))
    maxs = tuple(max(point[index] for point in points) for index in range(3))
    dimensions = tuple(maxs[index] - mins[index] for index in range(3))
    surface_area = sum(_triangle_area(*triangle) for triangle in triangles)
    volume = abs(sum(_signed_tetra_volume(*triangle) for triangle in triangles))
    fits = printer.fits(dimensions)
    warnings = _build_warnings(dimensions, volume, fits)

    return ModelAnalysis(
        source_path=source,
        file_type="STL",
        dimensions_mm=dimensions,
        volume_mm3=volume,
        surface_area_mm2=surface_area,
        triangle_count=len(triangles),
        is_watertight=None,
        fits_printer=fits,
        warnings=warnings,
    )


def _read_stl_triangles(path: Path) -> list[Triangle]:
    data = path.read_bytes()
    if len(data) < 84:
        raise StlReadError("Arquivo STL muito pequeno ou corrompido.")

    binary_triangles = _try_read_binary(data)
    if binary_triangles is not None:
        return binary_triangles

    return _read_ascii(data)


def _try_read_binary(data: bytes) -> list[Triangle] | None:
    triangle_count = struct.unpack("<I", data[80:84])[0]
    expected_size = 84 + triangle_count * 50
    if expected_size != len(data):
        return None

    triangles: list[Triangle] = []
    offset = 84
    for _ in range(triangle_count):
        offset += 12
        vertices = []
        for _vertex_index in range(3):
            vertices.append(struct.unpack("<fff", data[offset : offset + 12]))
            offset += 12
        offset += 2
        triangles.append((vertices[0], vertices[1], vertices[2]))
    return triangles


def _read_ascii(data: bytes) -> list[Triangle]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("latin-1")

    vertices: list[Vector] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("vertex "):
            continue
        parts = line.split()
        if len(parts) != 4:
            raise StlReadError("Linha vertex invalida em STL ASCII.")
        vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))

    if len(vertices) % 3 != 0:
        raise StlReadError("STL ASCII possui vertices incompletos.")

    return [
        (vertices[index], vertices[index + 1], vertices[index + 2])
        for index in range(0, len(vertices), 3)
    ]


def _triangle_area(a: Vector, b: Vector, c: Vector) -> float:
    ab = _sub(b, a)
    ac = _sub(c, a)
    cross = _cross(ab, ac)
    return 0.5 * math.sqrt(_dot(cross, cross))


def _signed_tetra_volume(a: Vector, b: Vector, c: Vector) -> float:
    return _dot(a, _cross(b, c)) / 6.0


def _build_warnings(
    dimensions: tuple[float, float, float], volume_mm3: float, fits_printer: bool
) -> tuple[str, ...]:
    warnings: list[str] = []
    if not fits_printer:
        warnings.append("O modelo excede o volume de impressao da Kobra S1.")
    if max(dimensions) < 5:
        warnings.append("Modelo muito pequeno; confirme se a unidade esta em milimetros.")
    if max(dimensions) > 220:
        warnings.append("Modelo grande; confira aderencia, empenamento e orientacao.")
    if volume_mm3 <= 0:
        warnings.append("Volume aproximado zerado; a malha pode estar aberta ou invertida.")
    return tuple(warnings)


def _sub(a: Vector, b: Vector) -> Vector:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a: Vector, b: Vector) -> Vector:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _dot(a: Vector, b: Vector) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

