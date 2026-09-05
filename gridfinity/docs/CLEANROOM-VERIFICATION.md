# Clean-room verification — the `gridfinity` OpenSCAD modes

**Cartridge:** `gridfinity` · **Modes:** `cup`, `baseplate_scad`, `lid`
**Ruling:** ADR-021 (2026-09-04) — a hyperobject with a non-CERN-OHL-W origin
leaves the commons and returns clean-room, to the same final result.
**Verified:** 2026-09-04 · **OpenSCAD** 2026.02.13, backend **Manifold** ·
measured with trimesh / numpy.

## What was and was not read

Written from the publicly documented Gridfinity specification (gridfinity.xyz)
and from a private baseline pack recording the removed version's manifest
contract and measured geometry. **Not read, at any point:** the removed
cartridge in this repository's git history, the archived satellite repository,
the GPL-3.0 upstream the removed modes descended from, its MIT ancestor, or any
fork or page carrying their source. No prior Gridfinity implementation is a
source of this work.

## How to reproduce

```
<python> docs/measure_cleanroom.py \
    --pack     <baseline pack dir> \
    --cartridge <this directory> \
    --scaffold  <render scaffold> \
    --out results.json
```

The measuring script is [`measure_cleanroom.py`](measure_cleanroom.py) in this
directory. It renders every variant in the pack's `VARIANTS.json` through these
`.scad` files using the platform's exact injection shape
(`-o out.stl --backend=Manifold -D k=v …`, booleans as `1`/`0`, numbers bare,
strings quoted, no `render_mode`), measures the mesh, and compares against the
pack's `MEASUREMENTS.json`. The scaffold is shaped like the platform's render
root: `<scaffold>/projects` resolving to the commons checkout, `<scaffold>/libs`
holding the libraries, `OPENSCADPATH=<scaffold>/libs`. Every render is bounded
by `timeout 600`.

These modes use **no third-party library**, so they render with an empty
`OPENSCADPATH`; the full sweep was re-run with `libs/` empty to prove it.

## Result: 40 of 40 variants pass

| Gate | Result |
| :--- | :--- |
| Watertight (every variant, no exceptions) | **40 / 40** — including all 12 `baseplate_scad`, of which the baseline passed only 2 |
| Body count 1 | **40 / 40** |
| Bounding box within ±0.05 mm of the baseline, all three axes | **40 / 40**, every one at **0.0000 mm** |
| Loads in trimesh with faces > 0 | **40 / 40** |

The envelope is the primary regression gate (SPEC §7.5): no quirk fix changes
it, so it is the check that survives every deliberate deviation. It matched
exactly at every variant.

### Per-variant

