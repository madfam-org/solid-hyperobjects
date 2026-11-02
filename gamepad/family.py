"""
Gamepad — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

The archetype: one parametric two-handed controller. A planar outline — a
rounded-rectangle bridge plus 0, 2 or 3 tapered grips — stands on a flat bottom
and is crowned by ONE analytic function z(x, y) that the body and every control
seat share, so the controls sit on the surface whatever the body plan. Five
written body plans (`outline`) span the brick, the crescent, the dogbone, handles
and the trident; `split` cuts the same body into two halves on Joy-Con-type rails
or on magnets, each half its own body, and `split_gap` pulls them apart.

COMPOSITION — a controller is a hyperobject of hyperobjects
-----------------------------------------------------------
Each component is a function in commons-lib/hardware/ taking its OWN parameter
dict; only the assembly functions below map this manifest's parameters onto them.

    component            module         CDG interface it exposes / consumes
    ------------------   ------------   --------------------------------------
    pad_body             pad_body       exposes device_envelope, grip_envelope
    pad_grip             pad_body       exposes grip_envelope (one grip)
    pad_rail             pad_body       exposes rail (Joy-Con type)
    pad_magnet_pockets   pad_body       exposes magnetic_seat
    deck_shell           structure      the bridge prism (reused as is)
    d_pad                controls       exposes dpad_seat (cross)
    face_button          controls       exposes button_seat (ring: diamond, circle pad)
    button_row           controls       exposes button_seat (system buttons)
    analog_stick         controls       exposes stick_seat (round gate)
    shoulder_trigger     controls       exposes trigger_seat (bumper, trigger notches)
    port_receptacle      connectors     exposes port_cutout (jack, charge port,
                                        touchpad, light bar, expansion slots)
    pad_face_layout      pad_controls   button_seat positions (row, diagonal,
                                        diamond, arc_2x3, big_a)
    pad_round_seats      pad_controls   exposes button_seat (per-button crown floor)
    pad_octagon_seat     pad_controls   exposes stick_seat (octagonal gate)
    pad_stick            pad_controls   the stick itself (shaft + cap, tilted)
    pad_trigger_blade    pad_controls   consumes trigger_seat
    pad_grille           pad_controls   a vented face; no upstream id
    pad_door_seam        pad_controls   exposes battery_bay (door outline)

TWO FILES. This file, `family.py`, is the authored half. `main.py` is generated
from it by `tools/inline_parts.py` (ruling R2 on gate H8). Edit this file or a
module, never main.py, then run `python3 tools/inline_parts.py --write gamepad`.

This is a FAMILY, not a product (NOTICE). Every default is the archetype's own,
written by tools/presets/gamepad.py; named presets would carry published
envelopes only. No logos, no glyphs, no fitted curves (ruling R3).

Frame (stated again in docs/README.md):

    X  across the hands. The pad is symmetric about x = 0, the split line.
    Y  front edge (toward the player, -Y) to the shoulders (+Y). The bridge is
       centred on the origin; grips run toward -Y.
    Z  thickness. The grips stand on z = 0; the bridge's underside is lifted by
       grip_drop; the top of the crown is z = thickness.

Parts (dispatched on `target_part`):
  - body         the controller body with every seat cut (two bodies when split)
  - controls     every cap: D-pad, face and system buttons, sticks, bumpers,
                 triggers, the under-trigger (each its own body)
  - envelope     the uncut body: the fit surface (1 body)
  - top_shell    the body above the seam, hollowed by shell_wall (1 body)
  - bottom_shell the body below the seam, hollowed by shell_wall (1 body)
  - left_half    the half at x < 0, with its rail or magnets when split (1 body)
  - right_half   the half at x > 0 (1 body)

Sandbox contract (apps/api/services/engine/cq_runner.py): `cq` and `math` are
injected; parameters arrive as bare globals read through PARAM; the solid is
assigned to `result`.
"""

import math  # noqa: F401 — injected by the sandbox; imported so the file runs standalone

