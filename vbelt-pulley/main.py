"""
V-Belt / Round-Belt Pulley — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A friction-drive pulley (sheave) for A-section V-belts or for O-ring / round
belts, and an idler sheave for rope, cord or cable. The rim carries one or more
grooves cut as bodies of revolution about the pulley axis (Z):

  * "A/13" — a classic A-section V-belt groove: a ~40° included-angle V, ~13 mm
             wide at the top (ISO 4183 A / SPZ family). The belt wedges into the
             V and drives by friction on the flanks. Built as the union of two
             coaxial cones so the channel is exactly a revolved triangle.
  * round  — a semicircular groove sized to a round belt / O-ring of `belt_dia`,
             built as a torus of the belt radius centred on the rim circle.
  * rope   — a deep throat for a rope, cord or cable of `rope_dia`: a round
             bottom slightly wider than the rope (radius 0.53 x rope_dia) so the
             rope is cradled and not pinched, and two straight flanks at
             `throat_angle` that rise 1.25 x rope_dia above the tread so the rope
             sits below the rim. It is sized by the tread diameter (where the
             rope sits), because that is what bends the rope.

Modes (dispatched via `target_part`):
  * "vbelt"        — a single V-groove sheave with an optional set-screw hub.
  * "roundbelt"    — a single semicircular groove for a round belt / O-ring.
  * "multi_groove" — a stacked V-belt sheave with `grooves` parallel V-grooves.
  * "rope_sheave"  — an idler sheave with one rope throat and a plain bore for a
                     bearing, a bushing or an axle. No hub: it turns on its axle.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `outer_dia`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.
"""

import cadquery as cq
import math


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default.
    `except Exception` catches the NameError raised for an unbound param name
    (the sandbox does not expose globals()/NameError directly)."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
belt_profile = str(  PARAM(lambda: belt_profile, "A/13"))  # "A/13" | "roundbelt"
outer_dia    = float(PARAM(lambda: outer_dia,     60.0))   # rim outer diameter, mm
groove_angle = float(PARAM(lambda: groove_angle,  40.0))   # V included angle, deg
groove_width = float(PARAM(lambda: groove_width,  13.0))   # V top width (A-section ≈ 13)
groove_depth = float(PARAM(lambda: groove_depth,  11.0))   # V radial depth, mm
belt_dia     = float(PARAM(lambda: belt_dia,       5.0))   # round belt / O-ring dia, mm
grooves      = int(  PARAM(lambda: grooves,          2))   # groove count (multi)
groove_pitch = float(PARAM(lambda: groove_pitch,  15.0))   # spacing between grooves, mm
bore         = float(PARAM(lambda: bore,           8.0))   # shaft bore diameter, mm
hub          = bool( PARAM(lambda: hub,           True))   # set-screw hub
hub_dia      = float(PARAM(lambda: hub_dia,       22.0))   # hub outer diameter, mm
hub_height   = float(PARAM(lambda: hub_height,     8.0))   # hub height, mm
setscrew     = bool( PARAM(lambda: setscrew,      True))   # radial set-screw hole
setscrew_dia = float(PARAM(lambda: setscrew_dia,   4.2))   # set-screw clearance (≈ M4)
tread_dia    = float(PARAM(lambda: tread_dia,     80.0))   # rope sheave: diameter the rope sits on
rope_dia     = float(PARAM(lambda: rope_dia,       5.0))   # rope / cord / cable diameter, mm
throat_angle = float(PARAM(lambda: throat_angle,  45.0))   # rope throat included angle, deg

target_part = str(  PARAM(lambda: target_part, "vbelt"))   # vbelt|roundbelt|multi_groove|rope_sheave

bore_raw = bore   # the rope sheave clamps the bore against its own tread, not outer_dia


# ── Derived / clamped geometry ───────────────────────────────────────────────
outer_dia = max(16.0, outer_dia)
outer_r = outer_dia / 2.0
bore = max(2.0, min(bore, outer_dia - 6.0))
bore_r = bore / 2.0
CLR = 0.10

