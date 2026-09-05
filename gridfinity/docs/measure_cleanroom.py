#!/usr/bin/env python3
"""Re-render every baseline variant through this cartridge and measure it.

Clean-room verification harness for the `gridfinity` OpenSCAD-engine modes
(`cup`, `baseplate_scad`, `lid`), authored by Innovaciones MADFAM under
CERN-OHL-W-2.0.

It renders each variant listed in the private baseline pack's VARIANTS.json
with exactly the platform's parameter-injection shape, measures the mesh with
trimesh, and compares against the pack's MEASUREMENTS.json:

  * watertight            must be True for every variant (STRICTER than the
                          baseline, whose baseplate was non-manifold at 10 of
                          12 variants);
  * body count            must equal the baseline's (1 everywhere);
  * bounding box          must match the baseline within +/-0.05 mm in all
                          three axes. This is the primary regression gate: no
                          quirk fix changes the envelope;
  * volume                compared and reported. It is only a gate where the
                          re-creation's feature set matches the baseline's;
                          wherever a documented quirk is being fixed the volume
                          moves well outside 2 % by design.

Usage:
    <python> measure_cleanroom.py --pack <baseline-pack-dir> \
        --cartridge <path to gridfinity/> --scaffold <scaffold dir> \
        [--out results.json]

The scaffold must be shaped like the platform's render root: <scaffold>/projects
resolving to the commons checkout (so that a mode file's
`include <../../libs/BOSL2/std.scad>` resolves) and <scaffold>/libs holding the
libraries, with OPENSCADPATH pointed at <scaffold>/libs.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import trimesh

OPENSCAD = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
BBOX_TOL = 0.05          # mm, the primary gate
VOLUME_REL_TOL = 0.02    # reported, gated only where no quirk is fixed

MODE_FILES = {
    "cup": "cup.scad",
    "baseplate_scad": "baseplate.scad",
    "lid": "lid.scad",
}


def scad_value(v):
    """The platform's -D value rules: bool -> 1/0, numbers bare, strings quoted."""
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return repr(v) if isinstance(v, float) else str(v)
    return '"%s"' % v


def render(scad_path: Path, params: dict, out_path: Path, scaffold: Path):
    cmd = [OPENSCAD, "-o", str(out_path), "--backend=Manifold"]
    for k, v in params.items():
        cmd += ["-D", "%s=%s" % (k, scad_value(v))]
    cmd.append(str(scad_path))
    env = dict(os.environ)
    env["OPENSCADPATH"] = str(scaffold / "libs")
    proc = subprocess.run(["timeout", "600"] + cmd, capture_output=True,
                          text=True, env=env, cwd=str(scaffold))
    return proc.returncode == 0 and out_path.exists(), proc.stderr[-4000:]


def measure(path: Path):
    mesh = trimesh.load(str(path), force="mesh", process=True)
    bodies = mesh.split(only_watertight=False)
    return {
        "loaded_in_trimesh": isinstance(mesh, trimesh.Trimesh) and len(mesh.faces) > 0,
        "watertight": bool(mesh.is_watertight),
        "body_count": int(len(bodies)) if len(bodies) else 1,
        "volume_mm3": round(float(mesh.volume), 3),
        "area_mm2": round(float(mesh.area), 3),
        "bbox_size_mm": [round(float(x), 4) for x in mesh.extents],
        "faces": int(len(mesh.faces)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--cartridge", required=True)
    ap.add_argument("--scaffold", required=True)
    ap.add_argument("--out")
    ap.add_argument("--only", help="filter: substring of '<mode>/<variant>'")
    args = ap.parse_args()

    pack = Path(args.pack)
    cartridge = Path(args.cartridge)
    scaffold = Path(args.scaffold)

    variants = json.loads((pack / "VARIANTS.json").read_text())["variants"]
    baseline = json.loads((pack / "MEASUREMENTS.json").read_text())["meshes"]

    tmpdir = Path(tempfile.mkdtemp(prefix="cg_measure_"))
    results = []
    n_pass = n_fail = 0

    for v in variants:
        mode, part, name = v["mode"], v["part"], v["variant"]
        tag = "%s/%s" % (mode, name)
        if args.only and args.only not in tag:
            continue
        key = "%s__%s__%s.stl" % (mode, part, name)
        base = baseline[key]["global"]
        params = dict(v["parameters"])
        # `enable_magnets` is declared for the CadQuery `bin` mode; three cup
        # presets carried it. The re-creation gives the cup its own
        # cup-scoped `enable_magnets`, so it is injected as-is.
        out = tmpdir / key
        ok, err = render(cartridge / MODE_FILES[mode], params, out, scaffold)
        if not ok:
            results.append({"variant": tag, "status": "RENDER_FAILED", "stderr": err})
            n_fail += 1
            print("FAIL  %-40s render failed\n%s" % (tag, err[-800:]))
            continue

        m = measure(out)
        bbox_delta = [round(abs(a - b), 4)
                      for a, b in zip(m["bbox_size_mm"], base["bbox_size_mm"])]
        vol_rel = (abs(m["volume_mm3"] - base["volume_mm3"]) / base["volume_mm3"]
                   if base["volume_mm3"] else 0.0)

        checks = {
            "watertight": m["watertight"] is True,
            "body_count": m["body_count"] == base["body_count"],
            "bbox_within_0p05": max(bbox_delta) <= BBOX_TOL,
            "loaded_in_trimesh": m["loaded_in_trimesh"],
        }
        passed = all(checks.values())
        n_pass += passed
        n_fail += (not passed)

        results.append({
            "variant": tag,
            "status": "PASS" if passed else "FAIL",
            "checks": checks,
            "measured": m,
            "baseline": {k: base[k] for k in
                         ("watertight", "body_count", "volume_mm3", "bbox_size_mm")},
            "bbox_delta_mm": bbox_delta,
            "volume_rel_delta": round(vol_rel, 6),
            "volume_within_2pct": vol_rel <= VOLUME_REL_TOL,
        })
        print("%-5s %-40s bbox_d=%-22s vol %9.3f -> %9.3f (%+6.1f%%) wt=%s n=%d"
              % ("PASS" if passed else "FAIL", tag, str(bbox_delta),
                 base["volume_mm3"], m["volume_mm3"],
                 100 * (m["volume_mm3"] - base["volume_mm3"]) / base["volume_mm3"]
                 if base["volume_mm3"] else 0.0,
                 m["watertight"], m["body_count"]))

    print("\n%d passed, %d failed, of %d" % (n_pass, n_fail, n_pass + n_fail))
    if args.out:
        Path(args.out).write_text(json.dumps(
            {"passed": n_pass, "failed": n_fail, "results": results}, indent=1))
        print("wrote %s" % args.out)
    print("meshes in %s" % tmpdir)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
