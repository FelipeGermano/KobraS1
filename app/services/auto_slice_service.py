from __future__ import annotations

from pathlib import Path

from app.domain.model_analysis import ModelAnalysis
from app.domain.slicer import AutoSliceResult
from app.domain.slicing_profile import SlicingProfile, UserChoices
from app.services.gcode_validation_service import validate_gcode
from app.services.project_export_service import export_recommended_3mf
from app.services.slicer_service import resolve_kobra_s1_profiles, run_slicer_command


class AutoSliceError(ValueError):
    """Raised when automatic slicing cannot be started."""


def generate_gcode(
    slicer_executable: str | Path,
    source_path: str | Path,
    output_dir: str | Path,
    analysis: ModelAnalysis,
    choices: UserChoices,
    profile: SlicingProfile,
    timeout_s: int = 600,
) -> AutoSliceResult:
    slicer = Path(slicer_executable)
    if not slicer.exists():
        raise AutoSliceError("O executavel do slicer nao existe.")
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    destination = destination.resolve()
    project_path = (destination / f"{Path(source_path).stem}_kobra_s1_auto.3mf").resolve()
    export_recommended_3mf(source_path, project_path, analysis, choices, profile)

    before = set(destination.rglob("*"))
    command = [str(slicer)]
    profiles = resolve_kobra_s1_profiles(choices.material, choices.quality)
    if profiles is not None:
        machine, process, filament = profiles
        command.extend(["--load-settings", f"{machine};{process}", "--load-filaments", str(filament)])
    command.extend(["--slice", "0", "--outputdir", str(destination), str(project_path)])
    result = run_slicer_command(command, timeout_s=timeout_s, output_dir=destination, cwd=slicer.parent)
    gcode = _find_newest_gcode(destination, before)
    validation = validate_gcode(gcode, profile) if gcode else None
    return AutoSliceResult(
        project_path=project_path,
        output_dir=destination,
        command_result=result,
        gcode_path=gcode,
        validation=validation,
    )


def _find_newest_gcode(output_dir: Path, before: set[Path]) -> Path | None:
    candidates = [
        path
        for path in output_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".gcode", ".gco", ".gc"} and path not in before
    ]
    if not candidates:
        candidates = [
            path
            for path in output_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".gcode", ".gco", ".gc"}
        ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)
