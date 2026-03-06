# Parametric Hinge Hyperobject

Parametric print-in-place hinges for mechanical assemblies. Three hinge types cover the most common rotary joint needs: living hinges for simple flex, pin hinges for structural rotation, and ball joints for multi-axis articulation.

## Modes

| Mode | Description | Key Parameters |
|------|-------------|----------------|
| Living Hinge | Thin-web flex hinge between two flat leaves | `hinge_thickness`, `bend_angle` |
| Pin Hinge | Multi-knuckle revolute joint with central pin | `pin_diameter`, `num_knuckles`, `clearance` |
| Ball Joint | Print-in-place ball-and-socket | `socket_diameter`, `clearance` |

All modes share `hinge_width` and `leaf_length` for consistent mounting dimensions.

## Hyperobject Profile

- **Domain**: Industrial
- **CDG Interfaces**:
  - `revolute_axis` (rail) -- pin diameter and hinge width define the rotation axis
  - `mounting_surface` (surface) -- leaf dimensions define attachment geometry
- **Material Awareness**: Shrinkage compensation enabled, tolerance varies by material
- **Commons License**: CERN-OHL-W-2.0

## Print Tips

- **PLA**: Good for living hinges at low cycle counts (~200 flex cycles before fatigue). Use 0.5-0.8mm web thickness.
- **TPU/TPE**: Best for high-cycle living hinges (thousands of cycles). Web thickness can go down to 0.3mm.
- **PETG**: Good structural choice for pin hinges and ball joints. More heat-resistant than PLA.
- **Clearance**: Start with 0.4mm clearance for pin hinge and ball joint. Increase to 0.5-0.6mm if parts fuse during printing.
- **Layer height**: Use 0.15-0.2mm layers for ball joint socket to get smooth articulation.
- **Orientation**: Print all modes flat on the build plate. Living hinge web must be parallel to bed for proper layer adhesion.

## OpenSCAD Libraries

Uses [BOSL2](https://github.com/BelfrySCAD/BOSL2) for geometry primitives (`cuboid`, `cyl`, `sphere`).
