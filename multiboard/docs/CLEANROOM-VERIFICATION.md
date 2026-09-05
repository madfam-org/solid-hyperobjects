# Clean-room verification — `multiboard`

ADR-021 §4 (interface-standard re-design). Everything below is measured, not
asserted; the harness that produced it is `docs/verify_cleanroom.py`, which
renders through the platform's own command shape and judges with trimesh.

| Field | Value |
| :-- | :-- |
| Cartridge | `multiboard`, mode `tile`, part `tile` |
| Engine | OpenSCAD 2026.02.13, `--backend=Manifold`, builtins only (no library includes) |
| Render command | `OpenSCAD --backend=Manifold -o out.stl -D x_cells=… -D y_cells=… -D cell_size=… -D height=… -D fn=… tile.scad` |
| Measurement | trimesh, `process=True, force="mesh"` |
| Interface tolerance | ±0.05 mm |
| Variants | 16 / 16 pass |
| Verified | 2026-09-05 |

Renders were run **sequentially**: each variant is a boolean against dozens of
full-depth helical thread tools, and overlapping them only makes the wall times
noisy.

## 1. Acceptance — every variant in `VARIANTS.json`

Rendered through this cartridge with the baseline's own parameter values, then
compared against the baseline's recorded statistics.

| Variant | s | Volume mm³ (ours) | Volume mm³ (baseline) | BBox ours | BBox baseline | Bodies ours/base | Watertight ours/base |
| :-- | --: | --: | --: | :-- | :-- | :-- | :-- |
| `defaults` | 2.8 | 33 262.7 | 23 790.6 | 113.00×113.00×6.40 | 100.0×100.0×6.4 | 1 / 1 | T / T |
| `preset-small_panel` | 2.8 | 33 262.7 | 23 790.6 | 113.00×113.00×6.40 | 100.0×100.0×6.4 | 1 / 1 | T / T |
| `preset-large_wall` | 8.2 | 88 326.5 | 71 782.4 | 213.00×163.00×6.40 | 200.0×150.0×6.4 | 1 / 1 | T / T |
| `preset-tool_rack` | 5.2 | 59 753.4 | 44 787.0 | 263.00×88.00×6.40 | 250.0×75.0×6.4 | 1 / 1 | T / T |
| `corner-allmin` | 0.5 | 2 648.8 | 67.2 | 38.00×38.00×4.00 | 20.0×20.0×4.0 | **1 / 4** | T / T |
| `corner-allmax` | 39.8 | 1 283 195.6 | 1 204 858.0 | 438.20×438.20×10.00 | 420.0×420.0×10.0 | **1 / 288** | **T / F** |
| `mix-a` | 12.1 | 94 260.5 | 75 302.0 | 138.00×213.00×8.00 | 125.0×200.0×8.0 | 1 / 1 | T / T |
| `mix-b` | 10.4 | 141 298.9 | 121 783.2 | 255.60×165.60×6.00 | 240.0×150.0×6.0 | **1 / 76** | **T / F** |
| `x_cells-min` | 1.1 | 11 855.7 | 5 793.7 | 38.00×113.00×6.40 | 25.0×100.0×6.4 | 1 / 1 | T / T |
| `x_cells-max` | 14.6 | 90 347.8 | 71 782.4 | 313.00×113.00×6.40 | 300.0×100.0×6.4 | 1 / 1 | T / T |
| `y_cells-min` | 1.5 | 11 855.7 | 5 793.7 | 113.00×38.00×6.40 | 100.0×25.0×6.4 | 1 / 1 | T / T |
| `y_cells-max` | 15.0 | 90 347.8 | 71 782.4 | 113.00×313.00×6.40 | 100.0×300.0×6.4 | 1 / 1 | T / T |
| `cell_size-min` | 6.6 | 33 262.7 | 2 765.5 | 113.00×113.00×6.40 | 80.0×80.0×6.4 | **1 / 25** | T / T |
| `cell_size-max` | 6.7 | 101 995.2 | 84 860.0 | 158.20×158.20×6.40 | 140.0×140.0×6.4 | **1 / 52** | **T / F** |
| `height-min` | 11.3 | 20 869.7 | 14 559.0 | 113.00×113.00×4.00 | 100.0×100.0×4.0 | 1 / 1 | T / T |
| `height-max` | 10.1 | 52 423.5 | 37 642.9 | 113.00×113.00×10.00 | 100.0×100.0×10.0 | 1 / 1 | T / T |

**16 passed, 0 failed.** Every variant is watertight and ONE body.

