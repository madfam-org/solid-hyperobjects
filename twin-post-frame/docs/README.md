# Twin-Post Frame

The two fixed members that hold a pair of parallel posts standing, generated
with **CadQuery** (B-Rep): a floor base with a socket for each post, and a
crossbar that ties their tops. With two posts they make a freestanding portal.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## What the two numbers decide

Everything in this family follows from the **post section** (`post_w` ×
`post_d`) and the **spacing** between the two post axes. Set them once and the
base and the crossbar agree: the sockets in the base and the caps under the
crossbar sit on the same two points, and a post cut square at both ends closes
the rectangle.

The posts are not part of this cartridge. Any rectangular tube or bar of the
declared section fits; a column with index holes turns the portal into a
height-adjustable rack.

Where the posts stand along the base (`post_y`) decides which way the frame
resists tipping. A base that reaches forward of the posts carries a load hung
in front of them; one that reaches both ways stands under a load on either
side. The manifest warns when the posts sit within a fifth of the depth from
an edge.

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Base** | `base` | Two rails joined by a rear and a front member, open in the middle. Each rail has a socket the post stands in, a bolt hole up through the socket floor, and a hole near each end for the stud of a levelling foot. |
| **Base with Front Ledge** | `base_ledged` | The same base with a low ledge along its front, below the top of the rails, for what must stand lower than the base and just in front of it: the hinge blocks of a folding platform, a kick plate. Two seats on the ledge, each a pair of holes, sit symmetric about the centre. |
| **Crossbar** | `crossbar` | A bar across the two post tops with a bolt hole down into each. With `cap_depth` above 0 a pocket caps each post; at 0 the underside is flat. With `arm_mount` on, two blind holes in the front face take the bolts of a hanging accessory. |

## Parameters

| Parameter | Range | Meaning |
| :--- | :--- | :--- |
| `spacing` | 200–1500 mm | Distance between the two post axes |
| `post_w`, `post_d` | 20–120 mm | Post section: width along the line between the posts, and depth |
| `fit` | 0.2–2 mm | Clearance per side between a post and its socket or cap |
| `bolt_d` | 4.5–12.5 mm | Clearance hole on each post axis |
| `base_depth`, `post_y` | 200–1000 mm, 40–800 mm | Length of the rails, and distance from the rear edge to the post axis |
| `rail_margin`, `rail_h` | 8–60 mm, 20–120 mm | How much wider than the post each rail is per side, and the height of the base |
| `rear_d`, `front_d` | 40–300 mm | Depth of the rear and the front member |
| `socket_depth` | 3–40 mm | How deep each post sits in the base |
| `foot_bolt_d` | 4.5–12.5 mm | Hole for each levelling-foot stud |
| `bar_h`, `bar_margin`, `cap_depth` | 15–120 mm, 0–20 mm, 0–30 mm | Crossbar height, its margin round the post section, and the depth of the caps |
| `arm_mount`, `arm_bolt_span`, `arm_hole_d`, `arm_mount_drop` | on / off, 20–200 mm, 3.3–10.5 mm, 8–100 mm | Two blind holes in the crossbar's front face: their spacing, their diameter (the tap drill: 6.8 for M8, 4.2 for M5) and how far below the top face they sit |
| `ledge_h`, `ledge_d` | 5–60 mm, 20–200 mm | Height of the ledge above the floor and how far it reaches in front of the base (ledged base only) |
| `ledge_seat_span`, `ledge_seat_pitch`, `ledge_seat_y`, `ledge_hole_d` | 50–1400 mm, 10–100 mm, 8–190 mm, 3.3–10.5 mm | The two ledge seats: distance between their centres, spacing of the two holes of each, distance of the hole line from the front face of the base, and the hole diameter (the tap drill: 5 for M6) |
| `rear_seats`, `rear_seat_x`, `rear_seat_px`, `rear_seat_py`, `rear_hole_d` | on / off, 0–700 mm, 10–300 mm, 10–280 mm, 3.3–10.5 mm | Rectangles of four blind holes in the top of the rear member, on either base: the offset of each of the two seats from the centre line (0 gives one seat), the pattern across and front to back, and the hole diameter (the tap drill: 6.8 for M8) |

## Constraints

- The rails keep at least 20 mm of window between them, and so do the rear and
  front members.
- Each socket stays clear of the foot holes at both ends of its rail.
- The socket leaves 5 mm of floor under the post, and the cap 5 mm of bar
  above it.
- A cap needs 3 mm of wall round the post; with no margin, set the cap to 0.
- The arm holes stay between the two posts and inside the height of the bar.
- A socket under 8 mm is flagged: it locates the post but barely braces it.
- The ledge stays at least 5 mm below the top of the rails; its seat holes keep
  3 mm of material to each edge, fit the width of the base and do not overlap.
- The rear seats fit the depth of the rear member, stay between the rails
  (clear of the sockets and the foot holes) and do not overlap.

## Making it

The base is a flat frame: cut from plate or sheet goods on a router, welded
from four lengths of tube with the sockets added as plates, or printed in
sections for a small stand. The crossbar is a bar with two pockets and two
holes. Bolt each post through the hole on its axis into a threaded insert or
a plug in the end of the tube.

This cartridge is a geometry family, not a structural design. What a portal
can carry depends on the posts, the material, the joints and the floor, and a
tall frame under a side load can tip. Whoever builds and uses it has to
establish that it is strong and stable enough, and anchor or ballast it when
it is not.

## Interfaces

- **Post sockets** (`socket_a`, `socket_b`): the socket floors in the base,
  one per post, facing up.
- **Floor face and foot holes** (`floor`): the underside of the base.
- **Post caps** (`cap_a`, `cap_b`): the seats under the crossbar, facing down.
- **Crossbar top face** (`bar_top`): where an accessory bolts on.
- **Crossbar arm mount** (`arm_mount`): the front face at the line of the two
  holes, facing forward. Polarity female (the thread side). It carries the
  size key `m8-screw-joint` when `arm_hole_d` is 6.8 and `m5-screw-joint` at
  4.2, so an arm whose beam bolts carry the same key mates here.

- **Rear seats** (`rear_seat_a`, `rear_seat_b`): the top of the rear member at
  the centre of each hole rectangle, facing up. Polarity female. The key
  follows `rear_hole_d`: `m8-screw-joint` at 6.8, `m6-screw-joint` at 5,
  `m5-screw-joint` at 4.2, `m10-screw-joint` at 8.5. The frame is on the face
  whether or not the holes are drilled; turn `rear_seats` on to drill them.
- **Ledge seats** (`ledge_seat_a`, `ledge_seat_b`): the top of the ledge between
  the two holes of each seat, facing up. Polarity female; `m6-screw-joint` at a
  5 mm hole, `m5-screw-joint` at 4.2, `m8-screw-joint` at 6.8.
- The ledged base repeats the base's own interfaces under its part:
  `ledged_socket_a`, `ledged_socket_b`, `ledged_floor`, `ledged_rear_seat_a`,
  `ledged_rear_seat_b`.

The hole patterns are parameters, not a standard: a seat mates a partner only if
the partner's own bolt pattern has the same pitches, which the size key does not
check.

The sockets and caps carry the size key `square-tube-80mm` when `post_w` is
80. The key reads the width only: a square 80 mm post is covered, and a
rectangular post has no key yet.

## Licence

CERN-OHL-W-2.0. See `LICENSE`.
