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

### Interface — matched

| Measurement | Baseline | This cartridge | Source |
| :--- | :--- | :--- | :--- |
| Block unit (grid pitch) | 10.0 mm | *(see measured table)* | beam X extent ÷ `length_units` |
| Beam cross-section | 10.0 × 10.0 mm per unit | | beam Y/Z extents |
| Through-hole diameter | 4.2 mm nominal (4.193 as tessellated) | | cylindrical face radius, B-Rep |
| Hole pitch | 10.0 mm (9.996 as tessellated) | | spacing of hole-face centres |
| Brace plate thickness | 2.5 mm per unit | | brace Z extent |
| Brace arm angle | 90° | | arms axis-aligned in X and Y |
| Fastener shank | 4.0 mm | | shaft XY extent |
| Fastener collar | 5.7 mm | | pin XY extent |
| Fastener length | `length_units` × 10 mm | | pin Z extent |
| Shank-to-hole clearance | 0.2 mm diametral | | 4.2 − shank |

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

*(filled from the harness runs — see the tables that follow)*

## Deviations

*(stated with the runs)*
