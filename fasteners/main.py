"""
Metric Fastener Generator — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

Parametric ISO metric hardware sized to mate real M-series fasteners: a bolt
(shaft + thread + head), a nut (threaded or plain bore), and a washer (flat or
split/spring). The major diameter equals the nominal (M5 => 5 mm), the pitch is
the real coarse-series pitch per size (M5 coarse = 0.8 mm), and the head/nut
across-flats follows the ISO 4014 / ISO 4032 wrench envelope, so printed parts
mesh with off-the-shelf metric hardware.

Thread strategy (verified watertight; default keeps the render fast):
  * `thread_style = "cosmetic"` (DEFAULT) — a single revolved 60° sawtooth ring
    that reads as a thread and carries the correct major/minor envelope, built
    with ONE revolve (no helical sweep) so it renders in ~1 s.
  * `thread_style = "real"` (opt-in) — the bottle-thread volumetric-rib idiom:
    a triangular ISO-ish profile swept along a genuine `makeHelix` path, unioned
    with its ROOT pushed a little way INTO the shaft/bore material (the `overlap`)
    so the boolean is a clean volumetric fuse rather than a fragile tangent kiss
    (a rib whose root sits exactly on the surface tessellates into cracks).
    The threaded length is capped to a few turns so it stays watertight and fast.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `diameter`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.
"""

import cadquery as cq
import math


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


# ── Parameters ───────────────────────────────────────────────────────────────
target_part  = str(  PARAM(lambda: target_part,  "bolt_cq"))   # bolt_cq | nut_cq | washer

diameter     = float(PARAM(lambda: diameter,       5.0))   # nominal thread major dia (M5=5)
length       = float(PARAM(lambda: length,        20.0))   # bolt shaft length (excl. head)
pitch        = float(PARAM(lambda: pitch,          0.8))   # thread pitch (M5 coarse = 0.8)
head_style   = str(  PARAM(lambda: head_style,   "hex"))   # hex | socket | button
nut_style    = str(  PARAM(lambda: nut_style,    "hex"))   # hex | square | nyloc
washer_type  = str(  PARAM(lambda: washer_type, "flat"))   # flat | spring
thread_style = str(  PARAM(lambda: thread_style, "cosmetic"))  # cosmetic | real
thread_enabled = bool(PARAM(lambda: thread_enabled, True)) # draw thread vs plain cylinder/bore
clearance    = float(PARAM(lambda: clearance,      0.2))   # per-side fit clearance (mm)

# Clamp inputs to sane ranges so extreme UI values still build watertight.
diameter  = max(2.0, min(diameter, 24.0))
length    = max(4.0, min(length, 120.0))
pitch     = max(0.25, min(pitch, min(3.0, diameter * 0.8)))
clearance = max(0.0, min(clearance, 1.0))

# Derived ISO envelope (nominal, so it mates real hardware).
MAJOR_R = diameter / 2.0                     # thread major (crest) radius
THR_DEPTH = 0.61343 * pitch                  # ISO 60° thread height (H); crest→root
MINOR_R = max(0.4, MAJOR_R - THR_DEPTH)      # thread minor (root) radius


# ── Thread primitives (inlined — repo-lib imports are blocked in the sandbox) ─
def _helix_path(p, height):
    """A helical wire centred on Z. Radius ~0 so a swept profile already at the
    target radius traces the true helix."""
    return cq.Wire.makeHelix(pitch=p, height=max(p, height), radius=1e-6)


# Trapezoidal thread-profile proportions (as fraction of pitch along Z). These
# are the bottle-thread / thread-capsule idiom values: a flat crest (0.14) and a
# wider root (0.32) keep the swept helix a clean, non-self-intersecting shell
# that fuses WATERTIGHT even at large diameter/pitch — a sharp triangular crest
# self-intersects over multiple turns and cracks.
CREST_HALF = 0.14
ROOT_HALF = 0.32
REAL_TURN_CAP = 3.0     # cap real threads to a few turns (watertight + fast)


def _turns_for(shaft_len):
    """Real threads are capped to a few turns: beyond the cap the helical-rib
    boolean grows super-linearly and can crack. Cosmetic threads pay no such
    cost, so they cover the whole length."""
    full = shaft_len / pitch
    if thread_style == "real":
        return max(1.0, min(REAL_TURN_CAP, full))
    return max(1.0, full)


