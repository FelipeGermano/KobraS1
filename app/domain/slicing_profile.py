from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationPlan:
    temperature_tower: tuple[int, ...]
    flow_ratio_steps: tuple[float, ...]
    pressure_advance_steps: tuple[float, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class StrengthConsumptionOption:
    strength: str
    walls: int
    infill_percent: int
    estimated_weight_g: float | None
    estimated_cost: float | None
    note: str


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
    custom_infill_enabled: bool = False
    custom_infill_percent: int | None = None
    filament_price_per_kg: float | None = None
    enable_temperature_calibration: bool = False
    enable_flow_calibration: bool = False
    enable_pressure_advance_calibration: bool = False


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
    estimated_total_weight_g: float | None
    estimated_cost: float | None
    estimated_cost_note: str
    calibration_plan: CalibrationPlan
    strength_consumption_options: tuple[StrengthConsumptionOption, ...]
    decision_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
