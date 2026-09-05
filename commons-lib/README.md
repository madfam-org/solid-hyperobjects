# `commons-lib/` — first-party helper library for the commons

Shared geometry helpers that commons cartridges resolve through
`OPENSCADPATH`, so no cartridge has to reach outside this repository at render
time.

## Provenance and licence

These helpers were originally authored by **Innovaciones MADFAM** and published
under **AGPL-3.0** in `madfam-org/yantra4d` (`libs/scad_core/core.scad`,
`libs/yantra4d/cdg_interfaces.scad`, `libs/cq_core/__init__.py`). As the rights
holder, Innovaciones MADFAM **relicensed** them under **CERN-OHL-W-2.0** on
**2026-09-05**, per operator ruling **G11**, so that they can live inside this
CERN-OHL-W-2.0 commons. See `LICENSE`.

Only the helpers the commons actually calls were brought across — nothing else
from the platform libraries is vendored here.

| File | Provides | Called by |
| :-- | :-- | :-- |
| `scad_core.scad` | `y4d_standard_thread` | `fasteners/bolt.scad` |
| `scad_core.scad` | `y4d_vesa_pattern` (+ `vesa_spec`), `y4d_standoff_set` (+ `y4d_standoff_barrel`), `y4d_french_cleat` | `framing-hyperobject/framing.scad` |
| `cq_core.py` | `cdg_french_cleat` | `framing-hyperobject/framing.py` (inline copy — see below) |

## Using it

**OpenSCAD** — include by library path; the directory *containing* `commons-lib`
must be on `OPENSCADPATH`:

```scad
include <commons-lib/scad_core.scad>
```

The commons CI sets `OPENSCADPATH=<workspace>/libs:<workspace>` — the second
entry is the repository ROOT, not `commons-lib` itself, so the `commons-lib/`
prefix in the include is what resolves the file. Locally:

```sh
export OPENSCADPATH="$PWD/libs:$PWD"
```

**CadQuery** — do **not** import this module from a cartridge. The render
sandbox blocks `sys`, `os` and `importlib`, so a cartridge script cannot import
a sibling module at all; that is precisely why the old `sys.path` hack never
rendered. Cartridges keep a self-contained inline copy, and `cq_core.py` is the
licensed canonical text those copies are kept in sync with.
