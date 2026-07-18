"""Test import-path setup for the two independently deployable services."""

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "applications" / "telemetry-api" / "src"))
sys.path.insert(0, str(REPOSITORY_ROOT / "applications" / "telemetry-generator" / "src"))
