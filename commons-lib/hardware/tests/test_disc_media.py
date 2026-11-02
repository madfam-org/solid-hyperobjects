"""commons-lib/hardware/disc_media.py, built with the real kernel OUTSIDE the sandbox.

Run: python3 -m pytest commons-lib/hardware/tests (needs cadquery). Expectations are
analytic (annulus and box arithmetic) at the keystone standard parts' own numbers.
"""

import importlib.util
import math
import pathlib

import pytest

cq = pytest.importorskip("cadquery")

REPO = pathlib.Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("inline_parts", REPO / "tools" / "inline_parts.py")
ip = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ip)

CD = {"diameter": 120.0, "hole": 15.0, "thickness": 1.2, "clamp_inner": 26.0,
      "clamp_outer": 33.0, "clamp_relief": 0.0, "ring_width": 1.0, "ring_height": 0.3}


@pytest.fixture(scope="module")
def ns():
    return ip.load(["disc_media"], root=REPO)


def bbox(wp):
    b = wp.val().BoundingBox()
    return (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)


def one_valid_body(wp):
    solids = wp.solids().vals()
    assert len(solids) == 1 and solids[0].isValid()
    return solids[0]


def test_cd_fills_the_standard_envelope(ns):
    disc = ns["revolved_disc"](CD)
    solid = one_valid_body(disc)
    assert bbox(disc) == pytest.approx((-60, -60, 0, 60, 60, 1.5), abs=1e-6)
    annulus = math.pi * (60 ** 2 - 7.5 ** 2) * 1.2
    ring = math.pi * (17.5 ** 2 - 16.5 ** 2) * 0.3
    assert solid.Volume() == pytest.approx(annulus + ring, rel=1e-5)


def test_relief_without_ring_and_a_solid_disc(ns):
    disc = ns["revolved_disc"]({**CD, "ring_height": 0.0, "clamp_relief": 0.1, "hole": 0.0})
    solid = one_valid_body(disc)
    expected = math.pi * 60 ** 2 * 1.2 - math.pi * (16.5 ** 2 - 13 ** 2) * 0.1
    assert solid.Volume() == pytest.approx(expected, rel=1e-5)


def test_arched_outline_is_the_umd_box(ns):
    shell = ns["disc_shell_outline"]({"shape": "arched", "width": 64.0, "length": 65.0,
                                      "thickness": 4.2, "corner_radius": 5.0,
                                      "top_arc_radius": 32.0, "bottom_arc_radius": 70.0})
    one_valid_body(shell)
    assert bbox(shell) == pytest.approx((-32, -32.5, 0, 32, 32.5, 4.2), abs=1e-6)


def test_boss_sets_the_maximum_thickness(ns):
    shell = ns["disc_shell_outline"]({"shape": "rounded_rect", "width": 80.0, "length": 84.0,
                                      "thickness": 5.0, "corner_radius": 3.0,
                                      "top_arc_radius": 0.0, "bottom_arc_radius": 0.0})
    shell = shell.union(ns["disc_shell_boss"]({"diameter": 50.0, "height": 0.15,
                                               "center_y": 2.0, "face_z": 5.0}))
    one_valid_body(shell)
    assert bbox(shell)[5] == pytest.approx(5.15, abs=1e-6)


def test_shutter_slides_by_its_offset(ns):
    p = {"width": 15.0, "length": 20.0, "thickness": 0.5, "center_y": -10.0, "lift": 0.02}
    closed = ns["disc_shutter_plate"]({**p, "offset": 0.0})
    opened = ns["disc_shutter_plate"]({**p, "offset": 15.0})
    assert bbox(opened)[0] - bbox(closed)[0] == pytest.approx(15.0, abs=1e-9)
    assert bbox(closed)[2] == pytest.approx(0.02, abs=1e-9)


def test_cutters_overshoot(ns):
    over = ns["DISC_OVERSHOOT"]
    win = ns["disc_window"]({"width": 30.0, "length": 15.0, "center_y": 12.5,
                             "from_z": 2.1, "top_z": 4.35})
    assert bbox(win)[5] == pytest.approx(4.35 + over, abs=1e-9)
    slot = ns["disc_read_slot"]({"spindle_diameter": 10.0, "slot_width": 10.0,
                                 "slot_length": 18.0, "slot_center_y": -14.0,
                                 "disc_center_y": 0.5, "to_z": 2.1})
    assert bbox(slot)[2] == pytest.approx(-over, abs=1e-9)
