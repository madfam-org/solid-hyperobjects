"""Native interface regressions; physical qualification is outside these tests."""

import json
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


def test_notches_are_present_without_claiming_assembly(geometry):
    solids, s, q = geometry
    assert inside(solids, 0, 11, 1, s, q)
    assert not inside(solids, 0, 11, 3, s, q)
    assert inside(solids, 19, 0, 1, s, q)
    assert not inside(solids, 19, 0, 3, s, q)