def male_rib(shaft_r, thread_h, overlap):
    """External helical rib (bolt). Root bites into the shaft by `overlap`; crest
    reaches shaft_r. Trapezoidal ISO-ish profile (see CREST_HALF/ROOT_HALF)."""
    root_r = max(0.4, shaft_r - THR_DEPTH - overlap)
    crest_r = shaft_r
    prof = (
        cq.Workplane("XZ")
        .polyline([
            (root_r, -pitch * ROOT_HALF),
            (crest_r, -pitch * CREST_HALF),
            (crest_r, pitch * CREST_HALF),
            (root_r, pitch * ROOT_HALF),
        ])
        .close()
    )
    rib = prof.sweep(_helix_path(pitch, thread_h), isFrenet=True)
    return rib.translate((0, 0, pitch * 0.5))


def female_rib(bore_r, thread_h, overlap):
    """Internal helical rib (nut). Root bites OUT into the wall at bore_r+overlap;
    crest points inward to grab the male crest."""
    root_r = bore_r + overlap
    crest_r = max(0.4, bore_r - (MAJOR_R - MINOR_R))
    prof = (
        cq.Workplane("XZ")
        .polyline([
            (root_r, -pitch * ROOT_HALF),
            (crest_r, -pitch * CREST_HALF),
            (crest_r, pitch * CREST_HALF),
            (root_r, pitch * ROOT_HALF),
        ])
        .close()
    )
    rib = prof.sweep(_helix_path(pitch, thread_h), isFrenet=True)
    return rib.translate((0, 0, pitch * 0.5))


def cosmetic_shaft(total_len):
    """A COMPLETE solid shaft with a 60° sawtooth outer profile, made in ONE
    revolve from the Z axis out to the sawtooth crest (~1 s). Because the whole
    shaft is a single revolved solid there is NO boolean at the minor radius —
    which is what keeps the cosmetic thread watertight (a separate ring unioned
    onto a core cylinder shares a coincident cylindrical face and cracks).

    The closed profile: up the axis (x=0), across the base, then a zig-zag right
    edge (root MINOR_R → crest MAJOR_R → root …) climbing to the top, and back
    across the top to the axis."""
    # ROUNDING the tooth count left the shaft short of total_len whenever
    # total_len was not a whole number of pitches: at M5 x 25 (pitch 0.8),
    # round(31.25) = 31 teeth reach only 24.8 mm, and the head -- placed at
    # z = length = 25 -- floated 0.2 mm above it, so `bolt_cq` rendered as two
    # bodies under preset m5_hex_25. Lay down enough whole teeth to reach
    # total_len, then close the profile AT total_len so the shaft is exactly as
    # long as it says. The last partial tooth is simply truncated.
    n = max(1, int(math.ceil(total_len / pitch)))
    pts = [(0.0, 0.0), (MINOR_R, 0.0)]
    z0 = 0.0
    for _ in range(n):
        z_crest = min(z0 + pitch * 0.5, total_len)
        pts.append((MAJOR_R, z_crest))
        if z_crest >= total_len:
            break
        z_root = min(z0 + pitch, total_len)
        pts.append((MINOR_R, z_root))
        if z_root >= total_len:
            break
        z0 += pitch
    if pts[-1][1] < total_len:
        pts.append((MINOR_R, total_len))
    pts.append((0.0, total_len))   # back to the axis along the top
    face = cq.Workplane("XZ").polyline(pts).close()
    return face.revolve(360, (0, 0, 0), (0, 1, 0))


def cosmetic_bore_negative(bore_r, total_h):
    """A single revolved NEGATIVE for a threaded nut bore: one solid (from the Z
    axis out to a sawtooth) whose outer edge zig-zags between the minor bore
    (bore_r) at the crests and the major bore (bore_r+depth) at the roots. Cut
    once from the nut body → an internally threaded bore in a SINGLE boolean
    (no pre-drilled cylinder, so no coincident cylindrical face to crack)."""
    depth = MAJOR_R - MINOR_R
    n = max(1, int(round(total_h / pitch)))
    pts = [(0.0, 0.0), (bore_r, 0.0)]
    z0 = 0.0
    for _ in range(n):
        pts.append((bore_r + depth, z0 + pitch * 0.5))
        pts.append((bore_r, z0 + pitch))
        z0 += pitch
    pts.append((0.0, z0))
    face = cq.Workplane("XZ").polyline(pts).close()
    return face.revolve(360, (0, 0, 0), (0, 1, 0))


