# MIGRATION — how this repository was built

RFC 0038 §9 "Topology P2": the solid commons is extracted from the `yantra4d`
platform **with full history**, and the satellite repos that held individual
cartridges are absorbed into it, also with full history.

## Source

- `madfam-org/yantra4d` at `cc99c57d0982293de0b383764a35fb7d0adbd2bc` (`main`).
- 34 public satellite repos, each at the commit `yantra4d` pinned. Every pin
  equalled the satellite's own `main`: zero drift.

## What was done

1. **Private client cartridges removed from all history.** `projects/tablaco`
   and `projects/tablaco-v2` existed as plain trees in earlier commits (they
   became submodules only in the 2026-08-24 tree swap). `git filter-repo
   --invert-paths --path projects/tablaco --path projects/tablaco-v2
   --path-glob 'projects/tablaco*'` ran **before** anything else. This repo is
   public; that content is the client's.
2. **`projects/` became the root.** `git filter-repo --subdirectory-filter
   projects`, so each cartridge sits at `<slug>/`. That keeps
   `<slug>/project.json` byte-identical in path terms to the platform's
   `projects/<slug>/project.json`, which is what lets `yantra4d` mount this
   whole repo as one submodule at `projects/`.
3. **`cq-hyperobject-test` dropped.** It is an engine test fixture
   (`box.py` + `box.step`), not a commons object, and is already excluded from
   the catalogue by the platform's `NOT_COMMONS` map. The platform vendors it
   for its own render-engine tests.
