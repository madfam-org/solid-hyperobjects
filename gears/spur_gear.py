"""Spur gear (CadQuery twin of spur_gear.scad).

`spur_gear.scad` calls BOSL2 `spur_gear()`, whose 2D cross-section comes from
`_gear_tooth_profile()` in `libs/BOSL2/gears.scad` (pinned at v2.0.753 /
`fcfce7c7`).  This file ports that construction so both kernels sample the SAME
curve rather than two approximations that happen to share an outside diameter.

The tooth is a real ISO 53 / DIN 867 involute: the involute of the base circle
`pr*cos(atan(tan(PA)/cos(helical)))`, with BOSL2's automatic profile shift, the
trochoidal undercut a meshing rack would carve, the rounded clearance valley at
the root, the tip cap, the jaggy strip and the self-intersection clip.  The one
deliberate difference from BOSL2 is its closing `resample_path(n=2*steps,
keep_corners=30)` — a vertex-REDUCTION pass over the same polyline.  We keep the
full-resolution samples, so BOSL2's coarser polygon is inscribed in ours and the
residual two-way Hausdorff distance (19-39 um at every preset) is BOSL2's own
chord error, not a construction difference.

The sandbox (`apps/api/services/engine/cq_runner.py`) blocks `sys`, so a
cartridge cannot put its own directory on `sys.path`; the profile code is
therefore inlined here rather than imported from a sibling module.  It is kept
byte-identical to the copy in `herringbone_gear.py`.
"""

import cadquery as cq
import json
import argparse
import math


# ── BOSL2 gears.scad port (degrees throughout, as in OpenSCAD) ───────────────

def _sin(a):
    return math.sin(math.radians(a))


def _cos(a):
    return math.cos(math.radians(a))


def _tan(a):
    return math.tan(math.radians(a))


def _atan(x):
    return math.degrees(math.atan(x))


def _atan2(y, x):
    return math.degrees(math.atan2(y, x))


def _polar_to_xy(r, a):
    return (r * _cos(a), r * _sin(a))


def _xy_to_polar(x, y):
    return (math.hypot(x, y), _atan2(y, x))


def _lookup(x, tbl):
    """OpenSCAD `lookup()`: piecewise-linear over `[key, value]` rows, clamped
    past both ends.  Every table built here is monotone in the key."""
    tbl = sorted(tbl, key=lambda p: p[0])
    if x <= tbl[0][0]:
        return tbl[0][1]
    if x >= tbl[-1][0]:
        return tbl[-1][1]
    for i in range(len(tbl) - 1):
        x0, y0 = tbl[i]
        x1, y1 = tbl[i + 1]
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tbl[-1][1]


def auto_profile_shift(teeth, pressure_angle=20.0, helical=0.0, profile_shift="auto"):
    """BOSL2 `auto_profile_shift()` — gears below the undercut limit get a
    positive shift so their teeth are not undercut away."""
    if profile_shift != "auto":
        return float(profile_shift)
    if teeth == 0:
        return 0.0
    pa = _atan(_tan(pressure_angle) / _cos(helical))
    min_teeth = 2.0 / (_sin(pa) ** 2)
    if teeth > math.floor(min_teeth):
        return 0.0
    return (1.0 - (teeth / min_teeth)) / _cos(helical)


def pitch_radius(mod, teeth, helical=0.0):
    """Transverse pitch radius.  `mod` is the NORMAL module, as BOSL2 takes it,
    so a helical gear's cross-section grows by 1/cos(helical)."""
    return mod * teeth / 2.0 / _cos(helical)


def _adendum(mod, profile_shift=0.0, shorten=0.0):
    return mod * (1.0 + profile_shift - shorten)


def _dedendum(mod, clearance=None, profile_shift=0.0):
    clear = 0.25 * mod if clearance is None else clearance
    return mod * (1.0 - profile_shift) + clear


def outer_radius(mod, teeth, helical=0.0, profile_shift=0.0, shorten=0.0):
    return pitch_radius(mod, teeth, helical) + _adendum(mod, profile_shift, shorten)


def root_radius_basic(mod, teeth, clearance=None, helical=0.0, profile_shift=0.0):
    return pitch_radius(mod, teeth, helical) - _dedendum(mod, clearance, profile_shift)


