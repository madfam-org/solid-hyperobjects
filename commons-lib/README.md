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
| `hardware/*.py` | the shared device components (see [below](#hardware--shared-device-components-inlined-at-build)) | every cartridge with a `family.py` (generated inline copies) |

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

## `hardware/` — shared device components, inlined at build

Gate H8 (how a component feeds an assembly cartridge) is settled by ruling
**R2**, 2026-11-01: components are authored **once** here and **inlined at
build** into every family's `main.py`. They are never imported — the sandbox
forbids it — and they are not an installed package either, because a package
would move many cartridges' geometry with no cartridge diff, so the render lane
would never see the change.

| Module | Components (CDG id each exposes) | Requires |
| :-- | :-- | :-- |
| `structure.py` | `deck_shell` (`device_envelope`, `cradle_seat`), `hinge_barrel` (`revolute_axis`, `mounting_surface`), `hinge_relief` (consumes `revolute_axis`), `speaker_grille` | `patterns` |
| `controls.py` | `d_pad` (`dpad_seat`), `face_button` + `button_row` (`button_seat`), `analog_stick` (`stick_seat`), `shoulder_trigger` (`trigger_seat`) | `patterns` |
| `connectors.py` | `port_receptacle` (`port_cutout`), `cartridge_slot` (`cartridge_slot`) | — |
| `displays.py` | `display_panel` (`display_recess`) | — |
| `patterns.py` | `linear_pattern`, `polar_pattern` (helpers, not components) | — |

The first twelve were lifted unchanged from `clamshell-dual-screen-handheld`
(geometry-identical at its defaults and all 13 presets). Plan §2.3 lists the
rest of the library; each lands with the family that first needs it.

**The rules a module lives by** (`tools/inline_parts.py` lints them):

- first line `# SPDX-License-Identifier: CERN-OHL-W-2.0`, and one
  `# requires: [<module> ...]` line in the leading comment block;
- at most 600 lines;
- top level holds only a docstring, `import math` / `import cadquery as cq`,
  functions and UPPER_CASE constants — the text runs at the top of every family
  that inlines it;
- every component takes **its own parameter dict**, reads no manifest global and
  knows no assembly;
- no two modules define the same name, and a family may not redefine one.

**How a family uses them.**

1. Author `<slug>/family.py`: the cartridge as you would write `main.py`, with
   exactly one line `# inline-parts: structure controls …` where the components go.
2. Generate: `python3 tools/inline_parts.py --write <slug>`. `main.py` becomes a
   banner, then `family.py` with each module (requirements first, once each)
   between `# BEGIN commons-lib/hardware/<m>.py@<git-blob-sha>` and
   `# END commons-lib/hardware/<m>.py@<git-blob-sha>`, verbatim. Commit both.
3. Never edit `main.py`. CI's `inline_parts.py --check` (manifests lane)
   regenerates every family in memory and fails on any drift.

**Changing a module** means regenerating every family that inlines it in the
same PR: those `main.py` files then appear in the diff and render. `render_scope.py`
also puts every inlining cartridge in scope when a module changes, even if a
`main.py` was not regenerated (fail-closed). The size gate exempts a generated
`main.py` by its markers; `family.py` and every module are measured.

**Testing outside the sandbox.** `tools/inline_parts.load([...])` executes the
modules in inline order into one namespace — the composition a generated
`main.py` runs. `hardware/tests/` builds every component with CadQuery and
checks bodies, volume and bounding box analytically
(`python3 -m pytest commons-lib/hardware/tests`; CI runs it in the `assemblies`
job, which has the kernel).