The **volumes and bounding boxes deliberately do not match** the baseline, and
the pack's ±2 % volume rule does not apply to this slug: under ADR-021 §4 the
form must differ, and a castellated perimeter adds both material and extent. The
comparison is carried here so the difference is visible and quantified, not
hidden. What must match — the interface — is §2.

Five entries are marked in bold because **the baseline was defective there and
this cartridge is not**: the baseline fragmented into 4, 288, 76, 25 and 52
bodies respectively, and three of those were not watertight. `SPEC.md` §5 asks
for this to be fixed rather than reproduced. It is fixed: one watertight body at
every point of the declared parameter range.

## 2. The interface — must match (±0.05 mm)

Measured on one representative bore of each class per variant, over 20 z-slices,
by the pack's own method (see the docstring in `verify_cleanroom.py` for why the
band is identified before it is measured).

| Variant | Primary major Ø | Primary minor Ø | Secondary major Ø | Secondary minor Ø | Thickness |
| :-- | --: | --: | --: | --: | --: |
| nominal | **22.54** | **20.15** | **6.95** | **4.48** | = `height` |
| `defaults` | 22.513 | 20.174 | 6.943 | 4.501 | 6.40 |
| `preset-small_panel` | 22.513 | 20.174 | 6.943 | 4.501 | 6.40 |
| `preset-large_wall` | 22.513 | 20.174 | 6.943 | 4.501 | 6.40 |
| `preset-tool_rack` | 22.513 | 20.174 | 6.943 | 4.501 | 6.40 |
| `corner-allmin` | 22.517 | 20.178 | — (1×1: no interior node) | — | 4.00 |
| `corner-allmax` | 22.514 | 20.175 | 6.945 | 4.501 | 10.00 |
| `mix-a` | 22.515 | 20.177 | 6.944 | 4.501 | 8.00 |
| `mix-b` | 22.516 | 20.176 | 6.943 | 4.501 | 6.00 |
| `x_cells-min` | 22.513 | 20.174 | — (1 column) | — | 6.40 |
| `x_cells-max` | 22.513 | 20.174 | 6.943 | 4.501 | 6.40 |
| `y_cells-min` | 22.513 | 20.174 | — (1 row) | — | 6.40 |
| `y_cells-max` | 22.513 | 20.174 | 6.943 | 4.501 | 6.40 |
| `cell_size-min` | 22.513 | 20.174 | 6.943 | 4.501 | 6.40 |
| `cell_size-max` | 22.513 | 20.174 | 6.943 | 4.501 | 6.40 |
| `height-min` | 22.517 | 20.178 | 6.945 | 4.501 | 4.00 |
| `height-max` | 22.514 | 20.175 | 6.945 | 4.501 | 10.00 |

Worst deviation over all 16 variants, all four diameters:

| Measurement | Worst deviation | Where | Tolerance |
| :-- | --: | :-- | --: |
| Primary major Ø | **−0.0274 mm** | `defaults` | ±0.05 |
| Primary minor Ø | **+0.0276 mm** | `corner-allmin` | ±0.05 |
| Secondary major Ø | **−0.0073 mm** | `mix-b` | ±0.05 |
| Secondary minor Ø | **+0.0210 mm** | `corner-allmax` | ±0.05 |

Grid pitch is 25.0 mm on both axes for both hole classes in every variant, and
panel thickness equals the `height` parameter exactly. Hole counts are
`x_cells × y_cells` primary and `(x_cells−1) × (y_cells−1)` secondary in every
variant — verified by probing each expected grid position for a bore wall, not
by trusting the loop bounds.

## 3. The form — must differ (ADR-021 §4)

| Feature | Baseline | Ours | Differs |
| :-- | :-- | :-- | :-- |
| Silhouette | plain rectangle, `x_cells·25 × y_cells·25` | castellated: a rounded tab at every boundary grid node stands proud of the rectangle | yes |
| BBox at defaults | 100.0 × 100.0 mm | **113.00 × 113.00 mm** (+6.5 mm per side) | yes |
| Corner treatment | octagonal chamfer, sized **from the cell module** | 45° flat of a **fixed 6.0 mm**, independent of the cell | yes |
| Rear face | none | 45° cone relief on every cell-centre bore (0.77 mm at defaults) | yes |
| Volume at defaults | 23 790.6 mm³ | 33 262.7 mm³ (+39.8 %) | yes |

