# Prop Guard

An **impact and finger guard** for FPV / RC propellers, generated with
**CadQuery** (B-Rep). A ring (or ducted shroud) sized to the propeller diameter
rides on spoke arms that bolt to the standard square **motor mount pattern**
(9×9 M2, 16×16 or 19×19 M3). Protects fingers and props on bump-ins; the ducted
variant also recovers static thrust on small craft.

Part of the **Yantra4D Hyperobjects Commons**. Official visualizer and
configurator: [Yantra4D](https://app.yantra4d.com).

## Modes

| Mode | Part | Description |
| :--- | :--- | :--- |
| **Ring Guard** | `ring_guard` | A full protective ring on arms bolted to the motor hub — the classic prop-guard. |
| **Ducted Shroud** | `ducted_shroud` | A deeper duct with a chamfered intake lip that follows the prop tip; adds protection and static thrust. |
| **Half Guard (bumper)** | `half_guard` | A 180° front bumper on a fan of arms — protects the leading edge at lower weight. |

## Parameters

| Group | Parameter | Default | Notes |
| :--- | :--- | :--- | :--- |
| Propeller | `prop_dia` | 127 mm | Prop diameter (5in = 127, 3in = 76 mm). |
| Propeller | `clearance` | 6.0 mm | Radial gap prop tip → ring inner wall. |
| Propeller | `ring_wall` | 3.0 mm | Ring wall thickness. |
| Propeller | `ring_height` | 10 mm | Ring height (ring / half modes). |
| Motor | `motor_pattern` | 16x16 | Square motor bolt pattern (`9x9` M2, `16x16`/`19x19` M3). |
| Motor | `hub_bore` | 10 mm | Central bore for the motor bell / shaft. |
| Arms | `arm_count` / `arm_width` | 3 / 6 mm | Spokes from hub to ring. |
| Duct | `duct_depth` / `duct_lip` | 16 / 3 mm | Ducted shroud height and intake lip (ducted mode). |

## Interfaces

The guard hosts the shared **motor bolt-pattern** CDG interface (the same square
4-hole pattern used by `motor-soft-mount` and `landing-skid`) and a **propeller
disc envelope** defined by `prop_dia + clearance`. Because the ring diameter is
derived from the real prop diameter, a guard generated for a 5-inch prop clears a
5-inch prop; scale `prop_dia` for any size.

The hub is sized to carry the pattern: its radius is at least the pattern's
half-diagonal plus the screw radius plus 2 mm of land (15.0 mm for 16x16, 17.1 mm
for 19x19, 9.6 mm for 9x9). Earlier versions sized the hub from the screw and
the bore alone (8 mm at the defaults), which put the 16x16 and 19x19 screw holes
outside the hub, so those patterns had no holes.

The ring is built as a watertight annulus (outer cylinder minus inner cylinder).
The ducted intake lip is a chamfer applied to the finished body, restricted to
the top-outer edge and wrapped in try/except so the shroud always exports as a
closed solid.

## Presets

- **5-inch Ring (16x16)** — reference freestyle prop guard.
- **3-inch Ducted (16x16)** — cinewhoop-style ducted shroud.
- **Toothpick Bumper (9x9)** — light half-ring front bumper for a micro.

## Hyperobject Profile

- **Domain:** commercial
- **CDG interfaces:**
  - **Motor Mount** (`bolt_pattern`, *16×16 / 19×19 / 9×9 brushless motor mount*)
    — the square 4-hole pattern + central bore, defined by `motor_pattern`,
    `prop_dia`, `hub_bore`. Interoperable with every FPV motor and the other
    drone-Commons parts on the same pattern.
  - **Hub Underside** (`bolt_pattern`, same pattern) — the hub's bottom face,
    so the guard can sit in a stack between an arm or soft mount and the motor.
  - **Propeller Disc Envelope** (`profile`, *internal*) — the swept prop-tip
    circle plus clearance, defined by `prop_dia`, `clearance`, `ring_wall`.
- **Material awareness:** `tolerance_by_material` is declared — tip clearance and
  ring wall are exposed so the fit and stiffness can be tuned per material.
- **Societal benefit:** prop guards prevent injuries and prop damage indoors and
  around people; on-demand guards sized to the exact prop and motor pattern make
  any craft safer to fly near others.
- **License:** CERN-OHL-W-2.0

## Mating frames (assemblies)

Both pattern interfaces carry a SEM-1 frame on the `ring_guard` part (mm, model
coordinates). Their size keys follow `motor_pattern` (`9x9` → `motor-mount-9x9-m2`,
`16x16` → `motor-mount-16x16-m3`, `19x19` → `motor-mount-19x19-m3`); symmetry 4;
`x_axis` `+x`.

| Interface | Origin | Normal | Polarity | Mates |
| :-- | :-- | :-- | :-- | :-- |
| `motor_mount` | `(0, 0, ring_height)`, the hub's top face | `+z` | male | a motor's base (female) |
| `hub_underside` | `(0, 0, 0)`, the hub's bottom face | `-z` | female | a male pattern below, such as `motor-soft-mount`'s plate or a frame's motor mount |

The frames are verified against the rendered part at the defaults and every
preset (`y4d-spec check --render`).

## Engine notes

- Engine: **CadQuery** (`main.py`). Exports STL / 3MF / STEP / GLB / GLTF / OBJ.
- Self-contained (sandbox-safe): parameters read via `PARAM(lambda: name,
  default)`; `target_part` dispatches which part to build; the final solid is
  assigned to `result`. The ring is a watertight annulus; the ducted lip chamfer
  is guarded with a non-fatal fallback. All modes render **watertight**; the
  large 5-inch ring stays under ~7 s.
