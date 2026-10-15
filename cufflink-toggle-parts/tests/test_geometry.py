"""Native interface regression probes; no manufacturing qualification."""

from pathlib import Path
import cadquery as cq
import pytest

SOURCE = Path(__file__).resolve().parents[1] / "main.py"


def build(**parameters):
    namespace = dict(parameters)
    exec(compile(SOURCE.read_text(), str(SOURCE), "exec"), namespace)
    return namespace


def volume(shape):
    return sum(s.Volume() for s in shape.solids().vals())


def inside(shape, point):
    return any(s.isInside(cq.Vector(*point)) for s in shape.solids().vals())


def valid(namespace, expected):
    solids = namespace["result"].solids().vals()
    assert len(solids) == expected
    assert all(s.isValid() and s.Volume() > 0 for s in solids)


@pytest.fixture(params=[(1, 1), (0.8, 0.85), (0.8, 1.15), (1.2, 0.85), (1.2, 1.15)])
def scales(request):
    return request.param


def test_common_transverse_pin_axis_and_toggle_clearance(scales):
    s, h = scales
    n = build(size=16 * s, section=h)
    valid(n, 2)
    pin = (
        cq.Workplane("YZ")
        .center(0, 10 * s * h)
        .circle(0.75 * s)
        .extrude(6 * s, both=True)
    )
    assert volume(n["a"].intersect(pin)) < 1e-7
    toggle = (
        n["b"].rotate((0, 0, 0), (0, 1, 0), 90).translate((-1.2 * s * h, 0, 10 * s * h))
    )
    assert volume(toggle.intersect(pin)) < 1e-7
    assert volume(toggle.intersect(n["a"])) < 1e-7
    assert inside(n["a"], (-3 * s, 1.2 * s, 10 * s * h))
