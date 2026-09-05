"""Per-parameter regression: every declared parameter must change the mesh.

SPEC.md's requirement for this cartridge, stated plainly: a parameter the
manifest offers a user must do something. A slider that renders the same solid
at both ends is a lie in the UI, and the baseline shipped several of them (the
brace mode accepted `length_units` and ignored it; the fastener mode accepted
`arm_a_units` and ignored it). This cartridge scopes every parameter with
`visible_in_modes`, so the test is: within each mode a parameter is VISIBLE in,
perturbing it away from the default must change the rendered volume.

`fn` is exempt and asserted the other way: this is B-Rep geometry, so a
tessellation hint must NOT change the solid. It is kept in the manifest because
the platform's UI and the OpenSCAD-side cartridges share the control, and it
still drives mesh export density downstream.

Run:
  /path/to/yantra4d/.venv/bin/python docs/test_parameters_change_geometry.py
Exit code 0 iff every visible parameter moves the geometry.
"""

import json
import math
import os
import sys

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
CART = os.path.dirname(HERE)

# The value to perturb each parameter to, away from its manifest default.
PERTURB = {
    "length_units": 7,
    "width_units": 3,
    "height_units": 3,
    "holes_x": False,
    "holes_y": False,
    "holes_z": False,
    "arm_a_units": 6,
    "arm_b_units": 6,
    "thickness_units": 2,
    "holes_enabled": False,
    "fastener_type_id": 1,
    "fn": 32,
}

EXEMPT_UNCHANGED = {"fn"}  # B-Rep: a tessellation hint must not move the solid.


def volume(script, params):
    g = {"cq": cq, "math": math}
    g.update(params)
    exec(compile(script, "main.py", "exec"), g)  # noqa: S102 — same contract as cq_runner
    return g["result"].val().Volume()


def main():
    script = open(os.path.join(CART, "main.py")).read()
    manifest = json.load(open(os.path.join(CART, "project.json")))
    parts = {m["id"]: m["parts"][0] for m in manifest["modes"]}

    baseline = {}
    for mode, part in parts.items():
        baseline[mode] = volume(script, {"target_part": part})

    failures = 0
    checked = 0
    print(f"{'parameter':20s} {'mode':10s} {'baseline':>12s} {'perturbed':>12s}  verdict")
    for p in manifest["parameters"]:
        pid = p["id"]
        scopes = p.get("visible_in_modes") or list(parts)
        for mode in scopes:
            part = parts[mode]
            v = volume(script, {"target_part": part, pid: PERTURB[pid]})
            moved = abs(v - baseline[mode]) > 1e-9
            checked += 1
            if pid in EXEMPT_UNCHANGED:
                ok = not moved
                verdict = "ok (B-Rep: correctly unchanged)" if ok else "FAIL: changed the solid"
            else:
                ok = moved
                verdict = "ok" if ok else "FAIL: no effect on the geometry"
            if not ok:
                failures += 1
            print(f"{pid:20s} {mode:10s} {baseline[mode]:>12.3f} {v:>12.3f}  {verdict}")

    print()
    print(f"checks={checked} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
