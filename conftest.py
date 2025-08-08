from pathlib import Path
import sys

# Ensure repository root and common web_interface paths are on PYTHONPATH for pytest runs
ROOT = Path(__file__).resolve().parent
for _p in [str(ROOT), str(ROOT / "web_interface"), str(ROOT / "web_interface" / "backend")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# WEB_ROOT path injection removed to ensure correct package discovery