"""
Rugged Box — sealed hinged carry case. Yantra4D hyperobject cartridge (CadQuery / B-Rep).

A printable protective case: a deep base, a shallower lid, a continuous seal ring
between them, print-in-place knuckle hinges along the back, over-centre latch straps
along the front, and optional stacking feet.

Clean-room authorship (ADR-021 §3/§4)
-------------------------------------
Written from a recorded interface specification only. The SEAL, HINGE FIT, LATCH
CATCH and PAYLOAD ENVELOPE are dimensional interfaces held to the recorded values so
that lids, gaskets and latches interchange. Everything that is FORM — the shell
silhouette, the wall treatment, the latch strap outline and the foot pad shape — is
MADFAM's own design, deliberately unlike any prior implementation.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `internalBoxWidthXMm`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.

Geometry notes (OCCT):
  - Fillets and chamfers are applied BEFORE features are cut. Filleting an edge
    that a later cut re-creates is the classic OCCT segfault.
  - Every cutting tool overshoots the material it removes.
  - Genuinely separate bodies (latch straps, feet, the parts of `complete`) are
    combined with cq.Compound.makeCompound. A union of non-touching solids leaves
    phantom slivers and reports the wrong body count.
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


# ── Parameters — every one of these reaches the geometry ─────────────────────
# dimensions
internalBoxWidthXMm      = float(PARAM(lambda: internalBoxWidthXMm,      100.0))
internalboxLengthYMm     = float(PARAM(lambda: internalboxLengthYMm,      60.0))
internalBoxTopHeightZMm  = float(PARAM(lambda: internalBoxTopHeightZMm,   20.0))
internalboxBottomHeightZMm = float(PARAM(lambda: internalboxBottomHeightZMm, 20.0))
# wall & rim
boxWallWidthMm           = float(PARAM(lambda: boxWallWidthMm,             3.0))
boxChamferRadiusMm       = float(PARAM(lambda: boxChamferRadiusMm,         4.0))
rimWidthMm               = float(PARAM(lambda: rimWidthMm,                 2.0))
rimHeightMm              = float(PARAM(lambda: rimHeightMm,                3.0))
# seal
boxSealType              = int(  PARAM(lambda: boxSealType,                  1))
gasketSlotWidth          = float(PARAM(lambda: gasketSlotWidth,            2.2))
gasketSlotDepth          = float(PARAM(lambda: gasketSlotDepth,            2.2))
# ribs
numSideSupportRibs       = int(  PARAM(lambda: numSideSupportRibs,           2))
supportRibThickness      = float(PARAM(lambda: supportRibThickness,        2.0))
supportRibWidth          = float(PARAM(lambda: supportRibWidth,            4.0))
# dividers
countainerWidthXSections = int(  PARAM(lambda: countainerWidthXSections,     1))
boxLengthYSections       = int(  PARAM(lambda: boxLengthYSections,           1))
numCountainerWidthXSectionsToSkip = int(PARAM(lambda: numCountainerWidthXSectionsToSkip, 0))
numBoxLengthYSectionsToSkip       = int(PARAM(lambda: numBoxLengthYSectionsToSkip,       0))
# hinges
numberOfHinges           = int(  PARAM(lambda: numberOfHinges,               2))
hingeTotalWidthMm        = float(PARAM(lambda: hingeTotalWidthMm,         25.0))
hingeRadiusMm            = float(PARAM(lambda: hingeRadiusMm,              4.0))
hingeCenterOffsetMm      = float(PARAM(lambda: hingeCenterOffsetMm,        5.0))
# latches
numberOfLatches          = int(  PARAM(lambda: numberOfLatches,              2))
latchSupportTotalWidth   = float(PARAM(lambda: latchSupportTotalWidth,    25.0))
latchCenterOffsetMm      = float(PARAM(lambda: latchCenterOffsetMm,        5.0))
latchClipCutoutAngle     = float(PARAM(lambda: latchClipCutoutAngle,      25.0))
latchOpenerLengthMultiplier = float(PARAM(lambda: latchOpenerLengthMultiplier, 1.4))
# feet
isFeetAdded              = bool( PARAM(lambda: isFeetAdded,              False))
feetwidthMm              = float(PARAM(lambda: feetwidthMm,                4.0))
feetLengthMm             = float(PARAM(lambda: feetLengthMm,              10.0))
boxGapMm                 = float(PARAM(lambda: boxGapMm,                   1.5))
# quality
BoxPolygonStyle          = int(  PARAM(lambda: BoxPolygonStyle,              2))

target_part = str(PARAM(lambda: target_part, "bottom"))
mode        = str(PARAM(lambda: mode,        ""))


# ── Interface constants (ADR-021 §4 — these MUST NOT drift) ──────────────────
# The seal is one interface seen three ways: the ring, the groove in the base and
# the rim on the lid. All three derive from GASKET_INSET_PER_SIDE below.
GASKET_INSET_PER_SIDE = 1.75   # ring outer face sits this far inside the shell face
HINGE_RUNNING_CLEAR   = 0.5    # radial base-knuckle → lid-knuckle clearance
HINGE_AXIAL_CLEAR     = 0.5    # per side; lid knuckle is 1.0 mm narrower overall
ASSEMBLY_CLEARANCE    = 0.5    # lid-to-base fit allowance
LATCH_STRAP_THICKNESS = 4.0    # latch strap / catch thickness
LATCH_ENGAGEMENT      = 5.0    # anchor and clip block height
FOOT_PAD_HEIGHT       = 3.0    # stacking foot height

EPS = 0.01      # coincident-face nudge
OVER = 2.0      # cutter overshoot


# ── Quality → tessellation ───────────────────────────────────────────────────
# BoxPolygonStyle is a real geometric choice, not a label: at the two low-poly
# settings the cylindrical features become inscribed prisms with 8 or 16 sides,
# and only "Curved" emits a true circular profile. Every cylinder in the
# cartridge goes through round_profile(), so changing this parameter changes the
# mesh — which the manifest promises and a declared-but-inert parameter breaks.
def arc_segments():
    if BoxPolygonStyle <= 1:
        return 8
    if BoxPolygonStyle == 2:
        return 16
    return 0          # 0 == a true circle, no faceting


def round_profile(wp, r):
    """A circular or polygonal profile of radius r on the given workplane.

    The polygon is INSCRIBED — its vertices sit on the circle of radius r, so
    its maximum extent is exactly 2r. That keeps the hinge knuckle's measured
    diameter on its declared interface value at every quality setting; a
    circumscribed polygon would measure oversize and break the ±0.05 mm band.
    `polygon(n, d)` takes the circumscribed-circle diameter of the polygon,
    which is precisely 2r for the inscribed case.
    """
    n = arc_segments()
    if n <= 0:
        return wp.circle(r)
    return wp.polygon(n, 2.0 * r)


# ── Derived envelope ─────────────────────────────────────────────────────────
wall  = max(0.6, boxWallWidthMm)
cav_x = max(5.0, internalBoxWidthXMm)          # payload envelope X  (INTERFACE)
cav_y = max(5.0, internalboxLengthYMm)         # payload envelope Y  (INTERFACE)
cav_zb = max(2.0, internalboxBottomHeightZMm)  # payload depth, base (INTERFACE)
cav_zt = max(2.0, internalBoxTopHeightZMm)     # payload depth, lid  (INTERFACE)

shell_x = cav_x + 2.0 * wall
shell_y = cav_y + 2.0 * wall
base_z  = cav_zb + wall                        # floor + cavity
lid_z   = cav_zt + wall

# Outer corner rounding, clamped so it can never exceed half the short side.
corner_r = max(0.0, min(boxChamferRadiusMm, min(shell_x, shell_y) / 2.0 - 0.2))
inner_r  = max(0.0, corner_r - wall)

# ── FORM: the shell signature ────────────────────────────────────────────────
# Our silhouette is NOT the baseline's plain chamfered box. Three devices carry it:
#   1. a continuous BELT RIB — a shallow band standing proud of the wall at the
#      seam, running all the way round both halves, which reads as one line when
#      the case is closed;
#   2. CORNER BUMPERS — a thicker pilaster at each vertical edge, so the case
#      lands on its corners rather than its faces;
#   3. a SOFTENED TOP/BOTTOM — the outer floor and lid crown are eased, not square.
BELT_PROUD  = 1.2                                   # how far the belt stands out
BELT_HEIGHT = 5.0                                   # belt band height
BUMPER_PROUD = 1.6                                  # corner pilaster projection
BUMPER_SPAN  = max(6.0, min(18.0, min(shell_x, shell_y) * 0.16))
# Top/bottom edge ease.
#
# Bounded by the skin actually behind that face. The base floor and the lid
# crown are each `wall` thick, and this fillet rounds their outer edge — so it
# must stay well under `wall`, not merely under a fraction of it that still
# leaves the skin marginal. The `tiny-20x20` preset (1 mm wall, a 5 mm cavity in
# a 6 mm lid) is the case that forced the tighter bound: a 0.45 mm ease on a
# 1 mm crown pinched the crown off as a second body.
CROWN_EASE   = max(0.0, min(1.2, wall * 0.3))

# ── The seal (INTERFACE) ─────────────────────────────────────────────────────
# The ring outer face is GASKET_INSET_PER_SIDE inside the shell face on every
# side, so at defaults 106 - 2*1.75 = 102.5 and 66 - 2*1.75 = 62.5.
gasket_outer_x = shell_x - 2.0 * GASKET_INSET_PER_SIDE
gasket_outer_y = shell_y - 2.0 * GASKET_INSET_PER_SIDE
ring_w = max(0.4, min(rimWidthMm, wall + GASKET_INSET_PER_SIDE - 0.2))
gasket_h = max(1.0, min(gasketSlotDepth, 5.0))      # 1–5 mm range is INTERFACE
groove_w = max(ring_w + 0.05, gasketSlotWidth)      # groove accepts the ring
gasket_r_out = max(0.0, corner_r - GASKET_INSET_PER_SIDE)
gasket_r_in  = max(0.0, gasket_r_out - ring_w)

# Lid engagement rim (INTERFACE: rimHeightMm deep, ASSEMBLY_CLEARANCE loose)
rim_h = max(0.5, rimHeightMm)
rim_out_x = gasket_outer_x - ASSEMBLY_CLEARANCE
rim_out_y = gasket_outer_y - ASSEMBLY_CLEARANCE

# ── The hinge (INTERFACE) ────────────────────────────────────────────────────
knuckle_r_base = max(1.0, hingeRadiusMm)                       # 4.0 default
knuckle_r_lid  = max(0.5, knuckle_r_base - HINGE_RUNNING_CLEAR)  # 3.5 default
knuckle_w_base = max(4.0, hingeTotalWidthMm)                   # 25.0 default
knuckle_w_lid  = max(2.0, knuckle_w_base - 2.0 * HINGE_AXIAL_CLEAR)  # 24.0
n_hinges  = max(1, numberOfHinges)
n_latches = max(1, numberOfLatches)

# ── The latch (INTERFACE) ────────────────────────────────────────────────────
catch_w = max(4.0, latchSupportTotalWidth)   # 25.0 default — the catch the strap clips over
strap_t = LATCH_STRAP_THICKNESS
engage  = LATCH_ENGAGEMENT


def _spread(count, offset, span):
    """Evenly place `count` features across `span`, pushed apart by `offset`.

    A single feature sits centred. Two or more spread symmetrically; `offset`
    widens the spread, clamped so the outermost feature stays on the wall.
    """
    if count <= 1:
        return [0.0]
    usable = max(1.0, span - 2.0 * (offset if offset > 0 else 0.0))
    pitch = usable / count
    limit = span / 2.0 - 1.0
    out = []
    for i in range(count):
        p = -usable / 2.0 + pitch * (i + 0.5)
        scale = 1.0 + (2.0 * offset / span if span > 0 else 0.0)
        p = p * scale
        out.append(max(-limit, min(limit, p)))
    return out


# ── FORM helpers ─────────────────────────────────────────────────────────────
def safe_fillet(wp, selector, r):
    """Fillet `selector` by r, but only keep the result if it is still ONE valid
    solid.

    OCCT does not always raise when a fillet over-runs the material behind the
    edge: on a thin skin it can return a shape that is quietly split or
    self-intersecting, which then exports as extra bodies. A bare try/except
    catches the exception case and misses this one, so the result is checked.
    """
    if r <= 0.05:
        return wp
    try:
        out = wp.edges(selector).fillet(r)
    except Exception:
        return wp
    try:
        if len(out.val().Solids()) == 1 and out.val().isValid():
            return out
    except Exception:
        pass
    return wp


def _fuse(base, parts):
    """Union a list of solids onto `base` in ONE n-ary boolean.

    Chaining `.union()` per feature makes OCCT rebuild the whole shape each
    time; on this cartridge that was the single largest cost. Fusing the
    additive features together first, then fusing that once onto the shell,
    produces the identical solid in a fraction of the time.
    """
    parts = [q for q in parts if q is not None]
    if not parts:
        return base
    tool = parts[0]
    for q in parts[1:]:
        tool = tool.union(q)
    return base.union(tool)


def _subtract(base, parts):
    """Cut a list of tools from `base`, fusing the tools first (same reasoning
    as _fuse: one boolean against a combined tool, not one per feature)."""
    parts = [q for q in parts if q is not None]
    if not parts:
        return base
    tool = parts[0]
    for q in parts[1:]:
        tool = tool.union(q)
    return base.cut(tool)


def rounded_rect_wire(w, d, r, z0=0.0):
    """A rounded-rectangle WIRE on the XY plane at z0: four straights joined by
    four quarter arcs.

    Drawn as 2D geometry rather than produced by filleting a 3D box. A
    `.edges("|Z").fillet(r)` is a full OCCT shape rebuild every time, and this
    cartridge needs a rounded profile a dozen times per part; building the
    profile once as a wire and extruding it is the same solid for a fraction of
    the cost, and it cannot fail the way a fillet on an already-featured solid
    can.
    """
    hw = w / 2.0
    hd = d / 2.0
    rr = max(0.0, min(r, hw - 1e-6, hd - 1e-6))
    wp = cq.Workplane("XY").workplane(offset=z0)
    if rr <= 0.05:
        return wp.rect(w, d)
    return (wp
            .moveTo(-hw + rr, -hd)
            .lineTo(hw - rr, -hd)
            .radiusArc((hw, -hd + rr), rr)
            .lineTo(hw, hd - rr)
            .radiusArc((hw - rr, hd), rr)
            .lineTo(-hw + rr, hd)
            .radiusArc((-hw, hd - rr), rr)
            .lineTo(-hw, -hd + rr)
            .radiusArc((-hw + rr, -hd), rr)
            .close())


def rounded_prism(w, d, h, r, z0=0.0):
    """Axis-aligned prism, XY-centred, base at z0, vertical edges rounded by r."""
    return rounded_rect_wire(w, d, r, z0).extrude(h)


def belt_band(z0, h):
    """FORM: the continuous belt rib — a band standing BELT_PROUD off the wall,
    right around the shell.

    Built as an extruded 2D RING PROFILE, not as a filleted solid that is then
    hollowed. Filleting a hollow rounded band and cutting it costs three heavy
    OCCT booleans and roughly eight seconds per call; a two-wire face extrudes
    in a fraction of that and produces the identical solid.
    """
    # One face carrying two wires — the outer belt profile and the inner hole —
    # extruded as a single ring. No boolean, no fillet.
    outer = rounded_rect_wire(shell_x + 2.0 * BELT_PROUD, shell_y + 2.0 * BELT_PROUD,
                              corner_r + BELT_PROUD, z0)
    inner = rounded_rect_wire(shell_x - EPS, shell_y - EPS,
                              max(0.0, corner_r - EPS), z0)
    return outer.add(inner.wires()).toPending().extrude(h)


def corner_bumpers(z0, h):
    """FORM: four corner pilasters. Each is a rounded post hugging one vertical
    edge, projecting BUMPER_PROUD, so the case lands on its corners.

    The post is anchored on the shell's own CORNER-ARC CENTRE and its radius is
    tied to the corner radius, so it always overlaps the shell and never escapes
    the belt envelope. That removes the trimming `.intersect()` a naive version
    needs — an intersect against a filleted prism is one of the most expensive
    booleans OCCT offers.

    Placing the post at the nominal rectangle corner instead leaves it floating
    free of the shell whenever the corner radius is large relative to the box:
    the `small-rounded-50x30` preset (50x30 cavity, 15 mm chamfer) did exactly
    that and produced four detached posts instead of four bumpers.
    """
    hx = shell_x / 2.0
    hy = shell_y / 2.0
    # The shell's corner arc is centred here, radius corner_r.
    cx = max(0.0, hx - corner_r)
    cy = max(0.0, hy - corner_r)
    # Reach BUMPER_PROUD past that arc — always overlapping material, never past
    # the belt line at corner_r + BELT_PROUD when BUMPER_PROUD <= BELT_PROUD... and
    # when it is not, the belt simply absorbs the post, which is the intended read.
    post_r = max(1.0, corner_r + BUMPER_PROUD)
    out = None
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            p = (cq.Workplane("XY").workplane(offset=z0)
                 .center(sx * cx, sy * cy))
            p = round_profile(p, post_r).extrude(h)
            out = p if out is None else out.union(p)
    return out


def side_ribs(z0, h, external):
    """FORM: stiffener ribs on the long walls. `numSideSupportRibs` per side,
    supportRibWidth along the wall, supportRibThickness proud of it."""
    if numSideSupportRibs <= 0 or supportRibThickness <= 0 or supportRibWidth <= 0:
        return None
    ribs = []
    xs = _spread(numSideSupportRibs, 0.0, shell_x * 0.72)
    t = supportRibThickness
    w = supportRibWidth
    for x in xs:
        for sy in (-1.0, 1.0):
            if external:
                y = sy * (shell_y / 2.0 + t / 2.0 - EPS)
            else:
                y = sy * (cav_y / 2.0 - t / 2.0 + EPS)
            r = (cq.Workplane("XY").workplane(offset=z0)
                 .center(x, y)
                 .box(w, t, h, centered=(True, True, False)))
            ribs.append(r)
    out = ribs[0]
    for r in ribs[1:]:
        out = out.union(r)
    return out


def dividers(z0, h):
    """Interior partition grid. `countainerWidthXSections` cells across X means
    that many minus one walls; the `...ToSkip` counts drop the first N walls,
    which merges the leading cells into one larger compartment."""
    walls = []
    nx = max(1, countainerWidthXSections)
    ny = max(1, boxLengthYSections)
    t = max(0.6, min(supportRibThickness, wall))
    if nx > 1:
        step = cav_x / nx
        skip = max(0, min(numCountainerWidthXSectionsToSkip, nx - 1))
        for i in range(1 + skip, nx):
            x = -cav_x / 2.0 + i * step
            walls.append(cq.Workplane("XY").workplane(offset=z0)
                         .center(x, 0).box(t, cav_y, h, centered=(True, True, False)))
    if ny > 1:
        step = cav_y / ny
        skip = max(0, min(numBoxLengthYSectionsToSkip, ny - 1))
        for i in range(1 + skip, ny):
            y = -cav_y / 2.0 + i * step
            walls.append(cq.Workplane("XY").workplane(offset=z0)
                         .center(0, y).box(cav_x, t, h, centered=(True, True, False)))
    if not walls:
        return None
    out = walls[0]
    for w in walls[1:]:
        out = out.union(w)
    return out


def pocket_depth(skin):
    """How deep a foot pocket may go into a skin of the given thickness.

    Never more than half the skin it is cut into. On a thin-walled shallow lid
    the crown left above the cavity can be only a couple of millimetres; a
    pocket sized from `wall` alone (plus the crown ease above it) cut clean
    through and detached the crown as a second body.
    """
    return max(0.3, min(FOOT_PAD_HEIGHT * 0.5, wall * 0.4, skin * 0.5))


def foot_pockets(z0, skin=None):
    """Recesses that accept the printed feet, on the outer floor of the base and
    the crown of the lid, so a stack registers. Only cut when feet are enabled.

    `skin` is the material actually available at that face — the floor under the
    base cavity, or the crown above the lid cavity — so the pocket can be capped
    against it rather than against the nominal wall.
    """
    if not isFeetAdded:
        return None
    d = pocket_depth(wall if skin is None else skin)
    pockets = []
    for (x, y) in foot_positions():
        p = (cq.Workplane("XY").workplane(offset=z0)
             .center(x, y)
             .slot2D(max(feetLengthMm, feetwidthMm + 0.01) + 2.0 * 0.25,
                     feetwidthMm + 2.0 * 0.25, 0)
             .extrude(d))
        pockets.append(p)
    out = pockets[0]
    for p in pockets[1:]:
        out = out.union(p)
    return out


def foot_positions():
    """Where the four feet sit — inset from the shell corners by the stacking gap.

    The four pads must stay APART. Clamping each half-spacing at a bare 1.0 mm
    let the two rows overlap on a small box with a large corner radius (the
    `small-rounded-50x30` preset: a 36 mm deep shell with a 15 mm corner leaves
    only 1 mm of half-spacing for a 4 mm wide pad). Two intersecting solids in a
    compound export as a non-watertight mesh, so the floor here is half the pad
    size plus a real gap, and the pads are pulled inward rather than allowed to
    collide.
    """
    L = max(2.0, feetLengthMm)
    W = max(1.5, feetwidthMm)
    # Never closer than the pad's own size plus a printable gap.
    min_hx = L / 2.0 + 0.6
    min_hy = W / 2.0 + 0.6
    inset_x = max(L / 2.0 + boxGapMm, corner_r + L / 2.0)
    inset_y = max(W / 2.0 + boxGapMm, corner_r + W / 2.0)
    hx = max(min_hx, shell_x / 2.0 - inset_x)
    hy = max(min_hy, shell_y / 2.0 - inset_y)
    return [(-hx, -hy), (hx, -hy), (-hx, hy), (hx, hy)]


# ── Hinge geometry ───────────────────────────────────────────────────────────
def hinge_y_back():
    """Y of the hinge axis: just outside the back wall, on the seam plane."""
    return shell_y / 2.0 + knuckle_r_base - BELT_PROUD * 0.25


def hinge_x_positions():
    return _spread(n_hinges, hingeCenterOffsetMm, shell_x - 2.0 * corner_r - 4.0)


def base_knuckles():
    """The base half of each print-in-place knuckle: a full cylinder of
    knuckle_r_base, knuckle_w_base wide, on the seam plane at the back."""
    yb = hinge_y_back()
    out = None
    for x in hinge_x_positions():
        k = (cq.Workplane("YZ").workplane(offset=x - knuckle_w_base / 2.0)
             .center(yb, base_z))
        k = round_profile(k, knuckle_r_base).extrude(knuckle_w_base)
        # A web tying the knuckle back to the wall, so it is not a floating boss.
        web = (cq.Workplane("XY").workplane(offset=base_z - knuckle_r_base)
               .center(x, (shell_y / 2.0 + yb) / 2.0)
               .box(knuckle_w_base, max(0.5, yb - shell_y / 2.0 + knuckle_r_base),
                    knuckle_r_base * 2.0, centered=(True, True, False)))
        piece = k.union(web)
        out = piece if out is None else out.union(piece)
    return out


def lid_knuckles():
    """The lid half: knuckle_r_lid (0.5 mm under the base radius) and 1.0 mm
    narrower, so the printed pair turns freely. Built in the lid's own frame."""
    yb = hinge_y_back()
    out = None
    for x in hinge_x_positions():
        k = (cq.Workplane("YZ").workplane(offset=x - knuckle_w_lid / 2.0)
             .center(yb, 0.0))
        k = round_profile(k, knuckle_r_lid).extrude(knuckle_w_lid)
        web = (cq.Workplane("XY").workplane(offset=-knuckle_r_lid)
               .center(x, (shell_y / 2.0 + yb) / 2.0)
               .box(knuckle_w_lid, max(0.5, yb - shell_y / 2.0 + knuckle_r_lid),
                    knuckle_r_lid * 2.0, centered=(True, True, False)))
        piece = k.union(web)
        out = piece if out is None else out.union(piece)
    return out


