# V-Belt / Round-Belt Pulley

A parametric friction-drive pulley (sheave) generated with **CadQuery** (B-Rep),
for A-section V-belts or for round belts and O-rings, plus an idler sheave for
rope, cord or cable. The rim carries one or more grooves cut as bodies of
revolution about the pulley axis.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## Groove geometry

- **V-Belt A / 13 mm** — a ~40° included-angle V-groove (ISO 4183 A / SPZ
  family), ~13 mm wide at the rim. The belt wedges into the V and drives by
  friction on the flanks. Built as the union of two coaxial cones so the channel
  is exactly a revolved triangle. The top width is auto-clamped to what the
  included angle and depth allow.
- **Round belt / O-ring** — a semicircular groove built as a torus of the belt
  radius centred on the rim circle.
- **Rope throat** — a deep groove for a rope, cord or cable. The bottom is an arc
  of radius 0.53 × `rope_dia`, slightly wider than the rope, so the rope is
  cradled and not pinched. Two straight flanks leave the arc on tangents at
  `throat_angle` and rise 1.25 × `rope_dia` above the tread, so the rope sits
  below the rim. It is one revolved profile.

## Sizing a rope sheave

A rope sheave is sized by its **tread diameter**, the diameter at the bottom of
the throat where the rope sits, because that is what bends the rope:

```
bend ratio = tread_dia ÷ rope_dia        rim diameter = tread_dia + 2.5 × rope_dia
```

A larger ratio is kinder to the rope. The manifest warns under 8; the real
minimum belongs to the rope's maker and its construction (wire rope and
high-modulus synthetic rope want far more than a braided cord). The rim diameter
is derived, and it is the number a guard or a block around the sheave has to
clear. The sheave is an idler: it has a plain bore for a bearing, a bushing or
an axle, and no hub. It is a geometry family, not a rated component.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **V-Belt** | `vbelt` | A single A-section V-groove sheave. |
| **Round Belt** | `roundbelt` | A single semicircular groove for a round belt / O-ring. |
| **Multi-Groove** | `multi_groove` | A stacked sheave with `grooves` parallel V-grooves. |
| **Rope Sheave** | `rope_sheave` | An idler sheave with one rope throat and a plain bore. |

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Belt & Groove | `belt_profile` | A/13 | V-belt or round-belt groove. |
| Belt & Groove | `outer_dia` | 60 mm | Rim outer diameter. |
| Belt & Groove | `groove_angle` | 40° | V included angle. |
| Belt & Groove | `groove_width` / `groove_depth` | 13 / 11 mm | V top width / radial depth. |
| Belt & Groove | `belt_dia` | 5 mm | Round-belt / O-ring cross-section. |
| Multi-Groove | `grooves` / `groove_pitch` | 2 / 15 mm | Groove count / spacing. |
| Rope & Throat | `tread_dia` | 80 mm | Rope sheave: diameter at the bottom of the throat. |
| Rope & Throat | `rope_dia` | 5 mm | Rope sheave: rope, cord or cable diameter. |
| Rope & Throat | `throat_angle` | 45° | Rope sheave: included angle between the flanks. |
| Body & Bore | `bore` | 8 mm | Shaft hole. On a rope sheave it stays 4 mm under the throat. |
| Hub & Set Screw | `hub` / `hub_dia` / `hub_height` | on / 22 / 8 mm | Set-screw hub. |
| Hub & Set Screw | `setscrew` / `setscrew_dia` | on / 4.2 mm | Radial M4 set screw. |

## Presets

- **A-Section Ø60 · 8 mm bore** — a general-purpose V-belt sheave.
- **O-Ring Drive Ø40 (5 mm belt)** — a light round-belt drive.
- **Twin-Groove Sheave Ø80** — a two-groove V-belt sheave.
- **Rope Sheave · 5 mm rope · Ø80 tread · 22 mm bore** — a 16:1 idler; the bore
  takes a 22 mm bearing or bushing.
- **Cord Sheave · 3 mm cord · Ø40 tread · 8 mm bore** — a small idler on an 8 mm
  axle.

## Hyperobject Profile

- **Domain:** industrial
- **CDG interfaces:**
  - **V-Belt Groove** (`profile`, ISO 4183 A/SPZ) — the friction interface,
    defined by `belt_profile`, `groove_angle`, `groove_width`, `groove_depth`,
    `outer_dia`.
  - **Round-Belt / O-Ring Groove** (`profile`, internal) — `belt_dia`,
    `outer_dia`.
  - **Rope Throat** (`profile`, internal) — `rope_dia`, `tread_dia`,
    `throat_angle`.
  - **Shaft Bore & Set Screw** (`socket`, internal) — `bore`, `setscrew`,
    `setscrew_dia`.
- **Material awareness:** `tolerance_by_material` is declared; the round-belt
  groove and bore carry a small print clearance.
- **Societal benefit:** printable sheaves let a maker set a drive ratio or
  replace a cracked pulley without sourcing a proprietary casting.
- **License:** CERN-OHL-W-2.0

## Engine notes

- Engine: **CadQuery** (`main.py`). Exports STL / 3MF / STEP / GLB / GLTF / OBJ.
- The script is **self-contained** (sandbox-safe): parameters are read via a
  `PARAM(lambda: name, default)` guard because the render sandbox does not expose
  `globals()` / `eval`. The final solid is assigned to `result`.
- All shipped presets and defaults render **watertight**.
