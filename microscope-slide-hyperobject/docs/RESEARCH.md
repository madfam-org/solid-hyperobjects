# Research: Microscope Slide Standards (ISO 8037)

This document outlines the geometric and material specifications used as the foundation for this hyperobject.

## 1. ISO 8037-1:1986 Standard
The most widely used standard for microscope slides in transmitted light microscopy.

### Core Dimensions
| Dimension | Standard Value | Tolerance |
| :--- | :--- | :--- |
| **Length** | 76.0 mm | ± 1.0 mm |
| **Width** | 26.0 mm | ± 1.0 mm |
| **Thickness** | 1.0 mm | ± 0.05 mm |

> [!NOTE]
> While the standard allows for ±1mm tolerance on length/width, most precision biological slides (e.g., Marienfeld, Thermo Fisher) target ±0.2mm for automated slide handling compatibility.

## 2. Global Variants
Other common standards encountered in specialized workflows:

- **US "3x1 inch":** 76.2 mm x 25.4 mm x 1.0 mm.
- **Petrographic (Geology):** 46.0 mm x 27.0 mm x 1.2 mm.
- **Supa Mega (Brain/Prostate Histology):** 75.0 mm x 50.0 mm x 1.0 mm.

## 3. FDM Printing Constraints for Retention
Fabricating holders for these optics requires specific volumetric clearances:

- **Slot Width:** Must account for slide thickness + material-specific "ooze" (typically +0.4mm for PLA).
- **Anti-Capillary Spacing:** When using liquid reagents (staining), slides must be raised ~0.5mm from the floor to prevent liquid being trapped by surface tension.
- **Rib Geometry:** Lead-in chamfers of at least 15° are required to guide brittle glass slides into slots without chipping.

## 4. References
- ISO 8037-1:1986 — Dimensions, thickness and optical properties.
- DIN ISO 8037-1.
