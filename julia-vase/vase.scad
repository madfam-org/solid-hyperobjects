// Yantra4D wrapper — Julia Fractal Vase
// Single mode: vase
// Revolves a sinusoidal-wave wall profile around Z axis.

height = 150;
base_radius = 40;
twist_angle = 360;
wave_frequency = 5;
wave_amplitude = 10;
wall_thickness = 2;
fn = 64;
resolution = 100;
render_mode = 0;

// Angular tessellation of the rotate_extrude.
//
// vase.py revolves the same profile with CadQuery's .revolve(), which produces
// an EXACT analytic surface of revolution -- no angular sampling at all. A
// 64-gon inscribed in the vase's peak radius therefore always measures small:
// at preset fractal_complex (peak radius 52) it read 103.95 x 103.92 against
// the true 104.0, a 0.080 mm bounding-box gap, just past the 0.05 mm parity
// band. Defaults sat inside the band only because the peak radius is smaller
// there -- the same error was always present.
//
// Refine to at least 256 facets: the sagitta at r = 52 is
// 52*(1 - cos(180/256)) = 3.9e-4 mm, so the worst-case bounding-box delta is
// ~8e-4 mm, two orders inside the band and independent of facet phase.
// max() rather than a plain multiply so a user-supplied fn is still honoured
// as a floor; the declared default of 64 is untouched.
$fn = fn > 0 ? max(fn, 256) : 256;
steps = max(20, resolution);

// Radius varies sinusoidally along height
function vase_radius(z) =
    base_radius + wave_amplitude * sin(z / height * wave_frequency * 180);

// Build the 2D wall profile for revolution (outer + inner in XZ plane)
outer_pts = [for (i = [0:steps]) let(z = i * height / steps)
    [vase_radius(z), z]];

inner_pts = [for (i = [steps:-1:0]) let(z = i * height / steps)
    [max(1, vase_radius(z) - wall_thickness), z]];

profile = concat(outer_pts, inner_pts);

// --- Render ---
if (render_mode == 0) {
    rotate_extrude(angle = 360)
        polygon(profile);
}
