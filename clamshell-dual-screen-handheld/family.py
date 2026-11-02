"""
Clamshell Dual-Screen Handheld — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

The archetype: two rigid decks joined by a knuckle hinge along the long edge.
The upper deck carries the primary display recess; the lower deck carries the
secondary display recess, the controls (D-pad, face buttons, sticks, shoulder
triggers, start/select), a USB-C port, a 3.5 mm jack, a cartridge slot and a
speaker grille. One continuous `fold_angle` rotates the upper deck about the
hinge: 0 closed, 180 flat.

COMPOSITION — a device is a hyperobject of hyperobjects
------------------------------------------------------
A screen, a hinge, a button, a D-pad, a stick, a port and a cartridge slot are
each a hyperobject in their own right that feeds into this one. Each is a
function in commons-lib/hardware/ taking its OWN parameter dict: no component
reads a manifest global, and none knows what assembly it is part of. The
assembly functions (`lower_deck_part`, `upper_deck_part`, `hinge_part`) are the
only code that maps this manifest's parameters onto those dicts.

    component            module         CDG interface it exposes / consumes
    ------------------   ------------   --------------------------------------
    deck_shell           structure      exposes device_envelope, cradle_seat
    display_panel        displays       exposes display_recess
    hinge_barrel         structure      exposes revolute_axis, mounting_surface
                                        (the ids `hinge-hyperobject` declares)
    hinge_relief         structure      consumes revolute_axis
    d_pad                controls       exposes dpad_seat
    face_button          controls       exposes button_seat (ring arrangement)
    button_row           controls       exposes button_seat (row: start/select)
    analog_stick         controls       exposes stick_seat
    shoulder_trigger     controls       exposes trigger_seat
    port_receptacle      connectors     exposes port_cutout
    cartridge_slot       connectors     exposes cartridge_slot
    speaker_grille       structure      a vented face; no upstream id yet

The manifest's `composition` block carries the same table for machines. The
vocabulary is Telesia's DEVICE_GEOMETRY.md §3.1. Gate H8 (how a component feeds
an assembly cartridge) is settled by ruling R2, 2026-11-01: the sandbox blocks
`sys`, `os` and `importlib`, so a component is never imported. Its canonical
text lives in commons-lib/hardware/ and is INLINED at build.

TWO FILES. This file, `family.py`, is the authored half. `main.py` is generated
from it by `tools/inline_parts.py`, which copies every module the
`# inline-parts:` directive names (plus their `# requires:`) between
`# BEGIN/END commons-lib/hardware/<m>.py@<git-blob-sha>` markers. Edit this
file or the module, never main.py, then run
`python3 tools/inline_parts.py --write clamshell-dual-screen-handheld`; CI's
`inline_parts.py --check` fails on any drift.

This is a FAMILY, not a product. Named presets carry published dimensions from
the keystone's reference-objects catalog with a provenance line; every other number is
an archetype default that is ours, and NOTICE says which is which. No logos, no
trade dress, no surface detail beyond what published dimensions imply.

Frame (stated again in docs/README.md, because manufacturers in this family
label the long axis "width" and the registry records their labels literally):

    X  deck_length   the LONG axis. The hinge axis is the X axis through the
                     origin. Registry `dimensions_mm.closed.height`.
    Y  deck_depth    the folding axis. Both decks extend from the hinge at y = 0
                     to the front face at y = deck_depth. Registry
                     `dimensions_mm.closed.width`.
    Z  thickness     upper_deck_thickness + lower_deck_thickness equals the
                     registry's `dimensions_mm.closed.depth`. The seam plane —
                     where the two decks meet when closed — is z = 0.

Parts (dispatched on `target_part`):
  - lower_deck : the deck that carries the controls and the ports.
  - upper_deck : the display deck, already rotated by `fold_angle`.
  - hinge      : the knuckle barrels, a half-cylinder run on the hinge axis.

Graph twin: `clamshell.graph.json` builds the same three parts from the same
parameters using the nineteen graph-engine node types, with each component's
nodes grouped under a component-slug prefix. Sub-graph reuse — yantra4d lane
G-CLUSTERS — is what would let the twin REFERENCE a component cartridge instead
of duplicating its nodes; until it lands the twin inlines them.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` (cadquery) and `math` are pre-injected globals; imported here too so the
    module lints clean (ruff F821) and runs standalone.
  - Manifest parameters arrive as BARE globals (a param `deck_length` -> global
    `deck_length`). They are read through the PARAM(lambda: name, default) guard
    because the sandbox exposes neither globals() nor eval/getattr.
  - The final solid is assigned to the top-level name `result`.
"""

import math  # noqa: F401 — injected by the sandbox; imported so the file runs standalone

