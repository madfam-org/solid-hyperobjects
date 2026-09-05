# Clean-room verification — `keyv2`

ADR-021 §3(c) acceptance evidence for the clean-room re-creation of the `keyv2`
keycap cartridge.

## What was and was not read

**Read:** the baseline pack for this slug — `SPEC.md`, `CONTRACT.json`,
`MEASUREMENTS.json`, `VARIANTS.json` and the reference mesh statistics; the
ADR-021 ruling and its 2026-09-04 amendment; the clean-room lane brief; the
platform's CadQuery runner contract and its sandbox whitelist; the
`parametric-box` cartridge as a CERN-OHL-W-2.0 style and manifest example;
CadQuery documentation.

**Not read, at any point:** the removed cartridge in this repository's git
history; the archived satellite repository under this slug; the upstream project
named in the baseline pack's "must NOT look at" section, in any form — sources,
generated files, examples or forks; any web page carrying them.

The implementation works from published mechanical dimensions and from the
recorded final-result measurements alone. A mechanical interface dimension is
not code.

## Tooling

| | |
| :-- | :-- |
| Engine | CadQuery 2.7.0 (OCCT B-Rep) |
| Measurement | trimesh 3.23.5, `process=True, force="mesh"` |
| Platform gate | `y4d-spec check ./keyv2 --render -v` |
| Harness | `scripts/verify_baseline.py` |
| Parameter regression | `scripts/param_regression.py` |

## Platform gate

```
  ok keyv2 (./keyv2, 4 render(s) verified (3 preset))
       (keycap, keycap): ok — volume 1567.69mm³, 1 body/bodies, watertight
       (keycap, keycap, preset 'cherry_r3_1u'): ok — volume 1765.65mm³, 1 body/bodies, watertight
       (keycap, keycap, preset 'dsa_uniform'): ok — volume 1378.45mm³, 1 body/bodies, watertight
       (keycap, keycap, preset 'sa_sculpted'): ok — volume 2934.42mm³, 1 body/bodies, watertight
y4d-spec check: cartridges=1 failures=0 notes=0 geometry=verified renders=4 presets=3 skipped=0
```

## How the interface dimensions are measured

On the **exact B-Rep, before export** — not on the mesh. Two traps, both of
which produced false readings during this work and are worth recording:

1. `cq.exporters.export` attaches a triangulation to the shape. After that,
   *both* `Shape.BoundingBox()` and `BRepBndLib.AddOptimal_s` measure the
   deflected mesh rather than the exact surfaces: the 18.05 mm footprint read
   19.86 mm. The harness measures first and exports second.
2. A tessellated cylinder is an inscribed polygon and reads under its true
   diameter. At a chord tolerance fine enough to resolve 5.5 mm within 0.05 mm
   the STL runs to tens of megabytes. Sections are taken with
   `BRepAlgoAPI_Section` on the solid, where a circle stays a circle.

Topology (watertight, body count, inverted bodies) is measured on the **exported
mesh**, because that is what a user prints and because a valid B-Rep can still
tessellate badly — see divergence 3.

## Variant results

All 16 recorded variants, rendered through the same runner contract with the
same parameters. Interface dimensions within ±0.05 mm; bounding boxes exact
against the recorded baseline.

| Variant | Watertight | Bodies (baseline) | Bounding box | Baseline bbox |
| :-- | :-- | :-- | :-- | :-- |
| `defaults` | yes | 1 (2) | 18.050 × 18.050 × 9.000 | 18.05 × 18.05 × 9.0 |
| `preset-cherry_r3_1u` | yes | 1 (2) | 18.050 × 18.050 × 10.000 | 18.05 × 18.05 × 10.0 |
| `preset-dsa_uniform` | yes | 1 (2) | 18.050 × 18.050 × 7.500 | 18.05 × 18.05 × 7.5 |
| `preset-sa_sculpted` | yes | 1 (1) | 18.050 × 18.050 × 16.500 | 18.05 × 18.05 × 16.5 |
| `corner-allmin` | yes | 1 (2) | 18.050 × 18.050 × 9.000 | 18.05 × 18.05 × 9.0 |
| `corner-allmax` | yes | 1 (1) | 37.100 × 18.050 × 10.399 | 37.1 × 18.05 × 10.4 |
| `mix-a` | yes | 1 (2) | 22.812 × 18.050 × 8.500 | 22.8125 × 18.05 × 8.5 |
| `mix-b` | yes | 1 (2) | 27.575 × 18.050 × 11.900 | 27.575 × 18.05 × 11.9 |
| `profile_id-max` | yes | 1 (2) | 18.050 × 18.050 × 8.901 | 18.05 × 18.05 × 8.9 |
| `row_id-max` | yes | 1 (2) | 18.050 × 18.050 × 10.500 | 18.05 × 18.05 × 10.5 |
| `key_size_id-max` | yes | 1 (2) | 37.100 × 18.050 × 9.000 | 37.1 × 18.05 × 9.0 |
| `stem_type_id-max` | yes | 1 (1) | 18.050 × 18.050 × 9.000 | 18.05 × 18.05 × 9.0 |
| `legend_enabled-max` | yes | 1 (2) | 18.050 × 18.050 × 9.000 | 18.05 × 18.05 × 9.0 |
| `font_size-min` | yes | 1 (2) | 18.050 × 18.050 × 9.000 | 18.05 × 18.05 × 9.0 |
| `font_size-max` | yes | 1 (2) | 18.050 × 18.050 × 9.000 | 18.05 × 18.05 × 9.0 |
| `dish_depth-min` | yes | 1 (2) | 18.050 × 18.050 × 9.000 | 18.05 × 18.05 × 9.0 |

