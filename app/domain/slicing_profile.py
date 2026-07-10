from dataclasses import dataclass


@dataclass(frozen=True)
class UserChoices:
    material: str
    strength: str
    quality: str
    priority: str
    supports_allowed: bool


@dataclass(frozen=True)
class SlicingProfile:
    printer: str
    material: str
    nozzle_temp_c: int
    bed_temp_c: int
    fan_percent: int
    layer_height_mm: float
    line_width_mm: float
    walls: int
    infill_percent: int
    infill_pattern: str
    top_bottom_layers: int
    speed_mm_s: int
    brim: bool
    supports: bool
    warnings: tuple[str, ...]

