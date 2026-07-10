from __future__ import annotations

import re
import subprocess
from pathlib import Path

from app.domain.slicer import SlicerCommandResult, SlicerInstallation


ANYCUBIC_DEFAULT_ROOT = Path("C:/Program Files/AnycubicSlicerNext")
QUALITY_LAYER_HEIGHTS = {
    "Rapida": "0.28",
    "Normal": "0.20",
    "Detalhada": "0.16",
    "Muito detalhada": "0.12",
}


class SlicerServiceError(ValueError):
    """Raised when the configured slicer cannot be used."""


def find_anycubic_slicer() -> SlicerInstallation | None:
    executable = ANYCUBIC_DEFAULT_ROOT / "AnycubicSlicerNext.exe"
    if not executable.exists():
        return None
    profile_root = ANYCUBIC_DEFAULT_ROOT / "resources" / "profiles" / "Anycubic"
    return SlicerInstallation(
        name="Anycubic Slicer Next",
        executable=executable,
        version=detect_slicer_version(executable),
        machine_profile=profile_root / "machine" / "Anycubic Kobra S1 0.4 nozzle.json",
        process_profile=profile_root / "process" / "0.20mm Standard @Anycubic Kobra S1 0.4 nozzle.json",
        filament_profile=profile_root / "filament" / "Anycubic PLA @Anycubic Kobra S1 0.4 nozzle.json",
    )


def resolve_kobra_s1_profiles(material: str, quality: str) -> tuple[Path, Path, Path] | None:
    profile_root = ANYCUBIC_DEFAULT_ROOT / "resources" / "profiles" / "Anycubic"
    layer = QUALITY_LAYER_HEIGHTS.get(quality, "0.20")
    machine = profile_root / "machine" / "Anycubic Kobra S1 0.4 nozzle.json"
    process = profile_root / "process" / f"{layer}mm Standard @Anycubic Kobra S1 0.4 nozzle.json"
    filament = profile_root / "filament" / f"Anycubic {material} @Anycubic Kobra S1 0.4 nozzle.json"
    if machine.exists() and process.exists() and filament.exists():
        return machine, process, filament
    return None


def detect_slicer_version(executable: str | Path) -> str | None:
    path = Path(executable)
    if not path.exists():
        return None
    result = run_slicer_command([str(path), "--help"], timeout_s=10)
    text = result.stdout + "\n" + result.stderr
    match = re.search(r"(AnycubicSlicerNext-[^\s:]+)", text)
    return match.group(1) if match else None


def validate_slicer_path(executable: str | Path) -> SlicerInstallation:
    path = Path(executable)
    if not path.exists():
        raise SlicerServiceError("O executavel do slicer nao existe.")
    version = detect_slicer_version(path)
    if version is None:
        raise SlicerServiceError("Nao foi possivel validar a versao do slicer.")
    found = find_anycubic_slicer()
    if found and found.executable == path:
        return found
    return SlicerInstallation(name="Slicer configurado", executable=path, version=version)


def open_project(executable: str | Path, project_path: str | Path) -> None:
    slicer = Path(executable)
    project = Path(project_path)
    if not slicer.exists():
        raise SlicerServiceError("O executavel do slicer nao existe.")
    if not project.exists():
        raise SlicerServiceError("O projeto 3MF nao existe.")
    subprocess.Popen([str(slicer), str(project)])


def run_slicer_command(
    command: list[str],
    timeout_s: int = 120,
    output_dir: str | Path | None = None,
    cwd: str | Path | None = None,
) -> SlicerCommandResult:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
            cwd=str(cwd) if cwd is not None else None,
        )
        generated = _collect_files(output_dir)
        return SlicerCommandResult(
            command=tuple(command),
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            generated_files=generated,
        )
    except subprocess.TimeoutExpired as exc:
        return SlicerCommandResult(
            command=tuple(command),
            exit_code=None,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + "\nTempo limite excedido.",
            generated_files=_collect_files(output_dir),
        )


def _collect_files(output_dir: str | Path | None) -> tuple[Path, ...]:
    if output_dir is None:
        return ()
    root = Path(output_dir)
    if not root.exists():
        return ()
    return tuple(path for path in root.rglob("*") if path.is_file())
