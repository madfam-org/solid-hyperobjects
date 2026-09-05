// Yantra4D wrapper — Herringbone Gear (BOSL2)
// BOSL2 `gears.scad` wrapper; no MCAD code. Involute parameterization
// (module, teeth, pressure angle) follows ISO 53 / DIN 867.
// BOSL2 renders herringbone natively in a single call (herringbone=true + helical angle)
include <BOSL2/std.scad>
include <BOSL2/gears.scad>

// Parameters (injected by Yantra4D platform via -D flags)
teeth_count = 20;
module_size = 2; // gear module (mm per tooth)
pressure_angle = 20; // degrees
thickness = 10; // total gear face width (mm)
bore_diameter = 5; // shaft bore (mm)
helical_angle = 30; // helix angle (degrees)
fn = 0;
render_mode = 0;

$fn = fn > 0 ? fn : 32;

// BOSL2 herringbone: single call, symmetric halves, no manual mirror() needed
spur_gear(
  mod=module_size,
  teeth=teeth_count,
  thickness=thickness,
  shaft_diam=bore_diameter,
  pressure_angle=pressure_angle,
  helical=helical_angle,
  herringbone=true
);