import cadquery as cq  # noqa: F401 — the inlined components below use it


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
# Every default below is the archetype's own (tools/presets/gamepad.py, derive()
# of ARCHETYPE_BASE): a generic two-stick controller with handles, no product.
outline = str(PARAM(lambda: outline, "handles"))
thickness = float(PARAM(lambda: thickness, 40.0))
bridge_width = float(PARAM(lambda: bridge_width, 115.44))
bridge_depth = float(PARAM(lambda: bridge_depth, 58.24))
bridge_corner_radius = float(PARAM(lambda: bridge_corner_radius, 10.4832))
grip_count = int(PARAM(lambda: grip_count, 2))
grip_root_x = float(PARAM(lambda: grip_root_x, 40.248))
grip_root_y = float(PARAM(lambda: grip_root_y, -11.648))
grip_length = float(PARAM(lambda: grip_length, 52.5311))
grip_splay_deg = float(PARAM(lambda: grip_splay_deg, 24.9415))
grip_drop = float(PARAM(lambda: grip_drop, 12.0))
grip_root_radius = float(PARAM(lambda: grip_root_radius, 17.472))
grip_tip_radius = float(PARAM(lambda: grip_tip_radius, 15.6))
center_grip_offset = float(PARAM(lambda: center_grip_offset, 0.0))
top_crown = float(PARAM(lambda: top_crown, 4.8))
bottom_crown = float(PARAM(lambda: bottom_crown, 3.2))
crown_span_x = float(PARAM(lambda: crown_span_x, 78.0))
crown_span_y = float(PARAM(lambda: crown_span_y, 74.88))
crown_center_y = float(PARAM(lambda: crown_center_y, 0.0))
seam_ratio = float(PARAM(lambda: seam_ratio, 0.5))
shell_wall = float(PARAM(lambda: shell_wall, 2.0))
control_recess_depth = float(PARAM(lambda: control_recess_depth, 1.2))
control_clearance = float(PARAM(lambda: control_clearance, 0.3))
dpad_kind = str(PARAM(lambda: dpad_kind, "cross"))
dpad_x = float(PARAM(lambda: dpad_x, -40.56))
dpad_y = float(PARAM(lambda: dpad_y, 5.824))
dpad_size = float(PARAM(lambda: dpad_size, 22.9632))
dpad_arm_width = float(PARAM(lambda: dpad_arm_width, 7.8075))
dpad_height = float(PARAM(lambda: dpad_height, 2.0))
face_count = int(PARAM(lambda: face_count, 4))
face_arrangement = str(PARAM(lambda: face_arrangement, "diamond"))
face_x = float(PARAM(lambda: face_x, 40.56))
face_y = float(PARAM(lambda: face_y, 5.824))
face_radius = float(PARAM(lambda: face_radius, 4.992))
face_spacing = float(PARAM(lambda: face_spacing, 10.4832))
face_tilt_deg = float(PARAM(lambda: face_tilt_deg, 0.0))
face_height = float(PARAM(lambda: face_height, 2.0))
stick_count = int(PARAM(lambda: stick_count, 2))
stick_layout = str(PARAM(lambda: stick_layout, "symmetric"))
stick_left_x = float(PARAM(lambda: stick_left_x, -22.308))
stick_left_y = float(PARAM(lambda: stick_left_y, -15.1424))
stick_right_x = float(PARAM(lambda: stick_right_x, 22.308))
stick_right_y = float(PARAM(lambda: stick_right_y, -15.1424))
stick_cap = str(PARAM(lambda: stick_cap, "concave"))
stick_radius = float(PARAM(lambda: stick_radius, 10.14))
stick_height = float(PARAM(lambda: stick_height, 10.14))
stick_gate = str(PARAM(lambda: stick_gate, "round"))
stick_gate_radius = float(PARAM(lambda: stick_gate_radius, 8.619))
stick_tilt_deg = float(PARAM(lambda: stick_tilt_deg, 0.0))
bumper_count = int(PARAM(lambda: bumper_count, 2))
bumper_x = float(PARAM(lambda: bumper_x, 40.56))
bumper_width = float(PARAM(lambda: bumper_width, 23.088))
bumper_height = float(PARAM(lambda: bumper_height, 4.48))
bumper_depth = float(PARAM(lambda: bumper_depth, 8.1536))
trigger_count = int(PARAM(lambda: trigger_count, 2))
trigger_x = float(PARAM(lambda: trigger_x, 40.56))
trigger_width = float(PARAM(lambda: trigger_width, 18.4704))
trigger_length = float(PARAM(lambda: trigger_length, 10.08))
trigger_depth = float(PARAM(lambda: trigger_depth, 12.8128))
trigger_travel_deg = float(PARAM(lambda: trigger_travel_deg, 0.0))
under_trigger = bool(PARAM(lambda: under_trigger, False))
under_trigger_y = float(PARAM(lambda: under_trigger_y, -15.1424))
system_button_count = int(PARAM(lambda: system_button_count, 2))
system_y = float(PARAM(lambda: system_y, 8.736))
system_pitch = float(PARAM(lambda: system_pitch, 50.1744))
system_radius = float(PARAM(lambda: system_radius, 2.808))
touchpad_present = bool(PARAM(lambda: touchpad_present, True))
touchpad_width = float(PARAM(lambda: touchpad_width, 41.5584))
touchpad_height = float(PARAM(lambda: touchpad_height, 24.4608))
touchpad_y = float(PARAM(lambda: touchpad_y, 8.736))
light_bar_present = bool(PARAM(lambda: light_bar_present, True))
light_bar_width = float(PARAM(lambda: light_bar_width, 34.632))
speaker_present = bool(PARAM(lambda: speaker_present, True))
speaker_y = float(PARAM(lambda: speaker_y, -6.9944))
headset_jack = bool(PARAM(lambda: headset_jack, True))
cable_exit = str(PARAM(lambda: cable_exit, "none"))
charge_port = bool(PARAM(lambda: charge_port, True))
expansion_slot_count = int(PARAM(lambda: expansion_slot_count, 0))
expansion_slot_face = str(PARAM(lambda: expansion_slot_face, "top"))
expansion_slot_y = float(PARAM(lambda: expansion_slot_y, 18.6368))
expansion_slot_pitch = float(PARAM(lambda: expansion_slot_pitch, 34.632))
expansion_slot_width = float(PARAM(lambda: expansion_slot_width, 18.4704))
expansion_slot_thickness = float(PARAM(lambda: expansion_slot_thickness, 4.0768))
expansion_slot_depth = float(PARAM(lambda: expansion_slot_depth, 12.6))
battery_door = bool(PARAM(lambda: battery_door, False))
battery_door_width = float(PARAM(lambda: battery_door_width, 41.5584))
battery_door_length = float(PARAM(lambda: battery_door_length, 29.12))
battery_door_y = float(PARAM(lambda: battery_door_y, -2.912))
split = str(PARAM(lambda: split, "none"))
split_gap = float(PARAM(lambda: split_gap, 0.0))
rail_length = float(PARAM(lambda: rail_length, 81.12))
rail_width = float(PARAM(lambda: rail_width, 12.0))

