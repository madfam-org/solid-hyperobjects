// Yantra4D Superformula Vase
// Generates cross-sections using Gielis superformula
// Extrudes with varying parameters along height for vase shape

// --- Parameters (overridden by platform) ---
m1 = 5;
m2 = 5;
n1 = 2;
n2 = 7;
n3 = 7;
height = 100;
wall_thickness = 2;
radius = 40;
fn = 0;
render_mode = 0;

$fn = fn > 0 ? fn : 48;
steps = max(20, floor(height / 3));

// Gielis superformula: compute radius at angle phi
// r(phi) = ( |cos(m*phi/4)/a|^n2 + |sin(m*phi/4)/b|^n3 ) ^ (-1/n1)
function sf_r(phi, m, n1_v, n2_v, n3_v, a=1, b=1) =
    let(
        t1 = abs(cos(m * phi / 4) / a),
        t2 = abs(sin(m * phi / 4) / b)
    )
    pow(pow(t1, n2_v) + pow(t2, n3_v), -1 / n1_v);

// Generate superformula cross-section points at given scale
function sf_shape(r, m, n1_v, n2_v, n3_v, pts=64) =
    [for (i = [0:pts-1])
        let(phi = i * 360 / pts,
            sr = sf_r(phi, m, n1_v, n2_v, n3_v))
        [r * sr * cos(phi), r * sr * sin(phi)]
    ];

// Vase profile: taper from narrow base to wider body, then narrow at top
function vase_radius(z, h, r) =
    let(t = z / h)
    r * (0.4 + 0.6 * sin(t * 180));  // sinusoidal taper

module vase_body() {
    // Stack cross-sections with hull approximation
    for (i = [0 : steps - 1]) {
        z0 = i * height / steps;
        z1 = (i + 1) * height / steps;
        r0 = vase_radius(z0, height, radius);
        r1 = vase_radius(z1, height, radius);

        hull() {
            translate([0, 0, z0])
                linear_extrude(0.01)
                    polygon(sf_shape(r0, m1, n1, n2, n3));
            translate([0, 0, z1])
                linear_extrude(0.01)
                    polygon(sf_shape(r1, m1, n1, n2, n3));
        }
    }
}

module vase_hollow() {
    difference() {
        vase_body();
        translate([0, 0, wall_thickness])
            scale([(radius - wall_thickness)/radius,
                   (radius - wall_thickness)/radius,
                   1])
                vase_body();
    }
}

// --- Render ---
if (render_mode == 0) {
    vase_hollow();
}