def base_knuckle_cutters():
    """The pocket in the base that receives the lid knuckle, with the running
    clearance already in it. Cut from the base after the knuckles are unioned."""
    yb = hinge_y_back()
    out = None
    for x in hinge_x_positions():
        # Bore the barrel so the pair is a true knuckle, not a solid lug.
        bore = (cq.Workplane("YZ").workplane(offset=x - knuckle_w_base / 2.0 - OVER)
                .center(yb, base_z))
        bore = round_profile(bore, max(0.6, knuckle_r_base * 0.38)).extrude(
            knuckle_w_base + 2.0 * OVER)
        out = bore if out is None else out.union(bore)
    return out


# ── Latch geometry (catch = INTERFACE, strap outline = FORM) ─────────────────
def latch_x_positions():
    return _spread(n_latches, latchCenterOffsetMm, shell_x - 2.0 * corner_r - 4.0)


def latch_catches(z_seam, on_lid):
    """The blocks the latch strap engages. INTERFACE: catch_w wide, `engage` tall,
    and standing exactly LATCH_STRAP_THICKNESS proud of the shell face. Base gets
    the anchor, lid the clip.

    The block reaches back INTO the wall by `root` so the union is a real solid
    overlap, never a coincident-face touch — a zero-thickness union sheet is what
    makes an otherwise sound assembly report as non-watertight.
    """
    yf = -shell_y / 2.0
    root = max(1.0, wall * 0.6)          # embedded depth, inside the shell
    depth = strap_t + BELT_PROUD + root  # proud by strap_t past the belt line
    out = None
    for x in latch_x_positions():
        # The lid catch starts ASSEMBLY_CLEARANCE above the seam, so the closed
        # case leaves the strap a real gap to seat in — and the two catch faces
        # are never coplanar, which would otherwise leave a zero-thickness sheet
        # between them in the assembled preview.
        z0 = (z_seam - engage) if not on_lid else (z_seam + ASSEMBLY_CLEARANCE)
        blk = (cq.Workplane("XY").workplane(offset=z0)
               .center(x, yf - depth / 2.0 + root)
               .box(catch_w, depth, engage, centered=(True, True, False)))
        try:
            blk = blk.edges("|X and <Y").fillet(min(0.8, strap_t * 0.2))
        except Exception:
            pass
        out = blk if out is None else out.union(blk)
    return out


