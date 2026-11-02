"""The book-fold phone: archetype, rules, catalog reader, derivation, fold states.

One inward-folding display on the LONG axis, a cover display outside. The archetype is two
rigid half-frames that meet at a fold axis, separated when closed by a gap the folded
display's teardrop occupies. Ported unchanged from Telesia's `scripts/device-presets.py`
(telesia@43828e9); only the readers moved to the catalog's `dimensions_mm.states`.

What this family publishes that the clamshell does not, and what follows:

  * an OPEN envelope as well as a closed one. Two derivations fall straight out of the
    pair and are SOURCED at both ends rather than archetype guesses:
        half thickness    = open.depth      (the open body IS one half)
        hinge gap         = closed.depth - 2 x open.depth
        camera-half width = open.width - closed.width
  * `open.height == closed.height` on every object that publishes both — the axis common
    to the two states IS the hinge axis, which makes the mapping a checked fact.

AXIS MAPPING (same trap as the clamshell, and Apple says so out loud):

    reference states.closed.height -> hinge_axis_length  (X, the hinge axis)
    reference states.closed.width  -> cover_half_width   (Y, closed)
    reference states.open.width    -> cover + camera half widths (Y, open)
    reference states.closed.depth  -> 2 x half_thickness + hinge gap (Z)
    reference states.open.depth    -> half_thickness (Z)
"""
from __future__ import annotations

import json

from common import DeriveError, Family, display, has_port, rnd, state

#: The archetype's own book-fold phone — no particular product. Running
#: `derive_bookfold()` on it produces the cartridge's parameter defaults.
BOOKFOLD_ARCHETYPE_BASE = {
    "slug": "__archetype__",
    "hinge_axis_length": 156.0,   # X, the hinge axis
    "cover_half_width": 74.0,     # Y, closed
    "closed_thickness": 10.0,     # Z, both halves plus the gap
    "open_width": 146.0,          # Y, open
    "open_depth": 4.7,            # Z, open — ONE half's thickness
    "inner_display": None,        # exercises the bezel fallback, as 27/28 do
    "cover_display": None,
    "usb_c_present": True,
    "card_slot_present": True,
}

BOOKFOLD_ARCHETYPE_RULES = {
    # ── Hinge gap ────────────────────────────────────────────────────────────
    # DERIVED from two published numbers, not invented: closed depth minus twice
    # the open depth is the space the folded display's teardrop occupies. Where
    # a manufacturer's two figures cannot both hold with two equal halves (OPPO
    # Find N3: 11.7 closed against 2 x 5.9 open = -0.1 mm), the CLOSED envelope
    # wins — it is the one this cartridge asserts against — and the half
    # thickness is derived from it instead, named as a fallback.
    "min_hinge_gap": 0.05,
    "fallback_hinge_gap": 0.6,
    # ── Crease relief and the hinge leaf ─────────────────────────────────────
    # The relief is a cylinder ON the fold axis, so it is invariant under the
    # fold: cutting it before the rotate and after give the same solid. Its
    # radius is capped by the wall it must leave against the outer face.
    "crease_relief_ratio": 0.45,      # of half_thickness, past the gap
    "hinge_wall": 0.6,                # material left against the outer face
    "hinge_running_clearance": 0.3,
    "hinge_span_ratio": 0.94,         # of hinge_axis_length
    # ── Shells and faces ─────────────────────────────────────────────────────
    "corner_radius": 6.0,             # 0 of 84 catalog objects publishes one
    "display_recess_depth": 0.8,
    "display_bezel": 2.5,             # fallback window inset; see below
    # ── Camera island ────────────────────────────────────────────────────────
    "lens_island_length_ratio": 0.20,   # of hinge_axis_length
    "lens_island_width_ratio": 0.42,    # of camera_half_width
    "lens_island_depth": 0.6,
    "lens_extra_depth": 1.2,            # past the island floor
    "lens_count": 3,
    "lens_radius_ratio": 0.13,          # of the island
    "lens_pitch_ratio": 0.30,           # of the island (> 2 x the radius ratio,
                                        # so the three apertures never overlap)
    "edge_margin": 6.0,
    # ── Side buttons ─────────────────────────────────────────────────────────
    "button_count": 2,
    "button_width": 14.0,
    "button_seat_depth": 2.0,         # the tool straddles the edge: bites half
    "button_height": 2.0,
    "button_pitch": 22.0,
    "button_center_ratio": 0.12,      # of hinge_axis_length, from centre
    # ── Ports on the end face ────────────────────────────────────────────────
    # 8.6 x 2.8 clears a USB-C receptacle (the plug is 8.34 x 2.56 nominal); the
    # rest of the opening geometry is archetype.
    "usb_c_width": 8.6,
    "usb_c_height": 2.8,
    "usb_c_depth": 10.0,              # straddles the end face: bites half
    "card_slot_width": 12.5,
    "card_slot_height": 2.0,
    "card_slot_depth": 8.0,
    "card_slot_offset_ratio": 0.22,   # of cover_half_width
    "speaker_hole_count": 5,
    "speaker_hole_radius": 0.7,
    "speaker_hole_depth": 6.0,
    "speaker_pitch": 3.0,
    "speaker_edge_gap": 1.0,
    # ── Frozen spans: cut solids deliberately larger than the part ───────────
    "hinge_clip_span": 400.0,
    "fold_angle": 135.0,
}

