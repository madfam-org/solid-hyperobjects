"""Disc media: archetype, rules, standard-part and catalog readers, derivation.

A revolved disc, optionally in a shell with a window, a read slot and a shutter.

WHERE THE NUMBERS COME FROM
---------------------------
  STANDARD   the keystone's standard parts (`hyperobjects_standard_parts`):
             `optical-disc-cd-120mm` (ECMA-130), `optical-disc-dvd-120mm` (ECMA-267),
             `umd-cartridge` (ECMA-365). Each becomes a preset of `kind: standard_part`
             whose source line names the part, its governing standard and its digest.
  CATALOG    proprietary or non-standard formats (GD-ROM, the 8 cm GameCube disc, the
             Wii disc, the Quick Disk, the 64DD disk) are reference objects of family
             `disc-media` (brief §3: `features.diameter_mm`, `thickness_mm`, `hole_mm`,
             `shell`, plus `dimensions_mm.states.shell`). The pinned catalog files none
             yet; each one filed becomes a preset at the next generator run.
  ARCHETYPE  ours: the default square-shell disc, and every window, slot and shutter.

AXIS MAPPING
------------
    standard diameter / centre_hole_diameter / thickness -> disc_diameter / disc_hole / disc_thickness
    standard clamping zone inner max / outer min         -> clamp_inner / clamp_outer_diameter
    standard total height max - thickness (DERIVED)      -> ring_height
    reference dimensions_mm.states.shell.width / height / depth
                                                         -> shell_width (X) / shell_length (Y) / shell_thickness (Z)
"""
from __future__ import annotations

from common import DeriveError, Family, rnd, state

# ─────────────────────────────────────────────────────────────────────────────
# The archetype. Every number below is OURS.
# ─────────────────────────────────────────────────────────────────────────────

#: The family default: a disc in a square shell that is no product.
ARCHETYPE_BASE = {
    "slug": "__archetype__",
    "diameter": 70.0, "hole": 10.0, "thickness": 1.0,
    "clamp_inner": 18.0, "clamp_outer": 24.0, "clamp_relief": 0.1, "ring_height": 0.2,
    "shell": {"outline": "rounded_rect", "width": 80.0, "length": 84.0, "thickness": 5.0,
              "corner_radius": 3.0, "top_arc_radius": None, "bottom_arc_radius": None,
              "boss_diameter": 0.0, "boss_height": 0.0, "disc_center_y": 2.0},
}

ARCHETYPE_RULES = {
    "ring_width": 1.0,             # the stacking ring's radial width
    "hole_ratio": 15.0 / 120.0,    # a hole scaled from the 120 mm standards, when unsourced
    "clamp_inner_ratio": 26.0 / 120.0, "clamp_outer_ratio": 33.0 / 120.0,
    "pocket_clearance": 0.3,
    "window_width_ratio": 0.5, "window_length_ratio": 0.25, "window_offset_ratio": 0.2,
    "read_slot_width_ratio": 0.17, "read_slot_length_ratio": 0.3, "spindle_ratio": 0.17,
    "shutter_overlap": 2.0, "shutter_thickness": 0.5,
    "corner_radius": 3.0,          # a rounded-rectangle shell, when unsourced
    "top_arc_ratio": 0.5, "bottom_arc_ratio": 1.25,   # unused unless outline is arched
}

PRESET_PARAM_ORDER = [
    "disc_diameter", "disc_hole", "disc_thickness", "clamp_inner_diameter",
    "clamp_outer_diameter", "clamp_relief", "ring_width", "ring_height",
    "shell_present", "shell_outline", "shell_width", "shell_length", "shell_thickness",
    "shell_corner_radius", "shell_top_arc_radius", "shell_bottom_arc_radius",
    "shell_boss_diameter", "shell_boss_height", "disc_center_y",
    "window_width", "window_length", "window_offset_y", "read_slot_width",
    "read_slot_length", "spindle_diameter", "shutter_overlap", "shutter_thickness",
]
ARCHETYPE_ONLY_PARAMS = ["pocket_clearance", "shutter_open"]
#: Parameters a bare disc's preset carries (a shell is never claimed for it).
DISC_ONLY = PRESET_PARAM_ORDER[:9]


