# WebInterface package init
from pathlib import Path
import sys

# Ensure repo root and package path are on PYTHONPATH for tests
REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = Path(__file__).resolve().parent

for p in [str(REPO_ROOT), str(WEB_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)