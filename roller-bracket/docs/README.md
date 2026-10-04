# Conveyor / Roller Bracket

A line-side bracket generated with **CadQuery** (B-Rep) that holds a roller axle
or shaft for conveyors and material handling. An upright web carries the shaft
seat — an open-top U-slot for a plain axle or a round pocket sized for a **608
bearing (OD 22 mm)** — above a mounting foot that bolts down, clips to 2020
extrusion, or mounts to a wall.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Roller Bracket** | `bracket` | Single upright with a plain shaft slot + foot. |
| **Bearing Bracket** | `bearing_bracket` | Single upright with a 608 bearing seat pocket. |
| **Bracket Pair** | `bracket_pair` | Two uprights facing each other on one shared base. |
| **2020 Axle Bracket** | `extrusion_bracket` | Single upright with a closed plain bore on a 2020 foot: the axle bracket of an idler (an 8 mm shaft in the bore, a 608 on the shaft beside the web). |

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Shaft Seat | `shaft_dia` | 8 mm | Roller axle / shaft diameter. |
| Shaft Seat | `open_slot` | on | Open the bore to the top for a drop-in axle. |
| Shaft Seat | `bearing_seat` | off | Cut a 22 mm pocket for a 608 bearing (single + pair modes). |
| Web & Foot | `mount_height` | 40 mm | Shaft axis height above the foot. |
| Web & Foot | `web_thick` / `web_width` | 8 / 30 mm | Upright web thickness and width. |
| Web & Foot | `foot_len` / `foot_thick` | 45 / 6 mm | Mounting foot length and thickness. |
| Mounting | `mount` | bolt_down | `bolt_down` / `extrusion` (2020) / `wall` (Roller and Bearing Bracket modes; the 2020 Axle Bracket is always `extrusion`). |
| Mounting | `mount_dia` | 5.5 mm | Mounting screw clearance diameter. |
| Pair | `pair_gap` | 100 mm | Clear span between the two uprights (roller length). |

## Presets

- **8 mm Axle Bracket** — bolt-down, open-top slot.
- **608 Idler Bracket** — a bearing seat for a standard 608 idler.
- **2020 Extrusion Roller** — a tab that drops into 2020 T-slot framing.
- **Conveyor Roller Pair (Ø10, 150)** — two bearing brackets 150 mm apart.
- **608 Idler Axle on 2020** — the 2020 Axle Bracket for an 8 mm idler axle, axis 35 mm
  above the extrusion face.

## On a 2020 extrusion

The `extrusion` mount (and the 2020 Axle Bracket) seats the foot on a 20 × 20 series-5
extrusion: a 5.8 mm key drops into the 6 mm slot opening, only as deep as the slot's
2 mm lips, so the foot's underside rests on the extrusion face and the cavity under the
lips stays free for T-nuts. Two `mount_dia` clearance holes on the slot line, one each
side of the web, take the screws into those T-nuts. Slot dimensions: MISUMI HFS5
"T Slot Dimensions" (6 mm opening, 2 mm lip, 4 mm below the lip),
<https://us.misumi-ec.com/pdf/fa/2012/p2_0513.pdf>. Before 2026-10 the key was 8 mm deep,
deeper than the 6 mm slot, and the four corner holes fell outside the 20 mm extrusion.

## Mating frames (ASM-1)

On the 2020 Axle Bracket (`extrusion_bracket`):

- **`extrusion_bracket_shaft_bore`** — female, `socket`, symmetry 0: the bore's entrance
  on the web's +X face, on the shaft axis (`x = web_thick / 2`, `z = mount_height`), with
  the normal +X out of the bore. At `shaft_dia` 8 its size key is `shaft-8mm`, the
  catalog 8 mm ground shaft (`shaft-8mm.host_end`); at any other diameter it has none.
  The shaft carries the 608 (`shaft-8mm.bearing_journal` ↔ `bearing-608.bore`) on the +X
  side, one washer off the web, and an `idler-608` pulley on the bearing's outer ring.
- **`extrusion_bracket_foot_slot`** — male, `profile`, symmetry 2, `tslot-2020-6mm`: the
  foot's underside at the origin, normal −Z toward the extrusion, `x_axis` +Y along the
  slot (the key and the two screws lie on that line).

Both frames are verified against the rendered part at the defaults and at every preset
(`y4d-spec check --render`).

## Hyperobject Profile

- **Domain:** industrial
- **CDG interfaces:**
  - **Roller Shaft Seat** (`socket`, *608 bearing OD 22 mm / plain shaft bore*) —
    the seat that carries the axle, defined by `shaft_dia`, `open_slot`,
    `bearing_seat`. A 608 pocket matches any standard skate/idler bearing.
  - **Mounting Foot Bolt Pattern** (`bolt_pattern`, internal) — `mount`,
    `mount_dia`, `foot_len`.
  - **2020 Extrusion Tab** (`rail`, *2020 T-slot, 6 mm slot*) — the drop-in tab
    for aluminium framing.
  - **2020 Axle Bracket Shaft Bore** and **Foot on the Slot** — the two framed
    interfaces above.
- **Material awareness:** `tolerance_by_material` is declared so the bearing/axle
  fit can be tuned per material and printer.
- **Societal benefit:** line-side roller support for DIY conveyors — one bracket
  family seats a plain axle or a 608 bearing and mounts three ways, so small shops
  build moving lines without proprietary hardware.
- **License:** CERN-OHL-W-2.0

## Engine notes

- Engine: **CadQuery** (`main.py`). Exports STL / 3MF / STEP / GLB / GLTF / OBJ.
- The script is **self-contained** (sandbox-safe): parameters are read via a
  `PARAM(lambda: name, default)` guard because the render sandbox does not expose
  `globals()` / `eval`. The final solid is assigned to `result`. `target_part`
  dispatches which mode part is built.
- All shipped presets and defaults render **watertight**.
