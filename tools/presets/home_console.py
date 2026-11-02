"""The home console: archetype, rules, catalog reader, derivation.

One parametric desktop console from the Magnavox Odyssey to the PS5: a lofted body
(slab, wedge, stepped, tower, cube, upright), its media interface (cartridge, card,
lid, tray, slot or none), console panel, controller and rear I/O, two vent fields
and the support (feet, stand seat, handle). The fact contract it reads is the
`home-console` section of the gaming-lanes brief §3 (kind `device`).

AXIS MAPPING
------------
    reference dimensions_mm.states.body.width   -> body_width   (X)
    reference dimensions_mm.states.body.depth   -> body_depth   (Y, front -> rear)
    reference dimensions_mm.states.body.height  -> body_height  (Z, feet down)

A console published only standing up (`states.vertical`, no `body`) is laid on its
side: body_width = vertical.height, body_height = vertical.width, body_depth =
vertical.depth, and orientation_tilt_deg = 90 stands it back up, so the envelope
box is the published vertical box.

WHAT IS OURS
------------
The BODY PLAN is never a fact: no maker publishes "stepped". It is chosen by
`plan_rule` from the sourced envelope, media, handle and display only, and every
shaping number (radii, tier, crown, vents, panel layout) is an archetype rule
below. A preset therefore asserts the maker's envelope, counts and kinds, and
nothing about the shape between them (trade-dress ruling R3).
"""
from __future__ import annotations

import json

from common import DeriveError, Family, is_sourced, rnd, state

ARCHETYPE_BASE = {
    "slug": "__archetype__",
    "body_width": 310.0, "body_depth": 190.0, "body_height": 62.0,
    "orientation_tilt_deg": 0.0, "role": "console", "body_plan": "stepped",
    "media_kind": "cart_top", "slot_door_kind": "flaps",
    "controller_port_count": 2, "controller_port_kind": "proprietary",
    "controller_port_face": "front", "hardwired_controllers": 0, "controller_bays": 0,
    "power_control": "slide", "reset_present": True, "eject_button": False,
    "panel_switch_count": 0, "front_button_count": 0, "memory_card_count": 0,
    "av_out_kind": "rca", "av_out_count": 1, "power_inlet_kind": "barrel",
    "expansion_port_count": 0, "expansion_port_face": "bottom", "network_port": False,
    "usb_port_count_front": 0, "usb_port_count_rear": 0, "channel_switch": False,
    "screen": None, "handle_present": False, "stand_seat_kind": "none",
    "side_cover_count": 0, "disc_diameter": 120.0,
}

ARCHETYPE_RULES = {
    "corner_radius_vertical_ratio": 0.06,   # of min(W, D)
    "corner_radius_top_ratio": 0.08,        # of H
    "edge_chamfer": 1.0,
    "wall_thickness": 2.5,
    "seam_height_ratio": 0.45,
    "seam_groove": 0.8,
    "tier_height_ratio": 0.38,              # stepped: of H
    "tier_inset_x_ratio": 0.12,             # of W
    "tier_inset_y_ratio": 0.08,             # of D, from the rear
    "front_break_ratio": 0.35,              # of D, from the front
    "wedge_front_ratio": 0.55,              # wedge: front height / H
    "upright_rear_ratio": 0.45,             # upright: rear height / H
    "side_cover_thickness": 6.0, "side_cover_overhang": 4.0,
    "cart_media": (120.0, 18.0, 60.0),      # width, thickness, insertion depth
    "card_media": (54.0, 2.0, 50.0),
    "slot_clearance": 1.0,
    "lid_margin": 12.0, "tray_height": 14.0,
    "panel_switch_pitch": 28.0, "panel_led_count": 1,
    "controller_port_pitch": 30.0, "cord_diameter": 6.0,
    "bay_width": 60.0, "bay_length_ratio": 0.7, "bay_depth": 18.0,
    "vent_pattern": "slots", "vent_pitch": 6.0, "vent_hole": 3.0, "vent_depth": 4.0,
    "foot_count": 4, "foot_diameter": 12.0, "foot_height": 3.0,
    "handle_span_ratio": 0.6, "handle_reach": 22.0, "handle_thickness": 10.0,
}

