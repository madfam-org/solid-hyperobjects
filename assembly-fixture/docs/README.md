# Assembly / Welding Fixture

A positioning aid generated with **CadQuery** (B-Rep) that holds parts in a
repeatable location during assembly, welding, gluing, or drilling. A base plate
carries locating pins (in a selectable pattern), optional raised stops forming a
corner reference, or a V-groove for round stock — plus mounting holes to bolt the
fixture to a bench.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Pin Plate** | `pin_plate` | Base plate + array of locating pins (corners / grid / linear). |
| **Stop Fixture** | `stop_fixture` | Base plate + two perpendicular edge fences forming an L / corner reference. |
| **V-Block** | `v_block` | A block with a V-groove that cradles round stock. |
| **Saddle** | `saddle` | A channel between two cheeks that nests rectangular stock: a tube, a bar or a post. Two saddles screwed to a bar hold two posts parallel at a set distance while they are fastened. |

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Base Plate | `base_w` / `base_d` / `base_t` | 120 / 90 / 10 mm | Plate width / depth / thickness. |
| Locating Pins | `pin_pattern` | corners | `corners` / `grid` / `linear`. |
| Locating Pins | `pin_dia` / `pin_height` | 8 / 18 mm | Pin diameter and height. |
| Locating Pins | `grid_cols` / `grid_rows` | 3 / 2 | Grid pattern layout. |
| Locating Pins | `pin_count` | 4 | Linear pattern count. |
| Stops & Fences | `stop_h` / `stop_t` | 15 / 8 mm | Fence height and thickness. |
| V-Groove | `v_angle` / `v_stock_dia` | 90° / 25 mm | Included angle and nominal round-stock diameter. |
| Mounting | `mount_dia` / `mount_inset` | 6.5 / 10 mm | Bolt-down hole size and edge inset. |
| Saddle | `saddle_stock_w` / `saddle_clear` | 50 / 0.3 mm | Outside width of the rectangular stock, and clearance per side. |
| Saddle | `cheek_h` / `cheek_t` | 25 / 8 mm | Height and thickness of the two cheeks. |
| Saddle | `saddle_len` / `saddle_flange` | 60 / 20 mm | Length along the stock, and base reach beside each cheek (the mounting holes sit in it). |

The Saddle has its own size parameters and reads `base_t`, `mount_holes` and
`mount_dia` only: it is as wide as the stock, its cheeks and its flanges make it.

## Presets

- **Corner Locator Plate** — 120×90 plate, four corner pins.
- **Grid Locating Bed (4×3)** — 200×150 bed with a 4×3 pin grid.
- **Welding Corner Jig** — 150×150 with tall corner fences.
- **Pipe V-Block (Ø25)** — a V-block for Ø25 round stock.
- **Saddle for 50 mm Square Tube** — a 60 mm long saddle with 25 mm cheeks.
- **Saddle for 80 mm Square Tube** — an 80 mm long saddle with 40 mm cheeks.

## Hyperobject Profile

- **Domain:** industrial
- **CDG interfaces:**
  - **Locator Pin Pattern** (`bolt_pattern`, internal) — the array of locating
    pins, defined by `pin_pattern`, `pin_dia`, `pin_inset`, `grid_cols`,
    `grid_rows`, `pin_count`. Any part drilled to the same pin pattern registers
    on the fixture.
  - **Bench Mounting Pattern** (`bolt_pattern`, internal) — `mount_dia`,
    `mount_inset`; a repeatable four-corner bolt-down.
  - **Round-Stock V-Seat** (`profile`, internal) — `v_angle`, `v_stock_dia`.
  - **Rectangular-Stock Seat** (`pocket`) — the floor of the Saddle's channel,
    with a mating frame; it carries the size key `square-tube-80mm` when
    `saddle_stock_w` is 80.
  - **Saddle Mounting Holes** (`bolt_pattern`, internal) — the underside of the
    Saddle, with a mating frame.
- **Material awareness:** `tolerance_by_material` is declared so pin/stop fits can
  be tuned per material and printer.
- **Societal benefit:** repeatable workholding for makers and small shops —
  locate, clamp, and reproduce part positions without buying dedicated tooling.
- **License:** CERN-OHL-W-2.0

## Engine notes

- Engine: **CadQuery** (`main.py`). Exports STL / 3MF / STEP / GLB / GLTF / OBJ.
- The script is **self-contained** (sandbox-safe): parameters are read via a
  `PARAM(lambda: name, default)` guard because the render sandbox does not expose
  `globals()` / `eval`. The final solid is assigned to `result`. `target_part`
  dispatches which mode part is built.
- All shipped presets and defaults render **watertight**.