| Variant | Baseline bbox | Measured bbox | Baseline vol mm³ | Measured vol mm³ | Δvol | Mesh |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| `cup/default` | 83.5 × 41.5 × 21.0 | 83.5 × 41.5 × 21.0 | 8857.262 | 23349.926 | +163.6 % | watertight |
| `cup/small_bin_scad` | 83.5 × 41.5 × 21.0 | 83.5 × 41.5 × 21.0 | 8857.262 | 24646.521 | +178.3 % | watertight |
| `cup/battery_holder_scad` | 125.5 × 83.5 × 21.0 | 125.5 × 83.5 × 21.0 | 20678.759 | 67337.728 | +225.6 % | watertight |
| `cup/tool_drawer_scad` | 167.5 × 83.5 × 14.0 | 167.5 × 83.5 × 14.0 | 22413.028 | 78048.930 | +248.2 % | watertight |
| `cup/screw_organizer_scad` | 125.5 × 83.5 × 28.0 | 125.5 × 83.5 × 28.0 | 24149.639 | 71950.474 | +197.9 % | watertight |
| `cup/pen_cup_scad` | 41.5 × 41.5 × 42.0 | 41.5 × 41.5 × 42.0 | 9194.268 | 17181.460 | +86.9 % | watertight |
| `cup/p_width_units_min` | 41.5 × 41.5 × 21.0 | 41.5 × 41.5 × 21.0 | 5132.028 | 12577.127 | +145.1 % | watertight |
| `cup/p_width_units_max` | 251.5 × 41.5 × 21.0 | 251.5 × 41.5 × 21.0 | 23758.199 | 66441.123 | +179.7 % | watertight |
| `cup/p_depth_units_min` | 83.5 × 41.5 × 21.0 | 83.5 × 41.5 × 21.0 | 8857.262 | 23349.926 | +163.6 % | watertight |
| `cup/p_depth_units_max` | 83.5 × 251.5 × 21.0 | 83.5 × 251.5 × 21.0 | 38411.006 | 119845.941 | +212.0 % | watertight |
| `cup/p_height_units_min` | 83.5 × 41.5 × 7.0 | 83.5 × 41.5 × 7.0 | 4737.902 | 17297.185 | +265.1 % | watertight |
| `cup/p_height_units_max` | 83.5 × 41.5 × 70.0 | 83.5 × 41.5 × 70.0 | 23275.022 | 43807.630 | +88.2 % | watertight |
| `cup/p_cup_floor_thickness_min` | 83.5 × 41.5 × 21.0 | 83.5 × 41.5 × 21.0 | 7957.956 | 22393.250 | +181.4 % | watertight |
| `cup/p_cup_floor_thickness_max` | 83.5 × 41.5 × 21.0 | 83.5 × 41.5 × 21.0 | 12688.173 | 27495.523 | +116.7 % | watertight |
| `cup/p_all_min` | 41.5 × 41.5 × 7.0 | 41.5 × 41.5 × 7.0 | 1974.215 | 8213.359 | +316.0 % | watertight |
| `cup/p_all_max` | 251.5 × 251.5 × 70.0 | 251.5 × 251.5 × 70.0 | 224849.193 | 499120.197 | +122.0 % | watertight |
| `cup/p_mid1` | 125.5 × 125.5 × 28.0 | 125.5 × 125.5 × 28.0 | 36036.614 | 97860.924 | +171.6 % | watertight |
| `cup/p_mid2` | 167.5 × 167.5 × 49.0 | 167.5 × 167.5 × 49.0 | 87524.574 | 203388.423 | +132.4 % | watertight |
| `baseplate_scad/default` | 84.0 × 84.0 × 5.0 | 84.0 × 84.0 × 5.0 | 2485.053 | 5677.971 | +128.5 % | watertight (baseline: **not**) |
| `baseplate_scad/baseplate_std_scad` | 84.0 × 84.0 × 5.0 | 84.0 × 84.0 × 5.0 | 2485.053 | 21066.057 | +747.7 % | watertight (baseline: **not**) |
| `baseplate_scad/p_width_units_min` | 42.0 × 84.0 × 5.0 | 42.0 × 84.0 × 5.0 | 1211.640 | 2808.099 | +131.8 % | watertight (baseline: **not**) |
| `baseplate_scad/p_width_units_max` | 252.0 × 84.0 × 5.0 | 252.0 × 84.0 × 5.0 | 7578.707 | 17157.459 | +126.4 % | watertight (baseline: **not**) |
| `baseplate_scad/p_depth_units_min` | 84.0 × 42.0 × 5.0 | 84.0 × 42.0 × 5.0 | 1211.640 | 2808.099 | +131.8 % | watertight (baseline: **not**) |
| `baseplate_scad/p_depth_units_max` | 84.0 × 252.0 × 5.0 | 84.0 × 252.0 × 5.0 | 7578.707 | 17157.459 | +126.4 % | watertight (baseline: **not**) |
| `baseplate_scad/p_bp_corner_radius_min` | 84.0 × 84.0 × 5.0 | 84.0 × 84.0 × 5.0 | 2299.733 | 5739.744 | +149.6 % | watertight |
| `baseplate_scad/p_bp_corner_radius_max` | 84.0 × 84.0 × 5.0 | 84.0 × 84.0 × 5.0 | 3617.566 | 5371.743 | +48.5 % | watertight (baseline: **not**) |
| `baseplate_scad/p_all_min` | 42.0 × 42.0 × 5.0 | 42.0 × 42.0 × 5.0 | 574.933 | 1434.936 | +149.6 % | watertight |
| `baseplate_scad/p_all_max` | 252.0 × 252.0 × 5.0 | 252.0 × 252.0 × 5.0 | 36072.310 | 51289.696 | +42.2 % | watertight (baseline: **not**) |
| `baseplate_scad/p_mid1` | 126.0 × 126.0 × 5.0 | 126.0 × 126.0 × 5.0 | 5557.098 | 12866.587 | +131.5 % | watertight (baseline: **not**) |
| `baseplate_scad/p_mid2` | 168.0 × 168.0 × 5.0 | 168.0 × 168.0 × 5.0 | 12069.172 | 22779.398 | +88.7 % | watertight (baseline: **not**) |
| `lid/default` | 83.0 × 41.0 × 2.0 | 83.0 × 41.0 × 2.0 | 6781.291 | 6081.260 | −10.3 % | watertight |
| `lid/lid_std_scad` | 83.0 × 41.0 × 2.0 | 83.0 × 41.0 × 2.0 | 6781.291 | 6081.260 | −10.3 % | watertight |
| `lid/p_width_units_min` | 41.0 × 41.0 × 2.0 | 41.0 × 41.0 × 2.0 | 3337.291 | 2938.016 | −12.0 % | watertight |
| `lid/p_width_units_max` | 251.0 × 41.0 × 2.0 | 251.0 × 41.0 × 2.0 | 20557.291 | 18654.239 | −9.3 % | watertight |
| `lid/p_depth_units_min` | 83.0 × 41.0 × 2.0 | 83.0 × 41.0 × 2.0 | 6781.291 | 6081.260 | −10.3 % | watertight |
| `lid/p_depth_units_max` | 83.0 × 251.0 × 2.0 | 83.0 × 251.0 × 2.0 | 41641.291 | 38538.508 | −7.5 % | watertight |
| `lid/p_all_min` | 41.0 × 41.0 × 2.0 | 41.0 × 41.0 × 2.0 | 3337.291 | 2938.016 | −12.0 % | watertight |
| `lid/p_all_max` | 251.0 × 251.0 × 2.0 | 251.0 × 251.0 × 2.0 | 125977.291 | 118075.582 | −6.3 % | watertight |
| `lid/p_mid1` | 125.0 × 125.0 × 2.0 | 125.0 × 125.0 × 2.0 | 31225.291 | 28903.814 | −7.4 % | watertight |
| `lid/p_mid2` | 167.0 × 167.0 × 2.0 | 167.0 × 167.0 × 2.0 | 55753.291 | 51931.327 | −6.9 % | watertight |

