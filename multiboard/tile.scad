// Modular Wall Tile (25 mm threaded grid) — Yantra4D Hyperobject Cartridge
// OpenSCAD geometry, builtins only. No library includes.
//
// A flat wall panel carrying a 25 mm square grid of internally threaded bores.
// Accessories screw straight into the grid: the thread is both the fastening and
// the locating feature, so no separate hardware is needed. Panels butt edge to
// edge and the small interior-node threads carry the seam connectors that keep
// the grid continuous across a joint.
//
// MADFAM clean-room implementation (ADR-021 §4). The INTERFACE — the 25 mm grid
// pitch, the two internal trapezoidal thread classes and the panel thickness —
// is implemented from measured dimensions so third-party 25 mm-grid accessories
// mate. The FORM — the plate silhouette, its corner treatment and the rear
// relief — is our own design and deliberately differs from any prior tile.
// See NOTICE.
//
// Why OpenSCAD, and why linear_extrude:
//   The thread is a TRUE HELIX, not a stack of concentric rings. In OpenSCAD a
//   `linear_extrude(height=h, twist=-360*h/pitch, slices=…)` of the 2-D tooth
//   profile IS a helix of that pitch — one extrusion per bore, full depth, no
//   sweep and no library. Manifold cuts them from the plate in seconds where a
//   B-Rep kernel's boolean against a swept helix costs minutes and fragments
//   the plate. That trade is what put this mode on this kernel.

// ── Manifest parameters (injected by the platform as -D name=value) ─────────
x_cells     = 4;          // cells along X
y_cells     = 4;          // cells along Y
cell_size   = 25;         // grid module, mm — see the clamp below
height      = 6.4;        // panel thickness, mm
fn          = 0;          // tessellation; 0 = the cartridge chooses

// ── The interface, as measured (mm). NOT user parameters: an accessory mates
//    to these, so they are frozen constants of the standard. ────────────────
GRID_PITCH        = 25.0;   // cell module, both axes, both hole classes
PRIMARY_MAJOR_D   = 22.54;  // cell-centre bore, thread major diameter
PRIMARY_MINOR_D   = 20.15;  // cell-centre bore, thread minor diameter
PRIMARY_PITCH     = 2.5;    // cell-centre thread pitch
SECONDARY_MAJOR_D = 6.95;   // interior-node bore, thread major diameter
SECONDARY_MINOR_D = 4.48;   // interior-node bore, thread minor diameter
SECONDARY_PITCH   = 3.0;    // interior-node thread pitch
FLANK_ANGLE       = 29.0;   // trapezoidal flank angle, both classes

// ── Our form constants (FORM, not interface — see NOTICE) ──────────────────
// These were user parameters in an earlier draft. They are constants here
// because the manifest contract fixes the parameter space, and because a form
// the maker can dial away is not much of a design decision.
TAB_RATIO    = 0.26;   // boundary tab radius, as a fraction of the grid module
CORNER_FLAT  = 6.0;    // 45° plate-corner flat, FIXED mm, independent of the cell
RELIEF_FRAC  = 0.12;   // rear cone relief depth, as a fraction of the thickness
RELIEF_MAX   = 0.8;    // …capped here, mm

// ── Clamped working values ─────────────────────────────────────────────────
NX = max(1, min(12, round(x_cells)));
NY = max(1, min(12, round(y_cells)));
H  = max(4, min(10, height));

// `cell_size` spaces the grid. The 25 mm module is the INTERFACE — an accessory
// printed for a 25 mm grid does not mate to a 30 mm one — so 25 is the default
// and the value the interface tables are measured at. Above 25 the same bores
// simply sit further apart, which is valid geometry and a real (if
// non-interoperable) panel; below 25 the Ø22.54 bore is wider than the cell and
// there is no material left between neighbouring bores, which is why the
// baseline fragmented into 25 separate bodies at 20 mm.
//
//   cell 20: edge web −1.27 mm, bore-to-bore wall −2.54 mm  → impossible
//   cell 25: edge web  1.23 mm, bore-to-bore wall  2.46 mm  → the interface
//   cell 35: edge web  6.23 mm, bore-to-bore wall 12.46 mm  → valid, wider
//
// So the value is clamped at the geometric floor rather than fragmenting the
// plate, and project.json carries a `severity: error` constraint that says so
// in the UI before a render is ever queued. Every point in the declared range
// therefore produces one watertight body — the commons bar, which the baseline
// did not meet.
CELL_FLOOR = GRID_PITCH;
PITCH = max(CELL_FLOOR, min(35, cell_size));