The tab overhang is asserted by the harness (`form_tab_overhang > 0.1`), so a
regression that flattened the silhouette back to the baseline rectangle would
fail the run rather than pass quietly.

Why the tabs are additive and never subtractive: at the 25 mm interface pitch
the Ø22.54 bore leaves only ~1.23 mm of web to a straight edge. A silhouette
that cut *into* the rectangle would sever that web and fragment the plate — the
same failure the baseline had for other reasons. Ours only adds material, and
the tab puts solid material all round a seam connector at an edge node.

## 4. The thread is a true helix

A `revolve()` of the tooth profile produces concentric rings: dimensionally
exact, and a screw cannot enter. This cartridge extrudes the 2-D tooth with
`twist = −360 · height / pitch`, which is a helix of that pitch by construction.

Proof by 8-angle radial sampling per z-slice: bin the section vertices by angle,
take the minimum radius per bin, and track the angular centre of the
minor-diameter band as z rises. On a true helix the band rotates one full turn
per pitch; on a ring stack it never moves.

| Bore | Declared pitch | Band advance | Measured lead | Error |
| :-- | --: | --: | --: | --: |
| Primary, at (62.5, 62.5) | 2.5 mm | **+144.4 °/mm** | **2.494 mm/turn** | −0.3 % |
| Secondary, at (50.0, 50.0) | 3.0 mm | **+121.0 °/mm** | **2.975 mm/turn** | −0.8 % |
| *a revolved ring stack* | — | *0 °/mm* | *infinite* | — |

Both bores were sampled because they carry **different** pitches. Each turns at
its own declared rate, which a shared-rate artefact of the sampling could not
produce. The full per-slice tables are reproducible with:

```
<venv>/bin/python docs/verify_cleanroom.py --helix <a defaults render>.stl
```

An extract from the primary bore, showing the minor band (≈20.15) walking around
the circle as z rises while the crest (≈22.5) follows it:

```
  z(mm)      0°     45°     90°    135°    180°    225°    270°    315°
  0.134 19.732  20.146  20.146  20.146  19.732  22.482  22.482  22.482
  0.670 22.479  22.479  19.729  20.144  20.144  20.144  19.729  22.479
  1.207 19.735  22.486  22.486  20.784  19.735  20.150  20.150  19.871
  1.743 20.164  19.749  21.781  22.502  22.502  19.749  20.037  20.164
  2.280 20.187  20.187  20.187  19.771  22.527  22.527  22.527  19.771
  2.816 22.561  19.801  20.217  20.217  20.217  19.801  22.561  22.561
```

## 5. Per-parameter regression

Two renders per manifest parameter, compared on **geometry** — volume, bounding
box and body count — never on bytes. Two STLs can differ byte-wise from facet
ordering alone, and could in principle be identical while the geometry moved; a
byte comparison proves neither direction.

| Parameter | Low → high | Expect | Volume low → high | BBox low → high | Result |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `x_cells` | 2 → 7 | differ | 18 991.4 → 54 669.6 | 63×113×6.4 → 188×113×6.4 | PASS |
| `y_cells` | 2 → 7 | differ | 18 991.4 → 54 669.6 | 113×63×6.4 → 113×188×6.4 | PASS |
| `height` | 4.4 → 9.2 | differ | 22 942.1 → 48 153.8 | ×4.4 → ×9.2 | PASS |
| `fn` | 16 → 40 | differ | 33 373.1 → 33 208.3 | unchanged (tessellation only) | PASS |
| `cell_size` | 20 → 25 | **identical** | 33 262.7 → 33 262.7 | unchanged | PASS |
| `cell_size` | 25 → 32 | differ | 33 262.7 → 78 969.8 | 113×113 → 144.64×144.64 | PASS |

**6 passed, 0 failed.** Every render was watertight and one body.

`cell_size` is asserted in **both** directions on purpose. Below 25 mm the value
is clamped at the geometric floor, so 20 and 25 *must* produce identical
geometry — that is the fix, and a test that only demanded difference would call
the fix a bug. Above 25 mm the bores genuinely move apart, so 25 vs 32 must
differ. `fn` correctly changes the mesh without moving the nominal dimensions.

## 6. Tessellation: the choice and the study

Two knobs, doing different jobs:

- **NSEG** — facets per turn of the 2-D tooth profile. Sets **radial** accuracy.
- **SLPT** — extrusion layers per turn of the helix. Sets **axial** fidelity.

### Cost, at the 4 × 4 default

