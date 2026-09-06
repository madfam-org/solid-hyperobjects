import cadquery as cq
import json
import argparse
import math


def create_thread(diameter, pitch, length):
    """A threaded shaft as ONE revolved solid, base at z=0.

    This used to be `from libs.cq_core import create_thread`, reached by
    appending to `sys.path`. The CadQuery sandbox
    (apps/api/services/engine/cq_runner.py) rejects `import sys` outright, so
    the bolt mode failed to render at all on the CadQuery side and had no
    parity measurement to compare.

    Rather than re-import, build the shaft the way this cartridge's own
    `main.py:136` `cosmetic_shaft` does, and for its stated reason: sweeping a
    separate helical rib onto a core cylinder leaves a coincident cylindrical
    face that cracks the shell, whereas a single revolve of a closed sawtooth
    profile -- up the axis, across the base, a zig-zag right edge climbing
    root->crest->root, back across the top -- is watertight by construction and
    much faster than a helical sweep.

    ISO 60-degree metric: thread depth 0.6134*pitch, crest at the nominal
    (major) radius, root 0.6134*pitch inside it.

    The shaft is always exactly `length` tall. `round(length / pitch)` truncates
    it to a whole number of pitches, so any length that is not a multiple of the
    pitch comes out SHORT -- M5 x 25 at pitch 0.8 gives 31 turns and stops at
    z = 24.800, while `build()` places the head at z = length = 25.000. The
    0.2 mm gap left the head as a second, detached body (CadQuery 2 bodies
    against OpenSCAD's 1, where `y4d_standard_thread(l=length)` always spans the
    full length). Round UP and trim the last, partial pitch back to `length`.
    """
    major_r = diameter / 2.0
    minor_r = max(0.4, major_r - 0.6134 * pitch)
    n = max(1, int(math.ceil(length / pitch)))
    pts = [(0.0, 0.0), (minor_r, 0.0)]
    z0 = 0.0
    for _ in range(n):
        # Clamp each profile vertex to the shaft top so the last (partial) pitch
        # ends flat at z = length instead of overshooting it.
        pts.append((major_r, min(z0 + pitch * 0.5, length)))
        pts.append((minor_r, min(z0 + pitch, length)))
        z0 += pitch
    pts.append((0.0, length))
    # Drop duplicate points the clamp may have produced at the top.
    dedup = [pts[0]]
    for pt in pts[1:]:
        if abs(pt[0] - dedup[-1][0]) > 1e-9 or abs(pt[1] - dedup[-1][1]) > 1e-9:
            dedup.append(pt)
    face = cq.Workplane("XZ").polyline(dedup).close()
    return face.revolve(360, (0, 0, 0), (0, 1, 0))


def build(params):
    diameter = float(params.get('diameter', 5.0))
    length = float(params.get('length', 20.0))
    head_diameter = float(params.get('head_diameter', 0.0))
    head_height = float(params.get('head_height', 0.0))
    head_style_id = int(params.get('head_style_id', 0))
    
    thread_enabled = params.get('thread_enabled', True)
    pitch = float(params.get('pitch', 0.8))
    
    head_d = head_diameter if head_diameter > 0 else diameter * 1.7
    head_h = head_height if head_height > 0 else diameter * 0.7
    
    # Shaft
    if thread_enabled:
        bolt = create_thread(diameter, pitch, length)
    else:
        bolt = cq.Workplane("XY").circle(diameter / 2.0).extrude(length)
    
    # Head
    head_wp = cq.Workplane("XY", origin=(0,0,length))
    
    if head_style_id == 0:
        # Hex head
        head = head_wp.polygon(6, head_d).extrude(head_h)
        bolt = bolt.union(head)
    elif head_style_id == 1:
        # Socket head
        head = head_wp.circle(head_d / 2.0).extrude(head_h)
        socket = head_wp.workplane(offset=head_h/2.0).polygon(6, diameter * 0.6).extrude(head_h/2.0 + 0.1)
        bolt = bolt.union(head).cut(socket)
    else:
        # Button head (approximated as a cylinder with rounded top or just a cylinder for now)
        # Using a fillet on the top edge to make it a dome
        head = head_wp.circle(head_d / 2.0).extrude(head_h * 0.6)
        # trying to fillet the top edge:
        bolt = bolt.union(head)
        try:
            bolt = bolt.edges(">Z").fillet((head_h * 0.6) - 0.1)
        except Exception:
            pass # fallback if fillet fails

    return bolt.clean()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()
    
    params = json.loads(args.params)
    res = build(params)
    
    if args.out:
        cq.exporters.export(res, args.out)
