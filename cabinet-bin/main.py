"""
Cabinet / Drawer Organizer Bin — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A fits-anything cabinet or drawer bin, sized by interior dimensions so the printed
cavity matches the space it must occupy. Three styles:

  * "bin"         : plain open-top bin with a stacking lip on the rim.
  * "angled_bin"  : the front wall is cut down at a slope for scoop-in access
                    (the classic pull-front pantry bin).
  * "divided_bin" : the plain bin plus an interior divider grid (X and/or Y).

The `shell()` + `divider_grid()` pair here is the reusable bin/tray body idiom
shared across the kitchen batch (cabinet-bin, cutlery-tray, …): a solid outer
block hollowed to a five-wall open shell, plus evenly spaced partition walls.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `wall`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.
"""

import cadquery as cq


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default.
    `except Exception` catches the NameError raised for an unbound param name
    (the sandbox does not expose globals()/NameError directly)."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters (interior-driven) ─────────────────────────────────────────────
inner_w   = float(PARAM(lambda: inner_w,   90.0))   # interior X width (mm)
inner_d   = float(PARAM(lambda: inner_d,  140.0))   # interior Y depth (mm, front-back)
inner_h   = float(PARAM(lambda: inner_h,   80.0))   # interior Z height (mm)
wall      = float(PARAM(lambda: wall,       2.0))   # wall / floor thickness (mm)
corner_r  = float(PARAM(lambda: corner_r,   3.0))   # outer vertical corner radius
style     = str(  PARAM(lambda: style,   "open"))   # open | angled-front | handled
lip       = float(PARAM(lambda: lip,        4.0))   # stacking-lip height (mm, 0 = none)
lip_clear = float(PARAM(lambda: lip_clear,  0.4))   # lip-to-rim clearance (print fit)
front_cut = float(PARAM(lambda: front_cut, 40.0))   # open-front sill height (angled)
div_x     = int(  PARAM(lambda: div_x,        0))   # interior dividers along X
div_y     = int(  PARAM(lambda: div_y,        0))   # interior dividers along Y
div_thick = float(PARAM(lambda: div_thick,  1.6))   # divider thickness (mm)

target_part = str(PARAM(lambda: target_part, "bin"))  # bin | angled_bin | divided_bin

# ── Derived envelope + clamps ────────────────────────────────────────────────
wall = max(1.0, min(wall, inner_w / 3.0, inner_d / 3.0))
outer_w = inner_w + 2.0 * wall
outer_d = inner_d + 2.0 * wall
outer_h = inner_h + wall               # floor thickness = wall
corner_r = max(0.0, min(corner_r, min(outer_w, outer_d) / 2.0 - 0.01))
lip = max(0.0, min(lip, wall * 3.0))
front_cut = max(0.0, min(front_cut, inner_h - 2.0))
div_x = max(0, min(div_x, 8))
div_y = max(0, min(div_y, 8))

FRONT_Y = -outer_d / 2.0


# ── Reusable bin/tray body idiom ─────────────────────────────────────────────
def _box(w, d, h, x=0.0, y=0.0, z=0.0):
    return (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x, y, z))
        .box(w, d, h, centered=(True, True, False))
    )


def shell(rounded=True):
    """Solid outer block minus interior cavity = a five-wall shell open at top."""
    body = _box(outer_w, outer_d, outer_h)
    if rounded and corner_r > 0.05:
        body = body.edges("|Z").fillet(corner_r)
    cavity = _box(inner_w, inner_d, inner_h + 1.0, 0.0, 0.0, wall)
    inner_r = max(0.0, corner_r - wall)
    if inner_r > 0.05:
        cavity = cavity.edges("|Z").fillet(inner_r)
    return body.cut(cavity)


def divider_grid():
    """Evenly spaced interior partition walls rising from the floor."""
    walls = []
    if div_x > 0:
        step = inner_w / (div_x + 1)
        for i in range(1, div_x + 1):
            x = -inner_w / 2.0 + i * step
            walls.append(_box(div_thick, inner_d, inner_h, x, 0.0, wall))
    if div_y > 0:
        step = inner_d / (div_y + 1)
        for i in range(1, div_y + 1):
            y = -inner_d / 2.0 + i * step
            walls.append(_box(inner_w, div_thick, inner_h, 0.0, y, wall))
    if not walls:
        return None
    grid = walls[0]
    for w in walls[1:]:
        grid = grid.union(w)
    return grid


