# Clean-room verification — `polydice`

Re-created under ADR-021 §3 from the recorded baseline pack, without access to the
removed cartridge, its satellite repository or its upstream. This document records how
the result was proved, what the pack got wrong, where the kernel forced a departure, and
what the verification harness itself got wrong.

## Summary

| Gate | Result |
| :-- | :-- |
| `y4d-spec check ./polydice --render -v` | **green** — `cartridges=1 failures=0 notes=0 geometry=verified renders=20 presets=15 skipped=0`; every render watertight, one body |
| `pytest polydice/tests` | **green** — `14 passed, 9 warnings in 6922.90s (1:55:22)`; all five modes distinct, all seven parameters change the mesh, numbering rule holds |
| 80-variant sweep against `VARIANTS.json` | **80/80 PASS** — watertight, one body, dimensions within ±0.05 mm of the ideal solid |

## What was verified against

**Not the recorded meshes.** The baseline is inert: all 80 of its renders are one
byte-identical mesh containing fourteen dice on a 30 mm grid (pack `SPEC.md` §5). It
fixes the contract and the nominal sizes and nothing else.

Acceptance is therefore stated against the **ideal Platonic solids**, computed from
their closed forms at the requested size. For a regular polyhedron those forms are
exact, so "within tolerance of the standard" is a stronger claim than "within tolerance
of a reference mesh" would have been.

Every variant in the pack's `VARIANTS.json` is rendered through the platform's own
runner contract — the restricted-builtins sandbox from `packages/commons-sandbox`
(`build_sandbox_builtins`), with `cq` and `math` injected, manifest parameters injected
as bare globals, `target_part` naming the part and `result` read back — and measured
with trimesh (`process=True`), the same normalisation the baseline pack used on its own
meshes.

Checked per variant:

- watertight;
- exactly one body, no negative- or zero-volume body;
- face-to-face, edge length and circumradius within **±0.05 mm** of the standard values
  for that solid at that `die_size`;
- inradius spread across the die's faces within ±0.05 mm (regularity);
- engraved material removed within the 0–6 % band (the pack predicts 1–3 % at default
  depth and glyph size);
- opposite faces summing to `faces + 1` for the d6, d8, d12 and d20.

Variants that request rounding are judged differently where rounding legitimately
changes a measure: a rounded die's circumradius must not *exceed* the ideal, and its
face-to-face and edge are reported but not failed, because clipping corners back to a
sphere shortens the edges by design. Those rows are marked ⚠.

## Sizing semantics

| Mode | `die_size` means | At the default 20 mm |
| :-- | :-- | :-- |
| `d6`, `d8`, `d12`, `d20` | face-to-face (twice the inradius) | 20 mm across the flats |
| `d4` | apex-to-base height | a tetrahedron 20 mm tall |

The d4 differs because the pack's measurements require it; the arithmetic is in
discrepancy 1 below.

## Discrepancies found in the baseline pack

Two genuine, plus one withdrawn. They are in the pack's derived and labelled
figures, not in its raw measurements — the measurements are sound and are what settles
each case.

### Root cause: `<die>_size_face_to_face` records a z-extent, not a face-to-face

Every one of those entries is `measured_from: "z extent of the <die> body decomposed
from the baseline mesh"`. A z-extent equals the face-to-face distance only when the die
happens to sit face-down. For one of the five — the d4 — it does not, and the label is
then wrong.

The test is independent of any nominal: for a regular solid the ratio
circumradius / inradius is a fixed constant, so comparing the *measured* circumradius
against half the recorded z-extent says immediately whether that z-extent is a
face-to-face.

| Die | measured circumradius | z-extent | circ ÷ (z/2) | ideal circ ÷ inradius | z-extent is f2f? | true f2f |
| :-- | --: | --: | --: | --: | :-- | --: |
| `d4` | 15.013 | 20.0 | 1.5013 | 3.0000 | **no** — z is the apex-to-base height | 10.009 |
| `d6` | 13.004 | 15.0 | 1.7339 | 1.7321 | yes | 15.016 |
| `d8` | 13.004 | 15.0 | 1.7339 | 1.7321 | yes | 15.016 |
| `d12` | 11.339 | 18.0 | 1.2599 | 1.2584 | yes | 18.021 |
| `d20` | 12.596 | 20.0 | 1.2596 | 1.2584 | yes | 20.019 |

The d6, d8, d12 and d20 all agree with their nominals to about 0.02 mm and need no
comment. Only the d4 does not, and it is discrepancy 1 below. (An earlier revision of
this document read the d12 row against a wrong dodecahedron constant and reported it as
a second discrepancy; that is withdrawn in §2.)

### 1. The d4's `die_size` is a height, not a face-to-face

`SPEC.md` §2 states the d4 nominal as 20 mm face-to-face. The measured circumradius of
15.013 mm rules that out: for a regular tetrahedron the circumradius is three times the
inradius, so a 20 mm face-to-face d4 would measure 30 mm to a vertex, twice what was
recorded. Read as an apex-to-base height the same 20 mm gives a circumradius of exactly
**15.000 mm**, matching the measurement to 0.013 mm. The recorded bounding box,
23.66 × 23.66 × **20.000**, says the same thing: the 20 is the height.

