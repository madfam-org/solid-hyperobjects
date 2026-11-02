"""The two-handed controller (`gamepad`): archetype, body-plan rules, catalog reader, derivation.

One parametric controller spans the brick (a rounded rectangle), the crescent (a bridge
with a concave front edge and splayed grips), the dogbone (end lobes), handles (two
tapered grips) and the trident (three grips), plus the same bodies split into halves
on rails or magnets. Every number below is OURS; no outline is fitted to any product.

AXIS MAPPING (gamepad contract, BRIEF §3: `dimensions_mm.states.body` {width, height,
depth} "as published")
--------------------------------------------------------------------------------------
    reference states.body.width                    -> X, across the hands (both halves
                                                      of a split object: 2 x width)
    the smaller of states.body.height / .depth     -> Z, `thickness` (makers disagree on
                                                      which label means "thickness")
    the larger of the two                          -> Y, front edge to shoulders
The envelope this family asserts is the body alone: sticks, triggers, bumper caps and
the cable stub are projecting parts (makers measure "excluding projecting parts").

THE BODY-PLAN RULE. The catalog records no outline, so the plan is chosen from sourced
counts by a rule that is ours: a split object is a brick in halves; two or more sticks
→ handles; one stick → trident; no stick and two or more bumpers → dogbone; no stick
and three or more face buttons → crescent; anything else → brick.

ARCHETYPE PRESETS. Until the catalog files controllers, the family ships one preset per
body plan (`kind: archetype`). They assert no product: their envelopes and counts are
ours, chosen as round numbers inside each plan's feasible range.
"""
from __future__ import annotations

import math

from common import DeriveError, Family, rnd, state

# ─────────────────────────────────────────────────────────────────────────────
# Body-plan rules — fractions of the envelope W (x) x D (y) x H (z). Ours.
# ─────────────────────────────────────────────────────────────────────────────
PLANS = {
    #           bridge W, D   corner  root r  tip r   drop    crowns         cluster x, y
    "brick":    dict(bw=1.00, bd=1.00, rc=0.20, rr=0.0, rt=0.0, drop=0.0, top=0.06, bot=0.04,
                     cx=0.56, cy=0.00),
    "crescent": dict(bw=0.84, bd=0.62, rc=0.16, rr=0.36, rt=0.21, drop=0.15, top=0.10, bot=0.06,
                     cx=0.52, cy=0.14),
    "dogbone":  dict(bw=None, bd=0.74, rc=0.10, rr=None, rt=0.50, drop=0.0, top=0.08, bot=0.05,
                     cx=0.52, cy=0.00),
    "handles":  dict(bw=0.74, bd=0.56, rc=0.18, rr=0.30, rt=0.15, drop=0.30, top=0.12, bot=0.08,
                     cx=0.52, cy=0.10),
    "trident":  dict(bw=0.80, bd=0.42, rc=0.22, rr=0.34, rt=0.12, drop=0.20, top=0.10, bot=0.05,
                     cx=0.60, cy=0.08),
}

RULES = {
    "face_radius": (0.032, 3.5, 6.0),       # of W, clamped
    "face_ring": 2.1,                        # diamond / big_a ring radius, in face radii
    "face_pitch": 2.6,                       # row / diagonal / arc pitch, in face radii
    "dpad_size": 4.6,                        # in face radii
    "dpad_arm": 0.34,                        # of dpad_size
    "stick_radius": (0.065, 6.0, 11.0),      # of W, clamped
    "stick_gate": 0.85,                      # of stick_radius
    "stick_in_x": 0.55, "stick_drop_y": 0.36,   # symmetric sticks: of cluster x / bridge depth
    "control_height": 2.0, "recess": 1.2, "clearance": 0.3,
    "system_radius": (0.018, 2.0, 3.0), "system_y": 0.30,   # of bridge depth above centre
    "touchpad_w": 0.36, "touchpad_h": 0.42, "touchpad_y": 0.05,
    "light_bar_w": 0.30, "speaker_gap": 3.5,
    "bumper_w": 0.20, "bumper_h": 0.16, "bumper_d": 0.14,
    "trigger_w": 0.80, "trigger_len": 0.36, "trigger_d": 0.22, "trigger_travel": 0.0,
    "slot_w": 0.16, "slot_t": 0.07, "slot_depth": 0.45, "slot_pitch": 0.30,
    "door_w": 0.36, "door_l": 0.50,
    "seam_ratio": 0.5, "shell_wall": 2.0,
    "rail_length": 0.78, "rail_width": 0.30,
}

