# FPV Camera Cage

**Protects and angles a micro FPV camera**, generated with **CadQuery** (B-Rep).
The camera drops into a cradle pocket sized to the standard form factor
(**nano 14 mm, micro 19 mm, mini 21 mm**) and the whole housing tilts to a chosen
up-angle, with tabs that bolt to the frame side plates.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Protective Cage** | `cage` | Full shell + a front rim frame and diagonal guard strut that shield the lens on impacts. |
| **Tilt Bracket** | `tilt_mount` | The shell only (open front) on the tilting mount — lighter, still cradles the cam. |
| **Naked Mount** | `naked_mount` | A thin backing plate with the lens aperture and board-mount holes for a "naked"/board cam. |

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Camera | `cam_size` | micro | Form factor: `nano` 14, `micro` 19, `mini` 21 mm. |
| Camera | `tilt` | 30° | Up-tilt angle (higher = faster flight). |
| Camera | `lens_hole` | on | Cut a rear lens/focus aperture. |
| Housing | `wall` | 2.0 mm | Cradle wall thickness. |
| Housing | `cam_clear` | 0.4 mm | Per-side clearance around the cam. |
| Frame Mount | `base_h` | 6.0 mm | Mount base height below the cradle. |
| Frame Mount | `mount_width` | 19 mm | Spacing between the frame-plate tabs. |
| Frame Mount | `tab_thick` / `tab_hole_d` | 3.0 / 2.2 mm | Tab thickness and bolt hole (M2). |

## Interfaces

The cradle pocket is derived directly from `cam_size` (plus `cam_clear` per side
and `wall`), so a housing generated for a *micro* cam accepts a 19 mm micro cam.
The two side tabs form the frame-mount bolt interface at `mount_width` spacing.
The whole housing is rotated up by `tilt` about the pitch axis before it is
joined to the base, exactly like a real cam mount.

## Presets

- **Micro Cage 30°** — the common freestyle setup.
- **Nano Tilt 40°** — light racing bracket for a nano cam.
- **Mini Naked 20°** — flat board-cam mount for a mini sensor.

## Hyperobject Profile

- **Domain:** commercial
- **CDG interfaces:**
  - **FPV Camera Cradle** (`pocket`, *FPV micro/nano cam — nano 14 / micro 19 /
    mini 21 mm*) — the cradle pocket, defined by `cam_size`, `cam_clear`, `wall`.
    Any camera of the selected form factor drops in.
  - **Frame Mount Tabs** (`bolt_pattern`, *internal*) — the two side tabs and
    bolt holes, defined by `mount_width`, `tab_thick`, `tab_hole_d`.
  - **Mating frames (ASM-1 v1.1):** `cage_cradle_floor` and
    `tilt_mount_cradle_floor` — the pocket floor (the closed wall with the lens
    aperture), normal toward the open side, tilted with the housing (`let`:
    camera width from `cam_size`, pocket depth, clamped tilt; degree trig).
    Female, symmetry 4, size key from `cam_size` (`fpv-camera-nano-14mm`,
    `fpv-camera-micro-19mm`, `fpv-camera-mini-21mm`). The housing tilts its open
    side DOWN and its floor's aperture UP, so the camera that looks up through the
    aperture seats here by its **front (lens) face** — the catalog camera's
    `front_face`. Needs hyperobjects-spec ≥ 0.4.0 with the FPV camera-chain keys.
  - **Not framed: the frame-mount tabs.** At every preset the housing is wider
    than a 19–20 mm side-plate camera bay (micro: 19 + 2·0.4 + 2·2 = 23.8 mm),
    and the tabs' outer faces stand `max(mount_width, out_w) + 2·tab_thick`
    apart (29.8 mm at the defaults), so `mount_width` never governs the spacing
    at any preset. Neither tab face can meet a side plate, so no tab frame is
    claimed until the mount itself is redesigned.
- **Material awareness:** `tolerance_by_material` is declared — the cam clearance
  and wall are exposed so the pocket fit can be tuned per material/printer.
- **Societal benefit:** the camera is the most-crashed and most-swapped part on
  an FPV craft; on-demand cages sized to the exact cam and tilt keep the picture
  level and the lens protected.
- **License:** CERN-OHL-W-2.0

## Engine notes

- Engine: **CadQuery** (`main.py`). Exports STL / 3MF / STEP / GLB / GLTF / OBJ.
- Self-contained (sandbox-safe): parameters read via `PARAM(lambda: name,
  default)`; `target_part` dispatches which part to build; the final solid is
  assigned to `result`. Base fillets are clamped and guarded. All modes render
  **watertight** in well under 20 s.
