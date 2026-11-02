"""What every device-family preset generator shares: reading the facts, assembling presets,
writing and checking a manifest.

WHY THIS EXISTS
---------------
No millimetre in a device-family cartridge is typed by hand. The facts (a product's
published envelope, displays, control counts, port kinds, each with its source) live in the
keystone's reference-objects catalog, `hyperobjects_reference` (hyperobjects-spec 0.19.0,
docs/REFERENCE_OBJECTS.md there). The family's archetype rules live beside the cartridge, in
`tools/presets/<family>.py`. One code path per family turns the first into presets and the
rules into the cartridge's parameter defaults, so the two cannot drift apart. The owner's
separation ruling of 2026-11-01 put both halves on the geometry side; consumers read
published, prerendered artifacts and hold neither.

Ported from Telesia's `scripts/device-presets.py` (telesia@43828e9), where the facts and
the generator lived until that ruling. Its archetype rules and derivations are unchanged.

WHAT COMES FROM WHERE
---------------------
  SOURCED    read straight from a reference object, where it is covered by a source:
             envelope, display active areas, control counts, port kinds.
  DERIVED    computed from a SOURCED value by an archetype rule in the family module. The
             rule is ours; the input is the maker's (a deck split of one published
             thickness).
  ARCHETYPE  ours outright, because no maker in the family publishes it (corner radius,
             recess depths, control sizes). Never presented as a device claim.

`null = unresolved, never guessed` is enforced by OMISSION: a preset sets only what the
catalog sources for that object. Everything else stays at the cartridge default, and the
preset names each group that fell back. An object whose closed envelope is null gets no
preset and is listed in `_generated_from.awaiting_a_source`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from hyperobjects_reference import family_digest, is_sourced, load_family, load_object, object_digest

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The rule the catalog states and every generated block repeats.
CATALOG_RULE = "null = unresolved, never guessed; every number carries its source"


class DeriveError(ValueError):
    """An input the archetype's rules cannot hold — reported, never silently fixed."""


def rnd(x: float) -> float:
    """Round to 4 dp and drop a pointless trailing .0 fraction.

    4 dp keeps the deck split exact to well inside the 0.5 mm bounding-box tolerance the
    cartridges' verification asserts.
    """
    v = round(float(x), 4)
    return int(v) if v == int(v) and abs(v) < 1e9 else v


# ─────────────────────────────────────────────────────────────────────────────
# Reading a reference object
# ─────────────────────────────────────────────────────────────────────────────

def state(obj: dict, name: str) -> dict:
    """One named envelope state (`closed`, `open` …), or {} when the object has none."""
    return ((obj.get("dimensions_mm") or {}).get("states") or {}).get(name) or {}


def display(obj: dict, role: str):
    """Return (width_mm, height_mm, derived) for a display role, or None.

    A display with no `active_area_mm`, or with a null width or height, returns None and
    the preset simply omits the screen parameters rather than inventing them.
    """
    for d in obj.get("displays") or []:
        if d.get("role") != role:
            continue
        area = d.get("active_area_mm") or {}
        w, h = area.get("width"), area.get("height")
        if w is None or h is None:
            return None
        return (float(w), float(h), bool(area.get("derived")))
    return None


def control_count(obj: dict, kind: str):
    """Count for a control kind, or None when the catalog does not resolve it.

    Absence and null are NOT the same thing, and conflating them is how an archetype
    default would assert a control the maker never listed, or erase one it did:

      kind present, count set    -> that count (sourced)
      kind present, count null   -> None; the control exists, the count does not
      kind absent, `controls` sourced
                                 -> 0: the maker's quoted list is complete and lacks it
                                    (Nintendo's DS pages list no stick; the DS has none)
      kind absent, `controls` not sourced
                                 -> None: nothing is known either way
    """
    for c in obj.get("controls") or []:
        if c.get("kind") == kind:
            return c.get("count")
    return 0 if is_sourced(obj, "controls") else None


