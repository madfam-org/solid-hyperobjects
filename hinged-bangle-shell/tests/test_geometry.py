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


def test_shared_pin_axis_and_complementary_knuckles(scales):
    s, h = scales
    n = build(size=60 * s, section=h)
    valid(n, 2)
    assert volume(n["a"].intersect(n["b"])) < 1e-7
    for z in [1, 4, 7]:
        assert not inside(n["a"], (30 * s, 0, z * s * h))
        assert not inside(n["b"], (30 * s, 0, z * s * h))
    for z in [1, 7]:
        assert inside(n["a"], (30 * s, 2 * s, z * s * h))
        assert not inside(n["b"], (30 * s, 2 * s, z * s * h))
    assert not inside(n["a"], (30 * s, 2 * s, 4 * s * h))
    assert inside(n["b"], (30 * s, 2 * s, 4 * s * h))
