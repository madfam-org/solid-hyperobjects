"""
FPV Antenna Mount — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

Holds a VTX (video transmitter) antenna clear of the propellers and routes it up
or back. Sized to the antenna connector standard (SMA bulkhead or the tiny U.FL
coax). Three modes: a tube mount that captures a rigid tube antenna, an SMA
bulkhead bracket, and a lightweight frame clip.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `connector`).
  - Access them via PARAM(lambda: <name>, <default>). Do NOT use
    globals()/eval/getattr — they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.
"""

import cadquery as cq
import math


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Connector exit table (nominal through-hole diameter, mm) ─────────────────
# SMA bulkhead threads are ~6.35 mm across flats; a clean 6.5 mm hole clears the
# barrel. U.FL is a tiny 2 mm coax push-fit — the hole just routes the thin cable.
CONNECTOR_EXIT = {"SMA": 6.5, "U.FL": 2.6}


def connector_exit_d(kind):
    """Return the antenna-exit hole diameter for the connector standard."""
    return CONNECTOR_EXIT.get(kind, 6.5)


# ── Parameters ───────────────────────────────────────────────────────────────
connector   = str(  PARAM(lambda: connector, "SMA"))    # SMA | U.FL
stalk_h     = float(PARAM(lambda: stalk_h,     35.0))   # stalk height (lifts antenna above props)
stalk_d     = float(PARAM(lambda: stalk_d,      8.0))   # stalk outer diameter
back_angle  = float(PARAM(lambda: back_angle,  25.0))   # rearward lean of the stalk (deg)
base_w      = float(PARAM(lambda: base_w,      18.0))   # foot base width (X)
base_l      = float(PARAM(lambda: base_l,      18.0))   # foot base length (Y)
base_h      = float(PARAM(lambda: base_h,       3.0))   # foot base thickness
bolt_d      = float(PARAM(lambda: bolt_d,       2.2))   # base bolt hole (M2 default)
bolt_span   = float(PARAM(lambda: bolt_span,   12.0))   # base bolt hole spacing
tube_d      = float(PARAM(lambda: tube_d,       4.0))   # rigid tube-antenna diameter (tube mode)
tube_len    = float(PARAM(lambda: tube_len,    28.0))   # tube capture length (tube mode)
clip_gap    = float(PARAM(lambda: clip_gap,     4.0))   # frame-plate thickness the clip grips (clip mode)
jack_body_d = float(PARAM(lambda: jack_body_d,  9.5))   # SMA bracket: clearance bore for a rear-mounted jack

target_part = str(PARAM(lambda: target_part, "tube_mount"))
# "tube_mount" | "sma_bracket" | "clip"


# ── Derived / clamped geometry ───────────────────────────────────────────────
exit_d = connector_exit_d(connector)
exit_r = max(0.8, exit_d / 2.0)
stalk_r = max(exit_r + 1.6, stalk_d / 2.0)
back_angle = max(0.0, min(back_angle, 45.0))
bolt_r = max(0.6, bolt_d / 2.0)

# ── SMA bracket: a REAR-mounted pigtail jack (owner decision O2(a)) ──────────
# The jack comes up from below: its rear body and hex travel the whole stalk and
# its shoulder bears on the cap's UNDERSIDE, its thread through the cap's exit
# hole. So below the cap the bore is a full-length clearance bore of `jack_body_d`
# (never less than 1 mm over the exit hole), open through the foot; the exit
# hole stays only through the cap. The stalk keeps a 1.6 mm wall round that bore,
# and the foot's two bolt holes move ACROSS the lean (along X), outside the stalk
# by a screw head's room: along Y the leaned stalk passes over the +Y bolt.
SMA_HEAD_ROOM = 2.0
SMA_WALL = 1.6
_bore_req_r = max(jack_body_d, exit_d + 1.0) / 2.0
_bore_min_r = exit_r + 0.5                 # the shoulder still needs a 0.5 mm annulus
# A requested span that can hold the stalk round the smallest bore is KEPT, and the
# jack bore is capped to fit inside it: a foot on a fixed pattern (bolt_span 20 on the
# frame's 20 x 20 VTX seat) never moves its holes, whatever jack_body_d asks for. A span
# too small for even that is widened as before (the 12 mm default -> 18.9 mm).
if max(stalk_r, _bore_min_r + SMA_WALL) + bolt_r + SMA_HEAD_ROOM <= bolt_span / 2.0 + 1e-9:
    sma_bore_r = min(_bore_req_r, bolt_span / 2.0 - bolt_r - SMA_HEAD_ROOM - SMA_WALL)
else:
    sma_bore_r = _bore_req_r
sma_stalk_r = max(stalk_r, sma_bore_r + SMA_WALL)
sma_bolt_span = max(bolt_span, 2.0 * (sma_stalk_r + bolt_r + SMA_HEAD_ROOM))
sma_base_w = max(base_w, sma_bolt_span + 2.0 * (bolt_r + 2.0))
sma_base_l = max(base_l, 2.0 * sma_stalk_r / math.cos(math.radians(back_angle)) + 3.0)


