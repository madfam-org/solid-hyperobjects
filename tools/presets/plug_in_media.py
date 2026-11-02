"""Plug-in media: archetype, rules, catalog reader, derivation.

Everything that plugs in by a contact edge, from a 1976 cartridge with a door to a
game card: a shell split on its mid-plane, a board whose tongue reaches a contact
window, and the features a slot registers against. One object per FORMAT (a shell
type), never per title.

AXIS MAPPING
------------
    reference dimensions_mm.states.shell.width  -> shell_width      (X, across the label)
    reference dimensions_mm.states.shell.height -> shell_height     (Z, up the label)
    reference dimensions_mm.states.shell.depth  -> shell_thickness  (Y, through the shell)

`features.insertion_edge` names the label edge that carries the contacts; the family
turns the shell so the envelope (its bounding box) is the same for every edge.

WHEN THE CATALOG IS EMPTY
-------------------------
At the time of writing the pinned catalog files no `plug-in-media` object (research lane
RA4 is filing them). The family therefore ships five ARCHETYPE presets (`kind:
archetype`) — named points in its own parameter space that assert nothing about any
product — and every object RA4 files becomes a preset at the next generator run.
"""
from __future__ import annotations

import math

from common import DeriveError, Family, rnd, state

# ─────────────────────────────────────────────────────────────────────────────
# The archetype. Every number below is OURS, not a format claim.
# ─────────────────────────────────────────────────────────────────────────────

#: The family default: a generic top-loading cartridge that is no product.
ARCHETYPE_BASE = {
    "slug": "__archetype__",
    "width": 100.0, "height": 110.0, "depth": 15.0,
    "grip_thickness": 19.0,
    "insertion_edge": "bottom", "card": False, "shutter": False,
    "pass_through_slot": False, "edge_contacts": None, "contact_pitch_mm": None,
    "notch_count": 0,
}

ARCHETYPE_RULES = {
    "corner_ratio": 0.08,          # of the shorter face side
    "corner_min": 0.5, "corner_max": 4.0,
    "wall_ratio": 0.11,            # of the thickness, hollow shells
    "wall_min": 0.8, "wall_max": 2.0,
    "pcb_thickness": 1.6,          # hollow shells
    "card_plate_ratio": 0.25,      # of a card's thickness: the contact plate
    "card_plate_min": 0.3, "card_plate_max": 0.8,
    "pcb_clearance": 0.3,
    "pcb_edge_recess": 1.0,        # contact edge -> board edge, hollow shells
    "window_ratio": 0.8,           # of the contact edge, when no pitch is sourced
    "window_margin": 2.0,          # outermost contact -> window side
    "window_depth_ratio": 0.09,    # of the shell's length away from the edge
    "window_depth_min": 4.0, "window_depth_max": 12.0,
    "card_window_ratio": 0.2, "card_window_min": 3.0, "card_window_max": 8.0,
    "edge_pitch": 2.5, "card_edge_pitch": 1.2,
    "grip_height_ratio": 0.2,      # of the shell's length, where a band exists
    "label_margin": 3.0,
    "label_width_ratio": 0.8, "label_back_width_ratio": 0.6,
    "label_back_height_ratio": 0.45,
    "label_depth": 0.6, "card_label_depth": 0.3,
    "ridge_count": 5, "ridge_pitch": 3.0, "ridge_depth": 0.6,
    "notch_width_ratio": 0.08, "notch_depth_ratio": 0.04, "notch_offset_ratio": 0.15,
    "shutter_extra": 6.0, "shutter_gap": 0.6,
    "pass_width_ratio": 0.7, "pass_thickness_ratio": 0.55, "pass_depth_ratio": 0.15,
    "card_threshold_mm": 4.0,      # fallback: a shell this thin or thinner is a card
}

#: Parameters a preset may carry, in the order written.
PRESET_PARAM_ORDER = [
    "shell_width", "shell_height", "shell_thickness", "grip_thickness", "grip_height",
    "corner_radius", "shell_wall", "insertion_edge", "card_mode",
    "contact_window_width", "contact_window_depth", "pcb_thickness", "pcb_edge_recess",
    "edge_contacts", "edge_pitch",
    "label_front_width", "label_front_height", "label_front_depth", "label_front_center",
    "label_back_width", "label_back_height", "label_back_depth", "label_back_center",
    "grip_ridge_count", "grip_ridge_pitch", "grip_ridge_depth",
    "notch_count", "notch_width", "notch_depth", "notch_offset",
    "shutter", "shutter_height", "shutter_gap", "shutter_groove_depth",
    "pass_through_slot", "pass_slot_width", "pass_slot_thickness", "pass_slot_depth",
]