#: The archetype default: a generic two-stick controller with handles. It is no product.
ARCHETYPE_BASE = {
    "slug": "__archetype__", "width": 156.0, "depth": 104.0, "thickness": 40.0,
    "outline": "handles", "split": "none",
    "dpad": True, "face_count": 4, "face_arrangement": "diamond",
    "stick_count": 2, "stick_layout": "symmetric", "bumper_count": 2, "trigger_count": 2,
    "under_trigger": False, "system_button_count": 2, "touchpad": True, "light_bar": True,
    "speaker": True, "headset_jack": True, "cable_exit": "none", "charge_port": True,
    "expansion_slot_count": 0, "expansion_slot_face": "top", "battery_door": False,
}


def _arch(slug, en, es, **kw):
    return dict(ARCHETYPE_BASE, slug=slug, _label=(en, es), **kw)


#: One archetype per body plan. Round numbers of ours; no product.
ARCHETYPES = [
    _arch("archetype-brick", "Archetype — brick", "Arquetipo — ladrillo",
          width=120.0, depth=54.0, thickness=20.0, outline="brick", face_count=2,
          face_arrangement="row", stick_count=0, bumper_count=0, trigger_count=0,
          touchpad=False, light_bar=False, speaker=False, headset_jack=False,
          cable_exit="top", charge_port=False),
    _arch("archetype-crescent", "Archetype — crescent", "Arquetipo — media luna",
          width=160.0, depth=92.0, thickness=32.0, outline="crescent", face_count=6,
          face_arrangement="arc_2x3", dpad_kind="disc", stick_count=0, bumper_count=0,
          trigger_count=0, system_button_count=1, touchpad=False, light_bar=False,
          speaker=False, headset_jack=False, cable_exit="top_center", charge_port=False,
          expansion_slot_count=2),
    _arch("archetype-dogbone", "Archetype — dogbone", "Arquetipo — hueso",
          width=144.0, depth=64.0, thickness=26.0, outline="dogbone", face_count=4,
          stick_count=0, trigger_count=0, touchpad=False, light_bar=False, speaker=False,
          headset_jack=False, cable_exit="top_center", charge_port=False),
    _arch("archetype-handles", "Archetype — handles, offset sticks",
          "Arquetipo — asas, palancas desfasadas",
          stick_layout="offset", touchpad=False, light_bar=False, speaker=False,
          stick_cap="convex", battery_door=True, charge_port=True),
    _arch("archetype-trident", "Archetype — trident", "Arquetipo — tridente",
          width=176.0, depth=112.0, thickness=34.0, outline="trident", face_count=6,
          face_arrangement="big_a", stick_count=1, trigger_count=0, under_trigger=True,
          system_button_count=1, touchpad=False, light_bar=False, speaker=False,
          headset_jack=False, cable_exit="top_center", charge_port=False,
          expansion_slot_count=1, expansion_slot_face="under", stick_gate="octagon"),
    _arch("archetype-rail-halves", "Archetype — halves on rails",
          "Arquetipo — mitades en rieles",
          width=76.0, depth=104.0, thickness=22.0, outline="brick", split="rail_halves",
          dpad_kind="circle", stick_layout="offset", touchpad=False, light_bar=False,
          speaker=False, headset_jack=False, charge_port=False),
    _arch("archetype-magnetic-halves", "Archetype — magnetic halves",
          "Arquetipo — mitades magnéticas",
          width=84.0, depth=112.0, thickness=24.0, outline="brick", split="magnetic_halves",
          dpad_kind="circle", stick_layout="offset", touchpad=False, light_bar=False,
          speaker=False, headset_jack=False, charge_port=False),
]


def _clamp(rule, x):
    k, lo, hi = rule
    return max(lo, min(hi, k * x))


# ─────────────────────────────────────────────────────────────────────────────
# Planform geometry, pure math (the generator runs without a CAD kernel). It mirrors
# commons-lib/hardware/pad_body.py's rules; the envelope-truth check proves they agree.
# ─────────────────────────────────────────────────────────────────────────────

