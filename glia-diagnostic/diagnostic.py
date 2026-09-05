import cadquery as cq
import json
import argparse


def PARAM(getter, default):
    """Read a platform-injected bare global, falling back to `default`.

    The render service execs this script with the user's parameters injected as
    bare globals (cq_runner.run_cadquery_script), so a name may or may not exist
    at module scope. `PARAM(lambda: name, default)` resolves it when it does and
    yields the default when it does not.
    """
    try:
        return getter()
    except NameError:
        return default


def build_stethoscope(params):
    diaphragm_size_mm = float(params.get('diaphragm_size_mm', 44))

    outer_d = diaphragm_size_mm + 4.0

    # Main body
    head = cq.Workplane("XY").circle(outer_d / 2.0).extrude(20.0)

    # Hollow sound chamber (leaving 2mm at bottom)
    chamber = (
        cq.Workplane("XY", origin=(0, 0, 2.0))
        .circle(diaphragm_size_mm / 2.0)
        .extrude(18.1)
    )
    head = head.cut(chamber)

    # Tube connector (on +X side).
    #
    # A connector that starts at exactly x = outer_d/2 is tangent to the
    # cylindrical face, and the union of two tangent solids is non-manifold, so
    # it has to start INSIDE the wall. But it must not start at the bell's
    # centre either: extruding from x = 0 drove a solid 8 mm bar straight
    # through the sound chamber, adding ~1100 mm^3 of material the chamber is
    # supposed to be free of, and putting this side 685 mm^3 (6.9%) above
    # diagnostic.scad. Bury it CONNECTOR_OVERLAP into the wall -- enough
    # overlap for the boolean, not enough to reach the chamber -- matching the
    # `down(_connector_overlap)` the OpenSCAD side now uses.
    CONNECTOR_OVERLAP = 2.0
    x_start = outer_d / 2.0 - CONNECTOR_OVERLAP
    connector = (
        cq.Workplane("YZ", origin=(x_start, 0, 10.0))
        .circle(8.0 / 2.0)
        .extrude(20.0 + CONNECTOR_OVERLAP)
    )

    # Air channel, bored the full length of the connector plus 1 mm past its
    # buried end so no cutter face is coincident with the wall.
    air_hole = (
        cq.Workplane("YZ", origin=(outer_d / 2.0 + 20.0, 0, 10.0))
        .circle(5.0 / 2.0)
        .extrude(-(20.0 + CONNECTOR_OVERLAP + 1.0))
    )

    head = head.union(connector).cut(air_hole)

    # Locking groove for the diaphragm retaining ring. The outer radius is clamped
    # to the body radius (outer_d), not outer_d + 0.1: an oversized cutter leaves a
    # zero-thickness skin of body wall behind, which is another source of
    # non-manifold geometry.
    groove = (
        cq.Workplane("XY", origin=(0, 0, 18.0))
        .circle(outer_d / 2.0)
        .circle(diaphragm_size_mm / 2.0)
        .extrude(2.0)
    )
    head = head.cut(groove)

    return head.clean()


def build_otoscope(params):
    speculum_size_mm = float(params.get('speculum_size_mm', 4.0))

    height = 30.0
    base_d = 8.0
    tip_d = speculum_size_mm

    # Main cone
    specula = cq.Solid.makeCone(base_d / 2.0, tip_d / 2.0, height)

    # Hollow channel
    hollow = cq.Solid.makeCone(
        (base_d - 1.5) / 2.0,
        (tip_d - 0.8) / 2.0,
        height + 0.2
    ).translate((0, 0, -0.1))

    # Snap ring
    ring = (
        cq.Workplane("XY", origin=(0, 0, -0.5))
        .circle((base_d + 1.0) / 2.0)
        .extrude(2.0)
    )

    res = cq.Workplane("XY").add(specula).union(ring).cut(hollow)

    return res.clean()


def build(params, mode="stethoscope"):
    # 'head' / 'specula' are the pre-1.0 part ids, kept as accepted aliases so any
    # saved configuration or external link that still names them keeps resolving.
    if mode in ("otoscope", "specula"):
        return build_otoscope(params)
    else:
        return build_stethoscope(params)


# ── platform entry point ──────────────────────────────────────────────────────
# The render service injects the mode/part selection as the bare global
# `target_part` and every slider as a bare global of its own id, then reads the
# finished solid back out of `result`.
target_part = str(PARAM(lambda: target_part, "stethoscope"))

_params = {
    "diaphragm_size_mm": PARAM(lambda: diaphragm_size_mm, 44),
    "speculum_size_mm": PARAM(lambda: speculum_size_mm, 4.0),
}

result = build(_params, mode=target_part)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--mode", type=str, default=target_part)
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args()

    cli_params = dict(_params)
    cli_params.update(json.loads(args.params))
    result = build(cli_params, mode=args.mode)

    if args.out:
        cq.exporters.export(result, args.out)
