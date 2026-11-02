"""Analytic layout and rigid-motion checks for the pad components."""
import importlib.util
from pathlib import Path
import pytest

pytest.importorskip("cadquery")
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("inline_parts_pad", ROOT / "tools/inline_parts.py")
ip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ip)


@pytest.fixture(scope="module")
def ns():
    return ip.load(["pad_body", "pad_controls"], root=ROOT)


def test_row_layout_rotates_around_its_center(ns):
    points = ns["pad_face_layout"]({"arrangement": "row", "count": 3,
        "spacing": 10, "radius": 3, "tilt_deg": 90, "center_x": 20, "center_y": 30})
    for actual, expected in zip(points, [(20, 20, 3), (20, 30, 3), (20, 40, 3)]):
        assert actual == pytest.approx(expected)


def test_crown_center_and_drop_are_analytic(ns):
    c={"thickness": 40, "floor": 10, "top_crown": 5, "bottom_crown": 3,
       "span_x": 80, "span_y": 100, "center_y": 0}
    assert ns["pad_crown_top"](c, 0, 0) == 40
    assert ns["pad_crown_bottom"](c, 0, 0) == 10
    assert ns["pad_crown_top"](c, 80, 0) == pytest.approx(35.1)
    assert ns["pad_crown_bottom"](c, 80, 0) == pytest.approx(12.94)


def test_trigger_rotation_preserves_valid_solid_and_volume(ns):
    p={"center_x": 20, "width": 15, "y_inner": 10, "notch_top": 30,
       "length": 12, "thickness": 3, "clearance": 0.3}
    a=ns["pad_trigger_blade"]({**p, "angle_deg": 0})
    b=ns["pad_trigger_blade"]({**p, "angle_deg": 20})
    assert a.isValid() and b.isValid()
    assert len(a.Solids()) == len(b.Solids()) == 1
    assert a.Volume() == pytest.approx(b.Volume())
    assert a.Center().sub(b.Center()).Length > 1


def test_stick_tilt_preserves_valid_connected_cap(ns):
    p={"center_x": 0,"center_y": 0,"floor_z": 20,"surface_z": 25,
       "radius": 8,"height": 10,"cap": "concave","clearance": 0.3}
    a=ns["pad_stick"]({**p,"tilt_deg": -20})
    b=ns["pad_stick"]({**p,"tilt_deg": 20})
    assert a.isValid() and b.isValid()
    assert len(a.Solids()) == len(b.Solids()) == 1
    assert a.Volume() == pytest.approx(b.Volume())
    assert a.Center().y == pytest.approx(-b.Center().y)


def test_handles_battery_door_produces_a_closed_exported_mesh():
    import json
    from y4d_spec.geometry import render_part
    manifest=json.loads((ROOT/"gamepad/project.json").read_text())
    values=next(p["values"] for p in manifest["presets"] if p["slug"]=="archetype-handles")
    check=render_part(ROOT/"gamepad","main.py","pad","body",params=values)
    assert check.ok, check.problems


def test_conservative_envelope_matches_archetype_boxes_and_sourced_body_axes():
    import json
    from y4d_spec.geometry import _exec_cartridge
    manifest=json.loads((ROOT/"gamepad/project.json").read_text())
    for preset in manifest['presets']:
        shape=_exec_cartridge(str(ROOT/"gamepad/main.py"),{
            **preset['values'],'target_part':'envelope'}).val()
        box=shape.BoundingBox()
        if 'registry' in preset:
            from hyperobjects_reference import is_sourced, load_object
            obj=load_object(preset['registry']['device'])
            body=obj['dimensions_mm']['states']['body']
            split=(obj.get('features') or {}).get('split') if is_sourced(obj, 'features.split') else None
            expected={'width':body['width'] * (2 if split and split != 'none' else 1),
                      'depth':max(body['height'],body['depth']),
                      'thickness':min(body['height'],body['depth'])}
        else:
            expected=preset['envelope_mm']
        assert (box.xlen,box.ylen,box.zlen)==pytest.approx(
            (expected['width'],expected['depth'],expected['thickness']),abs=0.01)
