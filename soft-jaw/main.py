"""
Parametric Vise Soft Jaw — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A machinable / printable soft-jaw insert that bolts into a standard CNC machine
vise (Kurt-style) and is pocketed to cradle a specific workpiece. The jaw is the
boolean  Base_Jaw − (vise bolt pattern) − (optional workpiece negative), with a
selectable gripping face (smooth / serrated / grid) and optional magnet pockets.

Three build targets are dispatched by `target_part`:
  - "jaw"      : a single soft-jaw block — vise bolt holes, gripping face,
                 optional round/rect workpiece pocket, optional magnet pockets.
  - "jaw_pair" : a matching left + right jaw set. The workpiece negative is split
                 across both jaws (each carries a half-pocket) so the closed vise
                 cradles the part — the way soft jaws are actually cut in pairs.
  - "vee_jaw"  : a jaw with a V-groove down the face to hold round stock (bar/pipe)
                 for cross-drilling or milling a flat.

The vise mounting is the CDG (Common Denominator Geometry): a Kurt-style vise jaw
bolt pattern (two counterbored SHCS through the jaw thickness at a standard span),
so any jaw generated here bolts onto the matching vise.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `jaw_width`).
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


MM = 25.4  # inches → millimetres


# ── Vise catalogue (the CDG standard bolt pattern per vise) ──────────────────
# width_in    : nominal jaw width the vise accepts (inches)
# bolt_span_in: centre-to-centre spacing of the two jaw mounting bolts (inches)
# bolt_shaft  : through-hole (clearance) diameter for the SHCS shaft (mm)
# bolt_head   : counterbore diameter for the SHCS head (mm)
# Values reflect common Kurt-style / industry hardware (1/2-13 SHCS on 6" vises).
_VISES = {
    0: {"name": "Kurt DX6 6\"",   "width_in": 6.0, "bolt_span_in": 3.875, "bolt_shaft": 11.0, "bolt_head": 16.0},
    1: {"name": "Orange Vise 6\"", "width_in": 6.0, "bolt_span_in": 4.000, "bolt_shaft": 11.0, "bolt_head": 16.0},
    2: {"name": "Tormach 5\"",     "width_in": 5.0, "bolt_span_in": 3.000, "bolt_shaft":  9.0, "bolt_head": 14.0},
}


# ── Parameters ───────────────────────────────────────────────────────────────
vise_model    = int(  PARAM(lambda: vise_model,      0))     # index into _VISES
jaw_width     = float(PARAM(lambda: jaw_width,       6.0))    # jaw width  (X, inch)
jaw_height    = float(PARAM(lambda: jaw_height,   1.735))     # jaw height (Z, inch)
jaw_thickness = float(PARAM(lambda: jaw_thickness, 0.75))     # jaw thickness (Y, inch)

face_pattern  = str(  PARAM(lambda: face_pattern, "smooth"))  # smooth|serrations|grid
serration_pitch = float(PARAM(lambda: serration_pitch, 2.5))  # groove pitch (mm)

workpiece      = str(  PARAM(lambda: workpiece,   "none"))    # none|round|rect
workpiece_dia  = float(PARAM(lambda: workpiece_dia,  25.0))   # round stock dia (mm)
workpiece_w    = float(PARAM(lambda: workpiece_w,    40.0))   # rect pocket width (mm, X)
workpiece_h    = float(PARAM(lambda: workpiece_h,    20.0))   # rect pocket height (mm, Z)
pocket_depth   = float(PARAM(lambda: pocket_depth,   10.0))   # how deep the pocket cuts (mm, Y)

magnet_pockets = bool( PARAM(lambda: magnet_pockets, True))   # 10x3mm magnet pockets on back
vee_angle      = float(PARAM(lambda: vee_angle,      90.0))   # included V-groove angle (deg)
pair_gap       = float(PARAM(lambda: pair_gap,       30.0))   # display gap between paired jaws (mm)

target_part    = str(  PARAM(lambda: target_part, "jaw"))     # jaw|jaw_pair|vee_jaw


# ── Resolve vise + derive envelope (all mm) ──────────────────────────────────
_vise = _VISES.get(vise_model, _VISES[0])

W = max(25.0, jaw_width * MM)          # jaw width  (X)
H = max(15.0, jaw_height * MM)         # jaw height (Z)
T = max(9.0, jaw_thickness * MM)       # jaw thickness (Y)

BOLT_SPAN  = _vise["bolt_span_in"] * MM
BOLT_SHAFT = _vise["bolt_shaft"]
BOLT_HEAD  = _vise["bolt_head"]
# keep the bolt span inside the jaw width with room for the counterbore
BOLT_SPAN = min(BOLT_SPAN, W - BOLT_HEAD - 4.0)
BOLT_SPAN = max(BOLT_SPAN, 0.0)

MAGNET_DIA   = 10.2   # 10 mm magnet + fit
MAGNET_DEEP  = 3.0    # 3 mm magnet thickness

# Body occupies X:[-W/2, W/2], Y:[0, T] (back face at y=0, gripping face at y=T),
# Z:[0, H] (base at z=0). The vise clamps the back; the workpiece sits at the face.


# ── Helpers ──────────────────────────────────────────────────────────────────
def jaw_blank():
    """The solid jaw block: back face at y=0, gripping face at y=T. The top
    front edge gets a small lead-in chamfer HERE — on the pristine straight edge,
    before any face grooves / pockets carve it (chamfering a serrated edge can
    crash the OCCT kernel, so it must happen on the clean blank)."""
    blank = cq.Workplane("XY").box(W, T, H, centered=(True, False, False))
    try:
        blank = blank.edges(">Z and >Y").chamfer(min(1.0, T / 6.0))
    except Exception:
        pass
    return blank


def bolt_cutter():
    """Two counterbored through-holes for the vise mounting SHCS. Drilled along
    +Y (from the back face into the vise). Each is a clearance shaft the full
    thickness plus a head counterbore recessed from the back face."""
    if BOLT_SPAN <= 1.0:
        xs = [0.0]
    else:
        xs = [-BOLT_SPAN / 2.0, BOLT_SPAN / 2.0]
    zc = H / 2.0
    shaft_r = min(BOLT_SHAFT, T * 0.9, W / 4.0) / 2.0
    head_r = min(BOLT_HEAD, W / 3.0) / 2.0
    head_r = max(head_r, shaft_r + 0.6)
    cbore_deep = min(max(T * 0.45, 5.0), T - 3.0)  # leave a bearing wall at the face

    cutter = None
    for x in xs:
        # full-length clearance shaft (Y axis)
        shaft = (
            cq.Workplane("XZ", origin=(x, -1.0, zc))
            .circle(shaft_r)
            .extrude(-(T + 2.0))   # extrude toward +Y through the block
        )
        # head counterbore recessed from the back face (y=0)
        cbore = (
            cq.Workplane("XZ", origin=(x, -1.0, zc))
            .circle(head_r)
            .extrude(-(cbore_deep + 1.0))
        )
        piece = shaft.union(cbore)
        cutter = piece if cutter is None else cutter.union(piece)
    return cutter


def magnet_cutter():
    """Two magnet pockets bored into the BACK face (y=0), one above and one below
    the bolt centreline, offset in X so they never clash with the bolts."""
    if not magnet_pockets:
        return None
    r = MAGNET_DIA / 2.0
    if r >= T / 2.0 - 0.5:
        return None
    xoff = W / 2.0 - r - 4.0
    zc = H / 2.0
    zsep = min(H / 3.0, zc - r - 1.0)
    pts = [(xoff, zc + zsep), (xoff, zc - zsep), (-xoff, zc + zsep), (-xoff, zc - zsep)]
    cutter = None
    for x, z in pts:
        pk = (
            cq.Workplane("XZ", origin=(x, 0.0, z))
            .circle(r)
            .extrude(-MAGNET_DEEP)   # into +Y from the back face
        )
        cutter = pk if cutter is None else cutter.union(pk)
    return cutter


def face_cutter():
    """Gripping-surface treatment cut into the front face (y=T). Serrations are
    horizontal V-grooves running in X; grid adds shallow vertical grooves too.
    Returns None for a smooth face."""
    if face_pattern == "smooth":
        return None

    pitch = max(1.5, min(serration_pitch, H / 4.0))
    groove_depth = min(0.8, pitch * 0.45)
    half_w = groove_depth  # ~90° V
    # Cap groove counts so the boolean stays fast (B-Rep unions/cuts are the
    # bottleneck); the pattern reads the same and remains dimensionally real.
    HZ_MAX, VT_MAX = 12, 10

    cutter = None

    def add(piece):
        nonlocal cutter
        cutter = piece if cutter is None else cutter.union(piece)

    # Horizontal V-grooves (run along X), stacked up the face in Z. The profile
    # spans the full width so a single-direction extrude covers the face.
    n = min(HZ_MAX, max(1, int(H / pitch) - 1))
    for i in range(1, n + 1):
        z = i * (H / (n + 1))
        prof = (
            cq.Workplane("YZ", origin=(-(W / 2.0 + 1.0), T, z))
            # profile in local (Y,Z): mouth at the face, apex cut inward (-Y)
            .polyline([(0.0, -half_w), (0.0, half_w), (-groove_depth, 0.0)])
            .close()
            .extrude(W + 2.0)
        )
        add(prof)

    if face_pattern == "grid":
        # Vertical grooves (run along Z), spaced across X.
        m = min(VT_MAX, max(1, int(W / (pitch * 2.0)) - 1))
        for j in range(1, m + 1):
            x = -W / 2.0 + j * (W / (m + 1))
            prof = (
                cq.Workplane("XY", origin=(x, T, -1.0))
                .polyline([(-half_w, 0.0), (half_w, 0.0), (0.0, -groove_depth)])
                .close()
                .extrude(H + 2.0)
            )
            add(prof)

    return cutter


def round_pocket(dia, depth, x_centre=0.0):
    """Half-round trough cut into the front face to cradle round stock (axis
    vertical, along Z). `depth` is how far into the jaw (−Y) the axis sits."""
    r = max(2.0, dia / 2.0)
    depth = max(1.0, min(depth, T - 3.0))
    return (
        cq.Workplane("XY", origin=(x_centre, T - depth, -1.0))
        .circle(r)
        .extrude(H + 2.0)
    )


def rect_pocket(w, h, depth, x_centre=0.0):
    """Rectangular pocket cut into the front face."""
    w = max(2.0, min(w, W - 4.0))
    h = max(2.0, min(h, H))
    depth = max(1.0, min(depth, T - 3.0))
    zc = H / 2.0
    return (
        cq.Workplane("XZ", origin=(x_centre, T + 0.5, zc))
        .rect(w, h)
        .extrude(-(depth + 0.5))
    )


def _apply_common(body):
    """Cut the always-present features: bolts, magnets, gripping face."""
    body = body.cut(bolt_cutter())
    mg = magnet_cutter()
    if mg is not None:
        body = body.cut(mg)
    fc = face_cutter()
    if fc is not None:
        body = body.cut(fc)
    return body


# ── jaw ──────────────────────────────────────────────────────────────────────
def build_jaw():
    body = jaw_blank()
    body = _apply_common(body)
    if workpiece == "round":
        body = body.cut(round_pocket(workpiece_dia, pocket_depth))
    elif workpiece == "rect":
        body = body.cut(rect_pocket(workpiece_w, workpiece_h, pocket_depth))
    return body


# ── jaw_pair ──────────────────────────────────────────────────────────────────
def build_jaw_pair():
    """Left + right jaws laid face-to-face with a display gap. The workpiece
    negative is split so each jaw carries the half that faces it — closing the
    vise brings the two halves together around the part."""
    # A single jaw with its half of the pocket (the pocket is centred on the face,
    # and each jaw only reaches `pocket_depth` in, so together they form the full
    # cavity when the faces meet).
    def one():
        b = jaw_blank()
        b = _apply_common(b)
        if workpiece == "round":
            b = b.cut(round_pocket(workpiece_dia, pocket_depth))
        elif workpiece == "rect":
            b = b.cut(rect_pocket(workpiece_w, workpiece_h, pocket_depth))
        return b

    jaw_a = one()
    jaw_b = one()

    # Right jaw: mirror across the XZ plane and push out along −Y so the two
    # gripping faces oppose each other across `pair_gap`.
    gap = max(2.0, pair_gap)
    jaw_a = jaw_a.translate((0.0, gap / 2.0, 0.0))
    jaw_b = (
        jaw_b.mirror(mirrorPlane="XZ")
        .translate((0.0, -gap / 2.0, 0.0))
    )
    return jaw_a.union(jaw_b)


# ── vee_jaw ───────────────────────────────────────────────────────────────────
def build_vee_jaw():
    """A jaw with a V-groove down the gripping face to cradle round stock. The
    groove axis runs vertically (Z); the notch opens toward the workpiece (+Y)."""
    body = jaw_blank()
    body = body.cut(bolt_cutter())
    mg = magnet_cutter()
    if mg is not None:
        body = body.cut(mg)

    half = math.radians(max(20.0, min(vee_angle, 150.0)) / 2.0)
    depth = min(max(T * 0.5, 6.0), T - 3.0)
    half_w = depth * math.tan(half)
    half_w = min(half_w, W / 2.0 - 2.0)

    # Triangular cutter in the (X,Y) plane, extruded up Z. Mouth at the face
    # (y=T), apex driven inward to y = T − depth.
    cutter = (
        cq.Workplane("XY", origin=(0.0, 0.0, -1.0))
        .polyline([(-half_w, T + 0.5), (half_w, T + 0.5), (0.0, T - depth)])
        .close()
        .extrude(H + 2.0)
    )
    body = body.cut(cutter)
    # No post-cut chamfer here: the mouth-of-V edges are fragile and chamfering
    # them can crash the OCCT kernel. The lead-in chamfer already lives on the
    # clean blank (jaw_blank).
    return body


# ── Dispatch ─────────────────────────────────────────────────────────────────
_dispatch = {
    "jaw":      build_jaw,
    "jaw_pair": build_jaw_pair,
    "vee_jaw":  build_vee_jaw,
}

result = _dispatch.get(target_part, build_jaw)()
