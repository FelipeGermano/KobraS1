from dataclasses import dataclass


@dataclass(frozen=True)
class UserChoices:
    material: str
    strength: str
    quality: str
    priority: str
    supports_allowed: bool
    purpose: str = "uso comum"
    environment: str = "interno"
    heat_exposure: bool = False
    needs_flexibility: bool = False
    stress_direction: str = "nao informado"
    copies: int = 1
    nozzle_diameter_mm: float = 0.4


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
    adhesion_type: str
    supports: bool
    support_style: str
    estimated_weight_g: float | None
    estimated_cost_note: str
    decision_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
