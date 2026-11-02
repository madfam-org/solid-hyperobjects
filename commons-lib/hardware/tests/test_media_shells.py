"""commons-lib/hardware/media_shells.py, built with the real kernel OUTSIDE the sandbox.

Run: python3 -m pytest commons-lib/hardware/tests (needs cadquery). Expectations are
analytic (box and fillet arithmetic) or topological (one valid body, the hull's box).
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


@pytest.fixture(scope="module")
def ns():
    return ip.load(["media_shells"], root=REPO)


def bbox(wp):
    b = wp.val().BoundingBox()
    return (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)


def one_valid_body(wp):
    solids = wp.solids().vals()
    assert len(solids) == 1
    assert solids[0].isValid()
    return solids[0]


def test_outer_without_band_is_a_rounded_slab(ns):
    hull = ns["media_shell_outer"]({"width": 40.0, "height": 30.0, "thickness": 3.0,
                                    "corner_radius": 2.0, "grip_thickness": 0.0,
                                    "grip_height": 0.0})
    solid = one_valid_body(hull)
    assert solid.Volume() == pytest.approx((40 * 30 - (4 - math.pi) * 4) * 3, rel=1e-6)
    assert bbox(hull) == pytest.approx((-20, -1.5, 0, 20, 1.5, 30), abs=1e-6)


def test_grip_band_thickens_only_the_far_edge(ns):
    hull = ns["media_shell_outer"]({"width": 100.0, "height": 110.0, "thickness": 15.0,
                                    "corner_radius": 4.0, "grip_thickness": 19.0,
                                    "grip_height": 22.0})
    one_valid_body(hull)
    assert bbox(hull) == pytest.approx((-50, -9.5, 0, 50, 9.5, 110), abs=1e-6)
    low = hull.intersect(cq.Workplane("XY").box(200, 50, 2).translate((0, 0, 5)))
    assert low.val().BoundingBox().ylen == pytest.approx(15.0, abs=1e-6)


def test_hollow_shell_with_window_stays_one_body_per_half(ns):
    p = {"width": 60.0, "height": 70.0, "thickness": 12.0, "corner_radius": 3.0}
    shell = ns["media_shell_outer"]({**p, "grip_thickness": 0.0, "grip_height": 0.0})
    shell = shell.cut(ns["media_shell_cavity"]({**p, "wall": 1.5}))
    shell = shell.cut(ns["contact_window"]({"width": 40.0, "depth": 6.0, "thickness": 9.0}))
    for side in (-1, 1):
        half = shell.intersect(cq.Workplane("XY").box(70, 7, 80).translate((0, side * 3.5, 35)))
        one_valid_body(half)


def test_board_tongue_and_pads_are_one_body(ns):
    board = ns["edge_connector_board"]({
        "thickness": 1.6, "center_y": 0.0,
        "panel_width": 50.0, "panel_bottom": 1.8, "panel_top": 60.0,
        "tongue_width": 39.4, "tongue_bottom": 1.0, "tongue_top": 2.0,
        "front_contacts": 16, "back_contacts": 16, "pitch": 2.0,
        "pad_length": 4.0, "pad_inset": 0.3,
    })
    one_valid_body(board)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox(board)
    assert (zmin, zmax) == pytest.approx((1.0, 60.0), abs=1e-6)
    assert ymax == pytest.approx(0.8 + ns["MEDIA_PAD_PROUD"], abs=1e-6)


def test_every_cutter_overshoots_its_face(ns):
    over = ns["MEDIA_OVERSHOOT"]
    lab = ns["label_recess"]({"width": 10.0, "height": 10.0, "depth": 0.5, "center_x": 0.0,
                              "center_z": 20.0, "face_y": -6.0, "outer_y": -6.0})
    assert bbox(lab)[1] == pytest.approx(-6.0 - over, abs=1e-6)
    assert bbox(lab)[4] == pytest.approx(-5.5, abs=1e-6)
    mouth = ns["pass_through_mouth"]({"width": 40.0, "thickness": 6.0, "depth": 10.0,
                                      "shell_height": 70.0})
    assert bbox(mouth)[5] == pytest.approx(70.0 + over, abs=1e-6)
    ring = ns["shutter_outline"]({"width": 20.0, "height": 10.0, "bottom": 1.0, "gap": 0.5,
                                  "depth": 0.5, "face_y": 6.0})
    assert bbox(ring)[4] == pytest.approx(6.0 + over, abs=1e-6)
    assert ring.val().Volume() == pytest.approx((21 * 11 - 20 * 10) * (0.5 + over), rel=1e-6)


@pytest.mark.parametrize("edge,box", [
    ("bottom", (-20, -1.5, -5, 20, 1.5, 25)),
    ("top", (-20, -1.5, 5, 20, 1.5, 35)),
])
def test_place_moves_toward_the_contact_edge(ns, edge, box):
    slab = ns["media_shell_outer"]({"width": 40.0, "height": 30.0, "thickness": 3.0,
                                    "corner_radius": 0.0, "grip_thickness": 0.0,
                                    "grip_height": 0.0})
    placed = ns["media_place"](slab, {"insertion_edge": edge, "width": 40.0,
                                      "height": 30.0, "travel": 5.0})
    assert bbox(placed) == pytest.approx(box, abs=1e-6)


def test_place_side_turns_the_contact_edge_to_plus_x(ns):
    # The canonical shell for a side edge is built `height` wide and `width` tall.
    slab = ns["media_shell_outer"]({"width": 30.0, "height": 40.0, "thickness": 3.0,
                                    "corner_radius": 0.0, "grip_thickness": 0.0,
                                    "grip_height": 0.0})
    marker = cq.Workplane("XY").box(2, 2, 2).translate((0, 0, 1))   # at the contact edge
    placed = ns["media_place"](slab.union(marker), {"insertion_edge": "side", "width": 40.0,
                                                    "height": 30.0, "travel": 0.0})
    assert bbox(placed) == pytest.approx((-20, -1.5, 0, 20, 1.5, 30), abs=1e-6)
    m = ns["media_place"](marker, {"insertion_edge": "side", "width": 40.0, "height": 30.0,
                                   "travel": 0.0})
    assert m.val().BoundingBox().xmax == pytest.approx(20.0, abs=1e-6)
