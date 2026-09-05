# Gridfinity

Gridfinity on the published **42 mm / 7 mm** standard, **dual-engine**. Two
CadQuery B-Rep modes and three OpenSCAD modes share one base profile — the
**0.8 / 1.8 / 2.15 mm** chamfer stack over a **5.00 mm** foot — so bins seat into
baseplates, bins stack on bins, and lids retain on bins.

**Version** 3.0.0 · **Slug** `gridfinity` · **Licence** CERN-OHL-W-2.0

For the full bilingual documentation see [`docs/README.md`](docs/README.md); for
the measurements that prove the geometry, see
[`docs/CLEANROOM-VERIFICATION.md`](docs/CLEANROOM-VERIFICATION.md).

## Modes and parts

Five modes, each with its own part. The engine column is what the platform
renders the mode with; it is not interchangeable.

| Mode | Part | Engine | Source | What it is |
| :--- | :--- | :--- | :--- | :--- |
| `bin` | Bin | CadQuery | `main.py` | Hollow storage bin, B-Rep. |
| `baseplate` | Baseplate | CadQuery | `main.py` | Plate whose sockets are the negative of the bin foot. |
| `cup` | Bin | OpenSCAD | `cup.scad` | Storage bin with dividers, label shelf, finger slide, sliding-lid rail, wall pattern, tapered corner, efficient floor. |
| `baseplate_scad` | Baseplate | OpenSCAD | `baseplate.scad` | Plate with optional reduced wall, magnets, screws. |
| `lid` | Lid | OpenSCAD | `lid.scad` | Lid in four types, with registration to the bin rim. |

The two engines are mutually independent implementations of the same standard,
each with its own parameter set. `bin` and `cup` build the same object; a bin
and a cup of the same size and wall thickness agree on footprint, height and
volume within the platform's parity rule (see the verification document).

## Parameters

Derived from `project.json`; the manifest is the source of truth. "Modes" is the
mode list the parameter applies to — a parameter is ignored by any other mode.

### Shared / CadQuery modes (`bin`, `baseplate`)

| Id | Type | Default | Range | Modes | What it does |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `target_part` | select | `bin` | `bin`, `baseplate` | bin, baseplate | Which Gridfinity part to generate. |
| `grid_x` | slider | 2 | 1–6 step 1 | bin, baseplate | Grid units in X — each unit is 42 mm. |
| `grid_y` | slider | 1 | 1–6 step 1 | bin, baseplate | Grid units in Y — each unit is 42 mm. |
| `grid_z` | slider | 3 | 1–12 step 1 | bin | Height in 7 mm units. |
| `wall` | slider | 1.2 | 0.8–3.0 step 0.1 | bin | Bin side-wall thickness. |
| `floor_th` | slider | 1.2 | 0.6–4.0 step 0.1 | bin | Solid floor above the base profile. |
| `lip_enabled` | checkbox | true | — | bin | Top lip so bins stack on one another. |
| `enable_magnets` | checkbox | false | — | bin, cup | 6 mm dia × 2 mm deep pockets at each cell corner, on the standard 26 mm square. |
| `finger_scoop` | checkbox | false | — | bin | Front ramp for easy access to contents. |
| `bp_thickness` | slider | 5.25 | 4.75–10.0 step 0.25 | baseplate | Plate thickness; ≥ 4.75 mm socket profile depth. |

### OpenSCAD modes — dimensions

| Id | Type | Default | Range | Modes | What it does |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `width_units` | slider | 2 | 1–6 step 1 | cup, baseplate_scad, lid | Grid units in X (multiples of 42 mm). |
| `depth_units` | slider | 1 | 1–6 step 1 | cup, baseplate_scad, lid | Grid units in Y (multiples of 42 mm). |
| `height_units` | slider | 3 | 1–10 step 1 | cup | Height units (multiples of 7 mm). |

### OpenSCAD `cup` — structure

| Id | Type | Default | Range | What it does |
| :--- | :--- | :--- | :--- | :--- |
| `cup_wall_thickness` | slider | 0 | 0–3 step 0.2 | 0 = auto based on height. |
| `cup_floor_thickness` | slider | 0.7 | 0.4–2 step 0.1 | Minimum floor thickness above magnets. |
| `vertical_chambers` | slider | 1 | 1–6 step 1 | Number of compartments along Y. |
| `horizontal_chambers` | slider | 1 | 1–6 step 1 | Number of compartments along X. |
| `lip_style_id` | slider | 0 | 0–3 step 1 | 0 = normal, 1 = reduced, 2 = minimum, 3 = none. |
| `headroom` | slider | 0.8 | 0–2 step 0.1 | Top undersizing for better stacking. |
| `efficient_floor_id` | slider | 0 | 0–3 step 1 | 0 = off, 1 = on, 2 = rounded, 3 = smooth — saves 30–40 % material. |

### OpenSCAD `cup` — features and mounting

