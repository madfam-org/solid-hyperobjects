# Gridfinity

An exact **CadQuery B-Rep** Gridfinity bin and baseplate on the published
**42 mm / 7 mm** standard: bins print on a 42 mm grid in 7 mm height units and
snap into a matching baseplate through the canonical stacking-lip base profile,
with optional corner magnet holes and a front finger scoop.

> The former OpenSCAD "extended" modes (`cup`, `baseplate_scad`, `lid`) were
> removed on 2026-09-04 (ADR-021, internal-devops): they descended from GPL-3.0
> code and are reserved for clean-room CadQuery re-creation.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

*Gridfinity en B-Rep exacto con CadQuery: un contenedor hueco y una base sobre el estándar publicado de 42 mm / 7 mm, con el perfil de base apilable, orificios opcionales para imanes y una muesca para el dedo.*

Gridfinity was created by **Zack Freedman** (MIT). The CadQuery CORE modes are a
clean-room re-authoring of the open standard's bin + baseplate geometry; the
**Version**: 2.1.0 · **Slug**: `gridfinity`

## Engines

This cartridge runs **two geometry kernels** side by side. The platform now
supports **per-mode engine selection**:

- **Default engine: CadQuery.** The two CORE modes (`bin`, `baseplate`) render as
  watertight **B-Rep** solids and export **STEP** (plus STL / 3MF / GLB / GLTF /
  OBJ). The three-chamfer base profile is built as a loft through
  rounded-rectangle wires — watertight by construction.
- **OpenSCAD side removed 2026-09-04 (ADR-021).** `cup`, `baseplate_scad` and `lid` descended from GPL-3.0 code and are reserved for clean-room CadQuery re-creation.

## Modes

All five modes from the merged manifest. The **engine** column shows which kernel
renders each mode; legacy modes carry an explicit `engine: openscad` override.

| Mode ID | Label (en) | Engine | File |
| :--- | :--- | :--- | :--- |
| `bin` | Bin | **CadQuery** (B-Rep) | `main.py` |
| `baseplate` | Baseplate | **CadQuery** (B-Rep) | `main.py` |

**CadQuery B-Rep modes**

- **Bin** (`bin`) — hollow storage bin: per-cell standardized base, body to
  `grid_z` × 7 mm, optional magnets / finger-scoop / stacking lip.
- **Baseplate** (`baseplate`) — a thin plate whose per-cell sockets are the
  **negative** of the bin base profile, so bins seat in.

## The Gridfinity standard (modelled exactly — CadQuery kernel)

| Quantity | Value |
| :--- | :--- |
| Grid module | **42.0 mm × 42.0 mm** per unit |
| Vertical unit | **7.0 mm** |
| Cell corner radius | **3.75 mm** |
| Base / lip profile (bottom-up) | **0.8 mm** chamfer (45°) → **1.8 mm** straight wall → **2.15 mm** chamfer (45°) |
| Total profile height | **≈ 4.75 mm** |
| Cell body footprint | 41.5 mm (42 − 0.5 mm inter-cell gap) |
| Baseplate socket clearance | 0.25 mm per side |

The three-chamfer base profile is a four-section loft through rounded-rectangle
wires — the geometry that makes bins **seat into baseplates** and **stack** on one
another. The baseplate socket is the same profile grown by the 0.25 mm clearance.

## Parameters

set (parameters are scoped to modes via `modes` / `visible_in_modes`).

### CadQuery B-Rep parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Grid | `target_part` | `bin` | `bin` or `baseplate` (select). |
| Grid | `grid_x` / `grid_y` | 2 / 1 | Units in X / Y (× 42 mm). Range 1–6. |
| Grid | `grid_z` | 3 | Height units (× 7 mm), bin only. Range 1–12. |
| Bin Structure | `wall` | 1.2 mm | Side-wall thickness. Range 0.8–3.0. |
| Bin Structure | `floor_th` | 1.2 mm | Solid floor above the base profile. |
| Bin Structure | `lip_enabled` | on | Top stacking lip. |
| Bin Features | `enable_magnets` | off | 6 mm dia × 2 mm pockets at each cell corner. |
| Bin Features | `finger_scoop` | off | Front access ramp. |
| Baseplate | `bp_thickness` | 5.25 mm | Plate thickness (≥ 4.75 mm socket depth). |

## Presets

**CadQuery**

- **Small Parts Bin (2×1×3)** — bin, magnets + finger-scoop.
- **Deep Bin (2×2×6)** — tall four-cell bin with magnets.
- **Standard Baseplate (2×2)** — the mating plate for the bins above.

## Hyperobject Profile

- **Domain:** household
- **CDG interfaces:**
  - **Gridfinity 42mm Grid** (`grid`) — standard *Gridfinity (42mm module, 7mm
    Z-unit)*, defined by `grid_x`, `grid_y`, `grid_z`. `compatible_with:
    ["multiboard"]`.
  - **Gridfinity Base Profile** (`profile`) — the 0.8 / 1.8 / 2.15 mm chamfer
    stack (~4.75 mm) shared by bin base and baseplate socket (`lip_enabled`,
    `bp_thickness`).
  - **Baseplate Snap Interface** (`snap`) — the bin ↔ baseplate mating socket with
    0.25 mm clearance (`grid_x`, `grid_y`, `bp_thickness`).
  - **6×2 mm Magnet Socket** (`socket`) — 6 mm dia × 2 mm N52 neodymium pockets
    (`enable_magnets`).
- **Societal benefit:** a universal, freely licensed modular storage grid for
  workshops, offices, and homes. One shared 42 mm / 7 mm standard lets bins,
  trays, and baseplates from any maker interoperate — reducing single-use
  organizers and packaging waste while keeping storage repairable and endlessly
  reconfigurable.
- **Commons license:** **CERN-OHL-W-2.0**

## Engine notes

- **CadQuery** modes live in `main.py`. The script is **self-contained**
  (sandbox-safe): parameters are read via a `PARAM(lambda: name, default)` guard
  because the render sandbox does not expose `globals()` / `eval` / `getattr`; the
  base profile is a `cq.Solid.makeLoft` through four rounded-rectangle wires
  (built with `cq.Sketch`), unioned per cell — watertight by construction. The
  final solid is assigned to `result`. A 2×1×3 bin and a 2×2 baseplate render in
  well under 25 s; a 3×3 bin renders in ~20 s. CadQuery modes export **STEP**.
- **OpenSCAD** modes (`cup.scad`, `baseplate.scad`, `lid.scad`) render through the
  legacy OpenSCAD kernel via the per-mode `engine: openscad` override.
- **Export formats:** STL / 3MF / STEP / GLB / GLTF / OBJ.

---
*Consolidated dual-engine README generated from `project.merged.json`.*
