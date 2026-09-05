# Involute Gears

Dual-kernel involute gears: exact **CadQuery B-Rep** modes (spur, helical,
internal ring, linear rack) plus the original **OpenSCAD** spur & herringbone
modes. Any two gears sharing the same **module** and **pressure angle** mesh
correctly at their theoretical centre distance.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

*Engranajes de involuta con doble kernel: modos exactos en CadQuery B-Rep
(recto, helicoidal, corona interna, cremallera lineal) más los modos originales
OpenSCAD de engranaje recto y de espiga. Dos engranajes con el mismo módulo y
ángulo de presión engranan correctamente.*

**Version**: 2.1.0 · **Slug**: `gears`

## Engines

This cartridge runs **two geometry kernels** side by side. The platform now
supports **per-mode engine selection**:

- **Default engine: CadQuery.** The four modern modes (`spur`, `helical`,
  `ring`, `rack`) render as watertight **B-Rep** solids and export **STEP** (plus
  STL / 3MF / GLB / GLTF / OBJ). The tooth flank is sampled directly from the
  true involute of the base circle — not a faceted CSG approximation — so meshing
  geometry is dimensionally *real*.
- **Legacy engine: OpenSCAD.** The two original modes (`spur_gear`,
  `herringbone_gear`) carry an explicit per-mode `engine: openscad` override and
  continue to run through their original `.scad` sources.

## Modes

All six modes from the merged manifest. The **engine** column shows which kernel
renders each mode; legacy modes carry an explicit `engine: openscad` override.

| Mode ID | Label (en) | Engine | File |
| :--- | :--- | :--- | :--- |
| `spur` | Spur Gear | **CadQuery** (B-Rep) | `main.py` |
| `helical` | Helical Gear | **CadQuery** (B-Rep) | `main.py` |
| `ring` | Ring (Internal) Gear | **CadQuery** (B-Rep) | `main.py` |
| `rack` | Rack (Linear) | **CadQuery** (B-Rep) | `main.py` |
| `spur_gear` | Spur Gear | **OpenSCAD** | `spur_gear.scad` |
| `herringbone_gear` | Herringbone Gear | **OpenSCAD** | `herringbone_gear.scad` |

**CadQuery B-Rep modes**

- **Spur Gear** (`spur`) — external involute spur gear (helix = 0). The default.
- **Helical Gear** (`helical`) — same tooth, twist-extruded along the face width
  via a helix angle.
- **Ring (Internal) Gear** (`ring`) — annular gear with teeth pointing inward
  inside a rim (planetary / annulus).
- **Rack (Linear)** (`rack`) — the gear's conjugate: straight-flanked teeth on a
  bar (rack-and-pinion).

**OpenSCAD legacy modes**

- **Spur Gear** (`spur_gear`) — involute spur gear (ISO 53 / DIN 867 profile).
- **Herringbone Gear** (`herringbone_gear`) — double-helical (V-tooth) gear that
  cancels axial thrust.

## Parameters

CadQuery and OpenSCAD modes each read their own parameter set (parameters are
scoped to modes via `modes` / `visible_in_modes`).

### CadQuery B-Rep parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Tooth Geometry | `m` (module) | 2 mm | Pitch dia = `m × teeth`. Must match to mesh. Range 0.5–6. |
| Tooth Geometry | `teeth` | 20 | Tooth count; sets the gear ratio. Range 6–120. |
| Tooth Geometry | `pressure_angle` | 20° | 14.5° / 20° / 25° (select). Must match to mesh. |
| Tooth Geometry | `helix` | 0° | 0 = spur; > 0 twists the extrusion (helical). Range 0–45. |
| Body & Bore | `thickness` | 8 mm | Face width (extrusion depth). Range 2–40. |
| Body & Bore | `bore` | 6 mm | Central shaft bore; 0 = solid. On the rack, a lengthwise mounting hole. |
| Hub & Set-Screw | `hub_enabled` / `hub_diameter` / `hub_height` | off / 16 / 6 | Optional raised boss around the bore (spur, helical). |
| Hub & Set-Screw | `setscrew` / `setscrew_dia` | off / 3 mm | Optional radial grub-screw hole into the bore (spur, helical). |
| Ring / Rack | `rim_width` | 6 mm | Ring: solid material outside the internal roots. |
| Ring / Rack | `rack_teeth` / `rack_height` | 12 / 10 mm | Rack length = `rack_teeth × π × m`; back thickness. |
| Quality | `flank_pts` | 9 | Involute samples per flank (facet control). |