#: Pure archetype — only in the defaults.
ARCHETYPE_ONLY_PARAMS = ["pcb_clearance", "insert_travel"]


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


# ─────────────────────────────────────────────────────────────────────────────
# Catalog reading (brief §3, `plug-in-media`)
# ─────────────────────────────────────────────────────────────────────────────

def _feature(obj: dict, name: str):
    """A feature value, or None when it is null or no value-tier source covers it."""
    from hyperobjects_reference import is_sourced

    value = (obj.get("features") or {}).get(name)
    if value is None or not is_sourced(obj, f"features.{name}"):
        return None
    return value


def read_media(obj: dict) -> dict | None:
    """Project a reference object onto `derive()`'s input, or None (shell unresolved)."""
    shell = state(obj, "shell")
    w, h, d = shell.get("width"), shell.get("height"), shell.get("depth")
    if w is None or h is None or d is None:
        return None
    edge = _feature(obj, "insertion_edge")
    return {
        "slug": obj["key"],
        "width": float(w), "height": float(h), "depth": float(d),
        "grip_thickness": None,
        "insertion_edge": edge if edge in ("bottom", "top", "side") else None,
        "card": _feature(obj, "card"),
        "shutter": _feature(obj, "shutter"),
        "pass_through_slot": _feature(obj, "pass_through_slot"),
        "edge_contacts": _feature(obj, "edge_contacts"),
        "contact_pitch_mm": _feature(obj, "contact_pitch_mm"),
        "notch_count": None,
    }


def registry_extra(obj: dict, values: dict) -> dict:
    return {"host_console": (obj.get("features") or {}).get("host_console")}


# ─────────────────────────────────────────────────────────────────────────────
# The one derivation path
# ─────────────────────────────────────────────────────────────────────────────

