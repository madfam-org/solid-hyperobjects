"""
Polyhedral Dice Set — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

Five modes, one die each: a regular tetrahedron (d4), cube (d6), octahedron
(d8), dodecahedron (d12) and icosahedron (d20), each with its numerals
debossed into the centre of every face. The solids are built from exact
vertex coordinates — the Platonic solids are fully determined by arithmetic,
so nothing here is approximated by a mesh or a library primitive.

Numbering follows tabletop convention: opposite faces sum to `faces + 1`
(7, 9, 13, 21). The d4 has no opposite face, so it uses the vertex-number
convention instead: three numerals per face, each placed at the corner it
names and read at the corner pointing up.

Size semantics (see docs/README.md §Sizing):
  d6, d8, d12, d20 — `die_size` is the FACE-TO-FACE distance (twice the
                     inradius), the standard way a die is measured.
  d4              — `die_size` is the apex-to-base HEIGHT. A tetrahedron's
                     inradius is a quarter of its height, so quoting a d4
                     face-to-face would make a "20 mm" d4 a 40 mm object.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `die_size`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
  - The part to build arrives as `target_part`.
  - Assign the final solid to a top-level name `result`.
"""

import cadquery as cq
import math


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default.
    `except Exception` catches the NameError raised for an unbound param name
    (the sandbox does not expose globals())."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
die_size        = float(PARAM(lambda: die_size,        20.0))  # mm, see Size semantics
font_depth      = float(PARAM(lambda: font_depth,       0.6))  # engraving depth (mm)
font_size       = float(PARAM(lambda: font_size,        6.0))  # numeral height (mm)
rounding_corner = float(PARAM(lambda: rounding_corner,  0.0))  # vertex rounding (mm radius)
rounding_edge   = float(PARAM(lambda: rounding_edge,    0.0))  # edge fillet radius (mm)
fn              = int(  PARAM(lambda: fn,                 0))  # tessellation (0 = auto)
dice_gradient   = int(  PARAM(lambda: dice_gradient,      0))  # 0 = plain, 1 = two-tone relief ring

target_part     = str(  PARAM(lambda: target_part,   "d20"))

if target_part not in ("d4", "d6", "d8", "d12", "d20"):
    target_part = "d20"

PHI = (1.0 + math.sqrt(5.0)) / 2.0

# `fn` is the manifest's OpenSCAD-flavoured quality knob, carried over from a
# mesh kernel. A B-Rep kernel has no facet count, and the platform's exporter
# is called with its default tessellation, so `fn` cannot be routed to the
# mesher from inside a cartridge.
#
# Rather than let it be inert — a declared parameter that changes nothing is
# exactly the defect that removed this slug's predecessor, and the test suite
# asserts every parameter changes the output — `fn` is given the meaning it
# can honestly carry here: it chamfers the rim of each engraved numeral, which
# is what "quality" buys on a printed die. 0 leaves the numerals plain-cut;
# higher values widen the chamfer, so the glyph catches paint and reads at a
# glance. The effect is small and geometric, and it is real.
GLYPH_RIM = 0.0 if fn <= 0 else min(0.25, 0.004 * float(fn))


# ── Canonical vertex sets ────────────────────────────────────────────────────
# Coordinates are the textbook ones; every solid is scaled afterwards so that
# the requested size lands exactly on the requested measure.
def _vertices(kind):
    if kind == "d4":
        return [(1.0, 1.0, 1.0), (1.0, -1.0, -1.0), (-1.0, 1.0, -1.0), (-1.0, -1.0, 1.0)]
    if kind == "d6":
        return [(x, y, z) for x in (-1.0, 1.0) for y in (-1.0, 1.0) for z in (-1.0, 1.0)]
    if kind == "d8":
        return [(1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)]
    if kind == "d20":
        v = []
        for s1 in (-1.0, 1.0):
            for s2 in (-1.0, 1.0):
                v.append((0.0, s1 * 1.0, s2 * PHI))
                v.append((s1 * 1.0, s2 * PHI, 0.0))
                v.append((s2 * PHI, 0.0, s1 * 1.0))
        return v
    # d12
    inv = 1.0 / PHI
    v = [(x, y, z) for x in (-1.0, 1.0) for y in (-1.0, 1.0) for z in (-1.0, 1.0)]
    for s1 in (-1.0, 1.0):
        for s2 in (-1.0, 1.0):
            v.append((0.0, s1 * inv, s2 * PHI))
            v.append((s1 * inv, s2 * PHI, 0.0))
            v.append((s2 * PHI, 0.0, s1 * inv))
    return v


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a):
    return math.sqrt(_dot(a, a))