#: Parameters a preset may carry, in the order they are written.
PRESET_PARAM_ORDER = [
    "body_width", "body_depth", "body_height", "orientation_tilt_deg", "role", "body_plan",
    "front_height", "rear_height", "crown", "side_draft_deg", "plan_skew_deg",
    "front_break_y", "upper_tier_height", "upper_tier_inset_x", "upper_tier_inset_y",
    "side_concavity", "corner_radius_vertical", "corner_radius_top",
    "side_cover_count", "media_kind", "media_width", "media_thickness",
    "media_insert_depth", "slot_center_x", "slot_center_y", "slot_center_z", "slot_door_kind",
    "disc_diameter", "lid_diameter", "lid_center_x", "lid_center_y", "tray_width",
    "tray_height", "tray_center_z", "eject_button", "memory_card_count",
    "screen_present", "screen_width", "screen_height", "screen_center_z",
    "power_control", "reset_present", "panel_switch_count", "panel_center_y",
    "front_button_count", "controller_port_count", "controller_port_kind",
    "controller_port_face", "controller_port_center_z", "hardwired_controllers",
    "controller_bays", "bay_length", "av_out_kind", "av_out_count", "power_inlet_kind",
    "expansion_port_count", "expansion_port_face", "network_port", "usb_port_count_front",
    "usb_port_count_rear", "channel_switch", "rear_port_center_z",
    "vent1_face", "vent1_center_u", "vent1_center_v", "vent1_width", "vent1_height",
    "vent2_face", "vent2_center_u", "vent2_center_v", "vent2_width", "vent2_height",
    "foot_count", "foot_diameter", "stand_seat_kind", "handle_present", "handle_span",
]

ARCHETYPE_ONLY_PARAMS = [
    "edge_chamfer", "wall_thickness", "seam_height_ratio", "seam_groove",
    "side_cover_thickness", "side_cover_overhang", "side_cover_offset", "slot_clearance",
    "lid_angle", "tray_extension", "panel_switch_pitch", "panel_led_count",
    "controller_port_pitch", "cord_diameter", "bay_width", "bay_depth",
    "vent1_pattern", "vent1_pitch", "vent1_hole_size", "vent1_depth",
    "vent2_pattern", "vent2_pitch", "vent2_hole_size", "vent2_depth",
    "foot_height", "handle_reach", "handle_thickness",
]

MEDIA_KIND = {
    "cartridge_top": "cart_top", "cartridge_front": "cart_front",
    "cartridge_rear": "cart_rear", "card_front": "card_front", "disc_lid": "disc_lid",
    "disc_tray": "disc_tray", "disc_slot": "disc_slot", "none": "none",
}
AV_PRIORITY = [("hdmi", "hdmi"), ("multi_av_out", "multi_av"), ("component_out", "rca"),
               ("composite_out", "rca"), ("s_video_out", "rca"), ("rf_out", "rf_f")]
CONTROLLER_KINDS = [("controller_de9", "de9"), ("controller_proprietary", "proprietary"),
                    ("controller_usb_a", "usb_a")]
POWER_INLET = {"hardwired_cord": "cord", "barrel": "barrel", "iec_c7": "iec_c7",
               "iec_c8": "iec_c8", "iec_c13": "iec_c13", "proprietary": "proprietary"}


# ─────────────────────────────────────────────────────────────────────────────
# Catalog reading
# ─────────────────────────────────────────────────────────────────────────────

def _kinds(obj: dict, field: str):
    """{kind: count} for a covered list, or None when the list is not sourced."""
    if not is_sourced(obj, field):
        return None
    out = {}
    for item in obj.get(field) or []:
        out[item["kind"]] = item.get("count")
    return out


