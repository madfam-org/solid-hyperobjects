# Gridfinity

Gridfinity on the published **42 mm / 7 mm** standard, **dual-engine**: two
CadQuery B-Rep modes and three OpenSCAD modes, all sharing one base profile — the
**0.8 / 1.8 / 2.15 mm** chamfer stack — so bins seat into baseplates, bins stack
on bins, and lids retain on bins.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

*Gridfinity sobre el estándar publicado de 42 mm / 7 mm, con doble motor: dos
modos B-Rep en CadQuery y tres modos en OpenSCAD, todos con el mismo perfil base
—la pila de chaflanes de 0.8 / 1.8 / 2.15 mm—, de modo que los contenedores
encajan en la placa base, se apilan entre sí y las tapas quedan retenidas.*

**Version**: 3.0.0 · **Slug**: `gridfinity` · **Licence**: CERN-OHL-W-2.0

---

## The three OpenSCAD modes are back, clean-room

`cup`, `baseplate_scad` and `lid` were removed from this commons on **2026-09-04**
under **ADR-021**, because they descended from GPL-3.0 code. They have been
**re-created clean-room** and returned, with their 27 parameters and 7 presets.

The re-creation was authored from a recorded final-result baseline and from the
publicly documented Gridfinity specification, **without access to the removed
implementation or to any upstream implementation**. It is not a port, a migration
or a derivation: it is MADFAM's own authoring of a public standard. See
[`../NOTICE`](../NOTICE) for the provenance statement and
[`CLEANROOM-VERIFICATION.md`](CLEANROOM-VERIFICATION.md) for the measurements
that prove it meets the standard and preserves the baseline's envelope.

**Every declared parameter now does something.** In the removed version 21 of the
27 changed no geometry at all — 14 on the cup, 4 on the baseplate, 3 on the lid.
Dividers, lip style, label shelf, finger slide, sliding-lid rail, wall pattern,
tapered corner, efficient floor, magnets and screws were advertised and inert.
All 27 are live here, verified by rendering each one off its default and
comparing the mesh.

*Los tres modos de OpenSCAD (`cup`, `baseplate_scad`, `lid`) se retiraron el
2026-09-04 conforme a ADR-021 por descender de código GPL-3.0, y regresan
**recreados en sala limpia**, con sus 27 parámetros y 7 preajustes. Se escribieron
a partir de una línea base medida y de la especificación pública de Gridfinity,
**sin acceso a la implementación retirada ni a ninguna implementación previa**.
En la versión retirada 21 de los 27 parámetros no cambiaban geometría alguna;
aquí los 27 están activos y verificados.*

---

## Engines

| Mode ID | Label (en) | Engine | File | Part |
| :--- | :--- | :--- | :--- | :--- |
| `bin` | Bin | **CadQuery** (B-Rep) | `main.py` | `bin` |
| `baseplate` | Baseplate | **CadQuery** (B-Rep) | `main.py` | `baseplate` |
| `cup` | Bin (OpenSCAD Extended) | **OpenSCAD** | `cup.scad` | `cup` |
| `baseplate_scad` | Baseplate (OpenSCAD Extended) | **OpenSCAD** | `baseplate.scad` | `baseplate_scad` |
| `lid` | Lid (OpenSCAD Extended) | **OpenSCAD** | `lid.scad` | `lid` |

The OpenSCAD modes share `gridfinity_std.scad`, which holds the constants, the
base profile and the grid helpers, so the foot and the socket are the *same
function* at different clearances and cannot drift apart. They use **no
third-party library**: every primitive is an OpenSCAD builtin, so they render
with nothing on `OPENSCADPATH`.

## The Gridfinity standard, as implemented

| Quantity | Value | Where |
| :--- | :--- | :--- |
| Grid module | **42.0 mm** in X and Y | all modes |
| Height unit | **7.0 mm** | `cup`, `bin` |
| Bin footprint | **42·n − 0.5 mm** | `cup`, `bin` |
| Baseplate footprint | **42·n** exactly | `baseplate_scad`, `baseplate` |
| Lid footprint | **42·n − 1.0 mm** | `lid` |
| Corner radius | **3.75 mm** at the widest section | all |
| Base profile | **0.8 mm** chamfer 45° → **1.8 mm** straight → **2.15 mm** chamfer 45° = 4.75 mm | all |
| Foot height | **5.00 mm** (the 4.75 mm profile + a 0.25 mm riser) | `cup`, `baseplate_scad` |
| Socket clearance | **0.25 mm** nominal (0.125 mm per side) | `baseplate_scad` |
| Stacking lip | the base profile as a recess at the rim | `cup` |
| Magnet socket | **6 mm** dia × **2 mm** deep on a **26 mm** square | `cup`, `baseplate_scad`, `lid` |
| Screw hole | **M3** clearance (3.4 mm), coaxial with the magnets | `cup`, `baseplate_scad` |

## Parameters — OpenSCAD modes