def base_radius(mod, teeth, pressure_angle=20.0, helical=0.0):
    trans_pa = _atan(_tan(pressure_angle) / _cos(helical))
    return pitch_radius(mod, teeth, helical) * _cos(trans_pa)


def _line_intersection(l1, l2):
    (x1, y1), (x2, y2) = l1[0], l1[1]
    (x3, y3), (x4, y4) = l2[0], l2[1]
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-12:
        return None
    a = x1 * y2 - y1 * x2
    b = x3 * y4 - y3 * x4
    return ((a * (x3 - x4) - (x1 - x2) * b) / den,
            (a * (y3 - y4) - (y1 - y2) * b) / den)


def _vector_angle(p0, p1, p2):
    """Interior angle (deg) at `p1` of the corner p0-p1-p2."""
    v1 = (p0[0] - p1[0], p0[1] - p1[1])
    v2 = (p2[0] - p1[0], p2[1] - p1[1])
    n1 = math.hypot(*v1)
    n2 = math.hypot(*v2)
    if n1 < 1e-12 or n2 < 1e-12:
        return 0.0
    c = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
    return math.degrees(math.acos(c))


def _arc_corner(n, r, corner):
    """BOSL2 `arc(n=, r=, corner=[p0,p1,p2])` — the radius-`r` fillet tucked
    into the corner, running from the p0 leg round to the p2 leg."""
    p0, p1, p2 = corner
    ang = _vector_angle(p0, p1, p2)
    if ang <= 0.0 or ang >= 180.0:
        return [p1]
    d = r / _tan(ang / 2.0)
    u1 = (p0[0] - p1[0], p0[1] - p1[1])
    n1 = math.hypot(*u1)
    u1 = (u1[0] / n1, u1[1] / n1)
    u2 = (p2[0] - p1[0], p2[1] - p1[1])
    n2 = math.hypot(*u2)
    u2 = (u2[0] / n2, u2[1] / n2)
    t1 = (p1[0] + u1[0] * d, p1[1] + u1[1] * d)
    t2 = (p1[0] + u2[0] * d, p1[1] + u2[1] * d)
    bis = (u1[0] + u2[0], u1[1] + u2[1])
    nb = math.hypot(*bis)
    if nb < 1e-12:
        return [p1]
    bis = (bis[0] / nb, bis[1] / nb)
    cd = r / _sin(ang / 2.0)
    cp = (p1[0] + bis[0] * cd, p1[1] + bis[1] * cd)
    a1 = _atan2(t1[1] - cp[1], t1[0] - cp[0])
    a2 = _atan2(t2[1] - cp[1], t2[0] - cp[0])
    da = ((a2 - a1 + 180.0) % 360.0) - 180.0  # the short way round
    return [(cp[0] + r * _cos(a1 + da * i / (n - 1)),
             cp[1] + r * _sin(a1 + da * i / (n - 1))) for i in range(n)]


def _deduplicate(path, eps=1e-9):
    out = []
    for p in path:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append(p)
    return out


