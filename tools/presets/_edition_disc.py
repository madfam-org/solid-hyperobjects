"""Diameter-only exact-edition studies; positive proxy height is authored."""
from common import rnd
from hyperobjects_reference import is_sourced

PROXY_THICKNESS_MM = 1.0


def read_edition_disc(obj):
    diameter = (obj.get('features') or {}).get('media_diameter_mm')
    if diameter is None or not is_sourced(obj, 'features.media_diameter_mm'):
        return None
    return dict(slug=obj['key'], diameter=diameter, _preset_mode='envelope')


def derive_diameter_proxy(src):
    # The envelope deliberately has no hole, hub, rings, label or clamp relief.
    # This is a bounding cylinder, not an assertion that a physical disc lacks holes.
    return dict(disc_diameter=rnd(src['diameter']), disc_thickness=PROXY_THICKNESS_MM,
                ring_height=0, shell_present=False), [
        '1 mm proxy height is authored; physical carrier thickness is unknown',
        'centre hole, clamping zone and stacking features are unknown and not represented by the envelope',
        'material, label artwork, shell and package contents are unknown and not represented',
    ]


def edition_disc_registry(obj):
    edition = obj['edition']
    return dict(edition=obj['key'], product_code=edition.get('product_code'),
        host_console=edition.get('platform'), geometry_scope='measured-diameter-only',
        sourced_fields=['features.media_diameter_mm'],
        authored_geometry=dict(proxy_thickness_mm=PROXY_THICKNESS_MM,
                               hole_and_hub='not represented in bounding cylinder'),
        unresolved_geometry=['physical thickness', 'centre hole diameter', 'clamp profile',
                             'stacking features', 'material', 'artwork'],
        source_records=sorted({s['url'] for s in obj['sources'] if s.get('url')
            and s.get('field') == 'features.catalog_media_size'}),
        caveat='Exact-edition carrier diameter only. The positive-volume cylinder uses an authored height; no optical-format compliance, complete media envelope, interior clearance or physical fit is established.')