def _foot():
    """A flat base foot with two bolt holes to fix the mount to the frame.
    Top at z=0, extends down to z=-base_h."""
    foot = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, -base_h / 2.0))
        .box(base_w, base_l, base_h, centered=(True, True, True))
    )
    try:
        foot = foot.edges("|Z").fillet(min(2.0, base_w / 2.0 - 0.5, base_l / 2.0 - 0.5))
    except Exception:
        pass
    for sy in (-1.0, 1.0):
        hole = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, sy * bolt_span / 2.0, -base_h / 2.0))
            .circle(bolt_r)
            .extrude(base_h * 2.0, both=True)
        )
        foot = foot.cut(hole)
    return foot


def _lean(solid):
    """Lean a solid rearward by `back_angle` about the X axis (a no-op at 0)."""
    if back_angle > 0.1:
        return solid.rotate((0, 0, 0), (1, 0, 0), -back_angle)
    return solid


def _stalk(height, outer_r, bore_r, lean=True):
    """An upright cylindrical stalk with an axial bore for the coax, growing from
    z=0 up to `height`. Leaned back by `back_angle` unless `lean=False` (so a
    caller can add a top feature first, then lean the whole assembly together)."""
    stalk = (
        cq.Workplane("XY")
        .circle(outer_r)
        .extrude(height)
    )
    if bore_r > 0.4:
        bore = cq.Workplane("XY").circle(bore_r).extrude(height + 2.0).translate((0, 0, -1.0))
        stalk = stalk.cut(bore)
    if lean:
        stalk = _lean(stalk)
    return stalk


def build_tube_mount():
    """Foot + stalk that captures a rigid tube antenna: the stalk top opens into
    a deeper socket sized to `tube_d` so a stiff tube/pagoda antenna seats in it."""
    foot = _foot()
    # Build the stalk upright, cut the tube socket, THEN lean the whole thing so
    # the bore and socket stay coaxial with the leaned stalk.
    stalk = _stalk(stalk_h, stalk_r, exit_r, lean=False)
    socket_r = max(exit_r + 0.3, tube_d / 2.0 + 0.3)
    socket = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, stalk_h - tube_len / 2.0))
        .circle(socket_r)
        .extrude(tube_len / 2.0 + 1.0, both=True)
    )
    stalk = _lean(stalk.cut(socket))
    return foot.union(stalk)


def build_sma_bracket():
    """Foot + a stalk ending in a flat bulkhead cap for a REAR-mounted SMA pigtail
    jack: the jack's body comes up the stalk's clearance bore (open through the
    foot), its shoulder seats on the cap's underside, its thread passes the cap's
    exit hole, and the nut and antenna go on top."""
    foot = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, -base_h / 2.0))
        .box(sma_base_w, sma_base_l, base_h, centered=(True, True, True))
    )
    try:
        foot = foot.edges("|Z").fillet(min(2.0, sma_base_w / 2.0 - 0.5, sma_base_l / 2.0 - 0.5))
    except Exception:
        pass
    for sx in (-1.0, 1.0):
        hole = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(sx * sma_bolt_span / 2.0, 0, -base_h / 2.0))
            .circle(bolt_r)
            .extrude(base_h * 2.0, both=True)
        )
        foot = foot.cut(hole)
    # Stalk + cap built upright, then leaned together so the cap stays square to it.
    stalk = cq.Workplane("XY").circle(sma_stalk_r).extrude(stalk_h)
    cap_t = max(2.0, base_h)
    cap = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, stalk_h + cap_t / 2.0))
        .box(sma_stalk_r * 2.6, sma_stalk_r * 2.6, cap_t, centered=(True, True, True))
    )
    try:
        cap = cap.edges("|Z").fillet(min(2.0, sma_stalk_r - 0.4))
    except Exception:
        pass
    exit_hole = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, stalk_h + cap_t / 2.0))
        .circle(exit_r)
        .extrude(cap_t, both=True)
    )
    top = _lean(stalk.union(cap).cut(exit_hole))
    # The clearance bore: from below the foot up to the cap's underside, leaned
    # with the stalk, cut from foot and stalk together.
    bore = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, -base_h * 3.0))
        .circle(sma_bore_r)
        .extrude(stalk_h + base_h * 3.0)
    )
    return foot.union(top).cut(_lean(bore))


def build_clip():
    """A lightweight C-clip that snaps onto a frame plate (thickness `clip_gap`)
    and carries a short stalk to route the antenna — no bolts needed."""
    # C-clip: an outer block with a slot cut for the plate and a mouth opening.
    wall = 2.2
    clip_w = base_w
    clip_h = clip_gap + 2.0 * wall
    clip_depth = 12.0
    body = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, clip_h / 2.0))
        .box(clip_w, clip_depth, clip_h, centered=(True, True, True))
    )
    # Plate slot (open toward -Y, the mouth).
    slot = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, -1.0, clip_h / 2.0))
        .box(clip_w + 2.0, clip_depth, clip_gap, centered=(True, True, True))
    )
    body = body.cut(slot)
    # Short upright stalk on top routing the coax up (kept vertical so it clears
    # the clip mouth predictably).
    stalk = _stalk(max(12.0, stalk_h * 0.5), stalk_r, exit_r, lean=False).translate((0, 0, clip_h))
    return body.union(stalk)


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "sma_bracket":
    result = build_sma_bracket()
elif target_part == "clip":
    result = build_clip()
else:  # "tube_mount"
    result = build_tube_mount()