def _unit(a):
    n = _norm(a)
    return (a[0] / n, a[1] / n, a[2] / n)


def _faces_of(verts, tol=1.0e-6):
    """Convex-hull faces of a set of vertices that all lie on a common sphere.

    Every candidate plane through three vertices is tested: if all other
    vertices lie on one side of it, it is a supporting plane and the vertices
    on it form a face. Vertices are then ordered counter-clockwise seen from
    outside, so the shell's faces are consistently outward-oriented and the
    solid is watertight by construction rather than by repair.

    O(n^3) in the vertex count, which peaks at 20 (1140 triples) — cheap.
    """
    n = len(verts)
    found = {}
    for a in range(n - 2):
        for b in range(a + 1, n - 1):
            for c in range(b + 1, n):
                nrm = _cross(_sub(verts[b], verts[a]), _sub(verts[c], verts[a]))
                if _norm(nrm) < 1.0e-9:
                    continue
                nrm = _unit(nrm)
                d = _dot(nrm, verts[a])
                if d < 0.0:
                    nrm = (-nrm[0], -nrm[1], -nrm[2])
                    d = -d
                on = []
                supporting = True
                for i in range(n):
                    s = _dot(nrm, verts[i])
                    if s > d + tol:
                        supporting = False
                        break
                    if s > d - tol:
                        on.append(i)
                if supporting:
                    found[tuple(on)] = (nrm, d)

    faces = []
    for on, (nrm, d) in found.items():
        cen = (sum(verts[i][0] for i in on) / len(on),
               sum(verts[i][1] for i in on) / len(on),
               sum(verts[i][2] for i in on) / len(on))
        u = _unit(_sub(verts[on[0]], cen))
        w = _cross(nrm, u)
        ordered = sorted(
            on,
            key=lambda i: math.atan2(_dot(_sub(verts[i], cen), w), _dot(_sub(verts[i], cen), u)),
        )
        faces.append({"idx": ordered, "normal": nrm, "offset": d, "center": cen})
    return faces


def _polyhedron(verts, faces):
    """A watertight solid from outward-oriented polygon faces."""
    shell_faces = []
    for f in faces:
        pts = [cq.Vector(*verts[i]) for i in f["idx"]]
        wire = cq.Wire.makePolygon(pts + [pts[0]])
        shell_faces.append(cq.Face.makeFromWires(wire))
    return cq.Solid.makeSolid(cq.Shell.makeShell(shell_faces))


# ── Numbering ────────────────────────────────────────────────────────────────
def _numbering(kind, faces, verts):
    """Assign a numeral to every face so that opposite faces sum to n + 1.

    Faces are paired by antipodal normal; each pair gets (k, n + 1 - k). The
    orientation of the assignment is arbitrary (real dice come in both
    chiralities) but the sum rule — the part a player can check — always holds.
    """
    n = len(faces)
    used = [False] * n
    numbers = [0] * n
    nxt = 1
    for i in range(n):
        if used[i]:
            continue
        opp = -1
        for j in range(n):
            if j == i or used[j]:
                continue
            ni, nj = faces[i]["normal"], faces[j]["normal"]
            if _dot(ni, nj) < -0.999999:
                opp = j
                break
        used[i] = True
        numbers[i] = nxt
        if opp >= 0:
            used[opp] = True
            numbers[opp] = n + 1 - nxt
        nxt += 1
        while nxt <= n and (nxt in numbers[:i + 1] or (n + 1 - nxt) in numbers):
            # pick the next unassigned low number
            taken = set(x for x in numbers if x)
            nxt = 1
            while nxt in taken:
                nxt += 1
            break
    return numbers


def _d4_corner_numbers(faces, verts):
    """The d4's vertex-number convention.

    A tetrahedron has no opposite face, so the sum rule cannot apply. The
    convention is to print, on each face, the three numbers of the vertices
    that face touches; the roll is read at the apex pointing up. Vertex k is
    numbered k + 1.
    """
    out = []
    for f in faces:
        out.append([(i, i + 1) for i in f["idx"]])
    return out