# ─────────────────────────────────────────────────────────────────────────────
# Readers
# ─────────────────────────────────────────────────────────────────────────────

def _std(part: dict, name: str):
    d = (part.get("dimensions") or {}).get(name)
    return None if d is None else float(d["value"])


def read_standard_part(key: str) -> dict:
    """A standard disc (or disc cartridge) projected onto derive()'s input."""
    from hyperobjects_standard_parts import load_part

    part = load_part(key)
    if key == "umd-cartridge":
        length, width = _std(part, "case_length"), _std(part, "case_width")
        top_r = _std(part, "top_arc_radius")
        return {
            "slug": key, "diameter": _std(part, "disc_diameter"), "hole": None,
            "thickness": _std(part, "disc_thickness"),
            "clamp_inner": None, "clamp_outer": None, "clamp_relief": 0.0, "ring_height": 0.0,
            "shell": {
                "outline": "arched", "width": width, "length": length,
                "thickness": _std(part, "case_thickness"),
                "corner_radius": _std(part, "bottom_corner_radius"),
                "top_arc_radius": top_r, "bottom_arc_radius": _std(part, "bottom_arc_radius"),
                # ECMA-365: 4.35 max inside the D1 = 50 mm circle about the disc centre.
                "boss_diameter": 50.0,
                "boss_height": _std(part, "case_thickness_max") - _std(part, "case_thickness"),
                # The top arc is "about the disc": its centre is the disc centre.
                "disc_center_y": length / 2.0 - top_r,
            },
        }
    thick = _std(part, "substrate_thickness") or _std(part, "thickness")
    rim = _std(part, "rim_height_max") or _std(part, "rim_thickness_max")
    return {
        "slug": key, "diameter": _std(part, "diameter"),
        "hole": _std(part, "centre_hole_diameter"), "thickness": thick,
        "clamp_inner": (_std(part, "clamping_area_inner_diameter_max")
                        or _std(part, "clamping_zone_inner_diameter_max")),
        "clamp_outer": (_std(part, "clamping_area_outer_diameter_min")
                        or _std(part, "clamping_zone_outer_diameter_min")),
        "clamp_relief": 0.0,
        "ring_height": (rim - thick) if rim is not None else None,
        "shell": None,
    }


def read_disc(obj: dict) -> dict | None:
    """A catalog object projected onto derive()'s input, or None (unresolved)."""
    from hyperobjects_reference import is_sourced

    if obj.get("kind") == "edition":
        from _edition_disc import read_edition_disc
        return read_edition_disc(obj)
    f = obj.get("features") or {}

    def feat(name):
        v = f.get(name)
        return None if v is None or not is_sourced(obj, f"features.{name}") else v

    dia, thick = feat("diameter_mm"), feat("thickness_mm")
    if dia is None or thick is None:
        return None
    src = {"slug": obj["key"], "diameter": float(dia), "hole": feat("hole_mm"),
           "thickness": float(thick), "clamp_inner": None, "clamp_outer": None,
           "clamp_relief": 0.0, "ring_height": 0.0, "shell": None}
    if feat("shell"):
        sh = state(obj, "shell")
        w, h, d = sh.get("width"), sh.get("height"), sh.get("depth")
        if w is None or h is None or d is None:
            return None
        src["shell"] = {"outline": "rounded_rect", "width": float(w), "length": float(h),
                        "thickness": float(d), "corner_radius": None,
                        "top_arc_radius": None, "bottom_arc_radius": None,
                        "boss_diameter": 0.0, "boss_height": 0.0, "disc_center_y": None}
    return src