def grip_layout(v: dict) -> list[tuple]:
    """(root_x, root_y, root_r, tip_x, tip_y, tip_r) per grip — pad_grip_layout's rules."""
    n = 0 if v["outline"] == "brick" else int(v["grip_count"])
    if n < 2:
        return []
    s, L = math.radians(v["grip_splay_deg"]), v["grip_length"]
    out = []
    for side in (-1.0, 1.0):
        rx, ry = side * v["grip_root_x"], v["grip_root_y"]
        if v["outline"] == "dogbone":
            out.append((rx, ry, v["grip_tip_radius"], rx, ry, v["grip_tip_radius"]))
        else:
            out.append((rx, ry, v["grip_root_radius"], rx + side * L * math.sin(s),
                        ry - L * math.cos(s), v["grip_tip_radius"]))
    if n >= 3:
        cy = -v["bridge_depth"] / 2.0 + v["grip_root_radius"]
        out.append((0.0, cy, v["grip_root_radius"], 0.0,
                    cy - L - v["center_grip_offset"], v["grip_tip_radius"]))
    return out


def extents(v: dict) -> tuple[float, float, float, float]:
    """(x_min, x_max, y_min, y_max) of the planform."""
    xs = [-v["bridge_width"] / 2.0, v["bridge_width"] / 2.0]
    ys = [-v["bridge_depth"] / 2.0, v["bridge_depth"] / 2.0]
    for rx, ry, r1, tx, ty, r2 in grip_layout(v):
        for cx, cy, r in ((rx, ry, r1), (tx, ty, r2)):
            xs += [cx - r, cx + r]
            ys += [cy - r, cy + r]
    return min(xs), max(xs), min(ys), max(ys)


def inside(v: dict, x: float, y: float, margin: float) -> bool:
    """Is the disc (x, y, margin) inside the planform (bridge or a grip hull)?"""
    bw, bd, rc = v["bridge_width"] / 2.0, v["bridge_depth"] / 2.0, v["bridge_corner_radius"]
    qx, qy = abs(x) - (bw - rc), abs(y) - (bd - rc)   # rounded-rectangle signed distance
    sd = math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - rc
    in_bridge = sd <= -margin
    if in_bridge and v["outline"] == "crescent":
        r = 0.42 * v["bridge_width"]
        yc = -v["bridge_depth"] / 2.0 - r + 0.30 * v["bridge_depth"]
        in_bridge = math.hypot(x, y - yc) >= r + margin
    if in_bridge:
        return True
    for rx, ry, r1, tx, ty, r2 in grip_layout(v):
        ex, ey = tx - rx, ty - ry
        ll = ex * ex + ey * ey
        u = 0.0 if ll == 0 else max(0.0, min(1.0, ((x - rx) * ex + (y - ry) * ey) / ll))
        px, py = rx + u * ex, ry + u * ey
        if math.hypot(x - px, y - py) <= r1 + u * (r2 - r1) - margin:
            return True
    return False


def crown_top(v: dict, x: float, y: float) -> float:
    q = (x / v["crown_span_x"]) ** 2 + ((y - v["crown_center_y"]) / v["crown_span_y"]) ** 2
    return v["thickness"] - v["top_crown"] * max(0.0, q - 0.02)


# ─────────────────────────────────────────────────────────────────────────────
# Catalog reading (BRIEF §3, `gamepad`, kind `controller`)
# ─────────────────────────────────────────────────────────────────────────────

def _count(obj, *kinds):
    for c in obj.get("controls") or []:
        if c.get("kind") in kinds:
            return c.get("count") if c.get("count") is not None else 1
    return 0 if obj.get("controls") else None


def _port(obj, *kinds):
    for c in obj.get("ports") or []:
        if c.get("kind") in kinds:
            return c.get("count") if c.get("count") is not None else 1
    return 0 if obj.get("ports") else None


