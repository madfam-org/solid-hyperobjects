"""Jeans Tack Button — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

The no-sew tack button of jeans and workwear — the rigid hard good the Fashion Cabinet
`jeans-button` notion places and bridges to here for its geometry. A domed button head on
a hollow socket that the tack (a separate nail) rivets into through the waistband. Printed
rigid it stands in for the metal jeans button.

Modes (dispatched via `target_part`):
  * "set"    — button head + tack side by side.
  * "button" — the head + socket only.
  * "tack"   — the nail that sets it.

Geometry: the head is a chamfered cylinder; the socket a bored cylinder under it; the tack
a small cylinder with a flat head. Small boolean count → fast, watertight.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `head_dia`).
  - Access them via PARAM(lambda: <name>, <default>). Do NOT use globals()/eval/getattr.
  - Assign the final solid to a top-level name `result`.
"""

import cadquery as cq


def PARAM(getter, default):
    """Return an injected global if present, else the default."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
head_dia  = float(PARAM(lambda: head_dia,  17.0))    # button head diameter (mm)
head_h    = float(PARAM(lambda: head_h,    5.0))     # head height (mm)
socket_dia = float(PARAM(lambda: socket_dia, 9.0))   # socket (under-head) diameter (mm)
socket_h  = float(PARAM(lambda: socket_h,  4.0))     # socket height (mm)
tack_dia  = float(PARAM(lambda: tack_dia,  4.0))     # tack (nail) shank diameter (mm)
tack_h    = float(PARAM(lambda: tack_h,    10.0))    # tack length (mm)

target_part = str(PARAM(lambda: target_part, "set"))  # set|button|tack

# ── Safe clamps ──────────────────────────────────────────────────────────────
head_dia   = max(10.0, min(head_dia, 28.0))
head_h     = max(2.0, min(head_h, 10.0))
socket_dia = max(5.0, min(socket_dia, head_dia - 3.0))
socket_h   = max(2.0, min(socket_h, 10.0))
tack_dia   = max(2.0, min(tack_dia, socket_dia - 1.0))
tack_h     = max(4.0, min(tack_h, 20.0))


# Every feature is placed ONCE: its workplane sits on the face it grows from and
# the extrude runs from that plane. `.transformed(offset=z)` followed by
# `.extrude(h)` spans [z, z+h], so writing the mid-height into the offset (the
# old idiom here) started the head above the socket and the shank above the tack
# head -- neither fused. Mating features overlap by WELD (>= 0.01 mm) because
# coincident faces do not fuse reliably in OCCT.
WELD = 0.2


def build_button():
    """Domed head over a bored socket. Socket z:[0, socket_h], head above it."""
    socket = (
        cq.Workplane("XY")
        .circle(socket_dia / 2.0)
        .extrude(socket_h)
    )
    head = (
        cq.Workplane("XY")
        .workplane(offset=socket_h - WELD)
        .circle(head_dia / 2.0)
        .extrude(head_h + WELD)
    )
    try:
        head = head.edges(">Z").fillet(min(head_h, head_dia * 0.15) * 0.9)
    except Exception:
        pass
    # Blind bore for the tack shank: starts 1 mm below the socket base (so the
    # cut breaks the bottom face cleanly) and reaches the same depth into the
    # head as before -- socket_h + head_h - 1 above z=0, never through the dome.
    bore = (
        cq.Workplane("XY")
        .workplane(offset=-1.0)
        .circle((tack_dia + 0.4) / 2.0)
        .extrude(socket_h + head_h)
    )
    return socket.union(head).cut(bore)


def build_tack():
    """The nail: a flat head z:[0, flat_h] + a shank rising from inside it."""
    flat_h = 1.4
    head = (
        cq.Workplane("XY")
        .circle(tack_dia * 0.9)
        .extrude(flat_h)
    )
    shank = (
        cq.Workplane("XY")
        .workplane(offset=flat_h - WELD)
        .circle(tack_dia / 2.0)
        .extrude(tack_h + WELD)
    )
    return head.union(shank)


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "button":
    result = build_button()
elif target_part == "tack":
    result = build_tack()
else:
    result = build_button().union(build_tack().translate((head_dia, 0, 0)))