| NSEG | SLPT | Wall time | STL size |
| --: | --: | --: | --: |
| 16 | 16 | 2.0 s | 15.84 MB |
| 24 | 16 | 2.0 s | 17.46 MB |
| 32 | 16 | 2.2 s | 18.65 MB |
| 48 | 16 | 3.1 s | 24.86 MB |
| 24 | 24 | 2.9 s | 25.90 MB |
| 32 | 24 | 3.0 s | 27.62 MB |
| **32** | **32** | **4.1 s** | **36.27 MB** |
| 48 | 24 | 4.2 s | 36.85 MB |
| 16 | 48 | 3.7 s | 45.47 MB |
| 32 | 48 | 4.8 s | 53.42 MB |
| 32 | 64 | 8.0 s | 70.52 MB |
| 48 | 48 | 8.0 s | 71.48 MB |
| 16 | 96 | 7.7 s | 89.99 MB |

Mesh size tracks **SLPT**, not NSEG. At SLPT 16, tripling NSEG (16 → 48) costs
15.8 → 24.9 MB; at NSEG 48, tripling SLPT (16 → 48) costs 24.9 → 71.5 MB. Every
layer duplicates the whole profile ring, so layers are the expensive axis.

### Accuracy, same renders

Deviation from nominal, in mm.

| NSEG | SLPT | Primary major | Primary minor | Secondary major | Secondary minor |
| --: | --: | --: | --: | --: | --: |
| 16 | 16 | −0.165 | +0.260 | −0.033 | +0.122 |
| 24 | 24 | −0.062 | +0.116 | −0.012 | +0.055 |
| 32 | 24 | −0.094 | +0.087 | −0.023 | +0.046 |
| 32 | 32 (uncorrected) | −0.020 | +0.079 | −0.007 | +0.032 |
| 48 | 24 | −0.119 | +0.139 | −0.031 | +0.028 |
| 48 | 48 | −0.012 | +0.034 | −0.002 | +0.012 |

Accuracy also tracks SLPT: NSEG alone buys almost nothing (48/16 is *worse* than
24/24 on the primary minor). So the two must rise together — but the naive way
to hit ±0.05 mm on all four diameters was NSEG = SLPT = 48, and that costs
71.5 MB at the default tile and **1.1 GB at the max-range corner**, large enough
to stall a mesh reader. That is where the previous attempt was left.

### The root-band correction, and why 32/32 is enough

The primary minor was the binding measurement. Dumping the raw per-slice root
radii showed why: the root reads as a **band**, not a line — at 32/32 it spans
19.78–20.55 mm within a single slice. The question is where in that band the
build radius should put the nominal.

A horizontal cut through the root crosses the twist between two extrusion
layers, so the band's inner extreme sits a further `cos(tps/2)` inside the build
radius. The previous code compensated by that **full** factor, which puts the
band's *floor* on nominal and therefore leaves the band's centre — what a mating
screw bears on, and what the measurement reports — reading wide.

Measured, at NSEG = SLPT = 32, primary minor:

| Root compensation | Deviation |
| :-- | --: |
| full `cos(tps/2)` (previous) | +0.079 mm |
| **`sqrt(cos(tps/2))`** | **+0.031 mm** |
| none | −0.018 mm |

The geometric mean of the two extremes centres the band. That is what the 0.5
exponent is — the midpoint of a band whose two ends are both known in closed
form, not a factor fitted to a measurement. With it, **32/32 meets ±0.05 mm on
all four diameters** at less than half the mesh of 48/48.

### The chosen operating point

`NSEG = 32`, `SLPT = NSEG`, root exponent 0.5, when `fn = 0`.

| Case | Wall time | STL | Watertight | Bodies | Budget |
| :-- | --: | --: | :-- | --: | :-- |
| Default 4 × 4 | **2.8 s** | **36.9 MB** | yes | 1 | < 40 MB, < 60 s ✅ |
| Max-range corner 12 × 12 × 10 mm | **39.8 s** | 570 MB | yes | 1 | < 150 s ✅ |

Both budgets in the lane brief are met, so **no additional cell-count constraint
was needed on those grounds**. `project.json` nevertheless carries a
`severity: error` constraint at `x_cells * y_cells <= 120` — the declared 12 × 12
maximum is 144 cells, and the corner mesh, while it renders in 39.8 s, is 570 MB
to hand downstream. The constraint keeps the platform inside a mesh size it can
serve, and it is stated in en/es in the manifest. `fn` remains exposed 0–64 for a
maker who wants a finer thread and will pay for it.

