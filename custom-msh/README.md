# Custom Microscope Slide Holder (AOCL)

Welcome to the `custom-msh` repository! If you're new to parametric manufacturing or the Yantra4D platform, you're in the right place. This document is designed to help you understand not just *what* this project does, but *why* it's built this way.

## Introduction: Welcome to the Era of Hyperobjects

If you've ever 3D printed a file from the internet, you're probably familiar with `.stl` files. An STL is what we call a **Static Mesh**—a fixed, rigid shell made of tiny triangles. If a hole is 3 millimeters wide but you only have a 4-millimeter screw, you are out of luck. The intelligence of the design is lost.

This project is different. It is a **Bounded 4D Hyperobject**.

Instead of a fixed shape, a Hyperobject is a *computational definition* of a family of objects that exist within a multidimensional parameter space. Written in OpenSCAD (a code-based 3D modeling language), the "object" here is actually a script. You don't download a specific slide holder; you download the *recipe* to generate infinite variations of a slide holder.

The "4th Dimension" in this context is the potential of the design space itself. It is "Bounded" because the code enforces logical limits (e.g., preventing a wall from becoming so thin it snaps).

## The Theory: Common Denominator Geometry (CDG)

Why do we need Hyperobjects? Because of **Common Denominator Geometry (CDG)**.

Originating in aerospace engineering, CDG is the idea that to build complex systems, you need a shared, mathematically rigorous "truth" or interface. In the realm of additive manufacturing, CDG represents the standardized interfaces—the rails, grids, threads, and sockets—that allow a globally distributed community to build compatible infrastructure without centralized coordination.

For this project, the **CDG** is the specific length, width, clearance, and interaction profile to hold a standard **AOCL microscope slide/substrate** (default 25.4mm × 25.4mm, supporting rectangular slides up to 76mm × 52mm).

By standardizing this interface in open code:
- You know that *any* variation you generate will securely hold the glass slide for its configured dimensions.
- You can adjust tolerances for different 3D printers or materials, without breaking the core functionality.
- You empower a "right to repair" and open science ecosystem independent of proprietary, rigid commercial lab hardware.

## Standalone Usage

This hyperobject is designed to be fully functional entirely independent of the Yantra4D ecosystem. The core geometry logic relies solely on the open-source **BOSL2** standard library.

To use this on your own machine via OpenSCAD:

```bash
# Clone the repository and properly pull the BOSL2 library submodule
git clone --recursive https://github.com/madfam-org/custom-msh.git

# Open the files directly in OpenSCAD
# (The code automatically links to the local BOSL2 folder included in the clone)
```

---

## Technical Architecture

This repository contains the OpenSCAD generators for a custom substrate holder system tailored for the 1×1 inch AOCL standard. It includes a single holder, a 10-slot staining rack, a 3-rack storage box with snap-fit lid, and assembly views.

### The Yantra4D Manifest ([`project.json`](./project.json))

To make these Hyperobjects usable for non-programmers, this project includes a [`project.json`](./project.json) file. This is the **Yantra4D Manifest**.

Yantra4D is an open platform that visualizes and configures these parametric models in a web browser. The `project.json` file acts as the bridge:
1. It reads the OpenSCAD variables (like `tolerance_xy` or `num_slots`).
2. It translates them into a user-friendly web interface with sliders and checkboxes.
3. It bundles standard presets (like a "Tight Tolerance" vs "Loose Tolerance" preset).

When you see the tables below, they are derived from this manifest.

---

## Project Specifications 

