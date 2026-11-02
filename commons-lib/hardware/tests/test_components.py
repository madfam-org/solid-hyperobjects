"""The commons-lib/hardware/ components, built with the real kernel OUTSIDE the sandbox.

Run: python3 -m pytest commons-lib/hardware/tests (needs cadquery; CI runs it in the
`assemblies` job, the every-PR job that installs the kernel).

Each module is loaded through `tools/inline_parts.load`, which executes the same
texts in the same order a generated main.py does. Every expectation is analytic
(box, cylinder, fillet arithmetic) at the clamshell's archetype defaults, so a change
to a component's construction shows up here before it shows up in a family render.
"""

import importlib.util
import math
import pathlib
import subprocess
import sys

import pytest

cq = pytest.importorskip("cadquery")

REPO = pathlib.Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("inline_parts", REPO / "tools" / "inline_parts.py")
ip = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ip)

MODULES = ("patterns", "structure", "controls", "connectors", "displays")
COMPONENTS = {
    "structure": {"deck_shell", "hinge_barrel", "hinge_relief", "speaker_grille"},
    "controls": {"d_pad", "face_button", "button_row", "analog_stick", "shoulder_trigger"},
    "connectors": {"port_receptacle", "cartridge_slot"},
    "displays": {"display_panel"},
    "patterns": {"linear_pattern", "polar_pattern"},
}


@pytest.fixture(scope="module")
def ns():
    return ip.load(list(MODULES), root=REPO)


def measure(wp):
    solids = wp.solids().vals()
    bb = wp.val().BoundingBox()
    return len(solids), sum(s.Volume() for s in solids), (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)


def assert_solid(wp, bodies, volume, bbox=None):
    n, v, box = measure(wp)
    assert all(s.isValid() for s in wp.solids().vals())
    assert n == bodies
    assert v == pytest.approx(volume, rel=1e-6)
    if bbox is not None:
        assert box == pytest.approx(bbox, abs=1e-6)


@pytest.mark.parametrize("name", MODULES)
def test_each_module_loads_alone_with_only_its_requirements(name):
    namespace = ip.load([name], root=REPO)
    defined = {k for k, v in namespace.items() if callable(v) and getattr(v, "__module__", None) == "commons_hardware"}
    expected = set(COMPONENTS[name])
    for req in ip.read_module(REPO, name)["requires"]:
        expected |= COMPONENTS[req]
    assert defined == expected


@pytest.mark.parametrize("name", MODULES)
def test_each_module_runs_as_a_plain_script(name):
    path = REPO / ip.HARDWARE / f"{name}.py"
    subprocess.run([sys.executable, str(path)], check=True, capture_output=True)


def test_patterns_count_copies(ns):
    box = cq.Workplane("XY").box(1, 1, 1)
    assert measure(ns["linear_pattern"](box, 1, 5))[0] == 1
    assert_solid(ns["linear_pattern"](box, 3, 5), 3, 3.0, (-0.5, -0.5, -0.5, 10.5, 0.5, 0.5))
    seat = cq.Workplane("XY").box(1, 1, 1).translate((4, 0, 0))
    assert_solid(ns["polar_pattern"](seat, 4, 90), 4, 4.0, (-4.5, -4.5, -0.5, 4.5, 4.5, 0.5))


def test_deck_shell(ns):
    p = {"length": 150.0, "depth": 90.0, "thickness": 12.1, "center_y": 45.0, "center_z": -6.05,
         "corner_radius": 5.0}
    area = 150.0 * 90.0 - (4 - math.pi) * 5.0 ** 2
    assert_solid(ns["deck_shell"](p), 1, area * 12.1, (-75, 0, -12.1, 75, 90, 0))


def test_hinge_barrel_is_a_run_of_half_knuckles(ns):
    p = {"barrel_radius": 5.445, "knuckle_length": 21.0, "knuckle_count": 3, "knuckle_pitch": 27.0,
         "knuckle_start_x": -27.0, "clip_span": 400.0, "clip_center_y": -200.0}
    half = math.pi * 5.445 ** 2 * 21.0 / 2
    assert_solid(ns["hinge_barrel"](p), 3, 3 * half, (-37.5, 0, -5.445, 37.5, 5.445, 5.445))


