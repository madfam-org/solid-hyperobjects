"""
Parametric Prosthetic Socket — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A printable/customizable socket *blank* — the tapered cup that interfaces a
residual limb with a prosthetic pylon. Because there is no real limb scan here,
the limb is PARAMETERIZED: proximal (top) diameter, distal (bottom) diameter,
socket length and wall thickness. The distal end carries the e-NABLE / Open
Source Leg 4-bolt pyramid-adapter pattern (the Common Denominator Geometry that
lets any compatible foot/knee bolt on).

  * "transtibial"  — below-knee: shorter, more elliptical cross-section
                     (target_part == "transtibial").
  * "transfemoral" — above-knee: longer, rounder cross-section
                     (target_part == "transfemoral").
  * "check_socket" — a thin test-fit socket with a dense ventilation pattern for
                     trial fitting (target_part == "check_socket").

NOT a certified clinical device — a residual-limb socket requires professional
clinician measurement, fitting and sign-off before use.

Watertight strategy (the hard part — organic revolved profiles crack at the
axis, so we NEVER revolve a profile that touches the axis):
  - The OUTER body is a LOFT through a stack of closed elliptical wires, from a
    small distal ellipse up to a large proximal ellipse (an optional brim flare
    widens the last sections). Lofting closed wires yields one manifold solid.
  - The distal end is CLOSED: the lowest loft section is a small (non-degenerate)
    ellipse and a solid adapter plate seals the bottom — no zero-area apex.
  - The cavity is a SECOND loft (the inner ellipse stack), raised by the floor
    thickness and pushed above the rim, then CUT from the outer solid. This
    hollows the cup, leaves the TOP open and the DISTAL end solid — equivalent to
    a shell() but robust (we do not rely on .shell(), which the brief warns can
    misbehave on lofted organic shells).
  - Ventilation holes and the bolt-pattern holes are through-cuts. Every result
    is a single closed manifold solid.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals; params arrive as BARE globals.
  - Read params via PARAM(lambda: <name>, <default>). No globals()/eval/getattr.
  - Assign the final solid to a top-level name `result`.
"""

import math

import cadquery as cq


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


# ── Parameters (limb-driven; diameters in mm) ────────────────────────────────
target_part = str(PARAM(lambda: target_part, "transtibial"))
# socket_type mirrors the mode when the platform injects target_part == default.
socket_type = str(PARAM(lambda: socket_type, "transtibial"))

proximal_dia = float(PARAM(lambda: proximal_dia, 95.0))   # top opening dia (mm)
distal_dia   = float(PARAM(lambda: distal_dia,   62.0))   # bottom dia (mm)
socket_len   = float(PARAM(lambda: socket_len,  180.0))   # cup length along limb (mm)
wall         = float(PARAM(lambda: wall,          4.0))   # shell wall thickness (mm)
floor        = float(PARAM(lambda: floor,         6.0))   # closed distal-end thickness (mm)

# Cross-section ovality: 1.0 = round; >1 flattens antero-posteriorly (Y vs X).
ovality      = float(PARAM(lambda: ovality,      1.18))
brim_flare   = float(PARAM(lambda: brim_flare,   1.12))   # proximal rim outward gain (1 = none)

# Distal e-NABLE / OSL 4-bolt pyramid adapter.
bolt_circle_dia = float(PARAM(lambda: bolt_circle_dia, 40.0))  # PCD of the 4 bolts (mm)
bolt_dia        = float(PARAM(lambda: bolt_dia,          5.5)) # M5 clearance (mm)
adapter_plate_dia = float(PARAM(lambda: adapter_plate_dia, 58.0))  # seat plate dia (mm)
pyramid         = bool(PARAM(lambda: pyramid, True))          # add the male pyramid boss

# Breathability.
ventilation = bool(PARAM(lambda: ventilation, False))   # ring pattern of wall holes
vent_density = int(PARAM(lambda: vent_density, 8))      # holes per ring

# ── Clamps (keep geometry sane + watertight) ─────────────────────────────────
proximal_dia = max(50.0, min(proximal_dia, 220.0))
distal_dia   = max(35.0, min(distal_dia, min(proximal_dia - 6.0, 180.0)))
socket_len   = max(80.0, min(socket_len, 420.0))
wall         = max(2.5,  min(wall, 8.0))
floor        = max(4.0,  min(floor, 14.0))
ovality      = max(1.0,  min(ovality, 1.5))
brim_flare   = max(1.0,  min(brim_flare, 1.35))
bolt_circle_dia = max(20.0, min(bolt_circle_dia, min(adapter_plate_dia - 8.0, distal_dia - 6.0)))
bolt_dia     = max(3.0,  min(bolt_dia, 8.0))
adapter_plate_dia = max(bolt_circle_dia + 10.0, min(adapter_plate_dia, distal_dia + 4.0))
vent_density = max(4,    min(vent_density, 14))

# Resolve which socket to build (mode wins; socket_type is the fallback selector).
_part = target_part
if _part not in ("transtibial", "transfemoral", "check_socket"):
    _part = socket_type if socket_type in (
        "transtibial", "transfemoral", "check_socket") else "transtibial"


