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
// Vertical overlap between consecutive stacked slabs, so their seams are
// volumetric rather than coincident faces.
lap = height / steps * 0.5;

// Gielis superformula: compute radius at angle phi
// r(phi) = ( |cos(m*phi/4)/a|^n2 + |sin(m*phi/4)/b|^n3 ) ^ (-1/n1)
function sf_r(phi, m, n1_v, n2_v, n3_v, a=1, b=1) =
    let(
        t1 = abs(cos(m * phi / 4) / a),
        t2 = abs(sin(m * phi / 4) / b)
    )
    pow(pow(t1, n2_v) + pow(t2, n3_v), -1 / n1_v);

// Generate superformula cross-section points at given scale
// `inset` is subtracted from the FINAL point radius, not from `r`. Subtracting
// it from `r` makes the effective wall scale with sf_r, so on a deeply lobed
// profile the valleys end up thinner than the nominal wall (1.06 mm against a
// nominal 1.5 mm at the sea_urchin preset).
function sf_shape(r, m, n1_v, n2_v, n3_v, pts=64, inset=0) =
    [for (i = [0:pts-1])
        let(phi = i * 360 / pts,
            sr = sf_r(phi, m, n1_v, n2_v, n3_v),
            rr = max(0.5, r * sr - inset))
        [rr * cos(phi), rr * sin(phi)]
    ];

// Vase profile: taper from narrow base to wider body, then narrow at top
function vase_radius(z, h, r) =
    let(t = z / h)
    r * (0.4 + 0.6 * sin(t * 180));  // sinusoidal taper

// `h_top` clamps the stack: pass a value below `height` to stop the void short
// of the rim so the vase closes over. Defaults to the full height for the
// outer shell.
// `r_inset` shrinks the cross-section radius by a CONSTANT amount rather than
// scaling it proportionally, so the wall thickness is the same at the
// superformula's lobe tips as in its valleys.
//
// `z_floor` raises the BOTTOM of the stack without shifting the profile. The
// inner void needs a floor of wall_thickness, but the old code got it with
// translate([0, 0, wall_thickness]) around the whole body -- which also
// shifted the PROFILE up, so on the vase's descending half the void's radius
// was evaluated a wall_thickness lower down, where the vase is WIDER. The
// wall there went negative (-0.14 mm and worse over the top third at the
// sea_urchin preset) and the void ate the top of the vase. Slicing the floor
// off instead keeps r(z) aligned between the two shells at every height.
module vase_body(h_top = height, r_inset = 0, z_floor = 0) {
    // Stack cross-sections with hull approximation.
    //
    // The `for` MUST be wrapped in union(): a bare for-loop emits each hull()
    // as a separate top-level child, so the "vase" was `steps` disjoint
    // sibling solids, never one shape (the sweep read 3/5/7/9 bodies across
    // the presets and none of them watertight).
    union() {
        for (i = [0 : steps - 1]) {
            z0 = i * height / steps;
            z1 = (i + 1) * height / steps;
            if (z0 < h_top && z1 > z_floor) {
                zt = min(z1, h_top);
                r0 = vase_radius(max(z0, z_floor), height, radius);
                r1 = vase_radius(zt, height, radius);

                // Each hull() slab starts at its own z0 but is extruded down
                // by `lap` at the bottom cap, so consecutive slabs OVERLAP
                // instead of meeting on a coincident face. Stacking them face
                // to face left every seam as a zero-thickness contact, which
                // is why the union above still returned several disjoint
                // bodies rather than one solid.
                zb = max(z_floor, z0 - lap);
                hull() {
                    translate([0, 0, zb])
                        linear_extrude(z0 - zb + 0.01)
                            polygon(sf_shape(r0, m1, n1, n2, n3, 64, r_inset));
                    translate([0, 0, zt])
                        linear_extrude(0.01)
                            polygon(sf_shape(r1, m1, n1, n2, n3, 64, r_inset));
                }
            }
        }
    }
}

module vase_hollow() {
    difference() {
        vase_body();
        // Two fixes here.
        //
        // 1. The void has to be CLAMPED to the vase's own height. The old
        //    scale() had a Z factor of 1, so the void was the full-height body
        //    merely shifted up by wall_thickness and overshot the rim into
        //    open space -- the 13.5 mm parity gap against the CadQuery side,
        //    which clamps its own void to height - 0.01
        //    (superformula.py:94). Clamped to the same value here: the void
        //    still reaches the rim, so the vase is OPEN at the top the way a
        //    vase must be. Stopping it lower would seal the interior into an
        //    undrainable cavity (a 2-body render, one of them negative).
        //
        // 2. The old scale() shrank the cross-section PROPORTIONALLY. On a
        //    lobed superformula profile that is not a constant wall: the lobe
        //    tips, being furthest out, lose the most material and the wall
        //    there goes to zero, splitting the shell into one piece per lobe
        //    (4 bodies at m1=5, 10 at m1=8). Inset the radius by a constant
        //    instead, which is what superformula.py does.
        {
            vase_body(height, wall_thickness, wall_thickness);
            // OVERSHOOT the rim. Ending the void exactly at the top face
            // leaves a coincident face there, which OCCT/Manifold resolves as
            // a sealed cavity: the render came back as 2 bodies, the inner one
            // NEGATIVE (an undrainable void, and unprintable). Cap the void
            // with a slab of the topmost cross-section that runs clear past
            // the rim so the bore breaks through and the vase is open.
            // Sized on the OUTER body's own top radius so the cap is never
            // wider than the rim it breaks through, and started just BELOW
            // that rim (the void's own top slab already reaches it) so it only
            // continues the bore upward instead of trimming the vase. Starting
            // it a full wall_thickness down, or sizing it on a lower slab's
            // wider radius, shaved the top off wherever the profile narrows
            // toward the rim -- sea_urchin lost 11.4 mm of its 60 mm height.
            translate([0, 0, height - wall_thickness])
                linear_extrude(wall_thickness + 2)
                    polygon(sf_shape(vase_radius(height, height, radius),
                                     m1, n1, n2, n3, 64, wall_thickness));
        }
    }
}

// --- Render ---
if (render_mode == 0) {
    vase_hollow();
}
