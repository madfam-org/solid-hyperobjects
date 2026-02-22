# Microscope Slide Hyperobject

A standardized, parametric OpenSCAD library for microscope slide retention geometry, strictly compliant with ISO 8037 standards.

---

## Overview
This project serves as a "primal hyperobject" within the Yantra4D ecosystem. It provides the core geometric primitives (ribs, slots, and arrays) needed to fabricate laboratory-grade slide holders, staining racks, and archival systems.

By centralizing the mathematical logic for slide retention, we ensure that every holder in the platform—regardless of who designed it—shares the same precision tolerances and standardized interfaces.

## 🛠 Features
- **ISO 8037 Compliance:** Built-in presets for Standard, US, Petrographic, and Supa Mega slides.
- **Parametric Retention:** Intelligent rib profiles with lead-in chamfers for glass-safe insertion.
- **FDM Optimized:** Integrated clearance management to handle material shrinkage and printing tolerances.
- **Plug-and-Play Cartridge:** Fully self-contained, vendor-free, and platform-agnostic.

## 🚀 Getting Started

### Using as a Submodule
This project is designed to be submoduled into the `libs/` folder of your own project:

```bash
git submodule add https://github.com/madfam-org/microscope-slide-hyperobject.git libs/microscope-slide-hyperobject
```

### SCAD Include
```openscad
// Include the core geometry
include <libs/microscope-slide-hyperobject/slide.scad>

// Generate a retention rib for a 1.0mm slide
slide_retention_rib(
    height = 20, 
    depth = 5, 
    root_w = 2.0, 
    tip_w = 1.2, 
    chamfer_h = 1.5
);
```

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
