"""Keep unknown controller counts distinct from sourced absence."""
import importlib.util
from pathlib import Path
import sys

import pytest

pytest.importorskip("hyperobjects_reference")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/presets"))
spec = importlib.util.spec_from_file_location("gamepad_presets", ROOT / "tools/presets/gamepad.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def test_uncovered_control_list_does_not_establish_absence(monkeypatch):
    monkeypatch.setattr(g, "is_sourced", lambda obj, field: False)
    obj = {"controls": [{"kind": "face_button", "count": 4}]}
    assert g._count(obj, "stick") is None
    assert g._count(obj, "face_button") is None


def test_null_count_remains_unknown_and_empty_complete_list_proves_zero(monkeypatch):
    monkeypatch.setattr(g, "is_sourced", lambda obj, field: True)
    assert g._count({"controls": [{"kind": "stick", "count": None}]}, "stick") is None
    assert g._count({"controls": []}, "stick") == 0
    assert g._port({"ports": []}, "expansion_slot") == 0


def test_multiple_compatible_port_kinds_are_counted(monkeypatch):
    monkeypatch.setattr(g, "is_sourced", lambda obj, field: True)
    obj = {"ports": [{"kind": "usb_c", "count": 1}, {"kind": "micro_usb", "count": 1}]}
    assert g._port(obj, "usb_c", "micro_usb") == 2


def test_every_archetype_has_a_render_target():
    from y4d_spec.rules import preset_targets
    import json
    manifest = json.loads((ROOT / "gamepad/project.json").read_text())
    targets = preset_targets(manifest)
    assert {p["slug"] for p in manifest["presets"]} <= {row[0] for row in targets}
