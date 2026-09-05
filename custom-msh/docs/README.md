# Custom MSH (AOCL)

Custom substrate holder system for AOCL substrates (default 25.4×25.4 mm, supports rectangular slides) -- holder, 10-slot staining rack, multi-rack joined body, 3-rack storage box with snap-fit lid, and assembly views.

Official Visualizer and Configurator: Yantra4D

*Sistema portamuestras para sustratos AOCL (predeterminado 25.4×25.4 mm, soporta sustratos rectangulares) -- soporte individual, rack de tincion de 10 ranuras, cuerpo multi-rack unido, caja para 3 racks con tapa a presion, y vistas de ensamblaje.*

*Visualizador y configurador oficial: Yantra4D*

**Version**: 2.4.0
**Slug**: `custom-msh`
**License**: CERN-OHL-W-2.0

## Modes

| ID | Label | SCAD File | Parts |
|---|---|---|---|
| `holder` | Single Holder | `holder.scad` | holder_body |
| `rack` | Staining Rack | `rack.scad` | rack |
| `multi_rack` | Multi-Rack (Y/X) | `multi_rack.scad` | multi_rack_body |
| `box` | Racks Box | `box.scad` | box_base, box_lid |
| `base` | Box Base | `box.scad` | box_base |
| `lid` | Box Lid | `box.scad` | box_lid |
| `assembly` | Assembly | `assembly.scad` | rack, box_base, box_lid, slides |

## Parameters

| Name | Type | Default | Range | Modes | Description |
|---|---|---|---|---|---|
| `assembly_level` | slider | 3 | 1-3 | (hidden) | Assembly detail level (1=rack+slides, 2=+box, 3=+lid) |
| `substrate_length` | slider | 25.4 | 15.0-76.0 (step 0.1) | all | Substrate length along rack Y-axis (mm). AOCL square: 25.4 mm; standard slide: 76 mm |
| `substrate_width` | slider | 25.4 | 15.0-52.0 (step 0.1) | all | Substrate width along rack Z-axis (mm). AOCL square: 25.4 mm; standard slide: 26 mm |
| `stack_along_y` | checkbox | No | | box, assembly, base, lid | Stack racks along Y-axis instead of X-axis |
| `tolerance_xy` | slider | 0.4 | 0.1-0.8 (step 0.05) | all | Horizontal clearance for FDM shrinkage compensation |
| `tolerance_z` | slider | 0.2 | 0.05-0.5 (step 0.05) | rack, multi_rack, assembly | Slot width clearance over substrate thickness |
| `wall_thickness` | slider | 2.0 | 1.2-4.0 (step 0.2) | all | Outer wall and pillar thickness |
| `holder_thickness` | slider | 2.0 | 1.0-30.0 (step 0.5) | holder | Total Z height of the holder block |
| `label_area` | checkbox | Yes | | holder, rack, multi_rack, box, base, lid | Debossed recess for handwritten or adhesive label |
| `chamfer_pocket` | checkbox | Yes | | holder | 45 degree chamfer at pocket entry |
| `num_slots` | slider | 10 | 5-15 | rack, multi_rack, assembly | Substrate positions per rack. AOCL spec: 10 |
| `handle` | checkbox | Yes | | rack, multi_rack, assembly | Integrated carrying handle arch |
| `open_bottom` | checkbox | Yes | | rack, multi_rack, assembly | Open crossbar base vs. solid floor |
| `drainage_angle` | slider | 5 | 0-15 | rack | Slope for fluid runoff (reserved) |
| `show_numbers` | checkbox | Yes | | rack, multi_rack, assembly | Engrave slot numbers on front face. Requires $fn > 0 |
| `numbering_start` | slider | 1 | 1-100 | rack, multi_rack, assembly | First slot number engraved. Requires show_numbers ON |
| `divider_style` | checkbox | Yes | | rack, multi_rack, assembly | Full-depth fins (ON) vs. stub ribs (OFF) |
| `num_racks` | slider | 3 | 1-5 | box, assembly, base, lid | How many racks the box accommodates |
| `multi_num_racks` | slider | 3 | 2-5 | multi_rack | Number of racks joined with shared diamond grid guards |
| `multi_stack_y` | checkbox | Yes | | multi_rack | ON = racks joined front-to-back (Y-axis, default). OFF = joined side-by-side (X-axis) |
| `frame_base_grid` | checkbox | Yes | | rack, multi_rack, assembly | Forces the divider fins to extend to Z=0 floor |
| `side_guards` | checkbox | Yes | | rack, assembly | 45-degree diamond grid retaining walls on sides |
| `fn` | slider | 32 | 0-64 (step 8) | all | Quality ($fn). 0=auto draft; higher=detail+numbers |

## Presets

| ID | Label | Modes |
|---|---|---|
| `default_holder` | Default Holder | holder |
| `default_rack` | Default Staining Rack | rack |
| `default_multi_rack` | Default Multi-Rack (3 Joined) | multi_rack |
| `default_box` | Default Racks Box | box, base, lid |
| `assembly_rack_slides` | Staining rack with slides | assembly |
| `assembly_box_nolid` | Racks box with racks & slides (no lid) | assembly |
| `assembly_box_lid` | Racks box with racks & slides (with lid) | assembly |

## Parts

| ID | render_mode | Label | Default Color | Notes |
|---|---|---|---|---|
| `holder_body` | 0 | Holder Body | `#4a90d9` | |
| `rack` | 1 | Rack | `#e5e7eb` | |
| `multi_rack_body` | 5 | Multi-Rack Body | `#e5e7eb` | |
| `box_base` | 2 | Box Base | `#4a90d9` | |
| `box_lid` | 3 | Box Lid | `#6b7280` | |
| `slides` | 4 | Slides | `#cce8f4` | glass: true |

## Hyperobject Profile

- **Domain**: medical
- **License**: CERN-OHL-W-2.0
- **CDG Interfaces**:
  - `aocl_substrate_pocket` (pocket) -- AOCL substrate retention geometry (supports rectangular substrates)
  - `snap_latch_interface` (snap) -- Snap-fit lid latch mechanism
- **Societal Benefit**: Enables fabrication of a precision substrate retention system for AOCL laboratory workflows -- independent of commercial supply chains.

## Render Estimates

- **base_time**: 5
- **per_unit**: 1
- **per_part**: 8

---
*Auto-generated from `project.json` by `scripts/generate-project-docs.py`*