def read_device(obj: dict) -> dict | None:
    """Project a reference object onto derive()'s input, or None (no envelope)."""
    body, vert = state(obj, "body"), state(obj, "vertical")
    src = {"slug": obj["key"]}
    if all(body.get(k) is not None for k in ("width", "height", "depth")):
        src.update(body_width=float(body["width"]), body_depth=float(body["depth"]),
                   body_height=float(body["height"]), orientation_tilt_deg=0.0)
    elif all(vert.get(k) is not None for k in ("width", "height", "depth")):
        src.update(body_width=float(vert["height"]), body_depth=float(vert["depth"]),
                   body_height=float(vert["width"]), orientation_tilt_deg=90.0)
    else:
        return None
    feat = obj.get("features") or {}
    fs = lambda k: feat.get(k) if is_sourced(obj, f"features.{k}") else None  # noqa: E731
    src["role"] = fs("role")
    media = _kinds(obj, "media")
    if media is not None:
        kinds = [MEDIA_KIND[k] for k in media if k in MEDIA_KIND and k != "none"]
        if not kinds:
            src["media_kind"] = "none"
        elif "disc_lid" in kinds and "cart_top" in kinds:
            src["media_kind"] = "disc_and_cart"
        else:
            src["media_kind"] = kinds[0]
    ports = _kinds(obj, "ports")
    if ports is not None:
        for kind, sel in CONTROLLER_KINDS:
            if kind in ports:
                src["controller_port_kind"], src["controller_port_count"] = sel, ports[kind]
                break
        else:
            src["controller_port_kind"], src["controller_port_count"] = "none", 0
        for kind, sel in AV_PRIORITY:
            if kind in ports:
                src["av_out_kind"], src["av_out_count"] = sel, ports[kind] or 1
                break
        src["network_port"] = "ethernet" in ports
        src["expansion_port_count"] = ports.get("expansion", 0) if "expansion" in ports else 0
        src["usb_port_count_rear"] = ports.get("usb_a", 0) if "usb_a" in ports else 0
        src["memory_card_count"] = ports.get("memory_card", 0) if "memory_card" in ports else 0
    controls = _kinds(obj, "controls")
    if controls is not None:
        src["power_control"] = "slide" if "power_switch" in controls else "push"
        src["reset_present"] = "reset_button" in controls
        src["eject_button"] = "eject_button" in controls
        src["panel_switch_count"] = controls.get("slide_switch") or 0
        src["front_button_count"] = sum((controls.get(k) or 1) for k in
                                        ("pause_button", "select_button") if k in controls)
    for key in ("controller_bays", "hardwired_controllers"):
        if fs(key) is not None:
            src[key] = int(fs(key))
    if fs("power_inlet") in POWER_INLET:
        src["power_inlet_kind"] = POWER_INLET[fs("power_inlet")]
    if fs("handle") is not None:
        src["handle_present"] = bool(fs("handle"))
    if fs("stand_included"):
        src["stand_seat_kind"] = "base_disc"
    for d in obj.get("displays") or []:
        if d.get("role") == "integrated":
            area = d.get("active_area_mm") or {}
            if area.get("width") is not None and area.get("height") is not None:
                src["screen"] = (float(area["width"]), float(area["height"]))
    return src


# ─────────────────────────────────────────────────────────────────────────────
# Archetype rules
# ─────────────────────────────────────────────────────────────────────────────

def plan_rule(s: dict) -> str:
    """The body plan, chosen ONLY from sourced envelope, media, handle and display."""
    if s.get("screen"):
        return "upright"
    if s.get("handle_present"):
        return "cube"
    if s["orientation_tilt_deg"] >= 45.0 or s["body_height"] > s["body_width"]:
        return "tower"
    return "slab"


def _get(s: dict, key: str, fallbacks: list, label: str):
    v = s.get(key)
    if v is None:
        fallbacks.append(label)
        return ARCHETYPE_BASE[key]
    return v


