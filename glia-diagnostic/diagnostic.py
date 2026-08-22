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
    # Extruded from the CENTRE of the bell, not from its outer wall: a connector
    # that starts at x = outer_d/2 is exactly tangent to the cylindrical face and
    # the union of two tangent solids is non-manifold — it renders as a mesh with
    # boundary edges that no slicer will print. Starting inside the body gives the
    # boolean real overlap to work with; the buried portion is absorbed by the union.
    connector = (
        cq.Workplane("YZ", origin=(0, 0, 10.0))
        .circle(8.0 / 2.0)
        .extrude(outer_d / 2.0 + 20.0)
    )

    # Air channel
    air_hole = (
        cq.Workplane("YZ", origin=(outer_d / 2.0 + 20.0, 0, 10.0))
        .circle(5.0 / 2.0)
        .extrude(-22.0)
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