# ─────────────────────────────────────────────────────────────────────────────
# The one derivation path
# ─────────────────────────────────────────────────────────────────────────────

def derive(src: dict, *, full: bool) -> tuple[dict, list[str]]:
    if src.get("_preset_mode") == "envelope":
        from _edition_disc import derive_diameter_proxy
        return derive_diameter_proxy(src)
    R = ARCHETYPE_RULES
    fb: list[str] = []
    v: dict = {}
    D, t = float(src["diameter"]), float(src["thickness"])
    hole = src.get("hole")
    if hole is None:
        fb.append("centre hole (scaled from the 120 mm standards)")
        hole = R["hole_ratio"] * D
    ci, co = src.get("clamp_inner"), src.get("clamp_outer")
    if ci is None or co is None:
        fb.append("clamp zone (scaled from the 120 mm standards)")
        ci, co = R["clamp_inner_ratio"] * D, R["clamp_outer_ratio"] * D
    ring_h = src.get("ring_height")
    if ring_h is None:
        fb.append("stacking ring")
        ring_h = 0.0
    if not (0 <= hole < ci < co and co + 2.0 * R["ring_width"] < D):
        raise DeriveError(f"{src['slug']}: hole {hole} / clamp {ci}-{co} / diameter {D} "
                          "do not nest. Not modelled.")
    v.update({
        "disc_diameter": rnd(D), "disc_hole": rnd(hole), "disc_thickness": rnd(t),
        "clamp_inner_diameter": rnd(ci), "clamp_outer_diameter": rnd(co),
        "clamp_relief": rnd(src.get("clamp_relief") or 0.0),
        "ring_width": rnd(R["ring_width"]), "ring_height": rnd(ring_h),
    })

    shell = src.get("shell")
    v["shell_present"] = shell is not None
    if shell is None and not full:
        return {k: v[k] for k in DISC_ONLY}, fb
    sh = shell or ARCHETYPE_BASE["shell"]
    W, L, T = float(sh["width"]), float(sh["length"]), float(sh["thickness"])
    corner = sh.get("corner_radius")
    if corner is None:
        fb.append("shell corner radius")
        corner = R["corner_radius"]
    dcy = sh.get("disc_center_y")
    if dcy is None:
        fb.append("disc position in the shell (centred)")
        dcy = 0.0
    v.update({
        "shell_outline": sh["outline"], "shell_width": rnd(W), "shell_length": rnd(L),
        "shell_thickness": rnd(T), "shell_corner_radius": rnd(corner),
        "shell_top_arc_radius": rnd(sh.get("top_arc_radius") or R["top_arc_ratio"] * W),
        "shell_bottom_arc_radius": rnd(sh.get("bottom_arc_radius") or R["bottom_arc_ratio"] * W),
        "shell_boss_diameter": rnd(sh.get("boss_diameter") or 0.0),
        "shell_boss_height": rnd(sh.get("boss_height") or 0.0),
        "disc_center_y": rnd(dcy),
        "window_width": rnd(R["window_width_ratio"] * D),
        "window_length": rnd(R["window_length_ratio"] * D),
        "window_offset_y": rnd(R["window_offset_ratio"] * D),
        "read_slot_width": rnd(R["read_slot_width_ratio"] * D),
        "read_slot_length": rnd(R["read_slot_length_ratio"] * D),
        "spindle_diameter": rnd(R["spindle_ratio"] * D),
        "shutter_overlap": rnd(R["shutter_overlap"]),
        "shutter_thickness": rnd(R["shutter_thickness"]),
    })
    pocket_h = t + ring_h + 2.0 * R["pocket_clearance"]
    if (T - pocket_h) / 2.0 <= R["shutter_thickness"] + 0.35:
        raise DeriveError(f"{src['slug']}: a {T} mm shell leaves no floor under a "
                          f"{pocket_h} mm pocket for the shutter track. Not modelled.")
    if shell is not None:
        fb.append("window, read slot and shutter")
    if not full:
        return {k: v[k] for k in PRESET_PARAM_ORDER}, fb
    v["pocket_clearance"] = rnd(R["pocket_clearance"])
    v["shutter_open"] = 0
    return {k: v[k] for k in PRESET_PARAM_ORDER + ARCHETYPE_ONLY_PARAMS}, fb


