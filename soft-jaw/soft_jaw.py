import cadquery as cq
import json
import argparse

# project.json declares face_pattern as a select over the STRINGS
# "smooth" | "serrations" | "grid" (default "smooth"). The jaw_body pair used
# to read it as an int here (0/1/2) while soft_jaw.scad compared it against
# "prismatic" -- a value that is not one of the manifest's options at all. So
# at preset kurt_dx6_prismatic_scad (face_pattern: 1) CadQuery added a 5 mm
# additive V-prism to the front face while OpenSCAD added nothing, and the two
# kernels' jaw_body bounding boxes differed by exactly that 5.000 mm in Y
# (19.05 vs 24.05).
#
# Both sides now normalise through this one table and build the SAME
# subtractive V-groove face that main.py's face_cutter() builds for the
# jaw / jaw_pair / vee_jaw modes -- the cartridge's standard construction. The
# legacy integer codes the *_scad presets carry are accepted as aliases so
# those presets keep resolving without being edited.
_FACE_PATTERNS = {
    0: "smooth", "0": "smooth", "smooth": "smooth",
    1: "serrations", "1": "serrations", "serrations": "serrations",
    2: "grid", "2": "grid", "grid": "grid",
}


def normalise_face_pattern(value):
    """Manifest string, or a legacy 0/1/2 code, -> one of the manifest's options."""
    if isinstance(value, bool):
        value = int(value)
    return _FACE_PATTERNS.get(value, _FACE_PATTERNS.get(str(value), "smooth"))


def build(params):
    jaw_width_inch = float(params.get('jaw_width', 6.0))
    face_pattern = normalise_face_pattern(params.get('face_pattern', 'smooth'))
    magnet_pockets = bool(params.get('magnet_pockets', True))
    serration_pitch = float(params.get('serration_pitch', 2.5))
    jaw_height_inch = float(params.get('jaw_height', 1.735)) # Using defaults from json, scad had 1.25 hardcoded but params allow it
    jaw_thickness_inch = float(params.get('jaw_thickness', 0.75))
    int(params.get('vise_model', 0))
    
    width_mm = jaw_width_inch * 25.4
    height_mm = jaw_height_inch * 25.4
    thickness_mm = jaw_thickness_inch * 25.4
    
    bolt_spacing = 3.875 * 25.4
    bolt_head_d = 14.0
    bolt_shaft_d = 9.0
    
    # 1. Main Body
    # Origin at center
    jaw = cq.Workplane("XY").box(width_mm, thickness_mm, height_mm)
    
    # 2. Face Pattern -- V-grooves CUT into the front face (-Y).
    #
    # This mirrors main.py's face_cutter(): serrations are horizontal V-grooves
    # running in X and stacked up the face in Z; grid adds vertical grooves
    # running in Z and spaced across X. Cutting (rather than the old additive
    # prism / ribs) is what keeps the jaw inside its declared envelope, so the
    # face pattern can never move the bounding box: a soft jaw's whole point is
    # that it bolts into the vise at a known thickness.
    if face_pattern != "smooth":
        y_face = -thickness_mm / 2.0          # front face plane
        pitch = max(1.5, min(serration_pitch, height_mm / 4.0))
        groove_depth = min(0.8, pitch * 0.45)
        half_w = groove_depth                 # ~90 deg included V
        HZ_MAX, VT_MAX = 12, 10

        cutters = []

        # Horizontal V-grooves: profile in the YZ plane, swept the full width.
        n = min(HZ_MAX, max(1, int(height_mm / pitch) - 1))
        for i in range(1, n + 1):
            z = -height_mm / 2.0 + i * (height_mm / (n + 1))
            cutters.append(
                cq.Workplane("YZ", origin=(-(width_mm / 2.0 + 1.0), y_face, z))
                # local (Y, Z): mouth on the face, apex driven into the jaw (+Y)
                .polyline([(0.0, -half_w), (0.0, half_w), (groove_depth, 0.0)])
                .close()
                .extrude(width_mm + 2.0)
            )

        if face_pattern == "grid":
            # Vertical V-grooves: profile in the XY plane, swept the full
            # height, and cut slightly SHALLOWER than the horizontal ones.
            #
            # At equal depth the two families' apex lines are coplanar and
            # cross along a zero-thickness line. OpenSCAD still calls that
            # manifold (genus 2, 0 boundary edges) but the tessellation
            # carried 96 edges shared by four faces and 108 zero-area
            # triangles at exactly y = -T/2 + groove_depth, and the mesh check
            # read it as not watertight. Offsetting the crossing family by a
            # fraction of the depth makes every crossing a real volume -- and
            # is how a cross-hatch knurl is actually cut. soft_jaw.scad
            # applies the same factor.
            grid_depth = groove_depth * 0.75
            m = min(VT_MAX, max(1, int(width_mm / (pitch * 2.0)) - 1))
            for j in range(1, m + 1):
                x = -width_mm / 2.0 + j * (width_mm / (m + 1))
                cutters.append(
                    cq.Workplane("XY", origin=(x, y_face, -height_mm / 2.0 - 1.0))
                    .polyline([(-half_w, 0.0), (half_w, 0.0), (0.0, grid_depth)])
                    .close()
                    .extrude(height_mm + 2.0)
                )

        for c in cutters:
            jaw = jaw.cut(c)
        jaw = jaw.clean()

    # 3. Mounting holes: counterbored SHCS bores driven in from the BACK face
    #    (+Y, the vise side) and tapering down toward the gripping face.
    #
    # The loft used to be built on cq.Workplane("XZ") with
    # `.workplane(offset=-(thickness+1))` and then translated to y = +T/2. On
    # the XZ plane the workplane normal points along +Y, so that offset moved
    # the far profile to y = +T+1, not -(T+1): the finished cone spanned
    # y = 9.525 .. 29.575 while the jaw itself ends at y = +9.525. Both bores
    # sat entirely OUTSIDE the jaw, touching its back face along a single
    # tangent circle, so `cut` removed nothing at all and jaw_body rendered
    # with no mounting holes -- 4,100 mm^3 of material the OpenSCAD side (and
    # the manifest's whole reason for a vise bolt pattern) does not have.
    #
    # Build the loft where it belongs instead: the wide counterbore mouth ON
    # the back face, tapering to the shaft diameter past the front face, with
    # a small overshoot at each end so neither mouth is a zero-thickness
    # opening. Same extents as soft_jaw.scad.
    y_back = thickness_mm / 2.0
    bore = (
        cq.Workplane("XZ", origin=(0, y_back + 0.5, 0))
        .circle(bolt_head_d / 2.0)
        .workplane(offset=thickness_mm + 1.0)
        .circle(bolt_shaft_d / 2.0)
        .loft()
    )
    jaw = (
        jaw.cut(bore.translate((bolt_spacing / 2.0, 0, 0)))
           .cut(bore.translate((-bolt_spacing / 2.0, 0, 0)))
           .clean()
    )
    
    # 4. Magnet Pockets (on BACK face >Y)
    if magnet_pockets:
        jaw = (
            jaw.faces(">Y")
            .workplane()
            .pushPoints([(0, height_mm/3), (0, -height_mm/3)])
            .hole(diameter=10.2, depth=3.0)
        )
        
    return jaw

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()
    
    params = json.loads(args.params)
    res = build(params)
    
    if args.out:
        cq.exporters.export(res, args.out)