#: Parameters a book-fold preset may carry. Order is the order they are written.
BOOKFOLD_PRESET_PARAM_ORDER = [
    "hinge_axis_length", "cover_half_width", "camera_half_width",
    "half_thickness", "cover_half_center_y", "cover_half_center_z",
    "camera_half_center_y", "camera_half_center_z",
    "hinge_cavity_radius", "hinge_cavity_span",
    "hinge_leaf_radius", "hinge_leaf_span",
    "inner_display_width", "inner_display_cover_span",
    "inner_display_camera_span", "inner_display_cover_center_y",
    "inner_display_camera_center_y", "inner_display_cover_cut_center_z",
    "inner_display_camera_cut_center_z",
    "cover_display_width", "cover_display_height", "cover_display_center_y",
    "cover_display_cut_center_z",
    "lens_island_width", "lens_island_height", "lens_island_center_x",
    "lens_island_center_y", "lens_island_cut_center_z",
    "lens_radius", "lens_pitch_x", "lens_first_center_x", "lens_center_y",
    "lens_cut_center_z",
    "button_first_center_x", "button_center_y", "button_center_z",
    "usb_c_center_x", "usb_c_center_y", "usb_c_center_z",
    "card_slot_center_x", "card_slot_center_y", "card_slot_center_z",
    "speaker_center_x", "speaker_first_center_y", "speaker_center_z",
    "usb_c_present", "card_slot_present",
]

#: Book-fold parameters that are pure archetype — defaults only, never a preset.
BOOKFOLD_ARCHETYPE_ONLY_PARAMS = [
    "corner_radius", "fold_angle", "display_recess_depth",
    "hinge_clip_span", "hinge_clip_center_y",
    "lens_island_depth", "lens_count", "lens_depth",
    "button_count", "button_width", "button_seat_depth", "button_height",
    "button_pitch_x",
    "usb_c_width", "usb_c_height", "usb_c_depth",
    "card_slot_width", "card_slot_height", "card_slot_depth",
    "speaker_hole_count", "speaker_hole_radius", "speaker_hole_depth",
    "speaker_pitch_y",
]


def _fit_display(area, x_extent: float, y_extent: float, slug: str, what: str):
    """Assign a published (width, height) active area to the device's X and Y.

    The catalog records a display's own width and height, and which of them runs
    along the hinge axis depends on how the panel is oriented in the body — the
    iPhone Duo's cover display is 77.19 x 112.31 in a closed body that is
    117.8 (X) x 84.1 (Y), so its HEIGHT runs along X, while its inner display is
    110.93 x 157.72 in an open body of 117.8 x 164.6, where its height runs
    along Y. One rule covers both: take the orientation that FITS, and when both
    fit, put the display's height on the device's longer axis (the portrait
    convention every phone in this family follows). Neither fitting is not a
    thing to round away — it is a disagreement between published numbers, so it raises.
    """
    w, h = float(area[0]), float(area[1])
    fits_wh = w <= x_extent and h <= y_extent
    fits_hw = h <= x_extent and w <= y_extent
    if fits_wh and fits_hw:
        return (w, h) if y_extent >= x_extent else (h, w)
    if fits_wh:
        return (w, h)
    if fits_hw:
        return (h, w)
    raise DeriveError(
        f"{slug}: the {what} active area {w} x {h} mm does not fit the published "
        f"{x_extent} x {y_extent} mm envelope in either orientation. Not modelled."
    )


