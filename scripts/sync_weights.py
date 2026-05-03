"""Sincroniza QUALITY_WEIGHTS de config.py → landing/lib/quality_weights.json.

Ejecutar después de cambiar los pesos en config.py:
  python scripts/sync_weights.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import QUALITY_WEIGHTS  # noqa: E402

out_path = ROOT / "landing" / "lib" / "quality_weights.json"

weights_pct = {k: int(round(v * 100)) for k, v in QUALITY_WEIGHTS.items()}

assert sum(weights_pct.values()) == 100, (
    f"Los pesos deben sumar 100%, actualmente suman {sum(weights_pct.values())}%"
)

out_path.write_text(json.dumps(weights_pct, indent=2, ensure_ascii=False) + "\n")
print(f"Weights escritos en {out_path.relative_to(ROOT)}: {weights_pct}")