The cartridge therefore treats `die_size` as the **apex-to-base height for the d4** and
as face-to-face for the other four. This is also the sane choice for a set: a d4 quoted
face-to-face at 20 mm would be a 40 mm-tall object, twice the size of the d20 beside it.
The parameter's label and tooltip state which measure applies.

### 2. Withdrawn — the d12's 18 mm nominal is correct

An earlier revision of this document claimed the d12's 18 mm nominal was a vertex-up
z-extent implying a true face-to-face of ≈13.997 mm, and `docs/README.md` was changed to
match. **That claim was wrong and is withdrawn.** It rested on the same bad dodecahedron
inradius constant as harness defect H1 below: compared against the erroneous ratio
1.6202, the pack's measured 1.2599 looked like a mismatch; compared against the true
dodecahedron ratio of **1.2584**, it agrees.

The pack's d12 entry is self-consistent at 18 mm face-to-face, and every figure in it
confirms the others:

| Pack figure | Implies | Agreement |
| :-- | --: | --: |
| z-extent 18.0 as face-to-face | circumradius 11.326 mm | measured 11.339 — within 0.013 mm |
| §4 edge 8.084 mm | face-to-face 18.003 mm | within 0.003 mm of the nominal |
| measured circumradius 11.339 mm | face-to-face 18.021 mm | within 0.021 mm of the nominal |

So the d12 needs no correction, and `docs/README.md` now states the figures the closed
forms give at a genuine 18 mm face-to-face — **edge 8.083 mm, circumradius 11.326 mm,
solid volume 4046.16 mm³** — which are also, to rounding, the pack's own. All five of the
README's derived-dimension rows were re-checked against the closed forms after this was
found; the other four were already correct.

The episode is left in the record rather than quietly deleted, because it is the same
defect as H1 and it shows the cost: one wrong constant produced a false discrepancy
report against a sound baseline *and* a wrong correction to shipped documentation. Only
the d4 (discrepancy 1) and the d8 (discrepancy 3) are genuine.

### 3. `SPEC.md` §4 — the d8 edge length

§4 gives the d8 edge as **21.213 mm** against a nominal 15 mm face-to-face. Those cannot
both hold: for a regular octahedron of edge `a` the face-to-face distance is `2a/√6`, so
an edge of 21.213 implies

    f2f = 2 × 21.213 / √6 = 17.320 mm

The figure 21.213 is `15 × √2`, the edge of an octahedron whose **circumradius** is 15 —
a different measure of the same die. The correct edge at 15 mm face-to-face is
**18.371 mm**, and the pack's own measured d8 circumradius of 13.004 mm independently
recovers an edge of 18.390 mm and a face-to-face of 15.016 mm. Here the nominal is right
and the §4 edge figure is wrong — the opposite of the d12 case.

## Parameters the baseline declared but never implemented

### `dice_gradient` had no geometry

The manifest declares it; the baseline referenced it nowhere, even nominally. Rather
than drop a declared parameter, it is given the meaning its own tooltip describes: `1`
cuts a shallow equatorial groove, so a filament change at that Z produces a clean
two-tone die. A real, visible geometric change.

### `fn` is not a facet count here

`fn` deserves the same note. It is an OpenSCAD-flavoured facet-count knob inherited from
a mesh kernel. A B-Rep kernel has no facet count and the platform calls its exporter
with the default tessellation, so a cartridge cannot route `fn` to the mesher. Leaving
it inert would reproduce exactly the defect that removed this slug's predecessor, so it
is given the meaning it can honestly carry: it widens the mouth of each engraved numeral
by a shallow second pass, so the glyph holds paint and reads at a glance.

The manifest label and tooltip, and both language halves of `docs/README.md`, were
corrected to describe that behaviour — an earlier revision of this cartridge documented
`fn` as a chamfer while the code widened the rim, which is the same class of defect
(documentation that does not match geometry) in miniature.

## Defects found in the verification harness itself

The first full sweep returned 69 PASS and 11 FAIL. Every one of the eleven was a defect
in the **harness's reference values**, not in the cartridge, and each was run to ground
rather than waived. They are recorded here because a verification harness that reports a
correct object as broken is as dangerous as one that reports a broken object as correct
— and because the next person to touch this sweep needs to know.

### H1 — the harness's ideal dodecahedron was the wrong solid

Ten of the eleven failures were d12 variants reporting the same three complaints: edge
off by −2.58 mm, circumradius off by −3.62 mm, and "engraved removal 53.65 % outside the
0–6 % band". A 53 % volume discrepancy is not engraving; it is a different solid.

The cartridge was not the different solid. Its `_faces_of` returns 12 pentagonal faces
from 20 vertices for the d12 — verified directly — and every measured die had
face-to-face exactly equal to the requested `die_size`.