def read_device_bookfold(obj: dict) -> dict | None:
    """Project a reference object onto `derive_bookfold()`'s input shape, or None.

    None means the CLOSED envelope is unresolved. The open envelope may be
    partly null and the archetype names a fallback for each part of it; the
    closed one is the whole point of a preset and is never defaulted.
    """
    closed = state(obj, "closed")
    openv = state(obj, "open")
    h, w, d = closed.get("height"), closed.get("width"), closed.get("depth")
    if h is None or w is None or d is None:
        return None
    return {
        "slug": obj["key"],
        "hinge_axis_length": float(h),   # closed.height == the hinge axis
        "cover_half_width": float(w),
        "closed_thickness": float(d),
        "open_width": None if openv.get("width") is None else float(openv["width"]),
        "open_depth": None if openv.get("depth") is None else float(openv["depth"]),
        "inner_display": display(obj, "inner"),
        "cover_display": display(obj, "cover"),
        "usb_c_present": has_port(obj, "usb_c"),
        "card_slot_present": has_port(obj, "sim"),
    }


def derive_bookfold(src: dict, *, full: bool) -> tuple[dict, list[str]]:
    """Return (values, fallbacks) for one book-fold device or the archetype.

    Frame: X is the hinge axis, through the ORIGIN (the graph engine's `rotate`
    turns about the origin and nothing else). The cover half spans y in
    [0, cover_half_width] below the gap; the camera half spans the same from the
    fold axis above it and turns about X by `fold_angle` — 0 closed, 180 open.
    The gap mid-plane is z = 0, which is why the open state has NO gap: a
    rotation about that axis lands both halves in the same z band, and the open
    depth is therefore one half's thickness, exactly as published.
    """
    R = BOOKFOLD_ARCHETYPE_RULES
    fallbacks: list[str] = []
    v: dict = {}

    L = float(src["hinge_axis_length"])
    wA = float(src["cover_half_width"])
    T = float(src["closed_thickness"])

    # ── L0 the two halves and the gap ────────────────────────────────────────
    open_depth = src.get("open_depth")
    if open_depth is None:
        fallbacks.append("half thickness (no published open depth)")
        t = (T - R["fallback_hinge_gap"]) / 2.0
    elif T - 2.0 * float(open_depth) >= R["min_hinge_gap"]:
        t = float(open_depth)
    else:
        fallbacks.append(
            "half thickness (the published open depth and closed depth cannot "
            "both hold with two equal halves)")
        t = (T - R["min_hinge_gap"]) / 2.0
    t = round(t, 4)
    gap = round(T - 2.0 * t, 4)
    if t <= 1.0:
        raise DeriveError(
            f"{src['slug']}: a half frame would be {t} mm thick. Not modelled.")

    open_width = src.get("open_width")
    if open_width is None:
        fallbacks.append("camera-half width (no published open width)")
        wB = wA
    else:
        wB = round(float(open_width) - wA, 4)
        if not 0.0 < wB <= wA:
            raise DeriveError(
                f"{src['slug']}: open width {open_width} mm minus closed width "
                f"{wA} mm gives a camera half of {wB} mm. Not modelled.")

    v["hinge_axis_length"] = rnd(L)
    v["cover_half_width"] = rnd(wA)
    v["camera_half_width"] = rnd(wB)
    v["half_thickness"] = rnd(t)
    v["cover_half_center_y"] = rnd(wA / 2.0)
    v["cover_half_center_z"] = rnd(-(gap / 2.0 + t / 2.0))
    v["camera_half_center_y"] = rnd(wB / 2.0)
    v["camera_half_center_z"] = rnd(gap / 2.0 + t / 2.0)

    # ── L1 displays ──────────────────────────────────────────────────────────
    # A null active area does NOT fall back to a fixed archetype rectangle the
    # way the clamshell's does: a fixed one does not fit a 117.9 mm open body and
    # overhangs a 164.6 mm one. It falls back to the SOURCED envelope inset by
    # the archetype bezel, which scales and is named per preset. (Sanity: on the
    # one device that publishes an active area, the rule lands within 0.5 mm of
    # Apple's own cover-display figure.)
    b = R["display_bezel"]
    recess = R["display_recess_depth"]
    open_y = wA + wB
    inner = src.get("inner_display")
    if inner is None:
        fallbacks.append("inner display active area")
        ix, iy = L - 2.0 * b, open_y - 2.0 * b
    else:
        ix, iy = _fit_display(inner, L, open_y, src["slug"], "inner display")
    cover = src.get("cover_display")
    if cover is None:
        fallbacks.append("cover display active area")
        cx, cy = L - 2.0 * b, wA - 2.0 * b
    else:
        cx, cy = _fit_display(cover, L, wA, src["slug"], "cover display")

    # The inner display is centred on the OPEN envelope, not on the fold axis,
    # so its bezels are equal — which puts unequal amounts of it on the two
    # halves whenever they are unequal widths.
    centre = (wA - wB) / 2.0
    span_cover = round(centre + iy / 2.0, 4)
    span_camera = round(iy / 2.0 - centre, 4)
    if not 0.0 < span_cover <= wA or not 0.0 < span_camera <= wB:
        raise DeriveError(
            f"{src['slug']}: the inner display ({iy} mm across the fold) does not "
            f"sit on halves of {wA} and {wB} mm. Not modelled.")
    v["inner_display_width"] = rnd(ix)
    v["inner_display_cover_span"] = rnd(span_cover)
    v["inner_display_camera_span"] = rnd(span_camera)
    v["inner_display_cover_center_y"] = rnd(span_cover / 2.0)
    v["inner_display_camera_center_y"] = rnd(span_camera / 2.0)
    v["inner_display_cover_cut_center_z"] = rnd(-(gap / 2.0 + recess / 2.0))
    v["inner_display_camera_cut_center_z"] = rnd(gap / 2.0 + recess / 2.0)
    v["cover_display_width"] = rnd(cx)
    v["cover_display_height"] = rnd(cy)
    v["cover_display_center_y"] = rnd(wA / 2.0)
    v["cover_display_cut_center_z"] = rnd(-(gap / 2.0 + t) + recess / 2.0)

    # ── L0 hinge: the crease relief and the leaf that turns in it ────────────
    relief = round(min(gap / 2.0 + R["crease_relief_ratio"] * t,
                       gap / 2.0 + t - R["hinge_wall"]), 4)
    leaf = round(relief - R["hinge_running_clearance"], 4)
    if leaf <= gap / 2.0:
        raise DeriveError(
            f"{src['slug']}: the hinge leaf would be {leaf} mm against a "
            f"{gap} mm gap — no room to turn. Not modelled.")
    v["hinge_cavity_radius"] = rnd(relief)
    v["hinge_cavity_span"] = rnd(L * R["hinge_span_ratio"])
    v["hinge_leaf_radius"] = rnd(leaf)
    v["hinge_leaf_span"] = rnd(L * R["hinge_span_ratio"]
                               - 2.0 * R["hinge_running_clearance"])

    # ── L2 camera island ─────────────────────────────────────────────────────
    # A RECESS, not a raised bump: every published depth in this family excludes
    # the camera bump and no manufacturer publishes its height, so raising an
    # island would both invent a dimension and break the published envelope.
    island = round(min(R["lens_island_length_ratio"] * L,
                       R["lens_island_width_ratio"] * wB), 4)
    m = R["edge_margin"]
    island_cx = round(L / 2.0 - island / 2.0 - m, 4)
    island_cy = round(island / 2.0 + m, 4)
    if island_cy + island / 2.0 > wB or island_cx - island / 2.0 < -L / 2.0:
        raise DeriveError(
            f"{src['slug']}: the camera island does not fit the camera half. "
            f"Not modelled.")
    z_outer_camera = gap / 2.0 + t
    n_lens = int(R["lens_count"])
    lens_pitch = round(island * R["lens_pitch_ratio"], 4)
    v["lens_island_width"] = rnd(island)
    v["lens_island_height"] = rnd(island)
    v["lens_island_center_x"] = rnd(island_cx)
    v["lens_island_center_y"] = rnd(island_cy)
    v["lens_island_cut_center_z"] = rnd(z_outer_camera - R["lens_island_depth"] / 2.0)
    v["lens_radius"] = rnd(island * R["lens_radius_ratio"])
    v["lens_pitch_x"] = rnd(lens_pitch)
    v["lens_first_center_x"] = rnd(island_cx - lens_pitch * (n_lens - 1) / 2.0)
    v["lens_center_y"] = rnd(island_cy)
    v["lens_cut_center_z"] = rnd(
        z_outer_camera - (R["lens_island_depth"] + R["lens_extra_depth"]) / 2.0)

    # ── L2 side buttons, on the cover half's opening edge ────────────────────
    bw, bp, bn = R["button_width"], R["button_pitch"], int(R["button_count"])
    first_btn = round(R["button_center_ratio"] * L - bp * (bn - 1) / 2.0, 4)
    last_btn = first_btn + bp * (bn - 1)
    if (first_btn - bw / 2.0 < -L / 2.0 + R["corner_radius"]
            or last_btn + bw / 2.0 > L / 2.0 - R["corner_radius"]):
        raise DeriveError(
            f"{src['slug']}: the button row runs into the corner radius. "
            f"Not modelled.")
    v["button_first_center_x"] = rnd(first_btn)
    v["button_center_y"] = rnd(wA)
    v["button_center_z"] = rnd(-(gap / 2.0 + t / 2.0))

    # ── L2 the end face: USB-C, the card tray, the speaker ──────────────────
    mid_z = -(gap / 2.0 + t / 2.0)
    v["usb_c_center_x"] = rnd(-L / 2.0)
    v["usb_c_center_y"] = rnd(wA / 2.0)
    v["usb_c_center_z"] = rnd(mid_z)
    card_y = round(R["card_slot_offset_ratio"] * wA, 4)
    if (card_y + R["card_slot_width"] / 2.0
            >= wA / 2.0 - R["usb_c_width"] / 2.0 - 1.0):
        raise DeriveError(
            f"{src['slug']}: the card tray would run into the USB-C opening. "
            f"Not modelled.")
    v["card_slot_center_x"] = rnd(-L / 2.0)
    v["card_slot_center_y"] = rnd(card_y)
    v["card_slot_center_z"] = rnd(mid_z)
    speaker_span = R["speaker_pitch"] * (R["speaker_hole_count"] - 1)
    sp_first = round(wA - R["corner_radius"] - R["speaker_edge_gap"]
                     - R["speaker_hole_radius"] - speaker_span, 4)
    if (sp_first - R["speaker_hole_radius"]
            <= wA / 2.0 + R["usb_c_width"] / 2.0 + 1.0):
        raise DeriveError(
            f"{src['slug']}: the speaker row would run into the USB-C opening. "
            f"Not modelled.")
    v["speaker_center_x"] = rnd(-L / 2.0)
    v["speaker_first_center_y"] = rnd(sp_first)
    v["speaker_center_z"] = rnd(mid_z)

    for key, name in (("usb_c_present", "usb-c port"),
                      ("card_slot_present", "sim card slot")):
        flag = src.get(key)
        if flag is None:
            fallbacks.append(name)
            flag = BOOKFOLD_ARCHETYPE_BASE[key]
        v[key] = bool(flag)

    if not full:
        return {k: v[k] for k in BOOKFOLD_PRESET_PARAM_ORDER if k in v}, fallbacks

    # ── archetype-only parameters (defaults emission) ────────────────────────
    v["corner_radius"] = rnd(R["corner_radius"])
    v["fold_angle"] = rnd(R["fold_angle"])
    v["display_recess_depth"] = rnd(recess)
    v["hinge_clip_span"] = rnd(R["hinge_clip_span"])
    v["hinge_clip_center_y"] = rnd(-R["hinge_clip_span"] / 2.0)
    v["lens_island_depth"] = rnd(R["lens_island_depth"])
    v["lens_count"] = n_lens
    v["lens_depth"] = rnd(R["lens_island_depth"] + R["lens_extra_depth"])
    v["button_count"] = bn
    v["button_width"] = rnd(bw)
    v["button_seat_depth"] = rnd(R["button_seat_depth"])
    v["button_height"] = rnd(R["button_height"])
    v["button_pitch_x"] = rnd(bp)
    v["usb_c_width"] = rnd(R["usb_c_width"])
    v["usb_c_height"] = rnd(R["usb_c_height"])
    v["usb_c_depth"] = rnd(R["usb_c_depth"])
    v["card_slot_width"] = rnd(R["card_slot_width"])
    v["card_slot_height"] = rnd(R["card_slot_height"])
    v["card_slot_depth"] = rnd(R["card_slot_depth"])
    v["speaker_hole_count"] = int(R["speaker_hole_count"])
    v["speaker_hole_radius"] = rnd(R["speaker_hole_radius"])
    v["speaker_hole_depth"] = rnd(R["speaker_hole_depth"])
    v["speaker_pitch_y"] = rnd(R["speaker_pitch"])
    order = BOOKFOLD_PRESET_PARAM_ORDER + BOOKFOLD_ARCHETYPE_ONLY_PARAMS
    return {k: v[k] for k in order if k in v}, fallbacks


