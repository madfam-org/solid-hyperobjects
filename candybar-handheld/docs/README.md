# Candy-Bar Handheld

A generic candy-bar handheld, generated with **CadQuery** (B-Rep): an upright slab
with a screen above its controls, in which **every control is its own named part**.
It is an archetype for a virtual device: a model a viewer can show, light and press,
and whose screen a program can draw on.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

It models no product. The shape is plain, nothing on it is traced or measured from
a device, and the two presets are illustrative sizes (see [`NOTICE`](../NOTICE)).

## Frame

Millimetres. X runs across the face and Y up it, both centred on the body. Z runs
through the body: the rear face is at `z = 0` and the front face at
`z = body_depth`. The device lies on its back, face up.

## Parts

Thirty-three parts. Two are structure and thirty-one are controls.

| Group | Parts | Where |
| :-- | :-- | :-- |
| Structure | `body`, `rear_mount` | the shell; a land on the rear with four screw holes for a module |
| Screen | `screen` | front face, above the controls |
| D-pad | `dpad_up`, `dpad_down`, `dpad_left`, `dpad_right` | front face, left; four arms around a hub that is part of the body |
| Face buttons | `button_south`, `button_east`, `button_west`, `button_north` | front face, right, in a diamond |
| Shoulders and triggers | `shoulder_left`, `shoulder_right`, `trigger_left`, `trigger_right` | top edge; shoulders near the face, triggers near the rear |
| Sticks | `stick_left`, `stick_right` | front face, below the D-pad and the face buttons |
| Light rings | `light_ring_left`, `light_ring_right` | let into the face around each stick |
| Menu buttons | `menu_left`, `menu_center`, `menu_right` | a row near the bottom of the face |
| Function buttons | `function_left`, `function_right` | below the screen's lower corners |
| Side controls | `power_button`, `slide_switch` (right side); `volume_up`, `volume_down` (left side) | the two long sides |
| Ports | `port_bottom`, `port_top`, `port_rear` | middle of the bottom edge, middle of the top edge, rear face |
| Light bars | `light_bar_upper`, `light_bar_lower` | rear face |

The face buttons are named by position (south, east, west, north), not by a letter:
which letter a device prints on each is that device's choice.

Every part is one body. A control sits in a seat cut into the body, a little wider
than the control (0.1 to 0.3 mm a side).

## Which controls a device has

Seven parameters switch controls on and off:

| Parameter | Values | Controls it switches |
| :-- | :-- | :-- |
| `stick_count` | 0, 1, 2 | `stick_left` from 1, `stick_right` from 2 |
| `light_ring_present` | on, off | a ring around each stick that is present |
| `shoulder_rows` | 0, 1, 2 | the shoulders from 1, the triggers from 2 |
| `menu_button_count` | 0 to 3 | 1 is `menu_center`; 2 is `menu_left` and `menu_right`; 3 is all |
| `function_button_count` | 0, 1, 2 | `function_left` from 1, `function_right` from 2 |
| `light_bar_count` | 0, 1, 2 | `light_bar_upper` from 1, `light_bar_lower` from 2 |
| `slide_switch_present`, `port_bottom_present`, `port_top_present`, `port_rear_present`, `rear_mount_present` | on, off | the part of the same name |

They do two things, and only two:

1. **The body carries a seat only for a control that is switched on.** With
   `stick_count` at 0 the face has no dish for a stick.
2. **The manifest's `device` block says where each control is present**
   (`present_when`, for example `stick_count >= 1`).

They do not change what a part's builder returns. Asked for `stick_right`, the
script returns the right stick where it would sit, whatever `stick_count` says. So a
render never fails or comes back empty because a control is switched off.

What a visitor sees is the list of parts of the **mode**:

- **`device`** lists all thirty-three parts. It is the full layout, and it matches
  the defaults, which switch everything on.
- **`device_plain`** lists nineteen: the body, the screen, the D-pad, the face
  buttons, the shoulders, `menu_left` and `menu_right`, power, volume, the bottom
  port and the upper light bar. Use it with parameters that switch the rest off, as
  the compact preset does. At the defaults the body still carries the seats of the
  controls this mode does not list.

A viewer that reads the `device` block can do better than a mode's fixed list: it
knows from `present_when` which controls exist at the visitor's parameters, and can
hide the others.

## The device block

`project.json` carries a `device` block in the **device-control vocabulary** of the
hyperobjects keystone (`device-controls/1.0`; contract in hyperobjects-spec,
`docs/DEVICE_CONTROLS.md`). It lists `body` and `rear_mount` as structure, the mount
with `present_when: rear_mount_present`, and declares each of the thirty-one controls:
its role, the Linux input event it sends, how it travels, and where it is present.

