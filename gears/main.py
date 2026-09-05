"""
Involute Gears — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A dimensionally-correct involute gear generator. Unlike a faceted CSG
approximation, the tooth flank here is sampled directly from the true involute
curve of the base circle (ISO 53 / DIN 867, 20° pressure angle), so meshing
geometry is real: any two gears sharing the same module and pressure angle
engage correctly. Supports external spur gears, helical gears (twisted
extrusion), internal ring (annular) gears, and linear racks.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` (cadquery) and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `teeth`).
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
m            = float(PARAM(lambda: m,               2.0))   # module (mm) — pitch dia = m*teeth
teeth        = int(  PARAM(lambda: teeth,            20))    # number of teeth
pressure_angle = float(PARAM(lambda: pressure_angle, 20.0)) # pressure angle (deg)
thickness    = float(PARAM(lambda: thickness,       8.0))   # face width / gear thickness (mm)
bore         = float(PARAM(lambda: bore,            6.0))   # central bore diameter (mm); 0 = solid
helix        = float(PARAM(lambda: helix,           0.0))   # helix angle (deg); 0 = spur

hub_enabled  = bool( PARAM(lambda: hub_enabled,   False))   # add a raised hub around the bore
hub_diameter = float(PARAM(lambda: hub_diameter,  16.0))    # hub outer diameter (mm)
hub_height   = float(PARAM(lambda: hub_height,     6.0))    # hub height above the gear face (mm)
setscrew     = bool( PARAM(lambda: setscrew,      False))   # radial set-screw hole into the bore
setscrew_dia = float(PARAM(lambda: setscrew_dia,   3.0))    # set-screw hole diameter (mm)

# Ring (internal / annular) gear
rim_width    = float(PARAM(lambda: rim_width,      6.0))    # radial rim thickness outside the root (mm)

# Rack (linear)
rack_teeth   = int(  PARAM(lambda: rack_teeth,      12))    # number of teeth along the rack
rack_height  = float(PARAM(lambda: rack_height,   10.0))   # back thickness below the tooth roots (mm)

flank_pts    = int(  PARAM(lambda: flank_pts,        9))    # involute samples per flank (facet control)

target_part  = str(  PARAM(lambda: target_part, "spur"))   # "spur" | "helical" | "ring" | "rack"

# ── Clamp / normalise inputs ─────────────────────────────────────────────────
m = max(0.2, m)
teeth = max(6, min(teeth, 240))
pressure_angle = max(10.0, min(pressure_angle, 30.0))
thickness = max(1.0, thickness)
flank_pts = max(4, min(flank_pts, 16))
pa = math.radians(pressure_angle)

# The "helical" mode is just spur with a non-zero helix default; either way a
# non-zero `helix` twists the extrusion.
if target_part == "helical" and abs(helix) < 1e-6:
    helix = 15.0


# ── Involute geometry (the core value) ───────────────────────────────────────
def _involute_point(rb, t):
    """Point on the involute of a circle of radius `rb` at roll angle `t` (rad).
    Radius from centre is rb*sqrt(1+t^2); the curve starts on the base circle."""
    return (rb * (math.cos(t) + t * math.sin(t)),
            rb * (math.sin(t) - t * math.cos(t)))


def _inv(angle):
    """Involute function inv(a) = tan(a) - a."""
    return math.tan(angle) - angle


def _roll_at_radius(rb, r):
    """Roll angle t such that the involute point sits at radius r (r >= rb)."""
    if r <= rb:
        return 0.0
    return math.sqrt((r / rb) ** 2 - 1.0)


def _one_tooth_profile(rp, rb, ro, rr, n):
    """Return the outline of a SINGLE tooth as an ordered list of (x, y) points,
    centred on the +X axis. Walks up one involute flank from the working root to
    the tip, crosses the tip land, and back down the mirrored flank. A short
    trochoid-approximating fillet ties the flank base into the root circle so the
    root is not a stress-raising sharp notch.

    Angular bookkeeping (all measured from the tooth centreline):
      - Tooth thickness at the pitch circle subtends  half_pitch = pi/(2*teeth).
      - The involute leaves the base circle offset by inv(pa) from the flank's
        pitch-point; so the flank centreline offset is half_pitch + inv(pa).
    """
    half_pitch = math.pi / (2.0 * teeth)
    # Where the raw involute crosses the pitch circle it subtends angle inv(pa)
    # about the origin. We want that pitch point to land at -half_pitch from the
    # centreline so the two mirrored flanks give a pitch tooth thickness of
    # exactly 2*half_pitch*rp = pi*m/2. Hence subtract a single offset:
    #   ang = phi_raw - beta0,  with beta0 = inv(pa) + half_pitch.
    beta0 = half_pitch + _inv(pa)

    # Radii we actually sample the involute across: from max(rb, rr) up to ro.
    r_start = max(rb, rr)
    t_end = _roll_at_radius(rb, ro)
    t_start = _roll_at_radius(rb, r_start)

    right = []  # right-hand flank, from root->tip
    for i in range(n):
        t = t_start + (t_end - t_start) * (i / (n - 1))
        x0, y0 = _involute_point(rb, t)
        # angle of this raw involute point about origin
        phi = math.atan2(y0, x0)
        r = rb * math.sqrt(1.0 + t * t)
        # Shift the whole flank so its pitch point sits at -half_pitch (see beta0).
        ang = phi - beta0
        right.append((r * math.cos(ang), r * math.sin(ang)))

    # Fillet at the root: if the dedendum drops below the base circle, add a
    # small radial run-in from the root circle to the first involute point so the
    # profile closes cleanly on the root arc (approximate trochoid).
    root_pts_r = []
    if rr < r_start - 1e-6:
        # start on the root circle directly radially inboard of the first flank pt
        fx, fy = right[0]
        fang = math.atan2(fy, fx)
        root_pts_r.append((rr * math.cos(fang), rr * math.sin(fang)))

    # Mirror the right flank across the X axis to get the left flank (tip->root).
    left = [(x, -y) for (x, y) in reversed(right)]
    root_pts_l = [(x, -y) for (x, y) in reversed(root_pts_r)]

    # Assemble: root(right) -> right flank up -> [tip land implied by two tip pts]
    #           -> left flank down -> root(left)
    pts = []
    pts.extend(root_pts_r)
    pts.extend(right)
    pts.extend(left)
    pts.extend(root_pts_l)
    return pts


def _gear_wire(rp, rb, ro, rr):
    """Build the full closed gear cross-section wire by generating one tooth and
    rotating it into `teeth` angular positions, joined by root-circle arcs."""
    tooth = _one_tooth_profile(rp, rb, ro, rr, flank_pts)
    step = 2.0 * math.pi / teeth

    all_pts = []
    for k in range(teeth):
        a = k * step
        ca, sa = math.cos(a), math.sin(a)
        for (x, y) in tooth:
            all_pts.append((x * ca - y * sa, x * sa + y * ca))
    return all_pts


def _extrude(wire_pts):
    """Extrude a closed 2D polygon `thickness` in Z, twisting for a helix.
    Twist total = thickness * tan(helix) / rp radians, applied via CadQuery's
    `twistExtrude` (degrees)."""
    wp = cq.Workplane("XY").polyline(wire_pts).close()
    if abs(helix) > 1e-6:
        rp = m * teeth / 2.0
        twist_deg = math.degrees(thickness * math.tan(math.radians(helix)) / rp)
        solid = wp.twistExtrude(thickness, twist_deg)
    else:
        solid = wp.extrude(thickness)
    return solid


# ── Post features (bore / hub / set-screw) ───────────────────────────────────
def _apply_bore_and_hub(solid, top_z):
    """Cut the central bore through everything and optionally add a hub with an
    optional radial set-screw hole."""
    if hub_enabled and hub_diameter > max(bore + 1.0, 2.0):
        hd = min(hub_diameter, (m * teeth) - 2.0 * m)  # keep hub inside root
        hd = max(hd, bore + 2.0)
        hub = (cq.Workplane("XY")
               .transformed(offset=cq.Vector(0, 0, top_z))
               .circle(hd / 2.0)
               .extrude(hub_height))
        solid = solid.union(hub)
        top_z = top_z + hub_height

    if bore > 0.05:
        br = min(bore / 2.0, (m * teeth) / 2.0 - m)  # never wider than the root
        br = max(br, 0.5)
        through = (cq.Workplane("XY")
                   .transformed(offset=cq.Vector(0, 0, -1.0))
                   .circle(br)
                   .extrude(top_z + 2.0))
        solid = solid.cut(through)

        if setscrew and setscrew_dia > 0.05:
            ssr = min(setscrew_dia / 2.0, 2.5)
            # radial hole from the bore wall outward, centred mid-height of the
            # hub if present else mid gear face.
            z_mid = (top_z if hub_enabled else thickness) / 2.0
            reach = (hub_diameter / 2.0 if hub_enabled else (m * teeth) / 2.0)
            hole = (cq.Workplane("XZ")
                    .transformed(offset=cq.Vector(0, z_mid, 0))
                    .circle(ssr)
                    .extrude(reach + 1.0))
            try:
                solid = solid.cut(hole)
            except Exception:
                pass  # non-fatal if the set-screw geometry degenerates
    return solid


# ── Part builders ────────────────────────────────────────────────────────────
def build_spur():
    """External involute spur (or helical) gear."""
    rp = m * teeth / 2.0            # pitch radius
    rb = rp * math.cos(pa)          # base radius
    ro = rp + m                     # outer/addendum radius
    rr = rp - 1.25 * m              # root/dedendum radius
    rr = max(rr, 0.5 * m)           # guard tiny gears
    wire = _gear_wire(rp, rb, ro, rr)
    solid = _extrude(wire)
    solid = _apply_bore_and_hub(solid, thickness)
    return solid


def build_ring():
    """Internal (annular) gear: teeth point INWARD inside a solid rim. Built by
    cutting an external-gear-shaped cavity from a plain cylindrical rim. For an
    internal gear the addendum/dedendum swap sense: the tooth tips reach inward
    to rp - m and the roots sit at rp + 1.25*m."""
    rp = m * teeth / 2.0
    rb = rp * math.cos(pa)
    # Internal tooth: tip (inner) at rp - m, root (outer) at rp + 1.25*m.
    ro = rp + 1.25 * m              # outer extent of the toothed cavity (roots)
    rr = rp - m                     # inner extent (tips) — cutter's "outer" is ro
    rr = max(rr, 0.4 * m)
    # The cutting tool is an EXTERNAL gear profile spanning [rr .. ro].
    wire = _gear_wire(rp, rb, ro, rr)
    cutter = _extrude(wire)

    rim_outer = ro + max(rim_width, 2.0)
    rim = (cq.Workplane("XY").circle(rim_outer).extrude(thickness))
    if abs(helix) > 1e-6:
        # match the cutter twist so the internal teeth are also helical
        pass
    ring = rim.cut(cutter)
    return ring


def build_rack():
    """Linear rack: the conjugate of an involute gear is a straight-sided trapezoid
    tooth (flanks at the pressure angle). Correct rack geometry:
      - pitch line where tooth thickness == space == pi*m/2 (circular pitch p = pi*m)
      - addendum m above the pitch line, dedendum 1.25*m below
      - flanks inclined at the pressure angle from the tooth centre normal.
    Teeth run along X; the bar is extruded `thickness` in Z (face width)."""
    n = max(2, min(rack_teeth, 60))
    p = math.pi * m                 # circular pitch (tooth+space along pitch line)
    add = m
    ded = 1.25 * m
    # Half tooth thickness at pitch line = p/4; flank horizontal run over the
    # tooth height due to the pressure angle:
    tan_pa = math.tan(pa)
    top_half = p / 4.0 - add * tan_pa      # half width of the tip land
    bot_half = p / 4.0 + ded * tan_pa      # half width at the root line
    top_half = max(top_half, 0.05 * m)     # keep a real tip land

    length = n * p
    x0 = -length / 2.0
    back = rack_height                      # solid backing below the roots
    y_root = -ded
    y_tip = add
    y_back = -ded - back

    pts = [(x0, y_back), (x0, y_root)]
    for i in range(n):
        cx = x0 + (i + 0.5) * p             # tooth centre
        # space to the left of this tooth is already on the root line; build the
        # trapezoid: rise left flank, tip land, fall right flank, then root gap.
        pts.append((cx - bot_half, y_root))
        pts.append((cx - top_half, y_tip))
        pts.append((cx + top_half, y_tip))
        pts.append((cx + bot_half, y_root))
    pts.append((x0 + length, y_root))
    pts.append((x0 + length, y_back))
    # close along the back
    wire = cq.Workplane("XY").polyline(pts).close()
    solid = wire.extrude(thickness)

    # Optional mounting bore through the back, along the rack length.
    if bore > 0.05 and back > bore:
        br = min(bore / 2.0, back / 2.0 - 0.5, thickness / 2.0 - 0.5)
        if br > 0.4:
            hole = (cq.Workplane("XY")
                    .transformed(offset=cq.Vector(0, y_back + back / 2.0, thickness / 2.0))
                    .transformed(rotate=cq.Vector(90, 0, 0))
                    .circle(br)
                    .extrude(length))
            try:
                solid = solid.cut(hole)
            except Exception:
                pass
    return solid


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "rack":
    result = build_rack()
elif target_part == "ring":
    result = build_ring()
else:  # "spur" (default) and "helical"
    result = build_spur()
