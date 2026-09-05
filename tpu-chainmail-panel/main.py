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

── WEAVE FEASIBILITY: the placement fix and the dimensional rule ────────────────
Two things have to hold for this to be chainmail rather than a pile of rings:
every interior ring must LINK all four of its diagonal neighbours, and no two
rings may SHARE MATERIAL (they would fuse into one body in the print).

  1. LINKING is a placement property. It is fixed by the row-tilt scheme in
     `_tilt_sign()` — see that function for what was wrong before and why. With
     it, all four diagonals link at EVERY `ring_id` in range; without it, exactly
     two of four linked at every `ring_id` in range.

  2. NON-OVERLAP is a dimensional property, and TWO different pairs bind it in
     two different regimes. Same-row neighbours are never the problem: they share
     a tilt sign and sit in parallel planes col_pitch*sin(tilt) apart — 5.8 mm at
     the defaults.

     (A) The DIAGONAL (linking) pair. Two diagonal rings are tilted oppositely and
         pass through each other's holes, so their centrelines approach to
         `diag_sep`, and they clear when `diag_sep >= wire_d` (the tube radii sum
         to 2*tube_r = wire_d). Bisecting that boundary on the analytic
         centrelines over the declared parameter box gives a surface linear in
         the parameters to within 0.62 mm:

             ring_id >= 6.3879*wire_d - 4.8324*clearance + 0.8208         (A)

         The MINUS on clearance is real, not a slip: a larger print gap shrinks
         `col_pitch`, which pulls the lattice in and buys slack on this pair.

     (B) The TWO-ROWS-APART pair, same column. These are not neighbours and do not
         link, but `row_pitch` is only 0.62*col_pitch, so at large clearance rows
         r and r+2 close up and collide — and because they share a tilt sign, no
         tilt can separate them. This one needs no fitting; it is exact. Both
         rings are tilted about Y, so their extent along Y is not foreshortened
         and is exactly 2*r_center. Requiring 2*row_pitch >= 2*r_center + wire_d
         and substituting row_pitch = 0.62*(ring_id + wire_d - clearance) and
         r_center = (ring_id + wire_d)/2 gives, with a 0.7 mm margin:

             ring_id >= 3.1667*wire_d + 5.1667*clearance + 0.7            (B)

     (A) binds at low clearance and (B) at high clearance; both are encoded as
     `error`-severity entries in project.json's `constraints[]`, so the UI cannot
     combine the ranges into an impossible weave. The ranges DO still admit
     infeasible points — at wire_d 6.0 the binding rule wants ring_id 32-38,
     above the 30 mm cap, at every clearance — which is exactly what the
     constraints exist to reject.

     Checked over the whole box (wire_d 1.2/2.4/3.4/6.0 x clearance
     0.2/0.45/1.5): at the smallest ring_id each rule admits, the worst pairwise
     gap on a 5x5 field — over ALL pair types, not just the diagonals — is
     positive at every feasible point (+0.063 to +0.168 mm), and every wire_d 6.0
     point is correctly rejected as impossible.

  Defaults and presets were re-derived from (A) and (B) and each verified by exact OCCT
  pairwise intersection (zero overlapping neighbour pairs) plus a Gauss linking
  number of +-1 on all four diagonals of every interior ring.

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
ring_id     = float(PARAM(lambda: ring_id,     15.0))   # ring inner diameter (mm) — see WEAVE FEASIBILITY
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


def _tilt_sign(r, c):
    """The 4-in-1 row-tilt scheme: the tilt sign depends on the ROW ONLY.

    Rings sit on an offset (brick) lattice — odd rows are shifted half a column —
    so EVERY diagonal neighbour of ring (r, c) lives in row r-1 or r+1. Making the
    sign a function of `r` alone therefore guarantees that all four diagonal
    partners are tilted the OPPOSITE way, which is the condition for two rings to
    interlink: two rings tilted the same way lie in parallel planes and can only
    miss or collide, never link.

    The scheme this replaces was `(r + c) % 2`. On a square lattice that would
    alternate correctly, but on the offset lattice the half-column shift flips the
    column parity of one diagonal and not the other, so one diagonal came out
    same-sign at every ring: measured on a 6x6, 36 of 72 diagonal pairs were
    same-sign, and every interior ring linked exactly 2 of its 4 neighbours no
    matter what `ring_id` was set to. Raising `ring_id` could never have fixed it;
    the defect was in the placement, not the dimensions.
    """
    return 1 if (r % 2 == 0) else -1


def _ring(cx, cy, tilt_sign):
    """One chainmail ring centred at (cx, cy) on the panel plane (XY), its plane
    tilted about the Y axis by ±tilt so it interlinks its row neighbours. Returns a
    Workplane so the "ring" mode has the same shape of result the other modes'
    members do; the panel builder uses the prototype + Location directly."""
    solid = _PROTOTYPE[tilt_sign].located(cq.Location(cq.Vector(cx, cy, 0)))
    return cq.Workplane(obj=solid)


def build_panel(n_rows, n_cols):
    """The interlocked ring grid. Even/odd rows are offset by half a column and the
    tilt alternates BY ROW, so every interior ring links its four diagonal
    neighbours — the 4-in-1 weave. Returns an Assembly of separate (interlinked)
    ring solids.

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
            # Row-tilt: the sign depends on the ROW ONLY. See _tilt_sign().
            tilt_sign = _tilt_sign(r, c)
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