def read_controller(obj: dict) -> dict | None:
    """Project a reference object onto derive()'s input, or None if its body is unresolved."""
    body = state(obj, "body")
    w, h, d = body.get("width"), body.get("height"), body.get("depth")
    if w is None or h is None or d is None:
        return None
    feats = obj.get("features") or {}
    split = feats.get("split") or "none"
    src = {"slug": obj["key"], "width": float(w) * (2.0 if split != "none" else 1.0),
           "thickness": float(min(h, d)), "depth": float(max(h, d)), "split": split}
    counts = {
        "dpad": _count(obj, "dpad"), "face_count": _count(obj, "abxy", "face_button"),
        "stick_count": _count(obj, "stick"), "bumper_count": _count(obj, "bumper"),
        "trigger_count": _count(obj, "trigger"),
        "system_button_count": _count(obj, "button"), "touchpad": _count(obj, "touchpad"),
        "headset_jack": _port(obj, "headphone_3_5"),
        "charge_port": _port(obj, "usb_c", "micro_usb", "mini_usb"),
        "expansion_slot_count": _port(obj, "expansion_slot"),
    }
    cable = _port(obj, "cable")
    counts["cable_exit"] = None if cable is None else ("top_center" if cable else "none")
    cell = feats.get("cell_kind")
    counts["battery_door"] = None if cell is None else cell in ("aa", "aaa")
    for k, val in counts.items():
        if val is None:
            src.setdefault("_fallbacks", []).append(k.replace("_", " "))
            continue
        src[k] = bool(val) if k in ("dpad", "touchpad", "headset_jack", "charge_port",
                                    "battery_door") else val
    sticks, bumpers, faces = (src.get("stick_count") or 0, src.get("bumper_count") or 0,
                              src.get("face_count") or 0)
    src["outline"] = ("brick" if split != "none" else "handles" if sticks >= 2 else
                      "trident" if sticks == 1 else "dogbone" if bumpers >= 2 else
                      "crescent" if faces >= 3 else "brick")
    if split != "none":
        src["stick_layout"], src["dpad_kind"] = "offset", "circle"
    return src


# ─────────────────────────────────────────────────────────────────────────────
# The one derivation path: envelope + plan + counts -> every parameter
# ─────────────────────────────────────────────────────────────────────────────

def _body(src: dict, v: dict) -> None:
    W, D, H = src["width"], src["depth"], src["thickness"]
    P = PLANS[src["outline"]]
    v["outline"], v["thickness"] = src["outline"], rnd(H)
    if src["outline"] == "dogbone":
        rt = P["rt"] * D
        bw, bd = W - 2.0 * rt + 2.0, P["bd"] * D
        v.update(grip_count=2, grip_root_x=rnd(W / 2.0 - rt), grip_root_y=0, grip_length=0,
                 grip_splay_deg=0, grip_root_radius=rnd(rt), grip_tip_radius=rnd(rt),
                 center_grip_offset=0)
        y_min, y_max = -D / 2.0, D / 2.0
    else:
        bw, bd = P["bw"] * W, P["bd"] * D
        y_max = bd / 2.0
        y_min = y_max - D
    v["bridge_width"], v["bridge_depth"] = rnd(bw), rnd(bd)
    v["bridge_corner_radius"] = rnd(P["rc"] * min(bw, bd))
    if src["outline"] in ("brick",):
        v.update(grip_count=0, grip_root_x=0, grip_root_y=0, grip_length=0, grip_splay_deg=0,
                 grip_root_radius=0, grip_tip_radius=0, center_grip_offset=0)
        if abs(bd - D) > 1e-9 or abs(bw - W) > 1e-9:
            raise DeriveError(f"{src['slug']}: a brick's bridge is its envelope")
    elif src["outline"] != "dogbone":
        rr, rt = P["rr"] * bd, P["rt"] * D
        # 1 mm inside the bridge corner: an inscribed root would be TANGENT to two
        # bridge faces, and tangent cylinders do not boolean (gotchas canon)
        rx, ry = bw / 2.0 - rr - 1.0, -bd / 2.0 + rr + 1.0
        tx, ty = W / 2.0 - rt, y_min + rt
        L = math.hypot(tx - rx, ty - ry)
        if L <= abs(rr - rt) + 1.0:
            raise DeriveError(f"{src['slug']}: grips too short for the {src['outline']} plan")
        n = 3 if src["outline"] == "trident" else 2
        v.update(grip_count=n, grip_root_x=rnd(rx), grip_root_y=rnd(ry), grip_length=rnd(L),
                 grip_splay_deg=rnd(math.degrees(math.atan2(tx - rx, ry - ty))),
                 grip_root_radius=rnd(rr), grip_tip_radius=rnd(rt), center_grip_offset=0)
        if n == 3:  # the centre prong stops 0.15 D above the side tips
            v["center_grip_offset"] = rnd((ry - (y_min + 0.15 * D + rt)) - L)
    v["grip_drop"] = rnd(P["drop"] * H if v["grip_count"] else 0.0)
    v["top_crown"], v["bottom_crown"] = rnd(P["top"] * H), rnd(P["bot"] * H)
    v["crown_center_y"] = 0
    v["crown_span_x"] = rnd(W / 2.0)
    v["crown_span_y"] = rnd(max(y_max, -y_min))
    got = extents(v)
    want = (-W / 2.0, W / 2.0, y_min, y_max)
    if max(abs(a - b) for a, b in zip(got, want)) > 0.005:
        raise DeriveError(f"{src['slug']}: planform {got} misses the envelope {want}")


