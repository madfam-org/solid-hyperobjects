# SPDX-License-Identifier: CERN-OHL-W-2.0
# requires:
"""Generic adapter envelope and prongs; no electrical internals or ratings.

X width, Y depth, Z height with the body floor at Z=0. Every component takes
its own parameter dictionary and knows no cartridge globals.
"""
import cadquery as cq


def adapter_body(p):
    """One rounded body with exact width/depth/height extents."""
    shape = (cq.Workplane('XY').box(p['width'],p['depth'],p['height'])
             .translate((0,0,p['height']/2)))
    if p['radius'] > 0:
        shape = shape.edges('|Z').fillet(p['radius'])
    return shape


def adapter_prongs(p):
    """Generic two/three-prong pattern, along +Y. Dimensions are archetypes.

    The named layout is a pattern cue, not a standard or certification claim.
    Each prong overlaps the body by 0.3 mm; returned as a compound, for the
    caller to fuse to its own body in a single union.
    """
    result = []
    for x in (-p['spacing']/2,p['spacing']/2):
        if p['layout'] == 'round_pair':
            prong = cq.Workplane('XZ').center(x,p['z']).circle(p['width']/2).extrude(
                -(p['length']+.3)).translate((0,p['body_depth']/2-.3,0))
        else:
            prong = cq.Workplane('XY').box(p['width'],p['length']+.3,p['thickness']).translate(
                (x,p['body_depth']/2+(p['length']-.3)/2,p['z']))
            if p['layout'] == 'angled_pair':
                prong=prong.rotate((x,0,p['z']),(x,1,p['z']),30 if x<0 else -30)
        result.extend(prong.vals())
    if p['layout'] == 'three_flat':
        result.append(cq.Workplane('XY').box(p['width'],p['length']+.3,p['thickness']).translate(
            (0,p['body_depth']/2+(p['length']-.3)/2,p['z']+p['spacing']*.7)).val())
    return cq.Workplane(obj=cq.Compound.makeCompound(result))


def adapter_inlet(p):
    """Recess cutter on -X, overshooting the wall by 1 mm."""
    return cq.Workplane('YZ').rect(p['width'],p['height']).extrude(p['depth']+1).translate(
        (-p['body_width']/2-1,0,p['body_height']/2))