4. **Satellites absorbed.** For each: clone from the local checkout, strip
   `.github/` (satellite-era CI, superseded by this repo's), handle nested
   submodules (below), `--to-subdirectory-filter <slug>`, then remove the
   gitlink in the commons and `git merge --allow-unrelated-histories`.
5. **Skeleton added.** `README.md`, `LICENSE` (CERN-OHL-W-2.0 per ADR-011),
   `NOTICE.md`, `CONTRIBUTING.md`, `.gitmodules`, `.github/workflows/ci.yml`.

Only `main` was carried across. `yantra4d`'s other remote branches and all tags
were dropped before filtering.

## Per-satellite record

| Slug | Source repo | Pinned sha | Commits upstream | Absorbed | Nested submodule | Tree-equal |
| :-- | :-- | :-- | --: | --: | :-- | :-- |
| `custom-msh` | `madfam-org/custom-msh` | `c5d72d7cde78` | 10 | 4 | `BOSL2` gitlink and `.gitmodules` dropped — redundant, BOSL2 is served from `libs/` | yes |
| `din-rail-clip` | `madfam-org/din-rail-clip` | `a5d7b8fd4c36` | 12 | 10 | — | yes |
| `extrusion-hyperobject` | `madfam-org/extrusion-hyperobject` | `efb583adc173` | 15 | 13 | — | yes |
| `faircap-filter` | `madfam-org/faircap-filter` | `0fc1f35b84e9` | 11 | 10 | — | yes |
| `fasteners` | `madfam-org/fasteners` | `acbb5226da60` | 9 | 7 | — | yes |
| `framing-hyperobject` | `madfam-org/framing-hyperobject` | `506c07b5756b` | 14 | 12 | — | yes |
| `gear-reducer` | `madfam-org/gear-reducer` | `40be32855487` | 8 | 6 | — | yes |
| `gears` | `madfam-org/gears` | `2d5b8a3e48ca` | 12 | 10 | — | yes |
| `glia-diagnostic` | `madfam-org/glia-diagnostic` | `9d76f8111f98` | 12 | 11 | — | yes |
| `gridfinity` | `madfam-org/gridfinity` | `4ad1cf246d1b` | 20 | 18 | `gridfinity_extended` KEPT as a submodule (GPL-3.0, must not be vendored); re-declared in the root `.gitmodules`, the dead nested `.gitmodules` removed | yes |
| `hinge-hyperobject` | `madfam-org/hinge-hyperobject` | `ae8829f5a33d` | 7 | 5 | — | yes |
| `implicit-lattice-hyperobject` | `madfam-org/implicit-lattice-hyperobject` | `be742ec52cb3` | 12 | 10 | — | yes |
| `julia-vase` | `madfam-org/julia-vase` | `8710d0ad1e14` | 8 | 6 | — | yes |
| `keyv2` | `madfam-org/keyv2` | `b0b816e4b5cc` | 7 | 5 | — | yes |
| `locking-mechanism-hyperobject` | `madfam-org/locking-mechanism-hyperobject` | `ac433d999171` | 18 | 16 | — | yes |
| `maze` | `madfam-org/maze` | `7da23c03102d` | 9 | 7 | — | yes |
| `microscope-slide-holder` | `madfam-org/microscope-slide-holder` | `3395159069c1` | 26 | 24 | — | yes |
| `microscope-slide-hyperobject` | `madfam-org/microscope-slide-hyperobject` | `30ad7678a989` | 12 | 10 | — | yes |
| `motor-mount` | `madfam-org/motor-mount` | `89e39e1d1a8f` | 13 | 11 | — | yes |
| `multiboard` | `madfam-org/multiboard` | `40430f39b2c0` | 8 | 6 | — | yes |
| `parametric-connector` | `madfam-org/parametric-connector` | `bff805fa04f2` | 11 | 9 | — | yes |
| `polydice` | `madfam-org/polydice` | `2159fcc4b87e` | 7 | 5 | — | yes |
| `portacosas` | `madfam-org/portacosas` | `c5876e845d2a` | 6 | 4 | — | yes |
| `prosthetic-socket` | `madfam-org/prosthetic-socket` | `bec40ac9720a` | 10 | 8 | — | yes |
| `relief` | `madfam-org/relief` | `668d360c418a` | 7 | 5 | — | yes |
| `rubiks-hyperobject` | `madfam-org/rubiks-hyperobject` | `232a352bb293` | 29 | 28 | — | yes |
| `rugged-box` | `madfam-org/rugged-box` | `970310a0c209` | 14 | 12 | — | yes |
| `scara-robotics` | `madfam-org/scara-robotics` | `f28f95acc8f9` | 9 | 7 | — | yes |
| `soft-jaw` | `madfam-org/soft-jaw` | `8dd0d2f17ebe` | 11 | 9 | — | yes |
| `spiral-planter` | `madfam-org/spiral-planter` | `3016c4bd9ea8` | 10 | 8 | — | yes |
| `stemfie` | `madfam-org/stemfie` | `6d846893f49a` | 10 | 8 | — | yes |
| `superformula` | `madfam-org/superformula` | `6f6a823de807` | 9 | 7 | — | yes |
| `torus-knot` | `madfam-org/torus-knot` | `b414c05288c9` | 11 | 9 | — | yes |
| `voronoi` | `madfam-org/voronoi` | `f7eb580ba02f` | 7 | 5 | — | yes |
| **total** | | | **394** | **325** | | **34/34 yes** |

**"Absorbed" is lower than "commits upstream" for most satellites, and that is
expected.** Stripping `.github/` makes CI-only commits empty, and `filter-repo`
prunes an empty commit rather than carrying a no-op. Every commit that survived
the strip is reachable from `HEAD` here — verified for all 325, not sampled.
`custom-msh` drops furthest (10 → 4) because it also loses its `BOSL2` gitlink
and `.gitmodules` commits.

"Tree-equal" compares `git rev-parse HEAD:<slug>` in this repo against
`git rev-parse HEAD:<slug>` in the prepared satellite: an identical tree hash,
not a file-by-file diff.

## Nested submodules

- **`custom-msh` → `BOSL2`** — dropped. It duplicated a library this repo
  already provides at `libs/BOSL2`, resolved through `OPENSCADPATH`.
- **`gridfinity` → `gridfinity_extended`** — kept as a submodule, pinned at
  `a28994652bc3990dbef384531ff0ce0addc5b35f`. Upstream is **GPL-3.0**, which is
  copyleft, not permissive, so its files are not vendored into this
  CERN-OHL-W-2.0 tree. It is re-declared in the root `.gitmodules` at
  `gridfinity/gridfinity_extended`; the satellite's own nested `.gitmodules`
  (whose relative path git never reads at a nested level) was removed.

## Known issue carried over: `../../libs/` include paths

50 `.scad` files across 22 cartridges contain `include <../../libs/…>`. That
path is correct at `projects/<slug>/` in the platform, where it resolves to
`<repo>/libs/`. Here, at `<slug>/`, it resolves to this repository's **parent**
directory.

This was verified, not assumed: OpenSCAD does **not** fall back to
`OPENSCADPATH` for an explicit relative include — it emits
`WARNING: Can't find include file '../../libs/BOSL2/std.scad'` and exits 1.
`y4d-spec` already reports these as notes (61 of them), for exactly this reason.

Rendering these cartridges standalone in this repo therefore needs a `libs/`
tree one level **above** the checkout, or the includes rewritten to `../libs/`
(which was verified to work, together with a bare `include <BOSL2/std.scad>`
resolved through `OPENSCADPATH`). Rewriting 50 cartridge source files is a
content change, and it would break the platform's own layout when it mounts
this repo at `projects/`, so it is **left for an operator decision** rather than
taken here.

Two cartridges additionally reach for the platform's own in-tree libraries —
`framing-hyperobject` (`libs/scad_core`, `libs/yantra4d`) and `fasteners`
(`libs/scad_core`, and `libs.cq_core` via `sys.path`). Those 193 lines are
AGPL-3.0 platform code; vendoring them into a CERN-OHL-W-2.0 commons is a
licensing decision, so it is **not** taken here either.

## Post-extraction cleanup (2026-09-04, coordinator)

- Removed `glia-diagnostic/BOSL2/.github/` (11 files: BOSL2 upstream's own
  `gen_docs`, `gen_tutorials`, `main`, `version_stamp`, `weekly_release`
  workflows, `release.yml`, issue templates and two JSON configs) — stale
  upstream CI vendored inside the cartridge's copy of BOSL2. GitHub only runs
  workflows from the repository root, so they were inert, but they read as
  live automation for a repo they have nothing to do with. The satellites' own
  caller workflows (the `validate-and-audit` callers of yantra4d's
  `project-ci-reusable.yml`) were already stripped from every satellite's
  history before absorption; none remain (`git grep project-ci-reusable` = 0).
- Removed `glia-diagnostic/BOSL2/` (148 files, 11 MB): a full vendored copy of
  the BOSL2 library (BSD-2) that nothing referenced — `diagnostic.scad`
  includes `../../libs/BOSL2/std.scad` (the shared `libs/` submodule), and the
  only other mention is a comment. Not a geometry change; the copy stays in
  history. The satellite and yantra4d `main` still carry it; the platform's
  pin to this repo drops it there too.

## Licence-origin removal (2026-09-04, operator ruling — ADR-021 in internal-devops)

Removed whole cartridges whose origin licence is not CERN-OHL-W-2.0: `keyv2`,
`stemfie`, `multiboard`, `polydice`, `rugged-box` (see NOTICE.md). Their
history is intact in this repository's git history and in the archived
satellite repos; the slugs are reserved for clean-room re-creations verified
against a recorded final-result baseline (manifest contract + reference
meshes), authored without access to the removed sources. None of the five is a
Fashion Cabinet bridge target (checked against `yantra4d-hardware.snapshot.json`
and `yantra4d-consumers.json`: zero references).

**`keyv2` returned 2026-09-04**, clean-room, as a CadQuery cartridge authored
from the recorded baseline pack alone. Same slug, same mode/part/parameter ids,
same ranges, defaults and presets, so saved configurations keep resolving. One
intentional divergence from the baseline is recorded in the cartridge's
`docs/CLEANROOM-VERIFICATION.md`: the baseline's default keycap exported as two
disjoint solids (the stem stood free inside the shell), and the re-creation
fuses the stem to the keytop so every variant is one printable body.

### `gridfinity` (ADR-021, 2026-09-04)

Removed the GPL-lineage OpenSCAD side only: modes `cup`, `baseplate_scad`, `lid`
(and their 7 presets and 3 parts) from `project.json`; `cup.scad`,
`baseplate.scad`, `lid.scad`; the unreferenced CadQuery ports `cup.py`, `lid.py`
and the exports `cup_2x1x3.stl`, `lid_2x1.stl`; the `gridfinity/gridfinity_extended`
git submodule (GPL-3.0; no remaining file included it) and its `.gitmodules`
entry. Also removed `baseplate.py` and `exports/baseplate_2x2.stl` (a port of the
removed OpenSCAD baseplate, on its parameter ids). Kept: `main.py` (CadQuery
`bin` + `baseplate`, MADFAM-authored from the published Gridfinity standard) and
the SDK wrapper; 10 parameters remain (the CadQuery set), 27 OpenSCAD-side
parameters went with their modes. The studio fallback manifest in yantra4d is regenerated from this
manifest by the platform lane.