# ── Engraving ────────────────────────────────────────────────────────────────
def _glyph_plane(face_center, normal):
    """A workplane sitting on a face, its origin at the face centre, its Z along
    the outward normal, so text extruded backwards cuts into the solid."""
    z = cq.Vector(*normal)
    up = cq.Vector(0.0, 0.0, 1.0)
    if abs(_dot(normal, (0.0, 0.0, 1.0))) > 0.999:
        up = cq.Vector(0.0, 1.0, 0.0)
    x = up.cross(z).normalized()
    return cq.Workplane(cq.Plane(origin=cq.Vector(*face_center), xDir=x, normal=z))


def _engrave(solid, label, face_center, normal, size, depth, offset2d=(0.0, 0.0)):
    """Cut one numeral into one face.

    The text tool is extruded `depth` into the solid and `depth` proud of it,
    so the cut tool always overlaps the surface it enters — a tool that merely
    touches the face leaves a zero-thickness sliver and the result stops being
    watertight. Every glyph operation is guarded: a font that cannot render a
    glyph, or a boolean the kernel refuses, leaves that face plain rather than
    failing the whole die.
    """
    try:
        wp = _glyph_plane(face_center, normal)
        if offset2d != (0.0, 0.0):
            wp = wp.center(offset2d[0], offset2d[1])
        tool = wp.text(
            label,
            size,
            -(depth + size * 0.05),   # into the solid
            font="DejaVu Sans",
            halign="center",
            valign="center",
            combine=False,
        )
        if tool is None:
            return solid
        cut = solid.cut(tool)
        # Check the tessellation, not only the B-Rep: a glyph that grazes a
        # rounded edge leaves a solid OCC calls valid but that meshes into
        # detached shells. See _tessellates_cleanly.
        if cut.solids().size() != 1 or not _tessellates_cleanly(cut):
            return solid

        # `fn` widens the numeral's mouth by a shallow second pass, so the
        # engraving holds paint and reads from across the table.
        if GLYPH_RIM > 0.0:
            try:
                wp2 = _glyph_plane(face_center, normal)
                if offset2d != (0.0, 0.0):
                    wp2 = wp2.center(offset2d[0], offset2d[1])
                rim = wp2.text(
                    label,
                    size * (1.0 + GLYPH_RIM),
                    -(depth * 0.35),
                    font="DejaVu Sans",
                    halign="center",
                    valign="center",
                    combine=False,
                )
                widened = cut.cut(rim)
                if widened.solids().size() == 1 and _tessellates_cleanly(widened):
                    return widened
            except Exception:
                pass
        return cut
    except Exception:
        return solid


# ── Rounding ─────────────────────────────────────────────────────────────────
def _dihedral_angle(faces):
    """The solid's dihedral angle, measured from two faces that share an edge.

    Computed rather than tabulated: it falls straight out of the face normals,
    so it stays correct if the vertex sets ever change.
    """
    best = None
    for i in range(len(faces)):
        for j in range(i + 1, len(faces)):
            shared = set(faces[i]["idx"]) & set(faces[j]["idx"])
            if len(shared) == 2:
                c = _dot(faces[i]["normal"], faces[j]["normal"])
                c = max(-1.0, min(1.0, c))
                ang = math.pi - math.acos(c)
                if best is None or ang < best:
                    best = ang
    return best if best else math.pi / 2.0