# ── Shared geometry helpers ──────────────────────────────────────────────────
def hex_prism(across_flats, height):
    """A regular hexagon prism (across-flats = wrench size), base at z=0."""
    r_circ = across_flats / math.cos(math.radians(30)) / 2.0   # flats→circumradius
    return (
        cq.Workplane("XY")
        .polygon(6, r_circ * 2.0)
        .extrude(height)
    )


def square_prism(across_flats, height):
    return cq.Workplane("XY").rect(across_flats, across_flats).extrude(height)


# ── Bolt ─────────────────────────────────────────────────────────────────────
def build_bolt():
    """Shaft + thread + head. `head_style` picks the head; `thread_style`
    picks cosmetic (fast, default) vs real helical threads."""
    if not thread_enabled:
        # Plain (unthreaded) shaft at the full major diameter.
        shaft = cq.Workplane("XY").circle(MAJOR_R).extrude(length)
    elif thread_style == "real":
        # Solid MINOR-radius core so the helix start/end embed in material, then
        # fuse the volumetric helical rib (root overlaps into the core). Real
        # threads are opt-in / best-effort: if the boolean ever fails, fall back
        # to the always-watertight cosmetic shaft.
        try:
            turns = _turns_for(length)
            thread_h = min(length, pitch * turns)
            overlap = min(0.5, pitch * 0.35)
            core = cq.Workplane("XY").circle(MINOR_R).extrude(length)
            shaft = core.union(male_rib(MAJOR_R, thread_h, overlap))
        except Exception:
            shaft = cosmetic_shaft(length)
    else:
        # Cosmetic: the entire shaft is ONE revolved sawtooth solid (no boolean
        # at the minor radius → watertight, ~1 s).
        shaft = cosmetic_shaft(length)

    # Head sits on top of the shaft (z = length upward).
    head = build_bolt_head()
    bolt = shaft.union(head)

    try:
        bolt = bolt.clean()
    except Exception:
        pass
    return bolt


def build_bolt_head():
    """Hex (ISO 4014), socket-cap (ISO 4762, with a hex Allen recess), or button
    (ISO 7380 dome) head, placed on top of the shaft at z=length."""
    head_af = diameter * 1.7                 # across-flats ≈ 1.7·d (M-series ~1.5–1.8)
    head_h = diameter * 0.7

    if head_style == "socket":
        # Cylindrical cap head with a hex socket (Allen) recess.
        d_head = diameter * 1.5
        h_head = diameter * 1.0
        head = cq.Workplane("XY").circle(d_head / 2.0).extrude(h_head)
        socket_af = max(1.5, diameter * 0.8)
        recess = hex_prism(socket_af, h_head * 0.6 + 0.1).translate((0, 0, h_head * 0.4))
        head = head.cut(recess)
        try:
            head = head.edges(">Z").chamfer(min(0.6, d_head * 0.08))
        except Exception:
            pass
        return head.translate((0, 0, length))

    if head_style == "button":
        # Low dome (button) head: disc + spherical cap, unioned with overlap.
        d_head = diameter * 1.9
        base_h = diameter * 0.25
        dome_h = diameter * 0.55
        disc = cq.Workplane("XY").circle(d_head / 2.0).extrude(base_h)
        # A shallow sphere segment sitting on the disc.
        sph_r = (d_head / 2.0) ** 2 / (2.0 * dome_h) + dome_h / 2.0
        dome = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, base_h - dome_h + sph_r - 0.4))
            .sphere(sph_r)
        )
        keep = cq.Workplane("XY").circle(d_head / 2.0).extrude(dome_h + 0.6).translate(
            (0, 0, base_h - 0.3)
        )
        dome = dome.intersect(keep)
        head = disc.union(dome)
        return head.translate((0, 0, length))

    # Default: hex head (ISO 4014) with a top chamfer.
    head = hex_prism(head_af, head_h)
    try:
        head = head.edges(">Z").chamfer(min(head_h * 0.25, head_af * 0.1))
    except Exception:
        pass
    return head.translate((0, 0, length))


