// Yantra4D Superformula Vase
// Generates cross-sections using Gielis superformula
// Skins them into an open-topped hollow vase along the height

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
pts = 64;

// Smallest radius any sampled point may collapse to. The inner void is inset
// by a CONSTANT wall_thickness; where a superformula valley is itself narrower
// than the wall an unclamped inset would go negative and turn the ring inside
// out. Flooring it keeps the void strictly inside the outer surface, which is
// what keeps deeply lobed presets (sea_urchin, m1 = 12) a single body at their
// own declared 1.5 mm wall. Mirrors MIN_RADIUS in superformula.py.
min_radius = 0.5;

// Gielis superformula: compute radius at angle phi
// r(phi) = ( |cos(m*phi/4)/a|^n2 + |sin(m*phi/4)/b|^n3 ) ^ (-1/n1)
function sf_r(phi, m, n1_v, n2_v, n3_v, a=1, b=1) =
    let(
        t1 = abs(cos(m * phi / 4) / a),
        t2 = abs(sin(m * phi / 4) / b)
    )
    pow(pow(t1, n2_v) + pow(t2, n3_v), -1 / n1_v);

// Vase profile: taper from narrow base to wider body, then narrow at top
function vase_radius(z, h, r) =
    let(t = z / h)
    r * (0.4 + 0.6 * sin(t * 180));  // sinusoidal taper

// One sampled cross-section as 3D points at height z.
// `z_at` overrides the height the PROFILE is evaluated at without moving the
// points in Z; the void's overshoot cap uses it to carry the rim section
// straight up past the top of the vase.
// `inset` is subtracted from the FINAL point radius, not from the profile
// radius: subtracting it before the sf_r multiply makes the effective wall
// scale with sf_r, so on a deeply lobed profile the valleys come out thinner
// than the nominal wall.
function ring(z, h, r, m, n1_v, n2_v, n3_v, inset=0, z_at=-1) =
    let(rz = vase_radius(z_at < 0 ? z : z_at, h, r))
    [for (i = [0 : pts - 1])
        let(phi = i * 360 / pts,
            rr = max(min_radius, rz * sf_r(phi, m, n1_v, n2_v, n3_v) - inset))
        [rr * cos(phi), rr * sin(phi), z]
    ];

// Flatten a list of rings (bottom to top) into one point list.
function flatten_rings(rings) =
    [for (ri = [0 : len(rings) - 1]) for (i = [0 : pts - 1]) rings[ri][i]];

// Triangles skinning consecutive rings, plus a centroid fan closing each end.
// OpenSCAD's polyhedron() wants each face wound CLOCKWISE when seen from
// OUTSIDE the solid — the opposite of the counter-clockwise convention the
// CadQuery side builds its shell with. Winding these the CadQuery way renders
// without error but inside-out, and difference() then keeps the void instead
// of removing it (2 bodies, both negative, 24x the volume).
// This is a genuine LOFT of the sampled sections. The previous version hulled
// each consecutive pair, and a convex hull cannot be concave: it filled in the
// superformula's lobes, inflating this side's outer body to 1.38e6 mm3 against
// 769e3 for the true polygon on the CadQuery side — the sweep's parity gap.
// The bare `for` that emitted each hull() as a separate top-level child is
// gone with it (the sweep read 3/5/7/9 disjoint bodies, none watertight).
function skin_faces(nr) =
    let(nv = nr * pts, cb = nv, ct = nv + 1)
    concat(
        [for (ri = [0 : nr - 2]) for (i = [0 : pts - 1])
            each [
                [ri*pts + i, (ri+1)*pts + (i+1)%pts, ri*pts + (i+1)%pts],
                [ri*pts + i, (ri+1)*pts + i, (ri+1)*pts + (i+1)%pts]
            ]
        ],
        // bottom cap, wound so its normal points down and out of the solid
        [for (i = [0 : pts - 1]) [cb, i, (i+1)%pts]],
        // top cap, wound the other way
        [for (i = [0 : pts - 1]) [ct, (nr-1)*pts + (i+1)%pts, (nr-1)*pts + i]]
    );

module skin(rings) {
    nr = len(rings);
    polyhedron(
        points = concat(flatten_rings(rings),
                        [[0, 0, rings[0][0][2]], [0, 0, rings[nr-1][0][2]]]),
        faces = skin_faces(nr),
        convexity = 10
    );
}

// Z values of the outer shell's cross-sections.
function outer_zs() = [for (i = [0 : steps]) i * height / steps];

// Z values of the void's cross-sections: floored at wall_thickness so the vase
// has a base, then the outer shell's own z values above it, so the two
// surfaces sample the profile at the SAME height and the wall is constant.
function void_zs() =
    let(zs = outer_zs(),
        above = [for (z = zs) if (z > wall_thickness) z],
        base = concat([wall_thickness], above))
    (base[len(base) - 1] < height) ? concat(base, [height]) : base;

module vase_body() {
    skin([for (z = outer_zs())
             ring(z, height, radius, m1, n1, n2, n3)]);
}

module vase_void() {
    zs = void_zs();
    // The last ring repeats the RIM cross-section one millimetre above the
    // top, so the cut breaks clean through the top face. Ending the void flush
    // with the rim leaves a coincident face that resolves as a sealed,
    // undrainable cavity — a 2-body render with one NEGATIVE body, which is
    // exactly what the CadQuery side was shipping.
    skin(concat(
        [for (z = zs) ring(z, height, radius, m1, n1, n2, n3, wall_thickness)],
        [ring(height + 1, height, radius, m1, n1, n2, n3, wall_thickness, height)]
    ));
}

module vase_hollow() {
    difference() {
        vase_body();
        vase_void();
    }
}

// --- Render ---
if (render_mode == 0) {
    vase_hollow();
}
