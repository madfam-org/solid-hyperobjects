"""The clamshell dual-screen handheld: archetype, rules, catalog reader, derivation.

Two rigid decks on a knuckle hinge along the long edge, a display in each, the controls
and the ports on the lower deck. Ported unchanged from Telesia's
`scripts/device-presets.py` (telesia@43828e9); only the reader moved from the registry's
`dimensions_mm.closed` to the catalog's `dimensions_mm.states.closed`.

AXIS MAPPING (the trap the makers' own labels set)
--------------------------------------------------
Makers in this family label the LONG axis "width" (Nintendo's 縦74mm×横134mm×厚さ21mm
gives 134 as 横 "width"), and the catalog records each axis as the source labels it.

    reference dimensions_mm.states.closed.height -> deck_length  (X, the hinge axis)
    reference dimensions_mm.states.closed.width  -> deck_depth   (Y, the folding axis)
    reference dimensions_mm.states.closed.depth  -> upper + lower deck thickness (Z)

The hinge axis is the X axis through the origin; the decks extend in +Y; the seam plane
is Z = 0.
"""
from __future__ import annotations

from common import DeriveError, Family, control_count, display, has_port, is_sourced, rnd, state

# ─────────────────────────────────────────────────────────────────────────────
# The archetype. Every number below is OURS, not a device claim. They are the
# cartridge's defaults and the rules by which sourced values become geometry.
# ─────────────────────────────────────────────────────────────────────────────

#: The archetype's own envelope — a generic dual-screen clamshell handheld that
#: is no particular product. Running `derive()` on it produces the cartridge's
#: parameter defaults.
ARCHETYPE_BASE = {
    "slug": "__archetype__",
    "deck_length": 150.0,          # X, the hinge axis
    "deck_depth": 90.0,            # Y, the folding axis
    "closed_thickness": 22.0,      # Z, both decks stacked
    "primary_screen": (100.0, 60.0),
    "secondary_screen": (80.0, 50.0),
    "face_button_count": 4,
    "stick_count": 2,
    "shoulder_button_count": 2,
    "menu_button_count": 2,
    "usb_c_present": True,
    "headphone_present": True,
}

ARCHETYPE_RULES = {
    # Deck split. The maker publishes ONE closed thickness; the archetype
    # divides it. The sum is always exactly the sourced number.
    "upper_deck_fraction": 0.45,
    # Hinge. Barrel radius is capped twice: by the thinner deck (so the barrel
    # stays inside the closed envelope in Z) and by the hinge-side bezel (so the
    # relief pocket never reaches a screen window).
    "barrel_thickness_ratio": 0.55,
    "hinge_running_clearance": 0.4,
    "rear_bezel_margin": 1.0,
    "hinge_knuckle_count": 3,
    "hinge_span_ratio": 0.50,       # of deck_length; the knuckle run
    "knuckle_length_ratio": 0.14,   # of deck_length; one knuckle
    # Shells and faces.
    "corner_radius": 5.0,           # 0 of 84 catalog objects publishes one
    "screen_recess_depth": 0.8,
    "control_recess_depth": 1.2,
    # Control layout, measured from the secondary screen.
    "control_margin": 18.0,         # screen edge -> cluster centre, in X
    "stick_offset_y": 18.0,         # cluster centre -> stick centre, toward hinge
    "front_row_gap": 8.0,           # screen edge -> menu/speaker row, in +Y
    "edge_margin": 6.0,             # any feature -> the front face
    "dpad_arm_length": 22.0,
    "dpad_arm_width": 8.0,
    "face_button_circle_radius": 11.0,
    "face_button_radius": 4.5,
    "stick_radius": 8.0,
    "menu_button_radius": 2.5,
    "menu_button_pitch": 12.0,
    "shoulder_gap": 4.0,            # knuckle run end -> shoulder cut, in X
    "shoulder_button_width": 26.0,
    "shoulder_button_depth": 6.0,   # how far the cut bites into the rear face
    "shoulder_button_height": 4.0,
    "speaker_hole_count": 6,
    "speaker_hole_radius": 0.9,
    "speaker_hole_pitch": 3.5,
    # Ports. The 3.5 mm figure is the connector's nominal diameter, which is the
    # catalog's own port kind (`headphone_3_5`); the rest is archetype.
    "usb_c_width": 9.0,
    "usb_c_height": 3.2,
    "usb_c_depth": 12.0,
    "headphone_radius": 1.75,
    "headphone_depth": 12.0,
    "headphone_offset_x": 0.30,     # of deck_length, from centre
    # Cartridge slot. ARCHETYPE THROUGHOUT: the catalog's ports[] vocabulary has
    # no game-card kind, so the family's 2026-09-13 compilation report recorded Nintendo's card
    # slot as omitted for want of a matching enum. No preset sources this
    # component; it is archetype furniture like the speaker grille.
    "cartridge_slot_width": 35.0,
    "cartridge_slot_height": 4.0,
    "cartridge_slot_depth": 10.0,
    "cartridge_slot_offset_x": 0.30,  # of deck_length, from centre
    # Frozen spans: cut solids made deliberately larger than the part, the
    # `h: 400` through-bore idiom the commons graph cartridges already use.
    "hinge_clip_span": 400.0,
    "fold_angle": 120.0,
}

