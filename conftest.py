import sys
from pathlib import Path

# Ensure that the backend package is on PYTHONPATH when tests are run from repo root
ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / 'backend'
path_str = str(BACKEND)
if path_str not in sys.path:
    sys.path.insert(0, path_str)
