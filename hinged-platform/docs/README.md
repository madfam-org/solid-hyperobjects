# Hinged Platform

A load-bearing panel that folds on a pin along one edge, and the block it
turns on, generated with **CadQuery** (B-Rep): a fold-down platform, a step, a
bench seat, a table leaf, a ramp or a tailgate.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the hinge line decides

Both parts are drawn about the same line: the hinge axis. Three numbers on it
are shared, and the two parts fit because they read the same three.

- **`panel_t` is also the barrel.** The hinge edge of the panel is rounded to
  half its thickness about the pin, and the barrel of each block has the same
  radius. Open, the top of the panel and the top of the barrels are one
  surface with no step to trip on.
- **`pin_d` is the pin.** Every bore is made 0.4 mm larger so the panel turns.
- **`block_w` is the notch.** The panel is cut away where each block sits,
  `side_gap` wider on each side, and deep enough for the barrel to turn in.

The panel folds from flat to vertical: 90 degrees. Open, it rests on the
**skid** under its free edge, which is as high as the hinge axis stands above
the floor less half the panel thickness; set `skid_h` to that figure and the
panel lies level.

## The fold lock

With `lock` on, a second, smaller hole runs parallel to the pin, midway
between the pin bore and the surface of the barrel. In the panel it enters
from the side edge and runs to the first block; in each block it passes
through the barrel above the pin. The two line up only when the panel stands
at 90 degrees. A pull pin pushed in from the side then holds the panel
folded, and pulling it lets the panel down.

The lock pin is small because it has to fit inside the barrel. It keeps a
folded panel from falling open; it is not what carries the panel in use.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Panel** | `panel` | The platform: rounded hinge edge, a notch per block, the pin bore across its width, and a skid under the free edge. |
| **Hinge Block** | `hinge_block` | One fixed block: a barrel on a flange that bolts down behind the hinge line. Make one per notch. |

Both parts are drawn in the same frame, so a block placed at a notch centre
sits in the panel as modelled.

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `panel_t` | 12–60 mm | Panel thickness and barrel diameter |
| `pin_d` | 4–16 mm | Hinge pin |
| `block_w` | 20–120 mm | Width of each block along the pin |
| `lock`, `lock_d` | on / off, 3–8 mm | The fold lock and its pin |
| `panel_w`, `panel_l` | 150–1200 mm, 150–1500 mm | Width along the hinge, and length from the axis to the free edge |
| `blocks`, `block_inset` | 2–4, 30–400 mm | Number of blocks, and the distance from each side edge to the nearest one |
| `side_gap` | 0.3–3 mm | Clearance between a block and each wall of its notch |
| `skid_h`, `skid_d` | 0–150 mm, 15–120 mm | The skid under the free edge (0 leaves the underside flat) |
| `axis_h` | 10–120 mm | Height of the hinge axis above the face the block is bolted to |
| `flange_l`, `flange_t`, `bolt_d` | 20–150 mm, 4–20 mm, 3.4–12.5 mm | The block's flange and its bolt holes |

## Constraints

- The panel keeps 3 mm of material round the pin.
- With the lock on, the lock hole fits between the pin and the barrel surface.
- The outer notches keep 12 mm of panel to the side edge, and all notches
  keep 20 mm between them.
- The panel is long enough for its skid and its hinge edge.
- The axis stands 4 mm above the flange, and the flange reaches far enough
  behind the barrel for its bolts.
- A lock on a block set more than 150 mm in from the edge is flagged: the
  lock pin has to be that long.

## Making it

The panel is a board: plywood or a composite sheet with the hinge edge rounded
over, the notches cut, and the pin bore drilled through the knuckles (drill it
before cutting the notches, from both edges, so it runs true). A flat panel
with a metal or printed hinge strip glued to its edge gives the same shape.
The blocks print lying on a side, or are milled from bar.

This cartridge is a geometry family, not a rated platform. A panel that
carries a person is a structure: its span, the board, the pin, the blocks and
their bolts decide what it holds, and a folding edge is a place where a hand
can be caught. Whoever builds and uses it has to establish that it is strong
enough and guard the gap at the hinge.

## Interfaces

- **Panel hinge bore** (`panel_hinge`) and **block hinge bore**
  (`block_hinge`): the pin bore, an 8 mm ground shaft when `pin_d` is 8.
- **Deck face** (`deck_face`): the top of the panel.
- **Block flange bolts** (`block_mount`): the underside of the block at the
  centre of its bolt pair (mid-way along the flange, behind the barrel), so a
  seat framed on its own hole pair puts the holes in line. Its
  size key follows `bolt_d`: an M5 screw joint at 5.5, M6 at 6.5 (the default),
  M8 at 8.5.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