#: Parameters a preset may carry. Order is the order they are written.
PRESET_PARAM_ORDER = [
    "deck_length", "deck_depth", "upper_deck_thickness", "lower_deck_thickness",
    "deck_center_y", "lower_deck_center_z", "upper_deck_center_z",
    "hinge_barrel_radius", "hinge_relief_radius", "hinge_relief_span",
    "hinge_knuckle_length", "hinge_knuckle_pitch", "hinge_knuckle_start_x",
    "primary_screen_width", "primary_screen_height", "primary_screen_center_y",
    "primary_screen_cut_center_z",
    "secondary_screen_width", "secondary_screen_height",
    "secondary_screen_center_y", "secondary_screen_cut_center_z",
    "dpad_center_x", "dpad_center_y",
    "face_button_center_x", "face_button_center_y", "face_button_count",
    "face_button_spacing_deg",
    "stick_count", "stick_first_center_x", "stick_pitch_x", "stick_center_y",
    "shoulder_button_count", "shoulder_button_first_center_x",
    "shoulder_button_pitch_x", "shoulder_button_center_y",
    "menu_button_count", "menu_button_first_center_x", "menu_button_pitch_x",
    "menu_button_center_y",
    "speaker_first_center_x", "speaker_center_y",
    "usb_c_center_x", "usb_c_center_y", "usb_c_center_z",
    "headphone_center_x", "headphone_center_y", "headphone_center_z",
    "cartridge_slot_center_x", "cartridge_slot_center_y", "cartridge_slot_center_z",
    "usb_c_present", "headphone_present",
]

#: Parameters that are pure archetype — never in a preset, only in the defaults.
ARCHETYPE_ONLY_PARAMS = [
    "secondary_screen_present", "corner_radius", "fold_angle", "screen_recess_depth", "control_recess_depth",
    "control_cut_center_z", "hinge_knuckle_count", "hinge_clip_span",
    "hinge_clip_center_y", "dpad_arm_length", "dpad_arm_width",
    "face_button_circle_radius", "face_button_radius", "stick_radius",
    "menu_button_radius", "shoulder_button_width", "shoulder_button_depth",
    "shoulder_button_height", "shoulder_button_center_z",
    "speaker_hole_count", "speaker_hole_radius", "speaker_hole_pitch",
    "usb_c_width", "usb_c_height", "usb_c_depth",
    "headphone_radius", "headphone_depth",
    "cartridge_slot_present", "cartridge_slot_width", "cartridge_slot_height",
    "cartridge_slot_depth",
]


def rnd(x: float) -> float:
    """Round to 4 dp and drop a pointless trailing .0 fraction.

    4 dp keeps the deck split exact to well inside the 0.5 mm bounding-box
    tolerance the cartridge's verification asserts.
    """
    v = round(float(x), 4)
    return int(v) if v == int(v) and abs(v) < 1e9 else v



# ─────────────────────────────────────────────────────────────────────────────
# Catalog reading
# ─────────────────────────────────────────────────────────────────────────────

def read_device(obj: dict) -> dict | None:
    """Project a reference object onto `derive()`'s input shape, or None.

    None means the closed envelope is unresolved, which is the one thing the
    archetype cannot default around: an envelope is the whole point of a preset.
    """
    closed = state(obj, "closed")
    h, w, d = closed.get("height"), closed.get("width"), closed.get("depth")
    if h is None or w is None or d is None:
        return None
    src = {
        "slug": obj["key"],
        "deck_length": float(h),     # closed.height == the LONG axis
        "deck_depth": float(w),
        "closed_thickness": float(d),
        "primary_screen": display(obj, "primary"),
        "secondary_screen": display(obj, "secondary"),
        "face_button_count": control_count(obj, "abxy"),
        "stick_count": control_count(obj, "stick"),
        "shoulder_button_count": control_count(obj, "bumper"),
        "menu_button_count": control_count(obj, "button"),
        "usb_c_present": has_port(obj, "usb_c"),
        "headphone_present": has_port(obj, "headphone_3_5"),
    }
    roles = {d.get("role") for d in obj.get("displays") or []}
    if is_sourced(obj, "displays") and roles == {"primary"}:
        src["secondary_screen_present"] = False
        src["_preset_mode"] = "configurable_screens"
    return src


