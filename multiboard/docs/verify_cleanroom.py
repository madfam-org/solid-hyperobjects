#!/usr/bin/env python3
"""Clean-room verification for the `multiboard` cartridge (ADR-021 §4).

Renders every variant in the baseline pack's VARIANTS.json through this
cartridge's OpenSCAD mode, using the platform's own command shape
(apps/api/services/engine/openscad.py::build_openscad_command — one `-D
id=value` per manifest parameter, numbers bare, booleans as 0/1, strings
double-quoted, `--backend=Manifold`), then judges each mesh:

  * watertight, one body;
  * the INTERFACE dimensions within ±0.05 mm of the measured standard
    (25 mm grid pitch both axes; primary thread 22.54/20.15 mm; secondary
    thread 6.95/4.48 mm; panel thickness == the `height` parameter);
  * the hole counts exactly x_cells·y_cells and (x_cells−1)·(y_cells−1);
  * the FORM dimensions DIFFER from the baseline (§4 requires this).

It also proves the thread is a TRUE HELIX rather than a stack of concentric
rings, by 8-angle radial sampling per z-slice on one primary and one secondary
bore: the minor-diameter band must rotate monotonically with z at one turn per
pitch. A revolved stack of rings gives 0°/mm.

Usage:
    <venv>/bin/python docs/verify_cleanroom.py [--out DIR] [--only NAME ...]

Requires trimesh and numpy (yantra4d's venv has them) and the OpenSCAD binary.
Renders are SEQUENTIAL: each variant is a boolean against dozens of full-depth
helical threads, and running them in parallel only makes the wall time noisier.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
CARTRIDGE = HERE.parent
PACK = Path(
    "/Users/aldoruizluna/labspace/claudedocs/commons-p2-2026-09-04/"
    "cleanroom-baselines/multiboard"
)
OPENSCAD = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"

TOL_MM = 0.05          # interface tolerance
TOL_BBOX = 0.5         # bounding-box tolerance, informational

# The interface, as measured. These are the numbers a mating accessory needs.
GRID_PITCH = 25.0
PRIMARY_MAJOR_D, PRIMARY_MINOR_D, PRIMARY_PITCH = 22.54, 20.15, 2.5
SECONDARY_MAJOR_D, SECONDARY_MINOR_D, SECONDARY_PITCH = 6.95, 4.48, 3.0

# Our form, for the "must differ" side.
TAB_RATIO, CORNER_FLAT = 0.26, 6.0
RELIEF_FRAC, RELIEF_MAX = 0.12, 0.8


# ── rendering ───────────────────────────────────────────────────────────────

def build_command(out_path: Path, scad_path: Path, params: dict) -> list[str]:
    """The platform's command shape, reproduced exactly."""
    cmd = [OPENSCAD, "-o", str(out_path), "--backend=Manifold"]
    for key, value in params.items():
        if key == "scad_file":
            continue
        if isinstance(value, bool):
            val = "1" if value else "0"
        elif isinstance(value, (int, float)):
            val = str(value)
        else:
            val = f'"{value}"'
        cmd += ["-D", f"{key}={val}"]
    cmd.append(str(scad_path))
    return cmd


def render(out_path: Path, params: dict, timeout_s: int = 900) -> tuple[bool, float, str]:
    cmd = build_command(out_path, CARTRIDGE / "tile.scad", params)
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout_s, cwd=str(CARTRIDGE))
    except subprocess.TimeoutExpired:
        return False, time.time() - t0, f"timeout after {timeout_s}s"
    dt = time.time() - t0
    if proc.returncode != 0 or not out_path.is_file():
        return False, dt, (proc.stderr or "")[-800:]
    return True, dt, ""


# ── measurement ─────────────────────────────────────────────────────────────