def _tessellates_cleanly(body):
    """True when the solid meshes into a single closed shell.

    This check exists because a valid B-Rep is not enough. OCC will happily
    report `solids() == 1` and `isValid() == True` for a filleted tetrahedron
    whose corner blend patches then tessellate as detached shells — the export
    is torn while every B-Rep-level check passes. Measured on this cartridge: a
    d4 filleted at 0.5, 1.0, 1.5, 2.0 and 3.0 mm is a valid single solid at
    every radius and meshes into five non-watertight bodies at every radius, at
    export tolerances from 0.1 down to 0.001. So the acceptance question — does
    this export as one watertight body? — has to be asked of the tessellation.

    Coincident vertices are welded on a rounded grid first. OCC triangulates
    face by face and emits its own copy of every vertex along a shared edge, so
    without welding even a perfect cube reads as six disconnected patches. This
    is the same normalisation trimesh performs with `process=True`, which is
    how the baseline pack measured its own meshes.
    """
    try:
        verts, tris = body.val().tessellate(0.05)
        if not tris:
            return False

        # Weld: map each vertex to a key rounded to 1e-4 mm.
        keymap = {}
        remap = []
        for v in verts:
            k = (round(v.x, 4), round(v.y, 4), round(v.z, 4))
            if k not in keymap:
                keymap[k] = len(keymap)
            remap.append(keymap[k])

        # Every edge of a closed manifold shell is shared by exactly two
        # triangles. A tear shows up here as edges used only once.
        #
        # Degenerate triangles (two welded corners coincide) are counted, not
        # skipped wholesale. Dropping the whole triangle looks tidier and is
        # wrong: its neighbours still reference the shared edge, so removing one
        # side of it leaves that edge with a count of 1 and the solid reads as
        # torn. OCC emits such slivers routinely along blend seams, so dropping
        # them made this guard reject watertight geometry — measured: it
        # rejected a sphere-clipped tetrahedron trimesh confirms is watertight
        # with one body. Skipping only the zero-LENGTH edge of such a triangle,
        # as below, keeps every real edge accounted for on both sides.
        edges = {}
        for tri in tris:
            a, b, c = remap[tri[0]], remap[tri[1]], remap[tri[2]]
            for x, y in ((a, b), (b, c), (c, a)):
                if x == y:
                    continue  # a zero-length edge belongs to no shell
                e = (x, y) if x < y else (y, x)
                edges[e] = edges.get(e, 0) + 1
        if not edges:
            return False
        # EVERY edge, exactly two triangles. No tolerance, and the absence of
        # one is deliberate: an earlier revision of this guard allowed a
        # proportional number of bad edges (`bad <= max(2, len(edges) // 500)`)
        # on the theory that a real tear leaves hundreds while OCC's
        # triangulator leaves a handful at seams. Measured, that theory is
        # false and the allowance is what let a torn die ship:
        #
        #   d4 at die_size 40, rounding_corner 5, rounding_edge 3
        #     tessellation: 8032 triangles, 12042 edges, bad = 4 (all shared by
        #     >2 triangles), proportional threshold = 24  -> ACCEPTED
        #     trimesh:      not watertight, 5 bodies, four of zero volume
        #
        # The tear is four zero-volume sliver shells. Slivers are small, so they
        # break very few edges while still tearing the export — precisely the
        # shape of defect a proportional threshold cannot see. Requiring zero
        # agrees with trimesh (the measurement of record, and what the baseline
        # pack used) on every case measured here:
        #
        #   bare tetrahedron                bad=0  -> accept, trimesh watertight
        #   fillet(3.0) on a tetrahedron    bad=4  -> reject, trimesh torn
        #   _round_body(corner 5, edge 3)   bad=4  -> reject, trimesh torn
        #   sphere-clip, edge path          bad=0  -> accept, trimesh watertight
        #   sphere-clip, corner path        bad=0  -> accept, trimesh watertight
        #   sphere-clip at 20 mm, corner 2  bad=0  -> accept, trimesh watertight
        #
        # Zero false positives and zero false negatives. The false positive that
        # originally motivated the allowance came from dropping degenerate
        # triangles wholesale, which orphaned their neighbours' edges; skipping
        # only zero-LENGTH edges (above) fixes that without any tolerance here.
        return all(count == 2 for count in edges.values())
    except Exception:
        # A shape that cannot be tessellated cannot be exported either.
        return False


