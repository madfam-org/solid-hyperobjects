"""
Indexed Column — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

An open rectangular tube with a row of index holes along one face: the fixed half
of a pin-and-hole height adjustment. A sleeve slides on the tube and a pin through
the sleeve drops into one of the holes. The Common Denominator Geometry is the
pair every such column shares: the section a sleeve has to fit, and the hole
pattern a pin has to find.

Part:
  * "column" — the tube with its row of holes, one body.

Frame: the column runs along Z with its lower end on Z = 0, so every hole height
is measured from that end. The holes are in the front face (+Y), centred on the
width. With `through` on, each hole also passes the back wall, for a pin that
goes right through the column.

The tube is open at both ends and every hole is a through cut that ends in the
open bore or beyond the far face, so no cut stops on a face.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals; read them through PARAM()
    so the script also runs standalone with any subset of them.
  - Assign the final solid to a top-level name `result`.
"""

import cadquery as cq


def PARAM(getter, default):
    """Return an injected global if present, else the default."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


def as_bool(v):
    return str(v).strip().lower() in ("1", "true", "yes", "on")


COLUMN_W = float(PARAM(lambda: column_w, 50.0))
COLUMN_D = float(PARAM(lambda: column_d, 50.0))
WALL = float(PARAM(lambda: wall, 3.0))
LENGTH = float(PARAM(lambda: length, 700.0))
HOLE_D = float(PARAM(lambda: hole_d, 10.5))
HOLE_PITCH = float(PARAM(lambda: hole_pitch, 50.0))
FIRST_HOLE = float(PARAM(lambda: first_hole, 50.0))
HOLE_COUNT = max(1, int(round(float(PARAM(lambda: hole_count, 12)))))
THROUGH = as_bool(PARAM(lambda: through, False))

EPS = 1.0                                   # through-cut overshoot
BORE_W = COLUMN_W - 2.0 * WALL              # the open bore
BORE_D = COLUMN_D - 2.0 * WALL


def tube():
    """The open rectangular tube, lower end on Z = 0."""
    outer = cq.Workplane("XY").box(COLUMN_W, COLUMN_D, LENGTH).translate((0, 0, LENGTH / 2.0))
    bore = (cq.Workplane("XY").box(BORE_W, BORE_D, LENGTH + 2.0 * EPS)
            .translate((0, 0, LENGTH / 2.0)))
    return outer.cut(bore)


def hole_heights():
    """Hole centres from the lower end; any that would leave the tube are dropped."""
    heights = [FIRST_HOLE + i * HOLE_PITCH for i in range(HOLE_COUNT)]
    return [z for z in heights if HOLE_D / 2.0 < z < LENGTH - HOLE_D / 2.0]


def build_column():
    body = tube()
    heights = hole_heights()
    if not heights:
        return body
    # One tool for the whole row. It starts in front of the face and runs back into
    # the open bore, or out past the back face when the holes go right through.
    depth = (COLUMN_D + 2.0 * EPS) if THROUGH else (EPS + WALL + BORE_D / 2.0)
    row = (cq.Workplane("XZ", origin=(0, COLUMN_D / 2.0 + EPS, 0))
           .pushPoints([(0.0, z) for z in heights]).circle(HOLE_D / 2.0).extrude(depth))
    return body.cut(row)


result = build_column()
