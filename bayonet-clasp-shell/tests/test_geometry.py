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


def test_nominal_insertion_and_turning_path(scales):
    s, h = scales
    n = build(size=12 * s, section=h)
    valid(n, 2)
    for z in [0, 2, 6, 12]:
        assert volume(n["a"].intersect(n["b"].translate((0, 0, z * s * h)))) < 1e-7
    for angle in [0, 30, 60, 90]:
        turned = n["b"].rotate((0, 0, 0), (0, 0, 1), angle)
        assert volume(n["a"].intersect(turned)) < 1e-7
    turned = n["b"].rotate((0, 0, 0), (0, 0, 1), 90)
    # The upper wall should obstruct straight extraction after turning.
    assert (
        volume(n["a"].intersect(turned.translate((0, 0, 2 * s * h)))) > 0.1 * s**3 * h
    )
