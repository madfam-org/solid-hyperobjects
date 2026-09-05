# Clean-room verification — `stemfie`

ADR-021 §3(c) acceptance evidence for this cartridge. Every number below is
measured, not asserted; the scripts that produce them ship alongside this file.

## Method

Two harnesses, both in this directory, both run on
`/Users/aldoruizluna/labspace/yantra4d/.venv/bin/python` (CadQuery + trimesh):

| Script | What it proves |
| :--- | :--- |
| `verify_cleanroom.py` | Renders every variant in the baseline pack through this cartridge's `main.py` using the platform's own parameter-injection contract (bare globals plus `target_part`, exactly as `apps/api/services/engine/cq_runner.py` does it), meshes each with trimesh (`force="mesh", process=True`), and compares watertightness, body count, volume and bounding box against the recorded baseline. It also measures the interface dimensions **off the B-Rep**, not the mesh. |
| `test_parameters_change_geometry.py` | Renders each declared parameter perturbed away from its default, in every mode the manifest makes it visible in, and asserts the volume moved. `fn` is asserted the other way: a tessellation hint must not move a B-Rep solid. |

Interface dimensions are read from the solid, not from the exported mesh,
deliberately. An STL tessellates a 4.2 mm circle into a polygon whose inscribed
diameter reads ~4.193 mm — which is exactly the figure the baseline pack
records, and the pack says so. A mating part is manufactured against the exact
value, so the exact value is what is checked.

## Tolerances applied

Per the lane brief and the baseline pack's `SPEC.md` §4:

- watertight, and **one body**, for every variant — including the two the
  baseline recorded as broken;
- interface dimensions within **±0.05 mm**;
- volume within **±2 %** of the recorded value;
- bounding box within **±0.5 mm**.

## Interface vs form

ADR-021 §4 is the governing text: the STEMFIE *design* is published under its
own terms, so this re-creation targets the **interface standard** — the
functional dimensions another part mates to — and authors its own **form** for
everything else. Both halves are proved below: interface matched, form
different.

### Interface — matched, 16/16

Measured off the B-Rep by `verify_cleanroom.py`'s `interface_checks`, tolerance
±0.05 mm:

| Measurement | Baseline | Measured | Verdict |
| :--- | ---: | ---: | :--- |
| Block unit (beam X extent ÷ `length_units`) | 10.000 | 10.000 | ok |
| Beam section width (1 BU) | 10.000 | 10.000 | ok |
| Beam section height (1 BU) | 10.000 | 10.000 | ok |
| Beam section width (4 BU) | 40.000 | 40.000 | ok |
| Through-hole diameter | 4.200 | 4.200 | ok |
| Hole pitch along the beam | 10.000 | 10.000 | ok |
| Through-hole count (4 BU beam) | 4 | 4 | ok |
| Brace plate thickness (1 unit) | 2.500 | 2.500 | ok |
| Brace plate thickness (2 units) | 5.000 | 5.000 | ok |
| Brace arm A extent (5 BU) | 50.000 | 50.000 | ok |
| Brace arm B extent (3 BU) | 30.000 | 30.000 | ok |
| Brace arm angle (deg) | 90.000 | 90.000 | ok |
| Fastener collar diameter | 5.700 | 5.700 | ok |
| Fastener length (4 BU) | 40.000 | 40.000 | ok |
| Fastener shank diameter | 4.000 | 4.000 | ok |
| Shank-to-hole clearance (diametral) | 0.200 | 0.200 | ok |

The hole and pitch readings are exact, not the baseline's 4.193 / 9.996: those
figures are the pack's own tessellation of a nominal 4.2 mm circle into a
32-sided polygon, and the pack says so. The B-Rep carries the value a mating
part is manufactured against.

The hole faces are selected by **axis**, not by radius. The beam's long-edge
fillets are cylinders too, and an early version of this harness averaged them in
and read the hole as 2.900 mm — a harness fault, not a geometry fault. Filtering
by radius instead would make the test circular (it could only ever find the value
it expects), so orientation is the discriminator.

### Form — ours, and different

