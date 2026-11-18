# Gripper Finger

A finger for a parallel-jaw gripper, generated with **CadQuery** (B-Rep): the
part that bolts onto the moving jaw of a robot gripper, a pneumatic clamp or a
bench fixture and actually touches the workpiece.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the two ends decide

A finger has two ends and each belongs to something else.

- **The root belongs to the gripper.** Its jaw has two tapped holes in a
  line; `jaw_pitch`, `jaw_bolt_d` and `root_margin` come from the gripper's
  drawing. The back of the finger seats on the jaw.
- **The tip belongs to the part.** A flat face grips flat sides. A **V
  notch** centres a round body: two fingers with facing notches hold a
  cylinder on four lines and bring it to the same place every time. Set the
  notch by its width and depth; a depth of half the width is a 90° V, which
  holds a wide range of diameters. A round body of diameter *d* touches a 90°
  V at 0.71 × *d* across, so the notch must be wider than that.

The gripping face is the plane Y = 0 and the notch runs the full height, so
the same finger made twice (one of them turned round) is a matched pair.

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `reach` | 30–250 mm | Length from root to tip |
| `finger_t`, `finger_h` | 6–40 mm, 10–120 mm | Thickness (gripping face to back) and height |
| `jaw_pitch`, `jaw_bolt_d`, `root_margin` | 8–80 mm, 3.4–10.5 mm, 4–30 mm | The jaw's two bolts and the distance from the root to the first |
| `vee`, `vee_x`, `vee_w`, `vee_depth` | on / off, 20–240 mm, 6–160 mm, 2–30 mm | The V notch: position from the root, width at the face, depth |
| `pad_holes`, `pad_span`, `pad_bolt_d` | on / off, 6–100 mm, 2.4–6.5 mm | Two holes near the tip for a bolted-on pad (flat finger) |

## Constraints

- The jaw bolts fit along the finger, with 2 mm between their holes and 2 mm
  of finger above and below.
- The notch keeps clear of the jaw bolts, leaves 3 mm of finger at the tip
  and 3 mm behind it.
- The pad holes fit in the height, and are not combined with a notch.
- A finger longer than eight times its thickness is flagged: it bends under
  the grip.

## Making it

The finger is one profile along its height: saw it from bar and mill the
notch, or print it lying on its back. A printed finger is the fast way to
find the right notch; once it holds, make the same shape in aluminium if the
part is heavy or the cycle count is high. Counterbore the jaw holes for the
screw heads if they must sit below the gripping face.

This cartridge is a geometry family, not a rated gripper component. Whether a
pair of fingers holds a given part depends on the gripper's force, the
friction at the faces and how the part is accelerated, and a dropped part is
a hazard. Whoever builds and uses the cell has to establish that the grip is
safe.

## Interfaces

- **Jaw mount** (`jaw_mount`): the back of the finger at the two bolts; an M5
  screw joint when `jaw_bolt_d` is 5.5.
- **Gripping face** (`grip_face`): the plane the workpiece meets; a soft pad
  from `soft-gripper-pad` bolts onto it.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
