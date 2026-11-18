# Pull Handle

The part of a cable or a cord that a hand holds, generated with **CadQuery**
(B-Rep): a grip the cord passes through, and a bar for two hands.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the grip decides

A handle fits a hand or it does not, and three numbers decide it.

- **`grip_d` is what the hand closes round.** A hand holds hardest on a grip
  it can close with the fingertips near the palm. One that is too thick opens
  the fingers and tires them; one that is too thin digs in. Try a tube or a
  dowel of the candidate diameter in the hand that will use it. The manifest
  flags anything over 40 mm.
- **`grip_l` is the hand's width plus room.** Measure across the knuckles of
  the hand, with its glove on if it wears one, and add room to move.
- **The flanges keep the hand on.** A flange `flange_h` proud at each end
  stops the hand sliding off sideways when the pull is not square.

The cord, strap or tie rod passes through the bore along the axis and is
stopped beyond the far flange, or runs through and back to a ring to make a
stirrup. The handle is not what holds the load: the cord and its termination
are.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Grip** | `grip` | A flanged tube with a bore along its axis. An optional pocket in its side holds a small module: a switch, a sensor, a tag. |
| **Bar** | `bar` | A solid two-hand bar with flanged ends and one or two cross holes for the eye bolts or the pin it is pulled by. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `grip_d` | 20–45 mm | Grip diameter |
| `flange_h`, `flange_t` | 0–15 mm, 2–15 mm | How far each end flange stands proud, and its thickness |
| `grip_l` | 80–200 mm | Length of the grip between the flanges |
| `cord_d` | 3–12 mm | Bore along the axis |
| `pocket`, `pocket_l`, `pocket_w`, `pocket_depth` | on / off, 10–60 mm, 6–16 mm, 1–12 mm | The module pocket |
| `bar_l` | 250–1300 mm | Length of the bar between the flanges |
| `eye_d`, `eye_spacing` | 4–12 mm, 0–1200 mm | Cross holes and the distance between them (0 gives one in the middle) |

## Constraints

- The grip keeps 4 mm of wall round the cord bore.
- With the pocket on: it leaves 2 mm of wall above the bore, fits the grip's
  width, and keeps 10 mm of grip at each end.
- The bar keeps 4 mm of material beside each cross hole, and the holes sit
  10 mm inside its ends.
- A grip over 40 mm and a flange under 3 mm are flagged.

## Making it

Both parts are turned: one profile about the axis, plus a drilled hole or a
milled pocket. Printed, the grip stands on a flange and needs no support; the
bar prints lying down in two halves or is cut from tube with printed end
flanges. Leave the surface as it prints, knurl it, or wrap it: the cartridge
models the shape under the wrap.

This cartridge is a geometry family, not a rated component. A handle people
pull on with their body weight has to be made of something that will not
snap, and it is only as strong as the cord, the knot or swage that ends it
and the hardware it clips to. Whoever builds and uses it has to establish
that.

## Interfaces

- **Cord bore** (`cord_bore`): the bore along the grip axis, entered at the
  -X end face.
- **Grip surface** (`grip_surface`): `grip_d`, `grip_l`, the flanges.
- **Module pocket** (`module_pocket`): the pocket's length, width and depth.
- **Bar eye holes** (`bar_eyes`): `eye_d`, `eye_spacing`. No frame is
  declared: the holes open on a round surface, which has no seating face.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
