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

> **Superseded.** That separate change was made in the follow-up pass below.
> `main.py` was repaired and the same three comparisons now pass on volume as
> well as envelope — 0.4702 %, 1.0426 % and 0.0730 % against a 2 % rule. See
> [CadQuery repair + parity](#cadquery-repair--parity). The two causes named
> here were correct, and two further defects (the baseplate's footprint rule and
> its socket clearance) and one more (the magnet square) were found while fixing
> them.

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

> **The CadQuery volumes in the block above are the pre-repair ones.** They are
> left as recorded because this section documents the clean-room lane as it ran.
> The CadQuery side was repaired in the follow-up pass below, and the current
> figures are in [CadQuery repair + parity](#cadquery-repair--parity). `y4d-spec`
> is still `failures=0`, still 5 renders and 3 skips, still 2 notes.

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

---

# CadQuery repair + parity

The clean-room lane above re-created the three OpenSCAD modes and left the
CadQuery side untouched, reporting two defects it had found there and was scoped
not to fix. This section is the follow-up pass that fixed them, under
**ADR-021 amendment §3** — *"a cartridge that fails is repaired when it is ours;
dual-engine cartridges must agree between kernels"*. `main.py` is MADFAM's own
authoring from the published standard, so it is repaired, not removed.

The repair changed only `main.py`. The OpenSCAD modes, the manifest, the presets
and every parameter id, range and default are untouched.

## The five defects and what each became

| # | Defect | Was | Now |
| :-- | :--- | :--- | :--- |
| 1 | **`lip_enabled` inert.** The lip was unioned onto the rim and then cut away again by a cavity running to `total_h + 1.0`. `bin` rendered byte-identical with the flag true and false — **the bin could not stack**. | 21750.876 mm³ either way | Subtractive recess. 25168.764 mm³ on, 22534.022 mm³ off — a 2634.74 mm³ difference. |
| 2 | **Foot 4.75 mm.** The chamfer stack alone, with no riser; the standard's foot is 5.00 mm. | planes at 0 / 4.750 / 5.950 / 21.000 | planes at 0 / 5.000 / 6.200 / 21.000 |
| 3 | **Socket clearance 1.0 mm.** `build_baseplate` passed `shrink=-2.0 * SOCKET_CLEAR` with `SOCKET_CLEAR = 0.25`, i.e. 0.5 mm per side — four times the standard's nominal. | 1.0 mm diametral | **0.25 mm diametral** (0.125 mm per side) |
| 4 | **Baseplate footprint 42·n − 0.5.** The plate used the *bin's* footprint rule. A 41.75 mm socket mouth does not fit inside a 41.5 mm outline, so cutting the socket truncated the plate's own top face (measured 5.2423 mm on a plate asked for 5.25). | 41.5 / 83.5 mm at n = 1 / 2 | **42.0 / 84.0 mm** — plates butt, as the standard requires |
| 5 | **Magnet centres at ±12.75 mm.** `MAG_INSET = 8.0` put them 8 mm in from each cell corner, giving a 25.5 mm square where the standard's — and the cartridge's own `magnet_socket_6x2` CDG interface's — is 26 mm. | ±12.750 mm | **±13.000 mm**, measured |

Two smaller corrections came with them, both cases of the code contradicting the
manifest it ships with:

- `bp_thickness`'s in-code fallback was 4.75 where the manifest's default is
  5.25. A render with nothing injected now builds the plate the configurator's
  own defaults describe.
- `bp_thickness`'s clamp floor was `BASE_H + 0.5` = 5.25, which silently refused
  the 4.75 mm minimum the manifest advertises as legal. It is now `BASE_H`, and
  `bp_thickness = 4.75` renders.

## What changed in `main.py`, by function

| Function | Change |
| :--- | :--- |
| module constants | `BASE_H` is now the 4.75 mm chamfer stack only; `BASE_RISER = 0.25` and `FOOT_H = 5.00` are new. `SOCKET_CLEAR_SIDE = 0.125` replaces the per-side misuse of `SOCKET_CLEAR`. `LIP_H` / `LIP_HEADROOM` are new. `MAG_INSET` became `MAG_PITCH = 26.0`. |
| `rr_wire` | Takes `xsz, ysz` instead of one square `size`, so the profile can be swept around a non-square footprint. |
| `profile_prism` **(new)** | The chamfer stack swept around any rounded rectangle, with the 0.25 mm full-width riser above it. One function builds the foot, the socket and the lip recess, so the three can never drift apart. |
| `base_profile_solid` | Now a thin wrapper: `profile_prism` on a square `CELL` section. Signature gains `with_riser`. |
| `footprint_prism` | Gains `clear`, the footprint rule — `GRID_CLEAR` (42·n − 0.5) for a bin, `0` (42·n) for a baseplate. |
| `build_bin` | Feet are `FOOT_H` tall and the body starts there. The additive lip block is gone; the cavity and the lip recess are unioned into one cutting tool and cut once, so the interior stays a single void. |
| `_lip_recess` **(new)** | The recess: the base profile swept around the whole footprint, widest section at the rim, clipped to the top `LIP_H`, inset by `wall + LIP_HEADROOM/2` per side. Returns `None` — rim stays a plain wall — when the bin is too short or too narrow to carry one. |
| `build_baseplate` | Plate footprint 42·n. Socket cut with `shrink=-SOCKET_CLEAR_SIDE` and no riser, so it is 4.75 mm deep and opens at the plate's top face. |
| `_cut_magnets` | Centres from `MAG_PITCH / 2` rather than an inset from the cell corner. |

## Interface dimensions, measured

Sections through the exported mesh, not assertions about the source.

| Quantity | Standard | Measured | Where |
| :--- | :--- | :--- | :--- |
| Foot, bed section | 35.60 mm | **35.6045 mm** | `bin` 1×1×3 at z = 0.001 |
| Foot, top of lower chamfer | 37.20 mm | **37.2000 mm** | at z = 0.800 |
| Foot, top of straight section | 37.20 mm | **37.2830 mm** | at z = 2.600 |
| Foot, top of chamfer stack | 41.50 mm | **41.5000 mm** | at z = 4.750 |
| Foot, top (after the riser) | 41.50 mm | **41.5000 mm** | at z = 4.990 |
| **Foot height** | **5.00 mm** | **5.000 mm** | full width from 4.750 to 5.000, body above |
| Socket mouth | 41.75 mm | **41.7357 mm at z = 5.249**, converging on 41.75 at the top face | `baseplate` 1×1 @ 5.25 |
| **Foot-to-socket clearance** | **0.25 mm** | **0.25 mm diametral** | 41.75 − 41.50 |
| Baseplate footprint | 42·n | **42.0 / 84.0 / 168.0 mm** at n = 1 / 2 / 4 | |
| Bin footprint | 42·n − 0.5 | **41.5 / 83.5 / 251.5 mm** at n = 1 / 2 / 6 | |
| Magnet socket | 6 mm dia × 2 mm | **6.0000 mm** | pockets sectioned at z = 1.0 |
| Magnet centres | 26 mm square | **±13.000 mm** in X and Y | |

The socket mouth is reported at z = 5.249 rather than at the face itself because
a horizontal section exactly at a planar top face returns the outline, not the
opening. Walking up — 41.0361 at 5.200, 41.4644 at 5.230, 41.6072 at 5.240,
41.6929 at 5.246, 41.7357 at 5.249 — converges on 41.75.

## Cross-engine parity: CadQuery `bin` vs OpenSCAD `cup`

Rendered at the three configurations the clean-room lane used, at the plain
configuration (no dividers, no label, no scoop, no wall pattern, no tapered
corner, no efficient floor, no magnets, no screws), and compared with the
platform's own rule — `y4d-s3/scripts/qa/verify_parity.py:check_mesh_parity`
at its default tolerance 0.001: **bbox extents within 0.001 mm**, **volume
within max(0.1 mm³, 2 % of the larger)**, **surface divergence within 0.5 mm**.

The CadQuery side is rendered through the platform runner
(`apps/api/services/engine/cq_runner.py`), the OpenSCAD side with
`--backend=Manifold` under `timeout 600`.

`bin` and `cup` expose **different parameter sets** — `cup_wall_thickness = 0`
means auto-by-height and `cup_floor_thickness` defaults to 0.7, where `bin`
takes `wall = 1.2` and `floor_th = 1.2`. Parity is a question about the geometry
the two kernels build from the *same physical description*, so the cup is driven
at the bin's wall and floor rather than at its own defaults.

| Config | bbox Δ | Tolerance | Volume `cup` | Volume `bin` | Volume Δ | Tolerance | Verdict |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 2 × 1 × 3 | **0.000000 mm** | 0.001 | 25287.675 | 25168.764 | 118.911 (0.4702 %) | 505.753 | **PASS** |
| 3 × 2 × 5 | **0.000000 mm** | 0.001 | 74398.095 | 73622.401 | 775.693 (1.0426 %) | 1487.962 | **PASS** |
| 1 × 1 × 6 | **0.000000 mm** | 0.001 | 17488.016 | 17475.257 | 12.759 (0.0730 %) | 349.760 | **PASS** |

**3 of 3 pass. Every mesh watertight, every mesh one body.**

Before the repair the same three comparisons failed on volume at 6.85 %, 4.85 %
and 11.35 % — the two engines disagreed by more than five times the tolerance.
The residual now is B-Rep-versus-mesh: CadQuery lofts a true 45° chamfer between
wires while OpenSCAD hulls between two extrusions at `$fn = 32`, and the fillets
tessellate differently. It scales with the number of filleted corners, which is
why 3 × 2 × 5 — six cells, so the most feet — carries the largest residual.

## The 40-variant OpenSCAD sweep, re-run

`docs/measure_cleanroom.py` re-run unchanged against the same baseline pack after
the repair:

```
40 passed, 0 failed, of 40
```

Watertight 40/40, body count 40/40, bounding box within ±0.05 mm 40/40 — every
one at 0.0000 mm, the envelope matching exactly. Nothing regressed: the repair
touched only `main.py`, and this sweep exercises only the OpenSCAD modes, so the
result is the expected one and is recorded as a control rather than as news.

## The CadQuery side through the platform runner

Every CadQuery configuration that the manifest describes, rendered through
`cq_runner.run_cadquery_script` and measured with trimesh:

| Group | Configurations | Result |
| :--- | ---: | :--- |
| Defaults (`bin`, `baseplate`) | 2 | watertight, 1 body |
| Presets (`small_parts_bin`, `deep_bin`, `standard_baseplate`) | 3 | watertight, 1 body |
| `bin` parameters off default, each end of each range | 12 | watertight, 1 body |
| `baseplate` parameters off default | 4 | watertight, 1 body |
| | **21** | **0 failures** |

**No CadQuery parameter is inert.** `lip_enabled` moves volume by 2634.742 mm³
at 2 × 1 × 3, which was the defect; `bp_thickness = 4.75`, the manifest's
declared minimum, now renders at all.

## y4d-spec

```
y4d-spec check ./gridfinity --render -v
  ok gridfinity (./gridfinity, 5 render(s) verified (3 preset), 3 skipped (no OpenSCAD kernel))
       (bin, bin): ok — volume 25168.76mm³, 1 body/bodies, watertight
       (baseplate, baseplate): ok — volume 5007.54mm³, 1 body/bodies, watertight
       (cup, cup): skip — OpenSCAD mode ('cup.scad') — this checker has no
            OpenSCAD kernel, so the mesh was NOT verified here; the platform renders it
       (baseplate_scad, baseplate_scad): skip — OpenSCAD mode ('baseplate.scad') — ...
       (lid, lid): skip — OpenSCAD mode ('lid.scad') — ...
       (bin, bin, preset 'small_parts_bin'): ok — volume 23314.67mm³, 1 body/bodies, watertight
       (bin, bin, preset 'deep_bin'): ok — volume 53225.27mm³, 1 body/bodies, watertight
       (baseplate, baseplate, preset 'standard_baseplate'): ok — volume 10078.47mm³, 1 body/bodies, watertight
  cartridges=1 failures=0 notes=2 geometry=verified renders=5 presets=3 skipped=3
```

**failures=0.** The 2 notes are the same thin-wall printability advisories on the
CadQuery `baseplate` recorded above (median local thickness 0.50 mm). They are
**not** resolved by this repair and are not claimed to be: the plate between
sockets is genuinely thin at the standard's own dimensions, the threshold is
marked provisional by the checker itself, and notes never fail a cartridge.

## Volumes moved, and why that is correct

The repair is a geometry fix, so the CadQuery volumes changed. Recorded so the
numbers are not later read as drift:

| Configuration | Before | After | Cause |
| :--- | ---: | ---: | :--- |
| `bin` 2 × 1 × 3 defaults | 21750.876 | 25168.764 | lip now real (+2634.74), foot now 5.00 mm |
| `bin` 3 × 2 × 5 | 66605.372 | 73622.401 | same |
| `bin` 1 × 1 × 6 | 15429.763 | 17475.257 | same |
| `baseplate` 2 × 1 @ 5.25 | 4497.730 | 5007.542 | footprint 42·n (83.5 × 41.5 → 84.0 × 42.0), socket clearance 0.25 not 1.0 |

## The top-level README

`README.md` documented seven parameters that never existed in this cartridge —
`gridx`, `gridy`, `gridz`, `stackable`, `magnet_holes`, `div_x`, `div_y` — under
a "Modes" list of three where the manifest declares five. It predated the
manifest. It has been rewritten from `project.json`: all 37 parameters with their
real ids, types, defaults, ranges and mode scoping, all 5 modes with their engine
and source file, all 10 presets, and the standard's dimensions. Nothing in it is
invented; every row is derived from the manifest.

## Reproducing

```
# parity, three configurations
<venv>/python cg2_parity.py <cartridge> <scaffold>

# the CadQuery side through the platform runner
<venv>/python cg2_cq_sweep.py

# the 40-variant OpenSCAD sweep (unchanged from the clean-room lane)
<venv>/python gridfinity/docs/measure_cleanroom.py \
  --pack <baseline-pack> --cartridge <cartridge> --scaffold <scaffold>

# the manifest and CadQuery geometry bar
PYTHONPATH=<y4d site-packages> <l2venv>/y4d-spec check ./gridfinity --render -v
```

`<venv>` is `yantra4d/.venv/bin/python`; the scaffold is as described in the
clean-room section above. OpenSCAD renders are sequential, each under
`timeout 600`.
