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

$fn = fn > 0 ? fn : 64;
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