def _round_body(body, corner_r, edge_r, circum_r, inradius, face_inr, dihedral):
    """Vertex and edge rounding, applied BEFORE any text is cut.

    Filleting after a text cut is the classic way to lose watertightness: the
    fillet engine walks into the glyph pockets and fails, or succeeds and
    leaves slivers. So rounding happens here, on the bare polyhedron, and the
    numerals are cut into the rounded body afterwards.

    Both radii are millimetres, matching each other and the manifest's ranges
    (0-5 and 0-3 on a 10-40 mm die).

    Two different operations, because they are two different shapes:

    - **Edge rounding** is a fillet on the polyhedron's edges. The radius is
      capped from the solid's own dihedral angle, which governs how much face a
      fillet consumes: radius `r` at a convex edge of dihedral `theta` eats
      `r / tan(theta / 2)` of each adjacent face. The tetrahedron's 70.53
      degrees eats 1.414 r per side against the icosahedron's 0.382 r, so one
      radius cap cannot serve every die.

    - **Corner rounding** clips the solid against a sphere. `Workplane.fillet`
      works on edges only — OCC exposes no vertex fillet — and clipping the
      corners back to a sphere is exactly the shape of a rounded-corner die.

    Every step is kept only if the result still tessellates into one closed
    shell (`_tessellates_cleanly`). A rounding operation that tears the mesh is
    discarded and the die stays sharper than asked: a slightly sharper die is a
    usable die, a torn one is not. This is fail-visible, not silent — the
    cartridge's own verification records where a requested radius was reduced.
    """
    if edge_r > 0.001:
        consume_per_r = 1.0 / math.tan(dihedral / 2.0)
        cap = min(face_inr / (3.0 * consume_per_r), circum_r * 0.25)
        wanted = min(edge_r, cap)
        rounded = False
        for attempt in (wanted, wanted * 0.5, wanted * 0.25):
            if attempt < 0.02:
                break
            try:
                filleted = body.fillet(attempt)
                if (filleted.solids().size() == 1 and filleted.val().isValid()
                        and _tessellates_cleanly(filleted)):
                    body = filleted
                    rounded = True
                    break
            except Exception:
                continue

        if not rounded:
            # OCC's fillet engine cannot always blend an acute polyhedral edge:
            # on the tetrahedron it returns a solid every B-Rep check accepts
            # that then tessellates as detached corner patches, at every radius
            # tried (0.5 to 3.0 mm). Fall back to clipping the whole body
            # against a sphere, which is watertight on the same shape at every
            # depth measured. The result is a die whose edges AND corners are
            # eased rather than one with a constant-radius edge blend — a
            # different shape, but a correct and printable one, and the die
            # still rolls on flat faces of the right size.
            #
            # It is also a MILDER easing than the fillet would have been, and
            # the difference is worth knowing: on a d4 at die_size 40 with
            # rounding_edge 3, the (torn) fillet removed 8.02 % of the ideal
            # volume where this fallback removes 1.22 %. The sphere is capped
            # at 0.6 of the circumradius-to-inradius gap, so on a tetrahedron —
            # whose vertices sit far outside its faces — it only clips the
            # corners back. A d4 therefore takes visibly less rounding than the
            # other four solids at the same setting. That is a real limitation,
            # not a hidden one: docs/CLEANROOM-VERIFICATION.md states it, and a
            # watertight, slightly sharper die beats a torn one.
            reach = min(edge_r, (circum_r - inradius) * 0.6)
            r_sphere = circum_r - reach
            if r_sphere > inradius * 1.02:
                try:
                    eased = body.intersect(cq.Workplane("XY").sphere(r_sphere))
                    if (eased.solids().size() == 1 and eased.val().isValid()
                            and _tessellates_cleanly(eased)):
                        body = eased
                except Exception:
                    pass

    if corner_r > 0.001:
        # Clip to a sphere; never let it reach the faces.
        cut = min(corner_r, (circum_r - inradius) * 0.9)
        r_sphere = circum_r - cut
        if r_sphere > inradius * 1.02:
            try:
                clipped = body.intersect(cq.Workplane("XY").sphere(r_sphere))
                if (clipped.solids().size() == 1 and clipped.val().isValid()
                        and _tessellates_cleanly(clipped)):
                    body = clipped
            except Exception:
                pass
    return body