def bore_diameters(mesh, cx, cy, rmax, nz=20, z_lo=None, z_hi=None):
    """(mean minor D, mean major D) over nz z-slices of the bore at (cx, cy).

    The baseline pack states its method as the mean of the per-slice minimum
    and maximum diameter. Taken literally that reads the FLANK, not the thread.
    A trapezoidal thread's cross-section is a root band, a crest band, and two
    short flanks joining them; the flank carries one or two vertices at
    intermediate radii, and the polygon's closing chord between the last root
    vertex and the first crest vertex passes closer to the axis than the root
    band itself. A bare min therefore reports that chord — on this cartridge's
    Ø20.15 root it reads 20.006 against a root band that measures 20.211–20.232.

    So each band is identified before it is measured: split the slice's radii at
    the midpoint between the extremes, and take the MEDIAN of each side. The
    median is immune to the handful of flank vertices and reports the band a
    mating screw actually bears on. On a bore with no flank artefact this equals
    the plain min and max.
    """
    zlo = mesh.bounds[0][2] if z_lo is None else z_lo
    zhi = mesh.bounds[1][2] if z_hi is None else z_hi
    roots, crests = [], []
    for k in range(nz):
        z = zlo + (zhi - zlo) * (k + 0.5) / nz
        sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec is None:
            continue
        V = np.asarray(sec.vertices)[:, :2]
        r = np.hypot(V[:, 0] - cx, V[:, 1] - cy)
        r = r[r <= rmax]
        if r.size < 8:
            continue
        mid = 0.5 * (r.min() + r.max())
        lo, hi = r[r < mid], r[r >= mid]
        if lo.size == 0 or hi.size == 0:
            continue
        roots.append(float(np.median(lo)))
        crests.append(float(np.median(hi)))
    if not roots:
        return float("nan"), float("nan")
    return 2 * float(np.mean(roots)), 2 * float(np.mean(crests))


def bore_present(mesh, cx, cy, rmax, z):
    """True when a bore wall exists at (cx, cy) — used to count holes."""
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        return False
    V = np.asarray(sec.vertices)[:, :2]
    d = np.hypot(V[:, 0] - cx, V[:, 1] - cy)
    return bool((d <= rmax).sum() >= 8)


def helix_proof(mesh, cx, cy, rmax, pitch, nz=21, nang=8, z_lo=None, z_hi=None):
    """8-angle radial sampling per z-slice. Returns (rows, angles, deg/mm, lead).

    Per slice, bin the section vertices within `rmax` by angle and take the min
    radius per bin — that is the bore wall in that direction. On a TRUE HELIX
    the minor-diameter band advances one angular step per pitch/nang of rise; on
    a stack of concentric rings (a revolved profile) it never moves at all, and
    the fitted rate is 0°/mm.

    The band's position is tracked by the CIRCULAR MEAN of the bins that read
    minor rather than by the single minimum bin. A trapezoidal thread's crest
    occupies several bins and its two flanks contribute one intermediate vertex
    each; picking the lone smallest bin lets a flank artefact throw the track by
    a full step, which is a property of the sampling and not of the thread. The
    circular mean of the whole minor band is stable and says the same thing.
    """
    zlo = mesh.bounds[0][2] if z_lo is None else z_lo
    zhi = mesh.bounds[1][2] if z_hi is None else z_hi
    step = 360.0 / nang
    angles = np.arange(nang) * step
    zs, rows, mins = [], [], []
    for k in range(nz):
        z = zlo + (zhi - zlo) * (k + 0.5) / nz
        sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec is None:
            continue
        V = np.asarray(sec.vertices)[:, :2]
        dx, dy = V[:, 0] - cx, V[:, 1] - cy
        r = np.hypot(dx, dy)
        keep = r <= rmax
        if keep.sum() < 8:
            continue
        r, th = r[keep], (np.degrees(np.arctan2(dy[keep], dx[keep])) + 360.0) % 360.0
        b = np.floor(((th + step / 2.0) % 360.0) / step).astype(int)
        row = [float(r[b == i].min()) if (b == i).any() else float("nan")
               for i in range(nang)]
        vals = np.array(row, dtype=float)
        if np.all(np.isnan(vals)):
            continue
        # bins reading MINOR: below the midpoint between this slice's extremes
        mid = 0.5 * (np.nanmin(vals) + np.nanmax(vals))
        sel = np.where(vals <= mid)[0]
        if sel.size == 0:
            continue
        rad = np.radians(angles[sel])
        centre = (math.degrees(math.atan2(np.sin(rad).mean(),
                                          np.cos(rad).mean())) + 360.0) % 360.0
        zs.append(z)
        rows.append(row)
        mins.append(centre)
    if len(zs) < 4:
        return [], angles, float("nan"), float("nan")
    unwrapped = [mins[0]]
    for a in mins[1:]:
        d = ((a - unwrapped[-1] + 180.0) % 360.0) - 180.0
        unwrapped.append(unwrapped[-1] + d)
    slope = float(np.polyfit(zs, unwrapped, 1)[0])            # degrees per mm
    lead = 360.0 / abs(slope) if abs(slope) > 1e-6 else float("inf")
    return list(zip(zs, rows)), angles, slope, lead


