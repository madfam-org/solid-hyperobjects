"""Native interface regressions; physical qualification is outside these tests."""

import json
import math
import runpy
from pathlib import Path

import cadquery as cq
import pytest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "project.json").read_text())
PARAMS = {p["id"]: p for p in MANIFEST["parameters"]}
CASES = [(PARAMS["size"]["default"], 1.0)] + [
    (size, section)
    for size in (PARAMS["size"]["min"], PARAMS["size"]["max"])
    for section in (PARAMS["section"]["min"], PARAMS["section"]["max"])
]


@pytest.fixture(params=CASES)
def geometry(request):
    size, section = request.param
    context = {"size": size, "section": section}
    context = runpy.run_path(str(ROOT / "main.py"), init_globals=context)
    solids = context["result"].solids().vals()
    expected = MANIFEST["verification"]["stages"]["geometry"]["checks"]["body_count"][
        "expected"
    ]
    assert len(solids) == expected
    assert all(s.isValid() and s.Volume() > 0 for s in solids)
    return solids, size / PARAMS["size"]["default"], section


def inside(solids, x, y, z, scale, section):
    return any(
        s.isInside(cq.Vector(x * scale, y * scale, z * scale * section), 1e-7)
        for s in solids
    )


def test_nominal_assembly_clearance_and_shared_pin(geometry):
    solids, s, q = geometry
    a, b, pin = solids
    b = b.translate((-32 * s, 0, 0))
    pin = pin.translate((-53 * s, 0, 0))
    for first, second in ((a, b), (a, pin), (b, pin)):
        assert first.intersect(second).Volume() < 1e-7
    for z in (0.2, 1.2, 2.2, 2.8, 3.8, 4.8):
        for i in range(12):
            angle = math.tau * i / 12
            assert not inside(
                [a, b], 11 + 0.9 * math.cos(angle), 0.9 * math.sin(angle), z, s, q
            )
    assert inside([a], 12.5, 0, 1.2, s, q)
    assert inside([b], 12.5, 0, 3.8, s, q)
    assert not inside([a, b], 12.5, 0, 2.5, s, q)
    assert pin.BoundingBox().zlen == pytest.approx(5 * s * q)