def gear_tooth_profile(mod, teeth, pressure_angle=20.0, clearance=None,
                       backlash=0.0, helical=0.0, profile_shift=0.0,
                       shorten=0.0, steps=16):
    """One external involute tooth, centred on +Y, in BOSL2's own point order
    (root valley, left flank, tip cap, right flank, root valley).  Port of
    BOSL2 `_gear_tooth_profile()` for `internal=false`, which is all this
    cartridge builds.  `steps` is BOSL2's `$gear_steps` (default 16)."""
    circ_pitch = mod * math.pi
    clear = 0.25 * mod if clearance is None else clearance

    arad = outer_radius(mod, teeth, helical, profile_shift, shorten)
    prad = pitch_radius(mod, teeth, helical)
    brad = base_radius(mod, teeth, pressure_angle, helical)
    rrad = root_radius_basic(mod, teeth, clear, helical, profile_shift)

    # Tooth thickness at the pitch circle, carried as the half-angle `tang`.
    tthick = (circ_pitch / math.pi / _cos(helical)
              * (math.pi / 2.0 + 2.0 * profile_shift * _tan(pressure_angle))
              - backlash)
    tang = tthick / prad / 2.0 * 180.0 / math.pi

    def involute(base_r, a):
        b = math.radians(a)
        return (base_r * (_cos(a) + b * _sin(a)),
                base_r * (_sin(a) - b * _cos(a)))

    # radius -> (90 - polar angle) along the involute, sampled every 5 deg of
    # roll, exactly as BOSL2 builds the table.
    involute_lup = []
    i = 0.0
    limit = arad / math.pi / brad * 360.0
    while i <= limit + 1e-12:
        r_, a_ = _xy_to_polar(*involute(brad, i))
        if r_ <= arad * 1.1:
            involute_lup.append([r_, 90.0 - a_])
        i += 5.0
    involute_rlup = [[b, a] for (a, b) in involute_lup]  # the reverse table

    soff = tang + (_lookup(brad, involute_lup) - _lookup(prad, involute_lup))
    ma_rad = min(arad, _lookup(90.0 - soff + 0.05 * 360.0 / teeth / 2.0, involute_rlup))
    ma_ang = _lookup(ma_rad, involute_lup)
    cap_steps = int(math.ceil((ma_ang + soff - 90.0) / 5.0))
    cap_step = (ma_ang + soff - 90.0) / cap_steps if cap_steps else 0.0

    # `ang_adj_to_opp(pressure_angle, circ_pitch/PI)` == (circ_pitch/PI)*tan(PA)
    ax = circ_pitch / 4.0 - (circ_pitch / math.pi) * _tan(pressure_angle)

    # The undercut a meshing rack would carve out of this tooth.
    undercut = []
    a = _atan2(ax, rrad)
    while a >= -90.0:
        x = -a / 360.0 * 2.0 * math.pi * prad + ax
        y = prad - circ_pitch / math.pi + profile_shift * circ_pitch / math.pi
        r_, a_ = _xy_to_polar(x, y)
        if r_ < arad * 1.05:
            undercut.append([r_, a_ - a + 180.0 / teeth])
        a -= 1.0
    if undercut:
        uc_min = min(range(len(undercut)), key=lambda k: undercut[k][0])
        undercut_lup = undercut[uc_min:]
    else:
        undercut_lup = []

    us = [k / steps / 2.0 for k in range(steps * 2 + 1)]

    def _flank_angle(r):
        """Inner envelope of the involute flank and the rack undercut."""
        a1 = _lookup(r, involute_lup) + soff
        if not undercut_lup or r < undercut_lup[0][0]:
            return a1, False
        a2 = _lookup(r, undercut_lup)
        return min(a1, a2), a1 > a2

    undercut_max = 0.0
    for u in us:
        r = rrad + (ma_rad - rrad) * u
        aa, cut = _flank_angle(r)
        if aa < 90.0 + 180.0 / teeth and cut:
            undercut_max = max(undercut_max, r)

    raw = []
    for u in us:
        r = rrad + (ma_rad - rrad) * u
        aa, _cut = _flank_angle(r)
        if r > (rrad + clear) and aa < 90.0 + 180.0 / teeth:
            raw.append(_polar_to_xy(r, aa))
    for k in range(cap_steps):
        raw.append(_polar_to_xy(ma_rad, ma_ang + soff - k * (cap_step - 1.0)))
    tooth_half_raw = _deduplicate(raw)

    # Round out the clearance valley where the flank meets the root circle.
    rcircum = 2.0 * math.pi * rrad
    rpart = (180.0 / teeth - tang) / 360.0
    line1 = [tooth_half_raw[0], tooth_half_raw[1]]
    zr = 180.0 / teeth  # BOSL2: zrot(180/teeth, p=[[0,rrad],[1,rrad]])
    line2 = [(-rrad * _sin(zr), rrad * _cos(zr)),
             (_cos(zr) - rrad * _sin(zr), _sin(zr) + rrad * _cos(zr))]
    isect_pt = _line_intersection(line1, line2)
    rcorner = [line2[0], isect_pt, line1[0]]
    maxr = (math.hypot(rcorner[0][0] - rcorner[1][0], rcorner[0][1] - rcorner[1][1])
            * _tan(_vector_angle(*rcorner) / 2.0))
    round_r = min(maxr, clear, rcircum * rpart)
    valley = _arc_corner(8, round_r, rcorner) if round_r > 0 else [isect_pt]
    rounded = _deduplicate(list(valley) + tooth_half_raw)

    # Strip "jaggies" left where the undercut crosses back over the flank.
    def _strip_left(path, i):
        out = []
        while i < len(path):
            out.append(path[i])
            if math.hypot(*path[i]) >= undercut_max:
                out.extend(path[i + 1:])
                return out
            angs = [_atan2(path[j][1] - path[i][1], path[j][0] - path[i][0])
                    for j in range(i + 1, len(path))
                    if math.hypot(*path[j]) < undercut_max]
            if not angs:
                i += 1
            else:
                i += min(range(len(angs)), key=lambda k: angs[k]) + 1
        return out

    tooth_half = rounded if not undercut_max else _strip_left(rounded, 0)

    # Clip any self-intersection past the tooth's angular half-pitch.
    invalid = [k for k, p in enumerate(tooth_half)
               if _atan2(p[1], p[0]) > 90.0 + 180.0 / teeth]
    if invalid and invalid[-1] + 1 < len(tooth_half):
        ind = invalid[-1]
        ipt = _line_intersection([(0.0, 0.0), _polar_to_xy(1.0, 90.0 + 180.0 / teeth)],
                                 [tooth_half[ind], tooth_half[ind + 1]])
        clipped = [ipt] + list(tooth_half[ind + 1:])
    else:
        clipped = tooth_half

    # Mirror across X to complete the tooth (BOSL2's `xflip` + `reverse`).
    return _deduplicate(list(clipped) + [(-x, y) for (x, y) in reversed(clipped)])