// Tessellation. Two knobs, and they do different jobs — keeping them separate
// is what makes the default tile affordable:
//
//   NSEG — facets per turn of the 2-D tooth profile. Sets RADIAL accuracy (how
//          round the bore is). Cheap: the facet count grows linearly in it.
//   SLPT — extrusion layers per turn of the helix. Sets AXIAL fidelity (how
//          smoothly the thread advances). Expensive: mesh size grows linearly
//          in it too, but from a much larger constant, because every layer
//          duplicates the whole profile ring.
//
// Measured at the 4 × 4 default, Manifold, on this cartridge (the study is in
// docs/CLEANROOM-VERIFICATION.md). Mesh size tracks SLPT, not NSEG: at SLPT 16,
// NSEG 16 → 48 costs 15.8 → 24.9 MB; at NSEG 48, SLPT 16 → 48 costs
// 24.9 → 71.5 MB. Accuracy tracks SLPT as well, so the pair must rise together
// and there is no gain in spending NSEG alone.
//
// 32/32 is the chosen operating point: every interface diameter inside
// ±0.05 mm, 36.3 MB and 3.9 s at the default tile, 562 MB and 39.5 s at the
// 12 × 12 × 10 mm max-range corner. An earlier draft ran 48 layers per turn and
// was dimensionally no better where it counts while costing 71.5 MB at the
// default and 1.1 GB at the corner — large enough to stall a mesh reader.
NSEG = (fn <= 0) ? 32 : max(16, min(128, round(fn)));
SLPT = NSEG;   // layers per turn; tied to NSEG so `fn` moves both coherently

W = NX * PITCH;
D = NY * PITCH;

// ── Thread geometry ─────────────────────────────────────────────────────────

// A tessellated arc from a0 to a1 at nominal radius r, at most `step` degrees
// per segment. `bias` decides where the polyline sits relative to r.
//
// A slice of a tessellated arc does not read one radius: it reads a BAND
// between the polyline's VERTICES (at the build radius rc) and its MID-CHORDS
// (at rc·cos(da/2)), whose mean is rc·(1 + cos(da/2))/2. Both arcs are
// therefore built at the rc that puts that mean on the nominal r, so the
// measured thread lands on the standard rather than one chord-sag inside it.
//
// `bias` distinguishes the two arcs' TWIST handling:
//   1 — the CREST. Its facets run with the helix, so the in-plane band above is
//       the whole story.
//   0 — the ROOT. A horizontal cut here also crosses the twist between two
//       extrusion layers, which sweeps the band further inward. The extreme of
//       that sweep is a further cos(tps/2), but the extreme is not what a
//       mating screw bears on and not what the measurement reports — the band's
//       CENTRE is. Compensating by the full cos(tps/2) therefore overshoots and
//       leaves the root reading wide (+0.079 mm at 32 layers per turn, measured);
//       compensating by none of it leaves it narrow (−0.018 mm). The geometric
//       mean of the two, sqrt(cos(tps/2)), centres the band: +0.031 mm, the best
//       of the three and comfortably inside the ±0.05 mm interface tolerance.
//       That is what the 0.5 exponent is — the midpoint of a band, not a fudge
//       factor fitted to a number.
ROOT_TWIST_EXP = 0.5;

function arc_pts(r, a0, a1, step, tps, bias) =
    let(k  = max(1, ceil(abs(a1 - a0) / step)),
        da = (a1 - a0) / k,
        band = (1 + cos(da / 2)) / 2,
        rc = (bias == 1) ? r / band
                         : r / (band * pow(cos(tps / 2), ROOT_TWIST_EXP)))
    [ for (i = [0:k]) [ rc * cos(a0 + da * i), rc * sin(a0 + da * i) ] ];

// The 2-D tooth: one trapezoidal thread turn seen in plan. Sweeping this with a
// twist of one full turn per `pitch` of rise gives the helical thread. The
// axial rise of one flank, `run`, becomes an ANGULAR width because the twist
// converts rise into rotation at exactly 360°/pitch.
module thread_profile(d_maj, d_min, pitch, n, tps) {
    step   = 360 / n;
    run    = (d_maj - d_min) / 2 * tan(FLANK_ANGLE / 2);   // axial mm
    flat   = max(0.05, (pitch - 2 * run) / 2);             // axial mm
    a_run  = 360 * run  / pitch;                           // as an angle
    a_flat = 360 * flat / pitch;
    polygon(points = concat(
        arc_pts(d_maj / 2, a_run,              a_run + a_flat, step, tps, 1),
        arc_pts(d_min / 2, 2 * a_run + a_flat, 360,            step, tps, 0)
    ));
}

