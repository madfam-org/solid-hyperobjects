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

| Module | Public API (CDG notes where listed) | Requires |
| :-- | :-- | :-- |
| `cables.py` | `cable_section`, `connector_plug`, `strain_relief`, `cable_path`, `cable_jacket`, `coil_cord`, `cable_ferrite`, `coil_with_leads` | — |
| `case_flexure.py` | `flexure_pose`, `flexure_web`, `flexure_lid`, `media_pocket_frame`, `outer_sleeve_lips` | `media_cases` |
| `connectors.py` | `port_receptacle` (`port_cutout`), `cartridge_slot` (`cartridge_slot`) | — |
| `console_io.py` | `media_cartridge_slot`, `card_slot`, `disc_lid_seat`, `disc_lid`, `disc_tray_bay`, `disc_tray`, `slot_loader`, `slot_door`, `slot_blank`, `slide_switch`, `controller_port`, `port_row` | `console_shell` |
| `console_shell.py` | `face_plane`, `face_frame`, `section_profile`, `shell_body`, `upper_tier`, `side_cover`, `vent_field`, `foot_set`, `stand_seat`, `handle` | — |
| `console_stands.py` | `console_stand_body` | `console_supports` |
| `console_supports.py` | `support_box`, `dock_chassis`, `dock_device_tool`, `dock_boss`, `dock_port_cut`, `dock_door`, `support_disc`, `stand_seat_tool` | — |
| `controls.py` | `d_pad` (`dpad_seat`), `face_button` + `button_row` (`button_seat`), `analog_stick` (`stick_seat`), `shoulder_trigger` (`trigger_seat`) | `patterns` |
| `disc_media.py` | `revolved_disc`, `disc_shell_outline`, `disc_shell_boss`, `disc_pocket`, `disc_window`, `disc_read_slot`, `disc_shutter_track`, `disc_shutter_plate` | — |
| `displays.py` | `display_panel` (`display_recess`) | — |
| `handheld_body.py` | `face_tool`, `face_cut_center`, `slab_depth`, `slab_bottom`, `rear_y`, `slab_body`, `half_space`, `media_slot`, `media_proxy`, `cell_bay_size`, `battery_bay`, `battery_door`, `side_rail`, `kickstand_recess`, `kickstand`, `edge_port`, `rear_recess` | — |
| `media_cases.py` | `case_box`, `case_pan`, `case_pin`, `case_hinge_eye`, `case_disc_hub`, `case_tray`, `case_booklet_tabs`, `case_open` | — |
| `media_shells.py` | `media_shell_outer`, `media_shell_cavity`, `contact_window`, `contact_pocket`, `edge_connector_board`, `label_recess`, `grip_ridges`, `keying_notches`, `shutter_outline`, `pass_through_mouth`, `media_place` | — |
| `pad_body.py` | `pad_crown_q`, `pad_crown_top`, `pad_crown_bottom`, `pad_crown_dome`, `pad_grip_count`, `pad_grip_layout`, `pad_grip`, `pad_body`, `pad_rail`, `pad_magnet_pockets` | `structure` |
| `pad_controls.py` | `pad_rotate_xy`, `pad_face_layout`, `pad_round_seats`, `pad_octagon_seat`, `pad_round_caps`, `pad_cross_cap`, `pad_stick`, `pad_box`, `pad_trigger_blade`, `pad_grille`, `pad_door_seam` | `pad_body` |
| `patterns.py` | `linear_pattern`, `polar_pattern` (helpers) | — |
| `power_cases.py` | `adapter_body`, `adapter_prongs`, `adapter_inlet` | — |
| `structure.py` | `deck_shell` (`device_envelope`, `cradle_seat`), `hinge_barrel` (`revolute_axis`, `mounting_surface`), `hinge_relief` (consumes `revolute_axis`), `speaker_grille` | `patterns` |

The first twelve components were lifted unchanged from
`clamshell-dual-screen-handheld` (geometry-identical at its defaults and original
13 presets). The inventory now includes console and controller bodies, optical
and plug-in media, handhelds, cases, cables, power adapters, docks and stands.
Public helpers share the same flat inline namespace as components; private
helpers are omitted from this table but still participate in collision checks.
Python names are not CDG IDs: interface bindings belong to each component's
source and the consuming cartridge manifest. The namespace table lists the
implemented API, not a promise of interchangeable physical parts.

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