target_part = str(PARAM(lambda: target_part, "body"))

# Archetype constants of the assembly (ours; docs/README.md "Archetype rules").
SPLIT_CLEARANCE = 0.4        # between two halves at split_gap 0 (the rail's running fit)
STICK_WELL = 2.5             # stick seat depth, in control recesses
TRIGGER_OPEN_DEG = 20.0      # a trigger at rest; trigger_travel_deg pulls it in
SYSTEM_HEIGHT = 1.0          # system buttons stand lower than face buttons
LIGHT_BAR_GAP, LIGHT_BAR_SLOT = 2.5, 1.6
GRILLE = {"rows": 2, "cols": 4, "pitch": 2.6, "hole_radius": 0.7}
JACK_RADIUS, JACK_DEPTH = 1.75, 12.0      # 3.5 mm nominal: the catalog's `headphone_3_5`
CHARGE_WIDTH, CHARGE_HEIGHT, CHARGE_DEPTH = 9.0, 3.2, 8.0
CABLE_RADIUS, CABLE_LENGTH = 4.0, 10.0
DOOR_GROOVE = 0.8
UNDER_TRIGGER_DEPTH, UNDER_TRIGGER_HANG = 10.0, 3.0


# inline-parts: controls connectors pad_body pad_controls


# ═════════════════════════════════════════════════════════════════════════════
# ASSEMBLY — the only code that maps this manifest's parameters onto component
# dicts. Everything above is portable; everything below is this cartridge.
# ═════════════════════════════════════════════════════════════════════════════

def _plan(inset):
    return {
        "thickness": thickness, "floor": _floor(), "top_crown": top_crown,
        "bottom_crown": bottom_crown, "span_x": crown_span_x, "span_y": crown_span_y,
        "center_y": crown_center_y, "outline": outline, "bridge_width": bridge_width,
        "bridge_depth": bridge_depth, "bridge_corner_radius": bridge_corner_radius,
        "grip_count": grip_count, "grip_root_x": grip_root_x, "grip_root_y": grip_root_y,
        "grip_length": grip_length, "grip_splay_deg": grip_splay_deg,
        "grip_root_radius": grip_root_radius, "grip_tip_radius": grip_tip_radius,
        "center_grip_offset": center_grip_offset, "inset": inset,
    }