groove_angle = max(20.0, min(groove_angle, 60.0))
groove_depth = max(2.0, min(groove_depth, outer_r - 3.0))
belt_dia = max(1.5, min(belt_dia, outer_r - 3.0))
# A-section top width, but never wider than what the included angle implies for
# this depth, and never wider than the rim can hold.
angle_top = 2.0 * math.tan(math.radians(groove_angle / 2.0)) * groove_depth
groove_width = max(3.0, min(groove_width, angle_top, outer_r * 1.6))

hub_dia = max(bore + 4.0, hub_dia)
hub_r = hub_dia / 2.0
hub_height = max(2.0, hub_height)


def rim_width_for(n):
    """Total axial rim width for n grooves at groove_pitch, plus side material."""
    if n <= 1:
        return max(groove_width + 6.0, belt_dia + 8.0)
    span = (n - 1) * groove_pitch
    return span + groove_width + 8.0


# ── Groove cutters (bodies of revolution about Z) ─────────────────────────────
def v_groove_cutter(z_center):
    """A V-channel: the union of two coaxial cones meeting at the apex circle
    (radius outer_r - groove_depth) at z_center, each opening out to the rim."""
    apex_r = max(0.5, outer_r - groove_depth)
    half = groove_width / 2.0

    # A V-groove is an ANNULAR channel, so it must be a revolved V profile --
    # not two `makeCone`s meeting at the apex circle. `makeCone` returns a
    # FILLED frustum, so that union was a solid hourglass whose waist is a disc
    # of radius apex_r: it removed the entire core of the sheave, parting the
    # rim into free flange discs. vbelt rendered 3 bodies and multi_groove
    # n+1 = 5, at defaults and at every preset.
    #
    # Revolve the V cross-section about Z instead. The profile runs from the
    # apex at (apex_r, 0) out to the rim at (outer_r, +-half) -- so the groove
    # is exactly `groove_width` wide where it meets the rim, as declared -- and
    # then 1 mm further along the same flanks so the cut breaks the surface
    # cleanly.
    radial = max(0.001, outer_r - apex_r)
    over = 1.0
    tip_r = outer_r + over
    tip_h = half * (radial + over) / radial
    profile = [
        (apex_r, 0.0),
        (tip_r, tip_h),
        (tip_r, -tip_h),
    ]
    return (
        cq.Workplane("XZ")
        .polyline([(r, z + z_center) for r, z in profile])
        .close()
        .revolve(360.0, (0, 0, 0), (0, 1, 0))
    )


def round_groove_cutter(z_center):
    """A semicircular groove: a torus of the belt radius centred on the rim."""
    r_belt = belt_dia / 2.0 + CLR
    t = cq.Solid.makeTorus(
        outer_r, r_belt, pnt=cq.Vector(0, 0, z_center), dir=cq.Vector(0, 0, 1),
    )
    return cq.Workplane(obj=t)


# ── Body helpers ─────────────────────────────────────────────────────────────
def rim(width):
    """The solid sheave blank, base at z=0, of the given axial width."""
    return cq.Workplane("XY").circle(outer_r).extrude(width)


def add_hub(body):
    """A set-screw hub extending below the rim (z<0)."""
    h = cq.Workplane("XY").circle(hub_r).extrude(hub_height)
    return body.union(h.translate((0, 0, -hub_height)))


def bore_out(body, z0, total_h):
    if bore_r <= 0.05:
        return body
    cutter = (
        cq.Workplane("XY")
        .circle(bore_r + CLR)
        .extrude(total_h + 1.0)
        .translate((0, 0, z0 - 0.5))
    )
    return body.cut(cutter)


def add_setscrew(body, z_center):
    if not setscrew:
        return body
    d = max(1.5, min(setscrew_dia, hub_dia * 0.4))
    hole = (
        cq.Workplane("YZ")
        .transformed(offset=cq.Vector(0, z_center, 0))
        .circle(d / 2.0)
        .extrude(hub_r + 0.5)
    )
    return body.cut(hole)