def derive(src: dict, *, full: bool) -> tuple[dict, list[str]]:
    """Return (values, fallbacks): every parameter when full, else the preset subset."""
    R, fb, v = ARCHETYPE_RULES, [], {}
    W, D, H = float(src["body_width"]), float(src["body_depth"]), float(src["body_height"])
    if min(W, D, H) < 20.0:
        raise DeriveError(f"{src['slug']}: envelope {W} x {D} x {H} mm is below the family floor")
    v.update(body_width=rnd(W), body_depth=rnd(D), body_height=rnd(H),
             orientation_tilt_deg=rnd(src.get("orientation_tilt_deg", 0.0)))
    v["role"] = _get(src, "role", fb, "role")
    plan = src.get("body_plan") or plan_rule(src)
    v["body_plan"] = plan
    m = min(W, D)
    v["front_height"] = rnd(H * R["wedge_front_ratio"])
    v["rear_height"] = rnd(H * R["upright_rear_ratio"])
    v["crown"] = rnd(src.get("crown", 0.0))
    v["side_draft_deg"] = rnd(src.get("side_draft_deg", 0.0))
    v["plan_skew_deg"] = rnd(src.get("plan_skew_deg", 0.0))
    v["front_break_y"] = rnd(D * R["front_break_ratio"])
    v["upper_tier_height"] = rnd(H * R["tier_height_ratio"])
    v["upper_tier_inset_x"] = rnd(W * R["tier_inset_x_ratio"])
    v["upper_tier_inset_y"] = rnd(D * R["tier_inset_y_ratio"])
    v["side_concavity"] = rnd(src.get("side_concavity", 0.0))
    v["corner_radius_vertical"] = rnd(m * R["corner_radius_vertical_ratio"])
    v["corner_radius_top"] = rnd(min(H, W) * R["corner_radius_top_ratio"])
    covers = int(src.get("side_cover_count", 0))
    v["side_cover_count"] = covers

    # Heights the panel and the ports sit at: the front face of the body plan.
    h_front = {"wedge": H * R["wedge_front_ratio"],
               "stepped": H * (1 - R["tier_height_ratio"])}.get(plan, H)
    h_rear = {"upright": H * R["upright_rear_ratio"],
              "stepped": H * (1 - R["tier_height_ratio"])}.get(plan, H)

    # ── media ────────────────────────────────────────────────────────────────
    mk = _get(src, "media_kind", fb, "media kind")
    v["media_kind"] = mk
    mw, mt, mi = R["card_media"] if mk == "card_front" else R["cart_media"]
    mw = min(mw, W - 4 * R["wall_thickness"] - 20.0)
    mi = min(mi, 0.6 * (H if mk == "cart_top" else D))
    v.update(media_width=rnd(mw), media_thickness=rnd(mt), media_insert_depth=rnd(mi))
    tier_mid = (D * R["front_break_ratio"] + D * (1 - R["tier_inset_y_ratio"])) / 2.0
    v["slot_center_x"] = 0
    v["slot_center_y"] = rnd(tier_mid - D / 2.0 if plan == "stepped" else D * 0.15)
    v["slot_center_z"] = rnd(h_front * 0.5)
    door = src.get("slot_door_kind") or "none"
    v["slot_door_kind"] = door if mk in ("cart_top", "cart_front", "cart_rear") else "none"
    dd = float(src.get("disc_diameter", ARCHETYPE_BASE["disc_diameter"]))
    v["disc_diameter"] = rnd(dd)
    v["lid_diameter"] = rnd(min(dd + R["lid_margin"], 0.8 * m))
    v["lid_center_x"] = 0
    v["lid_center_y"] = rnd(D * 0.12 if mk == "disc_and_cart" else 0.0)
    if mk == "disc_and_cart":
        v["slot_center_y"] = rnd(-D * 0.3)
    upright_drive = H > W           # the family turns the drive on its side
    v["tray_width"] = rnd(min(dd + R["lid_margin"], (H if upright_drive else W)
                              - 4 * R["wall_thickness"] - 30.0))
    v["tray_height"] = rnd(min(R["tray_height"], 0.3 * (W if upright_drive else h_front)))
    v["tray_center_z"] = rnd(H * 0.6 if upright_drive else h_front * 0.55)
    v["eject_button"] = bool(_get(src, "eject_button", fb, "eject button")) \
        if mk in ("disc_tray", "disc_slot", "disc_lid") else bool(src.get("eject_button", False))
    v["memory_card_count"] = int(_get(src, "memory_card_count", fb, "memory-card count"))

    # ── integrated display (the Vectrex) ─────────────────────────────────────
    screen = src.get("screen")
    v["screen_present"] = bool(screen)
    sw, sh = screen or (W * 0.7, H * 0.55)
    v.update(screen_width=rnd(sw), screen_height=rnd(sh), screen_center_z=rnd(H * 0.55))

    # ── panel, controller and rear I/O ──────────────────────────────────────
    v["power_control"] = _get(src, "power_control", fb, "power control")
    v["reset_present"] = bool(_get(src, "reset_present", fb, "reset button"))
    v["panel_switch_count"] = int(src.get("panel_switch_count", 0))
    v["panel_center_y"] = rnd(D * R["front_break_ratio"] / 2.0)
    v["front_button_count"] = int(src.get("front_button_count", 0))
    cpk = _get(src, "controller_port_kind", fb, "controller ports")
    v["controller_port_count"] = int(_get(src, "controller_port_count", fb, "controller-port count"))
    if cpk == "none":
        v["controller_port_count"] = 0
    v["controller_port_kind"] = cpk
    v["controller_port_face"] = src.get("controller_port_face", "front")
    v["controller_port_center_z"] = rnd(h_front * 0.3)
    v["hardwired_controllers"] = int(src.get("hardwired_controllers", 0))
    v["controller_bays"] = int(src.get("controller_bays", 0))
    v["bay_length"] = rnd(D * R["bay_length_ratio"])
    v["av_out_kind"] = _get(src, "av_out_kind", fb, "AV output")
    v["av_out_count"] = int(src.get("av_out_count", ARCHETYPE_BASE["av_out_count"]))
    v["power_inlet_kind"] = _get(src, "power_inlet_kind", fb, "power inlet")
    v["expansion_port_count"] = int(_get(src, "expansion_port_count", fb, "expansion-port count"))
    v["expansion_port_face"] = src.get("expansion_port_face", "bottom")
    v["network_port"] = bool(src.get("network_port", False))
    v["usb_port_count_front"] = int(src.get("usb_port_count_front", 0))
    v["usb_port_count_rear"] = int(_get(src, "usb_port_count_rear", fb, "rear USB count"))
    v["channel_switch"] = bool(src.get("channel_switch", False))
    rear_z = min(h_rear * 0.3, 30.0)
    v["rear_port_center_z"] = rnd(rear_z)

    # ── thermal: vent 1 on the rear's right half, above the port row where the
    #    rear is tall enough (the port row runs from the left); vent 2 on top ──
    v0, v1 = rear_z + 14.0, h_rear * 0.85
    if v1 - v0 < 8.0:
        v0, v1 = h_rear * 0.25, h_rear * 0.75
    v.update(vent1_face="rear", vent1_center_u=rnd(W * 0.25), vent1_center_v=rnd((v0 + v1) / 2.0),
             vent1_width=rnd(W * 0.3), vent1_height=rnd(v1 - v0))
    if plan == "tower":
        v.update(vent2_face="top", vent2_center_u=0, vent2_center_v=0,
                 vent2_width=rnd(W * 0.6), vent2_height=rnd(D * 0.6))
    elif plan == "stepped":
        v.update(vent2_face="top", vent2_center_u=rnd(-W * 0.2), vent2_center_v=rnd(tier_mid - D / 2.0),
                 vent2_width=rnd(W * 0.2), vent2_height=rnd(D * 0.25))
    else:
        v.update(vent2_face="top", vent2_center_u=rnd(-W * 0.3), vent2_center_v=rnd(D * 0.25),
                 vent2_width=rnd(W * 0.2), vent2_height=rnd(D * 0.2))
    v["vent2_face"] = src.get("vent2_face", v["vent2_face"])

    # ── support ──────────────────────────────────────────────────────────────
    v["foot_count"] = int(src.get("foot_count", R["foot_count"]))
    v["foot_diameter"] = rnd(min(R["foot_diameter"], m * 0.15))
    v["stand_seat_kind"] = src.get("stand_seat_kind", ARCHETYPE_BASE["stand_seat_kind"])
    v["handle_present"] = bool(src.get("handle_present", False))
    v["handle_span"] = rnd(W * R["handle_span_ratio"])

    if not full:
        return {k: v[k] for k in PRESET_PARAM_ORDER if k in v}, fb
    v.update(edge_chamfer=rnd(R["edge_chamfer"]), wall_thickness=rnd(R["wall_thickness"]),
             seam_height_ratio=rnd(R["seam_height_ratio"]), seam_groove=rnd(R["seam_groove"]),
             side_cover_thickness=rnd(R["side_cover_thickness"]),
             side_cover_overhang=rnd(R["side_cover_overhang"]), side_cover_offset=0,
             slot_clearance=rnd(R["slot_clearance"]), lid_angle=0, tray_extension=0,
             panel_switch_pitch=rnd(R["panel_switch_pitch"]),
             panel_led_count=int(R["panel_led_count"]),
             controller_port_pitch=rnd(R["controller_port_pitch"]),
             cord_diameter=rnd(R["cord_diameter"]), bay_width=rnd(R["bay_width"]),
             bay_depth=rnd(R["bay_depth"]), foot_height=rnd(R["foot_height"]),
             handle_reach=rnd(R["handle_reach"]), handle_thickness=rnd(R["handle_thickness"]))
    for i in (1, 2):
        v.update({f"vent{i}_pattern": R["vent_pattern"], f"vent{i}_pitch": rnd(R["vent_pitch"]),
                  f"vent{i}_hole_size": rnd(R["vent_hole"]), f"vent{i}_depth": rnd(R["vent_depth"])})
    order = PRESET_PARAM_ORDER + ARCHETYPE_ONLY_PARAMS
    return {k: v[k] for k in order if k in v}, fb