def _floor():
    """The bridge's underside: lifted by the grip drop only when grips carry the pad."""
    return grip_drop if (outline != "brick" and grip_count > 0) else 0.0


def _crown():
    return {"thickness": thickness, "floor": _floor(), "top_crown": top_crown,
            "bottom_crown": bottom_crown, "span_x": crown_span_x, "span_y": crown_span_y,
            "center_y": crown_center_y}


Z_OUT = thickness + 1.0                                  # every top cutter's overshoot
Y_OUT = crown_center_y + crown_span_y + 1.0             # beyond the shoulders
Y_FRONT_OUT = crown_center_y - crown_span_y - 1.0       # beyond the front edge
Y_EDGE = bridge_depth / 2.0                              # the shoulder edge


def _top(x, y):
    return pad_crown_top(_crown(), x, y)


def _bottom(x, y):
    return pad_crown_bottom(_crown(), x, y)


def _mid(x, y):
    return (_top(x, y) + _bottom(x, y)) / 2.0


def _rect(width, depth, z_lo, z_hi, x, y):
    """A box cutter through port_receptacle (`port_cutout`), from z_lo to z_hi."""
    return port_receptacle({"shape": "rect", "width": width, "height": z_hi - z_lo,
                            "depth": depth, "radius": 0.0, "center_x": x, "center_y": y,
                            "center_z": (z_lo + z_hi) / 2.0})


def _floor_under(buttons):
    return min(_top(x, y) for x, y, _ in buttons) - control_recess_depth


def _caps(buttons, floor_z, height):
    return pad_round_caps({"crown": _crown(), "buttons": buttons, "floor_z": floor_z,
                           "recess": control_recess_depth, "clearance": control_clearance,
                           "height": height})


def _dpad():
    if dpad_kind == "none":
        return [], []
    half = dpad_size / 2.0
    if dpad_kind == "disc":
        btn = [(dpad_x, dpad_y, half)]
        return ([pad_round_seats({"crown": _crown(), "buttons": btn,
                                  "recess": control_recess_depth})],
                _caps(btn, None, dpad_height))
    if dpad_kind == "circle":   # four round buttons on a ring: face_button's ring
        r = dpad_arm_width / 2.0
        btns = [(dpad_x + (half - r) * math.cos(math.radians(a)),
                 dpad_y + (half - r) * math.sin(math.radians(a)), r) for a in (0, 90, 180, 270)]
        z_lo = _floor_under(btns)
        seat = face_button({"count": 4, "spacing_deg": 90.0, "circle_radius": half - r,
                            "radius": r, "recess_depth": Z_OUT - z_lo, "center_x": dpad_x,
                            "center_y": dpad_y, "cut_center_z": (Z_OUT + z_lo) / 2.0})
        return [seat], _caps(btns, z_lo, dpad_height)
    tips = [(dpad_x + dx, dpad_y + dy, 0) for dx, dy in
            ((half, 0), (-half, 0), (0, half), (0, -half), (0, 0))]
    z_lo = _floor_under(tips)
    seat = d_pad({"arm_length": dpad_size, "arm_width": dpad_arm_width,
                  "recess_depth": Z_OUT - z_lo, "center_x": dpad_x, "center_y": dpad_y,
                  "cut_center_z": (Z_OUT + z_lo) / 2.0})
    cap = pad_cross_cap({"center_x": dpad_x, "center_y": dpad_y, "arm_length": dpad_size,
                         "arm_width": dpad_arm_width, "z0": z_lo + control_clearance,
                         "z1": _top(dpad_x, dpad_y) + dpad_height,
                         "clearance": control_clearance})
    return [seat], [cap]


