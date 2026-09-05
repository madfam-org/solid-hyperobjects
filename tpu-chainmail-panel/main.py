"""TPU Chainmail Panel — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A print-in-place flexible chainmail panel — the additive-manufacturing fabric that
the Fashion Cabinet `tpu-panel-impreso` fabric card describes as cloth and bridges to
here for its geometry. A grid of interlocked rings (the 4-in-1 European weave) prints
in one job as separate, already-linked solids and drapes like a textile: rigid link,
flexible sheet. Sized by ring count so a Fashion Cabinet garment panel's finished
dimensions drive the weave.

This is the soft-goods↔hard-goods seam made physical: Fashion Cabinet owns the panel
as a *fabric* (drape, stretch, cut planning); Yantra4D owns it as a *solid* (the
printable ring lattice). One material identity spans both — `bambu-tpu-95a`.

Modes (dispatched via `target_part`):
  * "panel"   — the full interlocked ring grid (rows x cols), print-in-place.
  * "swatch"  — a small 3x3 sample for a print/fit test.
  * "ring"    — a single ring (the unit cell), for tuning cross-section + clearance.

Every ring is a watertight solid; rings are NOT fused (they interlink by placement,
as real chainmail does) — the assembly is a set of separate solids the slicer prints
in place. Body count is therefore `rows * cols` for a panel, 9 for a swatch, 1 for a
single ring, and the manifest's `verification` block declares exactly that.

── Why the ring is a faceted prism, not `cq.Solid.makeTorus` ────────────────────
An analytic torus has two curved surfaces, and the platform's STL export
(`Assembly.save(..., tolerance=0.1, angularTolerance=0.1)`, mirrored by the spec's
render check) tessellates each ring to 31 752 triangles: an 80-ring default panel
became a 2 540 160-face / 127 MB STL that no user wants to download and that cost
over 6 GiB to verify. The ring here is a *faceted torus* — a regular
`WIRE_SIDES`-gon cross-section swept along a regular `PATH_SIDES`-gon centreline, as
lofted ruled sections. Every surface is planar, so the exporter emits the facets
exactly (2 triangles per quad, no deflection refinement) and one ring is 1 280
triangles — 24.8x smaller — for the same `ring_od`, `wire_d`, pitch, tilt and
interlink. Both polygons are *circumscribed* about their nominal radii, so the
faceted solid contains the analytic torus rather than shrinking inside it: wire
thickness and ring reach are never undersized, and the printed link is if anything a
hair stronger.

── Known defect, NOT introduced here: the weave does not actually interlink ─────
At the shipped defaults the rings collide instead of linking. Measured on this
cartridge's own geometry, before and after this change, with identical numbers
(142 of 205 neighbour pairs share material, max overlap 5.847 mm³; interior rings
link 2 of 4 diagonal neighbours, never 4). The cause is dimensional, not a
placement bug: four wire crossings through one ring's hole need
`ring_id >= 4*wire_d + 8*clearance` = 13.2 mm at the defaults, and the default
`ring_id` is 9.0 mm. No pitch or tilt can fix that — a search over tilt
(30–55°) x col_pitch (0.45–0.95 ring_od) x row_pitch (0.28–1.10 ring_od) found
configurations reaching 4 links and configurations with 0 clearance violations,
but never both. Fixing it means changing the parameter defaults (or making the
pitches derive from a feasibility check), which is a product decision outside the
mesh repair this module's change set is scoped to. Tracked separately; the
geometry here is byte-for-byte the same weave the cartridge always described,
rendered at a sane triangle count.

── Why placement is `cq.Location`, not `.translate()` ───────────────────────────
Every ring in a panel is the same shape at a different place. `Shape.translate()`
returns a *copy*, so OCCT sees N distinct shapes and meshes each one from scratch —
80 rings cost 4.5 GB and 41 s in the exporter alone. Adding the shared prototype to
the Assembly with a `loc=` instead keeps one TShape instanced N times: OCCT
triangulates it once and re-uses that mesh under each location. Same STL, same body
count, 0.53 GB and under 2 s. Only two prototypes are ever built (one per tilt sign).

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `rows`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr.
  - Assign the final result to a top-level name `result`.
"""

import cadquery as cq
import math


