from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ModelAnalysis:
    source_path: Path
    file_type: str
    dimensions_mm: tuple[float, float, float]
    volume_mm3: float
    surface_area_mm2: float
    triangle_count: int
    is_watertight: bool | None
    fits_printer: bool
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def width_mm(self) -> float:
        return self.dimensions_mm[0]

    @property
    def depth_mm(self) -> float:
        return self.dimensions_mm[1]

    @property
    def height_mm(self) -> float:
        return self.dimensions_mm[2]