def latch_strap():
    """FORM: our latch strap. A waisted plate — wide at the catch ends, pinched at
    the waist — with a thumb ramp on the free end and a clip lip that engages the
    catch. The catch dimensions it mates to are INTERFACE; this outline is ours."""
    w = catch_w
    waist = max(w * 0.52, 4.0)
    body_len = engage * 2.0 + rim_h + 6.0
    tab_len = max(3.0, body_len * (latchOpenerLengthMultiplier - 1.0) + 4.0)
    total_len = body_len + tab_len

    # Waisted outline, drawn once and extruded to the interface thickness.
    pts = [
        (-w / 2.0, 0.0),
        (-w / 2.0, body_len * 0.22),
        (-waist / 2.0, body_len * 0.5),
        (-waist / 2.0, body_len * 0.82),
        (-w / 2.0, body_len),
        (-w * 0.40, total_len - 1.2),
        (0.0, total_len),
        (w * 0.40, total_len - 1.2),
        (w / 2.0, body_len),
        (waist / 2.0, body_len * 0.82),
        (waist / 2.0, body_len * 0.5),
        (w / 2.0, body_len * 0.22),
        (w / 2.0, 0.0),
    ]
    strap = (cq.Workplane("XY").polyline(pts).close().extrude(strap_t))

    # The clip lip: a bar across the free end that hooks the lid catch.
    lip = (cq.Workplane("XY").workplane(offset=strap_t - EPS)
           .center(0.0, body_len * 0.90)
           .box(w * 0.80, max(1.2, engage * 0.34), max(1.0, engage * 0.5),
                centered=(True, True, False)))
    strap = strap.union(lip)

    # The pivot eye at the anchored end (INTERFACE: it rides the anchor block).
    eye = (cq.Workplane("XY").workplane(offset=-OVER)
           .center(0.0, max(1.6, engage * 0.44)))
    eye = round_profile(eye, max(0.8, engage * 0.26)).extrude(strap_t + 2.0 * OVER)
    strap = strap.cut(eye)

    # The clip cutout — latchClipCutoutAngle sets how far the relief is swept back,
    # so a tight angle grips and a loose one releases.
    ang = max(5.0, min(80.0, latchClipCutoutAngle))
    relief_d = max(0.4, strap_t * 0.5 * math.tan(math.radians(ang)) * 0.5)
    relief = (cq.Workplane("XY").workplane(offset=strap_t - relief_d)
              .center(0.0, body_len * 0.55)
              .box(waist * 0.62, max(1.0, body_len * 0.16), relief_d + OVER,
                   centered=(True, True, False)))
    strap = strap.cut(relief)

    # FORM: thumb ramp on the free end, so the tab lifts without a fingernail.
    ramp_h = min(strap_t * 0.6, 2.0)
    ramp = (cq.Workplane("XZ").workplane(offset=w / 2.0)
            .polyline([(total_len, strap_t + EPS),
                       (total_len - tab_len * 0.8, strap_t + EPS),
                       (total_len, strap_t - ramp_h)])
            .close().extrude(-w))
    strap = strap.cut(ramp)
    return strap