def test_hinge_relief(ns):
    p = {"relief_radius": 5.845, "relief_span": 75.8}
    assert_solid(ns["hinge_relief"](p), 1, math.pi * 5.845 ** 2 * 75.8,
                 (-37.9, -5.845, -5.845, 37.9, 5.845, 5.845))


def test_speaker_grille(ns):
    p = {"count": 6, "first_center_x": -66.75, "center_y": 78.0, "hole_radius": 0.9, "pitch": 3.5,
         "recess_depth": 1.2, "cut_center_z": -0.6}
    assert_solid(ns["speaker_grille"](p), 6, 6 * math.pi * 0.81 * 1.2,
                 (-67.65, 77.1, -1.2, -66.75 + 17.5 + 0.9, 78.9, 0))


def test_d_pad_is_two_crossed_bars(ns):
    p = {"arm_length": 22.0, "arm_width": 8.0, "recess_depth": 1.2, "center_x": -58.0, "center_y": 45.0,
         "cut_center_z": -0.6}
    assert_solid(ns["d_pad"](p), 1, (2 * 22 * 8 - 8 * 8) * 1.2, (-69, 34, -1.2, -47, 56, 0))


def test_face_button_ring(ns):
    p = {"count": 4, "spacing_deg": 90.0, "circle_radius": 11.0, "radius": 4.5, "recess_depth": 1.2,
         "center_x": 58.0, "center_y": 45.0, "cut_center_z": -0.6}
    assert_solid(ns["face_button"](p), 4, 4 * math.pi * 4.5 ** 2 * 1.2, (42.5, 29.5, -1.2, 73.5, 60.5, 0))


@pytest.mark.parametrize("name", ["button_row", "analog_stick"])
def test_rows_of_round_seats(ns, name):
    p = {"count": 2, "first_center_x": -58.0, "pitch_x": 116.0, "center_y": 27.0, "radius": 8.0,
         "recess_depth": 1.2, "cut_center_z": -0.6}
    assert_solid(ns[name](p), 2, 2 * math.pi * 64 * 1.2, (-66, 19, -1.2, 66, 35, 0))


def test_shoulder_trigger(ns):
    p = {"count": 2, "first_center_x": -54.5, "pitch_x": 109.0, "center_y": 0.0, "center_z": -6.05,
         "width": 26.0, "depth": 6.0, "height": 4.0}
    assert_solid(ns["shoulder_trigger"](p), 2, 2 * 26 * 6 * 4, (-67.5, -3, -8.05, 67.5, 3, -4.05))


def test_port_receptacle_rect_and_round(ns):
    rect = {"shape": "rect", "width": 9.0, "height": 3.2, "depth": 12.0, "radius": 0.0,
            "center_x": 0.0, "center_y": 90.0, "center_z": -6.05}
    assert_solid(ns["port_receptacle"](rect), 1, 9 * 12 * 3.2, (-4.5, 84, -7.65, 4.5, 96, -4.45))
    jack = {"shape": "round", "width": 0.0, "height": 0.0, "depth": 12.0, "radius": 1.75,
            "center_x": -45.0, "center_y": 90.0, "center_z": -6.05}
    assert_solid(ns["port_receptacle"](jack), 1, math.pi * 1.75 ** 2 * 12,
                 (-46.75, 84, -7.8, -43.25, 96, -4.3))


def test_cartridge_slot(ns):
    p = {"width": 35.0, "height": 4.0, "depth": 10.0, "center_x": 45.0, "center_y": 90.0, "center_z": -6.05}
    assert_solid(ns["cartridge_slot"](p), 1, 35 * 10 * 4, (27.5, 85, -8.05, 62.5, 95, -4.05))


def test_display_panel(ns):
    p = {"width": 80.0, "height": 50.0, "recess_depth": 0.8, "center_x": 0.0, "center_y": 45.0,
         "cut_center_z": -0.4}
    assert_solid(ns["display_panel"](p), 1, 80 * 50 * 0.8, (-40, 20, -0.8, 40, 70, 0))
