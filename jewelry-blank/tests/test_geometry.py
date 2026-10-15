"""Native interface regression probes; no manufacturing qualification."""

from pathlib import Path
import cadquery as cq
import pytest
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Torus

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


@pytest.mark.parametrize("profile", ["domed", "comfort"])
@pytest.mark.parametrize("dimensions", [(7, 6, 2), (3, 2, 1.2), (14, 16, 5)])
def test_profiles_blend_the_declared_rim_pair(profile, dimensions):
    ring_size, width, thickness = dimensions
    n = build(profile=profile, ring_size=ring_size, band_w=width, band_t=thickness)
    valid(n, 1)
    tori = []
    for face in n["result"].faces().vals():
        surface = BRepAdaptor_Surface(face.wrapped)
        if surface.GetType() == GeomAbs_Torus:
            tori.append(surface.Torus())
    assert len(tori) == 2
    assert sorted(t.Location().Z() for t in tori)[0] < 0
    assert sorted(t.Location().Z() for t in tori)[1] > 0
    for torus in tori:
        tangent_radius = (
            torus.MajorRadius() + torus.MinorRadius()
            if profile == "domed"
            else torus.MajorRadius() - torus.MinorRadius()
        )
        expected = n["outer_r"] if profile == "domed" else n["inner_r"]
        assert tangent_radius == pytest.approx(expected, abs=1e-7)
    assert volume(n["result"]) < volume(
        n["simple_band"](n["inner_r"], n["outer_r"], width)
    )
