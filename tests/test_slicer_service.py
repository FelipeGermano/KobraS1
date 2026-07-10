import sys

from app.services.slicer_service import run_slicer_command


def test_run_slicer_command_captures_output() -> None:
    result = run_slicer_command(
        [sys.executable, "-c", "print('ok')"],
        timeout_s=10,
    )

    assert result.success is True
    assert result.stdout.strip() == "ok"
