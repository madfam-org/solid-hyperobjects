# Cord Cut Jig

Two blocks that screw to a bench and cut cord, rope, cable or soft tube to the
same length every time, generated with **CadQuery** (B-Rep): one holds the
end, the other guides the blade.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the bench decides

The length is not a parameter. It is the distance on the bench from the axis
of the peg to the blade slot of the cut block, measured once with a tape when
the two are screwed down. Both parts mark that point: the peg stands on the
origin of its plate, and the slot is the mid-plane of the block.

What the cartridge does set is the cord: `cord_d` sizes the channel the cord
lies in, three quarters of its diameter deep and half a millimetre wider, so
the cord cannot roll while the blade comes down. The slot runs 2 mm deeper
than the channel, so the blade passes right through.

A cord that stretches has to be cut under the same pull every time: hang the
end on the peg, draw the cord taut by hand along the channel, and cut. A piece
that will carry an end loop is cut longer than its finished length by what the
loop takes; find that figure on a trial piece.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Anchor Peg** | `anchor_peg` | A plate with a round peg and a screw hole on each side of it. The end loop, knot or fitting hooks over the peg. |
| **Cut Block** | `cut_block` | A block with the cord channel along its top, the blade slot across it, and two screw holes on a diagonal. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `cord_d` | 1–16 mm | Diameter of what is being cut |
| `screw_d` | 3–6.5 mm | Clearance holes for the bench screws |
| `base_t`, `base_l`, `base_w` | 6–30 mm, 40–160 mm, 20–100 mm | The anchor's plate |
| `peg_d`, `peg_h` | 4–25 mm, 8–80 mm | The peg |
| `block_l`, `block_w`, `block_h` | 40–150 mm, 40–120 mm, 12–60 mm | The cut block |
| `blade_w` | 0.4–4 mm | Width of the blade slot: the blade plus a little |

## Constraints

- The anchor's plate is long enough for the peg and a screw on each side, and
  wider than both.
- The cut block is wide enough for the channel and a screw on each side, tall
  enough to keep 4 mm of solid under the slot, and long enough for its screws.
- A peg shorter than its own diameter is flagged: a loop rides off it.

## Making it

Both parts print as they stand, without supports. For a hot knife, make the
cut block from hardwood or aluminium instead: a printed slot softens. Screw
both to a board rather than to the bench itself if the length changes often,
and write the length on the board.

This is a workshop aid, not a guard. The slot keeps the blade square and away
from the hand that holds the cord, but a knife is still a knife.

## Interfaces

- **Bench faces** (`peg_bench_face`, `block_bench_face`): the underside of
  each part.
- **Anchor peg** (`peg`): the peg, on the origin of its plate.
- **Cord channel and blade slot** (`cord_channel`): `cord_d`, `blade_w`,
  `block_h`. No frame is declared: it is a guide, not a mate.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