def _need(v, x, y, margin, what, slug):
    if not inside(v, x, y, margin):
        raise DeriveError(f"{slug}: the {what} at ({x:.1f}, {y:.1f}) falls off the planform")


def derive(src: dict, *, full: bool = True) -> tuple[dict, list[str]]:
    """Return (values, fallbacks): every parameter, from an envelope, a plan and counts."""
    R = RULES
    fallbacks = list(src.get("_fallbacks", []))
    s = dict(ARCHETYPE_BASE, **{k: x for k, x in src.items() if not k.startswith("_")})
    slug = s["slug"]
    v: dict = {}
    _body(s, v)
    W, H = s["width"], s["thickness"]
    bw, bd = v["bridge_width"], v["bridge_depth"]
    P = PLANS[s["outline"]]
    cx, cy = P["cx"] * W / 2.0, P["cy"] * bd
    fr = _clamp(R["face_radius"], W)
    split = s["split"]
    v["split"], v["split_gap"] = split, 0
    v["seam_ratio"], v["shell_wall"] = rnd(R["seam_ratio"]), rnd(R["shell_wall"])
    v["control_recess_depth"], v["control_clearance"] = rnd(R["recess"]), rnd(R["clearance"])

    # sticks first: an offset layout moves the D-pad to the inner low spot
    n_st = int(s["stick_count"])
    layout = s.get("stick_layout", "symmetric")
    sr = _clamp(R["stick_radius"], W)
    sx, sy = R["stick_in_x"] * cx, cy - R["stick_drop_y"] * bd
    dpad_xy, left, right = (-cx, cy), (-sx, sy), (sx, sy)
    if layout == "offset":
        dpad_xy, left, right = (-sx, sy), (-cx, cy), (sx, sy)
    if s["outline"] == "trident":
        left = right = (0.0, -bd / 2.0 + v["grip_root_radius"])
    if split != "none":       # one stick per half: high on the left, low on the right
        dpad_xy, left, right = (-cx, sy), (-cx, cy), (cx, sy)
    v.update(stick_count=n_st, stick_layout=layout, stick_left_x=rnd(left[0]),
             stick_left_y=rnd(left[1]), stick_right_x=rnd(right[0]), stick_right_y=rnd(right[1]),
             stick_cap=s.get("stick_cap", "concave"), stick_radius=rnd(sr),
             stick_height=rnd(sr), stick_gate=s.get("stick_gate", "round"),
             stick_gate_radius=rnd(R["stick_gate"] * sr), stick_tilt_deg=0)
    for i, (x, y) in enumerate((left, right)[:n_st]):
        _need(v, x, y, v["stick_gate_radius"] + 1.5, f"stick {i + 1}", slug)

    v["dpad_kind"] = s.get("dpad_kind", "cross") if s.get("dpad", True) else "none"
    v["dpad_x"], v["dpad_y"] = rnd(dpad_xy[0]), rnd(dpad_xy[1])
    v["dpad_size"] = rnd(R["dpad_size"] * fr)
    v["dpad_arm_width"] = rnd(R["dpad_arm"] * v["dpad_size"])
    v["dpad_height"] = rnd(R["control_height"])
    if v["dpad_kind"] != "none":
        _need(v, dpad_xy[0], dpad_xy[1], v["dpad_size"] / 2.0 + 1.0, "D-pad", slug)

    fc, arr = int(s["face_count"]), s["face_arrangement"]
    ring = arr in ("diamond", "big_a")
    face_xy = (cx, cy)
    v.update(face_count=fc, face_arrangement=arr, face_x=rnd(face_xy[0]),
             face_y=rnd(face_xy[1]), face_radius=rnd(fr),
             face_spacing=rnd((R["face_ring"] if ring else R["face_pitch"]) * fr),
             face_tilt_deg=20 if arr in ("row", "arc_2x3") and s["outline"] != "brick" else 0,
             face_height=rnd(R["control_height"]))
    reach = v["face_spacing"] * (2.5 if not ring else 1.0) + fr * 1.6
    if fc:
        _need(v, face_xy[0], face_xy[1], min(reach, 0.9 * v["face_spacing"] + fr), "face cluster", slug)

    # system buttons, touchpad, light bar, speaker, jack
    nsys = int(s["system_button_count"])
    sysr = _clamp(R["system_radius"], W)
    tp = bool(s["touchpad"])
    tw, th = R["touchpad_w"] * bw, R["touchpad_h"] * bd
    ty = R["touchpad_y"] * bd + cy
    v.update(touchpad_present=tp, touchpad_width=rnd(tw), touchpad_height=rnd(th),
             touchpad_y=rnd(ty), system_button_count=nsys, system_radius=rnd(sysr))
    if tp:
        v["system_y"], v["system_pitch"] = rnd(ty), rnd(tw + 2.0 * sysr + 3.0)
    elif split != "none":
        v["system_y"], v["system_pitch"] = rnd(cy + 0.25 * bd), rnd(bw / 2.0)
    else:
        v["system_y"], v["system_pitch"] = rnd(cy + R["system_y"] * bd * 0.5 - 0.1 * bd), \
            rnd(max(4.0 * sysr, 0.12 * bw))
    for i in range(nsys):
        x = (i - (nsys - 1) / 2.0) * v["system_pitch"]
        _need(v, x, v["system_y"], sysr + 1.0, f"system button {i + 1}", slug)
    v.update(light_bar_present=bool(s["light_bar"]), light_bar_width=rnd(R["light_bar_w"] * bw),
             speaker_present=bool(s["speaker"]),
             speaker_y=rnd((ty - th / 2.0 - R["speaker_gap"]) if tp else cy - 0.2 * bd),
             headset_jack=bool(s["headset_jack"]))

    # shoulders
    nb, nt = int(s["bumper_count"]), int(s["trigger_count"])
    zb = H - v["grip_drop"]
    v.update(bumper_count=nb, bumper_x=rnd(cx), bumper_width=rnd(R["bumper_w"] * bw),
             bumper_height=rnd(R["bumper_h"] * zb), bumper_depth=rnd(R["bumper_d"] * bd),
             trigger_count=nt, trigger_x=rnd(cx),
             trigger_width=rnd(R["trigger_w"] * R["bumper_w"] * bw),
             trigger_length=rnd(R["trigger_len"] * zb), trigger_depth=rnd(R["trigger_d"] * bd),
             trigger_travel_deg=rnd(R["trigger_travel"]), under_trigger=bool(s["under_trigger"]),
             under_trigger_y=rnd(-bd / 2.0 + v["grip_root_radius"] - 0.2 * v["grip_root_radius"]))
    if v["bumper_x"] + v["bumper_width"] / 2.0 > W / 2.0 - 1.0:
        raise DeriveError(f"{slug}: bumpers run off the bridge")

    # ports and power
    v.update(cable_exit=s["cable_exit"], charge_port=bool(s["charge_port"]),
             expansion_slot_count=int(s["expansion_slot_count"]),
             expansion_slot_face=s["expansion_slot_face"],
             expansion_slot_width=rnd(R["slot_w"] * bw),
             expansion_slot_thickness=rnd(R["slot_t"] * bd),
             expansion_slot_depth=rnd(R["slot_depth"] * zb),
             expansion_slot_pitch=rnd(R["slot_pitch"] * bw))
    if s["expansion_slot_face"] == "under":
        v["expansion_slot_y"] = rnd(-bd / 2.0 + v["grip_root_radius"] - 2.0
                                    - v["grip_length"] / 2.0)
        v["expansion_slot_width"] = rnd(1.2 * v["grip_root_radius"])
        v["expansion_slot_thickness"] = rnd(0.35 * v["grip_root_radius"])
        v["expansion_slot_depth"] = rnd(0.45 * H)
    else:
        v["expansion_slot_y"] = rnd(bd / 2.0 - 0.18 * bd)
    v.update(battery_door=bool(s["battery_door"]), battery_door_width=rnd(R["door_w"] * bw),
             battery_door_length=rnd(R["door_l"] * bd), battery_door_y=rnd(-0.05 * bd))
    v.update(rail_length=rnd(R["rail_length"] * s["depth"]), rail_width=rnd(R["rail_width"] * H))

    if split != "none":
        for what, x, ext in (("D-pad", v["dpad_x"], v["dpad_size"] / 2.0),
                             ("face cluster", v["face_x"], v["face_spacing"] + fr),
                             ("stick", v["stick_left_x"], v["stick_gate_radius"])):
            if abs(x) - ext < 2.0:
                raise DeriveError(f"{slug}: the {what} straddles the split line")
    th_tip = min(crown_top(v, t[3] + math.copysign(t[5], t[3] or 1), t[4]) for t in
                 grip_layout(v)) if grip_layout(v) else H
    if th_tip < 0.4 * H:
        raise DeriveError(f"{slug}: the crown leaves {th_tip:.1f} mm at a grip tip")
    return {k: v[k] for k in PARAM_ORDER}, fallbacks