def latch_bodies():
    """Every latch strap as a SEPARATE body, spread so they never touch — the
    baseline merged them into one. Returned as a list for makeCompound."""
    proto = latch_strap()
    bb = proto.val().BoundingBox()
    pitch = bb.xlen + max(4.0, catch_w * 0.35)
    out = []
    for i in range(n_latches):
        x = (i - (n_latches - 1) / 2.0) * pitch
        out.append(proto.translate((x, 0.0, 0.0)))
    return out


# ── Feet (FORM: stadium pads, not the baseline's flat rectangles) ────────────
def feet_bodies():
    """Four stacking pads. FORM: an obround (stadium) pad with an eased underside,
    sized by feetLengthMm × feetwidthMm and placed by boxGapMm — all three of the
    manifest's feet parameters reach this geometry."""
    L = max(2.0, feetLengthMm)
    W = max(1.5, feetwidthMm)
    slot_len = max(L, W + 0.01)
    out = []
    # FORM: chamfer the ground face so the pad does not catch on a lip. Keep it
    # well inside both the pad half-width and the pad height: a chamfer that
    # consumes the whole semicircular end of the stadium leaves OCCT with a
    # degenerate face, which exports as a non-watertight body rather than
    # raising — so the size is bounded here rather than caught afterwards.
    cham = min(0.8, W * 0.25, FOOT_PAD_HEIGHT * 0.3)
    for (x, y) in foot_positions():
        pad = (cq.Workplane("XY").center(x, y)
               .slot2D(slot_len, W, 0)
               .extrude(FOOT_PAD_HEIGHT))
        if cham > 0.05:
            try:
                chamfered = pad.edges("<Z").chamfer(cham)
                # Only keep it if it is still one sound solid. A silently
                # damaged chamfer is worse than no chamfer.
                if len(chamfered.val().Solids()) == 1 and chamfered.val().isValid():
                    pad = chamfered
            except Exception:
                pass
        out.append(pad)
    return out


