# Index Pin

A parametric pull pin, generated with **CadQuery** (B-Rep): the loose half of
a pin-and-hole adjustment. The shank passes through a guide and into one of a
row of holes, a collar stops it at the right depth, and a grip lets a hand
pull it out again.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the shank decides

A pin holds by shear: the load tries to cut it where the moving part meets the
fixed one. Three numbers set how it behaves there.

- **`pin_d` is the hole, not the pin.** Enter the nominal diameter of the hole
  the pin has to enter; the shank is made `fit` smaller on the diameter. The
  two parts of the adjustment then carry the same number, and the pin always
  goes in.
- **`fit` is the play.** A loose pin drops in by itself and rattles; a close
  one has to be lined up. 0.2 mm suits a turned pin in a reamed hole; a printed
  pin wants more.
- **`engage_l` is everything under the collar**: the length of the guide the
  pin passes through plus the depth it enters the hole. A pin that reaches
  less than its own diameter into the hole bears on an edge.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Knob Pin** | `pull_pin` | Shank, collar and a round knob with a waist the fingers hook under. An optional cross hole in the knob takes a lanyard or a ring. |
| **T-Handle Pin** | `tee_pin` | The same shank and collar under a T-handle, for a pin pulled against friction or with a gloved hand. |

Either pin can carry a **clip hole**: a cross hole near the tip for a spring
clip, for a pin that passes right through both walls and must not work out.

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `pin_d` | 4–20 mm | Nominal diameter of the hole the pin enters |
| `fit` | 0–1 mm | How much smaller than the hole the shank is, on the diameter |
| `engage_l` | 12–150 mm | Length of the shank under the collar |
| `tip_chamfer` | 0–1.5 mm | Lead-in chamfer on the tip |
| `collar_d`, `collar_t` | 8–40 mm, 2–12 mm | The collar that stops the pin against the guide |
| `grip_d`, `grip_h` | 24–50 mm, 15–60 mm | The knob (knob pin) |
| `lanyard`, `lanyard_d` | on / off, 2–4 mm | Cross hole through the knob |
| `handle_l`, `handle_d`, `handle_rise` | 50–150 mm, 8–25 mm, 14–40 mm | The T-handle bar and its height above the collar (T-handle pin) |
| `clip_hole`, `clip_d`, `clip_offset` | on / off, 1.5–6 mm, 3–30 mm | Cross hole for a spring clip, and its distance from the tip |

## Constraints

- The collar stands at least 2 mm proud of the shank all round.
- The fit takes less than a quarter of the hole diameter, and the chamfer
  leaves half of the tip flat.
- The clip hole leaves 0.75 mm of shank on each side and sits inside the
  shank's length.
- The lanyard hole fits inside the head of the knob.
- The T-handle leaves 10 mm for the fingers and reaches past the collar.

## Making it

The pin is a turned part: one profile about its axis, plus a cross-drilled
hole or a pressed-in handle bar. Printed, it stands on the top of its knob or
lies on its side with supports; a printed pin is for light duty, because a
layered shank is weakest exactly in shear across the layers. For a pin that
carries a real load, turn it from steel or use the print as the knob on a
steel dowel.

This cartridge is a geometry family, not a rated component. What a pin can
carry depends on its material, the fit and the two parts it joins, and has to
be established by whoever builds and uses it.

## Interfaces

- **Shank** (`knob_pin_shank`, `tee_pin_shank`): a plain pin in a round hole
  of `pin_d`. The frame sits on the axis at the underside of the collar and
  points down the shank. No size key is declared: the interface-sizes
  vocabulary has no entry for a plain index pin yet.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