The fault was one character class in the harness's closed form for the dodecahedron's
inradius:

| | inradius at edge 1 | circ ÷ inradius |
| :-- | --: | --: |
| harness: `(a/2)·√(5/2 + 11/(10·√5))` | 0.86486 | 1.62021 |
| correct: `a·φ² / (2√(3−φ))` | 1.11352 | **1.25841** |

`11/(10·√5)` where the closed form has `(11/10)·√5`. The inradius comes out 22 % small,
so the derived ratio 1.6202 — the correct circumradius divided by that wrong inradius —
is not a geometric constant of anything; its nearness to φ = 1.618 is coincidence. The
harness ended up demanding a solid 29 % larger in edge than the one it had asked the
cartridge to build.

Re-evaluated against the canonical constants, all sixteen d12 variants match to
**0.0000 mm on both edge and circumradius**, and engraved removal falls between 0.13 %
and 2.62 % — inside the pack's predicted band:

| Variant | edge meas / std | circumradius meas / std | engraved |
| :-- | --: | --: | --: |
| `defaults` | 8.9806 / 8.9806 | 12.5841 / 12.5841 | 1.08 % |
| `die_size-min` | 4.4903 / 4.4903 | 6.2920 / 6.2920 | 2.62 % |
| `die_size-max` | 17.9611 / 17.9611 | 25.1682 / 25.1682 | 0.13 % |
| `preset-large_d6` | 13.4708 / 13.4708 | 18.8761 / 18.8761 | 0.32 % |

That one constant did damage in two places. Besides failing ten sweep variants, it is
also the source of the withdrawn d12 discrepancy in §2 above and of the wrong
edge/circumradius figures that had been written into `docs/README.md`. A single wrong
constant produced a false failure report against sound geometry *and* a wrong correction
to shipped documentation.

The cartridge's geometry, built from exact vertex coordinates rather than from a
tabulated ratio, was right the whole time — which is the argument for building solids
from coordinates.

### H2 — the inradius spread was measured from the centre of mass

The remaining failure, `d20__d20__font_depth-max`, reported an inradius spread of
0.0571 mm against a 0.05 mm tolerance. Everything else about that render is exact:
face-to-face 20.000, edge 13.23169 matching the standard to fourteen significant
figures, circumradius matching to 4 × 10⁻⁷ mm, watertight, one body, numbering correct.

The harness measured each face's inradius as the distance from the **engraved solid's
centre of mass** to that face's plane. The numerals are asymmetric — every face carries
a different glyph, so a different volume is cut from each — and that displaces the
centre of mass. Measured on this exact variant, the displacement is 0.030 mm, which is
most of the reported spread.

The cartridge centres every solid on the geometric origin, so the origin is the correct
reference. Re-measured there, on the B-Rep, changing nothing else:

| Variant | spread from centre of mass | spread from geometric origin |
| :-- | --: | --: |
| `d12__d12__font_depth-max` | 0.04504 | **0.00000** |
| `d12__d12__font_size-max` | 0.03537 | **0.00000** |
| `d20__d20__defaults` | 0.03090 | **0.00000** |
| `d20__d20__preset-standard_d20` | 0.03090 | **0.00000** |
| `d20__d20__font_depth-max` | 0.05710 | **0.00000** |
| `d20__d20__font_size-max` | 0.03090 | **0.00000** |

Every face of every die sits at exactly the requested inradius. The dice are regular to
the precision of the kernel; the harness's reference point was not.

Reading the spread off the tessellation instead does not work, and the attempt is worth
recording: the glyph pocket **floors** are planar too and sit below the face plane, so
area-weighted triangle groups mix face and pocket and report a spread of 0.03–0.08 mm on
the same geometry the B-Rep measures as exactly zero. The B-Rep face is the thing being
measured; the mesh is a sampling of it.

### Verdict after both fixes

**80/80 PASS.** No cartridge geometry was changed to obtain this result — the renders
are the ones the sweep already produced, re-evaluated against corrected references, with
the six spread outliers re-measured from the correct origin.

## Kernel finding — OCC cannot fillet a regular tetrahedron

Filleting the d4's edges produces a solid that **passes every B-Rep check and then
tessellates as detached shells**. Measured across radii 0.5, 1.0, 1.5, 2.0 and 3.0 mm,
and at export tolerances from 0.1 down to 0.001:

- `Workplane.fillet(r)` returns without raising;
- `solids().size() == 1` and `isValid() == True` at every radius;
- the tessellation is five separate, non-watertight shells at every radius, four of them
  of exactly zero volume.

So the B-Rep-level checks a cartridge would normally trust are not sufficient here: a
die that passes them still exports torn. The acceptance question — *does this export as
one watertight body?* — has to be asked of the **tessellation**.

That is what `_tessellates_cleanly` is for: it meshes the candidate, welds coincident
vertices on a rounded grid (OCC emits a separate vertex copy per face along every shared
edge, so without welding even a perfect cube reads as six disconnected patches), and
requires every edge to be shared by exactly two triangles. `_round_body` keeps a rounding
operation only if the result passes, and otherwise falls back to clipping the body
against a sphere, which is watertight on the same shape at every depth measured.