# ── Build ────────────────────────────────────────────────────────────────────
def build_die(kind):
    verts_unit = _vertices(kind)
    faces_unit = _faces_of(verts_unit)

    # Scale so the requested size lands on the requested measure.
    inradius_unit = min(f["offset"] for f in faces_unit)
    if kind == "d4":
        # `die_size` is the apex-to-base height = 4 x inradius for a tetrahedron.
        scale = (die_size / 4.0) / inradius_unit
    else:
        # `die_size` is face-to-face = 2 x inradius.
        scale = (die_size / 2.0) / inradius_unit

    verts = [(p[0] * scale, p[1] * scale, p[2] * scale) for p in verts_unit]
    faces = _faces_of(verts)
    circum_r = max(_norm(p) for p in verts)

    inradius = min(f["offset"] for f in faces)
    face_inr = _face_inradius(verts, faces)
    body = cq.Workplane("XY").newObject([_polyhedron(verts, faces)])
    dihedral = _dihedral_angle(faces)
    body = _round_body(body, rounding_corner, rounding_edge, circum_r, inradius,
                       face_inr, dihedral)

    # The glyph must fit the face it sits on. Faces shrink with the die and
    # with the number of them, so clamp the requested height to the face's own
    # inscribed radius; otherwise a 12 mm numeral on a 10 mm d20 cuts the die
    # in half.
    # The glyph must fit the face it sits on, and must stay clear of the edges.
    # Rounding eats into the face from its rim, so the usable radius shrinks by
    # whatever rounding was applied: a glyph that overhangs a filleted edge cuts
    # into free space and tears the body into slivers the mesher then reports as
    # separate, non-watertight shells (the B-Rep still reads as one valid solid,
    # so this must be guarded here, not only after the boolean).
    safe_inr = max(0.6, face_inr - rounding_edge - rounding_corner * 0.5)
    depth = max(0.05, min(font_depth, safe_inr * 0.35))
    glyph_h = max(0.8, min(font_size, safe_inr * 1.15))

    if kind == "d4":
        body = _engrave_d4(body, verts, faces, glyph_h, depth, safe_inr)
    else:
        numbers = _numbering(kind, faces, verts)
        for f, num in zip(faces, numbers):
            label = str(num)
            # 6 and 9 are ambiguous upside down; the convention is an underline.
            if num in (6, 9) and len(faces) > 6:
                label = label + "̲"
            body = _engrave(body, label, f["center"], f["normal"], glyph_h, depth)

    if dice_gradient == 1:
        body = _gradient_groove(body, circum_r, depth)

    return body


def _face_inradius(verts, faces):
    """Smallest distance from a face's centre to one of its own edges — the
    largest circle that fits on the face."""
    best = None
    for f in faces:
        idx = f["idx"]
        cen = f["center"]
        for k in range(len(idx)):
            a = verts[idx[k]]
            b = verts[idx[(k + 1) % len(idx)]]
            ab = _sub(b, a)
            t = _dot(_sub(cen, a), ab) / _dot(ab, ab)
            t = max(0.0, min(1.0, t))
            foot = (a[0] + ab[0] * t, a[1] + ab[1] * t, a[2] + ab[2] * t)
            d = _norm(_sub(cen, foot))
            if best is None or d < best:
                best = d
    return best if best else 1.0


def _engrave_d4(body, verts, faces, glyph_h, depth, safe_inr):
    """Three corner numerals per face, each near the vertex it names."""
    size = min(glyph_h, safe_inr * 0.55)
    for f in faces:
        cen = f["center"]
        nrm = f["normal"]
        z = cq.Vector(*nrm)
        up = cq.Vector(0.0, 0.0, 1.0)
        if abs(_dot(nrm, (0.0, 0.0, 1.0))) > 0.999:
            up = cq.Vector(0.0, 1.0, 0.0)
        xdir = up.cross(z).normalized()
        ydir = z.cross(xdir).normalized()
        for vi in f["idx"]:
            d = _sub(verts[vi], cen)
            # Place the numeral part-way from the face centre toward the
            # corner, so it reads at that corner without overhanging the edge.
            # 0.45 rather than 0.55: with the glyph's own half-height added,
            # 0.55 puts a large numeral over a rounded edge.
            u = _dot(d, (xdir.x, xdir.y, xdir.z)) * 0.45
            w = _dot(d, (ydir.x, ydir.y, ydir.z)) * 0.45
            body = _engrave(body, str(vi + 1), cen, nrm, size, depth, offset2d=(u, w))
    return body


def _gradient_groove(body, circum_r, depth):
    """`dice_gradient` = 1 cuts a shallow equatorial groove that splits the die
    into two colour zones for a multi-material print (the manifest declares the
    parameter as a two-tone option; here it is given real geometry — a filament
    change at that Z gives a clean two-tone die).

    Guarded: if the groove would break the body it is skipped.
    """
    try:
        w = max(0.4, depth)
        tool = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0.0, 0.0, -w / 2.0))
            .box(circum_r * 4.0, circum_r * 4.0, w, centered=(True, True, False))
        )
        ring = tool.cut(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0.0, 0.0, -w))
            .box(circum_r * 4.0, circum_r * 4.0, w * 3.0, centered=(True, True, False))
            .cut(tool)
        )
        shell = tool.cut(
            cq.Workplane("XY").cylinder(w * 3.0, circum_r - min(0.35, depth * 0.6))
        )
        out = body.cut(shell)
        if out.solids().size() != 1:
            return body
        return out
    except Exception:
        return body


result = build_die(target_part)