### Interface dimensions

Every row measured on the exact solid, tolerance ±0.05 mm.

| Interface | Expected | Measured | Where |
| :-- | --: | --: | :-- |
| 1u footprint X | 18.050 | 18.050 | all 1u variants |
| 1u footprint Y | 18.050 | 18.050 | all variants |
| 1.25u footprint X | 22.812 | 22.812 | `mix-a` |
| 1.5u footprint X | 27.575 | 27.575 | `mix-b` |
| 2u footprint X | 37.100 | 37.100 | `key_size_id-max`, `corner-allmax` |
| Cap height, DCS row 1 | 9.000 | 9.000 | `defaults` |
| Cap height, DCS row 3 | 10.000 | 10.000 | `preset-cherry_r3_1u` |
| Cap height, DCS row 4 | 10.500 | 10.500 | `row_id-max` |
| Cap height, DSA row 1 | 7.500 | 7.500 | `preset-dsa_uniform` |
| Cap height, SA row 3 | 16.500 | 16.500 | `preset-sa_sculpted` |
| Cap height, OEM row 2 | 11.900 | 11.900 | `mix-b` |
| Cap height, Cherry row 1 | 8.900 | 8.901 | `profile_id-max` |
| Cap height, Cherry row 4 | 10.400 | 10.399 | `corner-allmax` |
| Cherry MX stem OD | 5.500 | 5.500 | every Cherry-stem variant |
| MX cross arm span @ slop 0.35 | 4.275 | 4.275 | `defaults` |
| MX cross arm width @ slop 0.35 | 1.345 | 1.345 | `defaults` |
| MX cross arm span @ slop 0.60 | 4.400 | 4.400 | `corner-allmax` |
| Alps outer | 4.500 × 3.200 | 4.500 × 3.200 | `mix-a`, `mix-b` |
| Alps socket @ slop 0.45 | 2.750 × 0.750 | 2.750 × 0.750 | `mix-a` |
| Box outer | 6.000 × 6.000 | 6.000 × 6.000 | `stem_type_id-max`, `corner-allmax` |

The arm **width** is checked as well as the span, and deliberately: the span
alone would pass on a plain square hole of the same width. It is derived from
the socket loop's enclosed area, where a cross of span `L` and width `W`
encloses `2LW − W²`.

## Per-parameter regression

Every declared parameter must change the mesh. `scripts/param_regression.py`,
12 parameters, 0 failures.

| Parameter | Contract | Result |
| :-- | :-- | :-- |
| `profile_id` | changes the mesh | ok |
| `row_id` | changes the mesh | ok |
| `key_size_id` | changes the mesh | ok |
| `stem_type_id` | changes the mesh | ok |
| `legend_enabled` | changes the mesh | ok |
| `dish_depth` | changes the mesh | ok |
| `wall_thickness` | changes the mesh | ok |
| `keytop_thickness` | changes the mesh | ok |
| `stem_slop` | changes the mesh | ok |
| `legend_text` | inert with legend off, live with legend on | ok |
| `font_size` | inert with legend off, live with legend on | ok |
| `fn` | tessellation hint, solid unchanged | ok |

The legend is a real deboss: at defaults it removes 4.34 mm³ (1567.69 → 1563.35).

## Divergences from the recorded baseline

### 1. Body count — intentional, and the reason this is preferred