The 12 × 12 corner mesh was confirmed loadable: trimesh reads and processes the
570 MB result in 42.5 s to one watertight body.

## 7. Two discrepancies in the baseline pack

Both resolved in favour of `MEASUREMENTS.json`, which is the measured record;
`SPEC.md`'s prose disagrees with it in two places.

**(a) Secondary hole count.** `SPEC.md` §2 says secondary holes are
`(x_cells+1) × (y_cells+1)` — 25 at the 4 × 4 default. `MEASUREMENTS.json`'s
`hole_count_small_default` records **9**, measured, and describes it as "distinct
small-hole grid positions at defaults". Nine is `(4−1) × (4−1)`: the **interior**
intersections only. The measurement is the record of what was actually rendered,
so this cartridge places secondary bores at interior intersections,
`(x_cells−1) × (y_cells−1)`. This also agrees with the geometry: a bore centred
on a boundary node would be half off the plate.

The consequence is visible in §1 — `corner-allmin` (1 × 1) and the
`x_cells-min` / `y_cells-min` variants have **no** secondary bores at all, which
is correct: a single row or column has no interior intersection.

**(b) Thread nominals.** `SPEC.md` §4 gives the primary major as 22.5 and the
secondary major as 7.025. `MEASUREMENTS.json` records **22.537** and **6.948**
from the meshes. The §4 numbers are round nominals; the measured values are what
a mating accessory was actually cut against. This cartridge targets the measured
values (22.54 / 20.15 and 6.95 / 4.48), which is also what `SPEC.md` §2's own
table states — §2 and §4 disagree with each other, and §2 agrees with the
measurements.

Had the pack's §4 nominals been used instead, the secondary major would sit
0.077 mm from the measured standard — outside the ±0.05 mm interface tolerance.

## 8. Why not CadQuery

The commons doctrine is CadQuery-first, and this mode is not. The reason is
measured, not stylistic:

- A B-Rep boolean of true helical thread solids against the plate took **376 s
  at the default 4 × 4 tile** — against 2.8 s here.
- It did not merely render slowly: the result was **fragmented**, not one solid.

The manifest contract for this slug declares `engine: openscad` with mode `tile`
→ `scad_file: tile.scad`, so OpenSCAD is also the engine the contract asks for.
There is no `main.py` in this cartridge. Under Manifold, the same true helices
cut cleanly in seconds and yield one watertight body at every point of the
declared parameter range.

## 9. Manifest conformance

`y4d-spec check ./multiboard -v` → `cartridges=1 failures=0 notes=0`.

That is the **manifest** bar. It reports `geometry=NOT verified (pass --render)`;
`--render` was **not** used, because this cartridge's geometry is verified far
more strictly by the harness above — 16 variants against measured interface
dimensions, hole counts, helix lead and form difference, which `--render` does
not check.

The manifest was also diffed field-by-field against the pack's `CONTRACT.json`:
slug, mode ids, `scad_file`, mode labels, parts, part `render_mode`, every
parameter's id / type / default / min / max / step / group / visibility level /
visible-in-modes / label, all three presets' ids / values / labels, camera views,
parameter groups, export formats and estimate constants **all match exactly**.

Four differences are intentional and required by ADR-021:

| Field | Contract | This cartridge | Why |
| :-- | :-- | :-- | :-- |
| `project.engine` | absent | `openscad` | the platform requires it declared; §8 |
| `hyperobject.commons_license` | `CC-BY-NC-SA-4.0` | `CERN-OHL-W-2.0` | the commons licence; the point of the re-creation |
| `project.attribution` | Keep Making, CC-BY-NC-SA | Innovaciones MADFAM, CERN-OHL-W-2.0, lineage = the interface standard | ADR-021 §3(d) |
| `constraints` | 1 (warning) | 3 (that warning + two `severity: error`) | the cell-count budget and the `cell_size` floor; §6 and the defect fix |

## 10. Reproducing this

```
cd <cartridge>
<yantra4d venv>/bin/python docs/verify_cleanroom.py --out /tmp/renders --json /tmp/results.json
<yantra4d venv>/bin/python docs/verify_cleanroom.py --helix /tmp/renders/tile__tile__defaults.stl
```

The harness reads `VARIANTS.json` and `MEASUREMENTS.json` from the private
baseline pack, which is not part of this public repository; point `PACK` in
`verify_cleanroom.py` at a copy if it has moved. Renders are sequential and the
whole run takes about 3.5 minutes. The 12 × 12 corner render alone is 570 MB —
delete the render directory afterwards.
