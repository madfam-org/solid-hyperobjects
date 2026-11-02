"""Analytic fit and motion checks for the console component modules."""
import importlib.util
from pathlib import Path

import pytest

cq = pytest.importorskip("cadquery")
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("inline_parts_console", ROOT / "tools/inline_parts.py")
ip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ip)


@pytest.fixture(scope="module")
def ns():
    return ip.load(["console_shell", "console_io"], root=ROOT)


def test_plain_body_has_analytic_box_volume(ns):
    body = ns["shell_body"]({
        "width": 100, "depth": 80, "sections": [[0, 30], [80, 30]],
        "crown": 0, "draft_deg": 0, "concavity": 0, "corner_radius_top": 0,
        "edge_chamfer": 0, "corner_radius_plan": 0, "skew_deg": 0,
        "center_x": 0, "center_y": 0, "base_z": 0,
    }).val()
    assert body.isValid() and len(body.Solids()) == 1
    assert body.Volume() == pytest.approx(100 * 80 * 30)
    b = body.BoundingBox()
    assert (b.xlen, b.ylen, b.zlen) == pytest.approx((100, 80, 30), abs=1e-6)


def test_slot_keeps_media_clearance_and_cut_overshoot(ns):
    frame = {"origin": (0, 0, 0), "x_dir": (1, 0, 0), "normal": (0, 0, 1)}
    slot = ns["media_cartridge_slot"]({
        "frame": frame, "media_width": 40, "media_thickness": 5,
        "insert_depth": 20, "clearance": 0.5, "extra_depth": 0, "overshoot": 1,
    }).val().BoundingBox()
    assert (slot.xlen, slot.ylen, slot.zmin, slot.zmax) == pytest.approx((41, 6, -20.5, 1))


def test_tray_extension_is_pure_translation(ns):
    p = {"frame": {"origin": (0, -50, 20), "x_dir": (1, 0, 0), "normal": (0, -1, 0)},
         "width": 140, "height": 10, "depth": 130, "gap": 0.3,
         "disc_diameter": 120, "pocket_depth": 1.5, "travel": 100}
    closed = ns["disc_tray"]({**p, "extension": 0}).val()
    opened = ns["disc_tray"]({**p, "extension": 1}).val()
    assert closed.isValid() and opened.isValid()
    assert opened.Volume() == pytest.approx(closed.Volume())
    assert opened.Center().sub(closed.Center()).toTuple() == pytest.approx((0, -100, 0))


def test_handle_is_connected_and_bites_into_rear(ns):
    handle = ns["handle"]({"span": 60, "reach": 20, "thickness": 8,
                           "top_z": 40, "rear_y": 50, "center_x": 0, "bite": 0.2}).val()
    assert handle.isValid() and len(handle.Solids()) == 1
    assert handle.BoundingBox().ymin == pytest.approx(49.8)