// The cutting tool for one bore: a full-depth true helix.
// `slices` is what makes it a helix rather than a prism: the extrusion is
// twisted through one full turn per `pitch` of rise, and each layer is a
// rotated copy of the tooth. SLPT layers per turn, so the layer count follows
// the bore's depth in turns, not its diameter.
module thread_tool(d_maj, d_min, pitch, h, n) {
    turns = h / pitch;
    sl    = max(8, ceil(turns * SLPT));   // extrusion layers over the whole bore
    tps   = 360 * turns / sl;             // twist per layer, degrees
    linear_extrude(height = h, twist = -360 * turns, slices = sl, convexity = 10)
        thread_profile(d_maj, d_min, pitch, n, tps);
}

// ── Our silhouette (FORM — deliberately not the baseline's) ─────────────────
//
// The baseline the interface was measured from is a plain rectangle whose four
// vertical corners carry an octagonal chamfer scaled FROM the cell module. This
// is a different object:
//
//   * The perimeter is CASTELLATED: a rounded tab of material stands proud of
//     the rectangle at every grid node on the boundary, so the silhouette reads
//     as a row of lugs rather than a straight line. Each tab is centred on a
//     seam node, so a connector at an edge sits in solid material with metal all
//     round it instead of on a knife edge — the tab is what makes an edge seam
//     as strong as an interior one.
//   * The four plate corners take a 45° flat of FIXED millimetres, independent
//     of the grid module. Decoupling the corner treatment from the cell size is
//     itself a departure: the baseline derived its chamfer from the cell.
//
// The tile is additive at the boundary and never subtractive: the cell-centre
// bore already comes within about 1.2 mm of a straight edge, so a silhouette
// that cut INTO the rectangle would sever the boundary web and fragment the
// plate. Ours only adds.
module plate_blank() {
    tr = PITCH * TAB_RATIO;
    union() {
        cube([W, D, H]);
        for (i = [0:NX]) {
            translate([i * PITCH, 0, 0]) cylinder(h = H, r = tr, $fn = NSEG);
            translate([i * PITCH, D, 0]) cylinder(h = H, r = tr, $fn = NSEG);
        }
        for (j = [0:NY]) {
            translate([0, j * PITCH, 0]) cylinder(h = H, r = tr, $fn = NSEG);
            translate([W, j * PITCH, 0]) cylinder(h = H, r = tr, $fn = NSEG);
        }
    }
}

// The 45° corner flats, as four cutting wedges reaching well past any corner tab.
module corner_wedges() {
    c   = CORNER_FLAT;
    far = c + PITCH;
    for (k = [[0, 0,  1,  1], [1, 0, -1,  1], [1, 1, -1, -1], [0, 1,  1, -1]]) {
        ax = k[0] * W;  ay = k[1] * D;
        sx = -k[2];     sy = -k[3];
        translate([0, 0, -1]) linear_extrude(height = H + 2)
            polygon(points = [[ax + sx * far, ay - sy * c],
                              [ax + sx * far, ay + sy * far],
                              [ax - sx * c,   ay + sy * far]]);
    }
}

// ── Build ───────────────────────────────────────────────────────────────────
OVER = 1.0;   // the bore overshoots both faces so the cut is clean through

difference() {
    difference() {
        plate_blank();
        corner_wedges();
    }

    // Primary thread at every cell centre: x_cells × y_cells bores.
    for (i = [0:NX - 1]) for (j = [0:NY - 1])
        translate([(i + 0.5) * PITCH, (j + 0.5) * PITCH, -OVER])
            thread_tool(PRIMARY_MAJOR_D, PRIMARY_MINOR_D, PRIMARY_PITCH,
                        H + 2 * OVER, NSEG);

    // Secondary thread at the INTERIOR grid intersections only:
    // (x_cells − 1) × (y_cells − 1) bores, 9 at defaults. A boundary node
    // carries a tab, not a bore — the seam connector threads into the interior
    // node of the panel it is tying to.
    if (NX > 1 && NY > 1)
        for (i = [1:NX - 1]) for (j = [1:NY - 1])
            translate([i * PITCH, j * PITCH, -OVER])
                thread_tool(SECONDARY_MAJOR_D, SECONDARY_MINOR_D, SECONDARY_PITCH,
                            H + 2 * OVER, NSEG);

    // Rear relief (FORM): every cell-centre bore is coned on the back face so a
    // screw starts square without a bench chamfer. The baseline has no relief.
    dep = min(RELIEF_MAX, H * RELIEF_FRAC);
    for (i = [0:NX - 1]) for (j = [0:NY - 1])
        translate([(i + 0.5) * PITCH, (j + 0.5) * PITCH, H - dep])
            cylinder(h = dep + 0.01,
                     r1 = PRIMARY_MAJOR_D / 2,
                     r2 = PRIMARY_MAJOR_D / 2 + dep,
                     $fn = NSEG);
}
