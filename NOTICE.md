# NOTICE — licence carve-outs

Cartridges in this repository are licensed **CERN-OHL-W-2.0** (ADR-011,
RFC 0038 §9), and each carries its own `LICENSE`. The exceptions below are the
cases where a cartridge's own licence is **not** the whole story, because files
or dependencies from an upstream project travel under their own terms.

Each cartridge listed here also carries a `<slug>/NOTICE` with the full
attribution; this file is the index, not a replacement for it.

## Removed and re-created clean-room (operator ruling 2026-09-04, ADR-021 — all returned 2026-09-05)

The operator ruled that any hyperobject whose origin licence is not
CERN-OHL-W-2.0 leaves the commons and is re-created from scratch, clean-room,
to the same final result. Five cartridges were removed from this repository at
the 2026-09-04 commit (their history stays in git and in the archived
satellite repos); their slugs were **reserved** and each has since returned as
a clean-room implementation, verified against the recorded final result
(baseline packs of interfaces and reference meshes — never the removed source):

| Slug | Origin licence | Origin | Status |
| :-- | :-- | :-- | :-- |
| `keyv2` | GPL-3.0 | rsheldiii/KeyV2 | **returned** clean-room (#5, 2026-09-05), see below |
| `stemfie` | GPL-3.0-or-later | stemfie.org (Paulo Kiefe) | **returned** clean-room (#3, 2026-09-05) — implements the published STEMFIE grid/pin interface only |
| `multiboard` | CC-BY-NC-SA-4.0 | Multiboard (Keep Making) | **returned** interface-only (#7, 2026-09-05; ADR-021 §4: the 25 mm interface matches, the form is ours) |
| `polydice` | BSD-2-Clause | (unattributed upstream) | **returned** clean-room (#14, 2026-09-05) — five regular dice from public polyhedron mathematics |
| `rugged-box` | CC-BY-NC-SA-4.0 (vendored `RuggedBoxV1.scad` + parameter sets) | Super Customizable Rugged Box (Iceman) | **returned** interface-only (#4, 2026-09-05; ADR-021 §4: hinge/latch interfaces match, the form is ours; every parameter live) |

All five have returned (and `gridfinity`'s OpenSCAD side, re-created in our own OpenSCAD in #2, see below); the catalog is back to 500 cartridges, every one our authoring under CERN-OHL-W-2.0. Each returned cartridge carries its acceptance evidence under `<slug>/docs/`.

### `keyv2` — returned clean-room (ADR-021 §3)

`keyv2` was re-created from a recorded final-result baseline by an implementer
with no access to the removed cartridge, the archived satellite, or the upstream
project. It is MADFAM's own authoring under CERN-OHL-W-2.0 and implements
published mechanical interfaces only: the 19.05 mm keyboard key pitch and the
Cherry MX, Alps and Box Cherry stem dimensions. Its acceptance evidence, and the
one intentional divergence from the baseline (body count — the baseline's
default keycap was two disjoint solids with a free-floating stem, which cannot
be printed; the re-creation fuses the stem to the keytop), are recorded in
`keyv2/docs/CLEANROOM-VERIFICATION.md`.

## `gridfinity` — OpenSCAD side removed (ADR-021) and re-created clean-room, GPL submodule dropped

The cartridge's CadQuery modes (`bin`, `baseplate`, `main.py`) are MADFAM-authored
implementations of the published Gridfinity standard (Zack Freedman, MIT — a
specification, not code) and stay. Its three OpenSCAD modes (`cup`,
`baseplate_scad`, `lid`) descended from `gridfinity_extended_openscad` (ostat,
GPL-3.0) and its ancestor `gridfinity_openscad` (vector76, MIT) per the
cartridge's own README/NOTICE; they were removed on 2026-09-04 together with the
`gridfinity/gridfinity_extended` git submodule (no remaining file included it).
All three have since **returned** (#2, 2026-09-05) as clean-room OpenSCAD
re-creations — `cup.scad`, `baseplate.scad`, `lid.scad` and the geometry they
share in `gridfinity_std.scad` — authored from a recorded final-result baseline
and the published Gridfinity standard, without access to the removed cartridge
or to any upstream implementation. The cartridge again declares five modes
(`bin`, `baseplate` on CadQuery; `cup`, `baseplate_scad`, `lid` on OpenSCAD).
The acceptance evidence is in `gridfinity/docs/CLEANROOM-VERIFICATION.md`, and
the full provenance statement in `gridfinity/NOTICE`.

## Third-party libraries, not vendored

The `libs/*` submodules are third-party OpenSCAD libraries resolved at render
time. No source from them is distributed here; each keeps its own licence:

| Submodule | Upstream | Licence |
| :-- | :-- | :-- |
| `libs/BOSL2` | BelfrySCAD/BOSL2 | BSD-2-Clause |
| `libs/NopSCADlib` | nophead/NopSCADlib | GPL-3.0 |
| `libs/Round-Anything` | Irev-Dev/Round-Anything | MIT |
| `libs/threads-scad` | rcolyer/threads-scad | CC0-1.0 |
| `libs/MCAD` | openscad/MCAD | LGPL-2.1 |
| `libs/dotSCAD` | JustinSDK/dotSCAD | LGPL-3.0 |

Licence identifiers above are the upstreams' own; each submodule ships its
licence text in its own tree once initialised.

## Standards implemented (not licence carve-outs)

Several cartridges implement openly published standards whose reference
implementations are permissively licensed and credited in the cartridge's
`NOTICE` — Gridfinity (Zack Freedman / Voidstar Lab, MIT),
`gridfinity_openscad` (vector76, MIT), and others. Implementing a standard is
not a licence exposure; those attributions live with their cartridges.