# ─────────────────────────────────────────────────────────────────────────────
# The one derivation path: envelope + screens + counts -> parameter values
# ─────────────────────────────────────────────────────────────────────────────

def derive(src: dict, *, full: bool) -> tuple[dict, list[str]]:
    """Return (values, fallbacks).

    `full=True` returns every parameter (used for the cartridge defaults);
    `full=False` returns only the preset-carried subset, omitting any parameter
    whose catalog input was null.

    `fallbacks` names the groups that fell back to an archetype default because
    the catalog had no value, so docs/README.md can print them per preset.
    """
    R = ARCHETYPE_RULES
    fallbacks: list[str] = []
    v: dict = {}

    L = float(src["deck_length"])
    D = float(src["deck_depth"])
    T = float(src["closed_thickness"])
    published_depth = D
    single = src.get("secondary_screen_present") is False

    # ── L0 envelope ──────────────────────────────────────────────────────────
    v["deck_length"] = rnd(L)
    v["deck_depth"] = rnd(D)
    t_upper = round(T * R["upper_deck_fraction"], 4)
    t_lower = round(T - t_upper, 4)          # the SUM is the sourced number
    v["upper_deck_thickness"] = rnd(t_upper)
    v["lower_deck_thickness"] = rnd(t_lower)
    v["deck_center_y"] = rnd(D / 2.0)
    v["lower_deck_center_z"] = rnd(-t_lower / 2.0)
    v["upper_deck_center_z"] = rnd(t_upper / 2.0)

    # ── L1 screens ───────────────────────────────────────────────────────────
    primary = src.get("primary_screen")
    secondary = src.get("secondary_screen")
    if primary is None:
        fallbacks.append("primary display active area")
        pw, ph = (L * .72, published_depth * .50) if single else ARCHETYPE_BASE["primary_screen"]
    else:
        pw, ph = primary[0], primary[1]
    if secondary is None:
        if single:
            fallbacks.append("single-screen control layout (archetype)")
            sw, sh = L * .20, published_depth * .20
        else:
            fallbacks.append("secondary display active area")
            sw, sh = ARCHETYPE_BASE["secondary_screen"]
    else:
        sw, sh = secondary[0], secondary[1]

    recess = R["screen_recess_depth"]
    if primary is not None or full or single:
        v["primary_screen_width"] = rnd(pw)
        v["primary_screen_height"] = rnd(ph)
        v["primary_screen_center_y"] = rnd(D / 2.0)
        v["primary_screen_cut_center_z"] = rnd(recess / 2.0)
    if secondary is not None or full or single:
        v["secondary_screen_width"] = rnd(sw)
        v["secondary_screen_height"] = rnd(sh)
        v["secondary_screen_center_y"] = rnd(D / 2.0)
        v["secondary_screen_cut_center_z"] = rnd(-recess / 2.0)

    # ── L0 hinge ─────────────────────────────────────────────────────────────
    # The relief pocket must clear the barrel, stay inside the thinner deck, and
    # stop short of both screen windows. Both caps use screen numbers, so the
    # hinge is generated after the screens.
    rear_bezel = min((D - ph) / 2.0, (D - sh) / 2.0)
    relief_by_thickness = R["barrel_thickness_ratio"] * min(t_upper, t_lower) \
        + R["hinge_running_clearance"]
    relief_by_bezel = rear_bezel - R["rear_bezel_margin"]
    relief = round(min(relief_by_thickness, relief_by_bezel), 4)
    barrel = round(relief - R["hinge_running_clearance"], 4)
    if barrel <= 0.5:
        raise DeriveError(
            f"{src['slug']}: hinge barrel would be {barrel} mm — the hinge-side "
            f"bezel ({rear_bezel} mm) leaves no room. Not modelled."
        )
    if relief >= min(t_upper, t_lower):
        raise DeriveError(
            f"{src['slug']}: hinge relief {relief} mm reaches through the "
            f"{min(t_upper, t_lower)} mm deck. Not modelled."
        )
    v["hinge_barrel_radius"] = rnd(barrel)
    v["hinge_relief_radius"] = rnd(relief)

    hinge_run = L * R["hinge_span_ratio"]
    knuckle_len = L * R["knuckle_length_ratio"]
    count = R["hinge_knuckle_count"]
    v["hinge_relief_span"] = rnd(hinge_run + 2.0 * R["hinge_running_clearance"])
    v["hinge_knuckle_length"] = rnd(knuckle_len)
    v["hinge_knuckle_pitch"] = rnd((hinge_run - knuckle_len) / (count - 1))
    v["hinge_knuckle_start_x"] = rnd(-(hinge_run - knuckle_len) / 2.0)

    # ── L2 controls ──────────────────────────────────────────────────────────
    cluster_x = L * .24 if single else sw / 2.0 + R["control_margin"]
    centre_y = D / 2.0
    front_row_y = min(centre_y + sh / 2.0 + R["front_row_gap"],
                      D - R["edge_margin"])

    v["dpad_center_x"] = rnd(-cluster_x)
    v["dpad_center_y"] = rnd(centre_y)
    v["face_button_center_x"] = rnd(cluster_x)
    v["face_button_center_y"] = rnd(centre_y)

    face_n = src.get("face_button_count")
    if face_n is None:
        fallbacks.append("face-button count")
        face_n = 2 if single else ARCHETYPE_BASE["face_button_count"]
    if face_n is not None or full:
        v["face_button_count"] = int(face_n)
        v["face_button_spacing_deg"] = rnd(360.0 / int(face_n))

    stick_n = src.get("stick_count")
    if stick_n is None:
        fallbacks.append("stick count")
        stick_n = 0 if single else ARCHETYPE_BASE["stick_count"]
    v["stick_count"] = int(stick_n)
    v["stick_first_center_x"] = rnd(-cluster_x)
    v["stick_pitch_x"] = rnd(2.0 * cluster_x)
    v["stick_center_y"] = rnd(centre_y - R["stick_offset_y"])

    shoulder_n = src.get("shoulder_button_count")
    if shoulder_n is None:
        fallbacks.append("shoulder-button count")
        shoulder_n = ARCHETYPE_BASE["shoulder_button_count"]
    shoulder_width = min(R["shoulder_button_width"], L * .18) if single else R["shoulder_button_width"]
    shoulder_gap = min(R["shoulder_gap"], L * .02) if single else R["shoulder_gap"]
    shoulder_x = hinge_run / 2.0 + shoulder_gap + shoulder_width / 2.0
    if single:
        v["shoulder_button_width"] = rnd(shoulder_width)
    if shoulder_x + shoulder_width / 2.0 > L / 2.0:
        raise DeriveError(
            f"{src['slug']}: shoulder cut would run off the {L} mm deck end."
        )
    v["shoulder_button_count"] = int(shoulder_n)
    v["shoulder_button_first_center_x"] = rnd(-shoulder_x)
    v["shoulder_button_pitch_x"] = rnd(2.0 * shoulder_x)
    # Straddles the rear face (y = 0) rather than sitting flush against it, so
    # the cut never presents a face coincident with the deck's — the tool bites
    # shoulder_button_depth / 2 into real material.
    v["shoulder_button_center_y"] = 0

    menu_n = src.get("menu_button_count")
    if menu_n is None:
        fallbacks.append("menu-button count")
        menu_n = ARCHETYPE_BASE["menu_button_count"]
    menu_n = int(menu_n)
    menu_span = R["menu_button_pitch"] * max(menu_n - 1, 0)
    v["menu_button_count"] = menu_n
    v["menu_button_first_center_x"] = rnd(cluster_x - menu_span / 2.0)
    v["menu_button_pitch_x"] = rnd(R["menu_button_pitch"])
    v["menu_button_center_y"] = rnd(front_row_y)

    speaker_span = R["speaker_hole_pitch"] * (R["speaker_hole_count"] - 1)
    v["speaker_first_center_x"] = rnd(-cluster_x - speaker_span / 2.0)
    v["speaker_center_y"] = rnd(front_row_y)

    # ── L2 ports ─────────────────────────────────────────────────────────────
    v["usb_c_center_x"] = 0
    v["usb_c_center_y"] = rnd(D)
    v["usb_c_center_z"] = rnd(-t_lower / 2.0)
    v["headphone_center_x"] = rnd(-L * R["headphone_offset_x"])
    v["headphone_center_y"] = rnd(D)
    v["headphone_center_z"] = rnd(-t_lower / 2.0)
    v["cartridge_slot_center_x"] = rnd(L * (.25 if single else R["cartridge_slot_offset_x"]))
    v["cartridge_slot_center_y"] = rnd(D)
    v["cartridge_slot_center_z"] = rnd(-t_lower / 2.0)
    for key in ("usb_c_present", "headphone_present"):
        flag = src.get(key)
        if flag is None:
            fallbacks.append(key.replace("_present", "").replace("_", "-") + " port")
            flag = False if single else ARCHETYPE_BASE[key]
        v[key] = bool(flag)

    if full or single:
        v["secondary_screen_present"] = not single
    if not full:
        order = PRESET_PARAM_ORDER + (["secondary_screen_present", "shoulder_button_width"] if single else [])
        return {k: v[k] for k in order if k in v}, fallbacks

    # ── archetype-only parameters (defaults emission) ────────────────────────
    v["corner_radius"] = rnd(R["corner_radius"])
    v["fold_angle"] = rnd(R["fold_angle"])
    v["screen_recess_depth"] = rnd(recess)
    v["control_recess_depth"] = rnd(R["control_recess_depth"])
    v["control_cut_center_z"] = rnd(-R["control_recess_depth"] / 2.0)
    v["hinge_knuckle_count"] = int(count)
    v["hinge_clip_span"] = rnd(R["hinge_clip_span"])
    v["hinge_clip_center_y"] = rnd(-R["hinge_clip_span"] / 2.0)
    v["dpad_arm_length"] = rnd(R["dpad_arm_length"])
    v["dpad_arm_width"] = rnd(R["dpad_arm_width"])
    v["face_button_circle_radius"] = rnd(R["face_button_circle_radius"])
    v["face_button_radius"] = rnd(R["face_button_radius"])
    v["stick_radius"] = rnd(R["stick_radius"])
    v["menu_button_radius"] = rnd(R["menu_button_radius"])
    v["shoulder_button_width"] = rnd(shoulder_width)
    v["shoulder_button_depth"] = rnd(R["shoulder_button_depth"])
    v["shoulder_button_height"] = rnd(R["shoulder_button_height"])
    v["shoulder_button_center_z"] = rnd(-t_lower / 2.0)
    v["speaker_hole_count"] = int(R["speaker_hole_count"])
    v["speaker_hole_radius"] = rnd(R["speaker_hole_radius"])
    v["speaker_hole_pitch"] = rnd(R["speaker_hole_pitch"])
    v["usb_c_width"] = rnd(R["usb_c_width"])
    v["usb_c_height"] = rnd(R["usb_c_height"])
    v["usb_c_depth"] = rnd(R["usb_c_depth"])
    v["headphone_radius"] = rnd(R["headphone_radius"])
    v["headphone_depth"] = rnd(R["headphone_depth"])
    v["cartridge_slot_present"] = True
    v["cartridge_slot_width"] = rnd(R["cartridge_slot_width"])
    v["cartridge_slot_height"] = rnd(R["cartridge_slot_height"])
    v["cartridge_slot_depth"] = rnd(R["cartridge_slot_depth"])
    order = PRESET_PARAM_ORDER + ARCHETYPE_ONLY_PARAMS
    return {k: v[k] for k in order if k in v}, fallbacks