Volume is **outside ±2 % at every variant, and that is the expected and correct
outcome** where a quirk is being fixed (SPEC §7.4). Every deviation is accounted
for below; none is a silently widened tolerance.

## Interface dimensions

Measured on the re-created geometry. The standard's value, then what this
cartridge produces.

| Interface quantity | Standard | Measured | Where |
| :--- | :--- | :--- | :--- |
| Grid module, X and Y | 42.0 mm | 42.0000 mm | implied by every footprint |
| Height unit | 7.0 mm | 7.0000 mm | `cup` 1 u → 7.0, 10 u → 70.0 |
| Bin footprint | 42·n − 0.5 | 41.5 / 83.5 / 251.5 mm at n = 1 / 2 / 6 | `cup` |
| Baseplate footprint | 42·n | 42.0 / 84.0 / 252.0 mm | `baseplate_scad` |
| Lid footprint | 42·n − 1.0 | 41.0 / 83.0 / 251.0 mm | `lid` |
| Base profile, bed section | 41.5 − 2(0.8 + 2.15) = 35.60 | **35.610 mm** | `cup` at z = 0.005 |
| Base profile, top of lower chamfer | 41.5 − 2(2.15) = 37.20 | **37.190 mm** at z = 0.795 | `cup` |
| Base profile, top of straight section | 37.20 | **37.200 mm** at z = 2.595 | `cup` |
| Base profile, top of upper chamfer | 41.50 | **41.490 mm** at z = 4.745 | `cup` |
| Foot top (full width) | 41.50 | **41.500 mm** at z = 4.995 | `cup` |
| Foot height | 5.00 mm | **5.000 mm** | `cup` |
| Profile step heights | 0.80 / 1.80 / 2.15 mm | 0.80 / 1.80 / 2.15, riser 0.25 | `gridfinity_std.scad` |
| Corner radius at the widest section | 3.75 mm | **3.7485 mm** (arc fit, `fn` = 32) | `cup` |
| Corner radius at the bed | 3.75 − 2.15 − 0.8 = 0.80 | **0.7984 mm** | `cup` |
| Socket mouth (plate top face) | 41.5 + 0.25 = 41.75 | **41.750 mm** | `baseplate_scad` |
| Socket at plate bottom face | 35.60 + 0.25 = 35.85 | **35.860 mm** | `baseplate_scad` |
| Socket mouth corner radius | 3.75 + 0.125 = 3.875 | **3.8735 mm** | `baseplate_scad` 1 × 1 |
| **Foot-to-socket clearance** | **0.25 mm nominal** | **0.2500 mm** measured, diametral | foot 41.500 into socket 41.750 |
| Plate thickness | 5.0 mm | 5.000 mm | `baseplate_scad` |
| Lid plate thickness | 2.0 mm | 2.000 mm | `lid` |
| Magnet socket diameter | 6.0 mm | **6.000 mm** (radius 3.000) | `cup`, `baseplate_scad`, `lid` |
| Magnet socket depth | 2.0 mm | **2.000 mm** (z = 0.0 → 2.0) | `cup`, `baseplate_scad` |
| Magnet centres | 26 mm square about the cell centre | **±13.000 mm** in X and Y | all three |
| Screw hole | M3 clearance | 3.4 mm dia, coaxial with the magnets | `cup`, `baseplate_scad` |