def has_port(obj: dict, kind: str):
    """True/False from the object's port list, or None when that list is not sourced.

    Same rule as the control counts: a sourced `ports` list is the maker's own, so a
    kind missing from it is a sourced NO, not an unknown.
    """
    if any(p.get("kind") == kind for p in obj.get("ports") or []):
        return True
    return False if is_sourced(obj, "ports") else None


def preset_order(obj: dict) -> tuple:
    """Presets are listed by brand, then release (or announcement) date, then key."""
    return (obj.get("brand", "").lower(), obj.get("released") or obj.get("announced") or "",
            obj["key"])


# ─────────────────────────────────────────────────────────────────────────────
# One family
# ─────────────────────────────────────────────────────────────────────────────

class Family:
    """A family entry is the ONLY place a family-specific name appears in the assembly.

    Adding the next archetype is a new module with its own base / rules / read / derive and
    one entry in `presets.FAMILIES`; nothing here moves.
    """

    __slots__ = ("slug", "base", "read", "derive", "axis_mapping", "source_line",
                 "registry_extra", "extra_presets", "caveats", "supplemental_keys")

    def __init__(self, *, slug, base, read, derive, axis_mapping, source_line,
                 registry_extra=None, extra_presets=(), caveats=None, supplemental_keys=()):
        self.slug = slug
        self.base = base
        self.read = read
        self.derive = derive
        self.axis_mapping = axis_mapping
        self.source_line = source_line
        self.registry_extra = registry_extra
        # Exact edition envelopes can feed a family without changing catalog classification.
        self.supplemental_keys = tuple(supplemental_keys)
        #: Presets that are NOT products — a named point in the archetype's own parameter
        #: space, such as a fold state. They carry no `registry` block because they assert
        #: nothing about any product.
        self.extra_presets = list(extra_presets)
        #: Objects filed in the family whose archetype they do not quite obey; carried
        #: because their envelope is sourced and useful, with the caveat printed.
        self.caveats = dict(caveats or {})


def _skipped(obj: dict, reason: str) -> dict:
    return {"slug": obj["key"], "brand": obj.get("brand"), "model": obj.get("model"),
            "status": obj.get("status"), "reason": reason}


