// ============================================================================
// cabinet_drawer.scad — Class IV: High-Density Archival Cabinet
// ============================================================================
// Reference: docs/RESEARCH.pdf §7 (High-Density Archival Systems)
//
// Sliding drawer with vertical slots inside a stackable shell. T-slot or
// L-rail profiles guide drawer insertion. Shell units interlock vertically
// with trapezoidal dovetail tabs.
//
// Parts:
//   render_mode 0 → drawer  (slide-holding tray that slides into shell)
//   render_mode 1 → shell   (outer housing with rail guides + stack tabs)
// ============================================================================

use <slide_lib.scad>

// ---------------------------------------------------------------------------
// Parameters (injected by platform via -D)
// ---------------------------------------------------------------------------

// --- Slide Standard ---
slide_standard = 0; // 0=ISO, 1=US, 2=Petrographic, 3=Supa Mega, 4=Custom
custom_slide_length = 76;
custom_slide_width = 26;
custom_slide_thickness = 1.0;

// Every additive join in this file penetrates its neighbour by this much, so
// the union is a volumetric fuse rather than a coincident-face kiss. Manifold
// tears the latter apart. 0.1 mm is far below any print resolution and leaves
// the part's extents unchanged.
RAIL_BITE = 0.1;

// --- Architecture ---
num_slots = 25; // Number of slide positions per drawer
density = 0; // 0=archival, 1=working, 2=staining, 3=mailer

// --- Tolerances ---
tolerance_xy = 0.4; // XY clearance (mm)
tolerance_z = 0.2; // Z / thickness clearance (mm)

// --- Structure ---
wall_thickness = 2.4; // Outer wall thickness (mm) — RESEARCH §7.3 min 2.4
floor_thickness = 2.0; // Floor thickness (mm)

// --- Cabinet-specific ---
rail_profile = 0; // 0=t_slot, 1=l_rail
backstop = 1; // 1=flexible tab prevents full extraction
drawers_per_shell = 5; // Number of drawer slots in shell

// --- Features ---
label_area = 1; // 1=generate debossed label recess

// --- Quality ---
fn = 0; // Resolution ($fn), 0 = auto

// --- Mode ---
render_mode = 0; // 0=drawer, 1=shell

// ---------------------------------------------------------------------------
// Resolution
// ---------------------------------------------------------------------------
$fn = fn > 0 ? fn : 32;

// ---------------------------------------------------------------------------
// Resolve Slide Dimensions
// ---------------------------------------------------------------------------
_slide = resolve_slide(
  slide_standard, custom_slide_length,
  custom_slide_width, custom_slide_thickness
);
_sl = _slide[0]; // slide length
_sw = _slide[1]; // slide width
_st = _slide[2]; // slide thickness

// ---------------------------------------------------------------------------
// Derived Dimensions (RESEARCH §7)
// ---------------------------------------------------------------------------
_rib_w = density_rib_width(density);
_slot_w = slot_width(_st, tolerance_z);
_pitch = pitch(_slot_w, _rib_w);

// Drawer slot depth: slides sit half-width deep
_slot_depth = _sw * 0.5;
_rib_height = _slot_depth;

// Drawer envelope
_drawer_x = (num_slots * _pitch) + _rib_w + (2 * 1.5); // 1.5mm thin walls
_drawer_y = _sl + tolerance_xy + 4; // slide length + front/back walls
_drawer_z = _rib_height + floor_thickness;

// Rail dimensions
_rail_h = 3.0; // rail height
_rail_w = 3.0; // rail width (T-slot head or L-rail shelf)
_rail_stem = 1.5; // T-slot stem width
_rail_clearance = tolerance_xy + 0.1; // RESEARCH §7.2 extra clearance

// Shell envelope (houses multiple drawers)
_shell_wall = wall_thickness;
_drawer_gap = 1.0; // clearance between drawer and shell
_slot_h = _drawer_z + _drawer_gap + _rail_h;
// Shell X must encompass drawer + rails on each side + gaps + walls
_shell_x = _drawer_x + 2 * (_rail_w + _drawer_gap) + 2 * _shell_wall;
_shell_y = _drawer_y + _shell_wall + _drawer_gap + 5; // extra at back for backstop
_shell_z = (drawers_per_shell * _slot_h) + _shell_wall * 2;

// Stack tab (RESEARCH §7.1)
_tab_base = 15;
_tab_top = 10;
_tab_h = 4;
_tab_depth = 8;
_tab_y = (_shell_y - _tab_depth) / 2;

// Backstop tab
_backstop_w = 10;
_backstop_h = _drawer_z * 0.6;
_backstop_t = 1.5;

