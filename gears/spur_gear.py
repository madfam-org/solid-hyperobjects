import cadquery as cq
import json
import argparse
import math

def build(params):
    teeth_count = int(params.get('teeth_count', 20))
    module_size = float(params.get('module_size', 2.0))
    thickness = float(params.get('thickness', 5.0))
    bore_diameter = float(params.get('bore_diameter', 5.0))
    
    pressure_angle = float(params.get('pressure_angle', 20.0))

    # Involute profile, matching BOSL2's spur_gear() in spur_gear.scad. This
    # used to be four points per tooth — a trapezoid from the root circle out to
    # a flat tip — which held the right outside diameter but not the right tooth
    # area, leaving the two engines 6.88% apart by volume on identical bounds.
    # A trapezoidal tooth also will not mesh.
    alpha = math.radians(pressure_angle)
    R_pitch = module_size * teeth_count / 2.0
    R_base = R_pitch * math.cos(alpha)
    R_outer = R_pitch + module_size            # addendum = 1 module
    R_root = R_pitch - 1.25 * module_size      # dedendum = 1.25 modules

    def inv(a):
        return math.tan(a) - a

    # Angular half-width of a tooth measured at the base circle.
    psi_base = math.pi / (2 * teeth_count) + inv(alpha)

    def flank(r):
        """Angular offset of the involute flank at radius r."""
        if r <= R_base:
            return psi_base
        return psi_base - inv(math.acos(min(1.0, R_base / r)))

    STEPS = 8
    # The space between two teeth is the ROOT CIRCLE, an arc at R_root, not a
    # vee. The flanks are involutes and so start at R_base (18.794 mm at the
    # defaults), well above R_root (17.5 mm); joining one tooth's last flank
    # point straight to a single root point at the mid-angle and straight back
    # up left a wedge of material standing between every pair of teeth, above
    # the root circle the dedendum says should be there. The gear came out
    # 2.04% heavier than BOSL2's and its teeth did not reach full depth.
    # Each gap now runs radially down to R_root and follows the root circle
    # across to the next tooth.
    ROOT_STEPS = 4
    r_start = max(R_root, R_base)
    radii = [r_start + (R_outer - r_start) * i / STEPS for i in range(STEPS + 1)]

    pts = []
    for i in range(teeth_count):
        phi = 2.0 * math.pi * i / teeth_count

        # Radially out of the root circle, up the trailing flank, across the
        # tip, down the leading flank and radially back to the root circle.
        pts.append((R_root * math.cos(phi - psi_base),
                    R_root * math.sin(phi - psi_base)))
        for r in radii:
            a = phi - flank(r)
            pts.append((r * math.cos(a), r * math.sin(a)))
        for r in reversed(radii):
            a = phi + flank(r)
            pts.append((r * math.cos(a), r * math.sin(a)))
        pts.append((R_root * math.cos(phi + psi_base),
                    R_root * math.sin(phi + psi_base)))

        # The root circle arc across to the next tooth.
        a0 = phi + psi_base
        a1 = phi + 2.0 * math.pi / teeth_count - psi_base
        for k in range(1, ROOT_STEPS):
            a = a0 + (a1 - a0) * k / ROOT_STEPS
            pts.append((R_root * math.cos(a), R_root * math.sin(a)))

    gear_profile = cq.Workplane("XY").polyline(pts).close()

    gear = gear_profile.extrude(thickness)
    
    if bore_diameter > 0:
        bore = cq.Workplane("XY").circle(bore_diameter / 2.0).extrude(thickness + 2).translate((0,0,-1))
        gear = gear.cut(bore)
        
    return gear.clean()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()
    
    params = json.loads(args.params)
    res = build(params)
    
    if args.out:
        cq.exporters.export(res, args.out)
