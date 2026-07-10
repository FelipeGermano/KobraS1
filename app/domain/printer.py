from dataclasses import dataclass


@dataclass(frozen=True)
class PrinterProfile:
    name: str
    build_volume_mm: tuple[float, float, float]
    nozzle_diameter_mm: float
    max_nozzle_temp_c: int
    max_bed_temp_c: int

    def fits(self, dimensions_mm: tuple[float, float, float]) -> bool:
        return all(size <= limit for size, limit in zip(dimensions_mm, self.build_volume_mm))


KOBRA_S1 = PrinterProfile(
    name="Anycubic Kobra S1",
    build_volume_mm=(250.0, 250.0, 250.0),
    nozzle_diameter_mm=0.4,
    max_nozzle_temp_c=300,
    max_bed_temp_c=120,
)

