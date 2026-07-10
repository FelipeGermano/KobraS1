from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialProfile:
    name: str
    nozzle_temp_c: int
    bed_temp_c: int
    fan_percent: int
    base_speed_mm_s: int
    warnings: tuple[str, ...]


MATERIALS: dict[str, MaterialProfile] = {
    "PLA": MaterialProfile(
        name="PLA",
        nozzle_temp_c=210,
        bed_temp_c=60,
        fan_percent=80,
        base_speed_mm_s=120,
        warnings=("Nao recomendado para calor elevado ou sol direto.",),
    ),
    "PETG": MaterialProfile(
        name="PETG",
        nozzle_temp_c=240,
        bed_temp_c=75,
        fan_percent=40,
        base_speed_mm_s=80,
        warnings=("Exige filamento seco e pode aderir excessivamente a mesa.",),
    ),
    "ABS": MaterialProfile(
        name="ABS",
        nozzle_temp_c=255,
        bed_temp_c=100,
        fan_percent=15,
        base_speed_mm_s=70,
        warnings=("Usar camara fechada e ambiente ventilado.",),
    ),
    "ASA": MaterialProfile(
        name="ASA",
        nozzle_temp_c=260,
        bed_temp_c=100,
        fan_percent=20,
        base_speed_mm_s=70,
        warnings=("Indicado para uso externo, mas exige ambiente ventilado.",),
    ),
    "TPU": MaterialProfile(
        name="TPU",
        nozzle_temp_c=225,
        bed_temp_c=50,
        fan_percent=45,
        base_speed_mm_s=35,
        warnings=("Imprimir devagar e com retracao conservadora.",),
    ),
}