def _face():
    btns = pad_face_layout({"arrangement": face_arrangement, "count": face_count,
                            "spacing": face_spacing, "radius": face_radius,
                            "tilt_deg": face_tilt_deg, "center_x": face_x, "center_y": face_y})
    if not btns:
        return [], []
    if face_arrangement == "diamond":   # the ring face_button already builds
        z_lo = _floor_under(btns)
        seat = face_button({"count": face_count, "spacing_deg": 360.0 / face_count,
                            "circle_radius": face_spacing, "radius": face_radius,
                            "recess_depth": Z_OUT - z_lo, "center_x": face_x,
                            "center_y": face_y, "cut_center_z": (Z_OUT + z_lo) / 2.0})
        seat = seat.rotate((face_x, face_y, 0), (face_x, face_y, 1), face_tilt_deg)
        return [seat], _caps(btns, z_lo, face_height)
    seat = pad_round_seats({"crown": _crown(), "buttons": btns, "recess": control_recess_depth})
    return [seat], _caps(btns, None, face_height)


def _stick_points():
    pts = []
    if stick_count >= 1:
        pts.append((stick_left_x, stick_left_y))
    if stick_count >= 2:
        pts.append((-stick_left_x, stick_left_y) if stick_layout == "symmetric"
                   else (stick_right_x, stick_right_y))
    return pts


def _sticks():
    seats, caps = [], []
    well = STICK_WELL * control_recess_depth
    for x, y in _stick_points():
        zs = _top(x, y)
        z_lo = zs - well
        if stick_gate == "octagon":
            seats.append(pad_octagon_seat({"crown": _crown(), "center_x": x, "center_y": y,
                                           "radius": stick_gate_radius, "recess": well}))
        else:
            seats.append(analog_stick({"count": 1, "first_center_x": x, "pitch_x": 0.0,
                                       "center_y": y, "radius": stick_gate_radius,
                                       "recess_depth": Z_OUT - z_lo,
                                       "cut_center_z": (Z_OUT + z_lo) / 2.0}))
        caps.append(pad_stick({"center_x": x, "center_y": y, "floor_z": z_lo, "surface_z": zs,
                               "radius": stick_radius, "height": stick_height,
                               "cap": stick_cap, "tilt_deg": stick_tilt_deg,
                               "clearance": control_clearance}))
    return seats, caps


def _row_xs(n, x):
    return [-x, x][:n] if n <= 2 else [-x, x]


def _shoulders():
    seats, caps = [], []
    cl = control_clearance
    if bumper_count > 0:
        z_edge = _top(bumper_x, Y_EDGE)
        y_in = Y_EDGE - bumper_depth
        for row in range(2 if bumper_count > 2 else 1):
            n = min(2, bumper_count - 2 * row)
            z0 = z_edge - bumper_height - row * (bumper_height + 1.5)
            z1 = Z_OUT if row == 0 else z0 + bumper_height
            seats.append(shoulder_trigger({
                "count": n, "first_center_x": -bumper_x, "pitch_x": 2.0 * bumper_x,
                "center_y": (Y_OUT + y_in) / 2.0, "center_z": (z0 + z1) / 2.0,
                "width": bumper_width, "depth": Y_OUT - y_in, "height": z1 - z0}))
            for x in _row_xs(n, bumper_x):
                caps.append(pad_box({"x0": x - bumper_width / 2.0 + cl,
                                     "x1": x + bumper_width / 2.0 - cl, "y0": y_in + cl,
                                     "y1": Y_EDGE + 1.0, "z0": z0 + cl,
                                     "z1": (z_edge + 1.0) if row == 0 else z1 - cl}).val())
    if trigger_count > 0:
        top = _bottom(trigger_x, Y_EDGE) + trigger_length
        y_in = Y_EDGE - trigger_depth
        seats.append(shoulder_trigger({
            "count": trigger_count, "first_center_x": -trigger_x, "pitch_x": 2.0 * trigger_x,
            "center_y": (Y_OUT + y_in) / 2.0, "center_z": (top - 1.0) / 2.0,
            "width": trigger_width, "depth": Y_OUT - y_in, "height": top + 1.0}))
        for x in _row_xs(trigger_count, trigger_x):
            caps.append(pad_trigger_blade({
                "center_x": x, "width": trigger_width, "y_inner": y_in, "notch_top": top,
                "length": 1.35 * trigger_length,
                "thickness": min(trigger_depth - 2.0 * cl, 3.5), "clearance": cl,
                "angle_deg": TRIGGER_OPEN_DEG - trigger_travel_deg}))
    if under_trigger:
        w = 0.9 * grip_root_radius if grip_root_radius > 4.0 else 14.0
        h = 0.25 * thickness
        z_ref = 0.0 if pad_grip_count(_plan(0.0)) >= 3 else _bottom(0.0, under_trigger_y)
        y0, y1 = under_trigger_y - UNDER_TRIGGER_DEPTH / 2.0, under_trigger_y + UNDER_TRIGGER_DEPTH / 2.0
        seats.append(pad_box({"x0": -w / 2.0, "x1": w / 2.0, "y0": y0, "y1": y1,
                              "z0": -1.0, "z1": z_ref + h}))
        caps.append(pad_box({"x0": -w / 2.0 + cl, "x1": w / 2.0 - cl, "y0": y0 + cl,
                             "y1": y1 - cl, "z0": z_ref - UNDER_TRIGGER_HANG,
                             "z1": z_ref + h - cl}).val())
    return seats, caps