# ─────────────────────────────────────────────────────────────────────────────
# Archetype-only presets: one per body plan, asserting NO product
# ─────────────────────────────────────────────────────────────────────────────

def _arch(slug, en, es, why, **src):
    s = {**ARCHETYPE_BASE, "slug": slug, **src}
    if "body_plan" not in src:
        del s["body_plan"]          # the plan rule picks it, as for a product
    values, _ = derive(s, full=False)
    return {"slug": slug, "label": {"en": en, "es": es}, "kind": "archetype",
            "source": ("Archetype preset, not a product: a named point in the family's own "
                       f"parameter space ({why}). Every number is an archetype rule in "
                       "tools/presets/home_console.py. Generated — do not edit by hand."),
            "values": values}


ARCHETYPE_PRESETS = [
    _arch("archetype-wedge-cartridge-console", "Archetype — wedge cartridge console",
          "Arquetipo — consola de cartucho en cuña", "the wedge body plan, top cartridge, panel slide switches",
          body_plan="wedge", body_width=340.0, body_depth=230.0, body_height=90.0,
          slot_door_kind="none", panel_switch_count=4, controller_port_kind="de9",
          controller_port_face="rear", av_out_kind="rf_f", channel_switch=True,
          power_inlet_kind="cord"),
    _arch("archetype-front-loader-console", "Archetype — front-loading cartridge console",
          "Arquetipo — consola de cartucho de carga frontal", "the slab body plan, front cartridge door",
          body_plan="slab", body_width=250.0, body_depth=200.0, body_height=85.0,
          media_kind="cart_front", slot_door_kind="door", power_control="push"),
    _arch("archetype-card-console", "Archetype — card console", "Arquetipo — consola de tarjeta",
          "a small slab, front card slot", body_plan="slab", body_width=150.0, body_depth=145.0,
          body_height=40.0, media_kind="card_front", controller_port_count=1,
          controller_port_kind="round_din"),
    _arch("archetype-lid-disc-console", "Archetype — lid disc console",
          "Arquetipo — consola de disco con tapa", "the slab body plan, a hinged disc lid, crowned top",
          body_plan="slab", body_width=270.0, body_depth=190.0, body_height=60.0, crown=3.0,
          media_kind="disc_lid", memory_card_count=2, av_out_kind="multi_av"),
    _arch("archetype-cube-disc-console", "Archetype — cube disc console with handle",
          "Arquetipo — consola de disco cúbica con asa", "the cube body plan, small-disc lid, handle",
          body_width=150.0, body_depth=160.0, body_height=110.0, media_kind="disc_lid",
          disc_diameter=80.0, handle_present=True, controller_port_count=4),
    _arch("archetype-tray-disc-console", "Archetype — tray disc console",
          "Arquetipo — consola de disco con bandeja", "the slab body plan, a disc tray, concave sides",
          body_plan="slab", body_width=310.0, body_depth=260.0, body_height=85.0,
          side_concavity=4.0, media_kind="disc_tray", controller_port_count=2,
          controller_port_kind="usb_a", av_out_kind="hdmi", network_port=True,
          usb_port_count_rear=1, power_inlet_kind="iec_c8"),
    _arch("archetype-slot-disc-console", "Archetype — slot-loading disc console",
          "Arquetipo — consola de disco con ranura", "the slab body plan, crowned, skewed, slot loader",
          body_plan="slab", body_width=290.0, body_depth=280.0, body_height=60.0, crown=6.0,
          plan_skew_deg=8.0, media_kind="disc_slot", controller_port_kind="none",
          av_out_kind="hdmi", network_port=True, usb_port_count_front=2, usb_port_count_rear=2,
          power_inlet_kind="iec_c13"),
    _arch("archetype-tower-disc-console", "Archetype — tower disc console with covers",
          "Arquetipo — consola de disco en torre con cubiertas",
          "the tower body plan, two side covers, a stand seat, published standing",
          body_width=110.0, body_depth=260.0, body_height=390.0, side_cover_count=2,
          media_kind="disc_slot", controller_port_kind="none",
          av_out_kind="hdmi", network_port=True, usb_port_count_front=2, usb_port_count_rear=2,
          power_inlet_kind="iec_c7", stand_seat_kind="cradle", vent2_face="top"),
    _arch("archetype-upright-display-console", "Archetype — upright console with display",
          "Arquetipo — consola vertical con pantalla",
          "the upright body plan, an integrated front display, rear cartridge",
          body_width=240.0, body_depth=300.0, body_height=380.0, media_kind="cart_rear",
          slot_door_kind="none", screen=(150.0, 190.0), controller_port_count=2,
          controller_port_kind="de9", hardwired_controllers=1, power_inlet_kind="cord"),
    _arch("archetype-mini-console", "Archetype — mini console", "Arquetipo — consola mini",
          "role mini: a small slab, no media", role="mini", body_plan="slab", body_width=110.0,
          body_depth=80.0, body_height=36.0, media_kind="none", controller_port_count=2,
          controller_port_kind="usb_a", av_out_kind="hdmi", power_inlet_kind="barrel",
          power_control="push", foot_count=4),
    _arch("archetype-addon-disc-unit", "Archetype — add-on disc unit",
          "Arquetipo — unidad adicional de disco", "role addon: a slab under a host, with a host link",
          role="addon", body_plan="slab", body_width=300.0, body_depth=210.0, body_height=45.0,
          media_kind="disc_tray", controller_port_kind="none", av_out_kind="rca",
          power_inlet_kind="barrel", reset_present=False, expansion_port_count=1,
          expansion_port_face="rear"),
]


FAMILY = Family(
    slug="home-console",
    base=ARCHETYPE_BASE,
    read=read_device,
    derive=derive,
    axis_mapping={
        "body_width": "reference dimensions_mm.states.body.width (or states.vertical.height, laid flat)",
        "body_depth": "reference dimensions_mm.states.body.depth (or states.vertical.depth)",
        "body_height": "reference dimensions_mm.states.body.height (or states.vertical.width, laid flat)",
        "orientation_tilt_deg": "0 for states.body; 90 when only states.vertical is published",
    },
    source_line=("envelope body width x depth x height as published (feet and projections "
                 "excluded, as makers measure); media, ports, controls and features by kind."),
    extra_presets=json.loads(json.dumps(ARCHETYPE_PRESETS)),
)
