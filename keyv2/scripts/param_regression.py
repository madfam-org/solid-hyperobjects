"""Per-parameter regression: every declared parameter must change the mesh.

A parameter that is declared in the manifest but does nothing to the geometry is
a lie told to the user — the baseline this cartridge replaces had two of them
(`legend_text` and `font_size` were inert because the legend itself was never
cut). This test renders the defaults, then perturbs one parameter at a time and
requires the result to differ.

Two parameters are exempt, and each says why:

  * `legend_text` and `font_size` are gated behind `legend_enabled`. They are
    checked twice: with the legend OFF they must NOT change the mesh (that is
    the gating contract), and with the legend ON they MUST change it.
  * `fn` is a tessellation hint. The B-Rep kernel is exact and the cartridge
    does not consume it, so it is checked as a declared no-op on the solid.

Run:
  <venv>/bin/python scripts/param_regression.py
Exit code 0 iff every parameter behaves as declared.
"""

import json
import math
import os
import sys

import cadquery as cq


HERE = os.path.dirname(os.path.abspath(__file__))
CART = os.path.dirname(HERE)
MAIN = os.path.join(CART, "main.py")
MANIFEST = os.path.join(CART, "project.json")

SRC = open(MAIN, encoding="utf-8").read()


def build(**params):
    g = {"__builtins__": __builtins__, "cq": cq, "math": math, "__name__": "__main__"}
    g.update(params)
    exec(SRC, g)  # noqa: S102 — mirrors cq_runner's exec
    return g["result"]


def signature(solid):
    """A cheap shape fingerprint: volume, area and the tight bounding box.

    Read from the exact solid, never from an exported mesh — export attaches a
    triangulation and the bounding box then measures the deflected mesh.
    """
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    sh = solid.val()
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(sh.wrapped, box, True, False)
    x0, y0, z0, x1, y1, z1 = box.Get()
    return (
        round(sh.Volume(), 5),
        round(sh.Area(), 5),
        round(x1 - x0, 5),
        round(y1 - y0, 5),
        round(z1 - z0, 5),
    )


DEFAULTS = {
    "profile_id": 0, "row_id": 1, "key_size_id": 0, "stem_type_id": 0,
    "legend_enabled": False, "legend_text": "A", "font_size": 6,
    "dish_depth": 1, "wall_thickness": 3, "keytop_thickness": 1,
    "stem_slop": 0.35, "fn": 0,
}

# One perturbation per parameter, inside the manifest's declared range.
PERTURB = {
    "profile_id": 2,
    "row_id": 4,
    "key_size_id": 3,
    "stem_type_id": 1,
    "legend_enabled": True,
    "dish_depth": 0,
    "wall_thickness": 5,
    "keytop_thickness": 2,
    "stem_slop": 0.6,
}
# Legend-gated: must be inert with the legend off, live with it on.
GATED = {"legend_text": "W", "font_size": 10}
# Declared no-op on the B-Rep.
TESSELLATION_ONLY = {"fn": 64}


def main():
    manifest = json.load(open(MANIFEST))
    declared = [p["id"] for p in manifest["parameters"]]

    base = signature(build(**DEFAULTS))
    failures = 0
    covered = set()

    for pid, value in PERTURB.items():
        covered.add(pid)
        params = dict(DEFAULTS, **{pid: value})
        sig = signature(build(**params))
        changed = sig != base
        print(f"{'ok  ' if changed else 'FAIL'} {pid:18} {DEFAULTS[pid]!r} -> {value!r}  changed={changed}")
        if not changed:
            failures += 1

    # Gating: off = inert, on = live.
    legend_on = dict(DEFAULTS, legend_enabled=True)
    base_on = signature(build(**legend_on))
    for pid, value in GATED.items():
        covered.add(pid)
        off = signature(build(**dict(DEFAULTS, **{pid: value})))
        on = signature(build(**dict(legend_on, **{pid: value})))
        inert_off = off == base
        live_on = on != base_on
        ok = inert_off and live_on
        print(
            f"{'ok  ' if ok else 'FAIL'} {pid:18} gated: inert with legend off={inert_off}, "
            f"changes with legend on={live_on}"
        )
        if not ok:
            failures += 1

    for pid, value in TESSELLATION_ONLY.items():
        covered.add(pid)
        sig = signature(build(**dict(DEFAULTS, **{pid: value})))
        # A tessellation hint must not change the solid.
        ok = sig == base
        print(f"{'ok  ' if ok else 'FAIL'} {pid:18} tessellation hint, solid unchanged={ok}")
        if not ok:
            failures += 1

    missing = [p for p in declared if p not in covered]
    if missing:
        print(f"FAIL parameters declared but not exercised: {missing}")
        failures += 1

    print(f"\nparameters={len(declared)} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