import cadquery as cq  # noqa: F401 — the inlined components below use it


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default.

    `except Exception` catches the NameError raised for an unbound param name
    (the sandbox does not expose globals()/NameError directly).
    """
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
# Every default below is the archetype's own, generated by tools/presets/
# (this repository) from ARCHETYPE_BASE + ARCHETYPE_RULES. They describe
# no product. Device values arrive as presets.

# L0 — envelope
deck_length = float(PARAM(lambda: deck_length, 150.0))
deck_depth = float(PARAM(lambda: deck_depth, 90.0))
upper_deck_thickness = float(PARAM(lambda: upper_deck_thickness, 9.9))
lower_deck_thickness = float(PARAM(lambda: lower_deck_thickness, 12.1))
corner_radius = float(PARAM(lambda: corner_radius, 5.0))
fold_angle = float(PARAM(lambda: fold_angle, 120.0))
deck_center_y = float(PARAM(lambda: deck_center_y, 45.0))
lower_deck_center_z = float(PARAM(lambda: lower_deck_center_z, -6.05))
upper_deck_center_z = float(PARAM(lambda: upper_deck_center_z, 4.95))

# L0 — hinge. `hinge_relief_radius` is `hinge_barrel_radius` plus the archetype's
# 0.4 mm running clearance; the graph engine has no expressions, so the two are
# independent parameters that the generator keeps in step (lane G-EXPR).
hinge_barrel_radius = float(PARAM(lambda: hinge_barrel_radius, 5.445))
hinge_relief_radius = float(PARAM(lambda: hinge_relief_radius, 5.845))
hinge_relief_span = float(PARAM(lambda: hinge_relief_span, 75.8))
hinge_knuckle_count = int(PARAM(lambda: hinge_knuckle_count, 3))
hinge_knuckle_length = float(PARAM(lambda: hinge_knuckle_length, 21.0))
hinge_knuckle_pitch = float(PARAM(lambda: hinge_knuckle_pitch, 27.0))
hinge_knuckle_start_x = float(PARAM(lambda: hinge_knuckle_start_x, -27.0))
hinge_clip_span = float(PARAM(lambda: hinge_clip_span, 400.0))
hinge_clip_center_y = float(PARAM(lambda: hinge_clip_center_y, -200.0))

# L1 — displays
primary_screen_width = float(PARAM(lambda: primary_screen_width, 100.0))
primary_screen_height = float(PARAM(lambda: primary_screen_height, 60.0))
primary_screen_center_y = float(PARAM(lambda: primary_screen_center_y, 45.0))
primary_screen_cut_center_z = float(PARAM(lambda: primary_screen_cut_center_z, 0.4))
secondary_screen_width = float(PARAM(lambda: secondary_screen_width, 80.0))
secondary_screen_height = float(PARAM(lambda: secondary_screen_height, 50.0))
secondary_screen_center_y = float(PARAM(lambda: secondary_screen_center_y, 45.0))
secondary_screen_cut_center_z = float(PARAM(lambda: secondary_screen_cut_center_z, -0.4))
screen_recess_depth = float(PARAM(lambda: screen_recess_depth, 0.8))

# L2 — controls
control_recess_depth = float(PARAM(lambda: control_recess_depth, 1.2))
control_cut_center_z = float(PARAM(lambda: control_cut_center_z, -0.6))
dpad_center_x = float(PARAM(lambda: dpad_center_x, -58.0))
dpad_center_y = float(PARAM(lambda: dpad_center_y, 45.0))
dpad_arm_length = float(PARAM(lambda: dpad_arm_length, 22.0))
dpad_arm_width = float(PARAM(lambda: dpad_arm_width, 8.0))
face_button_center_x = float(PARAM(lambda: face_button_center_x, 58.0))
face_button_center_y = float(PARAM(lambda: face_button_center_y, 45.0))
face_button_count = int(PARAM(lambda: face_button_count, 4))
face_button_spacing_deg = float(PARAM(lambda: face_button_spacing_deg, 90.0))
face_button_circle_radius = float(PARAM(lambda: face_button_circle_radius, 11.0))
face_button_radius = float(PARAM(lambda: face_button_radius, 4.5))
stick_count = int(PARAM(lambda: stick_count, 2))
stick_first_center_x = float(PARAM(lambda: stick_first_center_x, -58.0))
stick_pitch_x = float(PARAM(lambda: stick_pitch_x, 116.0))
stick_center_y = float(PARAM(lambda: stick_center_y, 27.0))
stick_radius = float(PARAM(lambda: stick_radius, 8.0))
shoulder_button_count = int(PARAM(lambda: shoulder_button_count, 2))
shoulder_button_first_center_x = float(PARAM(lambda: shoulder_button_first_center_x, -54.5))
shoulder_button_pitch_x = float(PARAM(lambda: shoulder_button_pitch_x, 109.0))
shoulder_button_center_y = float(PARAM(lambda: shoulder_button_center_y, 0.0))
shoulder_button_center_z = float(PARAM(lambda: shoulder_button_center_z, -6.05))
shoulder_button_width = float(PARAM(lambda: shoulder_button_width, 26.0))
shoulder_button_depth = float(PARAM(lambda: shoulder_button_depth, 6.0))
shoulder_button_height = float(PARAM(lambda: shoulder_button_height, 4.0))
menu_button_count = int(PARAM(lambda: menu_button_count, 2))
menu_button_first_center_x = float(PARAM(lambda: menu_button_first_center_x, 52.0))
menu_button_pitch_x = float(PARAM(lambda: menu_button_pitch_x, 12.0))
menu_button_center_y = float(PARAM(lambda: menu_button_center_y, 78.0))
menu_button_radius = float(PARAM(lambda: menu_button_radius, 2.5))
speaker_hole_count = int(PARAM(lambda: speaker_hole_count, 6))
speaker_first_center_x = float(PARAM(lambda: speaker_first_center_x, -66.75))
speaker_center_y = float(PARAM(lambda: speaker_center_y, 78.0))
speaker_hole_radius = float(PARAM(lambda: speaker_hole_radius, 0.9))
speaker_hole_pitch = float(PARAM(lambda: speaker_hole_pitch, 3.5))

# L2 — ports and the cartridge slot. The presence flags exist because the
# registry knows, per device, which connectors the manufacturer lists: a Nintendo
# DS preset must not grow a USB-C socket. The graph twin cannot read them (no
# branching) — see docs/research/clamshell-archetype.md.
usb_c_present = bool(PARAM(lambda: usb_c_present, True))
usb_c_width = float(PARAM(lambda: usb_c_width, 9.0))
usb_c_height = float(PARAM(lambda: usb_c_height, 3.2))
usb_c_depth = float(PARAM(lambda: usb_c_depth, 12.0))
usb_c_center_x = float(PARAM(lambda: usb_c_center_x, 0.0))
usb_c_center_y = float(PARAM(lambda: usb_c_center_y, 90.0))
usb_c_center_z = float(PARAM(lambda: usb_c_center_z, -6.05))
headphone_present = bool(PARAM(lambda: headphone_present, True))
headphone_radius = float(PARAM(lambda: headphone_radius, 1.75))
headphone_depth = float(PARAM(lambda: headphone_depth, 12.0))
headphone_center_x = float(PARAM(lambda: headphone_center_x, -45.0))
headphone_center_y = float(PARAM(lambda: headphone_center_y, 90.0))
headphone_center_z = float(PARAM(lambda: headphone_center_z, -6.05))
cartridge_slot_present = bool(PARAM(lambda: cartridge_slot_present, True))
cartridge_slot_width = float(PARAM(lambda: cartridge_slot_width, 35.0))
cartridge_slot_height = float(PARAM(lambda: cartridge_slot_height, 4.0))
cartridge_slot_depth = float(PARAM(lambda: cartridge_slot_depth, 10.0))
cartridge_slot_center_x = float(PARAM(lambda: cartridge_slot_center_x, 45.0))
cartridge_slot_center_y = float(PARAM(lambda: cartridge_slot_center_y, 90.0))
cartridge_slot_center_z = float(PARAM(lambda: cartridge_slot_center_z, -6.05))

target_part = str(PARAM(lambda: target_part, "lower_deck"))


# ═════════════════════════════════════════════════════════════════════════════
# COMPONENTS — each is its own hyperobject. Each takes its own dict; none reads
# a manifest global; each is buildable standalone. They are authored once in
# commons-lib/hardware/ and inlined below by tools/inline_parts.py (ruling R2 on
# gate H8); the directive names the modules, `patterns` comes in as a
# requirement of `structure` and `controls`.
# ═════════════════════════════════════════════════════════════════════════════

# inline-parts: structure displays controls connectors


# ═════════════════════════════════════════════════════════════════════════════
# ASSEMBLY — the only code that maps this manifest's parameters onto component
# dicts. Everything above is portable; everything below is this cartridge.
# ═════════════════════════════════════════════════════════════════════════════

def _relief():
    return hinge_relief({
        "relief_radius": hinge_relief_radius,
        "relief_span": hinge_relief_span,
    })


def lower_deck_part():
    solid = deck_shell({
        "length": deck_length, "depth": deck_depth,
        "thickness": lower_deck_thickness,
        "center_y": deck_center_y, "center_z": lower_deck_center_z,
        "corner_radius": corner_radius,
    })
    solid = solid.cut(_relief())
    solid = solid.cut(display_panel({
        "width": secondary_screen_width, "height": secondary_screen_height,
        "recess_depth": screen_recess_depth,
        "center_x": 0.0, "center_y": secondary_screen_center_y,
        "cut_center_z": secondary_screen_cut_center_z,
    }))
    solid = solid.cut(d_pad({
        "arm_length": dpad_arm_length, "arm_width": dpad_arm_width,
        "recess_depth": control_recess_depth,
        "center_x": dpad_center_x, "center_y": dpad_center_y,
        "cut_center_z": control_cut_center_z,
    }))
    solid = solid.cut(face_button({
        "count": face_button_count, "spacing_deg": face_button_spacing_deg,
        "circle_radius": face_button_circle_radius, "radius": face_button_radius,
        "recess_depth": control_recess_depth,
        "center_x": face_button_center_x, "center_y": face_button_center_y,
        "cut_center_z": control_cut_center_z,
    }))
    if stick_count > 0:
        solid = solid.cut(analog_stick({
            "count": stick_count, "first_center_x": stick_first_center_x,
            "pitch_x": stick_pitch_x, "center_y": stick_center_y,
            "radius": stick_radius, "recess_depth": control_recess_depth,
            "cut_center_z": control_cut_center_z,
        }))
    if menu_button_count > 0:
        solid = solid.cut(button_row({
            "count": menu_button_count,
            "first_center_x": menu_button_first_center_x,
            "pitch_x": menu_button_pitch_x, "center_y": menu_button_center_y,
            "radius": menu_button_radius, "recess_depth": control_recess_depth,
            "cut_center_z": control_cut_center_z,
        }))
    if speaker_hole_count > 0:
        solid = solid.cut(speaker_grille({
            "count": speaker_hole_count,
            "first_center_x": speaker_first_center_x,
            "center_y": speaker_center_y, "hole_radius": speaker_hole_radius,
            "pitch": speaker_hole_pitch, "recess_depth": control_recess_depth,
            "cut_center_z": control_cut_center_z,
        }))
    if shoulder_button_count > 0:
        solid = solid.cut(shoulder_trigger({
            "count": shoulder_button_count,
            "first_center_x": shoulder_button_first_center_x,
            "pitch_x": shoulder_button_pitch_x,
            "center_y": shoulder_button_center_y,
            "center_z": shoulder_button_center_z,
            "width": shoulder_button_width, "depth": shoulder_button_depth,
            "height": shoulder_button_height,
        }))
    if usb_c_present:
        solid = solid.cut(port_receptacle({
            "shape": "rect", "width": usb_c_width, "height": usb_c_height,
            "depth": usb_c_depth, "radius": 0.0,
            "center_x": usb_c_center_x, "center_y": usb_c_center_y,
            "center_z": usb_c_center_z,
        }))
    if headphone_present:
        solid = solid.cut(port_receptacle({
            "shape": "round", "width": 0.0, "height": 0.0,
            "depth": headphone_depth, "radius": headphone_radius,
            "center_x": headphone_center_x, "center_y": headphone_center_y,
            "center_z": headphone_center_z,
        }))
    if cartridge_slot_present:
        solid = solid.cut(cartridge_slot({
            "width": cartridge_slot_width, "height": cartridge_slot_height,
            "depth": cartridge_slot_depth,
            "center_x": cartridge_slot_center_x,
            "center_y": cartridge_slot_center_y,
            "center_z": cartridge_slot_center_z,
        }))
    return solid


def upper_deck_part():
    solid = deck_shell({
        "length": deck_length, "depth": deck_depth,
        "thickness": upper_deck_thickness,
        "center_y": deck_center_y, "center_z": upper_deck_center_z,
        "corner_radius": corner_radius,
    })
    solid = solid.cut(_relief())
    solid = solid.cut(display_panel({
        "width": primary_screen_width, "height": primary_screen_height,
        "recess_depth": screen_recess_depth,
        "center_x": 0.0, "center_y": primary_screen_center_y,
        "cut_center_z": primary_screen_cut_center_z,
    }))
    # The fold. The hinge axis IS the X axis through the origin, so the whole
    # deck turns about it with no compensating translation: 0 closed, 180 flat.
    return solid.rotate((0, 0, 0), (1, 0, 0), fold_angle)


def hinge_part():
    return hinge_barrel({
        "barrel_radius": hinge_barrel_radius,
        "knuckle_length": hinge_knuckle_length,
        "knuckle_count": hinge_knuckle_count,
        "knuckle_pitch": hinge_knuckle_pitch,
        "knuckle_start_x": hinge_knuckle_start_x,
        "clip_span": hinge_clip_span,
        "clip_center_y": hinge_clip_center_y,
    })


BUILDERS = {
    "lower_deck": lower_deck_part,
    "upper_deck": upper_deck_part,
    "hinge": hinge_part,
}

result = BUILDERS.get(target_part, lower_deck_part)()
