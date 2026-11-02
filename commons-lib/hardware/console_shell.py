# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires:
"""commons-lib/hardware/console_shell.py — the body of a desktop device.

Components (plan §2.3, Structure): `shell_body`, `upper_tier`, `side_cover`,
`vent_field`, `foot_set`, `stand_seat`, `handle`. Helpers (no CDG id):
`section_profile`, `face_plane`, `face_frame`. Each component takes its OWN parameter dict,
reads no manifest global and knows no assembly. First authored for
`home-console` (2026-11-01).

THE BODY IS A LOFT OF ROUNDED CROSS-SECTIONS. `shell_body` lofts (ruled) a run
of cross-sections taken across the width (the XZ plane), stepping front to rear
along Y. Every shaping parameter is a property of a section or of the run:

  * a section is a flat-bottomed rounded outline: bottom chamfer, drafted and
    optionally concave sides, rounded top corners, a crowned top
    (`section_profile`); its points are exact at the extremes, so the solid's
    bounding box is the published W x D x H to rounding, never a spline bulge;
  * the run sets the height along Y (a wedge, an upright, a shelf), rounds the
    plan corners by lofting quarter-circle caps of narrowing sections at the
    front and rear, and leans the front and rear faces by shearing every
    section plane (the skew);
  * the bottom is z = 0, flat, on every section (the gotcha canon: no poles).

The ruled loft is fast and exact; a flat-faceted fillet is the honest L1 form.
Every tool a component returns overshoots its face by at least 1 mm.

Inlined, never imported: `tools/inline_parts.py` copies this text into every
family `main.py` that declares it (ruling R2 on gate H8).
"""

import math

import cadquery as cq

#: Segments in one plan-corner cap (sections = segments + 1).
CAP_SEGMENTS = 3
#: Segments in one rounded top corner of a section.
CORNER_SEGMENTS = 3
#: Segments across a crowned top (even, so the apex x = 0 is a vertex).
CROWN_SEGMENTS = 6
#: Segments up a concave side.
CONCAVE_SEGMENTS = 4


def face_plane(frame):
    """A cq.Plane from a frame dict: origin, x_dir, normal (outward)."""
    return cq.Plane(
        origin=tuple(frame["origin"]), xDir=tuple(frame["x_dir"]), normal=tuple(frame["normal"])
    )


def face_frame(p):
    """The frame of one face of a box-like body, on the face's OUTER plane.

    Not a component: the shared placement convention. Local X runs along the
    face, local Y up it (or rearward on the top), local +Z outward. `u, v` are
    the face's own two global coordinates: (x, y) on top and bottom, (x, z) on
    front and rear, (y, z) on the sides.

    p: face, u, v, width, depth, top, center_x
    """
    hw, hd, u, v, cx = p["width"] / 2.0, p["depth"] / 2.0, p["u"], p["v"], p["center_x"]
    return {
        "top": {"origin": (u, v, p["top"]), "x_dir": (1, 0, 0), "normal": (0, 0, 1)},
        "bottom": {"origin": (u, v, 0.0), "x_dir": (1, 0, 0), "normal": (0, 0, -1)},
        "front": {"origin": (u, -hd, v), "x_dir": (1, 0, 0), "normal": (0, -1, 0)},
        "rear": {"origin": (u, hd, v), "x_dir": (-1, 0, 0), "normal": (0, 1, 0)},
        "right": {"origin": (cx + hw, u, v), "x_dir": (0, 1, 0), "normal": (1, 0, 0)},
        "left": {"origin": (cx - hw, u, v), "x_dir": (0, -1, 0), "normal": (-1, 0, 0)},
    }[p["face"]]