# ── Cross-section helpers ────────────────────────────────────────────────────
def _profile_radius(t, r_distal, r_prox, flare):
    """Outer semi-axis at normalized height t in [0,1].

    A gentle convex taper (not a straight cone) reads as an anatomical cup:
    ease from distal to proximal, then add the brim flare over the top ~18%."""
    base = r_distal + (r_prox - r_distal) * (0.5 - 0.5 * math.cos(math.pi * t))
    if flare > 1.0 and t > 0.82:
        ft = (t - 0.82) / 0.18
        base *= 1.0 + (flare - 1.0) * ft
    return base


def _loft_stack(r_distal_x, r_distal_y, r_prox_x, r_prox_y, z0, z1,
                flare, sections):
    """Loft a closed elliptical solid between two heights. Returns a Workplane
    solid — watertight because every section is a closed wire and the ends are
    finite-area ellipses (never an on-axis point).

    Built on a SINGLE chained workplane (offset each section) so CadQuery sees a
    proper wire stack — the pattern the assistive-grip cartridge uses for its
    lofted body. `.ellipse()` needs x_radius != y_radius, so equal axes are
    nudged apart infinitesimally."""
    span = z1 - z0
    wp = cq.Workplane("XY")
    prev_z = z0
    for i in range(sections):
        t = i / (sections - 1)
        rx = _profile_radius(t, r_distal_x, r_prox_x, flare)
        ry = _profile_radius(t, r_distal_y, r_prox_y, flare)
        if abs(rx - ry) < 1e-4:
            ry = rx * 1.0001
        z = z0 + span * t
        wp = wp.workplane(offset=(z - prev_z)) if i > 0 else wp.workplane(offset=z)
        wp = wp.ellipse(rx, ry)
        prev_z = z
    return wp.loft(combine=True)


# ── Distal adapter plate + 4-bolt pyramid pattern (the CDG) ──────────────────
def _adapter_plate():
    """A solid seat disc at the distal end that the bolt pattern sits in. It
    overlaps the socket floor so the union is one solid."""
    return (
        cq.Workplane("XY")
        .circle(adapter_plate_dia / 2.0)
        .extrude(floor + 1.0)
    )


def _pyramid_boss():
    """The male 4-sided pyramid boss (e-NABLE / OSL). Built as a lofted square →
    smaller square, watertight. Sits centered on the distal face pointing -Z."""
    base = 26.0
    top = 15.0
    height = 14.0
    half_b = base / 2.0
    half_t = top / 2.0
    base_pts = [(-half_b, -half_b), (half_b, -half_b), (half_b, half_b), (-half_b, half_b)]
    top_pts = [(-half_t, -half_t), (half_t, -half_t), (half_t, half_t), (-half_t, half_t)]
    boss = (
        cq.Workplane("XY")
        .polyline(base_pts).close()
        .workplane(offset=-height)
        .polyline(top_pts).close()
        .loft(combine=True)
    )
    # Place the square base flush at z=0 (top of plate region), tip below.
    return boss


def _bolt_holes(depth_top, depth_bottom):
    """4 through-holes on the bolt-circle plus a central hole — cut through the
    distal plate/floor. Cylinders run well past both faces so the cut is clean."""
    holes = None
    r_pcd = bolt_circle_dia / 2.0
    hole = (
        cq.Workplane("XY")
        .workplane(offset=depth_top)
        .circle(bolt_dia / 2.0)
        .extrude(-(depth_top - depth_bottom))
    )
    holes = hole
    for k in range(4):
        ang = math.radians(45.0 + k * 90.0)
        x = r_pcd * math.cos(ang)
        y = r_pcd * math.sin(ang)
        h = (
            cq.Workplane("XY")
            .workplane(offset=depth_top)
            .center(x, y)
            .circle(bolt_dia / 2.0)
            .extrude(-(depth_top - depth_bottom))
        )
        holes = holes.union(h)
    return holes


