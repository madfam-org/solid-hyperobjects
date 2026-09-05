"""
Bench Dog / Hold-Down — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

Workholding that drops into a workbench dog hole. A round shank sized to the
hole (19 mm, 20 mm or 3/4 in) registers the tool; a head above the bench pushes,
pins or clamps the workpiece.

Three modes, dispatched by `target_part`:
  - round_dog     : a round-shank dog with a low stop head that a workpiece
                    presses against (pairs with a vise dog to trap stock).
  - holdfast      : a cam / hook hold-down whose offset arm levers down onto the
                    work when the shank is knocked or cammed in the hole.
  - planing_stop  : a wide-headed stop that fills a dog hole and gives a broad
                    end-stop for hand planing.

The `hole` select maps to the shank diameter:
  19mm -> 19.0, 20mm -> 20.0, 3/4in -> 19.05 mm.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `hole`).
  - Access them via PARAM(lambda: <name>, <default>). Do NOT use globals()/eval/
    getattr — they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.
"""

import cadquery as cq


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
hole        = str(  PARAM(lambda: hole,     "19mm"))   # dog-hole standard (select)
fit         = float(PARAM(lambda: fit,        0.3))    # per-side clearance shank↔hole
shank_len   = float(PARAM(lambda: shank_len, 40.0))    # shank length below the bench
head_h      = float(PARAM(lambda: head_h,    16.0))    # head height above the bench
head_w      = float(PARAM(lambda: head_w,    30.0))    # head footprint / face width
reach       = float(PARAM(lambda: reach,     55.0))    # holdfast arm reach (offset)
face_h      = float(PARAM(lambda: face_h,    24.0))    # stop face height (planing stop)

target_part = str(PARAM(lambda: target_part, "round_dog"))

# Map the hole standard to a nominal bore, then subtract clearance per side.
_HOLE = {"19mm": 19.0, "20mm": 20.0, "3/4in": 19.05}
bore = _HOLE.get(hole, 19.0)
shank_dia = max(3.0, bore - 2.0 * max(0.0, fit))
shank_r = shank_dia / 2.0


# ── Helpers ──────────────────────────────────────────────────────────────────
def shank(length):
    """Vertical round shank, top at z=0, extending downward by `length`.
    A short taper lead-in at the bottom eases entry."""
    body = (
        cq.Workplane("XY")
        .circle(shank_r)
        .extrude(-length)
    )
    try:
        body = body.edges("<Z").chamfer(min(shank_r * 0.4, 1.5))
    except Exception:
        pass
    return body


def block(w, d, h, cx=True, cy=True):
    return cq.Workplane("XY").box(w, d, h, centered=(cx, cy, False))


def safe_fillet(solid, sel, r):
    if r <= 0.3:
        return solid
    try:
        return solid.edges(sel).fillet(r)
    except Exception:
        return solid


# ── Round dog (shank + low stop head) ────────────────────────────────────────
def build_round_dog():
    """Round shank plus a modest head. The head has a flat push face and a small
    collar so it can't fall through the hole."""
    body = shank(shank_len)
    collar = cq.Workplane("XY").circle(bore / 2.0 + 2.5).extrude(3.0)
    head = block(head_w, head_w, head_h).translate((0, 0, 3.0))
    body = body.union(collar).union(head)
    body = safe_fillet(body, "|Z", min(head_w * 0.12, 3.0))
    return body