| Id | Type | Default | Range | What it does |
| :--- | :--- | :--- | :--- | :--- |
| `fingerslide_enabled` | checkbox | false | — | Add front ramp for easy access. |
| `label_enabled` | checkbox | false | — | Add label surface. |
| `sliding_lid_enabled` | checkbox | false | — | Enable sliding lid support. |
| `wallpattern_enabled` | checkbox | false | — | Enable decorative wall pattern. |
| `wallpattern_style_id` | slider | 0 | 0–3 step 1 | 0 = hexgrid, 1 = grid, 2 = voronoi, 3 = brick. |
| `tapered_corner_id` | slider | 0 | 0–2 step 1 | 0 = none, 1 = rounded, 2 = chamfered. |
| `tapered_corner_size` | slider | 10 | 5–20 step 1 | Corner taper radius / size. |
| `enable_screws` | checkbox | false | — | Add M3×6 screw holes in corners. |

### OpenSCAD `baseplate_scad`

| Id | Type | Default | Range | What it does |
| :--- | :--- | :--- | :--- | :--- |
| `bp_enable_magnets` | checkbox | false | — | Add magnet cavities in baseplate. |
| `bp_enable_screws` | checkbox | false | — | Add screw holes in baseplate corners. |
| `bp_corner_radius` | slider | 3.75 | 0–10 step 0.25 | Baseplate corner radius (the plate outline only, never the sockets). |
| `bp_reduced_wall` | slider | −1 | −1–10 step 0.5 | −1 = full height. |
| `bp_reduced_wall_taper` | checkbox | false | — | Taper the reduced wall edge. |

### OpenSCAD `lid`

| Id | Type | Default | Range | What it does |
| :--- | :--- | :--- | :--- | :--- |
| `lid_include_magnets` | checkbox | true | — | Include magnet cavities in lid. |
| `lid_efficient_floor` | slider | 0.7 | 0.4–2 step 0.1 | Lid efficient floor thickness. |
| `lid_type_id` | slider | 0 | 0–3 step 1 | 0 = default, 1 = flat, 2 = halfpitch, 3 = efficient. |

### Rendering

| Id | Type | Default | Range | Modes | What it does |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fn` | slider | 0 | 0–64 step 8 | cup, baseplate_scad, lid | 0 = auto (32); higher = more detail but slower. |

## Presets

| Id | Mode | What it sets |
| :--- | :--- | :--- |
| `small_parts_bin` | bin | 2×1×3, magnets, finger scoop. |
| `deep_bin` | bin | 2×2×6, magnets. |
| `standard_baseplate` | baseplate | 2×2. |
| `small_bin_scad` | cup | 2×1×3, magnets, finger slide. |
| `battery_holder_scad` | cup | 3×2×3, 3×2 chambers, label. |
| `tool_drawer_scad` | cup | 4×2×2, 4 chambers along X, wall pattern. |
| `screw_organizer_scad` | cup | 3×2×4, 2×3 chambers, label, magnets. |
| `pen_cup_scad` | cup | 1×1×6, magnets. |
| `baseplate_std_scad` | baseplate_scad | 2×2, magnets. |
| `lid_std_scad` | lid | 2×1, magnets. |

## The standard implemented

| Quantity | Value |
| :--- | :--- |
| Grid module | 42.0 mm in X and Y |
| Height unit | 7.0 mm |
| Bin footprint | 42·n − 0.5 mm |
| Baseplate footprint | 42·n mm |
| Lid footprint | 42·n − 1.0 mm |
| Corner radius, widest section | 3.75 mm |
| Base profile | 0.80 mm chamfer / 1.80 mm straight / 2.15 mm chamfer = 4.75 mm |
| Foot height | 5.00 mm (the 4.75 mm stack plus a 0.25 mm full-width riser) |
| Foot-to-socket clearance | 0.25 mm diametral (0.125 mm per side) |
| Magnet socket | 6 mm dia × 2 mm deep, on a 26 mm square |
| Screw hole | M3 clearance, 3.4 mm |

## Export

`export_formats` in `project.json`: STL, 3MF, STEP, GLB, glTF and OBJ.

## Licence and attribution

Licensed under the CERN Open Hardware Licence Version 2 — Weakly Reciprocal
(CERN-OHL-W-2.0). See [LICENSE](LICENSE) and [NOTICE](NOTICE).

Authored by **Innovaciones MADFAM**. It implements a published standard; it is
not a port, a migration or a derivation of any third-party implementation.

- **[Gridfinity](https://gridfinity.xyz/)** by Zack Freedman
  ([Voidstar Lab](https://www.voidstarlab.com/)) — the modular storage system
  standard this project implements, released under the **MIT License**.

> **2026-09-04 (ADR-021, internal-devops).** The three OpenSCAD modes (`cup`,
> `baseplate_scad`, `lid`) that descended from GPL-3.0 code were removed from the
> commons together with that git submodule and the helper scripts and exports
> derived from them — and have since been **re-created clean-room** and returned,
> with their 27 parameters and 7 presets, from the published Gridfinity standard
> and a recorded measurement baseline, without access to the removed
> implementation or to any upstream one. In a follow-up pass the CadQuery `bin`
> and `baseplate` were **repaired** under the ADR's amendment §3 (a cartridge
> that fails the rendering bar is repaired when it is ours): `lip_enabled` was
> inert and now builds the standard's stacking-lip recess, the foot was 4.75 mm
> and is now the standard's 5.00 mm, and the baseplate socket clearance was
> 1.0 mm diametral and is now the standard's 0.25 mm. See
> [docs/CLEANROOM-VERIFICATION.md](docs/CLEANROOM-VERIFICATION.md) for both the
> clean-room measurements and the cross-engine parity result.

See [NOTICE](NOTICE) for the full third-party attribution list.