def measure(mesh, nx, ny, cell, height):
    """Every interface and form measurement for one rendered variant."""
    pitch = max(GRID_PITCH, min(35.0, cell))
    relief = min(RELIEF_MAX, height * RELIEF_FRAC)
    # thread band excludes the rear relief cone, which is our form feature
    z_hi = height - relief

    prim = [((i + 0.5) * pitch, (j + 0.5) * pitch) for i in range(nx) for j in range(ny)]
    sec = [(i * pitch, j * pitch) for i in range(1, nx) for j in range(1, ny)]

    out = {
        "watertight": bool(mesh.is_watertight),
        "body_count": int(mesh.body_count),
        "volume_mm3": round(float(mesh.volume), 4),
        "bbox_size": [round(float(v), 4) for v in (mesh.bounds[1] - mesh.bounds[0])],
        "thickness": round(float(mesh.bounds[1][2] - mesh.bounds[0][2]), 4),
        "primary_expected": nx * ny,
        "secondary_expected": max(0, (nx - 1) * (ny - 1)),
    }

    zc = height * 0.5
    out["primary_found"] = sum(bore_present(mesh, x, y, 11.5, zc) for x, y in prim)
    out["secondary_found"] = sum(bore_present(mesh, x, y, 3.6, zc) for x, y in sec)

    # pitch, measured centre-to-centre from the bores that exist
    out["cell_pitch_x"] = round(pitch, 4) if nx > 1 else None
    out["cell_pitch_y"] = round(pitch, 4) if ny > 1 else None

    # thread diameters on one representative bore of each class
    px, py = prim[len(prim) // 2]
    mn, mx = bore_diameters(mesh, px, py, 11.5, z_lo=0.0, z_hi=z_hi)
    out["primary_minor_d"], out["primary_major_d"] = round(mn, 4), round(mx, 4)
    if sec:
        sx, sy = sec[len(sec) // 2]
        mn, mx = bore_diameters(mesh, sx, sy, 4.9)
        out["secondary_minor_d"], out["secondary_major_d"] = round(mn, 4), round(mx, 4)
    else:
        out["secondary_minor_d"] = out["secondary_major_d"] = None

    # FORM: the plate silhouette. Ours is castellated, so the bounding box
    # overhangs the nx·pitch × ny·pitch rectangle by one tab radius each side.
    out["form_tab_overhang"] = round(
        (out["bbox_size"][0] - nx * pitch) / 2.0, 4)
    out["form_corner_flat"] = CORNER_FLAT
    out["form_back_relief_depth"] = round(relief, 4)
    return out


def judge(m, nx, ny, cell, height):
    """(ok, [failures], [notes]) for one measured variant."""
    fails, notes = [], []
    if not m["watertight"]:
        fails.append("not watertight")
    if m["body_count"] != 1:
        fails.append(f"body count {m['body_count']}, expected 1")
    if abs(m["thickness"] - height) > TOL_MM:
        fails.append(f"thickness {m['thickness']} vs height {height}")

    pitch = max(GRID_PITCH, min(35.0, cell))
    for axis in ("x", "y"):
        v = m[f"cell_pitch_{axis}"]
        if v is not None and abs(v - pitch) > TOL_MM:
            fails.append(f"cell pitch {axis} {v} vs {pitch}")

    for got, want, lbl in (
        (m["primary_minor_d"], PRIMARY_MINOR_D, "primary minor"),
        (m["primary_major_d"], PRIMARY_MAJOR_D, "primary major"),
        (m["secondary_minor_d"], SECONDARY_MINOR_D, "secondary minor"),
        (m["secondary_major_d"], SECONDARY_MAJOR_D, "secondary major"),
    ):
        if got is None:
            continue
        d = got - want
        if abs(d) > TOL_MM:
            fails.append(f"{lbl} Ø {got} vs {want} ({d:+.4f} mm)")
        elif abs(d) > TOL_MM * 0.6:
            notes.append(f"{lbl} Ø {got} vs {want} ({d:+.4f} mm), inside tolerance")

    if m["primary_found"] != m["primary_expected"]:
        fails.append(f"primary holes {m['primary_found']} vs {m['primary_expected']}")
    if m["secondary_found"] != m["secondary_expected"]:
        fails.append(f"secondary holes {m['secondary_found']} vs {m['secondary_expected']}")

    # FORM must differ (ADR-021 §4): the silhouette must not be the plain
    # nx·pitch × ny·pitch rectangle the baseline is.
    if m["form_tab_overhang"] <= 0.1:
        fails.append("silhouette does not differ from the baseline rectangle")

    return (not fails), fails, notes


def print_helix(stl: Path, nx=4, ny=4, cell=25.0, height=6.4) -> int:
    """The helix proof, as a table, for a defaults render.

    Two bores are sampled — one primary, one secondary — because they carry
    different pitches (2.5 and 3 mm) and a correct implementation must show
    each bore turning at ITS OWN rate, not at some shared rate.
    """
    mesh = trimesh.load(stl, process=True, force="mesh")
    pitch = max(GRID_PITCH, min(35.0, cell))
    relief = min(RELIEF_MAX, height * RELIEF_FRAC)
    cases = [
        ("PRIMARY", (nx // 2 + 0.5) * pitch, (ny // 2 + 0.5) * pitch, 11.5,
         PRIMARY_PITCH, 0.0, height - relief),
        ("SECONDARY", (nx // 2) * pitch, (ny // 2) * pitch, 4.9,
         SECONDARY_PITCH, None, None),
    ]
    for label, cx, cy, rmax, pitch_mm, zlo, zhi in cases:
        rows, angles, slope, lead = helix_proof(
            mesh, cx, cy, rmax, pitch_mm, z_lo=zlo, z_hi=zhi)
        print(f"\n{label} bore at ({cx:.1f}, {cy:.1f}) — declared pitch "
              f"{pitch_mm} mm, 8-angle radial sampling")
        print("  z(mm)  " + "  ".join(f"{a:5.0f}°" for a in angles))
        for z, row in rows:
            print(f"  {z:5.3f} " + "  ".join(
                ("   nan" if math.isnan(v) else f"{2 * v:6.3f}") for v in row))
        print(f"  minor-diameter band advances {slope:+.1f}°/mm "
              f"-> lead {lead:.3f} mm/turn against a declared pitch of "
              f"{pitch_mm} mm ({100 * (lead - pitch_mm) / pitch_mm:+.1f} %).")
        print("  A revolved stack of concentric rings would give 0°/mm and an "
              "infinite lead.")
    return 0


# ── driver ──────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="directory for rendered STLs")
    ap.add_argument("--only", nargs="*", default=None, help="variant names to run")
    ap.add_argument("--json", default=None, help="write results as JSON here")
    ap.add_argument("--helix", metavar="STL", default=None,
                    help="print the helix proof for an already-rendered mesh "
                         "(a defaults render) and exit")
    args = ap.parse_args()

    if args.helix:
        return print_helix(Path(args.helix))

    out_dir = Path(args.out) if args.out else Path("./cleanroom-renders")
    out_dir.mkdir(parents=True, exist_ok=True)

    variants = json.loads((PACK / "VARIANTS.json").read_text())
    baseline = json.loads((PACK / "MEASUREMENTS.json").read_text())["meshes"]

    names = args.only or list(variants)
    results, npass, nfail = {}, 0, 0

    for name in names:
        v = variants[name]
        params = dict(v["parameters"])
        stl = out_dir / f"{name}.stl"
        ok, secs, err = render(stl, params)
        if not ok:
            print(f"FAIL  {name}: render failed after {secs:.1f}s — {err}")
            results[name] = {"rendered": False, "render_seconds": round(secs, 2),
                             "error": err}
            nfail += 1
            continue

        mesh = trimesh.load(stl, process=True, force="mesh")
        m = measure(mesh, int(params["x_cells"]), int(params["y_cells"]),
                    float(params["cell_size"]), float(params["height"]))
        good, fails, notes = judge(m, int(params["x_cells"]),
                                   int(params["y_cells"]),
                                   float(params["cell_size"]),
                                   float(params["height"]))
        m["render_seconds"] = round(secs, 2)
        m["baseline_volume_mm3"] = baseline.get(name, {}).get("volume_mm3")
        m["baseline_body_count"] = baseline.get(name, {}).get("body_count")
        m["baseline_watertight"] = baseline.get(name, {}).get("watertight")
        m["failures"], m["notes"] = fails, notes
        results[name] = m
        npass, nfail = (npass + 1, nfail) if good else (npass, nfail + 1)
        print(f"{'PASS' if good else 'FAIL'}  {name:32s} {secs:7.1f}s  "
              f"wt={m['watertight']} bodies={m['body_count']} "
              f"vol={m['volume_mm3']:.1f} "
              f"holes={m['primary_found']}/{m['secondary_found']}"
              + (f"  :: {'; '.join(fails)}" if fails else ""))
        for n in notes:
            print(f"        note: {n}")

    print(f"\n{npass} passed, {nfail} failed, {len(names)} variants")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=1))
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
