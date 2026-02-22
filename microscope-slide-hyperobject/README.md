# Microscope Slide Hyperobject

A standardized, parametric OpenSCAD library for microscope slide retention geometry, strictly compliant with ISO 8037 standards.

---

# Yantra4D: Microscope Slide Hyperobject

![Slide Thumb](https://4d-app.madfam.io/projects/microscope-slide.webp)

**The fundamental 4D Bounded Cartridge for optical microscopy.**

This project serves a dual purpose within the Yantra4D ecosystem:
1. **A Volumetric Cartridge:** It renders mathematically exact, 4D Bounded geometries of microscope glass substrates based on the global ISO 8037-1 and ISO 8255 standards.
2. **A CDG Library:** It provides the `slide_slot_array()` and `slide_retention_rib()` Common Denominator Geometry (CDG) interfaces for other projects (like the `microscope-slide-holder` and `custom-msh`) to securely grip slides without scratching the glass.

## The Ontological Boundary (ISO 8037-1)
This hyperobject is strictly constrained to the dimensional and optical tolerances required by professional optical microscopy. The glass substrate dictates the working distance between the condenser lens and the specimen plane.

### Supported Parameters
The following standard parameters are available in the configurator, rendering the exact glass substrate bounds:
- **0: ISO 8037-1 Primary:** 76.0mm x 26.0mm x 1.0mm
- **1: ISO 8037-1 Alternate:** 75.0mm x 25.0mm x 1.0mm
- **2: ISO 8255 #1.5H Cover Glass:** 22.0mm x 22.0mm x 0.17mm (High Performance)
- **3: ISO 8255 #1 Cover Glass:** 22.0mm x 22.0mm x 0.15mm
- **4: Custom:** Dynamically adjust length, width (10-55mm), and thickness (down to 0.1mm for microfluidics coverslips).

## Using as a CDG Library (Backward Compatibility)
To include the slide retention geometries in your own Yantra4D project, add this repository as a submodule:

```bash
git submodule add https://github.com/madfam-org/microscope-slide-hyperobject.git libs/microscope-slide-hyperobject
```

Then include it in your `.scad` file:

```openscad
include <libs/microscope-slide-hyperobject/slide.scad>

// Generates an array of retention ribs
slide_slot_array(
    count = 5,
    pitch = 30,
    height = 5,
    depth = 26,
    root_w = 2,
    tip_w = 1.2,
    chamfer_h = 1,
    tapered = true
);
```

## Material Considerations
When manufacturing the physical manifestation of this Bounded 4D Cartridge outside the digital realm:
- **Resin (SLA/DLP):** Use a clear photopolymer resin (like Formlabs Clear) with an RI close to `~1.523` and finish with a spin-coated liquid resin layer to eliminate voxel scattering.
- **Filament (FDM):** Use transparent Polycarbonate or PETT, extruded at 100% infill directly onto a glass build plate to clear the bottom layer. FDM is generally unsuitable for high-resolution microscopy due to internal void refraction.

## 📐 Technical Standards
Refer to [docs/RESEARCH.md](./docs/RESEARCH.md) for detailed dimensions and international standard references.

## ⚖ Distribution & Compliance

### 4-Point Standard
- [x] **Self-Contained:** No external dependencies outside of the cartridge.
- [x] **No Vendor Lock-in:** No opaque vendor directories.
- [x] **Appropriate Attribution:** Formalized in `project.json`.
- [x] **Standardized Manifest:** Passes Yantra4D `audit_compliance.py`.

### License
Licensed under the **CERN Open Hardware Licence Version 2 - Weakly Reciprocal (CERN-OHL-W-2.0)**.
Copyright (c) 2026 madfam-org.
