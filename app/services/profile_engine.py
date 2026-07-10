from app.domain.material import MATERIALS, MaterialProfile
from app.domain.model_analysis import ModelAnalysis
from app.domain.printer import KOBRA_S1, PrinterProfile
from app.domain.slicing_profile import SlicingProfile, UserChoices
from app.services.config_service import load_json_config


DEFAULT_STRENGTH_RULES = {
    "Decorativa": {"walls": 2, "infill": 8, "top_bottom": 3},
    "Leve": {"walls": 3, "infill": 12, "top_bottom": 4},
    "Uso comum": {"walls": 3, "infill": 15, "top_bottom": 4},
    "Resistente": {"walls": 4, "infill": 25, "top_bottom": 5},
    "Muito resistente": {"walls": 6, "infill": 35, "top_bottom": 6},
}

DEFAULT_QUALITY_RULES = {
    "Rapida": 0.28,
    "Normal": 0.20,
    "Detalhada": 0.16,
    "Muito detalhada": 0.12,
}

PRIORITIES = ["equilibrio", "economia de material", "resistencia", "qualidade visual", "velocidade"]
PURPOSES = ["decorativa", "prototipo", "uso comum", "funcional", "externo", "flexivel"]
ENVIRONMENTS = ["interno", "externo", "umido", "calor moderado"]
STRESS_DIRECTIONS = ["nao informado", "vertical", "horizontal", "torcao", "impacto"]

_process_config = load_json_config(
    "processes/strength_quality.json",
    {"strength": DEFAULT_STRENGTH_RULES, "quality": DEFAULT_QUALITY_RULES},
)
STRENGTH_RULES = _process_config.get("strength", DEFAULT_STRENGTH_RULES)
QUALITY_RULES = _process_config.get("quality", DEFAULT_QUALITY_RULES)