### OpenSCAD-extended parameters

The two legacy modes add their own parameters (they do not share the CadQuery
set above). By group:

- **Gear Geometry** (`gear_geometry`) — `teeth_count` (8–80), `module_size`
  (0.5–5), `helical_angle` (10–60°, herringbone only).
- **Bore** (`bore`) — `bore_diameter` (0–20 mm).
- **Quality** (`quality`) — `fn` — OpenSCAD `$fn` curve resolution (0 = default 32).

## Presets

**CadQuery**

- **Small Motor Pinion (20T)** — spur, m1.5, 20T, hub + M3 set-screw on a 3 mm shaft.
- **Quiet Drive Gear (60T helical)** — helical, m2, 60T, 20° helix, 8 mm bore.
- **Rack (module 2)** — 16-tooth rack to pair with an m2 pinion.

**OpenSCAD**

- **Small Motor (20T)** — spur_gear, 20T, module 1.5, 3 mm bore.
- **Large Drive (60T)** — spur_gear, 60T, module 2, 8 mm bore.
- **Gear Pair 5:1 (50T)** — spur_gear, 50T, module 1, 5 mm bore.

## The involute, briefly (CadQuery kernel)

For a gear of module `m`, tooth count `z`, pressure angle `α`:

- pitch radius `rp = m·z/2`
- base radius `rb = rp·cos α`
- addendum `= m` → outer radius `ro = rp + m`
- dedendum `= 1.25·m` → root radius `rr = rp − 1.25·m`

Each flank is the involute of the base circle, `P(t) = rb·(cos t + t·sin t,
sin t − t·cos t)`, sampled from the root up to `ro`, then rotated so the pitch
point lands half a circular-tooth-thickness off the centreline
(`β₀ = π/(2z) + inv α`, `inv α = tan α − α`), giving a pitch tooth thickness of
exactly `π·m/2`. One tooth is polar-patterned `z` times and extruded — or
**twist-extruded** for a helix. The **base pitch** `π·m·cos α` is the invariant
two gears must share to mesh; it falls out of matching module and pressure angle.

## Hyperobject Profile

- **Domain:** industrial
- **CDG interfaces:**
  - **Involute Gear Tooth** (`spline`, **ISO 53 / DIN 867 (20° involute)**) —
    defined by `m`, `teeth`, `pressure_angle`, `helix`. Mesh compatibility rule:
    two gears interoperate when they share the **same module and pressure
    angle** (and, for parallel-axis helical meshing, equal-and-opposite helix).
    Declared `compatible_with: ["gears"]` — the cartridge meshes with itself
    across tooth counts.
  - **Shaft Bore Interface** (`socket`, **ISO 286**) — `bore`, `setscrew`,
    `setscrew_dia`; the mounting interface to the shaft.
- **Material awareness:** `tolerance_by_material` is declared — bore and
  set-screw clearances are the print-fit knobs to tune per material / printer.
- **Societal benefit:** correct involute gearing underlies every mechanism, but
  stock gears rarely match a needed module + tooth count + bore. Mesh-accurate,
  on-demand gears let makers repair machines and build transmissions without
  tooling or lead time.
- **Commons license:** **CERN-OHL-W-2.0**

## Engine notes

- **CadQuery** modes live in `main.py`. The script is **self-contained**
  (sandbox-safe): `cq` and `math` are injected globals, parameters are read via a
  `PARAM(lambda: name, default)` guard because the render sandbox does not expose
  `globals()` / `eval`, and every helper is inlined. The final solid is assigned
  to `result`. Spur, helical, ring, rack, hub + set-screw, and extreme cases
  (6-tooth, 45° helix) all export **watertight**, and export **STEP**.
- **OpenSCAD** modes (`spur_gear.scad`, `herringbone_gear.scad`) render through
  the legacy OpenSCAD kernel via the per-mode `engine: openscad` override.
- **Export formats:** STL / 3MF / STEP / GLB / GLTF / OBJ.

---
*Consolidated dual-engine README generated from `project.merged.json`.*