def _system():
    n = system_button_count
    if n <= 0:
        return [], []
    btns = [((i - (n - 1) / 2.0) * system_pitch, system_y, system_radius) for i in range(n)]
    z_lo = _floor_under(btns)
    seat = button_row({"count": n, "first_center_x": btns[0][0], "pitch_x": system_pitch,
                       "center_y": system_y, "radius": system_radius,
                       "recess_depth": Z_OUT - z_lo, "cut_center_z": (Z_OUT + z_lo) / 2.0})
    return [seat], _caps(btns, z_lo, SYSTEM_HEIGHT)


def _features():
    """Cutters with no cap: touchpad, light bar, grille, jack, charge port, slots, door."""
    out = []
    rec = control_recess_depth
    if touchpad_present:
        w, h = touchpad_width / 2.0, touchpad_height / 2.0
        z_lo = min(_top(sx * w, touchpad_y + sy * h) for sx in (-1, 1) for sy in (-1, 1)) - rec
        out.append(_rect(touchpad_width, touchpad_height, z_lo, Z_OUT, 0.0, touchpad_y))
    if light_bar_present:
        y = touchpad_y + touchpad_height / 2.0 + LIGHT_BAR_GAP
        z_lo = min(_top(-light_bar_width / 2.0, y), _top(light_bar_width / 2.0, y)) - rec
        out.append(_rect(light_bar_width, LIGHT_BAR_SLOT, z_lo, Z_OUT, 0.0, y))
    if speaker_present:
        span = GRILLE["pitch"] * GRILLE["cols"] / 2.0
        z_lo = min(_top(-span, speaker_y), _top(span, speaker_y)) - rec
        out.append(pad_grille(dict(GRILLE, center_x=0.0, center_y=speaker_y,
                                   z_lo=z_lo, z_hi=Z_OUT)))
    if headset_jack:
        y_front = -bridge_depth / 2.0 + (PAD_CRESCENT_BITE * bridge_depth
                                         if outline == "crescent" else 0.0)
        y1 = y_front + JACK_DEPTH
        out.append(port_receptacle({"shape": "round", "width": 0.0, "height": 0.0,
                                    "depth": y1 - Y_FRONT_OUT, "radius": JACK_RADIUS,
                                    "center_x": 0.0, "center_y": (y1 + Y_FRONT_OUT) / 2.0,
                                    "center_z": _mid(0.0, y_front + 1.0)}))
    if charge_port:
        z = _mid(0.0, Y_EDGE - 1.0)
        out.append(_rect(CHARGE_WIDTH, Y_OUT - (Y_EDGE - CHARGE_DEPTH),
                         z - CHARGE_HEIGHT / 2.0, z + CHARGE_HEIGHT / 2.0,
                         0.0, (Y_OUT + Y_EDGE - CHARGE_DEPTH) / 2.0))
    xs = [0.0] if expansion_slot_count == 1 else \
        [-expansion_slot_pitch / 2.0, expansion_slot_pitch / 2.0][:expansion_slot_count]
    for x in xs:
        y = expansion_slot_y
        if expansion_slot_face == "under":
            z_ref = 0.0 if pad_grip_count(_plan(0.0)) >= 3 else _bottom(x, y)
            z_lo, z_hi = -1.0, z_ref + expansion_slot_depth
        else:
            z_lo, z_hi = _top(x, y) - expansion_slot_depth, Z_OUT
        out.append(_rect(expansion_slot_width, expansion_slot_thickness, z_lo, z_hi, x, y))
    if battery_door:
        w, h = battery_door_width / 2.0, battery_door_length / 2.0
        z_ref = max(_bottom(sx * w, battery_door_y + sy * h) for sx in (-1, 1) for sy in (-1, 1))
        out.append(pad_door_seam({"center_x": 0.0, "center_y": battery_door_y,
                                  "width": battery_door_width, "length": battery_door_length,
                                  "groove": DOOR_GROOVE, "z_lo": -1.0,
                                  "z_hi": z_ref + DOOR_GROOVE}))
    return out