def build_profile(
    choices: UserChoices,
    analysis: ModelAnalysis,
    printer: PrinterProfile = KOBRA_S1,
) -> SlicingProfile:
    material = _material_profile(choices.material)
    if material is None:
        raise ValueError(f"Material desconhecido: {choices.material}")

    strength = STRENGTH_RULES.get(choices.strength)
    if strength is None:
        raise ValueError(f"Nivel de resistencia desconhecido: {choices.strength}")

    layer_height = QUALITY_RULES.get(choices.quality)
    if layer_height is None:
        raise ValueError(f"Nivel de qualidade desconhecido: {choices.quality}")
    layer_height = float(layer_height)
    _validate_choices(choices, printer)

    walls = int(strength["walls"])
    infill = int(strength.get("infill", strength.get("infill_percent", 15)))
    top_bottom_layers = int(strength.get("top_bottom", strength.get("top_bottom_layers", 4)))
    speed = material.base_speed_mm_s
    warnings = list(material.warnings)
    reasons = [
        f"Material {material.name}: {material.nozzle_temp_c} C no bico e {material.bed_temp_c} C na mesa.",
        f"Resistencia {choices.strength}: {walls} paredes, {infill}% de preenchimento.",
        f"Qualidade {choices.quality}: camada de {layer_height:.2f} mm.",
    ]

    if choices.priority == "resistencia":
        walls += 1
        infill = min(45, infill + 8)
        speed = int(speed * 0.85)
        reasons.append("Prioridade em resistencia aumentou paredes/preenchimento e reduziu velocidade.")
    elif choices.priority == "velocidade":
        layer_height = min(0.28, layer_height + 0.04)
        speed = int(speed * 1.15)
        reasons.append("Prioridade em velocidade aumentou camada e velocidade base.")
    elif choices.priority == "qualidade visual":
        layer_height = min(layer_height, 0.16)
        speed = int(speed * 0.85)
        reasons.append("Prioridade visual reduziu camada/velocidade para acabamento.")
    elif choices.priority == "economia de material":
        infill = max(8, infill - 5)
        reasons.append("Economia de material reduziu preenchimento dentro do limite seguro.")

    if choices.purpose in {"funcional", "externo"}:
        walls = max(walls, 4)
        infill = max(infill, 20)
        reasons.append("Finalidade funcional/externa elevou resistencia minima.")
    if choices.needs_flexibility and material.name != "TPU":
        warnings.append("Flexibilidade foi solicitada; TPU costuma ser mais adequado que este material.")
    if choices.needs_flexibility and material.name == "TPU":
        speed = min(speed, 35)
        infill = min(infill, 18)
        reasons.append("TPU/flexibilidade manteve velocidade baixa e preenchimento moderado.")
    if choices.heat_exposure and material.name == "PLA":
        warnings.append("PLA nao e recomendado para calor/sol; considere PETG, ABS ou ASA.")
    if choices.environment == "externo" and material.name not in {"ASA", "PETG"}:
        warnings.append("Uso externo: ASA e PETG tendem a ser escolhas mais seguras.")
    if choices.stress_direction in {"vertical", "impacto"}:
        walls += 1
        reasons.append("Esforco informado aumentou paredes para compensar direcao/carga.")

    supports = choices.supports_allowed and _likely_needs_support(analysis)
    support_style = "tree(auto)" if supports else "nenhum"
    brim, adhesion_type = _adhesion_recommendation(analysis, material)
    if supports:
        reasons.append("Geometria indica balancos; suporte foi habilitado.")
    if brim:
        reasons.append(f"Aderencia recomendada: {adhesion_type}.")

    if not analysis.fits_printer:
        warnings.append("Nao fatie antes de reduzir escala ou dividir o modelo.")
    warnings.extend(analysis.warnings)
    if choices.copies > 1:
        reasons.append(f"Quantidade solicitada: {choices.copies} copias; confirme distribuicao no slicer.")

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
        top_bottom_layers=top_bottom_layers,
        speed_mm_s=speed,
        brim=brim,
        adhesion_type=adhesion_type,
        supports=supports,
        support_style=support_style,
        estimated_weight_g=_estimate_weight(analysis, material, infill),
        estimated_cost_note="Estimativa de peso usa volume do modelo e densidade media; confira no slicer.",
        decision_reasons=tuple(dict.fromkeys(reasons)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def _likely_needs_support(analysis: ModelAnalysis) -> bool:
    return analysis.support_likely or (analysis.height_mm > 80 and min(analysis.width_mm, analysis.depth_mm) < 20)


def _adhesion_recommendation(analysis: ModelAnalysis, material: MaterialProfile) -> tuple[bool, str]:
    large = analysis.height_mm > 120 or max(analysis.width_mm, analysis.depth_mm) > 180
    small_base = analysis.base_contact_area_mm2 <= 100 and max(analysis.dimensions_mm) > 20
    warp_prone = material.name in {"ABS", "ASA", "PETG", "TPU"}
    if large or small_base or warp_prone:
        return True, "brim"
    return False, "sem brim"


def _estimate_weight(analysis: ModelAnalysis, material: MaterialProfile, infill_percent: int) -> float | None:
    if analysis.volume_mm3 <= 0:
        return None
    density = {
        "PLA": 1.24,
        "PETG": 1.27,
        "ABS": 1.04,
        "ASA": 1.07,
        "TPU": 1.20,
    }.get(material.name)
    if density is None:
        return None
    shell_factor = 0.22
    solid_fraction = min(0.95, shell_factor + (infill_percent / 100.0) * 0.78)
    return round(analysis.volume_mm3 / 1000.0 * density * solid_fraction, 2)


def _validate_choices(choices: UserChoices, printer: PrinterProfile) -> None:
    if choices.priority not in PRIORITIES:
        raise ValueError(f"Prioridade desconhecida: {choices.priority}")
    if choices.purpose not in PURPOSES:
        raise ValueError(f"Finalidade desconhecida: {choices.purpose}")
    if choices.environment not in ENVIRONMENTS:
        raise ValueError(f"Ambiente desconhecido: {choices.environment}")
    if choices.stress_direction not in STRESS_DIRECTIONS:
        raise ValueError(f"Direcao de esforco desconhecida: {choices.stress_direction}")
    if choices.copies < 1:
        raise ValueError("Quantidade de copias deve ser pelo menos 1.")
    if abs(choices.nozzle_diameter_mm - printer.nozzle_diameter_mm) > 0.001:
        raise ValueError("O MVP aceita apenas o bico de 0,4 mm da Kobra S1.")


def _material_profile(name: str) -> MaterialProfile | None:
    config = load_json_config("materials/materials.json")
    raw = config.get(name)
    fallback = MATERIALS.get(name)
    if raw is None:
        return fallback
    return MaterialProfile(
        name=name,
        nozzle_temp_c=int(raw.get("nozzle_temp_c", fallback.nozzle_temp_c if fallback else 210)),
        bed_temp_c=int(raw.get("bed_temp_c", fallback.bed_temp_c if fallback else 60)),
        fan_percent=int(raw.get("fan_percent", fallback.fan_percent if fallback else 60)),
        base_speed_mm_s=fallback.base_speed_mm_s if fallback else 80,
        warnings=fallback.warnings if fallback else (),
    )
