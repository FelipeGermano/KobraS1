from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SlicerInstallation:
    name: str
    executable: Path
    version: str | None = None
    machine_profile: Path | None = None
    process_profile: Path | None = None
    filament_profile: Path | None = None


@dataclass(frozen=True)
class SlicerCommandResult:
    command: tuple[str, ...]
    exit_code: int | None
    stdout: str
    stderr: str
    generated_files: tuple[Path, ...] = field(default_factory=tuple)

    @property
    def success(self) -> bool:
        return self.exit_code == 0


@dataclass(frozen=True)
class GcodeValidation:
    path: Path
    is_valid: bool
    bounds_mm: tuple[float, float, float, float, float, float] | None
    nozzle_temps_c: tuple[int, ...]
    bed_temps_c: tuple[int, ...]
    estimated_time: str | None
    filament_used: str | None
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class AutoSliceResult:
    project_path: Path
    output_dir: Path
    command_result: SlicerCommandResult
    gcode_path: Path | None
    validation: GcodeValidation | None

    @property
    def success(self) -> bool:
        return self.gcode_path is not None and self.validation is not None and self.validation.is_valid
