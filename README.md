# solid-hyperobjects

Last Updated: 2026-10-05

The **solid** half of the MADFAM hyperobjects commons: parametric cartridges for
printed and machined bodies, rendered from CadQuery (B-Rep) or OpenSCAD (CSG).

A hyperobject here is not a mesh. It is the *family* a mesh regenerates into: a
`project.json` manifest declaring parameters, modes, parts and presets, plus the
source that turns a parameter point into geometry. Every cartridge is verified
fail-closed — each `(mode, part)` pair must render watertight, positive-volume
and free of inverted bodies, at its defaults **and** at every preset it ships.

**512 cartridges** — the five slugs once withdrawn for licence reasons have all
returned as clean-room re-creations (see [`NOTICE.md`](./NOTICE.md)). Licensed
CERN-OHL-W-2.0, with the carve-outs recorded there.

Measured on 2026-10-05: 512 manifests · **512/512** with a declared body
count · **509/512** carrying at least
one feasibility constraint · **20** animated assemblies · **5** cartridges with a
reasoned cross-kernel parity exemption or widened tolerance (the count of 2026-09-29;
the cartridges added since agree at the parity bar).

## The four-repo topology

Per [RFC 0038 §9](https://github.com/madfam-org/internal-devops) — platforms are
separated from commons, and the contracts are packaged once:

| Repo | Holds |
| :-- | :-- |
| `yantra4d` | the solid platform: studio, API, tiers, render workers, admin |
| `fashion-cabinet` | the soft platform: studio, API, kernel runtime, the MTM seam |
| **`solid-hyperobjects`** (this repo) | the solid cartridges, catalog, indexes |
| `soft-hyperobjects` | the garments, fc indexes, fabric cards, bodies |
| `hyperobjects-spec` | schemas, sandbox, validators — the verification bar itself |

**The keystone rule:** the bar lives in `hyperobjects-spec`, never in platform
code. CI here installs that package and runs it. A contributor can therefore
check a cartridge without cloning a platform, and passing that check and passing
CI are the same thing.

The platform mounts this repo as a single submodule at `projects/`, which is why
every cartridge sits at `<slug>/` in the root here: `<slug>/project.json` in this
repo is `projects/<slug>/project.json` there, unchanged.

## Assemblies and graph twins

[`assemblies/`](./assemblies/README.md) holds type-level assemblies (ASM-1) that compose
cartridges from this repo with keystone standard parts:

- **A, [`voron-2-4-class-350-motion-frame`](./assemblies/voron-2-4-class-350-motion-frame/README.md):**
  the motion system of a Voron 2.4-class 350 CoreXY printer, as an original design that cites
  the 2.4r2 guide by page only. 235 components, 292 mates, 25 joints, 10 belt paths and 23
  poses (home, the six limits of the three driven joints, 16 sweep samples), collision-clean.
  Its machine bindings map Klipper's X, Y and Z onto the three driven joints, each value cited
  to the public Klipper reference configuration.
- **B, [`fpv-5in-freestyle`](./assemblies/fpv-5in-freestyle/README.md):** a 5-inch FPV
  freestyle frame with motors, camera, stack and antenna chain.

**Graph twins.** The ten printed cartridges in A (`ab-drive`, `ab-front-idler`,
`bed-extrusion-mount`, `corner-idler-bracket`, `toolhead-proxy`, `x-carriage`, `xy-joint`,
`z-belt-clamp`, `z-drive-housing`, `z-joint`) each carry a `*.graph.json` in graph format
1.1, declared as `graph_file` on the mode beside the script. The script stays the rendered
source and the oracle: `--parity` compares the graph with it at the defaults and at every
preset, gate for gate, and a script retires only after that parity holds across the nightly
sweep. Each cartridge's `docs/README.md` has a *Graph twin* section.

## Validating a cartridge

```bash
pip install "hyperobjects-spec[geometry] @ git+https://github.com/madfam-org/hyperobjects-spec@142db1802bbf9e1135ceae6c9c531c469f2d295b"

y4d-spec check ./gridfinity                # manifest + files, under a second
y4d-spec check ./gridfinity --render       # + geometry, every (mode, part) and every preset
# Whole commons, manifests only; exclude library/helper directories.
for manifest in */project.json; do
  y4d-spec check "${manifest%/project.json}" -v || exit 1
done
y4d-spec rules                             # what is checked, and where each rule came from
```

Manifest conformance is pure Python. `--render` pulls a CAD kernel (~400 MB);
on Debian/Ubuntu it also needs `libgl1`, `libglib2.0-0` **and** `libxrender1`.

OpenSCAD cartridges resolve their library includes through `OPENSCADPATH`:
third-party libraries from the pinned `libs/*` submodules, and the first-party
helpers in `commons-lib/` from the repository root:

```bash
git submodule update --init --recursive
export OPENSCADPATH="$PWD/libs:$PWD"
```

## How CI verifies a change

The keystone pin CI installs is `142db180` (`SPEC_PIN` in
[`.github/workflows/ci.yml`](./.github/workflows/ci.yml)). Every gate below is
that package's, run from this repo — there is no second, hidden bar.
Compiler warning/error lines are retained as bounded notes identified by mode,
part and preset, even when OpenSCAD exports a valid partial mesh. Review them:
a geometry pass is not proof that every include or module resolved. Notes stay
nonblocking until whole-commons false-positive analysis supports a stronger rule.

- **Manifest conformance** runs on every PR for all 512 cartridges
  (`y4d-spec check`, seconds), alongside the unit tests for this repo's own CI
  scripts (`python3 -m pytest .github/scripts`) and the reporter's selftest.
- **Assembly check** runs on every PR for every
  [`assemblies/<slug>/assembly.json`](./assemblies/) (ASM-1 §3, §7):
  `y4d-spec assembly check --commons . --standard-parts <the pinned keystone's
  catalog>` through [`.github/scripts/assembly_check.py`](./.github/scripts/assembly_check.py).
  It fails on any validation error (an unresolved component, a mate that breaks
  the mating rule, a mate or cycle that does not close within 0.05 mm / 0.5°, an
  unreachable component) and on a directory under `assemblies/` with no
  `assembly.json`. It runs with `--collision` (keystone ≥ 0.9.0): rendered
  cartridges and catalog envelopes are intersected at every pose of the sweep, and
  an overlap above 1 mm³ that the assembly does not declare in `allowed_overlaps`
  fails. A component with no solid yet is named in a warning, never passed.
- **Render lane (per PR, chunked).** `render-scope` takes the fork-point diff and
  decides *which* cartridges need geometry, then `render-changed` runs them as a
  matrix of groups of at most eight (`max-parallel: 2`, 60-minute jobs). Each
  group runs:

  ```
  y4d-spec check ./<slug> --render --require-openscad --parity
  ```

  Both kernels, every `(mode, part)`, at defaults **and** at every preset.
  `--require-openscad` means a missing binary is a failure, never a skip (the
  runner image ships OpenSCAD **2026.02.13**, the version the platform image
  pins, enforced by the spec's `y4d-spec render-env` contract and by enclii's own
  drift check on the runner image). `--parity` compares the two kernels'
  meshes — it has been a merge-path gate since 2026-09-06. On a mode that
  declares both a script and a `graph_file` (a graph twin), the same `--parity`
  compares the graph with its script. A change to `SPEC_PIN` puts every graph
  cartridge back in scope, because the transpiler ships with the keystone.
- **What `render-scope` skips, and why.** A cartridge whose *only* change is
  manifest metadata is dropped from the scope: the allow-list in
  [`.github/scripts/render_scope.py`](./.github/scripts/render_scope.py) covers
  attribution, prose, tags, lineage, and — since 2026-09-06 — `constraints`
  (feasibility rules the configurator evaluates on the parameter set; they never
  reach a kernel) and `animations` (parameter-state sequences the API re-renders
  on demand; a cartridge's own render never reads them). Anything else —
  `.py`/`.scad` source, `fonts/`, `parameters`, `parts`, `modes`, `presets`,
  `engine`, `verification`, or any file the script does not recognise — keeps
  the cartridge in scope. An unparseable manifest keeps it in scope too: the
  lane fails closed, never open.
- **Nightly full sweep (chunked, 09:00Z / 03:00 CDMX).** `nightly-scope` cuts the
  whole commons into deterministic groups of at most eight and uploads the scope
  as an artifact; `render-nightly` renders them (`max-parallel: 3`, 90-minute
  jobs, per-group log artifact, same `--render --require-openscad --parity`);
  `nightly-report` concatenates the logs and decides the verdict. A cartridge
  measured slower than five minutes locally gets a group of its own — `zipper`
  does, at 39 min 12 s for 18 renders.
- **The nightly verdict is three conditions, all required.** Green needs (1)
  every render group green, (2) the **completeness check** — the union of the
  cartridges actually rendered must equal the scope artifact, so a job that dies
  before reaching its tail cannot pass as green, and (3) **zero FAIL rows** in
  the concatenated log, failing closed on an empty count. The group step runs
  under `set -o pipefail` with a sticky return code and prints a
  `GROUP VERDICT:` line; without pipefail a `… | tee` pipeline reported `tee`'s
  exit 0 and produced a false green (run 34023334942: 67 green jobs over 62 FAIL
  rows). `nightly_report.py --green` refuses a log that still contains FAIL rows.
- **A red sweep opens one tracking issue, not one per night.**
  [`.github/scripts/nightly_report.py`](./.github/scripts/nightly_report.py)
  (stdlib only) parses the FAIL lines into a table — `cartridge | mode/part |
  preset | engine | reason` — and maintains a single issue labelled
  **`nightly-sweep`**: it creates the issue, rewrites its body on later red runs
  (latest table on top, dated history below) with a delta comment naming what
  broke and what got fixed, and **closes it when the sweep goes green**. A
  never-rendered cartridge appears as a `NEVER RENDERED` row. Auth is the job's
  `GITHUB_TOKEN` (`issues: write`), retrying once with `MADFAM_BOT_PAT` on 403;
  a reporting failure never turns a green sweep red.
- **The bar per render.** Watertight, positive volume, no inverted
  (negative-volume) body, **B-Rep validity before tessellation** (`BRepCheck`
  plus a per-solid signed-volume test — a `Reversed()` solid is `IsValid()` yet
  negative, and a macOS-green render is not proof: the tripod-hub fuse is
  invalid on macOS OCCT and valid on Linux OCP), the declared body count, and
  cross-kernel parity.
- **Parity is three gates.** Extents (AABB), volume, and — since keystone
  `3aa57133` — *shape*: the placement offset (AABB-centre delta) is reported as a
  note, or fails under a per-part `"placement": "strict"`, and the Hausdorff
  distance is computed **after** alignment and fails above `max(0.5 mm,
  tolerance)`. A pair may be exempted or given a wider tolerance only with a
  written reason (see [`CONTRIBUTING.md`](./CONTRIBUTING.md)); the summary line
  reads `parity=N/M ok, warn=K, exempt=E, failures=J`.
- **Declared body counts.** `verification.stages.geometry.checks.body_count.expected`
  at the base, with per-mode/part overrides under
  `verification.mode_overrides.<mode>.part_overrides.<part>` using
  **stage-qualified keys** (`"geometry.body_count"`); parametric counts use the
  `part_quantities` expression dialect.

## Layout

```
<slug>/project.json     the manifest — single source of truth for the cartridge
<slug>/*.py             CadQuery source
<slug>/*.scad           OpenSCAD source
<slug>/LICENSE          CERN-OHL-W-2.0 (or the cartridge's own, if it differs)
<slug>/NOTICE           third-party attributions, where any apply
libs/*                  pinned third-party OpenSCAD libraries (submodules)
commons-lib/*           first-party shared helpers, resolved via OPENSCADPATH
```

## Related repositories and contracts

Each link goes to the document that defines the contract on the other side.

| Contract | Defined in | What this repo relies on |
| :-- | :-- | :-- |
| Assemblies (ASM-1), kinematics (§9), `--collision`, golden poses | hyperobjects-spec [`docs/ASSEMBLIES.md`](https://github.com/madfam-org/hyperobjects-spec/blob/main/docs/ASSEMBLIES.md) | the checker behind the `assemblies` job and the [assemblies](./assemblies/README.md) here |
| Graph format 1.x (`.graph.json`) | hyperobjects-spec [`graph.schema.json`](https://github.com/madfam-org/hyperobjects-spec/blob/main/src/y4d_spec/graph/graph.schema.json) and [`VENDORED.md`](https://github.com/madfam-org/hyperobjects-spec/blob/main/src/y4d_spec/graph/VENDORED.md) | the transpiler `--parity` runs on every graph twin |
| Cartridge checks, parity, the golden-twin rule | hyperobjects-spec [`README.md`](https://github.com/madfam-org/hyperobjects-spec/blob/main/README.md) | `y4d-spec check`, the bar of every CI lane |
| Authoring and editing graph cartridges | yantra4d [`docs/guides/graph-cartridges.md`](https://github.com/madfam-org/yantra4d/blob/main/docs/guides/graph-cartridges.md) | the Studio graph editor that edits forks of these cartridges |
| Where forks and imports are stored | yantra4d [`docs/operations/user-projects-storage.md`](https://github.com/madfam-org/yantra4d/blob/main/docs/operations/user-projects-storage.md) | a fork is written outside this commons; the commons stays read-only |
| Render artifacts and the render worker | yantra4d [`docs/operations/render-artifact-storage.md`](https://github.com/madfam-org/yantra4d/blob/main/docs/operations/render-artifact-storage.md) | how the platform renders a cartridge from this repo |
| Type, assembly and instance shells; the twin graph | asset-shells [`README.md`](https://github.com/madfam-org/asset-shells/blob/main/README.md) (*Publish API*, *Twin graph*) | the store a solid-commons release publishes its shells and assembly shells to |
| Machine telemetry (Sparkplug 3.0) | pravara-mes [`packages/sparkplug/README.md`](https://github.com/madfam-org/pravara-mes/blob/main/packages/sparkplug/README.md) | raw machine-axis values, which a viewer maps through an assembly's machine bindings (ASM-1 §9.2) |

## Contributing

One cartridge per PR, born bilingual (en/es), CERN-OHL-W-2.0. See
[`CONTRIBUTING.md`](./CONTRIBUTING.md).

Automated contributors start at [`AGENTS.md`](./AGENTS.md), which maps the CI
lanes and the rules that are not obvious from reading the code.