def gear_outline(mod, teeth, pressure_angle=20.0, helical=0.0, clearance=None,
                 backlash=0.0, profile_shift="auto", shorten=0.0, steps=16):
    """The full closed gear cross-section: one tooth repeated `teeth` times by
    `zrot(-i*360/teeth)`, exactly as BOSL2's `spur_gear2d()` assembles `perim`.
    Returns (x, y) tuples ready for `cq.Workplane("XY").polyline(...)`."""
    ps = auto_profile_shift(teeth, pressure_angle, helical, profile_shift)
    tooth = gear_tooth_profile(mod=mod, teeth=teeth, pressure_angle=pressure_angle,
                               clearance=clearance, backlash=backlash,
                               helical=helical, profile_shift=ps,
                               shorten=shorten, steps=steps)
    pts = []
    for i in range(teeth):
        a = -i * 360.0 / teeth
        ca, sa = _cos(a), _sin(a)
        pts.extend([(x * ca - y * sa, x * sa + y * ca) for (x, y) in tooth])
    return _deduplicate(pts)


# ── the part ─────────────────────────────────────────────────────────────────

def build(params):
    teeth_count = int(params.get('teeth_count', 20))
    module_size = float(params.get('module_size', 2.0))
    thickness = float(params.get('thickness', 5.0))
    bore_diameter = float(params.get('bore_diameter', 5.0))
    pressure_angle = float(params.get('pressure_angle', 20.0))

    # ONE closed 2D wire for the whole gear, extruded once — no per-tooth
    # solids to union (gotcha #37: build the outline as one region).
    #
    # BOSL2's spur_gear() is `attachable(anchor=CENTER)` with
    # `linear_extrude(height=thickness, center=true)`, so the SCAD twin spans
    # [-thickness/2, +thickness/2].  Parity's Hausdorff gate compares raw
    # vertices with NO alignment step, so the CadQuery side has to sit at the
    # same Z, not merely have the same height.
    pts = gear_outline(mod=module_size, teeth=teeth_count,
                       pressure_angle=pressure_angle, helical=0.0)
    gear = (cq.Workplane("XY", origin=(0, 0, -thickness / 2.0))
            .polyline(pts).close().extrude(thickness))

    if bore_diameter > 0:
        # BOSL2's spur_gear(shaft_diam=) subtracts the bore from the same 2D
        # region before extruding; cutting a through-bore is equivalent, and
        # the cutter overshoots both faces by 1 mm (gotcha #26).
        bore = (cq.Workplane("XY").circle(bore_diameter / 2.0)
                .extrude(thickness + 2)
                .translate((0, 0, -thickness / 2.0 - 1.0)))
        gear = gear.cut(bore)

    return gear.clean()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()

    params = json.loads(args.params)
    res = build(params)

    if args.out:
        cq.exporters.export(res, args.out)