| Group | Parameter | Modes | Default | What it does |
| :--- | :--- | :--- | :--- | :--- |
| Dimensions | `width_units` | all three | 2 | Grid units in X (× 42 mm). 1–6. |
| Dimensions | `depth_units` | all three | 1 | Grid units in Y (× 42 mm). 1–6. |
| Dimensions | `height_units` | `cup` | 3 | Height units (× 7 mm). 1–10. |
| Bin Structure | `cup_wall_thickness` | `cup` | 0 | Side wall; **0 = auto**, scaling 0.95 → 1.6 mm with height. |
| Bin Structure | `cup_floor_thickness` | `cup` | 0.7 | Solid floor above the foot; moves the cavity floor. |
| Bin Structure | `vertical_chambers` | `cup` | 1 | Compartments along Y — real internal dividers. |
| Bin Structure | `horizontal_chambers` | `cup` | 1 | Compartments along X — real internal dividers. |
| Bin Structure | `lip_style_id` | `cup` | 0 | 0 normal (4.75 mm recess), 1 reduced (2.95), 2 minimum (2.15), 3 none. |
| Bin Structure | `headroom` | `cup` | 0.8 | Undersizes the lip recess so a stacked bin clears it. |
| Bin Structure | `efficient_floor_id` | `cup` | 0 | 0 off, 1 chamfered, 2 rounded, 3 dished relief under the cavity. |
| Bin Features | `fingerslide_enabled` | `cup` | off | A concave ramp in the interior front corner. |
| Bin Features | `label_enabled` | `cup` | off | An overhanging shelf along the rear interior wall. |
| Bin Features | `sliding_lid_enabled` | `cup` | off | Grooves in the interior side walls for a sliding lid. |
| Bin Features | `wallpattern_enabled` | `cup` | off | A relief milled into the side walls, leaving 0.4 mm. |
| Bin Features | `wallpattern_style_id` | `cup` | 0 | 0 hexgrid, 1 grid, 2 voronoi, 3 brick. |
| Bin Features | `tapered_corner_id` | `cup` | 0 | 0 none, 1 rounded, 2 chamfered relief on the front-left corner. |
| Bin Features | `tapered_corner_size` | `cup` | 10 | That relief's size, 5–20 mm. |
| Mounting | `enable_screws` | `cup` | off | M3 clearance through the feet. |
| Mounting | `enable_magnets` | `cup`, `bin` | off | 6 × 2 mm sockets in the feet on the 26 mm square. |
| Mounting | `bp_enable_magnets` | `baseplate_scad` | off | Magnet cavities; the socket gains a floor to host them. |
| Mounting | `bp_enable_screws` | `baseplate_scad` | off | M3 through-holes; likewise. |
| Baseplate | `bp_corner_radius` | `baseplate_scad` | 3.75 | The **plate outline** radius only, 0–10 mm. |
| Baseplate | `bp_reduced_wall` | `baseplate_scad` | −1 | −1 = full 5 mm; else lowers the material between sockets. |
| Baseplate | `bp_reduced_wall_taper` | `baseplate_scad` | off | Chamfers the reduced wall's collar instead of leaving it square. |
| Lid | `lid_include_magnets` | `lid` | on | 6 mm pockets in the underside, depth-capped to keep 0.4 mm. |
| Lid | `lid_efficient_floor` | `lid` | 0.7 | Membrane left under the relief pocket (lid type 3). |
| Lid | `lid_type_id` | `lid` | 0 | 0 default (registration step), 1 flat, 2 halfpitch ridge, 3 efficient. |
| Rendering | `fn` | all three | 0 | `$fn`; **0 = auto = 32**. Tessellation only. |

`bp_corner_radius` drives the **plate outline only**. The socket corner radius is
fixed by the standard at 3.75 mm plus the clearance: a socket rounded past that
stops accepting a standard foot.

## Presets

**OpenSCAD** — and unlike the removed version, each now produces what its name
promises:

- **Small Parts Bin (2×1×3)** `small_bin_scad` — finger slide, magnets.
- **Battery Holder (3×2×3)** `battery_holder_scad` — 3 × 2 chambers, label shelf.
- **Tool Drawer (4×2×2)** `tool_drawer_scad` — 4 chambers, wall pattern.
- **Screw Organizer (3×2×4)** `screw_organizer_scad` — 2 × 3 chambers, label, magnets.
- **Pen Cup (1×1×6)** `pen_cup_scad` — a tall single-cell cup with magnets.
- **Standard Baseplate (2×2)** `baseplate_std_scad` — magnet cavities.
- **Standard Lid (2×1)** `lid_std_scad` — magnets, registration step.

**CadQuery** — Small Parts Bin (2×1×3), Deep Bin (2×2×6), Standard Baseplate (2×2).

## Hyperobject profile

- **Domain:** household · **Commons licence:** CERN-OHL-W-2.0
- **CDG interfaces:** Gridfinity 42 mm Grid (`grid`), Gridfinity Base Profile
  (`profile`), Baseplate Snap Interface (`snap`, 0.25 mm clearance), 6×2 mm
  Magnet Socket (`socket`). All four are **realised in geometry** — in the
  removed version only the first was.
- **Societal benefit:** a universal, freely licensed modular storage grid. One
  shared 42 mm / 7 mm standard lets bins, trays and baseplates from any maker
  interoperate, reducing single-use organizers and packaging waste while keeping
  storage repairable and endlessly reconfigurable.

## Rendering

OpenSCAD modes render through the platform's standard injection shape:

```
OPENSCADPATH=<root>/libs \
  OpenSCAD -o out.stl --backend=Manifold -D width_units=2 -D depth_units=1 … cup.scad
```

Booleans arrive as `1`/`0`, numbers bare, strings quoted; `render_mode` is not
injected because every part in these modes declares `render_mode: 0`.

CadQuery modes live in `main.py`, sandbox-safe: parameters read via
`PARAM(lambda: name, default)`, the final solid assigned to `result`.

**Export formats:** STL / 3MF / STEP / GLB / GLTF / OBJ.
