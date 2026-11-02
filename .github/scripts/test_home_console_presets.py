"""A published port kind may have an unresolved count; it must not become zero."""
import importlib.util
from pathlib import Path
import sys

import pytest

pytest.importorskip("hyperobjects_reference")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/presets"))
spec = importlib.util.spec_from_file_location("home_console_presets", ROOT / "tools/presets/home_console.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def test_null_port_counts_fall_back_explicitly(monkeypatch):
    monkeypatch.setattr(h, "is_sourced", lambda obj, field: True)
    obj = {"key": "test-console", "dimensions_mm": {"states": {"body": {
        "width": 300, "depth": 200, "height": 60}}},
        "ports": [{"kind": k, "count": None} for k in (
            "controller_proprietary", "expansion", "usb_a", "memory_card")],
        "media": [], "controls": [], "features": {}}
    values, fallbacks = h.derive(h.read_device(obj), full=False)
    assert values["controller_port_count"] == h.ARCHETYPE_BASE["controller_port_count"]
    assert {"controller-port count", "expansion-port count", "rear USB count", "memory-card count"} <= set(fallbacks)


def test_vertical_only_state_restores_the_published_axes():
    obj = {"key": "test-standing", "dimensions_mm": {"states": {"vertical": {
        "width": 90, "height": 300, "depth": 220}}}}
    source = h.read_device(obj)
    assert (source["body_width"], source["body_depth"], source["body_height"]) == (300, 220, 90)
    assert source["orientation_tilt_deg"] == 90
