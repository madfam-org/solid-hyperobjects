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


def test_continuous_wire_route(scales):
    s, h = scales
    n = build(size=10 * s, section=h)
    valid(n, 1)
    # Each vertical leg and the shallow joining bridge must be empty space.
    for x in [-2.5, 2.5]:
        for z in [0.25, 1.5, 2.5]:
            assert not inside(n["result"], (x * s, 0, z * s * h))
    for x in [-2.5, -1.25, 0, 1.25, 2.5]:
        assert not inside(n["result"], (x * s, 0, 2.5 * s * h))
    assert inside(n["result"], (0, 2 * s, 2.5 * s * h))