def stacking_lip(body):
    """Add an upstand lip on the rim that nests the bin above (with lip_clear)."""
    if lip <= 0.05:
        return body
    lip_w = inner_w - 2.0 * lip_clear
    lip_d = inner_d - 2.0 * lip_clear
    # A ring whose OUTER face is inset to lip_w (inside the cavity opening,
    # inner_w) cannot touch the rim annulus, which only begins AT inner_w — so
    # the old inward-drawn ring floated over the open cavity as a second body.
    # Build the upstand as the rim itself carried upward (footprint outer_w ×
    # outer_d, bore inner_w × inner_d, so it overlaps the walls exactly), then
    # shave its outside back to lip_w × lip_d above the rim so it still nests
    # into the bin above with lip_clear per side.
    LIP_BITE = 0.5          # how far the upstand reaches down into the rim
    upstand = _box(outer_w, outer_d, lip + LIP_BITE, 0.0, 0.0, outer_h - LIP_BITE)
    if corner_r > 0.05:
        upstand = upstand.edges("|Z").fillet(corner_r)
    bore = _box(inner_w, inner_d, lip + LIP_BITE + 2.0,
                0.0, 0.0, outer_h - LIP_BITE - 1.0)
    inner_r = max(0.0, corner_r - wall)
    if inner_r > 0.05:
        bore = bore.edges("|Z").fillet(inner_r)
    # Trim the outside of the upstand down to the nesting footprint, above the
    # rim only (the LIP_BITE band below stays full width and fuses to the wall).
    nest_clear = _box(outer_w + 2.0, outer_d + 2.0, lip + 1.0, 0.0, 0.0, outer_h)
    nest_keep = _box(lip_w, lip_d, lip + 1.0, 0.0, 0.0, outer_h)
    if corner_r > 0.05:
        nest_keep = nest_keep.edges("|Z").fillet(
            max(0.0, min(corner_r, min(lip_w, lip_d) / 2.0 - 0.01))
        )
    ring = upstand.cut(bore).cut(nest_clear.cut(nest_keep))
    return body.union(ring)


def cut_angled_front(body):
    """Slope the front wall down toward the front for scoop-in access.

    Removes an upper wedge: the opening sill sits at `front_cut` on the inner
    edge of the front wall and slopes UP toward the back rim, so the front is
    low (easy reach) and the back stays full height."""
    top_z = outer_h + lip + 1.0
    back_y = inner_d / 2.0
    # Triangle in the YZ plane: low at the front, full height at the back rim.
    pts = [
        (FRONT_Y - 1.0, wall + front_cut),   # front outer face, at sill height
        (back_y + 1.0, top_z),               # back rim, full height
        (FRONT_Y - 1.0, top_z),              # front, top — closes the upper wedge
    ]
    wedge = (
        cq.Workplane("YZ")
        .polyline(pts)
        .close()
        .extrude(outer_w + 4.0)
        .translate((-(outer_w + 4.0) / 2.0, 0, 0))
    )
    return body.cut(wedge)


def add_handle():
    """A pull tab on the front face for the 'handled' style."""
    hw = min(inner_w * 0.5, 40.0)
    ht = 10.0
    tab = _box(hw, wall * 1.6, ht, 0.0, FRONT_Y - wall * 0.3, outer_h - ht - lip - 1.0)
    grip = _box(hw, wall * 3.0, wall * 1.6, 0.0, FRONT_Y - wall * 1.3, outer_h - lip - 3.0)
    return tab.union(grip)


# ── Part builders ────────────────────────────────────────────────────────────
def build_bin():
    body = shell()
    body = stacking_lip(body)
    if style == "handled":
        body = body.union(add_handle())
    try:
        body = body.clean()
    except Exception:
        pass
    return body


def build_angled_bin():
    # No stacking lip here: the sloped open front is the access feature, and a
    # full rim lip would fight it. Back/side walls keep full height for stiffness.
    body = shell()
    body = cut_angled_front(body)
    try:
        body = body.clean()
    except Exception:
        pass
    return body


def build_divided_bin():
    body = shell()
    grid = divider_grid()
    # Guarantee a visible divider even if the user left counts at 0.
    if grid is None:
        mid = _box(div_thick, inner_d, inner_h, 0.0, 0.0, wall)
        grid = mid
    body = body.union(grid)
    body = stacking_lip(body)
    try:
        body = body.clean()
    except Exception:
        pass
    return body


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "angled_bin":
    result = build_angled_bin()
elif target_part == "divided_bin":
    result = build_divided_bin()
else:
    result = build_bin()