None of these is a dimension another part mates to, and each is a deliberate
departure from the recorded baseline shape.

| Feature | Baseline | This cartridge | How it differs |
| :--- | :--- | :--- | :--- |
| Beam long edges | chamfered (recorded as `form`, "chamfered long edges") | **0.8 mm fillet** | A rounded profile, not a flat 45° cut. The silhouette is an arc where the baseline's is a straight facet. |
| Beam hole mouths | square | square | Left square deliberately: a mouth chamfer on three intersecting hole arrays is where the boolean gets fragile, and this cartridge's whole reason for existing is that the baseline's boolean fell apart there. |
| Brace outer corners | square (the baseline's volumes fit sharp square cells) | **2.5 mm radius** | Every convex vertical edge is rounded. |
| Brace re-entrant corner | square | **2.0 mm fillet** | The inside of the L carries a fillet, which also removes the stress riser a square inside corner puts in a printed part. |
| Brace hole mouths | square | **0.4 mm × 45° chamfer, both faces** | A visible lead-in on both sides of every hole. |
| Fastener collar | a flat ring, ~2.0 mm tall (derived: 25.73 mm³ of ring volume at Ø5.7 over Ø4.0) | **1.5 mm cylindrical land over a 1.0 mm conical underside taper**, 2.5 mm total | The underside is a cone, not a flat shoulder — it self-centres into a chamfered hole and prints without a horizontal overhang at the collar. |
| Fastener free end(s) | square-cut | **0.8 mm taper down to Ø3.4** | A lead-in on the pin's free end, and on both ends of the plain shaft. |

Everything in the "This cartridge" column is generated from named constants at
the top of `main.py` (`BEAM_EDGE_R`, `BRACE_OUT_R`, `BRACE_IN_R`,
`BRACE_MOUTH_C`, `COLLAR_LAND_H`, `COLLAR_TAPER_H`, `LEAD_IN_H`, `LEAD_IN_D`),
separated in the source from the interface constants so the two are never
confused by a later editor.

## The baseline defects, fixed rather than reproduced

`SPEC.md` §5 records two, and says to fix them:

1. **`holes_z` off produced 3 bodies and a non-watertight mesh** at otherwise
   default beam parameters (`beam__beam__holes_z-min`).
2. **`beam__beam__mix-b` was non-watertight with 57 bodies** — larger
   width/height with a partial hole set, the hole arrays on different axes
   intersecting and the boolean degenerating.

Both have the same cause and the same fix. This cartridge builds the entire
hole array as one set of solids, **fuses it once**, and subtracts it in a
**single boolean** (`_cut_all` in `main.py`); the beam's edge fillet is applied
to the clean box **before** the holes, never to the holed body. OCCT then has
one tool and one intersection problem to resolve instead of a chain of partial
results, and every variant — the two above included — comes out as one
watertight solid. The measured table below is the proof.

## Measured results

### `y4d-spec check ./stemfie --render -v`

```
  ok stemfie (./stemfie, 7 render(s) verified (4 preset))
       (beam, beam): ok — volume 2734.82mm³, 1 body/bodies, watertight
       (brace, brace): ok — volume 1051.07mm³, 1 body/bodies, watertight
       (fastener, fastener): ok — volume 526.51mm³, 1 body/bodies, watertight
       (beam, beam, preset 'beam_5u'): ok — volume 3418.52mm³, 1 body/bodies, watertight
       (fastener, fastener, preset 'beam_5u'): ok — volume 652.12mm³, 1 body/bodies, watertight
       (brace, brace, preset 'brace_90deg'): ok — volume 1051.07mm³, 1 body/bodies, watertight
       (fastener, fastener, preset 'fastener_standard'): ok — volume 275.28mm³, 1 body/bodies, watertight
y4d-spec check: cartridges=1 failures=0 notes=0 geometry=verified renders=7 presets=4 skipped=0
```

Zero notes. Each unscoped preset is offered only in the modes whose parameters it
sets, resolved from `visible_in_modes`, so none renders geometry identical to its
mode's defaults while claiming to change something.

### Per-parameter regression

`test_parameters_change_geometry.py` — **checks=15 failures=0**. Every declared
parameter moves the volume in every mode `visible_in_modes` exposes it in; `fn`
is asserted the other way and correctly does not move a B-Rep solid.

| Parameter | Mode | Baseline volume | Perturbed | Verdict |
| :--- | :--- | ---: | ---: | :--- |
| `length_units` | beam | 2734.599 | 4785.548 | ok |
| `length_units` | fastener | 526.746 | 903.738 | ok |
| `width_units` | beam | 2734.599 | 8247.747 | ok |
| `height_units` | beam | 2734.599 | 8247.747 | ok |
| `holes_x` | beam | 2734.599 | 3067.239 | ok |
| `holes_y` | beam | 2734.599 | 3067.239 | ok |
| `holes_z` | beam | 2734.599 | 3067.239 | ok |
| `arm_a_units` | brace | 1050.974 | 1690.330 | ok |
| `arm_b_units` | brace | 1050.974 | 1690.330 | ok |
| `thickness_units` | brace | 1050.974 | 2113.174 | ok |
| `holes_enabled` | brace | 1050.974 | 1235.380 | ok |
| `fastener_type_id` | fastener | 526.746 | 499.790 | ok |
| `fn` | beam / brace / fastener | — | unchanged | ok (B-Rep: correctly unchanged) |

### Baseline variant sweep — 48/48

`verify_cleanroom.py`, every variant in `VARIANTS.json` rendered through the
platform's own parameter-injection contract and compared against
`MEASUREMENTS.json`. **Every variant watertight, one body**, volume within
+1.68 % / −1.19 % (tolerance ±2 %), bounding box within ±0.5 mm on every axis.

| Variant | wt | bodies | volume mm³ | Δ vol | verdict |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `beam__beam__defaults` | 1 | 1 | 2734.82 | +0.03 % | ok |
| `beam__beam__preset-beam_5u` | 1 | 1 | 3418.52 | −0.03 % | ok |
| `beam__beam__preset-brace_90deg` | 1 | 1 | 2734.82 | +0.03 % | ok |
| `beam__beam__preset-fastener_standard` | 1 | 1 | 1367.41 | +0.38 % | ok |
| `beam__beam__corner-allmin` | 1 | 1 | 994.50 | +0.90 % | ok |
| `beam__beam__corner-allmax` | 1 | 1 | 220432.45 | −0.22 % | ok |
| `beam__beam__mix-a` | 1 | 1 | 36145.04 | −0.04 % | ok |
| **`beam__beam__mix-b`** | **1** | **1** | 64802.06 | −0.13 % | **ok — baseline was 57 bodies, not watertight** |
| `beam__beam__length_units-min` | 1 | 1 | 683.71 | +1.07 % | ok |
| `beam__beam__length_units-max` | 1 | 1 | 13674.07 | −0.24 % | ok |
| `beam__beam__width_units-max` | 1 | 1 | 11005.22 | −0.03 % | ok |
| `beam__beam__height_units-max` | 1 | 1 | 11005.21 | −0.03 % | ok |
| `beam__beam__holes_x-min` | 1 | 1 | 3067.47 | +0.08 % | ok |
| `beam__beam__holes_y-min` | 1 | 1 | 3067.47 | +0.08 % | ok |
| **`beam__beam__holes_z-min`** | **1** | **1** | 3067.48 | +0.08 % | **ok — baseline was 3 bodies, not watertight** |
| `beam__beam__arm_a_units-min` | 1 | 1 | 2734.82 | +0.03 % | ok |
| `brace__brace__defaults` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__preset-beam_5u` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__preset-brace_90deg` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__preset-fastener_standard` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__corner-allmin` | 1 | 1 | 236.57 | −1.19 % | ok |
| `brace__brace__corner-allmax` | 1 | 1 | 8112.63 | +0.28 % | ok |
| `brace__brace__mix-a` | 1 | 1 | 2485.36 | +1.68 % | ok |
| `brace__brace__mix-b` | 1 | 1 | 4255.93 | +0.04 % | ok |
| `brace__brace__length_units-min` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__length_units-max` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__width_units-max` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__height_units-max` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__holes_x-min` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__holes_y-min` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__holes_z-min` | 1 | 1 | 1051.07 | +0.38 % | ok |
| `brace__brace__arm_a_units-min` | 1 | 1 | 625.94 | −0.04 % | ok |
| `fastener__fastener__defaults` | 1 | 1 | 526.51 | +0.26 % | ok |
| `fastener__fastener__preset-beam_5u` | 1 | 1 | 652.12 | +0.32 % | ok |
| `fastener__fastener__preset-brace_90deg` | 1 | 1 | 526.51 | +0.26 % | ok |
| `fastener__fastener__preset-fastener_standard` | 1 | 1 | 275.28 | −0.06 % | ok |
| `fastener__fastener__corner-allmin` | 1 | 1 | 149.67 | −0.61 % | ok |
| `fastener__fastener__corner-allmax` | 1 | 1 | 2509.36 | +0.49 % | ok |
| `fastener__fastener__mix-a` | 1 | 1 | 903.34 | +0.40 % | ok |
| `fastener__fastener__mix-b` | 1 | 1 | 1755.69 | +0.44 % | ok |
| `fastener__fastener__length_units-min` | 1 | 1 | 149.67 | −0.61 % | ok |
| `fastener__fastener__length_units-max` | 1 | 1 | 2536.29 | +0.53 % | ok |
| `fastener__fastener__width_units-max` | 1 | 1 | 526.51 | +0.26 % | ok |
| `fastener__fastener__height_units-max` | 1 | 1 | 526.51 | +0.26 % | ok |
| `fastener__fastener__holes_x-min` | 1 | 1 | 526.51 | +0.26 % | ok |
| `fastener__fastener__holes_y-min` | 1 | 1 | 526.51 | +0.26 % | ok |
| `fastener__fastener__holes_z-min` | 1 | 1 | 526.51 | +0.26 % | ok |
| `fastener__fastener__arm_a_units-min` | 1 | 1 | 526.51 | +0.26 % | ok |

The rows where several variants share a volume are the pack's own recorded
behaviour, not a dispatch fault: they perturb a parameter that mode does not
consume. The manifest scopes those with `visible_in_modes`, so the UI never
offers them there; the sweep renders them anyway because the baseline recorded
them, and they match.

## Deviations

1. **The pack's `SPEC.md` §5.3 says the manifest declares no mode scoping; the
   recorded `CONTRACT.json` does**, on every parameter. The contract is the
   artefact, so it was followed. The consequence is the good one — the parameter
   leak the prose warns about does not exist here, and the presets still work,
   because `y4d-spec`'s preset expansion scopes an unscoped preset from exactly
   that field.

2. **One factual correction to the recorded contract.** The `length_units`
   tooltip read "1 BU = 12.5 mm" in both languages while every measured dimension
   in the pack — and the standard — is 10 mm. Corrected. No id, type, range,
   default, group or scope was changed.

3. **No hole-mouth chamfer on the beam**, though the brace has one. It would have
   been a further form marker, but it puts a chamfer on three *intersecting* hole
   arrays — precisely the boolean that degenerated in the baseline and that this
   re-creation exists to fix. The form split is already carried elsewhere, so the
   risk bought nothing.

4. **Two defects the sweep found in this cartridge, both fixed before the PR
   settled.** A brace with either arm at a single block unit failed to build (the
   L footprint degenerates to a rectangle and the six-point path then contains a
   zero-length segment; OCCT rejects it as `BRep_API: command not done`), and the
   interface harness read the hole as 2.900 mm because it counted the beam's edge
   fillets as holes. Both are recorded here rather than quietly corrected: the
   sweep earned its keep by finding them.

5. **Render times in this record are not comparable to a quiet machine.** These
   runs shared the host with sibling clean-room lanes at load averages of
   150–265. The 20 × 4 × 4 corner (320 fused hole cutters) took 256 s under that
   load — the manifest maximum, inside the platform's 600 s budget, and
   substantially faster on an idle host.
