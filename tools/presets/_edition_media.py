"""Exact edition media envelopes; no shared format dimensions or internals inferred."""
from common import rnd
from hyperobjects_reference import is_sourced

AXES = ('media_width_mm', 'media_height_mm', 'media_depth_mm')


def read_edition(obj):
    features = obj.get('features') or {}
    if not all(features.get(key) is not None and is_sourced(obj, 'features.' + key)
               for key in AXES):
        return None
    return dict(slug=obj['key'], width=features[AXES[0]], height=features[AXES[1]],
                depth=features[AXES[2]], _preset_mode='envelope')


def derive_envelope(src):
    return dict(shell_width=rnd(src['width']), shell_height=rnd(src['height']),
                shell_thickness=rnd(src['depth']), grip_thickness=0, grip_height=0,
                corner_radius=0, insertion_edge='bottom', card_mode=False,
                insert_travel=0), [
        'conservative rectangular envelope; actual outline/corner radii unknown',
        'contact edge orientation unknown; bottom is the family frame only',
        'shell split, PCB, contacts, keying, latch, labels and grip details unknown; not rendered',
    ]


def edition_registry(obj):
    edition = obj['edition']
    return dict(edition=obj['key'], product_code=edition.get('product_code'),
                host_console=edition.get('platform'), geometry_scope='measured-envelope-only',
                media_format=(edition.get('media') or {}).get('key'),
                sourced_fields=['features.' + key for key in AXES],
                source_records=sorted({s['url'] for s in obj['sources'] if s.get('url')
                    and s.get('field') == 'features.catalog_media_size'}),
                caveat='Exact edition media measurements only; no universal N64 format or authentic surface/internal detail claim.')
