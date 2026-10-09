# Preserved bed mount fork

Last Updated: 2026-10-09

This directory preserves an unfinished local Yantra4D fork of the existing
`bed-extrusion-mount` cartridge, named `p8rt-bed-extrusion-mount`.
Its six files are copied byte for byte, including the CERN-OHL-W-2.0 license,
fork metadata, script, manifest, graph and documentation.

The current graph changes the first box width expression by adding `10`.
That modification has not been verified against the Python geometry.
The copied design documentation describes its earlier validation and is not
evidence that this edited fork passes parity.

The source belongs to solid-hyperobjects, which owns solid cartridges.
Yantra4D owns the consuming platform; manufacturing execution belongs elsewhere.
This snapshot is outside the catalog and does not claim a new cartridge slug.
Before integrating it, reconcile it with the existing bed-extrusion-mount
family and pass the required manifest, geometry and parity checks.

Validation here covers JSON parsing, credential review and remote file recovery.
No geometry correctness, fabrication readiness, merge or deployment is claimed.

Public-safe boundary: this snapshot contains public licensed geometry and fork
metadata only; machine and operational evidence remain in the private audit.