Every interface figure is within 0.01 mm of nominal, i.e. inside the ±0.05 mm
gate. The residual is fillet tessellation at `fn` = 32 — the baseline's own
corner-radius measurement was 3.7485 mm for the same reason.

### The parts actually mate

- **Bin into baseplate.** The foot tops out at 41.500 mm; the socket mouth is
  41.750 mm. Diametral clearance **0.2500 mm**, the standard's nominal, measured
  not asserted. The socket is `gf_foot_profile` grown by the clearance — the same
  function the foot is built from — so the two cannot drift apart.
- **Bin on bin.** The rim carries a recess whose surface is the base profile,
  sweeping the whole footprint: 80.48 × 38.48 mm at the rim narrowing to
  74.70 × 32.70 mm at its base, on a 2 × 1 bin. The feet of the bin above (a
  41.5 mm cell array at 42 mm pitch) land on that taper and self-centre. The
  removed version had **no lip at any height** and its bins could not stack.
- **Lid on bin.** The lid's underside carries a 79.8 × 37.8 mm spigot, 0.9 mm
  deep, which enters the bin's lip recess. The removed version's lid was a
  featureless plate with no fit feature of any kind.

## Deviations from the baseline, and why

Each is a defect the baseline pack marks "do not reproduce" (SPEC §5), fixed
here. The envelope is unchanged in every case.

