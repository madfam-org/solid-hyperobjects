# solid-hyperobjects

The **solid** half of the MADFAM hyperobjects commons: parametric cartridges for
printed and machined bodies, rendered from CadQuery (B-Rep) or OpenSCAD (CSG).

A hyperobject here is not a mesh. It is the *family* a mesh regenerates into: a
`project.json` manifest declaring parameters, modes, parts and presets, plus the
source that turns a parameter point into geometry. Every cartridge is verified
fail-closed — each `(mode, part)` pair must render watertight, positive-volume
and free of inverted bodies, at its defaults **and** at every preset it ships.

**495 cartridges** (five slugs reserved for clean-room re-creation — see `NOTICE.md`). Licensed CERN-OHL-W-2.0, with the carve-outs recorded in
[`NOTICE.md`](./NOTICE.md).

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

## Validating a cartridge

```bash
pip install "hyperobjects-spec[geometry] @ git+https://github.com/madfam-org/hyperobjects-spec@308efae80b0e8d03d6e4d018d2d9c1ebce9406d6"

y4d-spec check ./gridfinity                # manifest + files, under a second
y4d-spec check ./gridfinity --render       # + geometry, every (mode, part) and every preset
y4d-spec check ./*/ -v                     # the whole commons, manifests only
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

- **Manifest conformance** runs on every PR for all 500 cartridges (`y4d-spec check`, seconds).
- **Render lane** runs on every PR for the cartridges the PR touched (fork-point diff; manifest-metadata-only
  changes are skipped), in groups of at most eight cartridges per job. Since 2026-09-05 it renders **both
  kernels**: CadQuery through the spec's sandboxed runner and OpenSCAD through the platform's own command
  line (`--require-openscad` — a missing binary is a failure, never a skip; the runner image ships OpenSCAD
  2026.02.13, the version the platform image pins, per the spec's `y4d-spec render-env` contract).
- **Nightly full sweep** renders every cartridge, both kernels, at defaults and every preset.
- The bar per render: watertight, positive volume, no inverted (negative-volume) body, and the body count
  the manifest declares — `verification.stages.geometry.checks.body_count.expected` at the base, with
  per-mode/part overrides under `verification.mode_overrides.<mode>.part_overrides.<part>` using
  **stage-qualified keys** (`"geometry.body_count"`); parametric counts use the `part_quantities`
  expression dialect.

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

## Contributing

One cartridge per PR, born bilingual (en/es), CERN-OHL-W-2.0. See
[`CONTRIBUTING.md`](./CONTRIBUTING.md).