| Parts | Role | Sends | Travel |
| :-- | :-- | :-- | :-- |
| `dpad_*` | button | `BTN_DPAD_UP`, `_DOWN`, `_LEFT`, `_RIGHT` | `-z`, `button_travel` |
| `button_*` | button | `BTN_SOUTH`, `BTN_EAST`, `BTN_WEST`, `BTN_NORTH` | `-z`, `button_travel` |
| `shoulder_*` | button | `BTN_TL`, `BTN_TR` | `-y`, 1.0 mm |
| `trigger_*` | trigger | `BTN_TL2` with `ABS_Z`; `BTN_TR2` with `ABS_RZ` | `-y`, 1.2 mm |
| `stick_left` | stick | `ABS_X`, `ABS_Y`; click `BTN_THUMBL` | tilt `stick_tilt`; click `-z`, 0.6 mm |
| `stick_right` | stick | `ABS_RX`, `ABS_RY`; click `BTN_THUMBR` | tilt `stick_tilt`; click `-z`, 0.6 mm |
| `menu_left`, `menu_center`, `menu_right` | button | `BTN_SELECT`, `BTN_MODE`, `BTN_START` | `-z`, `button_travel` |
| `function_left`, `function_right` | button | `BTN_TRIGGER_HAPPY1`, `BTN_TRIGGER_HAPPY2` | `-z`, `button_travel` |
| `power_button` | button | `KEY_POWER` | `-x`, 0.4 mm |
| `volume_up`, `volume_down` | button | `KEY_VOLUMEUP`, `KEY_VOLUMEDOWN` | `+x`, 0.4 mm |
| `slide_switch` | switch, 2 positions | `SW_MUTE_DEVICE` | `-y`, `slide_switch_throw` |
| `screen` | screen | `screen_pixels_w` × `screen_pixels_h` pixels | lit face looks `+z`, top of the picture `+y` |
| `light_ring_*`, `light_bar_*` | light | any colour (`rgb`) | |
| `port_*` | port | connector `usb-c` | |

These are a generic default. A device built from this cartridge states its own
codes, labels and connectors in its own copy of the block.

`screen_pixels_w` and `screen_pixels_h` are the only parameters no solid reads: they
are the screen's pixel count, read by the `device` block. The manifest marks them
`intentionally_unused` and says why.

## The graph

`candybar.graph.json` is a **wrapper graph** (graph format 1.2): one `script` node
runs `main.py`, the graph declares every parameter, group, preset, constraint and
interface, and each of the thirty-three parts is an output. Both modes name it as
their `graph_file`. `--parity` requires the mesh the graph renders to be the
script's, byte for byte.

The graph copies the manifest's entries and pins `main.py` by sha256. After an edit
to `main.py`, or to a parameter, preset, constraint or interface in the manifest,
copy the entry into the graph's `declarations` and update `provenance.sources`
(`shasum -a 256 main.py`). `y4d-spec check` fails until the two agree.

## Presets

Both are illustrative: round numbers that show two corners of the parameter space.

| Preset | Mode | Body (mm) | Screen | Layout |
| :-- | :-- | :-- | :-- | :-- |
| `tall_two_sticks` | `device` | 88 × 164 × 18 | 3.5 in, 4:3, 640 × 480 | everything: two sticks with light rings, shoulders and triggers, three menu and two function buttons, the slide switch, three ports, two light bars, the rear mount |
| `compact_no_sticks` | `device_plain` | 74 × 116 × 15 | 2.8 in, 4:3, 320 × 240 | D-pad, four face buttons, two shoulders, two menu buttons, power, volume, a bottom port, one light bar |

## Constraints

Forty-two, all errors: the configurator refuses a parameter set that breaks one, and
both presets satisfy every one. Together they hold one layout. Top to bottom on the
face: the screen, the function buttons, the D-pad (left) and the face buttons (right)
in one row, the sticks, the menu row.

- **Face.** Every face control stays 3 mm inside the outline and out of the rounded
  corners. Neighbouring clusters keep 2 mm apart: the screen from everything below it,
  the D-pad from the face buttons, the sticks from each other, the rows from each other.
  Within a cluster, the face buttons and the menu buttons do not overlap, and the D-pad
  span leaves an arm at least 2 mm long.
- **Top edge.** The shoulders and triggers stay on the straight part of the edge
  (`shoulder_inset` at least `corner_radius`), clear of each other and of the top port
  by 1.5 mm, so their seats never share a face with the port's seat. A shoulder and a
  trigger fit one behind the other (`body_depth` at least `2 × shoulder_thickness + 3`).
  The edge ports stay on the straight part of the top and bottom edges.
- **Sides.** The side buttons and the slide switch stay on the straight part of the
  sides, 3 mm or the corner radius from its ends, whichever is more.
- **Rear.** The light bars, the rear port and the rear mount stay 3 mm inside the rear
  and out of its corners, and 2 mm apart.
- **Body.** The corner radius is under half the width and half the height.

A rule applies only where its control is present (`stick_count < 1 || …`). The
configurator's evaluator has no square root, absolute value or tangent, so three
bounds stand in, each on the safe side: a screen's half-height is taken as
`17.97 × screen_diagonal × screen_aspect_h / (screen_aspect_w + screen_aspect_h)` (at
most 4 % over the true value from 1:1 to 16:9), a stick's dish as widening by
`stick_tilt / 51.9` per millimetre of height (tan 30° is 0.577, and tan is convex), and
`(y < 0 ? -y : y)` for the distance from the centre line.

## Interfaces

- `device_envelope` — the outline, for a stand, a dock or a case.
- `screen_window` — the lit rectangle in the front face.
- `rear_module_mount` — four clearance holes, 4 mm in from each corner of the land.

## Verifying a change

```bash
y4d-spec check ./candybar-handheld
y4d-spec check ./candybar-handheld --render --require-openscad --parity \
  --openscad-path libs --openscad-path .
```

With a keystone that carries the device-control vocabulary, the first command also
checks the `device` block against the parts, modes, presets and graph, and the
second checks each control against the mesh it rendered.
