# Parametric Vise Soft Jaw

Custom CNC **soft jaws** for Kurt-style and machine vises — a **dual-kernel**
hyperobject that renders on **CadQuery (B-Rep)** by default and keeps its original
**OpenSCAD** mode. A soft jaw is a machinable/printable insert that bolts into the
vise on a standard jaw bolt pattern and is pocketed to cradle a specific
workpiece.

*Mordazas blandas CNC personalizadas para tornillos tipo Kurt y de máquina — un
hiperobjeto de **doble núcleo** que renderiza en **CadQuery (B-Rep)** por defecto
y conserva su modo **OpenSCAD** original. Un inserto mecanizable/imprimible que se
atornilla al tornillo con un patrón de pernos estándar y se cajea para sujetar una
pieza específica.*

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

**Version**: 2.1.0 · **Slug**: `soft-jaw`

## Modes

The default kernel is **CadQuery (B-Rep)**; the legacy `jaw_body` mode carries an
explicit `engine: openscad` and renders on OpenSCAD.

| Mode id | Label (en) | Engine | File |
| :--- | :--- | :--- | :--- |
| `jaw` | Soft Jaw | CadQuery B-Rep | `main.py` |
| `jaw_pair` | Jaw Pair | CadQuery B-Rep | `main.py` |
| `vee_jaw` | V-Groove Jaw | CadQuery B-Rep | `main.py` |
| `jaw_body` | Soft Jaw (OpenSCAD) | OpenSCAD | `soft_jaw.scad` |

**CadQuery modes** — `jaw`, `jaw_pair`, `vee_jaw`:

- **Soft Jaw** (`jaw`) — a single jaw block: vise bolt holes, gripping face,
  optional round/rect workpiece pocket, optional magnet pockets.
- **Jaw Pair** (`jaw_pair`) — a matching left + right jaw set. The workpiece
  negative is split across both jaws so the closed vise cradles the part — the way
  soft jaws are cut in pairs.
- **V-Groove Jaw** (`vee_jaw`) — a jaw with a V-groove down the face to hold round
  stock (bar / pipe) for cross-drilling or milling a flat.

**OpenSCAD mode** — `jaw_body`: the original single `jaw_body` soft jaw from
`soft_jaw.scad`, driven by the legacy parameter set.

The mode's part id **is** the `target_part` the CadQuery script dispatches on, so
each mode renders its own distinct geometry.

## Parameters

### CadQuery parameters (main modes)

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Vise Compatibility | `vise_model` | Kurt DX6 (6") | Sets the mounting bolt pattern (Kurt / Orange / Tormach). |
| Dimensions | `jaw_width` | 6.0 in | Width across the vise (X). |
| Dimensions | `jaw_height` | 1.735 in | Face height (Z). |
| Dimensions | `jaw_thickness` | 0.75 in | Depth from vise to face (Y). |
| Workpiece Pocket | `workpiece` | none | none / round / rect negative cut into the face. |
| Workpiece Pocket | `workpiece_dia` | 25 mm | Round-stock diameter. |
| Workpiece Pocket | `workpiece_w` / `workpiece_h` | 40 / 20 mm | Rectangular pocket size. |
| Workpiece Pocket | `pocket_depth` | 10 mm | How deep the pocket cuts (Y). |
| Face & Features | `face_pattern` | smooth | smooth / serrations / grid gripping face. |
| Face & Features | `serration_pitch` | 2.5 mm | Groove spacing for serrations/grid. |
| Face & Features | `vee_angle` | 90° | Included V-groove angle (V-Groove Jaw). |
| Face & Features | `magnet_pockets` | on | 10×3 mm magnet pockets on the back face. |
| Face & Features | `pair_gap` | 30 mm | Display gap between the two jaws (Jaw Pair, visual only). |

Dimensions are entered in **inches** (the shop convention for vises); pockets,
magnets and serrations are in **mm**. Internally everything is converted to mm.

### OpenSCAD-extended parameters

The legacy `jaw_body` (OpenSCAD) mode adds its own parameters by group — notably a
**Quality** group with `fn` ($fn) — plus its own reading of the shared
`vise_model` / `jaw_width` / `jaw_height` / `jaw_thickness` / `face_pattern` /
`magnet_pockets` controls. Only `jaw_body` exposes these legacy rows.

## Presets

- **Kurt DX6 Smooth (Mar-free)** — a plain 6" jaw for finished parts (`jaw`).
- **Kurt DX6 Round-Stock Pair** — a serrated pair with a 25 mm round pocket (`jaw_pair`).
- **Tormach 5" V-Block** — a V-groove jaw for round stock on a 5" vise (`vee_jaw`).
- Legacy OpenSCAD presets — **Kurt DX6 Prismatic (Round Stock)**, **Kurt DX6
  Smooth (Mar-free)**, **Orange Vise 6" Grid** — target the `jaw_body` mode.

## Hyperobject Profile

- **Domain:** industrial
- **CDG interfaces:**
  - **Vise Jaw Mount** (`bolt_pattern`, *Kurt-style vise bolt pattern*) — two
    counterbored SHCS through the jaw thickness at the standard span for the
    selected vise (`vise_model`, `jaw_width`, `jaw_thickness`). This is what makes
    the jaw bolt onto a real vise; any jaw generated for a given vise shares the
    pattern.
  - **Workpiece Pocket** (`pocket`, internal) — the negative the part sits in,
    defined by `workpiece`, `workpiece_dia`, `workpiece_w`, `workpiece_h`,
    `pocket_depth`. In **Jaw Pair** the pocket is split across both jaws.
- **Material awareness:** `shrinkage_compensation` and `tolerance_by_material`
  are declared — the pocket/clearance can be tuned so a printed or cut jaw grips
  the nominal part correctly across materials.
- **Societal benefit:** local machine shops can tool up for a new job in minutes
  with a workpiece-specific jaw cut on-demand, on a bolt pattern that fits the
  vises already on the bench.
- **License:** CERN-OHL-W-2.0

## Engines

- **Default engine: CadQuery (B-Rep).** `jaw`, `jaw_pair`, and `vee_jaw` render
  on CadQuery; every shipped preset and default renders **watertight** and exports
  **STEP** (alongside STL / 3MF / GLB / GLTF / OBJ).
- **Legacy engine: OpenSCAD.** The `jaw_body` mode carries an explicit per-mode
  `engine: openscad` and renders `soft_jaw.scad` through the OpenSCAD kernel,
  preserving the original soft jaw exactly.
- The CadQuery script is **self-contained** (sandbox-safe): parameters are read via
  a `PARAM(lambda: name, default)` guard because the render sandbox does not expose
  `globals()` / `eval`. The final solid is assigned to `result`, and the active
  part is chosen by the `target_part` global.
- The top-front lead-in chamfer is applied to the **clean blank** before any face
  grooves or pockets are cut — chamfering an already-serrated edge can crash the
  OCCT kernel, so it is done on the pristine box.