| # | Baseline behaviour | This cartridge | Why |
| :-- | :--- | :--- | :--- |
| 1 | **No stacking lip** at any height; bins could not stack. | A perimeter lip recess, the base profile at the rim, styled by `lip_style_id`. | SPEC §5 quirk 1: the manifest advertises `lip_enabled`/`lip_style_id` and the CDG interface `gridfinity_base_profile`; the standard requires it. |
| 2 | **Base profile a single straight 12.95° ramp**, 39.2 → 41.5 mm over 5 mm. | The standard three-step stack, 35.6 / 37.2 / 37.2 / 41.5 over 4.75 mm plus a 0.25 mm riser to the 5.0 mm foot height. | SPEC §5 quirk 2: "implement the standard profile". **This is the deviation SPEC §7.3 partially contradicts itself on** — see the note below. |
| 3 | **Socket taper 15.64°**, a different angle from the foot, reaching the full 42.0 mm at the plate top; sockets touched each other and the plate edge exactly. | One shared profile at 0.125 mm per side, socket mouth 41.75 mm, a 0.25 mm rib between adjacent sockets and 0.125 mm to the plate edge. | SPEC §5 quirk 3 and §7.3: "41.5 mm + the standard clearance, not 42.0". |
| 4 | **Baseplate not watertight** — 60 non-manifold edges at 10 of 12 variants, caused by quirk 3. | Watertight at **all 12**. | SPEC §5 quirk 4: "the one baseline property the acceptance check inverts". |
| 5 | Interior corner radius equal to the exterior (3.75 mm both) on a shelled body. | Interior radius reduced by the wall thickness. | SPEC §5 quirk 5, classified `form`: "do whatever is geometrically correct". |
| 6 | `bp_corner_radius` drove the **socket** corners as well as the plate outline; above 3.75 mm the sockets stopped accepting a standard foot. | It drives the **plate outline only**; the socket radius is fixed by the standard. | SPEC §5 quirk 6. |
| 7 | The **lid was a featureless plate** — no recess, rim, magnets or lid types. | A registration step, a half-pitch ridge, an efficient relief and magnet pockets; four live lid types. | SPEC §5 quirk 7 and §2.3. Footprint and 2.0 mm thickness unchanged, so the envelope holds; the recess is cut into it. |
| 8 | **21 of 27 parameters were inert** (14 cup, 4 baseplate, 3 lid). | All 27 change geometry — verified, see below. | SPEC §5 quirk 8: "the re-creation SHOULD implement them". |
| 9 | `enable_magnets` was accepted on three `cup` presets but applied to no cup parameter. | The parameter is widened to `["bin", "cup"]` and the cup implements magnet sockets, so those presets mean what they say. | SPEC §4: "do not leave it silently accepted-and-ignored". |
| 10 | `fn = 0` resolved to 32. | Same: `gf_fn(fn) = fn > 0 ? fn : 32`. | SPEC §5 quirk 10 — reproduced deliberately; it is a sane default, not a defect. |
| — | The baseplate socket **passed clean through** the plate, leaving nowhere to host magnets. | With `bp_enable_magnets` or `bp_enable_screws` the socket is raised onto a 2.6 mm floor. With both off, it still passes clean through. | The declared parameters had no material to cut. The plate's outside dimensions are unchanged, and the mating surface is the same profile at the same clearance — only its unused bottom is shortened. This is why `baseplate_std_scad` shows +747.7 % volume: it is the one preset that asks for magnets. |

### A contradiction in the baseline pack, resolved in favour of the standard

SPEC §7.3 lists the base-profile **endpoints** — including "39.2 mm at the bed" —
as still holding to ±0.05 mm while simultaneously instructing that the standard
profile replace the baseline's single ramp (quirk 2). The two cannot both be
satisfied: 39.2 mm is a consequence of the 12.95° ramp being fixed, whereas the
standard's 0.8 + 2.15 mm chamfers give **35.6 mm** at the bed for a 41.5 mm cell.

Resolved in favour of the standard, because §5 quirk 2 is unambiguous
("implement the standard profile"), §7.5 names the **envelope** as the check that
survives every quirk fix, and the bed section is a mid-profile dimension, not an
envelope one. The other endpoints §7.3 names — 5.0 mm foot height, the
42·n − 0.5 / 42·n footprints, the 3.75 mm corner radius — all hold to ±0.05 mm
and are tabulated above. **Measured bed section: 35.610 mm.** Recorded here so
the deviation is visible rather than buried.