def _controls():
    seats, caps = [], []
    for build in (_dpad, _face, _sticks, _shoulders, _system):
        s, c = build()
        seats += s
        caps += c
    return seats, caps


def _cable_boss():
    """The cable's strain-relief stub on the shoulder edge (`cable_exit`, F18's seat)."""
    if cable_exit == "none":
        return None
    x = 0.0 if cable_exit == "top_center" else -bridge_width / 4.0
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(
        CABLE_RADIUS, CABLE_LENGTH + 2.0, cq.Vector(x, Y_EDGE - 2.0, _mid(x, Y_EDGE - 1.0)),
        cq.Vector(0, 1, 0)))


def _base():
    """The crowned body with the cable stub fused on: everything before any seat."""
    body = pad_body(_plan(0.0))
    boss = _cable_boss()
    return body if boss is None else body.union(boss)


def _tools():
    seats, _ = _controls()
    return [s for t in seats + _features() for s in t.vals()]


def _cut(solid, tools):
    """Cut, in ONE boolean, every tool whose box meets the solid's (a tool that cannot
    touch it only costs time)."""
    a = solid.val().BoundingBox()
    near = [t for t in tools if not (
        t.BoundingBox().xmin > a.xmax or t.BoundingBox().xmax < a.xmin
        or t.BoundingBox().ymin > a.ymax or t.BoundingBox().ymax < a.ymin
        or t.BoundingBox().zmin > a.zmax or t.BoundingBox().zmax < a.zmin)]
    return cq.Workplane("XY").add(solid.val().cut(*near)) if near else solid


def _half(side):
    """One half (side -1 left, +1 right) with its seats, rail or magnets, unshifted."""
    inner = PAD_RAIL_HEIGHT if split == "rail_halves" else 0.0
    keep = cq.Workplane("XY").box(4000, 4000, 4000).translate((side * (2000 + inner), 0, 0))
    tools = _tools()
    z = _mid(0.0, crown_center_y)
    if split == "magnetic_halves":
        tools += pad_magnet_pockets({"side": side, "pitch": 0.6 * rail_length,
                                     "center_y": crown_center_y, "center_z": z}).vals()
    half = _cut(_base().intersect(keep), tools)
    if split == "rail_halves":
        half = half.union(pad_rail({"side": side, "length": rail_length, "width": rail_width,
                                    "center_y": crown_center_y, "center_z": z}))
    return half


def _shift():
    return (SPLIT_CLEARANCE + split_gap) / 2.0 if split != "none" else 0.0


def _compound(solids):
    return cq.Workplane("XY").add(cq.Compound.makeCompound(solids))


def body_part():
    if split == "none":
        return _cut(_base(), _tools())
    s = _shift()
    return _compound([_half(-1).translate((-s, 0, 0)).val(),
                      _half(1).translate((s, 0, 0)).val()])


def controls_part():
    _, caps = _controls()
    s = _shift()
    if s:
        caps = [c.translate(cq.Vector(s if c.Center().x >= 0 else -s, 0, 0)) for c in caps]
    return _compound(caps)


def envelope_part():
    return pad_body(_plan(0.0))


def _shell(upper):
    """The body above (or below) the seam plane, hollowed by the inset body: seats and
    cavity cut in one boolean."""
    seam = seam_ratio * thickness
    z0, z1 = (seam, Z_OUT + 1.0) if upper else (-2.0, seam)
    keep = cq.Workplane("XY").box(4000, 4000, z1 - z0).translate((0, 0, (z0 + z1) / 2.0))
    return _cut(_base().intersect(keep), _tools() + pad_body(_plan(shell_wall)).vals())


BUILDERS = {
    "body": body_part,
    "controls": controls_part,
    "envelope": envelope_part,
    "top_shell": lambda: _shell(True),
    "bottom_shell": lambda: _shell(False),
    "left_half": lambda: _half(-1),
    "right_half": lambda: _half(1),
}

result = BUILDERS.get(target_part, body_part)()