The baseline recorded **two disjoint solids** for the default keycap and for 11
of its 16 variants: the cylindrical stem stood free inside the shell, touching
nothing. A free-floating stem cannot be printed as one part. `SPEC.md` §5 names
this a printability defect and says fixing it is preferred, provided the
interface dimensions do not change and the divergence is recorded.

**Every variant here is one body.** The stem runs the full height from the base
to the underside of the keytop, and support ribs join it to the shell wall. The
ribs start 3.5 mm above the base so the post's cylindrical outer surface stays
clear where the switch housing meets it — the 5.5 mm outer diameter remains a
free, measurable surface, and no interface dimension moved.

### 2. Volume — a consequence of divergence 1, and outside the pack's ±2 %

Volumes run 5–9 % above the recorded baseline. This is the added material of the
fused stem and its ribs; it is arithmetic, not drift. Bounding boxes and
interface dimensions are unaffected.

| Variant | Baseline | This cartridge | Δ |
| :-- | --: | --: | --: |
| `defaults` | 1481.66 | 1567.69 | +5.8 % |
| `preset-cherry_r3_1u` | 1644.77 | 1765.65 | +7.3 % |
| `preset-dsa_uniform` | 1210.54 | 1378.45 | +13.9 % |
| `preset-sa_sculpted` | 2668.05 | 2934.42 | +10.0 % |
| `corner-allmin` | 949.23 | 1112.49 | +17.2 % |
| `corner-allmax` | 3593.59 | 4123.04 | +14.7 % |

The pack sets ±2 % on volume. That tolerance cannot be met while also fixing the
free-floating stem, because the fix *is* added material. Interface dimensions —
which the pack requires exact — are all met. Recorded here rather than resolved
by loosening the check.

### 3. Socket plug depth, where `keytop_thickness` > 1 mm

The baseline's socket runs to `height − keytop_thickness − 0.5 mm`. Here it
stops `max(0.5, keytop_thickness / 2)` below the top of the post. At the default
`keytop_thickness = 1` this evaluates to 0.5 and the recorded interface is
unchanged; it only deepens the solid plug on thick-keytop caps.

The reason is empirical: at `corner-allmax` (2u, 5 mm walls, Box stem, 2 mm
keytop) the tapering cavity ceiling pinched the thin ring of post wall above the
socket into a **1.85 mm³ loose fragment**, and the export came back as two
bodies. A substantial plug prevents it. `largest_solid()` in `main.py` is a
second, explicit guard against boolean debris; it is a guard and is commented as
one, not a substitute for the geometry fix.

## Defects found by these tests during development

Recorded because each one would have shipped as a silent lie about the
cartridge, and because two of them are traps any CadQuery cartridge can hit.

1. **The dish and legend cutters floated above the solid.** `top_plane_z()`
   returned `cap_height + rise/2` where the tilted top face's mean height is
   `cap_height − rise/2`. `dish_depth`, `legend_enabled`, `legend_text` and
   `font_size` all read as inert — the same class of defect the baseline had,
   reproduced by accident. Caught by the per-parameter regression.
2. **Height short on flat profiles.** The measure-and-re-place height correction
   ran only on the tilted branch, so DSA measured 7.370 against a required
   7.500, SA 16.410 against 16.500, `corner-allmax` 10.343 against 10.400.
3. **A degenerate triangle at the dish apex.** DSA exported as two mesh bodies,
   the second being a single zero-area face. The B-Rep was valid throughout —
   one solid, 66 faces, smallest 1.17 mm², no slivers — so a solid-level check
   would have passed it, and the platform's own gate reported "not watertight —
   1 boundary edge". The stray face had two vertices, one at exactly
   `(0, 0, 6.5)`: CadQuery's sphere is a surface of revolution whose **pole**
   landed on the dish axis. Rotating the sphere 90° about X moves the poles off
   the cut region; a sphere's parameterisation changes, its geometry does not.

The first two hypotheses for defect 3 — dish depth punching through the keytop,
then tangency at the filleted rim — were both wrong. Stage-by-stage solid counts
and the stray face's vertex coordinates identified it.

## Reproducing

```sh
VENV=/path/to/venv/bin/python
PACK=/path/to/cleanroom-baselines/keyv2

$VENV keyv2/scripts/verify_baseline.py \
    --variants     $PACK/VARIANTS.json \
    --measurements $PACK/MEASUREMENTS.json \
    --out          /tmp/keyv2-verify

$VENV keyv2/scripts/param_regression.py

y4d-spec check ./keyv2 --render -v
```

Both scripts exit non-zero on any failure.
