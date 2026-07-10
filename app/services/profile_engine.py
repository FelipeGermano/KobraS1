from app.domain.material import MATERIALS
from app.domain.model_analysis import ModelAnalysis
from app.domain.printer import KOBRA_S1, PrinterProfile
from app.domain.slicing_profile import SlicingProfile, UserChoices


STRENGTH_RULES = {
    "Decorativa": {"walls": 2, "infill": 8, "top_bottom": 3},
    "Leve": {"walls": 3, "infill": 12, "top_bottom": 4},
    "Uso comum": {"walls": 3, "infill": 15, "top_bottom": 4},
    "Resistente": {"walls": 4, "infill": 25, "top_bottom": 5},
    "Muito resistente": {"walls": 6, "infill": 35, "top_bottom": 6},
}

QUALITY_RULES = {
    "Rapida": 0.28,
    "Normal": 0.20,
    "Detalhada": 0.16,
    "Muito detalhada": 0.12,
}


def build_profile(
    choices: UserChoices,
    analysis: ModelAnalysis,
    printer: PrinterProfile = KOBRA_S1,
) -> SlicingProfile:
    material = MATERIALS.get(choices.material)
    if material is None:
        raise ValueError(f"Material desconhecido: {choices.material}")

    strength = STRENGTH_RULES.get(choices.strength)
    if strength is None:
        raise ValueError(f"Nivel de resistencia desconhecido: {choices.strength}")

    layer_height = QUALITY_RULES.get(choices.quality)
    if layer_height is None:
        raise ValueError(f"Nivel de qualidade desconhecido: {choices.quality}")

    walls = int(strength["walls"])
    infill = int(strength["infill"])
    speed = material.base_speed_mm_s
    warnings = list(material.warnings)

    if choices.priority == "resistencia":
        walls += 1
        infill = min(45, infill + 8)
        speed = int(speed * 0.85)
    elif choices.priority == "velocidade":
        layer_height = min(0.28, layer_height + 0.04)
        speed = int(speed * 1.15)
    elif choices.priority == "qualidade visual":
        layer_height = min(layer_height, 0.16)
        speed = int(speed * 0.85)
    elif choices.priority == "economia de material":
        infill = max(8, infill - 5)

    supports = choices.supports_allowed and _likely_needs_support(analysis)
    brim = analysis.height_mm > 120 or max(analysis.width_mm, analysis.depth_mm) > 180

    if not analysis.fits_printer:
        warnings.append("Nao fatie antes de reduzir escala ou dividir o modelo.")
    warnings.extend(analysis.warnings)

    return SlicingProfile(
        printer=printer.name,
        material=material.name,
        nozzle_temp_c=material.nozzle_temp_c,
        bed_temp_c=material.bed_temp_c,
        fan_percent=material.fan_percent,
        layer_height_mm=round(layer_height, 2),
        line_width_mm=round(printer.nozzle_diameter_mm * 1.05, 2),
        walls=walls,
        infill_percent=infill,
        infill_pattern="Gyroid",
        top_bottom_layers=int(strength["top_bottom"]),
        speed_mm_s=speed,
        brim=brim,
        supports=supports,
        warnings=tuple(dict.fromkeys(warnings)),
    )


def _likely_needs_support(analysis: ModelAnalysis) -> bool:
    return analysis.height_mm > 80 and min(analysis.width_mm, analysis.depth_mm) < 20