Rounding is applied to the bare polyhedron **before** any numeral is cut. Filleting after
a text cut is the standard way to lose watertightness — the fillet engine either walks
into the glyph pockets and fails, or succeeds and leaves slivers.

### Defect found during this verification: the guard was too loose to fire

The sweep's variant `d4__d4__corner-allmax` (`die_size=40, font_depth=1.5, font_size=12,
rounding_corner=5, rounding_edge=3, dice_gradient=1` — every parameter at the top of its
declared range) **failed**: the exported mesh had five bodies, four of exactly zero
volume, and was not watertight.

Rebuilding that variant stage by stage attributes the tear precisely:

| Stage | trimesh | OCC B-Rep | `_tessellates_cleanly` |
| :-- | :-- | :-- | :-- |
| bare tetrahedron | watertight, 1 body, 13856.409 mm³ | `solids=1` | True |
| **after `_round_body`** | **not watertight, 5 bodies** `[12744.68, 0, 0, 0, 0]` | `solids=1` | **True** |
| after engraving | inherits the torn body | | |

The tear is created by the rounding, before a single glyph is cut, and the designed
fallback never ran — because it is gated on `_tessellates_cleanly`, which returned True
on the torn body.

The cause was the guard's tolerance. It accepted a proportional number of non-manifold
edges (`bad <= max(2, len(edges) // 500)`) rather than requiring zero. That allowance
had been introduced to stop the guard rejecting a sphere-clipped tetrahedron that
trimesh confirms is watertight — a real false positive — but on a 24 772-triangle mesh
it tolerates up to 49 bad edges, and the actual tear is four *zero-volume sliver* shells,
which contribute very few bad edges while still making the export non-watertight. Fixing
a false positive had bought a false negative, and the cartridge would have shipped a torn
die while reporting success.

That inverts the guard's whole purpose, so it was fixed rather than merely documented.
The guard now requires **every** edge to be shared by exactly two triangles, with no
tolerance. Measured against trimesh on six bodies spanning both failure modes:

| Body | bad edges | old rule | strict rule | trimesh |
| :-- | --: | :-- | :-- | :-- |
| bare tetrahedron, 40 mm | 0 | accept | accept ✓ | watertight, 1 body |
| `fillet(3.0)` on that tetrahedron | 4 (all shared by >2) | **accept ✗** | reject ✓ | **torn, 5 bodies** |
| `_round_body(corner 5, edge 3)` | 4 (all shared by >2) | **accept ✗** | reject ✓ | **torn, 5 bodies** |
| sphere-clip, edge path | 0 | accept | accept ✓ | watertight, 1 body |
| sphere-clip, corner path | 0 | accept | accept ✓ | watertight, 1 body |
| sphere-clip 20 mm, corner 2 | 0 | accept | accept ✓ | watertight, 1 body |

Zero false positives and zero false negatives. Note the last row: that is the exact body
whose rejection motivated the allowance in the first place, and it passes the strict rule
cleanly. The allowance was never needed — the original false positive came from dropping
degenerate triangles wholesale, which orphaned their neighbours' edges, and skipping only
zero-*length* edges fixes it with no tolerance at all.

With the guard firing correctly the existing fallback engages as designed:

| Variant | before the fix | after the fix |
| :-- | :-- | :-- |
| `d4__d4__corner-allmax` | not watertight, 5 bodies, 4 of zero volume | **watertight, 1 body**, 13687.974 mm³ |
| `d4__d4__defaults` | watertight, 1715.135 mm³ | unchanged, 1715.135 mm³ |
| `d4__d4__preset-large_d6` | watertight | unchanged, 5804.598 mm³ |
| `d4__d4__mix-a` | watertight | unchanged, 1682.716 mm³ |

The unrounded and mildly-rounded variants are bit-for-bit unchanged, as expected: the
strict rule only alters behaviour where bad edges exist.

### What the fallback costs, stated plainly

The fallback eases the d4 **less** than the requested fillet would have. On a d4 at
`die_size` 40 with `rounding_edge` 3, the (torn) fillet removed 8.02 % of the ideal
volume; the sphere-clip fallback removes 1.22 %. The clip radius is capped at 0.6 of the
circumradius-to-inradius gap, and a tetrahedron's vertices sit far outside its faces, so
the sphere only clips the corners back rather than blending the edges.

A d4 therefore takes visibly less rounding than the other four solids at the same
setting. That is a real limitation of this cartridge and it is recorded here rather than
hidden: a watertight, slightly sharper die is usable and a torn one is not.

## Cost of the tessellation guard

The guard is not free, and the cost is worth recording for whoever maintains this next.
Measured on a d4 at defaults, single process:

| | |
| :-- | --: |
| total build | 341.9 s |
| in `_tessellates_cleanly` | 300.1 s (**87.8 %**) |
| calls | 12 (one per glyph) |
| per-glyph cost, first → last | 18.6 s → 67.2 s |

The cost grows through the build because each call re-meshes the whole accumulating body.
It buys the one thing B-Rep checks cannot give — proof the export is not torn — so it
stays, but a future pass could hoist it out of the per-glyph loop if the per-glyph
rejection is shown never to fire.

## Deviations from the recorded baseline, in one list

Every one is deliberate and each is argued above.

| # | Deviation | Why |
| :-- | :-- | :-- |
| 1 | All five modes produce five different dice; all seven parameters change the mesh | The baseline was inert — one mesh for all 80 renders. This is the defect that removed the slug, not a behaviour to preserve (`SPEC.md` §5) |
| 2 | `die_size` is the apex-to-base **height** for the d4, face-to-face for the rest | The pack's own measured d4 circumradius (15.013 mm) and bounding box (z = 20.000) both say the recorded 20 mm is a height. Discrepancy 1 |
| 3 | `rounding_corner` is millimetres, not a percentage of the circumscribed diameter | `SPEC.md` §3 flags the units mismatch and instructs the re-implementer to pick one meaning and state it. Millimetres matches the manifest's 0–5 range and `rounding_edge` |
| 4 | `dice_gradient` cuts an equatorial groove | Declared in the manifest with no geometry behind it. `SPEC.md` §3: "drop it, or give it a meaning and implement it" |
| 5 | `fn` widens the engraved numerals' mouths instead of setting a facet count | A B-Rep kernel has no facet count and the exporter is called with the default tessellation. An inert declared parameter is the defect that removed the predecessor |
| 6 | The d4 rounds less than the other solids at the same setting | OCC tears a filleted tetrahedron at every radius measured; the watertight fallback is a milder easing. Stated in full above |
| 7 | One body per render, not fourteen | The baseline emitted every die type at once on a 30 mm grid. `SPEC.md` §4 names one body as the target and fourteen as the defect |

## Reproducing this

The sweep harness, the guard-threshold probe and the spread re-measurement are working
files of the verification, not cartridge code, and they live in the private record
alongside the baseline pack rather than in the commons:

| Script | What it does |
| :-- | :-- |
| `c1b_sweep.py` | renders all 80 `VARIANTS.json` variants through the sandbox contract and measures each with trimesh |
| `c1b_threshold.py` | the six-body false-positive / false-negative table for the tessellation guard |
| `c1b_verify_fix.py` | re-renders the four d4 variants across the guard fix |
| `c1c_spreads.py` | re-measures inradius spread from the geometric origin (harness defect H2) |
| `c1c_reeval.py` | re-evaluates the 80 recorded renders against corrected references (H1 + H2) |

The two gates that a reviewer can run directly, from the repository root:

```
PYTHONPATH=<yantra4d venv site-packages> \
  y4d-spec check ./polydice --render -v

<yantra4d venv>/bin/python -m pytest polydice/tests -q
```

The test suite is the standing regression: it asserts that the five modes produce five
different meshes and that each of the seven parameters changes the mesh. `SPEC.md` §5
asked for exactly this — "had one existed, this would never have shipped."

**Budget for it.** Fourteen tests, most of which render a d20 twice, and every render
pays the tessellation guard's per-glyph cost (measured above at 87.8 % of build time).
On an unloaded machine the suite takes on the order of an hour; on a machine sharing CPU
with other work it takes several. A first attempt here was killed by a one-hour `timeout`
at 8 of 14 tests — the cap, not the suite, was wrong. Give it hours, not minutes, and do
not read a timeout as a failure."

## Per-variant results

All 80 variants of `VARIANTS.json`, measured after both harness defects were corrected.
`std` columns are the exact ideal solid at that variant's `die_size`. Rows marked ⚠
request rounding, which legitimately shortens edges and reduces the circumradius; for
those the circumradius is checked only for not *exceeding* the ideal, and edge and
face-to-face are reported rather than enforced.

One gap in the pack's own coverage is worth naming: **every one of its 80 variants sets
`fn = 0`**, so this sweep never exercises that parameter. `fn` is proved to change the
mesh only by `tests/test_parameters_take_effect.py`, which renders a d20 at `fn` 0 and 64
and compares the exported meshes. A pack that perturbs six of the seven parameters cannot
by itself establish that the seventh is not inert — which is the defect that removed this
slug — so the regression test, not this table, is the evidence for `fn`.

Seven of the eighty renders share a mesh with another row. Both causes are correct
behaviour, and neither weakens the "every mode and every parameter changes the mesh"
claim:

- **Five**: `preset-standard_d20` declares `die_size 20, font_depth 0.6, font_size 6,
  rounding 0/0` — which *is* the parameter set's defaults. A preset that restates the
  defaults must produce the default mesh.
- **Two**: `font_size-max` (12 mm) on the d4 and d20. Those two solids have the smallest
  faces in the set, so a 12 mm numeral is clamped to the face's inscribed radius, landing
  on the same glyph height the default 6 mm already produced. The clamp is the documented
  behaviour that keeps a large numeral from cutting a small die apart.

The regression suite exercises `font_size` at 3 versus 9, both below the d20's clamp, so
parameter sensitivity is proved on values where the parameter is free to act. Across the
five modes at identical parameters the meshes are five distinct hashes, which is the
acceptance test the baseline failed.

| Variant | Mode | Watertight | Bodies | Edge (meas / std) | F2F (meas / std) | Circumradius (meas / std) | Engraved | Result |
| :-- | :-- | :-: | --: | --: | --: | --: | --: | :-: |
| `defaults` | `d4` | yes | 1 | 24.495 / 24.495 | 10.000 / 10.000 | 15.000 / 15.000 | 0.98 % | PASS |
| `preset-standard_d20` | `d4` | yes | 1 | 24.495 / 24.495 | 10.000 / 10.000 | 15.000 / 15.000 | 0.98 % | PASS |
| `preset-large_d6` | `d4` | yes | 1 | 31.718 / 36.742 | 15.000 / 15.000 | 20.500 / 22.500 | 0.70 % | PASS ⚠ |
| `preset-mini_d8` | `d4` | yes | 1 | 14.697 / 14.697 | 6.000 / 6.000 | 9.000 / 9.000 | 1.47 % | PASS |
| `corner-allmin` | `d4` | yes | 1 | 12.247 / 12.247 | 5.000 / 5.000 | 7.500 / 7.500 | 0.73 % | PASS |
| `corner-allmax` | `d4` | yes | 1 | 36.056 / 48.990 | 20.000 / 20.000 | 25.000 / 30.000 | 1.22 % | PASS ⚠ |
| `mix-a` | `d4` | yes | 1 | 15.133 / 24.495 | 10.000 / 10.000 | 11.500 / 15.000 | 2.85 % | PASS ⚠ |
| `mix-b` | `d4` | yes | 1 | 31.718 / 36.742 | 15.000 / 15.000 | 20.500 / 22.500 | 0.49 % | PASS ⚠ |
| `die_size-min` | `d4` | yes | 1 | 12.247 / 12.247 | 5.000 / 5.000 | 7.500 / 7.500 | 1.71 % | PASS |
| `die_size-max` | `d4` | yes | 1 | 48.990 / 48.990 | 20.000 / 20.000 | 30.000 / 30.000 | 0.33 % | PASS |
| `font_depth-min` | `d4` | yes | 1 | 24.495 / 24.495 | 10.000 / 10.000 | 15.000 / 15.000 | 0.48 % | PASS |
| `font_depth-max` | `d4` | yes | 1 | 24.495 / 24.495 | 10.000 / 10.000 | 15.000 / 15.000 | 2.08 % | PASS |
| `font_size-min` | `d4` | yes | 1 | 24.495 / 24.495 | 10.000 / 10.000 | 15.000 / 15.000 | 0.55 % | PASS |
| `font_size-max` | `d4` | yes | 1 | 24.495 / 24.495 | 10.000 / 10.000 | 15.000 / 15.000 | 0.98 % | PASS |
| `rounding_corner-max` | `d4` | yes | 1 | 10.000 / 24.495 | 10.000 / 10.000 | 10.000 / 15.000 | 7.36 % | PASS ⚠ |
| `rounding_edge-max` | `d4` | yes | 1 | 16.613 / 24.495 | 10.000 / 10.000 | 12.000 / 15.000 | 1.72 % | PASS ⚠ |
| `defaults` | `d6` | yes | 1 | 20.000 / 20.000 | 20.000 / 20.000 | 17.321 / 17.321 | 0.31 % | PASS |
| `preset-standard_d20` | `d6` | yes | 1 | 20.000 / 20.000 | 20.000 / 20.000 | 17.321 / 17.321 | 0.31 % | PASS |
| `preset-large_d6` | `d6` | yes | 1 | 22.368 / 30.000 | 30.000 / 30.000 | 23.981 / 25.981 | 0.31 % | PASS ⚠ |
| `preset-mini_d8` | `d6` | yes | 1 | 12.000 / 12.000 | 12.000 / 12.000 | 10.392 / 10.392 | 0.57 % | PASS |
| `corner-allmin` | `d6` | yes | 1 | 10.000 / 10.000 | 10.000 / 10.000 | 8.660 / 8.660 | 0.24 % | PASS |
| `corner-allmax` | `d6` | yes | 1 | 17.730 / 40.000 | 40.000 / 40.000 | 29.641 / 34.641 | 1.95 % | PASS ⚠ |
| `mix-a` | `d6` | yes | 1 | 4.312 / 20.000 | 20.000 / 20.000 | 13.821 / 17.321 | 5.45 % | PASS ⚠ |
| `mix-b` | `d6` | yes | 1 | 22.368 / 30.000 | 30.000 / 30.000 | 23.981 / 25.981 | 0.46 % | PASS ⚠ |
| `die_size-min` | `d6` | yes | 1 | 10.000 / 10.000 | 10.000 / 10.000 | 8.660 / 8.660 | 2.25 % | PASS |
| `die_size-max` | `d6` | yes | 1 | 40.000 / 40.000 | 40.000 / 40.000 | 34.641 / 34.641 | 0.04 % | PASS |
| `font_depth-min` | `d6` | yes | 1 | 20.000 / 20.000 | 20.000 / 20.000 | 17.321 / 17.321 | 0.17 % | PASS |
| `font_depth-max` | `d6` | yes | 1 | 20.000 / 20.000 | 20.000 / 20.000 | 17.321 / 17.321 | 0.62 % | PASS |
| `font_size-min` | `d6` | yes | 1 | 20.000 / 20.000 | 20.000 / 20.000 | 17.321 / 17.321 | 0.06 % | PASS |
| `font_size-max` | `d6` | yes | 1 | 20.000 / 20.000 | 20.000 / 20.000 | 17.321 / 17.321 | 1.49 % | PASS |
| `rounding_corner-max` | `d6` | yes | 1 | 4.312 / 20.000 | 20.000 / 20.000 | 12.321 / 17.321 | 17.11 % | PASS ⚠ |
| `rounding_edge-max` | `d6` | yes | 1 | 4.506 / 20.000 | 20.000 / 20.000 | 14.321 / 17.321 | 3.20 % | PASS ⚠ |
| `defaults` | `d8` | yes | 1 | 24.495 / 24.495 | 20.000 / 20.000 | 17.321 / 17.321 | 0.50 % | PASS |
| `preset-standard_d20` | `d8` | yes | 1 | 24.495 / 24.495 | 20.000 / 20.000 | 17.321 / 17.321 | 0.50 % | PASS |
| `preset-large_d6` | `d8` | yes | 1 | 36.742 / 36.742 | 30.000 / 30.000 | 25.981 / 25.981 | 0.15 % | PASS ⚠ |
| `preset-mini_d8` | `d8` | yes | 1 | 14.697 / 14.697 | 12.000 / 12.000 | 10.392 / 10.392 | 0.91 % | PASS |
| `corner-allmin` | `d8` | yes | 1 | 12.247 / 12.247 | 10.000 / 10.000 | 8.660 / 8.660 | 0.39 % | PASS |
| `corner-allmax` | `d8` | yes | 1 | 41.641 / 48.990 | 40.000 / 40.000 | 32.419 / 34.641 | 1.26 % | PASS ⚠ |
| `mix-a` | `d8` | yes | 1 | 22.045 / 24.495 | 20.000 / 20.000 | 16.580 / 17.321 | 0.90 % | PASS ⚠ |
| `mix-b` | `d8` | yes | 1 | 31.843 / 36.742 | 30.000 / 30.000 | 24.500 / 25.981 | 1.08 % | PASS ⚠ |
| `die_size-min` | `d8` | yes | 1 | 12.247 / 12.247 | 10.000 / 10.000 | 8.660 / 8.660 | 1.63 % | PASS |
| `die_size-max` | `d8` | yes | 1 | 48.990 / 48.990 | 40.000 / 40.000 | 34.641 / 34.641 | 0.06 % | PASS |
| `font_depth-min` | `d8` | yes | 1 | 24.495 / 24.495 | 20.000 / 20.000 | 17.321 / 17.321 | 0.28 % | PASS |
| `font_depth-max` | `d8` | yes | 1 | 24.495 / 24.495 | 20.000 / 20.000 | 17.321 / 17.321 | 0.99 % | PASS |
| `font_size-min` | `d8` | yes | 1 | 24.495 / 24.495 | 20.000 / 20.000 | 17.321 / 17.321 | 0.10 % | PASS |
| `font_size-max` | `d8` | yes | 1 | 24.495 / 24.495 | 20.000 / 20.000 | 17.321 / 17.321 | 1.02 % | PASS |
| `rounding_corner-max` | `d8` | yes | 1 | 24.495 / 24.495 | 20.000 / 20.000 | 17.321 / 17.321 | 0.37 % | PASS ⚠ |
| `rounding_edge-max` | `d8` | yes | 1 | 17.146 / 24.495 | 20.000 / 20.000 | 15.099 / 17.321 | 3.81 % | PASS ⚠ |
| `defaults` | `d12` | yes | 1 | 8.981 / 8.981 | 20.000 / 20.000 | 12.584 / 12.584 | 1.08 % | PASS |
| `preset-standard_d20` | `d12` | yes | 1 | 8.981 / 8.981 | 20.000 / 20.000 | 12.584 / 12.584 | 1.08 % | PASS |
| `preset-large_d6` | `d12` | yes | 1 | 13.471 / 13.471 | 30.000 / 30.000 | 18.876 / 18.876 | 0.32 % | PASS ⚠ |
| `preset-mini_d8` | `d12` | yes | 1 | 5.388 / 5.388 | 12.000 / 12.000 | 7.550 / 7.550 | 1.97 % | PASS |
| `corner-allmin` | `d12` | yes | 1 | 4.490 / 4.490 | 10.000 / 10.000 | 6.292 / 6.292 | 0.84 % | PASS |
| `corner-allmax` | `d12` | yes | 1 | 17.961 / 17.961 | 40.000 / 40.000 | 25.168 / 25.168 | 0.49 % | PASS ⚠ |
| `mix-a` | `d12` | yes | 1 | 8.981 / 8.981 | 20.000 / 20.000 | 12.584 / 12.584 | 0.68 % | PASS ⚠ |
| `mix-b` | `d12` | yes | 1 | 13.471 / 13.471 | 30.000 / 30.000 | 18.876 / 18.876 | 0.54 % | PASS ⚠ |
| `die_size-min` | `d12` | yes | 1 | 4.490 / 4.490 | 10.000 / 10.000 | 6.292 / 6.292 | 2.62 % | PASS |
| `die_size-max` | `d12` | yes | 1 | 17.961 / 17.961 | 40.000 / 40.000 | 25.168 / 25.168 | 0.13 % | PASS |
| `font_depth-min` | `d12` | yes | 1 | 8.981 / 8.981 | 20.000 / 20.000 | 12.584 / 12.584 | 0.60 % | PASS |
| `font_depth-max` | `d12` | yes | 1 | 8.981 / 8.981 | 20.000 / 20.000 | 12.584 / 12.584 | 2.16 % | PASS |
| `font_size-min` | `d12` | yes | 1 | 8.981 / 8.981 | 20.000 / 20.000 | 12.584 / 12.584 | 0.22 % | PASS |
| `font_size-max` | `d12` | yes | 1 | 8.981 / 8.981 | 20.000 / 20.000 | 12.584 / 12.584 | 1.61 % | PASS |
| `rounding_corner-max` | `d12` | yes | 1 | 8.981 / 8.981 | 20.000 / 20.000 | 12.584 / 12.584 | 0.48 % | PASS ⚠ |
| `rounding_edge-max` | `d12` | yes | 1 | 8.981 / 8.981 | 20.000 / 20.000 | 12.584 / 12.584 | 0.35 % | PASS ⚠ |
| `defaults` | `d20` | yes | 1 | 13.232 / 13.232 | 20.000 / 20.000 | 12.584 / 12.584 | 1.14 % | PASS |
| `preset-standard_d20` | `d20` | yes | 1 | 13.232 / 13.232 | 20.000 / 20.000 | 12.584 / 12.584 | 1.14 % | PASS |
| `preset-large_d6` | `d20` | yes | 1 | 10.388 / 19.848 | 30.000 / 30.000 | 16.876 / 18.876 | 2.02 % | PASS ⚠ |
| `preset-mini_d8` | `d20` | yes | 1 | 7.939 / 7.939 | 12.000 / 12.000 | 7.550 / 7.550 | 1.70 % | PASS |
| `corner-allmin` | `d20` | yes | 1 | 6.616 / 6.616 | 10.000 / 10.000 | 6.292 / 6.292 | 0.86 % | PASS |
| `corner-allmax` | `d20` | yes | 1 | 22.494 / 26.463 | 40.000 / 40.000 | 24.395 / 25.168 | 0.37 % | PASS ⚠ |
| `mix-a` | `d20` | yes | 1 | 11.909 / 13.232 | 20.000 / 20.000 | 12.326 / 12.584 | 0.19 % | PASS ⚠ |
| `mix-b` | `d20` | yes | 1 | 14.460 / 19.848 | 30.000 / 30.000 | 17.376 / 18.876 | 0.94 % | PASS ⚠ |
| `die_size-min` | `d20` | yes | 1 | 6.616 / 6.616 | 10.000 / 10.000 | 6.292 / 6.292 | 1.98 % | PASS |
| `die_size-max` | `d20` | yes | 1 | 26.463 / 26.463 | 40.000 / 40.000 | 25.168 / 25.168 | 0.29 % | PASS |
| `font_depth-min` | `d20` | yes | 1 | 13.232 / 13.232 | 20.000 / 20.000 | 12.584 / 12.584 | 0.58 % | PASS |
| `font_depth-max` | `d20` | yes | 1 | 13.232 / 13.232 | 20.000 / 20.000 | 12.584 / 12.584 | 2.17 % | PASS |
| `font_size-min` | `d20` | yes | 1 | 13.232 / 13.232 | 20.000 / 20.000 | 12.584 / 12.584 | 0.49 % | PASS |
| `font_size-max` | `d20` | yes | 1 | 13.232 / 13.232 | 20.000 / 20.000 | 12.584 / 12.584 | 1.14 % | PASS |
| `rounding_corner-max` | `d20` | yes | 1 | 13.232 / 13.232 | 20.000 / 20.000 | 12.584 / 12.584 | 0.09 % | PASS ⚠ |
| `rounding_edge-max` | `d20` | yes | 1 | 9.262 / 13.232 | 20.000 / 20.000 | 11.811 / 12.584 | 1.35 % | PASS ⚠ |
