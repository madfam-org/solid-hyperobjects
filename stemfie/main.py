"""
STEMFIE-compatible construction set — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

Three parts of an open construction kit for STEM teaching: a `beam`, a right-angle
`brace`, and a `fastener` (pin or plain shaft). Everything is dimensioned on one
grid module, so any beam bolts to any other beam, at any hole, on any of the three
axes — and to parts printed elsewhere that follow the same 10 mm block standard.

INTERFACE vs FORM
-----------------
This cartridge implements the *interface* of the STEMFIE 10 mm block standard —
the functional dimensions another part mates to — and gives everything else a
form of MADFAM's own authoring. See `NOTICE` and `docs/CLEANROOM-VERIFICATION.md`.

  interface (matched exactly, other parts depend on them)
    BU              10.0 mm   block unit / grid pitch
    HOLE_D           4.2 mm   through-hole diameter (clearance hole)
    hole pitch      10.0 mm   = 1 BU, holes at cell centres
    beam section    10 x 10 mm per (width_units, height_units)
    brace plate      2.5 mm   = BU/4 per thickness_unit
    brace angle       90 deg
    SHANK_D          4.0 mm   fastener shank
    COLLAR_D         5.7 mm   fastener collar / head
    clearance        0.2 mm   diametral, HOLE_D - SHANK_D

  form (ours, deliberately not the upstream shape)
    beam long edges rounded with a 0.8 mm FILLET (not a chamfer)
    brace outer corners rounded 2.5 mm, inner re-entrant corner filleted 2.0 mm
    brace hole mouths chamfered 0.4 mm x 45 deg on both faces
    fastener collar = 1.5 mm cylindrical land + 1.0 mm conical underside taper
    fastener free end carries a 0.8 mm lead-in taper down to 3.4 mm

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `length_units`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.

SPDX-License-Identifier: CERN-OHL-W-2.0
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


# ── The interface constants (STEMFIE 10 mm block standard) ───────────────────
BU = 10.0          # block unit / grid pitch — interface
HOLE_D = 4.2       # through-hole diameter — interface
SHANK_D = 4.0      # fastener shank diameter — interface (0.2 mm under the hole)
COLLAR_D = 5.7     # fastener collar diameter — interface
PLATE_U = BU / 4.0  # 2.5 mm brace plate per thickness unit — interface

# ── The form constants (MADFAM authoring, non-functional) ────────────────────
BEAM_EDGE_R = 0.8       # fillet radius on the beam's four long edges
BRACE_OUT_R = 2.5       # brace outer corner radius
BRACE_IN_R = 2.0        # brace re-entrant (inner) corner fillet
BRACE_MOUTH_C = 0.4     # brace hole-mouth chamfer, both faces
COLLAR_LAND_H = 1.5     # cylindrical part of the fastener collar
COLLAR_TAPER_H = 1.0    # conical underside of the fastener collar
LEAD_IN_H = 0.8         # lead-in taper height on a fastener's free end
LEAD_IN_D = 3.4         # lead-in taper's small diameter


# ── Parameters ───────────────────────────────────────────────────────────────
length_units     = int(PARAM(lambda: length_units,      4))   # beam / fastener length, BU
width_units      = int(PARAM(lambda: width_units,       1))   # beam Y extent, BU
height_units     = int(PARAM(lambda: height_units,      1))   # beam Z extent, BU
holes_x          = bool(PARAM(lambda: holes_x,       True))   # beam through-holes along X
holes_y          = bool(PARAM(lambda: holes_y,       True))   # beam through-holes along Y
holes_z          = bool(PARAM(lambda: holes_z,       True))   # beam through-holes along Z
arm_a_units      = int(PARAM(lambda: arm_a_units,       3))   # brace arm A, BU
arm_b_units      = int(PARAM(lambda: arm_b_units,       3))   # brace arm B, BU
thickness_units  = int(PARAM(lambda: thickness_units,   1))   # brace plate, x BU/4
holes_enabled    = bool(PARAM(lambda: holes_enabled, True))   # brace connection holes
fastener_type_id = int(PARAM(lambda: fastener_type_id,  0))   # 0 = pin, 1 = plain shaft
fn               = int(PARAM(lambda: fn,                0))   # tessellation hint (B-Rep: unused)

target_part = str(PARAM(lambda: target_part, "beam"))         # "beam" | "brace" | "fastener"

# Clamp to the manifest's declared ranges so an out-of-range injection cannot
# produce a degenerate solid rather than an honest error.
length_units = max(1, min(20, length_units))
width_units = max(1, min(4, width_units))
height_units = max(1, min(4, height_units))
arm_a_units = max(1, min(10, arm_a_units))
arm_b_units = max(1, min(10, arm_b_units))
thickness_units = max(1, min(2, thickness_units))
fastener_type_id = max(0, min(1, fastener_type_id))


# ── Helpers ──────────────────────────────────────────────────────────────────
def _cell_centres(n):
    """Centres of `n` block-unit cells along one axis, centred on the origin.

    A cell centre sits half a block unit in from the face, so every hole lands on
    the 10 mm grid — this is the interface rule that makes any two parts mate.
    """
    span = n * BU
    return [-span / 2.0 + (i + 0.5) * BU for i in range(n)]


def _hole_cutter(axis, a, b, through):
    """One through-hole cylinder of HOLE_D along `axis`, positioned at (a, b) on
    the other two axes and running past both faces so the cut is a clean through.

    Returned as a raw `cq.Solid` rather than a Workplane: the whole array is fused
    in ONE call and cut in ONE boolean (see `_cut_all`), and that is what keeps
    the result a single watertight solid.
    """
    over = through + 2.0
    r = HOLE_D / 2.0
    if axis == "x":
        origin, direction = cq.Vector(-over / 2.0, a, b), cq.Vector(1, 0, 0)
    elif axis == "y":
        origin, direction = cq.Vector(a, -over / 2.0, b), cq.Vector(0, 1, 0)
    else:
        origin, direction = cq.Vector(a, b, -over / 2.0), cq.Vector(0, 0, 1)
    return cq.Solid.makeCylinder(r, over, origin, direction)


def _cut_all(body, solids):
    """Fuse the whole cutter array, then subtract it in a single boolean.

    Two things depend on doing it this way rather than cutting one hole at a time,
    or handing the cutters to `cut()` as separate arguments:

      * The hole arrays on different axes INTERSECT at every cell centre. A
        multi-argument cut treats the cutters as independent and subtracts the
        shared volume more than once; a sequential chain of Workplane unions is
        correct but pays an O(n) boolean each step and gets slow enough to time
        out on the 20x4x4 corner (320 holes). One fuse plus one cut is both
        correct and fast.
      * It is the fix for the recorded baseline defect. The baseline cut each
        axis separately and degenerated where the arrays crossed — three loose
        bodies and a non-watertight mesh with `holes_z` off, 57 bodies at larger
        width/height with a partial hole set. Fusing first gives OCCT one clean
        tool and one intersection to resolve, and every variant comes out as a
        single watertight solid.
    """
    if not solids:
        return body
    tool = solids[0] if len(solids) == 1 else solids[0].fuse(*solids[1:])
    return cq.Workplane(obj=body.val().cut(tool))


# ── Beam ─────────────────────────────────────────────────────────────────────
def build_beam():
    """A `length_units x width_units x height_units` block-unit beam, holed on
    whichever axes are enabled, with our own rounded long edges.

    Bounding box is exactly (length_units, width_units, height_units) x 10 mm —
    the interface — and the mesh is one watertight body for every combination of
    the three hole switches, including all of them off.
    """
    lx, ly, lz = length_units * BU, width_units * BU, height_units * BU

    body = cq.Workplane("XY").box(lx, ly, lz)

    # Form: round the four edges running the length of the beam. Applied BEFORE
    # the holes so the fillet operates on a clean box — filleting after the
    # boolean is where the baseline's mixed-axis variants fell apart.
    r = min(BEAM_EDGE_R, min(ly, lz) / 2.0 - 0.05)
    if r > 0.05:
        body = body.edges("|X").fillet(r)

    xs = _cell_centres(length_units)
    ys = _cell_centres(width_units)
    zs = _cell_centres(height_units)

    cutters = []
    if holes_x:
        # One hole per (y, z) cell, running the full length.
        for y in ys:
            for z in zs:
                cutters.append(_hole_cutter("x", y, z, lx))
    if holes_y:
        for x in xs:
            for z in zs:
                cutters.append(_hole_cutter("y", x, z, ly))
    if holes_z:
        for x in xs:
            for y in ys:
                cutters.append(_hole_cutter("z", x, y, lz))

    return _cut_all(body, cutters)


# ── Brace ────────────────────────────────────────────────────────────────────
def build_brace():
    """A right-angle L plate: `arm_a_units` cells along +X, `arm_b_units` along +Y,
    sharing the corner cell, `thickness_units x 2.5 mm` thick.

    Interface: 90 degrees, 10 mm cells, 2.5 mm per thickness unit, one 4.2 mm hole
    at every cell centre. Form: rounded outer corners, a filleted inner corner,
    and chamfered hole mouths — none of which any mating part sees.
    """
    a, b = arm_a_units, arm_b_units
    t = thickness_units * PLATE_U
    ax, by = a * BU, b * BU

    # The L footprint, drawn from the origin corner so arm A runs +X and arm B +Y.
    #
    # When either arm is a single block unit the L degenerates to a rectangle, and
    # the six-point path would then contain a zero-length segment (at a == 1,
    # ax == BU, so the (ax, BU) -> (BU, BU) leg has no length). OCCT rejects that
    # with a bare "BRep_API: command not done"; the fix is to emit the rectangle
    # the shape actually is rather than a degenerate polygon.
    if a == 1 or b == 1:
        outline = cq.Workplane("XY").rect(ax, by, centered=False)
    else:
        outline = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(ax, 0)
            .lineTo(ax, BU)
            .lineTo(BU, BU)
            .lineTo(BU, by)
            .lineTo(0, by)
            .close()
        )
    body = outline.extrude(t)

    # Form: soften every vertical edge. The re-entrant corner takes the smaller
    # radius; CadQuery's variable-radius selection is per-edge, so do it in two
    # passes and let a failure on a degenerate footprint stay non-fatal.
    if a == 1 or b == 1:
        # Rectangle: four convex corners, no re-entrant one.
        try:
            body = body.edges("|Z").fillet(min(BRACE_OUT_R, BU / 2.0 - 0.05))
        except Exception:
            pass
    else:
        # The single concave corner sits at (BU, BU); every other vertical edge is
        # convex. Two passes, because the two get different radii; a failure on a
        # degenerate footprint leaves the corner square rather than killing the part.
        try:
            body = body.edges("|Z").filter(lambda e: not _is_inner_corner(e)).fillet(BRACE_OUT_R)
        except Exception:
            pass
        try:
            body = body.edges("|Z").filter(_is_inner_corner).fillet(BRACE_IN_R)
        except Exception:
            pass

    # Interface: one 4.2 mm hole at the centre of every cell.
    if holes_enabled:
        centres = []
        for i in range(a):
            centres.append((i * BU + BU / 2.0, BU / 2.0))
        for j in range(1, b):
            centres.append((BU / 2.0, j * BU + BU / 2.0))

        cutters = []
        r = HOLE_D / 2.0
        c = BRACE_MOUTH_C
        for cx, cy in centres:
            cutters.append(
                cq.Solid.makeCylinder(r, t + 2.0, cq.Vector(cx, cy, -1.0), cq.Vector(0, 0, 1))
            )
            # Form: a 45 degree lead-in at each mouth, top and bottom. A cone
            # frustum opening outward is the chamfer; makeCone takes the two radii.
            cutters.append(
                cq.Solid.makeCone(r, r + c, c, cq.Vector(cx, cy, t - c), cq.Vector(0, 0, 1))
            )
            cutters.append(
                cq.Solid.makeCone(r + c, r, c, cq.Vector(cx, cy, 0.0), cq.Vector(0, 0, 1))
            )
        body = _cut_all(body, cutters)

    # Centre the part on the origin so the viewer frames it like the other modes.
    return body.translate((-ax / 2.0, -by / 2.0, -t / 2.0))


def _is_inner_corner(edge):
    """True for the one vertical edge at the L's re-entrant corner, at (BU, BU)."""
    try:
        c = edge.Center()
        return abs(c.x - BU) < 1e-6 and abs(c.y - BU) < 1e-6
    except Exception:
        return False