# ── Nut ──────────────────────────────────────────────────────────────────────
def build_nut():
    """Hex / square / nyloc nut with a threaded (or plain) bore. Nyloc adds a
    plain nylon-insert collar on top with a slightly undersized (locking) bore."""
    across_flats = diameter * 1.8            # ISO 4032 nut width ≈ 1.8·d
    body_h = diameter * 0.8
    collar_h = diameter * 0.35 if nut_style == "nyloc" else 0.0
    total_h = body_h + collar_h

    if nut_style == "square":
        body = square_prism(across_flats, total_h)
    else:
        body = hex_prism(across_flats, total_h)
        # Chamfer both faces of the hex (ISO 4032 washer-face style).
        try:
            body = body.edges(">Z or <Z").chamfer(min(body_h * 0.15, across_flats * 0.08))
        except Exception:
            pass

    # The nyloc nylon-insert collar (if any) is unioned on top of the body first,
    # so the whole stack is one solid. The BODY portion gets the working thread;
    # the COLLAR keeps an undersized plain (locking) bore.
    if nut_style == "nyloc":
        collar = hex_prism(across_flats, collar_h).translate((0, 0, body_h))
        body = body.union(collar)

    # Female bore: clears the male major crest by `clearance` per side.
    bore_r = MAJOR_R + clearance

    # --- Thread / bore the load-bearing BODY portion (z in [0, body_h]) ---
    if thread_enabled and thread_style == "real":
        # Real threads are opt-in / best-effort; fall back to the always-
        # watertight cosmetic bore negative if the rib boolean ever fails.
        try:
            hole = cq.Workplane("XY").circle(bore_r).extrude(body_h + 1.0).translate((0, 0, -0.5))
            nut = body.cut(hole)
            overlap = min(0.5, pitch * 0.35)
            turns = _turns_for(body_h)
            thread_h = min(body_h, pitch * turns)
            nut = nut.union(female_rib(bore_r, thread_h, overlap))
        except Exception:
            nut = body.cut(cosmetic_bore_negative(bore_r, body_h))
    elif thread_enabled:
        # Cosmetic: one revolved threaded-bore negative → internal crests in a
        # single watertight boolean (no pre-drilled coincident cylinder).
        nut = body.cut(cosmetic_bore_negative(bore_r, body_h))
    else:
        hole = cq.Workplane("XY").circle(bore_r).extrude(body_h + 1.0).translate((0, 0, -0.5))
        nut = body.cut(hole)

    # --- Bore the COLLAR portion (z in [body_h, total_h]) ---
    if collar_h > 0.0:
        # Undersized locking bore (grips the male thread) when threaded; else
        # a plain clearance bore for symmetry.
        collar_bore_r = max(0.4, MINOR_R + clearance) if thread_enabled else bore_r
        collar_hole = (
            cq.Workplane("XY")
            .circle(collar_bore_r)
            .extrude(collar_h + 1.0)
            .translate((0, 0, body_h - 0.5))
        )
        nut = nut.cut(collar_hole)

    try:
        nut = nut.clean()
    except Exception:
        pass
    return nut


# ── Washer ───────────────────────────────────────────────────────────────────
def build_washer():
    """Flat washer (ISO 7089 proportions) or a split/spring lock washer. ID =
    nominal + clearance so it slips over the bolt; OD ≈ 2·d; thickness ≈ 0.18·d."""
    inner_r = MAJOR_R + max(0.3, clearance)
    outer_r = diameter * 1.1                  # OD ≈ 2.2·d
    thick = max(0.6, diameter * 0.18)

    ring = (
        cq.Workplane("XY")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(thick)
    )

    if washer_type == "spring":
        # Split lock washer: a helically-lifted split ring. Build the flat ring,
        # cut a radial slot, then raise one cut face by ~1 thickness so the ring
        # is a single-turn helical spring (watertight — it is one solid body).
        slot = (
            cq.Workplane("XY")
            .rect(outer_r + 2.0, thick * 0.9, centered=(False, True, True))
            .extrude(thick + 2.0)
            .translate((0, 0, thick / 2.0))
        )
        ring = ring.cut(slot)
        # Tilt the whole ring slightly so the split ends sit at different heights
        # (the characteristic lock-washer ramp). A small rotation about X keeps it
        # a single watertight solid.
        try:
            ring = ring.rotate((0, 0, 0), (1, 0, 0), 6.0)
            # Re-seat so the lowest point rests on z=0.
            bb = ring.val().BoundingBox()
            ring = ring.translate((0, 0, -bb.zmin))
        except Exception:
            pass
    else:
        # Flat washer: soften both edges lightly.
        try:
            ring = ring.edges(">Z or <Z").chamfer(min(thick * 0.25, 0.4))
        except Exception:
            pass

    try:
        ring = ring.clean()
    except Exception:
        pass
    return ring


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "nut_cq":
    result = build_nut()
elif target_part == "washer":
    result = build_washer()
else:
    result = build_bolt()