def bookfold_registry_extra(obj: dict, values: dict) -> dict:
    """Per-preset facts a reader needs that are not parameter values.

    `hinge_gap_mm` is the family's defining dimension and CANNOT be a manifest
    parameter: with no expressions in the graph format (yantra4d lane G-EXPR)
    every placement that carries it — the two halves' centre-Z values — is a
    frozen constant, and a constant cannot be driven by the quantity it was
    computed from. So it is recorded here, per preset, with its two sources.
    """
    closed = state(obj, "closed")
    openv = state(obj, "open")
    gap = None
    if closed.get("depth") is not None and values.get("half_thickness") is not None:
        gap = rnd(float(closed["depth"]) - 2.0 * float(values["half_thickness"]))
    derived_areas = [
        d.get("role") for d in obj.get("displays") or []
        if ((d.get("active_area_mm") or {}).get("width") is not None
            and (d.get("active_area_mm") or {}).get("derived"))
    ]
    return {
        "hinge_gap_mm": gap,
        "published_open_mm": {
            "height": openv.get("height"),
            "width": openv.get("width"),
            "depth": openv.get("depth"),
        },
        "derived_active_areas": derived_areas,
        "hinge_crease": (obj.get("hinge") or {}).get("crease"),
    }


#: Fold states for the book-fold family. The plan's L0 rung asks for a
#: continuous fold angle WITH named states; these are those states, and they are
#: emitted by this generator like every other preset so that no millimetre and
#: no degree in a cartridge is ever typed by hand.
BOOKFOLD_FOLD_STATES = [
    {
        "slug": "fold-state-closed",
        "label": {"en": "Fold state — closed", "es": "Estado — cerrado"},
        "kind": "fold_state",
        "source": (
            "Archetype fold state, not a device. Closed: the two half-frames "
            "face each other across the hinge gap, and the bounding box is the "
            "closed envelope a preset asserts against."
        ),
        "values": {"fold_angle": 0},
    },
    {
        "slug": "fold-state-half-open",
        "label": {"en": "Fold state — half open", "es": "Estado — medio abierto"},
        "kind": "fold_state",
        "source": (
            "Archetype fold state, not a device. 90 degrees: the fold's "
            "mid-travel, where the two halves and the hinge leaf are furthest "
            "from interfering."
        ),
        "values": {"fold_angle": 90},
    },
    {
        "slug": "fold-state-open",
        "label": {"en": "Fold state — open", "es": "Estado — abierto"},
        "kind": "fold_state",
        "source": (
            "Archetype fold state, not a device. 180 degrees: the halves are "
            "coplanar, the gap has closed itself, and the bounding box is the "
            "open envelope a preset asserts against."
        ),
        "values": {"fold_angle": 180},
    },
]


FAMILY = Family(
    slug="book-fold-phone",
    base=BOOKFOLD_ARCHETYPE_BASE,
    read=read_device_bookfold,
    derive=derive_bookfold,
    axis_mapping={
        "hinge_axis_length": "reference dimensions_mm.states.closed.height (the long axis, the hinge axis; equal to dimensions_mm.states.open.height on every object that publishes both)",
        "cover_half_width": "reference dimensions_mm.states.closed.width (the folding axis, closed)",
        "cover_half_width + camera_half_width": "reference dimensions_mm.states.open.width",
        "half_thickness": "reference dimensions_mm.states.open.depth (the open body is ONE half)",
        "2 x half_thickness + the hinge gap": "reference dimensions_mm.states.closed.depth",
    },
    source_line=(
        "envelope closed AND open height x width x depth as published; the "
        "half thickness is the published open depth and the hinge gap is the "
        "closed depth less twice it."
    ),
    registry_extra=bookfold_registry_extra,
    extra_presets=json.loads(json.dumps(BOOKFOLD_FOLD_STATES)),
)
