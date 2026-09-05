# solid-hyperobjects

The **solid** half of the MADFAM hyperobjects commons: parametric cartridges for
printed and machined bodies, rendered from CadQuery (B-Rep) or OpenSCAD (CSG).

A hyperobject here is not a mesh. It is the *family* a mesh regenerates into: a
`project.json` manifest declaring parameters, modes, parts and presets, plus the
source that turns a parameter point into geometry. Every cartridge is verified
fail-closed — each `(mode, part)` pair must render watertight, positive-volume
and free of inverted bodies, at its defaults **and** at every preset it ships.

**500 cartridges.** Licensed CERN-OHL-W-2.0, with the carve-outs recorded in
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
pip install "hyperobjects-spec[geometry] @ git+https://github.com/madfam-org/hyperobjects-spec@cb19e515c4d9b6a603e7d3863a7e6027e6877c59"

y4d-spec check ./gridfinity                # manifest + files, under a second
y4d-spec check ./gridfinity --render       # + geometry, every (mode, part) and every preset
y4d-spec check ./*/ -v                     # the whole commons, manifests only
y4d-spec rules                             # what is checked, and where each rule came from
```

Manifest conformance is pure Python. `--render` pulls a CAD kernel (~400 MB);
on Debian/Ubuntu it also needs `libgl1`, `libglib2.0-0` **and** `libxrender1`.

OpenSCAD cartridges resolve their library includes from the pinned `libs/*`
submodules:

```bash
git submodule update --init --recursive
export OPENSCADPATH="$PWD/libs"
```

## Layout

```
<slug>/project.json     the manifest — single source of truth for the cartridge
<slug>/*.py             CadQuery source
<slug>/*.scad           OpenSCAD source
<slug>/LICENSE          CERN-OHL-W-2.0 (or the cartridge's own, if it differs)
<slug>/NOTICE           third-party attributions, where any apply
libs/*                  pinned third-party OpenSCAD libraries (submodules)
```

## Contributing

One cartridge per PR, born bilingual (en/es), CERN-OHL-W-2.0. See
[`CONTRIBUTING.md`](./CONTRIBUTING.md).