# ── Holdfast (cam hold-down with offset arm) ─────────────────────────────────
def build_holdfast():
    """A shank with an arm that reaches out and a pad that presses down on the
    work. Camming the shank in the hole levers the pad onto the workpiece."""
    body = shank(shank_len)
    # Neck rising just above the bench.
    neck = cq.Workplane("XY").circle(shank_r + 3.0).extrude(head_h)
    body = body.union(neck)
    # Horizontal arm reaching in +X at the top of the neck.
    arm_h = max(10.0, shank_dia * 0.9)
    # A SECOND `arm.translate((0, 0, head_h - arm_h))` used to follow the one
    # below, commented "Raise arm to top of neck" -- the same move applied
    # twice. It lifted the arm to z in [18.90, 36.00], clear of both the neck
    # and the pad, so the pad came off as a second, floating body (sweep:
    # 2 bodies at defaults and at preset:printed_holdfast).
    #
    # The arm also has to stay ON the bench. head_h (16.0) is smaller than
    # arm_h (max(10, shank_dia*0.9) = 16.56 at the default 19 mm hole), so
    # hanging the arm from the neck top put its underside at z = -0.56, down
    # inside the shank's zone -- where the arm's start face at x = shank_r is
    # exactly TANGENT to the shank cylinder of the same radius. That tangent
    # plane/cylinder contact is what cracked the union (not watertight, and no
    # exception raised). Seat the arm on the bench top instead: its underside
    # is z = 0 and it rises arm_h, overlapping the neck for min(arm_h, head_h).
    arm = block(reach, arm_h, arm_h, cx=False, cy=True).translate(
        (shank_r, 0, 0.0)
    )
    body = body.union(arm)
    # Down-pad at the arm tip that contacts the work. It must OVERLAP the arm,
    # not abut it: placed at x = reach + shank_r - head_w/2 the pad's far face
    # landed at exactly x = shank_r + reach, the arm's own far face, and that
    # coincident face is what cracked the union open (holdfast rendered 1 body,
    # not watertight, once the arm was back down on the neck). Pull the pad
    # inboard by _PAD_BITE so the two solids share volume instead of a plane,
    # and hang it BELOW the arm rather than straddling it -- the pad presses
    # down on the work, so its top belongs inside the arm and its bottom below.
    _PAD_BITE = 2.0
    pad_h = arm_h * 0.9
    pad_top = _PAD_BITE                       # bites up into the arm from z=0
    pad = block(head_w, arm_h + 6.0, pad_h).translate(
        (reach + shank_r - head_w / 2.0 - _PAD_BITE, 0, pad_top - pad_h)
    )
    body = body.union(pad)
    return body.clean()


# ── Planing stop (wide-headed end stop) ──────────────────────────────────────
def build_planing_stop():
    """Fills a dog hole with a shank and presents a broad, tall face that stops
    stock for hand planing. The face is wider than the hole for a big bearing
    surface, backed by a solid buttress block so it can't fold."""
    body = shank(shank_len)
    # Broad base plate that sits on the bench top.
    base = block(head_w * 1.4, head_w, 6.0)
    body = body.union(base)
    # Tall stop face rising from the front (−Y) edge of the base — the plane
    # pushes stock into this face.
    face_t = 8.0
    face = block(head_w * 1.4, face_t, face_h).translate((0, -head_w / 2.0 + face_t / 2.0, 6.0))
    body = body.union(face)
    # Solid buttress behind the face: a stepped stack tapering back over the
    # base so the face is braced.
    #
    # `block()` is Y-CENTRED, so translating each step to y = -head_w/2 + face_t
    # (as this did) put its MIDPOINT on the face's back plane: the two deepest
    # steps then reached y = -21.50 and -24.75, out past the front of both the
    # base and the stop face (y = -20) into mid-air, and every step shared that
    # same y plane with the others. The stack was four coplanar-faced solids,
    # which is what the blanket "|X" fillet below then chained across into a
    # non-manifold shape (hand_plane_stop: not watertight, sweep vol 44835.65).
    #
    # Anchor each step on the face's BACK plane instead and grow it backwards
    # (+Y) over the base, overlapping into the face by `_BRACE_BITE` so each
    # union has real volume to fuse rather than a coincident face.
    steps = 4
    _BRACE_BITE = 1.0
    y_back = -head_w / 2.0 + face_t          # the stop face's back plane
    max_depth = head_w / 2.0 - y_back        # room left on the base behind it
    for i in range(steps):
        frac = 1.0 - i / float(steps)
        h = 6.0 + face_h * frac
        d = _BRACE_BITE + max_depth * (1.0 - i / float(steps))
        brace = block(head_w * 0.6, d, h, cy=False).translate(
            (0, y_back - _BRACE_BITE, 0.0)
        )
        body = body.union(brace)
    # Soften the buttress's own vertical step edges only. A blanket "|X" fillet
    # over the whole assembly reaches the coincident seams the unions leave and
    # returns a bad shape without raising, which safe_fillet cannot detect.
    return body.clean()


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "holdfast":
    result = build_holdfast()
elif target_part == "planing_stop":
    result = build_planing_stop()
else:
    result = build_round_dog()
