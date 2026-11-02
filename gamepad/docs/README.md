# Gamepad

An original two-handed controller family with brick, crescent, dogbone, handles
and trident body plans. The same body can split into rail or magnetic halves.
Named presets carry published envelopes and counts, while the profile, surface,
layouts and control shapes remain our archetype constructions. See
[NOTICE](../NOTICE).

## Frame and envelope

| Model axis | Reference field | Interpretation |
|---|---|---|
| X | `states.body.width` | across the hands, centered at X=0 |
| Y | larger of published height/depth | front (−Y) to shoulders (+Y) |
| Z | smaller of published height/depth | thickness; grip underside at Z=0 |

The smallest-axis convention is our explicit mapping because source axis labels
differ. For a reference describing one detachable half, the generator doubles
width to construct a pair; the preset provenance states that mapping. A named
preset never claims that the shell between the published extrema matches a
maker's design. `envelope` excludes sticks, button caps, cable stubs and split
displacement; these are projecting parts. It is a flat-topped continuous planform hull including the bridge and grips,
conservatively filling the crown. Source facts constrain the bounding dimensions,
not a manufacturer's curved surface. The assembled preview retains the crown.

## Modes and parts

| Mode | Parts | Purpose |
|---|---|---|
| pad | body, controls | assembled preview; individual caps are separate solids |
| envelope | envelope | one conservative flat-topped planform hull |
| top_shell | top_shell | hollow upper shell |
| bottom_shell | bottom_shell | hollow lower shell |
| left_half, right_half | corresponding half | shell half with its rail or magnet pockets |

`body` is one solid for an unsplit pad, two for a split pad. The `controls`
body count is the sum of actual caps; a circle-pad comprises four caps. The
manifest declares this as an expression. Shell parts are previews of the
archetype; no bosses, fastening design or electronic assembly is implied.

## Composition and construction

| Module | Components | Interfaces |
|---|---|---|
| pad_body | crowned body, grips | device_envelope, grip_envelope |
| pad_body | rail and magnet pockets | rail, magnetic_seat |
| controls | D-pad, buttons, stick/trigger seats | dpad_seat, button_seat, stick_seat, trigger_seat |
| pad_controls | control layouts, cap solids, stick, trigger blade | control seats and live motion |
| pad_controls | grille and battery-door seam | battery_bay, archetype grille |
| connectors | receptacle cuts | port_cutout |

The crown is a shared analytic height function used by both the body and control
seats. Its loft uses exact ellipse edges with an explicit start parameter away from
the split plane and grip joins. Joined solids overlap; cuts overshoot the surface. The bridge and grips
are built as one body before feature cuts. Generic ports are keep-outs, and the
rails are archetypal rectangular profiles rather than maker profiles.

`family.py` is authored. Regenerate `main.py` with
`python3 tools/inline_parts.py --write gamepad`; never edit it directly.

## Presets and archetype rules

`tools/presets/gamepad.py` owns derivation and reads the reference catalog at
`SPEC_PIN`. Missing envelopes are listed as `awaiting_a_source`; unknown
counts and uncovered lists fall back explicitly. Only a covered complete list
establishes absence. Null counts stay unknown.

| Archetype | Envelope W × Y × Z (mm) | Exercises |
|---|---|---|
| brick | 120 × 54 × 20 | flat controller, two-button row |
| crescent | 160 × 92 × 32 | six-button arc, concave front |
| dogbone | 144 × 64 × 26 | end lobes, bumpers |
| handles | 156 × 104 × 40 | two sticks, rear battery seam |
| trident | 176 × 112 × 34 | third grip, under trigger, octagonal stick gate |
| rail halves | 76 × 104 × 22 | paired brick halves and rails |
| magnetic halves | 84 × 112 × 24 | paired halves with magnet pockets |

Every archetype dimension is ours. Source counts select a plan by our rule:
split means brick halves; ≥2 sticks means handles; one stick means trident;
≥2 bumpers without sticks means dogbone; ≥3 face buttons means crescent;
otherwise brick. Plan ratios and every control size are documented beside
`PLANS` and `RULES` in the generator. Wall thickness 2 mm, seam ratio 0.5,
clearance 0.3 mm and recess depth 1.2 mm are archetype constants. Those shell
constants remain defaults rather than preset values so a pad preset has an
actual visible-mode intersection and is rendered by the verifier.

Animations move trigger blades, tilt sticks, and detach magnetic halves.
Their frames are checked for valid positive-volume solids. They explain motion;
collision-free operation, comfort, electronics and physical retention are not
certified.

## Awaiting a source

Exact profiles, shell fasteners, port positions, control positions, rail
profiles, grip texture and crown curvature remain archetypal. Partial catalog
records retain unknown values and explicit fallback groups. No values are
inferred from photos, and no artwork is included.