# ── The gasket ring (INTERFACE) ──────────────────────────────────────────────
def build_gasket():
    """One closed rectangular ring: gasket_outer_x × gasket_outer_y, ring_w wide,
    gasket_h tall. Printed in TPU and pressed into the base groove."""
    outer = rounded_prism(gasket_outer_x, gasket_outer_y, gasket_h, gasket_r_out)
    inner = rounded_prism(gasket_outer_x - 2.0 * ring_w, gasket_outer_y - 2.0 * ring_w,
                          gasket_h + 2.0 * OVER, gasket_r_in, -OVER)
    return outer.cut(inner)


# ── The base ─────────────────────────────────────────────────────────────────
def build_bottom():
    # 1. FORM shell, eased before anything is cut into it (OCCT ordering).
    body = safe_fillet(rounded_prism(shell_x, shell_y, base_z, corner_r),
                       "<Z", CROWN_EASE)

    # 2. Every additive feature in ONE fuse: the FORM belt and bumpers and ribs,
    #    the INTERFACE hinge knuckles, and the INTERFACE latch anchor blocks.
    belt_h = min(BELT_HEIGHT, base_z * 0.6)
    body = _fuse(body, [
        belt_band(base_z - belt_h, belt_h),
        corner_bumpers(0.0, base_z - CROWN_EASE),
        side_ribs(max(0.0, base_z * 0.18), base_z * 0.55, external=True),
        base_knuckles(),
        latch_catches(base_z, on_lid=False),
    ])

    # 3. Every subtractive feature in ONE cut: the payload cavity (INTERFACE
    #    envelope), the seal groove (INTERFACE), the hinge bore and the foot
    #    pockets.
    groove_out = rounded_prism(gasket_outer_x + (groove_w - ring_w),
                               gasket_outer_y + (groove_w - ring_w),
                               gasket_h + OVER,
                               max(0.0, gasket_r_out + (groove_w - ring_w) / 2.0),
                               base_z - gasket_h)
    groove_in = rounded_prism(gasket_outer_x - 2.0 * ring_w - (groove_w - ring_w),
                              gasket_outer_y - 2.0 * ring_w - (groove_w - ring_w),
                              gasket_h + 2.0 * OVER,
                              max(0.0, gasket_r_in - (groove_w - ring_w) / 2.0),
                              base_z - gasket_h - OVER)
    cuts = [
        rounded_prism(cav_x, cav_y, cav_zb + OVER, inner_r, wall),
        groove_out.cut(groove_in),
        base_knuckle_cutters(),
        foot_pockets(-EPS, skin=wall),   # base: the skin is the floor
    ]
    if boxSealType == 2:
        # Seal type 2 adds a drain relief outside the groove; type 1 is the plain
        # rim. The parameter must change the geometry, so it does.
        rd = min(0.6, gasket_h * 0.3)
        relief = rounded_prism(
            gasket_outer_x + 2.0 * (GASKET_INSET_PER_SIDE * 0.5),
            gasket_outer_y + 2.0 * (GASKET_INSET_PER_SIDE * 0.5),
            rd + OVER,
            max(0.0, gasket_r_out + GASKET_INSET_PER_SIDE * 0.5),
            base_z - rd)
        keep = rounded_prism(gasket_outer_x + (groove_w - ring_w) + 0.02,
                             gasket_outer_y + (groove_w - ring_w) + 0.02,
                             rd + 2.0 * OVER,
                             max(0.0, gasket_r_out), base_z - 1.0 - OVER)
        cuts.append(relief.cut(keep))
    body = _subtract(body, cuts)

    # 4. Interior dividers and inner ribs, added after the cavity exists.
    body = _fuse(body, [
        dividers(wall, cav_zb),
        side_ribs(wall, cav_zb * 0.85, external=False),
    ])
    return body