// ---------------------------------------------------------------------------
// drawer — Slide-holding tray with rail flanges
// ---------------------------------------------------------------------------
module drawer() {
  // Shift to positive coordinates (compensate for left rail protrusion)
  // Left rail extent: -_rail_w (3.0) + head offset (-0.75) = -3.75
  translate([_rail_w + (_rail_w - _rail_stem) / 2, 0, 0]) {
    union() {
      // Base trough
      difference() {
        cube([_drawer_x, _drawer_y, _drawer_z]);

        // Hollow interior for slots
        translate([1.5, 1.5, floor_thickness])
          cube(
            [
              _drawer_x - 3,
              _drawer_y - 3,
              _rib_height + 1,
            ]
          );

        // Front label recess
        if (label_area == 1) {
          _label_w = min(30, _drawer_x * 0.5);
          _label_h = min(8, _drawer_z * 0.5);
          translate([(_drawer_x - _label_w) / 2, -0.01, (_drawer_z - _label_h) / 2])
            rotate([90, 0, 0])
              translate([0, 0, -0.4])
                label_recess(_label_w, _label_h, 0.5);
        }
      }

      // Rib array.
      //
      // Three coincident faces, all of them slivers in the export:
      //  * the ribs sat exactly ON the trough floor plane (z = floor_thickness),
      //  * their two ends sat exactly on the trough's front and back walls
      //    (y = 1.5 and y = 78.9, which is precisely the interior cut's span),
      //  * and the array runs to x = 60.0, which is exactly the interior cut's
      //    far wall, so the last rib's outer face was coplanar with it. (N slots
      //    genuinely need N+1 ribs -- a slot is the gap BETWEEN two ribs -- and
      //    the trough is sized `num_slots * pitch + rib_w` wide, so the last rib
      //    landing on the wall is by design, not an off-by-one.)
      // Manifold tore each of those into a zero-volume 2-face shell; the drawer
      // exported as 4 bodies, 3 of them degenerate, and not watertight.
      //
      // The ribs now sink RAIL_BITE into the floor and overrun the front and
      // back walls by RAIL_BITE at each end. Rib WIDTHS and PITCH are untouched
      // -- they set the slot the glass sits in -- so the far-wall coincidence is
      // closed by a separate filler block below rather than by fattening ribs.
      translate([1.5, 1.5 - RAIL_BITE, floor_thickness - RAIL_BITE]) {
        slot_array(
          count=num_slots,
          pitch=_pitch,
          height=_rib_height + RAIL_BITE,
          depth=_drawer_y - 3 + 2 * RAIL_BITE,
          root_w=_rib_w,
          tip_w=_rib_w * 0.7,
          chamfer_h=min(1.5, _rib_height * 0.1),
          tapered=true
        );
      }

      // The last rib's outer face lands exactly on the trough's far wall.
      // A thin filler spanning that plane turns the kiss into a fuse without
      // touching any rib's width or the slot pitch.
      translate([1.5 + num_slots * _pitch + _rib_w - RAIL_BITE,
                 1.5 - RAIL_BITE,
                 floor_thickness - RAIL_BITE])
        cube([2 * RAIL_BITE,
              _drawer_y - 3 + 2 * RAIL_BITE,
              _rib_height + RAIL_BITE]);

      // Rail flanges along drawer sides.
      //
      // Every one of these met the drawer body (and the T-slot's own stem met
      // its head and its bridge) on an EXACT plane -- a zero-overlap kiss.
      // Manifold, the backend the platform and `y4d-spec check --render` both
      // use, snaps near-coincident vertices and tears such a pair apart; the
      // drawer came out as 4 shells, not watertight, with the rails detached.
      //
      // Each rail now penetrates the body by RAIL_BITE and the T-slot's parts
      // overlap each other by the same amount, so every join is a volumetric
      // fuse. The rails' OUTER faces are untouched -- they are the running
      // surfaces that mate with the shell's channels, so their positions and
      // the drawer's overall extents are unchanged.
      if (rail_profile == 0) {
        // T-slot: stem + head
        // Left rail
        translate([-_rail_w, 0, _drawer_z / 2 - _rail_h / 2]) {
          // Stem, carried RAIL_BITE into the body (was flush at x = _rail_w).
          cube([_rail_stem + RAIL_BITE, _drawer_y, _rail_h]);
          // Head, overlapping the stem rather than abutting it.
          translate([-(_rail_w - _rail_stem) / 2, 0, _rail_h * 0.25])
            cube([_rail_w + RAIL_BITE, _drawer_y, _rail_h * 0.5]);

          // Bridge from the stem to the body: starts RAIL_BITE back inside the
          // stem and ends RAIL_BITE inside the body.
          translate([_rail_stem - RAIL_BITE, 0, 0])
            cube([_rail_w - _rail_stem + 2 * RAIL_BITE, _drawer_y, _rail_h]);
        }
        // Right rail. The stem starts RAIL_BITE inside the body and keeps its
        // original outer face, so the drawer's overall width is unchanged.
        translate([_drawer_x - RAIL_BITE, 0, _drawer_z / 2 - _rail_h / 2]) {
          cube([_rail_stem + RAIL_BITE, _drawer_y, _rail_h]);
          translate([_rail_stem - (_rail_w - _rail_stem) / 2,
                     0, _rail_h * 0.25])
            cube([_rail_w + RAIL_BITE, _drawer_y, _rail_h * 0.5]);
        }
      } else {
        // L-rail: simple shelf, each biting RAIL_BITE into the body.
        // Left rail
        translate([-_rail_w, 0, 0])
          cube([_rail_w + RAIL_BITE, _drawer_y, _rail_h]);
        // Right rail
        translate([_drawer_x - RAIL_BITE, 0, 0])
          cube([_rail_w + RAIL_BITE, _drawer_y, _rail_h]);
      }
    }
  }
}