# ─────────────────────────────────────────────────────────────────────────────
# Presets that are not catalog objects
# ─────────────────────────────────────────────────────────────────────────────

STANDARD_PRESETS = [
    ("optical-disc-cd-120mm", "disc", "CD, 120 mm (ECMA-130)", "CD de 120 mm (ECMA-130)"),
    ("optical-disc-dvd-120mm", "disc", "DVD, 120 mm (ECMA-267)", "DVD de 120 mm (ECMA-267)"),
    ("umd-cartridge", "shell", "UMD cartridge (ECMA-365)", "Cartucho UMD (ECMA-365)"),
]


def _standard_presets() -> list[dict]:
    from hyperobjects_standard_parts import load_part, part_digest

    out = []
    for key, mode, en, es in STANDARD_PRESETS:
        part = load_part(key)
        values, fb = derive(read_standard_part(key), full=False)
        out.append({
            "slug": f"standard-{key}",
            "label": {"en": en, "es": es},
            "kind": "standard_part",
            "mode": mode,
            "source": (f"hyperobjects-spec standard part `{key}` "
                       f"({part['governing']['designation']}); dimensions as the standard "
                       "states them, read through hyperobjects_standard_parts. Generated by "
                       "tools/presets/presets.py — do not edit by hand."),
            "standard_part": {"key": key, "digest": part_digest(part),
                              "archetype_fallbacks": fb},
            "values": values,
        })
    return out


def _archetype_presets() -> list[dict]:
    values, _ = derive(ARCHETYPE_BASE, full=False)
    what_en = "a disc in a square shell with a window, a read slot and a sliding shutter."
    what_es = "un disco en una carcasa cuadrada con ventana, ranura de lectura y compuerta corrediza."
    return [{
        "slug": "archetype-square-shell-disc",
        "label": {"en": "Archetype — square-shell disc", "es": "Arquetipo — disco en carcasa cuadrada"},
        "kind": "archetype",
        "mode": "shell",
        "source": ("Archetype, not a product: " + what_en + " Every number is the family's "
                   "own rule (tools/presets/disc_media.py). Generated by "
                   "tools/presets/presets.py — do not edit by hand."),
        "description": {"en": what_en, "es": what_es},
        "values": values,
    }]


def registry_extra(obj: dict, values: dict) -> dict:
    if obj.get("kind") == "edition":
        from _edition_disc import edition_disc_registry
        return edition_disc_registry(obj)
    return {"host_console": (obj.get("features") or {}).get("host_console")}


FAMILY = Family(
    slug="disc-media",
    base=ARCHETYPE_BASE,
    read=read_disc,
    derive=derive,
    axis_mapping={
        "disc_diameter / disc_hole / disc_thickness": "standard part dimensions, or reference features.diameter_mm / hole_mm / thickness_mm",
        "ring_height": "standard total height max - thickness (derived); 0 for a catalog object",
        "shell_width": "reference dimensions_mm.states.shell.width (X)",
        "shell_length": "reference dimensions_mm.states.shell.height (Y)",
        "shell_thickness": "reference dimensions_mm.states.shell.depth (Z)",
    },
    source_line="catalog format dimensions as published; exact edition proxies source only the carrier diameter and declare authored thickness.",
    registry_extra=registry_extra,
    extra_presets=_standard_presets() + _archetype_presets(),
    supplemental_keys=(
        "nintendo-gamecube-the-legend-of-zelda-twilight-princess-jp",
        "nintendo-wii-the-legend-of-zelda-twilight-princess-jp",
    ),
)