# ── The lid ──────────────────────────────────────────────────────────────────
def build_top(flat=True):
    """The lid, built seam-face at z=0 upward to the crown at lid_z.
    `flat=True` returns it flipped for printing (crown on the bed)."""
    body = safe_fillet(rounded_prism(shell_x, shell_y, lid_z, corner_r),
                       ">Z", CROWN_EASE)

    # INTERFACE: the engagement rim, rim_h tall below the seam face, with
    # ASSEMBLY_CLEARANCE under the groove it enters.
    #
    # Built as a SHOULDER, not a free-hanging ring. The rim's INNER wall is the
    # sealing face and carries the interface dimension; the outer face is only
    # structure and runs out to whichever is larger, its own interface value or
    # the cavity wall. On a thin wall the cavity runs outside a nominal rim and
    # removes the ceiling it hangs from, which split the lid into two bodies.
    # See docs/CLEANROOM-VERIFICATION.md section 4b.
    rim_seal_in_x = rim_out_x - 2.0 * ring_w   # INTERFACE: the sealing face
    rim_seal_in_y = rim_out_y - 2.0 * ring_w
    rim_out = rounded_prism(max(rim_out_x, cav_x + EPS),
                            max(rim_out_y, cav_y + EPS),
                            rim_h,
                            max(0.0, gasket_r_out - ASSEMBLY_CLEARANCE / 2.0), -rim_h)
    rim_in = rounded_prism(rim_seal_in_x, rim_seal_in_y,
                           rim_h + 2.0 * OVER,
                           max(0.0, gasket_r_in - ASSEMBLY_CLEARANCE / 2.0),
                           -rim_h - OVER)
    adds = [
        # FORM: the same belt and bumpers, so the closed case reads as one object.
        belt_band(0.0, min(BELT_HEIGHT, lid_z * 0.6)),
        corner_bumpers(0.0, lid_z - CROWN_EASE),
        side_ribs(max(0.0, lid_z * 0.25), lid_z * 0.5, external=True),
        rim_out.cut(rim_in),
        lid_knuckles(),                       # INTERFACE
        latch_catches(0.0, on_lid=True),      # INTERFACE
    ]
    if boxSealType == 2:
        # A matching bead on the lid rim face for the second seal type.
        bd = min(0.6, rim_h * 0.25)
        bead = rounded_prism(rim_out_x, rim_out_y, bd,
                             max(0.0, gasket_r_out - ASSEMBLY_CLEARANCE / 2.0),
                             -rim_h - bd)
        bead_in = rounded_prism(rim_out_x - 2.0 * ring_w, rim_out_y - 2.0 * ring_w,
                                bd + 2.0 * OVER, max(0.0, gasket_r_in),
                                -rim_h - 1.0 - OVER)
        adds.append(bead.cut(bead_in))
    body = _fuse(body, adds)

    # The crown is what is left above the cavity once it is hollowed, minus the
    # ease already rounded off its outer edge. The foot pockets are capped
    # against it.
    lid_crown = max(0.4, lid_z - cav_zt - CROWN_EASE)

    # Hollow the lid cavity from the seam face UPWARD ONLY. Dipping below z=0
    # shaves the rim, which lives entirely under the seam plane; the rim is
    # widened where it is built so the cavity cannot undercut it. The cavity is
    # never shrunk - it is the payload interface.
    body = _subtract(body, [
        rounded_prism(cav_x, cav_y, cav_zt + OVER, inner_r, 0.0),
        # Lid: the skin is the crown left above the cavity, less the crown ease
        # already rounded off its outer edge.
        foot_pockets(lid_z - pocket_depth(lid_crown) + EPS, skin=lid_crown),
    ])

    body = _fuse(body, [side_ribs(0.0, cav_zt * 0.8, external=False)])

    if flat:
        # Print flat: rotate 180 degrees about X so the crown sits on the bed.
        body = body.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, lid_z))
    return body