#: Objects filed in this family whose archetype they do not quite obey.
CAVEATS = {
    "nintendo-2ds": (
        "Nintendo describes this model as \"a new distinctive fixed slate form "
        "design\"; it does not fold. Its reference object has every hinge field "
        "null, and the family's compilation report of 2026-09-13 proposed moving it "
        "to a slate-dual-screen-handheld family. The preset therefore pins "
        "fold_angle to 0 and carries the envelope only — the archetype's fold "
        "is not a claim about this device."
    ),
}

def _single_screen_archetype():
    values, _ = derive(dict(ARCHETYPE_BASE, secondary_screen_present=False), full=False)
    return {"slug": "archetype-single-screen", "kind": "archetype", "mode": "configurable_screens",
        "label": {"en": "Archetype — single screen", "es": "Arquetipo — una pantalla"},
        "source": "Original single-screen clamshell, not a product. Closed envelope includes its rear hinge; control layout and unknown features are explicit archetype rules.",
        "values": values}


FAMILY = Family(
    slug="clamshell-dual-screen-handheld",
    base=ARCHETYPE_BASE,
    read=read_device,
    derive=derive,
    axis_mapping={
        "deck_length": "reference dimensions_mm.states.closed.height (the long axis, the hinge axis)",
        "deck_depth": "reference dimensions_mm.states.closed.width (the folding axis)",
        "upper_deck_thickness + lower_deck_thickness": "reference dimensions_mm.states.closed.depth",
    },
    source_line="envelope closed height x width x depth as published.",
    caveats=CAVEATS,
    extra_presets=[_single_screen_archetype()],
)