#: Every parameter, in manifest order.
PARAM_ORDER = [
    "outline", "thickness", "bridge_width", "bridge_depth", "bridge_corner_radius",
    "grip_count", "grip_root_x", "grip_root_y", "grip_length", "grip_splay_deg", "grip_drop",
    "grip_root_radius", "grip_tip_radius", "center_grip_offset",
    "top_crown", "bottom_crown", "crown_span_x", "crown_span_y", "crown_center_y",
    "seam_ratio", "shell_wall", "control_recess_depth", "control_clearance",
    "dpad_kind", "dpad_x", "dpad_y", "dpad_size", "dpad_arm_width", "dpad_height",
    "face_count", "face_arrangement", "face_x", "face_y", "face_radius", "face_spacing",
    "face_tilt_deg", "face_height",
    "stick_count", "stick_layout", "stick_left_x", "stick_left_y", "stick_right_x",
    "stick_right_y", "stick_cap", "stick_radius", "stick_height", "stick_gate",
    "stick_gate_radius", "stick_tilt_deg",
    "bumper_count", "bumper_x", "bumper_width", "bumper_height", "bumper_depth",
    "trigger_count", "trigger_x", "trigger_width", "trigger_length", "trigger_depth",
    "trigger_travel_deg", "under_trigger", "under_trigger_y",
    "system_button_count", "system_y", "system_pitch", "system_radius",
    "touchpad_present", "touchpad_width", "touchpad_height", "touchpad_y",
    "light_bar_present", "light_bar_width", "speaker_present", "speaker_y", "headset_jack",
    "cable_exit", "charge_port", "expansion_slot_count", "expansion_slot_face",
    "expansion_slot_y", "expansion_slot_pitch", "expansion_slot_width",
    "expansion_slot_thickness", "expansion_slot_depth",
    "battery_door", "battery_door_width", "battery_door_length", "battery_door_y",
    "split", "split_gap", "rail_length", "rail_width",
]


