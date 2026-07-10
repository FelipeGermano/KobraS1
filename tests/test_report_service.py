import json
from pathlib import Path

import numpy as np

from app.services.report_service import save_summary


def test_save_summary_converts_numpy_scalars(tmp_path: Path) -> None:
    summary = {
        "analysis": {
            "support_likely": np.bool_(True),
            "volume_mm3": np.float64(123.4),
            "triangle_count": np.int64(42),
        }
    }

    output = save_summary(summary, tmp_path)

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["analysis"]["support_likely"] is True
    assert loaded["analysis"]["volume_mm3"] == 123.4
    assert loaded["analysis"]["triangle_count"] == 42