def build_presets(fam: Family, objects: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return (presets, skipped) for one family."""
    presets, skipped = [], []
    for obj in sorted(objects, key=preset_order):
        src = fam.read(obj)
        if src is None:
            skipped.append(_skipped(obj, "closed envelope unresolved in the catalog (null)"))
            continue
        try:
            values, fallbacks = fam.derive(src, full=False)
        except DeriveError as exc:
            skipped.append(_skipped(obj, str(exc)))
            continue

        caveat = fam.caveats.get(obj["key"])
        if caveat:
            values["fold_angle"] = 0

        model = obj.get("model") or obj["key"]
        preset = {
            "slug": obj["key"],
            "label": {
                "en": model,
                "es": model,      # product names are proper nouns; not translated
            },
            "source": (
                f"hyperobjects-spec reference-objects catalog, object `{obj['key']}` "
                f"(status: {obj.get('status')}); {fam.source_line} "
                f"Generated by tools/presets/presets.py — do not edit by hand."
            ),
            "registry": {
                "device": obj["key"],
                "catalog": "hyperobjects_reference",
                "status": obj.get("status"),
                "igdb_platform": (obj.get("external_ids") or {}).get("igdb_platform"),
                "sourced": sorted({
                    s.get("field", "").split("[")[0].split(".")[0]
                    for s in obj.get("sources") or []
                    if s.get("field")
                }),
                "archetype_fallbacks": fallbacks,
            },
            "values": values,
        }
        # A family may route an explicitly supported variation to its own mode.
        # This does not change unscoped legacy presets or their render targets.
        if src.get("_preset_mode"):
            preset["mode"] = src["_preset_mode"]
        if fam.registry_extra is not None:
            preset["registry"].update(fam.registry_extra(obj, values))
        if caveat:
            preset["registry"]["caveat"] = caveat
        presets.append(preset)
    presets.extend(json.loads(json.dumps(fam.extra_presets)))
    return presets, skipped


def generated_from(fam: Family, objects: list[dict], skipped: list[dict],
                   directory: str | Path | None = None) -> dict:
    """The provenance block. It carries the family digest of the facts and no keystone
    version, so a keystone bump that moves no fact leaves every manifest unchanged."""
    return {
        "note": (
            "GENERATED — do not edit `presets` by hand. Every dimension in every preset is "
            "read from the keystone's reference-objects catalog (hyperobjects_reference) or "
            "derived from it by the archetype rules in tools/presets and in docs/README.md. "
            "Re-run the generator to change them."
        ),
        "generator": "solid-hyperobjects:tools/presets/presets.py",
        "command": (
            f"python3 tools/presets/presets.py --family {fam.slug} "
            f"--write {fam.slug}/project.json"
        ),
        "catalog": {
            "package": "hyperobjects-spec",
            "module": "hyperobjects_reference",
            "schema": "reference-object",
            "family_digest": family_digest(fam.slug, directory),
            "objects": len(objects),
            "rule": CATALOG_RULE,
        },
        "family": fam.slug,
        "axis_mapping": fam.axis_mapping,
        "awaiting_a_source": skipped,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Manifest writing / checking
# ─────────────────────────────────────────────────────────────────────────────

def manifest_defaults(manifest: dict) -> dict:
    return {p["id"]: p.get("default") for p in manifest.get("parameters", []) if "id" in p}


def generated(fam: Family, directory: str | Path | None = None) -> tuple[dict, list[dict]]:
    """(`_generated_from`, `presets`) exactly as the generator emits them today."""
    objects = load_family(fam.slug, directory)
    objects += [load_object(key, directory) for key in fam.supplemental_keys]
    presets, skipped = build_presets(fam, objects)
    metadata = generated_from(fam, objects, skipped, directory)
    if fam.supplemental_keys:
        metadata["catalog"]["supplemental_objects"] = {
            obj["key"]: object_digest(obj) for obj in objects
            if obj["key"] in fam.supplemental_keys
        }
    return metadata, presets


def write_manifest(path: Path, fam: Family, directory: str | Path | None = None) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["_generated_from"], manifest["presets"] = generated(fam, directory)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def check_manifest(path: Path, fam: Family, directory: str | Path | None = None) -> list[str]:
    """Every way the manifest differs from what the generator would write today."""
    manifest = json.loads(path.read_text(encoding="utf-8"))
    block, presets = generated(fam, directory)
    problems = []
    if manifest.get("presets") != presets:
        have = {p.get("slug"): p for p in manifest.get("presets") or []}
        want = {p.get("slug"): p for p in presets}
        drifted = sorted(s for s in set(have) | set(want) if have.get(s) != want.get(s))
        problems.append("presets[] differs from what the generator emits"
                        + (f" ({', '.join(map(str, drifted))})" if drifted else " (order)"))
    if manifest.get("_generated_from") != block:
        problems.append("_generated_from differs from what the generator emits")

    wanted_defaults, _ = fam.derive(fam.base, full=True)
    have_defaults = manifest_defaults(manifest)
    for key, value in wanted_defaults.items():
        if key not in have_defaults:
            problems.append(f"parameter `{key}` is missing from the manifest")
        elif have_defaults[key] != value:
            problems.append(f"parameter `{key}` default is {have_defaults[key]!r}, "
                            f"the archetype rules give {value!r}")
    for key in have_defaults:
        if key not in wanted_defaults:
            problems.append(f"parameter `{key}` is not produced by the archetype rules")
    return problems


def report(path: Path, problems: list[str]) -> int:
    if problems:
        print(f"FAIL: {path}", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"OK: {path} matches the reference catalog and the archetype rules")
    return 0