**Version**: 2.4.0  
**Slug**: `custom-msh`  
**License**: CERN-OHL-W-2.0  
**Official Configurator**: [Yantra4D](https://github.com/madfam-org/yantra4d)

### Included Modes (Hyperobject Generators)

| ID | Label | SCAD File | Parts | Description |
|---|---|---|---|---|
| `holder` | Single Holder | [`holder.scad`](./holder.scad) | holder_body | Generates a single AOCL substrate holder. |
| `rack` | Staining Rack | [`rack.scad`](./rack.scad) | rack | Generates a rack holding multiple substrates. |
| `multi_rack` | Multi-Rack | [`multi_rack.scad`](./multi_rack.scad) | multi_rack_body | Generates 2–5 contiguous racks joined front-to-back (Y-axis, default) or side-by-side (X-axis) with diamond grid junction guards. |
| `box` | Racks Box | [`box.scad`](./box.scad) | box_base, box_lid | Generates an outer enclosure for racks (base + lid). |
| `base` | Box Base | [`box.scad`](./box.scad) | box_base | Box base only (for single-piece printing). |
| `lid` | Box Lid | [`box.scad`](./box.scad) | box_lid | Box lid only (for single-piece printing). |
| `assembly`| Assembly | [`assembly.scad`](./assembly.scad) | rack, box_base, box_lid, slides | Interactive combined assembly view with glass substrates. |
| `library`| CDG Library | [`aocl_lib.scad`](./aocl_lib.scad) | N/A | Core underlying geometry math & shapes (imported by others). |

### Parameters & Data Standards

The following interactive parameters define the bounds of this hyperobject. Notice how the core CDG (the AOCL substrate dimensions) is exposed but defaults to the industry standard.

| Name | Type | Default | Range | Description |
|---|---|---|---|---|
| `assembly_level` | slider | 3 | 1–3 | Assembly detail level (1=rack+slides, 2=+box, 3=+lid). Hidden parameter. |
| `substrate_length` | slider | 25.4 | 15.0–76.0 (step 0.1) | Substrate dimension along the rack's Y-axis (front-to-back). **AOCL square: 25.4 mm; standard slide: 76 mm** |
| `substrate_width` | slider | 25.4 | 15.0–52.0 (step 0.1) | Substrate dimension along the rack's Z-axis (slot depth). **AOCL square: 25.4 mm; standard slide: 26 mm** |
| `stack_along_y` | checkbox | Yes | - | Stack racks along Y-axis instead of X-axis |
| `tolerance_xy` | slider | 0.4 | 0.1–0.8 (step 0.05) | Horizontal clearance added to pocket/slot openings for FDM shrinkage |
| `tolerance_z` | slider | 0.2 | 0.05–0.5 (step 0.05) | Slot width clearance over substrate thickness |
| `wall_thickness` | slider | 2.0 | 1.2–4.0 (step 0.2) | Outer structural wall and pillar thickness |
| `holder_thickness` | slider | 2.0 | 1.0–30.0 (step 0.5) | Total Z height of the holder block |
| `label_area` | checkbox | Yes | - | Subtracts a debossed recess for adding a handwritten or adhesive label |
| `chamfer_pocket` | checkbox | Yes | - | Adds a 45° chamfer at pocket entry to guide substrate insertion |
| `num_slots` | slider | 10 | 5–15 | Number of substrate positions per rack. |
| `handle` | checkbox | Yes | - | Sculpts an integrated FDM-printable carrying arch into each side wall via a 45° peaked `hull()` void — no external handle or support material required |
| `open_bottom` | checkbox | Yes | - | Toggles an open crossbar base (less material, cleanable) vs. solid floor |
| `drainage_angle` | slider | 5 | 0–15 | Slope for fluid runoff (0 = flat). Reserved for future use. |
| `show_numbers` | checkbox | Yes | - | Engrave slot identification numbers on the front and back faces. Also requires Quality ($fn) > 0. |
| `numbering_start` | slider | 1 | 1–100 | First slot number engraved on the rack. Requires Show Slot Numbers ON and Quality ($fn) > 0. |
| `divider_style` | checkbox | Yes | - | Full-depth fins (ON) vs. stub ribs at front+back only (OFF) |
| `num_racks` | slider | 3 | 1–5 | How many racks the box accommodates. |
| `multi_num_racks` | slider | 3 | 2–5 | How many racks are joined with shared diamond grid guards. Direction controlled by Stack Along Y-Axis. |
| `multi_stack_y` | checkbox | Yes | - | ON = racks joined front-to-back (Y-axis, default). OFF = racks joined side-by-side (X-axis). |
| `frame_base_grid` | checkbox | Yes | - | Forces the divider fins to extend downwards to the absolute Z=0 floor |
| `side_guards` | checkbox | Yes | - | Generates a 1.5mm 45-degree diamond grid lattice as a mid-height retaining wall along the rack sides |
| `fn` | slider | 32 | 0–64 (step 8) | Polygon resolution. 0 = auto (fast draft). Higher = slower but detailed. |

### Configurator Presets

| Preset | Modes |
|---|---|
| **Default Holder** | holder |
| **Default Staining Rack** | rack |
| **Default Multi-Rack (3 Joined)** | multi_rack |
| **Default Racks Box** | box, base, lid |
| **Staining rack WITH slides** | assembly (level 1) |
| **Racks box WITH racks & slides (no lid)** | assembly (level 2) |
| **Racks box WITH racks & slides (with lid)** | assembly (level 3) |

### Color Identifiers

| ID | Label | Default Color | Notes |
|---|---|---|---|
| `holder_body` | Holder Body | `#4a90d9` | |
| `rack` | Rack | `#e5e7eb` | |
| `multi_rack_body` | Multi-Rack Body | `#e5e7eb` | render_mode 5 |
| `box_base` | Box Base | `#4a90d9` | |
| `box_lid` | Box Lid | `#6b7280` | |
| `slides` | Slides | `#cce8f4` | glass: true |

---
*Generated alongside `project.json` for integration with Yantra4D*