# ── Fastener ─────────────────────────────────────────────────────────────────
def build_fastener():
    """A pin (`fastener_type_id` 0) or a plain shaft (1), `length_units` BU long.

    Interface: 4.0 mm shank — 0.2 mm diametral clearance in the 4.2 mm hole — a
    5.7 mm collar on the pin, and a Z extent of exactly `length_units x 10 mm`.
    Form: the collar's conical underside and the lead-in taper on the free end.
    """
    total = length_units * BU
    rs = SHANK_D / 2.0
    rc = COLLAR_D / 2.0

    lead = min(LEAD_IN_H, total / 6.0)
    rl = LEAD_IN_D / 2.0

    if fastener_type_id == 0:
        # Pin: shank the full declared length, tapered at the free (z=0) end only.
        parts = [
            cq.Solid.makeCone(rl, rs, lead, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1)),
            cq.Solid.makeCylinder(rs, total - lead, cq.Vector(0, 0, lead), cq.Vector(0, 0, 1)),
        ]
        # Form: a collar that is a cylindrical land above a conical underside taper,
        # sitting INSIDE the declared length so the Z extent stays on the interface.
        land = min(COLLAR_LAND_H, total / 3.0)
        taper = min(COLLAR_TAPER_H, total / 3.0)
        z0 = total - land - taper
        parts.append(cq.Solid.makeCone(rs, rc, taper, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1)))
        parts.append(
            cq.Solid.makeCylinder(rc, land, cq.Vector(0, 0, z0 + taper), cq.Vector(0, 0, 1))
        )
    else:
        # Plain shaft: no collar, tapered at both free ends.
        parts = [
            cq.Solid.makeCone(rl, rs, lead, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1)),
            cq.Solid.makeCylinder(
                rs, total - 2.0 * lead, cq.Vector(0, 0, lead), cq.Vector(0, 0, 1)
            ),
            cq.Solid.makeCone(
                rs, rl, lead, cq.Vector(0, 0, total - lead), cq.Vector(0, 0, 1)
            ),
        ]

    solid = parts[0].fuse(*parts[1:])
    return cq.Workplane(obj=solid).translate((0, 0, -total / 2.0))


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "brace":
    result = build_brace()
elif target_part == "fastener":
    result = build_fastener()
else:
    result = build_beam()
