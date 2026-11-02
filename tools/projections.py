#!/usr/bin/env python3
"""Render a cartridge's presets as committed SVG projections (hidden-line drawings).

WHY THIS EXISTS
---------------
Consumers of the commons (a product page, a catalogue, a hardware panel) show a drawing of a
family at a named preset. Under the owner's separation ruling of 2026-11-01 that drawing
is geometry, so it is made HERE, from the cartridge itself, and consumers ingest it. They
never redraw it. The drawing is the CadQuery hidden-line SVG of the real B-Rep, rendered
through the same sandboxed execution the keystone's `y4d-spec check --render` uses. It is
a projection of the model, not an illustration.

USAGE
-----
    python3 tools/projections.py <slug> --mode device \\
        --view closed:0,-1,0.35:fold_angle=0 --view open:0,-1,0.35:fold_angle=180

        writes <slug>/docs/projections/<preset>-<view>.svg for every preset in the
        manifest, plus archetype-default-<view>.svg for the defaults

    --preset SLUG   only that preset (repeatable); --defaults-only skips the presets
    --check         exit 1 when a committed projection is missing (it does not re-render)

A view is `name:dx,dy,dz[:param=value,...]`: the projection direction, then parameter
overrides applied on top of the preset (a fold state, an orientation). Fold-state presets
(`kind: fold_state`) assert nothing about a product and are skipped.

Needs the keystone with its [geometry] extra (cadquery). Run it locally and commit the
SVGs; CI does not render them, so a projection is evidence the author produced, like the
clamshell's 28.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

#: SVG export options. Fixed, so a re-render of an unchanged preset is byte-stable.
SVG_OPTS = {"width": 900, "height": 600, "marginLeft": 20, "marginTop": 20,
            "showAxes": False, "strokeWidth": 0.4, "showHidden": True}


def parse_view(text: str) -> tuple[str, tuple[float, float, float], dict]:
    parts = text.split(":")
    if len(parts) < 2:
        raise SystemExit(f"--view {text!r}: expected name:dx,dy,dz[:param=value,...]")
    name, direction = parts[0], tuple(float(x) for x in parts[1].split(","))
    if len(direction) != 3 or not any(direction):
        raise SystemExit(f"--view {text!r}: the direction needs three numbers, not all zero")
    overrides = {}
    for item in ":".join(parts[2:]).split(",") if len(parts) > 2 else []:
        if not item:
            continue
        key, _, raw = item.partition("=")
        try:
            overrides[key] = json.loads(raw)
        except json.JSONDecodeError:
            overrides[key] = raw          # a select value
    return name, direction, overrides


def _script(manifest: dict, mode_id: str) -> str:
    for mode in manifest.get("modes", []):
        if mode.get("id") == mode_id:
            return mode.get("cq_file") or mode.get("scad_file")
    raise SystemExit(f"no mode {mode_id!r} in the manifest")


def _parts(manifest: dict, mode_id: str) -> list[str]:
    for mode in manifest.get("modes", []):
        if mode.get("id") == mode_id:
            return list(mode.get("parts") or [])
    return []


def render_svg(cartridge: Path, script: str, parts: list[str], params: dict,
               direction: tuple[float, float, float], out: Path) -> None:
    """Union the mode's parts at `params` and write their hidden-line SVG to `out`."""
    import cadquery as cq
    from y4d_spec.geometry import _exec_cartridge

    shapes = []
    for part in parts or [None]:
        call = dict(params)
        if part is not None:
            call["target_part"] = part
        result = _exec_cartridge(str(cartridge / script), call)
        if result is None:
            raise SystemExit(f"{cartridge.name}: {part or 'default'} rendered nothing")
        if isinstance(result, cq.Assembly):
            shapes.append(result.toCompound())
        elif isinstance(result, cq.Workplane):
            shapes.extend(v for v in result.vals() if isinstance(v, cq.Shape))
        else:
            shapes.append(result)
    compound = cq.Compound.makeCompound(shapes)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_svg = Path(tmp) / "p.svg"
        cq.exporters.export(compound, str(tmp_svg), exportType="SVG",
                            opt={**SVG_OPTS, "projectionDir": direction})
        out.write_bytes(tmp_svg.read_bytes())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("--mode", required=True, help="the mode to draw (its parts are unioned)")
    ap.add_argument("--view", action="append", required=True)
    ap.add_argument("--preset", action="append", help="only these presets")
    ap.add_argument("--defaults-only", action="store_true")
    ap.add_argument("--check", action="store_true", help="only verify the files exist")
    args = ap.parse_args(argv)

    cartridge = REPO_ROOT / args.slug
    manifest = json.loads((cartridge / "project.json").read_text(encoding="utf-8"))
    views = [parse_view(v) for v in args.view]
    targets = [("archetype-default", {})]
    if not args.defaults_only:
        for p in manifest.get("presets", []):
            if p.get("kind") == "fold_state":
                continue
            if args.preset and p.get("slug") not in args.preset:
                continue
            targets.append((p["slug"], dict(p.get("values") or {})))

    out_dir = cartridge / "docs" / "projections"
    missing, written = [], 0
    script, parts = _script(manifest, args.mode), _parts(manifest, args.mode)
    for slug, values in targets:
        for name, direction, overrides in views:
            out = out_dir / f"{slug}-{name}.svg"
            if args.check:
                if not out.is_file():
                    missing.append(str(out.relative_to(REPO_ROOT)))
                continue
            render_svg(cartridge, script, parts, {**values, **overrides}, direction, out)
            written += 1
    if args.check:
        for m in missing:
            print(f"missing: {m}", file=sys.stderr)
        print(f"projections check: {args.slug} targets={len(targets)} views={len(views)} "
              f"missing={len(missing)}")
        return 1 if missing else 0
    print(f"projections: {args.slug} wrote {written} SVG(s) to "
          f"{out_dir.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