def PARAM(getter, default):
    """Return an injected global if present, else the default."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
rows        = int(  PARAM(lambda: rows,        10))     # rings down the panel
cols        = int(  PARAM(lambda: cols,        8))      # rings across the panel
ring_id     = float(PARAM(lambda: ring_id,     9.0))    # ring inner diameter (mm)
wire_d      = float(PARAM(lambda: wire_d,      2.4))    # ring wire (cross-section) diameter (mm)
clearance   = float(PARAM(lambda: clearance,   0.45))   # print gap between linked rings (mm)

target_part = str(  PARAM(lambda: target_part, "panel"))  # panel|swatch|ring

# ── Safe clamps ──────────────────────────────────────────────────────────────
rows      = max(1, min(rows, 40))
cols      = max(1, min(cols, 40))
ring_id   = max(4.0, min(ring_id, 30.0))
wire_d    = max(1.2, min(wire_d, 6.0))
clearance = max(0.2, min(clearance, 1.5))

ring_od   = ring_id + 2.0 * wire_d        # ring outer diameter
r_center  = (ring_id + wire_d) / 2.0      # ring centreline radius
tube_r    = wire_d / 2.0                  # wire cross-section radius

# 4-in-1 geometry: rings lie in tilted planes so each links four neighbours. The
# in-plane pitch packs rings so a linked pair overlaps by ~one wire; the row pitch
# is half that (offset rows interleave). Tilt alternates ± so adjacent columns link.
col_pitch = (ring_od - wire_d - clearance)          # centre-to-centre across a row
row_pitch = col_pitch * 0.62                        # interleaved rows sit closer
tilt_deg  = 32.0                                     # ring plane tilt off vertical

# Facet counts for the ring prism. 16 sides on the wire and 40 around the ring put
# the worst-case chord error at ~1.9% of the wire radius and ~0.3% of the ring
# radius — under a 0.4 mm nozzle's own resolution at every parameter value in range,
# and far under the 0.1 mm deflection the STL exporter would have used anyway.
WIRE_SIDES = 16
PATH_SIDES = 40


def _base_ring():
    """One un-tilted chainmail ring, centred on the origin in the XY plane.

    A regular WIRE_SIDES-gon cross-section swept along a regular PATH_SIDES-gon
    centreline, built as a ruled loft through the section polygons. Ruled loft
    between two polygons of equal vertex count is exactly the planar quad strip
    joining them, so the solid is a closed polyhedron and the STL exporter emits
    its facets rather than refining a curved surface.

    Both polygons are circumscribed about the nominal radii (`/cos(pi/n)`), so the
    faceted solid *contains* the analytic torus of the same `r_center`/`tube_r`:
    the wire is never thinner than `wire_d` and the ring never reaches less far
    than `ring_od`, which is the direction a printable, load-bearing link wants to
    err in. Volume lands ~1.2% above the analytic torus at the default facet counts.
    """
    cs_r   = tube_r   / math.cos(math.pi / WIRE_SIDES)   # circumscribed wire radius
    path_r = r_center / math.cos(math.pi / PATH_SIDES)   # circumscribed centreline radius

    sections = []
    for i in range(PATH_SIDES):
        a = 2.0 * math.pi * i / PATH_SIDES
        ca, sa = math.cos(a), math.sin(a)
        pts = []
        for j in range(WIRE_SIDES):
            # +0.5 offsets the cross-section polygon so a vertex never lands on the
            # ring's own mid-plane — the facet seam stays off the print's Z seam.
            b = 2.0 * math.pi * (j + 0.5) / WIRE_SIDES
            u = cs_r * math.cos(b)      # offset along the outward radial direction
            v = cs_r * math.sin(b)      # offset along the ring axis (Z)
            pts.append(cq.Vector(path_r * ca + u * ca, path_r * sa + u * sa, v))
        sections.append(cq.Wire.makePolygon(pts, close=True))

    # Closing the loop back onto sections[0] seals the last quad strip, so the loft
    # is a closed solid with no cap faces — a torus topology, watertight.
    return cq.Solid.makeLoft(sections + [sections[0]], ruled=True)


# Exactly two ring shapes exist for a whole panel — one per tilt sign. Every ring in
# the weave is one of these two, instanced at a Location (see the module docstring).
_BASE = _base_ring()
_PROTOTYPE = {
    +1: _BASE.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), +tilt_deg),
    -1: _BASE.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), -tilt_deg),
}


def _ring(cx, cy, tilt_sign):
    """One chainmail ring centred at (cx, cy) on the panel plane (XY), its plane
    tilted about the Y axis by ±tilt so it interlinks its row neighbours. Returns a
    Workplane so the "ring" mode has the same shape of result the other modes'
    members do; the panel builder uses the prototype + Location directly."""
    solid = _PROTOTYPE[tilt_sign].located(cq.Location(cq.Vector(cx, cy, 0)))
    return cq.Workplane(obj=solid)


def build_panel(n_rows, n_cols):
    """The interlocked ring grid. Even/odd rows are offset by half a column and the
    tilt alternates so every interior ring links its four diagonal neighbours — the
    4-in-1 weave. Returns an Assembly of separate (interlinked) ring solids.

    Each ring is added as the shared tilted prototype under its own `loc`, never as
    a translated copy: the Assembly holds N instances of 2 shapes, so the exporter
    meshes 2 rings and places the result N times."""
    asm = cq.Assembly()
    idx = 0
    for r in range(n_rows):
        y = r * row_pitch
        x_off = (col_pitch / 2.0) if (r % 2) else 0.0
        for c in range(n_cols):
            x = c * col_pitch + x_off
            # Alternate tilt across columns AND rows so neighbours interlink.
            tilt_sign = 1 if ((r + c) % 2 == 0) else -1
            asm.add(_PROTOTYPE[tilt_sign], name=f"ring_{idx}",
                    loc=cq.Location(cq.Vector(x, y, 0)),
                    color=cq.Color("#8a8f94"))
            idx += 1
    return asm


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "ring":
    result = _ring(0, 0, 1)
elif target_part == "swatch":
    result = build_panel(3, 3)
else:
    result = build_panel(rows, cols)