def _archetype_preset(a: dict) -> dict:
    values, _ = derive(a)
    en, es = a["_label"]
    return {
        "slug": a["slug"],
        "label": {"en": en, "es": es},
        "kind": "archetype",
        "source": (
            f"Archetype {a['outline']} body plan{'' if a['split'] == 'none' else ', ' + a['split']}"
            f", not a product: envelope {rnd(a['width'])} x {rnd(a['depth'])} x "
            f"{rnd(a['thickness'])} mm (W x D x H) and its control counts are ours, every other "
            "number follows the archetype rules in tools/presets/gamepad.py. Generated — do "
            "not edit by hand."
        ),
        "envelope_mm": {"width": rnd(a["width"]), "depth": rnd(a["depth"]),
                        "thickness": rnd(a["thickness"])},
        "values": values,
    }


FAMILY = Family(
    slug="gamepad",
    base=ARCHETYPE_BASE,
    read=read_controller,
    derive=derive,
    axis_mapping={
        "x (bridge, grips)": "reference dimensions_mm.states.body.width (2 x width for a split object)",
        "thickness": "the smaller of reference dimensions_mm.states.body.height / depth",
        "y (front edge to shoulders)": "the larger of reference dimensions_mm.states.body.height / depth",
    },
    source_line="envelope body width x height x depth as published (body only, projecting parts excluded).",
    extra_presets=[_archetype_preset(a) for a in ARCHETYPES],
)