// ---------------------------------------------------------------------------
// shell — Outer housing with rail channels and stack tabs
// ---------------------------------------------------------------------------
module shell() {
  // Position of drawer within shell
  _dx = _shell_wall + _drawer_gap + _rail_w;

  union() {
    difference() {
      // Outer box
      cube([_shell_x, _shell_y, _shell_z]);

      // Drawer slot cavities
      for (d = [0:drawers_per_shell - 1]) {
        _dz = _shell_wall + d * _slot_h;

        // Main drawer cavity (open at front)
        translate([_dx - _drawer_gap, -0.01, _dz])
          cube(
            [
              _drawer_x + _drawer_gap * 2,
              _drawer_y + _drawer_gap,
              _drawer_z + _drawer_gap,
            ]
          );

        // Rail channels
        if (rail_profile == 0) {
          // T-slot channels
          // Left channel
          translate([_dx - _rail_w - _rail_clearance - _drawer_gap, -0.01, _dz + _drawer_z / 2 - _rail_h / 2 - _rail_clearance / 2]) {
            cube([_rail_stem + _rail_clearance, _shell_y + 0.02, _rail_h + _rail_clearance]);
            translate([-(_rail_w - _rail_stem) / 2 - _rail_clearance / 2, 0, _rail_h * 0.25 - _rail_clearance / 2])
              cube([_rail_w + _rail_clearance, _shell_y + 0.02, _rail_h * 0.5 + _rail_clearance]);
          }
          // Right channel
          translate([_dx + _drawer_x + _drawer_gap, -0.01, _dz + _drawer_z / 2 - _rail_h / 2 - _rail_clearance / 2]) {
            cube([_rail_stem + _rail_clearance, _shell_y + 0.02, _rail_h + _rail_clearance]);
            translate([_rail_stem - (_rail_w - _rail_stem) / 2, 0, _rail_h * 0.25 - _rail_clearance / 2])
              cube([_rail_w + _rail_clearance, _shell_y + 0.02, _rail_h * 0.5 + _rail_clearance]);
          }
        } else {
          // L-rail channels
          translate([_dx - _rail_w - _rail_clearance - _drawer_gap, -0.01, _dz - _rail_clearance / 2])
            cube([_rail_w + _rail_clearance, _shell_y + 0.02, _rail_h + _rail_clearance]);
          translate([_dx + _drawer_x + _drawer_gap, -0.01, _dz - _rail_clearance / 2])
            cube([_rail_w + _rail_clearance, _shell_y + 0.02, _rail_h + _rail_clearance]);
        }
      }

      // Female stack tab recesses on bottom
      translate([_shell_x * 0.25 - _tab_base / 2 - 0.2, _tab_y - 0.2, -0.01])
        stack_tab_female(_tab_base, _tab_top, _tab_h, _tab_depth);
      translate([_shell_x * 0.75 - _tab_base / 2 - 0.2, _tab_y - 0.2, -0.01])
        stack_tab_female(_tab_base, _tab_top, _tab_h, _tab_depth);

      // Label area on shell front (one per drawer slot)
      if (label_area == 1) {
        for (d = [0:drawers_per_shell - 1]) {
          _dz = _shell_wall + d * _slot_h;
          _label_w = min(25, _shell_x * 0.3);
          _label_h = min(6, _slot_h * 0.3);
          translate([(_shell_x - _label_w) / 2, -0.01, _dz + (_slot_h - _label_h) / 2])
            rotate([90, 0, 0])
              translate([0, 0, -0.4])
                label_recess(_label_w, _label_h, 0.5);
        }
      }
    }

    // Backstop tabs at rear (one per drawer slot)
    if (backstop == 1) {
      for (d = [0:drawers_per_shell - 1]) {
        _dz = _shell_wall + d * _slot_h;
        translate(
          [
            _shell_x / 2 - _backstop_w / 2,
            _shell_y - _shell_wall - _backstop_t,
            _dz,
          ]
        )
          cube([_backstop_w, _backstop_t, _backstop_h]);
      }
    }

    // Stack tabs — male on top
    translate([_shell_x * 0.25 - _tab_base / 2, _tab_y, _shell_z])
      stack_tab_male(_tab_base, _tab_top, _tab_h, _tab_depth);
    translate([_shell_x * 0.75 - _tab_base / 2, _tab_y, _shell_z])
      stack_tab_male(_tab_base, _tab_top, _tab_h, _tab_depth);
  }
}

// ---------------------------------------------------------------------------
// Render Mode Dispatch
// ---------------------------------------------------------------------------
if (render_mode == 0) {
  drawer();
}

if (render_mode == 1) {
  shell();
}
