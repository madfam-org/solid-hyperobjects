# Shaft Encoder Mount

The two parts that turn the end of a shaft into an angle sensor, generated
with **CadQuery** (B-Rep): a cap that holds a magnet on the axis, and a bridge
that holds the sensor board in front of it.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the axis decides

A magnetic angle sensor is a chip that reads the direction of the field from
one small magnet turning in front of it. It needs a magnet magnetised **across
its diameter** (north on one half of the face, south on the other), not
through its thickness as most disc magnets are. And it needs three things from
the mount:

- **The magnet on the axis.** The cap's pocket is concentric with its shaft
  bore, so the magnet turns about its own centre. A magnet that sits off the
  axis gives an error that repeats every turn.
- **The chip on the same axis.** The bridge has a window on the axis and the
  board's hole pattern centred on it. Check on the board's drawing that the
  chip sits at the centre of its hole pattern; not every board does.
- **The right gap.** The sensor's data sheet gives the distance it wants
  between the magnet's face and the chip, usually a millimetre or two. Here
  that gap is set by `stand_h`, the clear height under the bridge:

```
stand_h = height of the shaft end above the mounting face
        + web_t + magnet_h          (the cap adds these above the shaft end)
        + the gap the sensor asks for
        + the height of the chip under the board
        - plate_t                   (the board sits on top of the bridge)
```

Measure the shaft end on the real machine. Shim under the feet to trim the
last tenths.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Magnet Cap** | `magnet_cap` | Slips onto the shaft end to `bore_depth`. A pocket in the outer face seats the magnet flush; a radial set screw holds the cap. |
| **Sensor Bridge** | `sensor_bridge` | A bridge on two bolted feet, with the window and the board's holes on top. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `shaft_d`, `shaft_fit`, `bore_depth` | 3–25 mm, 0–0.5 mm, 6–30 mm | Shaft end, the play of the bore on it, and how far the cap goes on |
| `setscrew`, `set_d` | on / off, 2–5 mm | Radial set screw hole |
| `cap_wall` | 1.5–8 mm | Wall round the shaft or the magnet, whichever is larger |
| `magnet_d`, `magnet_h`, `magnet_fit` | 3–12 mm, 1–6 mm, 0–0.4 mm | The magnet and the play of its pocket |
| `web_t` | 0.8–5 mm | Solid layer between the shaft end and the magnet |
| `board_px`, `board_py`, `board_hole_d` | 8–80 mm, 0–60 mm, 1.8–4.5 mm | The board's hole pattern (`board_py` 0 for two holes in a line) |
| `window_d` | 4–30 mm | Window on the axis |
| `stand_h` | 8–120 mm | Clear height under the bridge |
| `leg_span`, `bridge_d` | 20–200 mm, 10–100 mm | Clear width between the legs, and depth of the bridge |
| `plate_t`, `foot_w`, `mount_bolt_d` | 2–8 mm, 8–30 mm, 2.4–6.5 mm | Thickness, feet and their holes |

## Constraints

- The set screw sits inside the depth of the bore.
- The board holes sit inside the legs and inside the depth of the bridge, and
  the window keeps clear of them.
- Each foot leaves 2 mm of material on both sides of its hole.
- A loose magnet pocket (over 0.2 mm) is flagged.

## Making it

Print the cap with the magnet pocket up; print the bridge on its side so the
legs are solid and the top is true. Use a material that is not magnetic for
both, and non-magnetic screws near the magnet: steel next to it bends the
field. Glue the magnet in. A cap on a shaft that turns fast must be balanced
and held by more than friction: use the set screw on a flat.

This cartridge is a geometry family, not a calibrated sensor. The reading
depends on the chip, the magnet, the real gap and a calibration after
assembly.

## Interfaces

- **Shaft bore floor** (`shaft_bore`): the floor of the bore, which the end
  of the shaft seats on; an 8 mm ground shaft when `shaft_d` is 8. The frame
  is on the floor and not at the mouth because the magnet pocket is a second,
  smaller bore on the same axis.
- **Magnet pocket** (`magnet_pocket`): the pocket floor. No size key is
  declared: a disc magnet needs two numbers and a size key reads one.
- **Sensor board seat** (`board_seat`): the top of the bridge.
- **Bridge feet** (`bridge_feet`): the underside of the feet; an M3 screw
  joint when `mount_bolt_d` is 3.4.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
