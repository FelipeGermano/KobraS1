from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class MeshIssue:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ModelAnalysis:
    source_path: Path
    file_type: str
    dimensions_mm: tuple[float, float, float]
    volume_mm3: float
    surface_area_mm2: float
    triangle_count: int
    component_count: int
    is_watertight: bool
    is_winding_consistent: bool
    is_volume: bool
    degenerate_face_count: int
    non_manifold_edge_count: int
    inverted_normal_likely: bool
    thin_wall_warning: bool
    base_contact_area_mm2: float
    support_likely: bool
    scale_suspect: bool
    fits_printer: bool
    embedded_printer_names: tuple[str, ...] = field(default_factory=tuple)
    ignored_external_settings: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
    issues: tuple[MeshIssue, ...] = field(default_factory=tuple)
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