def section_profile(p):
    """The closed (x, z) outline of one cross-section, counter-clockwise.

    Not a component: the profile `shell_body` lofts. The point COUNT depends
    only on which features are on (chamfer, concavity, corner, crown), never on
    the size, so every section of one run lofts vertex to vertex. Extremes are
    vertices: x = +-width/2 at the foot of each side, z = height at the apex (or
    along a flat top), so the outline's box is exactly width x height.

    p: width, height, crown, draft_deg, concavity, corner_radius, chamfer
    """
    half, h, crown, c = p["width"] / 2.0, p["height"], p["crown"], p["chamfer"]
    tan_d = math.tan(math.radians(p["draft_deg"]))
    z_corner = h - crown
    top_half = half - (z_corner - c) * tan_d
    side_len = math.hypot(half - top_half, z_corner - c)
    r = min(p["corner_radius"], 0.45 * side_len, 0.45 * top_half)
    start = (half, c)
    ux, uz = (top_half - half) / side_len, (z_corner - c) / side_len
    a = (top_half - ux * r, z_corner - uz * r)
    chain = [start]
    if p["concavity"] > 0.0:
        for k in range(1, CONCAVE_SEGMENTS):
            s = k / CONCAVE_SEGMENTS
            x = half + (a[0] - half) * s - p["concavity"] * math.sin(math.pi * s)
            chain.append((x, c + (a[1] - c) * s))
    if r > 0.0:
        bx = top_half - r
        b = (bx, h - crown * (bx / top_half) ** 2)
        chain.append(a)
        for k in range(1, CORNER_SEGMENTS):
            t = k / CORNER_SEGMENTS
            chain.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * top_half + t * t * b[0],
                          (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * z_corner + t * t * b[1]))
        chain.append(b)
    else:
        chain.append((top_half, z_corner))
    if crown > 0.0:
        x_last = chain[-1][0]
        for k in range(1, CROWN_SEGMENTS // 2):
            x = x_last * (1 - 2 * k / CROWN_SEGMENTS)
            chain.append((x, h - crown * (x / top_half) ** 2))
    mirror = [(-x, z) for x, z in reversed(chain)]
    if c > 0.0:
        pts = [(-half + c, 0.0), (half - c, 0.0)] + chain
    else:
        pts = [(-half, 0.0)] + chain
        mirror = mirror[:-1]
    if crown > 0.0:
        pts.append((0.0, h))
    return pts + mirror


def _height_at(sections, yf):
    """Linear height along the run; `sections` is [[y_from_front, height], ...]."""
    if yf <= sections[0][0]:
        return sections[0][1]
    for (y0, h0), (y1, h1) in zip(sections, sections[1:]):
        if yf <= y1:
            return h0 + (h1 - h0) * (yf - y0) / max(y1 - y0, 1e-9)
    return sections[-1][1]


def shell_body(p):
    """The lofted body of a desktop device (one solid, flat bottom at base_z).

    CDG exposed: `device_envelope` (the outline every fit-to accessory mates
    to) and `cradle_seat` (its flat underside).

    p: width, depth, sections ([[y_from_front, height], ...], front 0 to rear
       depth), crown, draft_deg, concavity, corner_radius_top, edge_chamfer,
       corner_radius_plan, skew_deg, center_x, center_y, base_z
    """
    w, d = p["width"], p["depth"]
    secs = sorted([float(y), float(h)] for y, h in p["sections"])
    tan_s = math.tan(math.radians(p["skew_deg"]))
    shift = secs[-1][1] * tan_s
    span = d - shift
    rv = min(p["corner_radius_plan"], 0.45 * w, 0.45 * span)
    h_min = min(h for _, h in secs)
    chamfer = min(p["edge_chamfer"], 0.25 * h_min)
    crown = min(p["crown"], 0.5 * (h_min - chamfer))
    base = {
        "crown": crown, "draft_deg": p["draft_deg"], "concavity": p["concavity"],
        "corner_radius": min(p["corner_radius_top"], 0.4 * (h_min - chamfer - crown)),
        "chamfer": chamfer,
    }
    stations = []
    if rv >= 0.5:
        for k in range(CAP_SEGMENTS + 1):
            phi = math.radians(90.0 * k / CAP_SEGMENTS)
            stations.append((rv * (1 - math.cos(phi)), w - 2 * rv * (1 - math.sin(phi))))
    else:
        stations.append((0.0, w))
    inner = [y * span / d for y, _ in secs]
    lo, hi = stations[-1][0], span - stations[-1][0]
    for y in inner:
        if lo + 0.5 < y < hi - 0.5 and all(abs(y - s[0]) > 0.5 for s in stations):
            stations.append((y, w))
    rear = [(span - y, wk) for y, wk in reversed(stations[: CAP_SEGMENTS + 1 if rv >= 0.5 else 1])]
    stations = sorted(stations + rear)
    wires = []
    for yb, wk in stations:
        h = _height_at(secs, yb * d / span)
        prof = section_profile({**base, "width": wk, "height": h})
        y0 = yb - d / 2.0
        pts = [cq.Vector(x + p["center_x"], y0 + z * tan_s + p["center_y"], z + p["base_z"])
               for x, z in prof]
        wires.append(cq.Wire.makePolygon(pts, close=True))
    solid = cq.Solid.makeLoft(wires, ruled=True)
    return cq.Workplane("XY").add(solid)


def upper_tier(p):
    """A raised tier standing on a body: the step of a stepped console.

    CDG exposed: none of its own; it is part of `device_envelope`. A flat run of
    the same lofted section, standing `bite` into the body below so the two fuse
    once (the canon's 0.2 mm bite), its top at `top_z`.

    p: width, depth, top_z, bottom_z, crown, draft_deg, corner_radius_top,
       corner_radius_plan, skew_deg, center_x, center_y
    """
    h = p["top_z"] - p["bottom_z"]
    return shell_body({
        "width": p["width"], "depth": p["depth"], "sections": [[0.0, h], [p["depth"], h]],
        "crown": p["crown"], "draft_deg": p["draft_deg"], "concavity": 0.0,
        "corner_radius_top": p["corner_radius_top"], "edge_chamfer": 0.0,
        "corner_radius_plan": p["corner_radius_plan"], "skew_deg": p["skew_deg"],
        "center_x": p["center_x"], "center_y": p["center_y"], "base_z": p["bottom_z"],
    })


def side_cover(p):
    """A removable side panel: the outer `thickness` of a body's side, moved out.

    CDG exposed: `mounting_surface` (its inner face). It is the body's own outline
    intersected with a slab, so a cover always follows the body plan; `offset`
    moves it outward along X (the kernel-side explode variable).

    p: body (a solid), side (+1 right, -1 left), outer_x (the side's x),
       thickness, offset
    """
    s = p["side"]
    inner_x = p["outer_x"] - s * p["thickness"]
    lo, hi = sorted((inner_x, p["outer_x"] + s * 5.0))
    slab = cq.Workplane("XY").box(hi - lo, 4000.0, 4000.0).translate(((lo + hi) / 2.0, 0.0, 0.0))
    cover = p["body"].intersect(slab)
    return cover.translate((s * p["offset"], 0.0, 0.0))


def _vent_points(pattern, width, height, pitch):
    """Hole centres for a vent pattern, centred on (0, 0), inside width x height."""
    if pattern == "radial":
        rmax = min(width, height) / 2.0
        pts = [(0.0, 0.0)]
        ring = 1
        while ring * pitch <= rmax:
            r = ring * pitch
            n = max(int(2 * math.pi * r / pitch), 6)
            pts.extend((r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n))
                       for i in range(n))
            ring += 1
        return pts
    nu = max(int(width // pitch), 1)
    nv = max(int(height // pitch), 1)
    pts = []
    for j in range(nv):
        v = (j - (nv - 1) / 2.0) * pitch
        staggered = pattern == "hex" and j % 2 == 1 and nu > 1
        count = nu - 1 if staggered else nu
        pts.extend(((i - (count - 1) / 2.0) * pitch, v) for i in range(count))
    return pts


def vent_field(p):
    """A vent field: ONE 2-D region on a face, extruded once (the tool).

    CDG exposed: `vent_face` — the bounded region that must stay unobstructed.
    Patterns: `slots` (rows of slots spanning the width), `grid` (square holes),
    `hex` (hexagons, staggered rows), `holes` (round), `radial` (round holes on
    rings). The tool spans `overshoot` outside the face to `depth` inside.

    p: frame (origin, x_dir, normal), pattern, width, height, pitch, hole_size,
       depth, overshoot
    """
    plane = face_plane(p["frame"])
    wp = cq.Workplane(plane).workplane(offset=p["overshoot"])
    size = p["hole_size"]
    if p["pattern"] == "slots":
        nv = max(int(p["height"] // p["pitch"]), 1)
        pts = [(0.0, (j - (nv - 1) / 2.0) * p["pitch"]) for j in range(nv)]
        sk = wp.pushPoints(pts).slot2D(max(p["width"], size * 1.01), size)
    else:
        pts = _vent_points(p["pattern"], p["width"], p["height"], p["pitch"])
        wp = wp.pushPoints(pts)
        if p["pattern"] == "grid":
            sk = wp.rect(size, size)
        elif p["pattern"] == "hex":
            sk = wp.polygon(6, size)
        else:
            sk = wp.circle(size / 2.0)
    return sk.extrude(-(p["depth"] + p["overshoot"]))


def _foot_points(count, sx, sy):
    hx, hy = sx / 2.0, sy / 2.0
    table = {
        1: [(0.0, 0.0)],
        2: [(-hx, 0.0), (hx, 0.0)],
        3: [(-hx, -hy), (hx, -hy), (0.0, hy)],
        4: [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)],
        5: [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy), (0.0, 0.0)],
        6: [(-hx, -hy), (0.0, -hy), (hx, -hy), (hx, hy), (0.0, hy), (-hx, hy)],
    }
    return table[max(1, min(int(count), 6))]


def foot_set(p):
    """The feet under a body: `count` round pads (1-6) on an inset rectangle.

    CDG exposed: none; the feet are projections a maker's envelope excludes.
    Each foot stands `bite` up into the body so the assembly fuses them once.

    p: count, diameter, height, span_x, span_y, center_x, center_y, base_z, bite
    """
    pts = [(x + p["center_x"], y + p["center_y"])
           for x, y in _foot_points(p["count"], p["span_x"], p["span_y"])]
    return (
        cq.Workplane("XY").workplane(offset=p["base_z"] - p["height"])
        .pushPoints(pts).circle(p["diameter"] / 2.0).extrude(p["height"] + p["bite"])
    )


def stand_seat(p):
    """The seat a stand registers in, cut into the underside (the tool).

    CDG exposed: `stand_seat` — consumed by the planned `console-stand` family.
    `base_disc`: a round recess (a screw-on base); `cradle`: two parallel grooves
    along Y (a slide-in cradle).

    p: kind ("base_disc"|"cradle"), diameter, depth, groove_width, groove_pitch,
       groove_length, center_x, center_y, base_z
    """
    z0 = p["base_z"] - 1.0
    h = p["depth"] + 1.0
    if p["kind"] == "cradle":
        tool = (
            cq.Workplane("XY").workplane(offset=z0)
            .pushPoints([(p["center_x"] - p["groove_pitch"] / 2.0, p["center_y"]),
                         (p["center_x"] + p["groove_pitch"] / 2.0, p["center_y"])])
            .rect(p["groove_width"], p["groove_length"]).extrude(h)
        )
        return tool
    return (
        cq.Workplane("XY").workplane(offset=z0).center(p["center_x"], p["center_y"])
        .circle(p["diameter"] / 2.0).extrude(h)
    )


def handle(p):
    """A carry handle: a U bail behind the rear face, under the top edge.

    CDG exposed: `grip_surface`. Two posts bite into the rear face and a bar
    joins them `reach` behind it — one solid.

    p: span, reach, thickness, top_z, rear_y, center_x, bite
    """
    t = p["thickness"]
    zc = p["top_z"] - t / 2.0
    post_len = p["reach"] + p["bite"]
    yc = p["rear_y"] - p["bite"] + post_len / 2.0
    out = None
    for sx in (-1.0, 1.0):
        post = cq.Workplane("XY").box(t, post_len, t).translate(
            (p["center_x"] + sx * (p["span"] - t) / 2.0, yc, zc))
        out = post if out is None else out.union(post)
    bar = cq.Workplane("XY").box(p["span"], t, t).translate(
        (p["center_x"], p["rear_y"] + p["reach"] - t / 2.0, zc))
    return out.union(bar)
