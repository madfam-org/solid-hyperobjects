# Cable Spool

A parametric flanged drum generated with **CadQuery** (B-Rep). It winds a cable,
cord or rope and mounts on a shaft: the working end of a winch, a cable-driven
actuator, a tensioner or a hoist.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the drum diameter decides

The drum is a lever. With the cable on the first layer, the pull and the shaft
torque are tied by the drum radius:

```
torque = pull × drum_d ÷ 2        cable speed = shaft speed × drum_d ÷ 2
```

A larger drum asks more torque for the same pull and bends the cable less. A
smaller drum does the opposite. The manifest warns under 8 cable diameters; the
real minimum belongs to the cable's maker and its construction (wire rope and
high-modulus synthetic rope want far more than a braided cord).

Each extra layer of cable adds one cable diameter to the radius, so the pull a
given torque delivers falls as the drum fills. Size the winding width to keep
the working length on as few layers as the application allows.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Plain Spool** | `spool` | Two flanges, a through bore, an optional keyway and an anchor hole. |
| **Spool with Set-Screw Hub** | `spool_hub` | The same drum with a hub on one side carrying two radial set-screw holes at 90°. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `drum_d` | 20–200 mm | Diameter the cable winds on |
| `drum_w` | 8–150 mm | Clear width between the flanges |
| `flange_h` | 3–40 mm | Flange height above the drum |
| `flange_t` | 2–12 mm | Flange thickness |
| `bore` | 3–40 mm | Shaft bore |
| `keyway`, `key_w` | on/off, 2–12 mm | Square keyway along the bore, half the key width deep |
| `cable_d` | 1–10 mm | Cable diameter |
| `anchor` | on/off | A hole through one flange, centred in the flange height, to knot or crimp the cable end |
| `hub_d`, `hub_l` | 10–120 mm, 8–40 mm | Hub diameter and length (hub mode) |
| `setscrew_dia` | 2.5–8 mm | Tap-drill diameter of the set-screw holes (hub mode) |

## Constraints

- The drum keeps at least 4 mm of wall around the bore, and the hub at least 3 mm.
- The flanges stand at least one cable diameter plus 3 mm above the drum, so the
  cable is retained and the anchor hole keeps a wall on both sides.
- The key is narrower than the shaft; the set-screw hole fits inside the hub.
- The hub is never wider than the flange.

## Making it

The axis is vertical, so the part prints flange-down with no supports on the
drum. For a load-bearing drum, machine it or print it solid: the cable's whole
pull goes through the bore, the key and the flange roots. This cartridge is a
geometry family, not a rated component. The safe working load of a drum depends
on the material, the process and the shaft fit, and has to be established by
whoever builds and uses it.

## Interfaces

- **Shaft bore, keyway and set screws** (`shaft_bore`): `bore`, `keyway`, `key_w`, `setscrew_dia`.
- **Cable drum** (`cable_drum`): `drum_d`, `drum_w`, `flange_h`, `cable_d`.

## Mating frames (assemblies)

`shaft_bore` carries a SEM-1 frame on the plain `spool` part, so the drum can be
placed on a shaft in an assembly:

- **Origin and normal:** origin `(0, 0, 0)`, the centre of the bore where it
  opens in the drum's lower face. Normal `-z`, out of the bore.
- **Orientation:** `x_axis` `+x`. Symmetry 0.
- **Polarity and size key:** polarity female (the bore takes the shaft); size key
  `{param: bore, map: {"19": shaft-19mm-key-6mm}}`: a 19 mm shaft end with a 6 mm
  parallel key.

The frame is verified against the rendered part at the defaults and every preset
(`y4d-spec check --render`).

Limits:

- **One shaft size.** At any `bore` other than 19 mm the interface has no size
  key, so a mate that needs one fails and names the slider value.
- **The key assumes the keyway.** The size key says "keyed 19 mm shaft"; the part
  only matches it with `keyway` on and `key_w` at 6 mm, and nothing in the frame
  checks that.
- **Where the drum sits along the shaft** is the partner's frame to state: this
  frame only says the shaft enters at the lower face.
- **`spool_hub` has no frame yet.**

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