# ── Ventilation (radial through-holes in the wall) ───────────────────────────
def _vent_holes(r_distal, r_prox, rings, per_ring):
    """Rings of radial holes bored through the wall between distal and proximal.

    Every hole is a cylinder that STARTS well outside the outer surface and is
    long enough to fully exit past the axis, so it makes a clean radial
    through-cut (never a tangent that would leave a non-manifold sliver). All
    holes are grouped into ONE Compound and cut in a single boolean — an O(n)
    grouping instead of an O(n²) pairwise union, so it stays fast AND watertight
    (the seed-tray cartridge uses the same trick). Holes are kept clear of the
    rim-fillet band so the softened rim is never nicked."""
    shapes = []
    hole_r = min(3.0, wall * 0.85)
    z_lo = floor + 16.0
    # Keep every hole below BOTH a fixed rim margin and the point where the brim
    # flare begins (t=0.82) — holes grazing the flared/filleted wall leave
    # non-manifold slivers, so the band stops before the flare.
    z_hi = min(socket_len - 30.0, 0.78 * socket_len)
    if z_hi <= z_lo:
        return None
    # Each cylinder starts r_max out and reaches just to the axis: it pierces the
    # NEAR wall cleanly and terminates in the open cavity, so it never touches the
    # far wall (one hole per position, not two).
    r_max = max(r_prox, r_distal) * max(brim_flare, ovality) + wall + 10.0
    cyl_len = r_max
    for r in range(rings):
        t = r / max(rings - 1, 1)
        z = z_lo + (z_hi - z_lo) * t
        stagger = (r % 2) * (math.pi / per_ring)
        for c in range(per_ring):
            ang = stagger + 2.0 * math.pi * c / per_ring
            cx = math.cos(ang)
            cy = math.sin(ang)
            # Launch point r_max out along the radial, aim back toward the axis.
            start = cq.Vector(r_max * cx, r_max * cy, z)
            hole = (
                cq.Workplane("XY")
                .transformed(
                    offset=start,
                    rotate=cq.Vector(90.0, 0.0, math.degrees(ang) + 90.0),
                )
                .circle(hole_r)
                .extrude(-cyl_len)
            )
            shapes.append(hole.val())
    if not shapes:
        return None
    return cq.Workplane("XY").add(cq.Compound.makeCompound(shapes))


# ── Socket assembly ──────────────────────────────────────────────────────────
def build_socket(r_prox, r_dist, length, ov, flare, ventilate, vent_rings):
    """Assemble one manifold socket solid.

    r_prox / r_dist are the *round* outer radii; ovality flattens Y relative to X
    so the cup is anatomically elliptical without touching the axis anywhere."""
    # X keeps the nominal radius; Y is flattened by ovality (medio-lateral wider).
    prox_x = r_prox
    prox_y = r_prox / ov
    dist_x = r_dist
    dist_y = r_dist / ov

    # 1) Outer solid loft (distal small → proximal large).
    outer = _loft_stack(dist_x, dist_y, prox_x, prox_y, 0.0, length, flare, 11)

    # 2) Inner cavity loft: same taper minus wall, raised by floor, poking above
    #    the rim so the top is fully open after the cut.
    in_prox_x = max(prox_x - wall, 2.0)
    in_prox_y = max(prox_y - wall, 2.0)
    in_dist_x = max(dist_x - wall, 2.0)
    in_dist_y = max(dist_y - wall, 2.0)
    cavity = _loft_stack(
        in_dist_x, in_dist_y, in_prox_x, in_prox_y,
        floor, length + 8.0, flare, 11,
    )
    body = outer.cut(cavity)

    # 3) Distal adapter plate (solid seat) unioned to the closed floor.
    body = body.union(_adapter_plate())

    # 4) Male pyramid boss under the plate (optional).
    if pyramid:
        try:
            body = body.union(_pyramid_boss())
        except Exception:
            pass  # boss is cosmetic-structural; never fatal to the socket

    # 5) Bolt pattern: cut through plate + pyramid region.
    try:
        bh = _bolt_holes(floor + 2.0, -18.0 if pyramid else -2.0)
        body = body.cut(bh)
    except Exception:
        pass

    # 6) Ventilation holes.
    if ventilate:
        vh = _vent_holes(r_dist, r_prox, vent_rings, vent_density)
        if vh is not None:
            body = body.cut(vh)

    # 7) Soften the proximal rim for skin comfort (non-fatal).
    try:
        body = body.edges(">Z").fillet(min(wall * 0.35, 1.0))
    except Exception:
        pass

    return body


# ── Per-mode presets ─────────────────────────────────────────────────────────
def build_transtibial():
    # Below-knee: shorter, more elliptical (higher ovality), modest flare.
    return build_socket(
        r_prox=proximal_dia / 2.0,
        r_dist=distal_dia / 2.0,
        length=min(socket_len, 230.0),
        ov=max(ovality, 1.12),
        flare=brim_flare,
        ventilate=ventilation,
        vent_rings=3,
    )


def build_transfemoral():
    # Above-knee: longer, rounder (lower ovality), fuller brim.
    return build_socket(
        r_prox=proximal_dia / 2.0,
        r_dist=distal_dia / 2.0,
        length=max(socket_len, 240.0),
        ov=min(ovality, 1.12),
        flare=max(brim_flare, 1.1),
        ventilate=ventilation,
        vent_rings=4,
    )


def build_check_socket():
    # Test-fit socket: thin wall, always ventilated, denser hole pattern.
    global wall  # noqa: PLW0603 — intentional thin-wall override for the check mode
    wall_prev = wall
    wall = max(2.5, min(wall, 3.5))
    try:
        body = build_socket(
            r_prox=proximal_dia / 2.0,
            r_dist=distal_dia / 2.0,
            length=socket_len,
            ov=ovality,
            flare=brim_flare,
            ventilate=True,
            vent_rings=5,
        )
    finally:
        wall = wall_prev
    return body


# ── Dispatch ─────────────────────────────────────────────────────────────────
if _part == "transfemoral":
    result = build_transfemoral()
elif _part == "check_socket":
    result = build_check_socket()
else:  # "transtibial"
    result = build_transtibial()