# ── Assemblies ───────────────────────────────────────────────────────────────
def _solids(wp):
    """Every solid in a Workplane, as Shape objects for makeCompound."""
    return [s for s in wp.val().Solids()]


def build_complete():
    """All four printable parts, laid apart so they slice without overlap.
    A COMPOUND, never a union: the parts do not touch and must stay separate."""
    gap = max(8.0, shell_x * 0.08)
    bottom = build_bottom().translate((-(shell_x + gap) / 2.0, 0.0, 0.0))
    top = build_top(flat=True).translate(((shell_x + gap) / 2.0, 0.0, 0.0))

    y_row = shell_y / 2.0 + max(hinge_y_back(), 0.0) + gap
    gasket = build_gasket().translate((-(shell_x + gap) / 2.0, y_row, 0.0))

    latches = latch_bodies()
    shapes = _solids(bottom) + _solids(top) + _solids(gasket)
    for l in latches:
        shapes += _solids(l.translate(((shell_x + gap) / 2.0, y_row, 0.0)))
    if isFeetAdded:
        for f in feet_bodies():
            shapes += _solids(f.translate((0.0, -(shell_y + gap), 0.0)))
    return cq.Compound.makeCompound(shapes)


def build_closed_view():
    """Preview only: the lid seated on the base with the latches in place.
    Not for printing — the parts interpenetrate at the latch by design."""
    bottom = build_bottom()
    # The lid rides on the seam plane, its rim entering the base groove.
    top = build_top(flat=False).translate((0.0, 0.0, base_z))
    shapes = _solids(bottom) + _solids(top)
    strap = latch_strap()
    # Stand each strap clear of everything the front face already carries: the
    # belt rib and the latch catch blocks both stand proud of the wall, so
    # clearing only the strap thickness pushed the strap into the catches and
    # the preview came back non-watertight on the smallest preset.
    front_proud = strap_t + BELT_PROUD + max(BUMPER_PROUD, 0.0)
    for x in latch_x_positions():
        s = (strap.rotate((0, 0, 0), (1, 0, 0), 90)
             .translate((x, -shell_y / 2.0 - front_proud - 0.4,
                         base_z - engage - 0.5)))
        shapes += _solids(s)
    if isFeetAdded:
        for f in feet_bodies():
            shapes += _solids(f.translate((0.0, 0.0, -FOOT_PAD_HEIGHT)))
    return cq.Compound.makeCompound(shapes)


# ── Dispatch ─────────────────────────────────────────────────────────────────
# The platform renders one (mode, part) at a time and passes `target_part`. The
# multi-part modes (`complete`, `closed-view`) are named by `mode`, so a request
# for a single part inside them still yields that part's own geometry — which is
# what makes every (mode, part) render distinct.
if mode == "complete" and target_part in ("complete", "", "assembly"):
    result = build_complete()
elif mode == "closed-view" and target_part in ("closed-view", "", "assembly"):
    result = build_closed_view()
elif target_part == "top":
    result = build_top(flat=True)
elif target_part == "latches":
    result = cq.Compound.makeCompound(
        [s for l in latch_bodies() for s in _solids(l)])
elif target_part == "gasket":
    result = build_gasket()
elif target_part == "feet":
    result = cq.Compound.makeCompound(
        [s for f in feet_bodies() for s in _solids(f)])
elif target_part == "complete":
    result = build_complete()
elif target_part == "closed-view":
    result = build_closed_view()
else:
    result = build_bottom()