## Every parameter is live

Each of the 27 was rendered at its default and again off its default (each
enumerated option separately), and the meshes compared on volume, face count and
extents. **43 probes, 43 changed the geometry, 0 inert.** Every perturbed render
is watertight and a single body.

| Mode | Parameters proven live |
| :--- | :--- |
| `cup` (19) | `width_units`, `depth_units`, `height_units`, `cup_wall_thickness`, `cup_floor_thickness`, `vertical_chambers`, `horizontal_chambers`, `lip_style_id` (all 4 values), `headroom`, `efficient_floor_id` (all 4), `fingerslide_enabled`, `label_enabled`, `sliding_lid_enabled`, `wallpattern_enabled`, `wallpattern_style_id` (all 4), `tapered_corner_id` (all 3), `tapered_corner_size`, `enable_screws`, `enable_magnets`, `fn` |
| `baseplate_scad` (8) | `width_units`, `depth_units`, `bp_enable_magnets`, `bp_enable_screws`, `bp_corner_radius`, `bp_reduced_wall`, `bp_reduced_wall_taper`, `fn` |
| `lid` (6) | `width_units`, `depth_units`, `lid_include_magnets`, `lid_efficient_floor`, `lid_type_id` (all 4), `fn` |

`fn` is live as **tessellation only**, exactly as the contract records it: face
count changes, the shape does not.

## Manifest parity

Checked mechanically against the pack's `CONTRACT.json`: all 27 parameter ids
present, with matching `type`, `default`, `min`, `max`, `step`, `group`,
`options` and both `label` and `tooltip` in `en` and `es`; all 7 preset ids with
matching `mode`, `label` and `values`; all 3 mode ids and 3 part ids with
matching labels and `render_mode`. **Zero mismatches.** The `lid` / `lid_std_scad`
id asymmetry is preserved. No id was renamed; `visible_in_modes` was added, which
the lane brief permits.

## Cross-engine parity: CadQuery `bin` vs OpenSCAD `cup`

The commons' `scripts/qa/verify_parity.py` pairs a mode's own `.scad` with its
own `.py`. `bin` and `cup` are **different modes**, so that script never pairs
them — it classifies `bin` as a CadQuery-only placeholder and `cup` as an
OpenSCAD-only mode and skips both, which is the correct classification. Its
comparison rule was therefore applied by hand across the two modes, at the plain
configuration (no dividers, no features) where `cup` has nothing `bin` lacks.

| Case | bbox delta | Verdict | Volume: cup / bin | Volume verdict |
| :--- | ---: | :--- | ---: | :--- |
| 2 × 1 × 3 | **0.000000 mm** | PASS (≤ 0.001) | 25287.675 / 21748.362 | outside 2 % |
| 3 × 2 × 5 | **0.000000 mm** | PASS (≤ 0.001) | 74398.095 / 66603.095 | outside 2 % |
| 1 × 1 × 6 | **0.000000 mm** | PASS (≤ 0.001) | 17488.016 / 15428.653 | outside 2 % |

**Footprint and height agree exactly at every size.** The base profile agrees
section by section to ~0.01 mm: bed 35.610 (cup) vs 35.622 (bin), top of the
lower chamfer 37.190 vs 37.197, top of the upper chamfer 41.490 vs 41.427.

The volume gap is a constant Hausdorff distance of 3.3429 mm at all three sizes
— one systematic difference, not noise. It decomposes into exactly two causes,
both on the CadQuery side:

