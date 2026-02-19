# Microscope Slide Holder

Parametric microscope slide retention system — trays, boxes, staining racks, and archival cabinets

Official Visualizer and Configurator: Yantra4D

*Sistema paramétrico de retención de portaobjetos de microscopio — bandejas, cajas, bastidores de tinción y gabinetes archivadores

Visualizador y configurador oficial: Yantra4D*

**Version**: 2.0.0  
**Slug**: `microscope-slide-holder`

## Modes

| ID | Label | SCAD File | Parts |
|---|---|---|---|
| `box` | Storage Box | `box.scad` | box_base, box_lid |
| `tray` | Horizontal Tray | `tray.scad` | tray |
| `staining_rack` | Staining Rack | `staining_rack.scad` | rack |
| `cabinet_drawer` | Cabinet Drawer | `cabinet_drawer.scad` | drawer, shell |

## Parameters

| Name | Type | Default | Range | Description |
|---|---|---|---|---|
| `slide_standard` | slider | 0 | 0–4 | 0=ISO 76×26, 1=US 76.2×25.4, 2=Petrographic 46×27, 3=Supa Mega 75×50, 4=Custom |
| `custom_slide_length` | slider | 76 | 40–100 (step 0.1) | Only used when Standard = 4 (Custom) |
| `custom_slide_width` | slider | 26 | 15–55 (step 0.1) | Only used when Standard = 4 (Custom) |
| `custom_slide_thickness` | slider | 1.0 | 0.5–2.0 (step 0.1) | Only used when Standard = 4 (Custom) |
| `num_slots` | slider | 25 | 1–100 | Number of slide positions |
| `tolerance_xy` | slider | 0.4 | 0.1–1.0 (step 0.05) | Horizontal clearance for FDM printing |
| `tolerance_z` | slider | 0.2 | 0.05–0.5 (step 0.05) | Slide thickness clearance |
| `wall_thickness` | slider | 2.0 | 1.2–4.0 (step 0.2) | Outer wall thickness |
| `label_area` | checkbox | Yes |  | Generate debossed label recess |
| `fn` | slider | 0 | 0–64 (step 8) | 0 = auto; higher = more detail but slower |
| `rib_profile` | slider | 0 | 0–1 | 0=tapered (guides insertion), 1=rectangular (simpler) |
| `rib_width` | slider | 1.8 | 0.8–3.0 (step 0.1) | Rib root width |
| `density` | slider | 1 | 0–3 | 0=archival (2.6mm), 1=working (3.5mm), 2=staining (5mm), 3=mailer (6mm) |
| `lid_latch` | slider | 0 | 0–2 | 0=snap-fit, 1=magnetic, 2=none |
| `stackable` | checkbox | Yes |  | Generate stacking lip and groove |
| `numbering_start` | slider | 1 | 0–999 | First slot number for debossed labels (requires $fn > 0) |
| `tray_columns` | slider | 5 | 1–10 | Columns of slide pockets |
| `tray_rows` | slider | 2 | 1–5 | Rows of slide pockets |
| `finger_notch` | checkbox | Yes |  | Cylindrical notch for easy slide removal |
| `anti_capillary` | checkbox | Yes |  | Floor rails to break vacuum seal under slide |
| `handle` | checkbox | Yes |  | Generate carrying handle on rack |
| `drainage_angle` | slider | 5 | 0–15 | Slope for fluid runoff |
| `open_bottom` | checkbox | Yes |  | Crossbar floor instead of solid (better fluid circulation) |
| `rail_profile` | slider | 0 | 0–1 | 0=T-slot (more secure), 1=L-rail (simpler) |
| `backstop` | checkbox | Yes |  | Flexible tab prevents full drawer extraction |
| `drawers_per_shell` | slider | 5 | 1–10 | Number of drawer slots in the shell |

## Presets

- **Standard 25-Place Box**
  `slide_standard`=0, `num_slots`=25, `density`=1, `lid_latch`=0, `stackable`=Yes
- **100-Place Archival Box**
  `slide_standard`=0, `num_slots`=100, `density`=0, `stackable`=Yes, `lid_latch`=0
- **Petrographic Box (20)**
  `slide_standard`=2, `num_slots`=20, `density`=1
- **Drying Tray (5×2)**
  `slide_standard`=0, `num_slots`=10, `tray_columns`=5, `tray_rows`=2, `anti_capillary`=Yes, `finger_notch`=Yes
- **20-Slide Staining Rack**
  `slide_standard`=0, `num_slots`=20, `handle`=Yes, `drainage_angle`=5
- **Compact 5-Slide Box**
  `slide_standard`=1, `num_slots`=5, `density`=1, `stackable`=No
- **Supa Mega Tray (2×2)**
  `slide_standard`=3, `num_slots`=4, `tray_columns`=2, `tray_rows`=2, `finger_notch`=Yes
- **Cabinet Unit (5 drawers)**
  `slide_standard`=0, `num_slots`=25, `drawers_per_shell`=5, `rail_profile`=0

## Parts

| ID | Label | Default Color |
|---|---|---|
| `box_base` | Box Base | `#4a90d9` |
| `box_lid` | Box Lid | `#6b7280` |
| `tray` | Tray | `#4a90d9` |
| `rack` | Rack | `#e5e7eb` |
| `drawer` | Drawer | `#4a90d9` |
| `shell` | Shell | `#2d2d2d` |

## Constraints

- `num_slots >= 1` — At least 1 slide slot required (error)
- `custom_slide_thickness > 0` — Slide thickness must be positive (error)
- `custom_slide_length > custom_slide_width` — Length must exceed width (error)
- `wall_thickness >= 1.2` — Walls below 1.2mm may not print reliably (3 perimeters at 0.4mm nozzle) (warning)
- `num_slots <= 50` — More than 50 slots may exceed typical print bed width (warning)
- `tolerance_xy >= 0.2` — Tolerance below 0.2mm may cause insertion difficulty (warning)
- `!(slide_standard == 3 && density == 0)` — Supa Mega slides at archival density require very wide print bed (warning)

## Assembly Steps

1. **Print the parts**
   0.2mm layers, 20–30% infill. PLA for dry storage, PETG for staining
2. **Attach lid (box mode)**
   Align lid snap-fit latches with base catches
3. **Insert microscope slides**
   Slide microscope slides in from the top into the slots

## Render Estimates

- **base_time**: 5
- **per_unit**: 2
- **per_part**: 8
- **fn_factor**: 32
- **wasm_multiplier**: 3
- **warning_threshold_seconds**: 60

---
*Auto-generated from `project.json` by `scripts/generate-project-docs.py`*