def derive(src: dict, *, full: bool) -> tuple[dict, list[str]]:
    """Return (values, fallbacks). Every value is sourced or follows a rule above."""
    R = ARCHETYPE_RULES
    fb: list[str] = []
    v: dict = {}

    W, H, D = float(src["width"]), float(src["height"]), float(src["depth"])
    edge = src.get("insertion_edge")
    if edge is None:
        fb.append("insertion edge")
        edge = "bottom"
    card = src.get("card")
    if card is None:
        fb.append("card or shell (from thickness)")
        card = D <= R["card_threshold_mm"]
    card = bool(card)
    CW, CH = (H, W) if edge == "side" else (W, H)

    gt = src.get("grip_thickness") or 0.0
    band = (not card) and gt > D
    v["shell_width"], v["shell_height"], v["shell_thickness"] = rnd(W), rnd(H), rnd(D)
    v["grip_thickness"] = rnd(gt if band else 0.0)
    grip_h = CH * R["grip_height_ratio"] if band else 0.0
    v["grip_height"] = rnd(grip_h)
    v["corner_radius"] = rnd(_clamp(R["corner_ratio"] * min(W, H), R["corner_min"],
                                    R["corner_max"]))
    wall = _clamp(R["wall_ratio"] * D, R["wall_min"], R["wall_max"])
    v["shell_wall"] = rnd(wall)
    v["insertion_edge"] = edge
    v["card_mode"] = card

    # ── contact edge ─────────────────────────────────────────────────────────
    clear = R["pcb_clearance"]
    if card:
        pcb_t = _clamp(R["card_plate_ratio"] * D, R["card_plate_min"], R["card_plate_max"])
        depth_c = _clamp(R["card_window_ratio"] * CH, R["card_window_min"],
                         R["card_window_max"])
        default_pitch = R["card_edge_pitch"]
        room = CW - 2.0 * R["label_margin"]
    else:
        pcb_t = R["pcb_thickness"]
        depth_c = _clamp(R["window_depth_ratio"] * CH, R["window_depth_min"],
                         R["window_depth_max"])
        default_pitch = R["edge_pitch"]
        room = CW - 2.0 * wall - 2.0
    if not card and 2.0 * wall + pcb_t + 2.0 * clear >= D:
        raise DeriveError(f"{src['slug']}: a {D} mm shell has no room for a board. Not modelled.")
    pitch = src.get("contact_pitch_mm")
    n = src.get("edge_contacts")
    if pitch is None:
        fb.append("contact pitch")
        pitch = default_pitch
    if n is None:
        fb.append("edge-contact count")
    per_face = None if n is None else (int(n) if card else int(math.ceil(int(n) / 2.0)))
    if per_face is None:
        window_w = min(R["window_ratio"] * CW, room)
        per_face = int((window_w - 2.0 * R["window_margin"]) // pitch)
        n = per_face if card else 2 * per_face
    else:
        window_w = per_face * float(pitch) + 2.0 * R["window_margin"]
        if window_w > room:
            raise DeriveError(f"{src['slug']}: {n} contacts at {pitch} mm need a "
                              f"{window_w} mm window; the edge has {room} mm. Not modelled.")
    v["contact_window_width"] = rnd(window_w)
    v["contact_window_depth"] = rnd(depth_c)
    v["pcb_thickness"] = rnd(pcb_t)
    v["pcb_edge_recess"] = rnd(R["pcb_edge_recess"])
    v["edge_contacts"] = int(n)
    v["edge_pitch"] = rnd(pitch)

    # ── shutter, pass-through ────────────────────────────────────────────────
    shutter = src.get("shutter")
    if shutter is None:
        fb.append("shutter")
        shutter = False
    shutter_h = depth_c + R["shutter_extra"]
    v["shutter"] = bool(shutter)
    v["shutter_height"] = rnd(shutter_h)
    v["shutter_gap"] = rnd(R["shutter_gap"])
    v["shutter_groove_depth"] = rnd(min(R["ridge_depth"], 0.4 * wall))
    passing = src.get("pass_through_slot")
    if passing is None:
        fb.append("pass-through slot")
        passing = False
    v["pass_through_slot"] = bool(passing)
    v["pass_slot_width"] = rnd(R["pass_width_ratio"] * CW)
    v["pass_slot_thickness"] = rnd(R["pass_thickness_ratio"] * D)
    v["pass_slot_depth"] = rnd(R["pass_depth_ratio"] * CH)

    # ── grip ridges, labels ──────────────────────────────────────────────────
    ridges = 0 if card else R["ridge_count"]
    v["grip_ridge_count"] = ridges
    v["grip_ridge_pitch"] = rnd(R["ridge_pitch"])
    v["grip_ridge_depth"] = rnd(min(R["ridge_depth"], 0.4 * wall))
    m = R["label_margin"]
    top = CH - max(grip_h, ridges * R["ridge_pitch"]) - m
    if passing:
        top = min(top, CH - R["pass_depth_ratio"] * CH - m)
    bottom_f = depth_c + m
    label_d = R["card_label_depth"] if card else min(R["label_depth"], 0.4 * wall)
    if top - bottom_f < 2.0 * m:
        raise DeriveError(f"{src['slug']}: no room for a label between the contact window "
                          f"and the grip. Not modelled.")
    v["label_front_width"] = rnd(R["label_width_ratio"] * CW)
    v["label_front_height"] = rnd(top - bottom_f)
    v["label_front_depth"] = rnd(label_d)
    v["label_front_center"] = rnd((top + bottom_f) / 2.0)
    bottom_b = (shutter_h + 0.5 + 2.0 * R["shutter_gap"] if shutter else depth_c) + m
    back_h = min(R["label_back_height_ratio"] * (top - bottom_b), top - bottom_b)
    v["label_back_width"] = rnd(R["label_back_width_ratio"] * CW)
    v["label_back_height"] = rnd(back_h)
    v["label_back_depth"] = rnd(0.0 if card else label_d)
    v["label_back_center"] = rnd(bottom_b + back_h / 2.0)

    # ── keying ───────────────────────────────────────────────────────────────
    notches = src.get("notch_count")
    if notches is None:
        fb.append("keying notches")
        notches = 0
    v["notch_count"] = int(notches)
    v["notch_width"] = rnd(R["notch_width_ratio"] * CH)
    v["notch_depth"] = rnd(R["notch_depth_ratio"] * CW)
    v["notch_offset"] = rnd(R["notch_offset_ratio"] * CH)

    if not full:
        return {k: v[k] for k in PRESET_PARAM_ORDER if k in v}, fb
    v["pcb_clearance"] = rnd(clear)
    v["insert_travel"] = 0
    return {k: v[k] for k in PRESET_PARAM_ORDER + ARCHETYPE_ONLY_PARAMS}, fb


# ─────────────────────────────────────────────────────────────────────────────
# Archetype presets: named points of the family's own space, never products
# ─────────────────────────────────────────────────────────────────────────────

ARCHETYPE_PRESETS = [
    ("top-loading-cartridge", "Top-loading cartridge", "Cartucho de carga superior",
     "the family default: a shell inserted contact edge down, with a thicker grip band.",
     "el valor por defecto de la familia: una carcasa que entra con el borde de contactos abajo, con una banda de agarre más gruesa.",
     ARCHETYPE_BASE),
    ("front-loading-cartridge", "Front-loading cartridge", "Cartucho de carga frontal",
     "a wide, flat shell whose contacts are on the label's top edge, so the label reads upright as it lies in the slot; two keying notches.",
     "una carcasa ancha y plana con los contactos en el borde superior de la etiqueta, para que se lea derecha en la ranura; dos muescas de codificación.",
     {**ARCHETYPE_BASE, "width": 120.0, "height": 130.0, "depth": 17.0, "grip_thickness": 0.0,
      "insertion_edge": "top", "notch_count": 2}),
    ("card", "Card", "Tarjeta",
     "a monolithic thin card with its contact field in a back-face pocket on a side edge, and one keying notch.",
     "una tarjeta delgada monolítica con su campo de contactos en un rebaje de la cara trasera en un borde lateral, y una muesca de codificación.",
     {**ARCHETYPE_BASE, "width": 40.0, "height": 30.0, "depth": 3.0, "grip_thickness": 0.0,
      "insertion_edge": "side", "card": True, "notch_count": 1}),
    ("pass-through-cartridge", "Pass-through cartridge", "Cartucho de paso",
     "a deep shell with a slot in its far edge that takes a second medium.",
     "una carcasa profunda con una ranura en el borde opuesto que recibe un segundo medio.",
     {**ARCHETYPE_BASE, "width": 110.0, "height": 130.0, "depth": 22.0, "grip_thickness": 0.0,
      "pass_through_slot": True}),
    ("shuttered-cartridge", "Shuttered cartridge", "Cartucho con compuerta",
     "a shell whose contact window is covered by a door outlined in its back face.",
     "una carcasa cuya ventana de contactos está cubierta por una compuerta delineada en la cara trasera.",
     {**ARCHETYPE_BASE, "width": 105.0, "height": 120.0, "depth": 20.0, "grip_thickness": 0.0,
      "shutter": True}),
]


def _archetype_presets() -> list[dict]:
    out = []
    for slug, en, es, what_en, what_es, base in ARCHETYPE_PRESETS:
        values, _ = derive(base, full=False)
        out.append({
            "slug": f"archetype-{slug}",
            "label": {"en": f"Archetype — {en.lower()}", "es": f"Arquetipo — {es.lower()}"},
            "kind": "archetype",
            "source": ("Archetype, not a product: " + what_en + " Every number is the "
                       "family's own rule (tools/presets/plug_in_media.py); no format is "
                       "claimed. Generated by tools/presets/presets.py — do not edit by hand."),
            "description": {"en": what_en, "es": what_es},
            "values": values,
        })
    return out


FAMILY = Family(
    slug="plug-in-media",
    base=ARCHETYPE_BASE,
    read=read_media,
    derive=derive,
    axis_mapping={
        "shell_width": "reference dimensions_mm.states.shell.width (X, across the label face)",
        "shell_height": "reference dimensions_mm.states.shell.height (Z, up the label face)",
        "shell_thickness": "reference dimensions_mm.states.shell.depth (Y, through the shell)",
    },
    source_line="shell width x height x depth as published; features as quoted.",
    registry_extra=registry_extra,
    extra_presets=_archetype_presets(),
)