1. **`lip_enabled` is inert in the CadQuery `bin` mode.** `main.py` unions a base
   profile at the rim and then cuts it away again with the cavity, which runs to
   `total_h + 1.0`. Rendering `bin` with `lip_enabled` true and false gives
   **identical volume (21748.362 mm³) and identical bbox** — the same defect the
   baseline pack records as quirk 1 for the removed OpenSCAD side. The CadQuery
   bin cannot stack. Setting `cup`'s `lip_style_id = 3` (no lip) to match removes
   most of the gap: 22983.134 vs 21748.362, from 16 % down to 5.4 %.
2. **The CadQuery foot is 4.75 mm tall, not 5.00 mm.** Its horizontal planes sit
   at z = 0 / 4.750 / 5.950 / 21.000; the OpenSCAD cup's at z = 0 / 5.000 /
   6.200 / 21.000 — the *same four planes with the same areas to 0.02 mm²*,
   offset by exactly 0.25 mm. The pack records the foot height as an interface
   dimension of **5.0 mm**; the OpenSCAD side matches it, the CadQuery side is
   0.25 mm short. The residual after accounting for the riser is the difference
   between a true 45° chamfer and CadQuery's linear loft between profile wires.

Both causes are defects in `main.py`, which this lane was scoped not to change.
They are reported rather than worked around: matching them would have meant
building a bin that cannot stack and a foot 0.25 mm off the standard. **Parity is
achieved on footprint and height; it is blocked on volume by the CadQuery side's
missing lip and short foot.** Repairing `main.py` is a separate change.

## Spec-tool conformance

```
y4d-spec check ./gridfinity -v
  ok gridfinity (./gridfinity)
  cartridges=1 failures=0 notes=0 geometry=NOT verified (pass --render) renders=0 presets=0 skipped=0
```

Green on the manifest bar. With `--render` it is also green, and it says in its
own words why it is not the geometry gate for these three modes:

```
y4d-spec check ./gridfinity --render -v
  ok gridfinity (./gridfinity, 5 render(s) verified (3 preset), 3 skipped (no OpenSCAD kernel))
       (bin, bin): ok — volume 21750.88mm3, 1 body/bodies, watertight
       (baseplate, baseplate): ok — volume 4497.73mm3, 1 body/bodies, watertight
       (cup, cup): skip — OpenSCAD mode ('cup.scad') — this checker has no
            OpenSCAD kernel, so the mesh was NOT verified here; the platform renders it
       (baseplate_scad, baseplate_scad): skip — OpenSCAD mode ('baseplate.scad') — ...
       (lid, lid): skip — OpenSCAD mode ('lid.scad') — ...
       (bin, bin, preset 'small_parts_bin'): ok — 21282.54mm3, 1 body, watertight
       (bin, bin, preset 'deep_bin'): ok — 48007.83mm3, 1 body, watertight
       (baseplate, baseplate, preset 'standard_baseplate'): ok — 9276.22mm3, 1 body, watertight
  cartridges=1 failures=0 notes=2 geometry=verified renders=5 presets=3 skipped=3
```

**failures=0.** The three OpenSCAD modes are skipped, not verified, because this
checker has no OpenSCAD kernel — so the geometry evidence for them is the
40-variant sweep above, which renders each mode through OpenSCAD itself with the
platform's own injection shape.

The 2 notes are thin-wall printability advisories on the **CadQuery**
`baseplate` (median local thickness 0.50 mm), pre-existing and untouched by this
change. Notes never fail a cartridge.

## Cross-engine classification

`verify_parity.py`'s own `classify_mode`, run against this manifest, returns:

```
bin              -> skip   scad_file 'main.py' is a CadQuery-only placeholder
baseplate        -> skip   scad_file 'main.py' is a CadQuery-only placeholder
cup              -> skip   OpenSCAD-only mode (no cup.py alongside cup.scad)
baseplate_scad   -> skip   OpenSCAD-only mode (no baseplate.py alongside baseplate.scad)
lid              -> skip   OpenSCAD-only mode (no lid.py alongside lid.scad)
```

Five skips, **zero failures**: no mode declares a `cq_file` it does not ship,
which is the condition that would make the parity sweep fail a cartridge.
