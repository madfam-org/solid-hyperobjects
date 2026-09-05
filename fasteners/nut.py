import cadquery as cq
import json
import argparse
import math


def _hex_prism(across_flats, height):
    """A regular hexagon prism whose ACROSS-FLATS width is the wrench size.

    `cq.Workplane.polygon(n, diameter)` takes the CIRCUMSCRIBED diameter, so a
    wrench size has to be converted first. This is the same helper, with the
    same conversion, that this cartridge's own `main.py:179` uses -- its
    module docstring states the convention outright: "across-flats follows the
    ISO 4014 / ISO 4032 wrench envelope".
    """
    r_circ = across_flats / math.cos(math.radians(30)) / 2.0
    # `polygon` puts a VERTEX on +X (flats on Y). BOSL2's threaded_nut puts a
    # FLAT on +X (vertices on Y): nut.scad's render measures x = 8.5 across the
    # flats and y = 9.72 across the corners. Rotate 30 degrees so the two
    # kernels present the same face to the same axis -- without it the AABB is
    # the right size but transposed, which the parity gate reads as a 1.31 mm
    # divergence.
    prism = (
        cq.Workplane("XY")
        .polygon(6, r_circ * 2.0)
        .extrude(height)
        .rotate((0, 0, 0), (0, 0, 1), 30)
    )
    # BOSL2 truncates the hex corners: `_nutshape` (threading.scad:2544)
    # intersects the prism with a cylinder of d = 0.99 * across-corners, which
    # is why nut.scad measures 9.7168 across the corners of an 8.5 mm nut and
    # not the geometric 9.8150. Port the same clip -- it is the ISO 4032
    # washer-face relief, real geometry rather than tessellation.
    clip = cq.Workplane("XY").circle(r_circ * 2.0 * 0.99 / 2.0).extrude(height)
    return prism.intersect(clip)


def _cosmetic_bore_negative(bore_r, total_h, pitch, depth):
    """One revolved negative for an internally threaded bore.

    Ported from `main.py:159` `cosmetic_bore_negative`, and for its reason: a
    single solid from the Z axis out to a sawtooth, cut in ONE boolean, leaves
    no coincident cylindrical face to crack the shell.
    """
    n = max(1, int(round(total_h / pitch)))
    pts = [(0.0, 0.0), (bore_r, 0.0)]
    z0 = 0.0
    for _ in range(n):
        pts.append((bore_r + depth, z0 + pitch * 0.5))
        pts.append((bore_r, z0 + pitch))
        z0 += pitch
    pts.append((0.0, z0))
    face = cq.Workplane("XZ").polyline(pts).close()
    return face.revolve(360, (0, 0, 0), (0, 1, 0))


def build(params):
    diameter = float(params.get('diameter', 5.0))
    width = float(params.get('width', 0.0))
    height = float(params.get('height', 0.0))
    nut_style_id = int(params.get('nut_style_id', 0))
    pitch = float(params.get('pitch', 0.8))
    thread_enabled = params.get('thread_enabled', True)
    
    # `width` is the wrench size (across flats), exactly as nut.scad passes it
    # to BOSL2 `threaded_nut(nutwidth=...)` -- BOSL2 documents nutwidth as
    # "flat to flat width of nut" (threading.scad:286).
    nut_w = width if width > 0 else diameter * 1.7
    nut_h = height if height > 0 else diameter * 0.8
    nyloc_extra = nut_h * 0.3 if nut_style_id == 2 else 0.0
    
    total_h = nut_h + nyloc_extra
    
    # Outer shape
    wp = cq.Workplane("XY")
    
    if nut_style_id == 1:
        # Square
        nut = wp.rect(nut_w, nut_w).extrude(total_h)
    else:
        # Hex (or Hex + nyloc)
        nut = _hex_prism(nut_w, total_h)
        
    # Bore. nut.scad routes through BOSL2 `threaded_nut` when thread_enabled,
    # so an internally threaded bore is what the OpenSCAD side produces; this
    # side used to cut a plain cylinder either way.
    if thread_enabled:
        # ISO 60-degree metric: thread depth 0.6134*pitch (H = 0.866*p, the
        # engaged flank is 5/8 H). The nut's minor bore is the nominal
        # diameter, the major bore is that plus the depth.
        depth = 0.6134 * pitch
        hole = _cosmetic_bore_negative(diameter / 2.0, total_h + 1.0, pitch,
                                       depth).translate((0, 0, -0.5))
    else:
        hole = wp.circle(diameter / 2.0).extrude(total_h + 1.0).translate((0,0,-0.5))
    
    nut = nut.cut(hole)
        
    # Nyloc top rounding (optional detailing)
    if nut_style_id == 2:
        try:
            nut = nut.edges(">Z and %LINE").fillet(nyloc_extra - 0.1)
        except Exception:
            pass
            
    return nut.clean()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()
    
    params = json.loads(args.params)
    res = build(params)
    
    if args.out:
        cq.exporters.export(res, args.out)