# ── Builders ─────────────────────────────────────────────────────────────────
def _finish(body, rim_w):
    z_low = 0.0
    if hub:
        body = add_hub(body)
        z_low = -hub_height
    body = bore_out(body, z_low, rim_w - z_low)
    if hub:
        body = add_setscrew(body, z_center=max(2.0, hub_height * 0.5))
    return body


def build_single(kind):
    rim_w = rim_width_for(1)
    body = rim(rim_w)
    z_mid = rim_w / 2.0
    if kind == "roundbelt":
        body = body.cut(round_groove_cutter(z_mid))
    else:
        body = body.cut(v_groove_cutter(z_mid))
    return _finish(body, rim_w)


def build_multi():
    n = max(2, min(int(grooves), 8))
    rim_w = rim_width_for(n)
    body = rim(rim_w)
    span = (n - 1) * groove_pitch
    start = (rim_w - span) / 2.0
    cutter = None
    for i in range(n):
        g = v_groove_cutter(start + i * groove_pitch)
        cutter = g if cutter is None else cutter.union(g)
    if cutter is not None:
        body = body.cut(cutter)
    return _finish(body, rim_w)


# ── Rope sheave ──────────────────────────────────────────────────────────────
ROPE_GROOVE_R = 0.53      # throat bottom radius / rope diameter: cradled, not pinched
ROPE_GROOVE_DEPTH = 1.25  # rim height above the tread / rope diameter


def build_rope_sheave():
    """An idler sheave: a rim with one rope throat and a plain through bore.

    The throat is one revolved profile: a bottom arc on the tread circle, and two
    flanks tangent to it that run 1 mm past the rim so the cut breaks the surface
    cleanly. Sized from the tread, so the rim diameter is derived:
    tread_dia + 2 * ROPE_GROOVE_DEPTH * rope_dia.
    """
    d = max(1.0, rope_dia)
    tread_r = max(6.0, tread_dia / 2.0)
    half = math.radians(max(20.0, min(throat_angle, 70.0)) / 2.0)
    groove_r = ROPE_GROOVE_R * d
    depth = ROPE_GROOVE_DEPTH * d
    rim_r = tread_r + depth

    # tangent point of a flank on the bottom arc, measured from the tread (u) and
    # from the throat's mid-plane (v)
    tan_u = groove_r * (1.0 - math.sin(half))
    tan_v = groove_r * math.cos(half)
    rim_v = tan_v + (depth - tan_u) * math.tan(half)         # half-width at the rim
    over = 1.0
    end_v = tan_v + (depth + over - tan_u) * math.tan(half)

    width = 2.0 * rim_v + 2.0 * max(3.0, 0.6 * d)            # throat plus two flanges
    mid = width / 2.0
    throat = (
        cq.Workplane("XZ")
        .moveTo(tread_r + tan_u, mid - tan_v)
        .threePointArc((tread_r, mid), (tread_r + tan_u, mid + tan_v))
        .lineTo(rim_r + over, mid + end_v)
        .lineTo(rim_r + over, mid - end_v)
        .close()
        .revolve(360.0, (0, 0, 0), (0, 1, 0))
    )
    body = cq.Workplane("XY").circle(rim_r).extrude(width).cut(throat)

    bore_d = max(2.0, min(bore_raw, 2.0 * tread_r - 8.0))    # keep 4 mm under the throat
    cutter = (
        cq.Workplane("XY")
        .circle(bore_d / 2.0 + CLR)
        .extrude(width + 1.0)
        .translate((0, 0, -0.5))
    )
    return body.cut(cutter)


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "rope_sheave":
    result = build_rope_sheave()
elif target_part == "roundbelt":
    result = build_single("roundbelt")
elif target_part == "multi_groove":
    result = build_multi()
else:
    result = build_single("roundbelt" if belt_profile == "roundbelt" else "vbelt")
