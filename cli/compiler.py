#!/usr/bin/env python3
"""
Metropolis Procedural Spatial Compiler (cli/compiler.py)
Transforms a declarative semantic city specification (02-city-spec.json)
into a production-grade 3D WebGL MapLibre dataset (city-data.js) and standalone viewer.

Usage:
    python -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --out docs/city-data.js
    python -m cli.compiler --spec my-spec.json --web-dir dist/ --serve 8080
"""

import argparse
import colorsys
import http.server
import json
import math
import os
import shutil
import socketserver
import sys

# Geodetic constants for latitude ~52.5 degrees (meters to degrees conversion)
LAT_CENTER = 52.5150
LNG_CENTER = 13.4000
DEG_LAT_PER_METER = 1.0 / 111320.0
DEG_LNG_PER_METER = 1.0 / (111320.0 * math.cos(math.radians(LAT_CENTER)))

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))

def adjust_color(hex_str, sat_mult=1.0, light_mult=1.0):
    try:
        r, g, b = hex_to_rgb(hex_str)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l = min(1.0, max(0.0, l * light_mult))
        s = min(1.0, max(0.0, s * sat_mult))
        nr, ng, nb = colorsys.hls_to_rgb(h, l, s)
        return rgb_to_hex(nr, ng, nb)
    except Exception:
        return hex_str

BADGE_MIN_SEPARATION_M = 220.0

# Vertical exaggeration applied to all 3D buildings (1 / 1.5 keeps the skyline readable)
BUILDING_HEIGHT_SCALE = 1.0 / 1.5

# Field constraints: tape colours are kept clear of the district accent hues
FIELD_PALETTE = ['#e8ecf5', '#ff4d9d', '#8c9eff', '#ff8a50', '#b2ff59', '#ffd740']
FIELD_TAPE_INSET_M = 14.0
FIELD_TAPE_SPACING_M = 16.0

# Project status of spires: amber scaffolding around a spire that is still being built
SPIRE_STATUSES = ('done', 'active', 'planned')
SCAFFOLD_COLOR = '#ffb300'

# Claims tested by a study: pin colour by verdict
CHALLENGE_VERDICTS = ('supported', 'conditional', 'contradicted', 'exploratory')
VERDICT_COLORS = {'supported': '#00e599', 'conditional': '#ffb700', 'contradicted': '#ff1744', 'exploratory': '#a0a8bc'}

# Plazas: data grids painted on the ground with bars per cell
PLAZA_LABEL_MARGIN_M = 180.0   # west margin for row labels
PLAZA_HEADER_MARGIN_M = 110.0  # north margin for title and column labels
PLAZA_MAX_BAR_M = 60.0

# "You are here" line extends this far beyond the districts on each side
NOW_LINE_OVERHANG_M = 140.0

# Priorities: ground target + hovering pin, in pale gold (amber belongs to a district hue)
PRIORITY_COLOR = '#ffe9a8'
PRIORITY_BEAM_COLOR = '#fff6d6'
PRIORITY_RING_RADII = (22.0, 40.0, 58.0)
PRIORITY_ARC_RADIUS = 74.0
PRIORITY_ARC_GAP_DEG = 10.0

def geo_distance_m(a, b):
    """Approximate ground distance in metres between two [lng, lat] points near the city centre."""
    return math.hypot((a[0] - b[0]) / DEG_LNG_PER_METER, (a[1] - b[1]) / DEG_LAT_PER_METER)

def scale_ring(ring, factor, center=None):
    """Scales a ring of [lng, lat] points about `center` (default: the ring's own centroid)."""
    pts = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
    if center is None:
        center = [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]
    return [[round(center[0] + (p[0] - center[0]) * factor, 7), round(center[1] + (p[1] - center[1]) * factor, 7)] for p in ring]

# --- Spire archetypes (spire `kind`) ---------------------------------------
# Every archetype is a stack of vertical prisms (fill-extrusion) with a ~110 m footprint.
# Tiers flagged `top` become the translucent part of an `active` (unfinished) spire.
SPIRE_KINDS = ('system', 'knowledge', 'instrument', 'hub')

def _local(lng, lat):
    """Returns a function mapping local metre offsets (dx east, dy north) to [lng, lat]."""
    return lambda dx, dy: [round(lng + dx * DEG_LNG_PER_METER, 7), round(lat + dy * DEG_LAT_PER_METER, 7)]

def _ring(pt, pts):
    ring = [pt(x, y) for x, y in pts]
    return ring + [ring[0]]

def _rect(pt, x0, y0, x1, y1):
    return _ring(pt, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])

def _disc(pt, r, n=24, cx=0.0, cy=0.0):
    return _ring(pt, [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)])

def _tier(name, rings, base_h, top_h, color, top=False):
    return {'name': name, 'rings': rings, 'base_h': base_h, 'top_h': top_h, 'color': color, 'top': top}

def build_spire_shape(kind, lng, lat, H, colors, sides=8):
    """Tiers, scaffold and ground outlines for one spire of the given archetype and height H."""
    pt = _local(lng, lat)
    white = '#ffffff'

    if kind == 'knowledge':  # cathedral: Latin-cross nave facing south, twin west towers with spires
        cross = [(-17, -55), (17, -55), (17, 10), (42, 10), (42, 40), (17, 40), (17, 55),
                 (-17, 55), (-17, 40), (-42, 40), (-42, 10), (-17, 10)]
        nave_h = max(28.0, H * 0.30)
        tower_h = H * 0.70
        tiers = [
            _tier('plinth', [_rect(pt, -48, -64, 48, 66)], 0.0, 4.0, colors['base']),
            _tier('nave', [_ring(pt, cross)], 4.0, nave_h, colors['lower']),
            _tier('apse', [_ring(pt, [(17 * math.cos(math.pi * i / 10), 55 + 17 * math.sin(math.pi * i / 10)) for i in range(11)])], 4.0, nave_h, colors['lower']),
            _tier('nave-roof', [_rect(pt, -8, -52, 8, 52)], nave_h, nave_h + H * 0.07, colors['mid']),
            _tier('transept-roof', [_rect(pt, -39, 21, 39, 29)], nave_h, nave_h + H * 0.07, colors['mid']),
            _tier('lantern', [_rect(pt, -10, 15, 10, 35)], nave_h, H * 0.48, colors['mid']),
            _tier('lantern-cap', [_rect(pt, -6, 19, 6, 31)], H * 0.48, H * 0.55, colors['crown']),
        ]
        for side, tx in (('w', -13), ('e', 13)):
            tiers.append(_tier(f'tower-{side}', [_rect(pt, tx - 8, -55, tx + 8, -39)], 4.0, tower_h, colors['mid']))
            steps = [(6.5, 0.79), (4.5, 0.87), (3.0, 0.94), (1.5, 1.0)]
            prev = tower_h
            for i, (half, frac) in enumerate(steps):
                tiers.append(_tier(f'spire-{side}{i}', [_rect(pt, tx - half, -47 - half, tx + half, -47 + half)],
                                   prev, H * frac, colors['crown'] if i < 3 else white, top=True))
                prev = H * frac
        scaffold = {'posts': [pt(x, y) for x, y in ((-25, -60), (25, -60), (-25, -34), (25, -34))],
                    'base_h': tower_h, 'top_h': H + 6.0, 'deck': _rect(pt, -26, -61, 26, -33)}
        return {'tiers': tiers, 'scaffold': scaffold, 'outlines': [_ring(pt, cross)]}

    if kind == 'instrument':  # observatory: round drum, catwalk, stepped hemispherical dome
        r = 38.0
        drum_top = max(30.0, H - r)
        tiers = [
            _tier('pedestal', [_disc(pt, 56)], 0.0, 5.0, colors['base']),
            _tier('drum', [_disc(pt, 40)], 5.0, drum_top, colors['lower']),
            _tier('catwalk', [_disc(pt, 46), _disc(pt, 40)[::-1]], drum_top * 0.55, drum_top * 0.55 + 2.5, colors['mid']),
        ]
        steps = 6
        for i in range(steps):
            z0, z1 = r * i / steps, r * (i + 1) / steps
            zm = (z0 + z1) / 2
            tiers.append(_tier(f'dome-{i}', [_disc(pt, r * math.sqrt(max(0.0, 1 - (zm / r) ** 2)))],
                               drum_top + z0, drum_top + z1, colors['crown'], top=True))
        tiers.append(_tier('finial', [_disc(pt, 2.5, n=8)], drum_top + r, drum_top + r + 8, white, top=True))
        scaffold = {'posts': [pt(42 * math.cos(a), 42 * math.sin(a)) for a in (0.79, 2.36, 3.93, 5.50)],
                    'base_h': drum_top, 'top_h': drum_top + r + 6, 'deck': _disc(pt, 44)}
        return {'tiers': tiers, 'scaffold': scaffold, 'outlines': [_disc(pt, 40), _disc(pt, 56)]}

    if kind == 'hub':  # TV tower: flared base, slim shaft, spherical pod, upper mast, antenna
        pod_z, pod_r = H * 0.67, 21.0
        tiers = [
            _tier('pedestal', [_disc(pt, 40, n=16)], 0.0, 8.0, colors['base']),
            _tier('flare-0', [_disc(pt, 22, n=16)], 8.0, H * 0.06, colors['lower']),
            _tier('flare-1', [_disc(pt, 15, n=16)], H * 0.06, H * 0.12, colors['lower']),
            _tier('flare-2', [_disc(pt, 10, n=12)], H * 0.12, H * 0.18, colors['mid']),
            _tier('shaft', [_disc(pt, 6.5, n=12)], H * 0.18, pod_z - pod_r, colors['mid']),
        ]
        steps = 6
        for i in range(steps):
            z0 = -pod_r + 2 * pod_r * i / steps
            z1 = -pod_r + 2 * pod_r * (i + 1) / steps
            zm = (z0 + z1) / 2
            tiers.append(_tier(f'pod-{i}', [_disc(pt, pod_r * math.sqrt(max(0.05, 1 - (zm / pod_r) ** 2)))],
                               pod_z + z0, pod_z + z1, colors['crown'], top=True))
        tiers.append(_tier('mast', [_disc(pt, 4.0, n=10)], pod_z + pod_r, H * 0.86, colors['mid'], top=True))
        tiers.append(_tier('antenna', [_disc(pt, 1.6, n=6)], H * 0.86, H, white, top=True))
        scaffold = {'posts': [pt(26 * math.cos(a), 26 * math.sin(a)) for a in (0.79, 2.36, 3.93, 5.50)],
                    'base_h': pod_z - pod_r, 'top_h': H + 4, 'deck': _disc(pt, 28)}
        return {'tiers': tiers, 'scaffold': scaffold, 'outlines': [_disc(pt, 40, n=16)]}

    # system (default): stepped skyscraper with setbacks and a needle
    base_tier_h, mid_tier_h = round(H * 0.35, 1), round(H * 0.72, 1)
    poly_t1 = create_regular_polygon(lng, lat, 44.0, sides=sides, rotation_deg=0)
    poly_t2 = create_regular_polygon(lng, lat, 32.0, sides=sides, rotation_deg=22.5)
    tiers = [
        _tier('pedestal', [create_regular_polygon(lng, lat, 56.0, sides=sides, rotation_deg=15)], 0.0, 5.0, colors['base']),
        _tier('tier1', [poly_t1], 5.0, base_tier_h, colors['lower']),
        _tier('tier2', [poly_t2], base_tier_h, mid_tier_h, colors['mid']),
        _tier('tier3', [create_regular_polygon(lng, lat, 20.0, sides=sides, rotation_deg=45)], mid_tier_h, H, colors['crown'], top=True),
        _tier('needle', [create_regular_polygon(lng, lat, 5.0, sides=4, rotation_deg=45)], H, round(H + 32.0, 1), white, top=True),
    ]
    scaffold = {'posts': create_regular_polygon(lng, lat, 24.0, sides=4, rotation_deg=45)[:4],
                'base_h': mid_tier_h, 'top_h': H + 8.0,
                'deck': create_regular_polygon(lng, lat, 27.0, sides=4, rotation_deg=45)}
    return {'tiers': tiers, 'scaffold': scaffold, 'outlines': [poly_t1, poly_t2]}

def place_on_curve(curve_coords, placed, preferred_idx=None, min_sep=BADGE_MIN_SEPARATION_M):
    """Picks a point on the curve for a marker: the preferred index (default: the apex)
    if it is clear of already-placed markers, otherwise the nearest point along the
    curve that is, falling back to the most isolated point. Returns (point, index)."""
    last = len(curve_coords) - 1
    start = last // 2 if preferred_idx is None else max(2, min(last - 2, preferred_idx))
    candidates = [start]
    for step in range(1, last):
        for idx in (start - step, start + step):
            if 2 <= idx <= last - 2:
                candidates.append(idx)
    best, best_idx, best_clearance = curve_coords[start], start, -1.0
    for idx in candidates:
        pt = curve_coords[idx]
        clearance = min((geo_distance_m(pt, q) for q in placed), default=float('inf'))
        if clearance >= min_sep:
            return pt, idx
        if clearance > best_clearance:
            best, best_idx, best_clearance = pt, idx, clearance
    return best, best_idx

def meters_to_geo(dx_meters, dy_meters, base_lng=LNG_CENTER, base_lat=LAT_CENTER):
    """Convert delta (x, y) in meters to geodetic (lng, lat)."""
    return [
        round(base_lng + dx_meters * DEG_LNG_PER_METER, 7),
        round(base_lat + dy_meters * DEG_LAT_PER_METER, 7)
    ]

def create_regular_polygon(center_lng, center_lat, radius_meters, sides=8, rotation_deg=0):
    """Generates coordinates for a closed regular polygon in meters around center."""
    coords = []
    rot_rad = math.radians(rotation_deg)
    for i in range(sides):
        angle = rot_rad + (2 * math.pi * i) / sides
        dx = radius_meters * math.cos(angle)
        dy = radius_meters * math.sin(angle)
        coords.append(meters_to_geo(dx, dy, center_lng, center_lat))
    coords.append(coords[0])  # Close the ring
    return coords

def create_rectangle(center_lng, center_lat, width_m, height_m):
    """Generates a rectangular polygon in meters around center."""
    hw = width_m / 2.0
    hh = height_m / 2.0
    corners = [
        meters_to_geo(-hw, -hh, center_lng, center_lat),
        meters_to_geo(hw, -hh, center_lng, center_lat),
        meters_to_geo(hw, hh, center_lng, center_lat),
        meters_to_geo(-hw, hh, center_lng, center_lat),
        meters_to_geo(-hw, -hh, center_lng, center_lat)
    ]
    return corners

def bezier_curve(p0, p1, p2, p3, steps=28):
    """Generates cubic Bezier curve points between p0 and p3 with control points p1 and p2."""
    points = []
    for step in range(steps + 1):
        t = step / steps
        lng = ((1 - t) ** 3 * p0[0] +
               3 * ((1 - t) ** 2) * t * p1[0] +
               3 * (1 - t) * (t ** 2) * p2[0] +
               (t ** 3) * p3[0])
        lat = ((1 - t) ** 3 * p0[1] +
               3 * ((1 - t) ** 2) * t * p1[1] +
               3 * (1 - t) * (t ** 2) * p2[1] +
               (t ** 3) * p3[1])
        points.append([round(lng, 7), round(lat, 7)])
    return points

def validate_spec(spec):
    """Validates structural integrity and reference resolution of the spec."""
    errors = []
    if 'city_metadata' not in spec:
        errors.append("Missing required field 'city_metadata'")
    if 'districts' not in spec or not spec['districts']:
        errors.append("Spec must contain non-empty 'districts' array")
    if 'spires' not in spec:
        errors.append("Spec must contain 'spires' array")

    district_ids = {d['id']: d for d in spec.get('districts', [])}
    spire_ids = {}

    for d in spec.get('districts', []):
        if not d.get('id', '').startswith('@dist-'):
            errors.append(f"District ID must start with '@dist-': {d.get('id')}")

    for s in spec.get('spires', []):
        sid = s.get('id', '')
        if not sid.startswith('@spire-'):
            errors.append(f"Spire ID must start with '@spire-': {sid}")
        dref = s.get('district_ref')
        if dref not in district_ids:
            errors.append(f"Spire {sid} references unknown district {dref}")
        spire_ids[sid] = s

    for b in spec.get('bottlenecks', []):
        bid = b.get('id', '')
        if not bid.startswith('@bneck-'):
            errors.append(f"Bottleneck ID must start with '@bneck-': {bid}")
        dref = b.get('district_ref')
        if dref not in district_ids:
            errors.append(f"Bottleneck {bid} references unknown district {dref}")

    for c in spec.get('challenges', []):
        cid = c.get('id', '')
        if not cid.startswith('@chal-'):
            errors.append(f"Challenge ID must start with '@chal-': {cid}")
        dref = c.get('district_ref')
        if dref not in district_ids:
            errors.append(f"Challenge {cid} references unknown district {dref}")

    for cond in spec.get('conduits', []):
        cid = cond.get('id', '')
        if not cid.startswith('@conduit-'):
            errors.append(f"Conduit ID must start with '@conduit-': {cid}")
        if cond.get('from') not in spire_ids:
            errors.append(f"Conduit {cid} 'from' references unknown spire {cond.get('from')}")
        if cond.get('to') not in spire_ids:
            errors.append(f"Conduit {cid} 'to' references unknown spire {cond.get('to')}")
        if cond.get('status', 'operational') not in CONDUIT_STATUSES:
            errors.append(f"Conduit {cid} has unknown status '{cond.get('status')}' (expected one of {', '.join(CONDUIT_STATUSES)})")

    errors.extend(validate_v2_semantics(spec, district_ids, spire_ids))
    return errors

# --- Schema v2: constraint semantics ---------------------------------------
CONDUIT_STATUSES = ('operational', 'thin', 'planned')
SCOPE_TARGET_PREFIX = {'edge': '@conduit-', 'node': '@spire-', 'field': '@dist-'}
SCOPE_EFFECTS = {
    'edge': ('slowdown', 'closure'),
    'node': ('slowdown', 'closure'),
    'field': ('slowdown', 'noise', 'blind'),
}
REMEDY_PREFIXES = ('@conduit-', '@spire-', '@chal-')

def validate_v2_semantics(spec, district_ids, spire_ids):
    """Hard errors for the optional schema-v2 fields (scope/constrains/effect/at/remedied_by,
    advanced_by/blocked_by). Specs without these fields are unaffected."""
    errors = []
    conduit_ids = {c.get('id') for c in spec.get('conduits', [])}
    chal_ids = {c.get('id') for c in spec.get('challenges', [])}
    bneck_ids = {b.get('id') for b in spec.get('bottlenecks', [])}
    plaza_ids = {p.get('id') for p in spec.get('plazas', [])}
    known = {'@conduit-': conduit_ids, '@spire-': set(spire_ids), '@dist-': set(district_ids), '@chal-': chal_ids}

    def resolves(ref):
        return any(ref.startswith(pfx) and ref in ids for pfx, ids in known.items())

    for b in spec.get('bottlenecks', []):
        bid = b.get('id', '')
        scope = b.get('scope')
        if scope is None:
            for field in ('constrains', 'effect', 'at'):
                if field in b:
                    errors.append(f"Bottleneck {bid} sets '{field}' but has no 'scope'")
            continue
        if scope not in SCOPE_TARGET_PREFIX:
            errors.append(f"Bottleneck {bid} has unknown scope '{scope}' (expected edge | node | field)")
            continue
        targets = b.get('constrains') or []
        if not targets:
            errors.append(f"Bottleneck {bid} (scope {scope}) must list at least one 'constrains' target")
        prefix = SCOPE_TARGET_PREFIX[scope]
        for ref in targets:
            if not ref.startswith(prefix):
                errors.append(f"Bottleneck {bid} (scope {scope}) can only constrain {prefix}* refs, got {ref}")
            elif not resolves(ref):
                errors.append(f"Bottleneck {bid} constrains unknown {ref}")
        effect = b.get('effect', 'slowdown')
        if effect not in SCOPE_EFFECTS[scope]:
            errors.append(f"Bottleneck {bid}: effect '{effect}' is not valid for scope {scope} (allowed: {', '.join(SCOPE_EFFECTS[scope])})")
        if 'at' in b:
            if scope != 'edge':
                errors.append(f"Bottleneck {bid}: 'at' is only meaningful for scope edge")
            elif not isinstance(b['at'], (int, float)) or not 0.0 <= b['at'] <= 1.0:
                errors.append(f"Bottleneck {bid}: 'at' must be a number in 0..1")
        for ref in b.get('remedied_by', []):
            if not ref.startswith(REMEDY_PREFIXES) or not resolves(ref):
                errors.append(f"Bottleneck {bid} remedied_by unknown or unsupported ref {ref}")

    bs = spec.get('city_metadata', {}).get('building_scale', 1.0)
    if not isinstance(bs, (int, float)) or not 0.2 <= bs <= 3.0:
        errors.append("city_metadata.building_scale must be a number between 0.2 and 3.0")
    for sp in spec.get('spires', []):
        if sp.get('kind', 'system') not in SPIRE_KINDS:
            errors.append(f"Spire {sp.get('id')} has unknown kind '{sp.get('kind')}' (expected one of {', '.join(SPIRE_KINDS)})")
        if sp.get('status', 'done') not in SPIRE_STATUSES:
            errors.append(f"Spire {sp.get('id')} has unknown status '{sp.get('status')}' (expected one of {', '.join(SPIRE_STATUSES)})")
    for b in spec.get('bottlenecks', []):
        for ref in b.get('causes', []):
            if ref not in bneck_ids or ref == b.get('id'):
                errors.append(f"Bottleneck {b.get('id')} causes unknown or self ref {ref}")
    now = spec.get('city_metadata', {}).get('now_marker')
    if now:
        if now.get('district_ref') not in district_ids:
            errors.append(f"now_marker references unknown district {now.get('district_ref')}")
        pos = now.get('position', 0.5)
        if not isinstance(pos, (int, float)) or not 0.0 <= pos <= 1.0:
            errors.append("now_marker.position must be a number in 0..1 (0 = south edge, 1 = north edge)")

    for c in spec.get('challenges', []):
        cid = c.get('id', '')
        for ref in c.get('advanced_by', []):
            if ref not in spire_ids and ref not in plaza_ids:
                errors.append(f"Challenge {cid} advanced_by unknown spire or plaza {ref}")
        for ref in c.get('blocked_by', []):
            if ref not in bneck_ids and ref not in spire_ids and ref not in plaza_ids:
                errors.append(f"Challenge {cid} blocked_by unknown bottleneck, spire or plaza {ref}")
        if c.get('verdict') is not None and c['verdict'] not in CHALLENGE_VERDICTS:
            errors.append(f"Challenge {cid} has unknown verdict '{c['verdict']}' (expected one of {', '.join(CHALLENGE_VERDICTS)})")
    all_refs = set(district_ids) | set(spire_ids) | bneck_ids | plaza_ids | \
        {c.get('id') for c in spec.get('challenges', [])} | {c.get('id') for c in spec.get('conduits', [])}
    for t_idx, stop in enumerate(spec.get('tour', [])):
        label = stop.get('id', f'#{t_idx + 1}')
        if not stop.get('title') or not stop.get('text'):
            errors.append(f"Tour stop {label} needs a title and a text")
        for ref in stop.get('focus', []):
            if ref not in all_refs:
                errors.append(f"Tour stop {label} focuses on unknown {ref}")
        target = stop.get('camera', {}).get('target')
        if target and target != 'city' and target not in all_refs:
            errors.append(f"Tour stop {label} camera target is unknown: {target}")
        for pid in stop.get('plaza_layers', {}):
            if pid not in plaza_ids:
                errors.append(f"Tour stop {label} sets a layer on unknown plaza {pid}")
    for pz in spec.get('plazas', []):
        pid = pz.get('id', '')
        if not pid.startswith('@plaza-'):
            errors.append(f"Plaza ID must start with '@plaza-': {pid}")
        if pz.get('district_ref') not in district_ids:
            errors.append(f"Plaza {pid} references unknown district {pz.get('district_ref')}")
        rows, cols = pz.get('rows', []), pz.get('cols', [])
        if not rows or not cols:
            errors.append(f"Plaza {pid} needs non-empty 'rows' and 'cols'")
        for layer in pz.get('layers', []):
            cells = layer.get('cells', [])
            if len(cells) != len(rows) or any(len(r) != len(cols) for r in cells):
                errors.append(f"Plaza {pid} layer '{layer.get('id')}' must have {len(rows)}x{len(cols)} cells (null for unpublished)")
        for h in pz.get('highlight', []):
            if not (0 <= h.get('row', -1) < len(rows) and 0 <= h.get('col', -1) < len(cols)):
                errors.append(f"Plaza {pid} highlight outside the grid: {h}")
    return errors

def lint_spec(spec):
    """Non-fatal warnings about schema-v2 semantics that are valid but probably unintended."""
    warnings = []
    bnecks = spec.get('bottlenecks', [])
    spires = {s['id']: s for s in spec.get('spires', [])}
    conduits = {c['id']: c for c in spec.get('conduits', [])}
    scoped = [b for b in bnecks if b.get('scope')]
    if scoped and len(scoped) < len(bnecks):
        for b in bnecks:
            if not b.get('scope'):
                warnings.append(f"Bottleneck {b['id']} has no scope; it is drawn as a legacy tower")
    referenced = set()
    for b in scoped:
        referenced.update(b.get('constrains', []))
        referenced.update(b.get('remedied_by', []))
        for ref in b.get('constrains', []):
            if ref in b.get('remedied_by', []):
                warnings.append(f"Bottleneck {b['id']} both constrains and is remedied by {ref}")
        if b['scope'] == 'edge':
            endpoint_districts = set()
            for ref in b.get('constrains', []):
                cond = conduits.get(ref)
                if cond:
                    for end in (cond['from'], cond['to']):
                        if end in spires:
                            endpoint_districts.add(spires[end]['district_ref'])
            if endpoint_districts and b['district_ref'] not in endpoint_districts:
                warnings.append(f"Bottleneck {b['id']} (edge) lives in {b['district_ref']}, away from the conduits it constrains")
    for cid, cond in conduits.items():
        ends_planned = any(spires.get(end, {}).get('status') == 'planned' for end in (cond['from'], cond['to']))
        if cond.get('status') == 'planned' and cid not in referenced and not ends_planned:
            warnings.append(f"Conduit {cid} is 'planned' but no bottleneck explains or is remedied by it")
    return warnings

def compile_metropolis_data(spec):
    """Compiles the spec into GeoJSON features and metadata structures."""
    district_ids = {d['id']: d for d in spec['districts']}
    DISTRICT_WIDTH = 1100.0   # meters
    DISTRICT_HEIGHT = 680.0   # meters
    DISTRICT_GAP = 240.0      # meters

    compiled_districts = []
    spire_locations = {}
    district_centers = {}

    sorted_districts = sorted(spec['districts'], key=lambda x: x.get('order', 1))
    num_districts = len(sorted_districts)
    total_span = (num_districts - 1) * (DISTRICT_HEIGHT + DISTRICT_GAP)
    start_y = -total_span / 2.0

    building_features = []
    wireframe_features = []

    # 1. Compile Districts & Spires
    for idx, dist in enumerate(sorted_districts):
        dist_y = start_y + idx * (DISTRICT_HEIGHT + DISTRICT_GAP)
        dist_x = 0.0
        center_coords = meters_to_geo(dist_x, dist_y)
        district_centers[dist['id']] = {
            'lng': center_coords[0],
            'lat': center_coords[1],
            'dy': dist_y,
            'color': dist['color']
        }

        runway_poly = create_rectangle(center_coords[0], center_coords[1], DISTRICT_WIDTH, DISTRICT_HEIGHT)
        compiled_districts.append({
            'id': dist['id'],
            'name': dist['name'],
            'scale_label': dist.get('scale_label', f"Level {idx+1}"),
            'order': dist.get('order', idx+1),
            'color': dist['color'],
            'glow': dist.get('glow', 'rgba(0, 240, 255, 0.4)'),
            'description': dist.get('description', ''),
            'eu_infrastructures': dist.get('eu_infrastructures', []),
            'center': center_coords,
            'bounds': runway_poly
        })

        dist_spires = [s for s in spec.get('spires', []) if s['district_ref'] == dist['id']]
        spire_offsets = [
            (-320.0, 30.0, 8),
            (0.0, -40.0, 6),
            (320.0, 30.0, 8),
            (0.0, 230.0, 6),
            (-160.0, -230.0, 6),
            (160.0, -230.0, 6)
        ]

        for s_idx, spire in enumerate(dist_spires):
            offset_x, offset_y, sides = spire_offsets[s_idx % len(spire_offsets)]
            if 'place' in spire:  # explicit position in metres from the district centre
                offset_x, offset_y = float(spire['place'][0]), float(spire['place'][1])
            spire_lnglat = meters_to_geo(dist_x + offset_x, dist_y + offset_y)
            spire_locations[spire['id']] = {
                'lng': spire_lnglat[0],
                'lat': spire_lnglat[1],
                'title': spire['title'],
                'codename': spire.get('codename', spire.get('code', 'SPIRE')),
                'district_ref': dist['id'],
                'color': dist['color']
            }

            scale_lvl = spire.get('scale_level', 0.8)
            # Towering 3D Heights: 120m to 210m tall (before the global and per-city scales)
            total_height = round(100.0 + scale_lvl * 110.0, 1)
            colors = {
                'base': dist['color'],
                'lower': adjust_color(dist['color'], sat_mult=1.0, light_mult=0.42),
                'mid': adjust_color(dist['color'], sat_mult=0.95, light_mult=0.68),
                'crown': dist['color']
            }
            kind = spire.get('kind', 'system')
            shape = build_spire_shape(kind, spire_lnglat[0], spire_lnglat[1], total_height, colors, sides)

            # Project status (schema v2): done = solid; active = solid body with the building's
            # top part as a translucent ghost inside amber scaffolding; planned = whole ghost.
            status = spire.get('status', 'done')
            for tier in shape['tiers']:
                ghost = status == 'planned' or (status == 'active' and tier['top'])
                props = {
                    'id': f"{spire['id']}-{tier['name']}", 'spire_ref': spire['id'], 'entity_type': 'spire',
                    'name': spire['title'], 'tier': tier['name'], 'kind': kind, 'status': status,
                    'height': round(tier['top_h'], 1), 'base_height': round(tier['base_h'], 1), 'color': tier['color']
                }
                if ghost:
                    props['ghost'] = True
                building_features.append({'type': 'Feature', 'properties': props,
                                          'geometry': {'type': 'Polygon', 'coordinates': tier['rings']}})
            if status == 'active':
                sc = shape['scaffold']
                for c_idx, corner in enumerate(sc['posts']):
                    building_features.append({
                        'type': 'Feature',
                        '_center': [spire_lnglat[0], spire_lnglat[1]],  # posts scale towards the spire axis
                        'properties': {
                            'id': f"{spire['id']}-scaffold-{c_idx}", 'spire_ref': spire['id'], 'entity_type': 'spire',
                            'name': spire['title'], 'tier': 'scaffold', 'kind': kind, 'status': status,
                            'height': round(sc['top_h'], 1), 'base_height': round(sc['base_h'], 1), 'color': SCAFFOLD_COLOR
                        },
                        'geometry': {'type': 'Polygon', 'coordinates': [create_regular_polygon(corner[0], corner[1], 2.4, sides=4)]}
                    })
                building_features.append({
                    'type': 'Feature',
                    '_center': [spire_lnglat[0], spire_lnglat[1]],
                    'properties': {
                        'id': f"{spire['id']}-scaffold-deck", 'spire_ref': spire['id'], 'entity_type': 'spire',
                        'name': spire['title'], 'tier': 'scaffold', 'kind': kind, 'status': status,
                        'height': round(sc['base_h'] + 2.0, 1), 'base_height': round(sc['base_h'], 1), 'color': SCAFFOLD_COLOR
                    },
                    'geometry': {'type': 'Polygon', 'coordinates': [sc['deck']]}
                })

            # Ground outlines for crisp facet edges
            for ring in shape['outlines']:
                wireframe_features.append({
                    'type': 'Feature',
                    'properties': {'color': dist['color']},
                    'geometry': {'type': 'LineString', 'coordinates': ring}
                })

    # 2. 3D Bottleneck Hazard Radars (Dynamic height based on severity!)
    compiled_bottlenecks = []
    bneck_offsets = [(-490.0, -180.0), (490.0, 180.0), (-500.0, 160.0), (500.0, -170.0), (0.0, 250.0)]
    for b_idx, bneck in enumerate(spec.get('bottlenecks', [])):
        d_center = district_centers[bneck['district_ref']]
        off_x, off_y = bneck_offsets[b_idx % len(bneck_offsets)]
        coords = meters_to_geo(off_x, d_center['dy'] + off_y)
        codename = bneck.get('codename', bneck.get('code', f"BOT-0{b_idx+1}"))

        # Dynamic height scaling based on severity (0.4 to 1.0)
        severity = float(bneck.get('severity', 0.8))
        bneck_total_h = round(75.0 + severity * 95.0, 1)  # 113m to 170m
        base_h = round(bneck_total_h * 0.48, 1)
        core_h = round(bneck_total_h * 0.78, 1)
        needle_h = bneck_total_h

        compiled_bottlenecks.append({
            'id': bneck['id'],
            'code': bneck.get('code', f"BOT-0{b_idx+1}"),
            'codename': codename,
            'title': bneck['title'],
            'severity': severity,
            'district_ref': bneck['district_ref'],
            'nature': bneck.get('nature', 'Physical Rate-Limiter'),
            'impact': bneck.get('impact', ''),
            'remedy': bneck.get('remedy', ''),
            'coordinates': coords,
            'scope': bneck.get('scope'),
            'constrains': bneck.get('constrains', []),
            'effect': bneck.get('effect', 'slowdown') if bneck.get('scope') else None,
            'delay_label': bneck.get('delay_label', ''),
            'remedied_by': bneck.get('remedied_by', []),
            'causes': bneck.get('causes', []),
            'caused_by': [o['id'] for o in spec.get('bottlenecks', []) if bneck['id'] in o.get('causes', [])],
            'anchors': []
        })

        # Schema v2: scoped constraints are drawn on the roads, nodes and zones they
        # affect (section 4b), not as a standalone tower.
        if bneck.get('scope'):
            continue

        # Generate 3D Hazard Citadel (Red Hexagonal Obelisk)
        poly_bneck_base = create_regular_polygon(coords[0], coords[1], 42.0, sides=6, rotation_deg=0)
        building_features.append({
            'type': 'Feature',
            'properties': {
                'id': f"{bneck['id']}-base",
                'bottleneck_ref': bneck['id'],
                'entity_type': 'bottleneck',
                'name': bneck['title'],
                'codename': codename,
                'tier': 'hazard_base',
                'height': base_h,
                'base_height': 0.0,
                'color': '#800020',
                'opacity': 0.95
            },
            'geometry': {'type': 'Polygon', 'coordinates': [poly_bneck_base]}
        })

        poly_bneck_core = create_regular_polygon(coords[0], coords[1], 26.0, sides=6, rotation_deg=30)
        building_features.append({
            'type': 'Feature',
            'properties': {
                'id': f"{bneck['id']}-core",
                'bottleneck_ref': bneck['id'],
                'entity_type': 'bottleneck',
                'name': bneck['title'],
                'codename': codename,
                'tier': 'hazard_core',
                'height': core_h,
                'base_height': base_h,
                'color': '#ff1744',
                'opacity': 0.98
            },
            'geometry': {'type': 'Polygon', 'coordinates': [poly_bneck_core]}
        })

        poly_bneck_needle = create_regular_polygon(coords[0], coords[1], 5.0, sides=4, rotation_deg=45)
        building_features.append({
            'type': 'Feature',
            'properties': {
                'id': f"{bneck['id']}-needle",
                'bottleneck_ref': bneck['id'],
                'entity_type': 'bottleneck',
                'name': bneck['title'],
                'codename': codename,
                'tier': 'hazard_needle',
                'height': needle_h,
                'base_height': core_h,
                'color': '#ff3366',
                'opacity': 1.0
            },
            'geometry': {'type': 'Polygon', 'coordinates': [poly_bneck_needle]}
        })

    # 3. 3D Strategic Priorities & Challenges (Dynamic height based on impact_scale!)
    compiled_challenges = []
    target_features = []
    chal_offsets = [(470.0, -180.0), (-470.0, 190.0), (480.0, 150.0), (-480.0, -170.0), (0.0, -250.0)]
    for c_idx, chal in enumerate(spec.get('challenges', [])):
        d_center = district_centers[chal['district_ref']]
        off_x, off_y = chal_offsets[c_idx % len(chal_offsets)]
        if 'place' in chal:
            off_x, off_y = float(chal['place'][0]), float(chal['place'][1])
        coords = meters_to_geo(off_x, d_center['dy'] + off_y)
        codename = chal.get('codename', chal.get('code', f"PRIO-0{c_idx+1}"))
        verdict = chal.get('verdict')

        # Dynamic height scaling based on impact_scale (0.4 to 1.0)
        impact = float(chal.get('impact_scale', 0.8))
        chal_total_h = round(85.0 + impact * 105.0, 1)  # 127m to 190m
        base_h = round(chal_total_h * 0.48, 1)
        core_h = round(chal_total_h * 0.78, 1)
        needle_h = chal_total_h

        compiled_challenges.append({
            'id': chal['id'],
            'code': chal.get('code', f"PRIO-0{c_idx+1}"),
            'codename': codename,
            'title': chal['title'],
            'impact_scale': impact,
            'district_ref': chal['district_ref'],
            'type': chal.get('type', 'Strategic Priority'),
            'target': chal.get('target', ''),
            'advanced_by': chal.get('advanced_by', []),
            'blocked_by': chal.get('blocked_by', []),
            'verdict': verdict,
            'coordinates': coords
        })

        # Priority = destination: a target painted on the ground and a gem-shaped pin hovering
        # above it on a thin light beam (pin height = impact_scale). No solid body, so priorities
        # never read as another spire.
        # Stepped octahedron: widths grow to the girdle and shrink again (bottom -> top)
        pin_top = chal_total_h
        pin_steps = [(8.0, 7.0), (8.0, 13.0), (7.0, 19.0), (8.0, 13.0), (7.0, 7.0)]  # (tier height, radius)
        pin_bottom = pin_top - sum(h for h, _ in pin_steps)
        solids = [('beam', 0.0, pin_bottom, 2.2, 8, PRIORITY_BEAM_COLOR)]
        level = pin_bottom
        for step_idx, (tier_h, radius) in enumerate(pin_steps):
            solids.append((f'pin_{step_idx}', level, level + tier_h, radius, 4, VERDICT_COLORS.get(verdict, PRIORITY_COLOR)))
            level += tier_h
        for tier, lo, hi, radius, sides, color in solids:
            building_features.append({
                'type': 'Feature',
                'properties': {
                    'id': f"{chal['id']}-{tier}",
                    'challenge_ref': chal['id'],
                    'entity_type': 'challenge',
                    'name': chal['title'],
                    'codename': codename,
                    'tier': f"challenge_{tier}",
                    'height': round(hi, 1),
                    'base_height': round(lo, 1),
                    'color': color
                },
                'geometry': {'type': 'Polygon', 'coordinates': [
                    create_regular_polygon(coords[0], coords[1], radius, sides=sides, rotation_deg=45 if sides == 4 else 0)]}
            })

        # Ground target: bullseye rings and a centre dot
        for ring_r in PRIORITY_RING_RADII:
            target_features.append({
                'type': 'Feature',
                'properties': {'kind': 'ring', 'challenge_ref': chal['id']},
                'geometry': {'type': 'LineString', 'coordinates': create_regular_polygon(coords[0], coords[1], ring_r, sides=48)}
            })
        target_features.append({
            'type': 'Feature',
            'properties': {'kind': 'dot', 'challenge_ref': chal['id']},
            'geometry': {'type': 'Polygon', 'coordinates': [create_regular_polygon(coords[0], coords[1], 7.0, sides=24)]}
        })

        # Outer ring split into arcs: green per spire that advances the priority, red per
        # constraint that holds it back. Counts come straight from the spec.
        forces = [(ref, 'advance') for ref in chal.get('advanced_by', [])] + \
                 [(ref, 'block') for ref in chal.get('blocked_by', [])]
        if forces:
            span = 360.0 / len(forces)
            for f_idx, (ref, force) in enumerate(forces):
                start = 90.0 + f_idx * span + PRIORITY_ARC_GAP_DEG / 2
                end = start + span - PRIORITY_ARC_GAP_DEG
                steps = max(4, int((end - start) / 6))
                arc = []
                for k in range(steps + 1):
                    ang = math.radians(start + (end - start) * k / steps)
                    arc.append([round(coords[0] + math.cos(ang) * PRIORITY_ARC_RADIUS * DEG_LNG_PER_METER, 7),
                                round(coords[1] + math.sin(ang) * PRIORITY_ARC_RADIUS * DEG_LAT_PER_METER, 7)])
                target_features.append({
                    'type': 'Feature',
                    'properties': {'kind': 'arc', 'force': force, 'ref': ref, 'challenge_ref': chal['id'],
                                   'color': '#00e599' if force == 'advance' else '#ff1744'},
                    'geometry': {'type': 'LineString', 'coordinates': arc}
                })

    # 4. Highways (conduits): operational highways, ferries (thin) and planned roads
    conduit_features = []
    compiled_conduits = []
    spire_lookup = {s['id']: s for s in spec.get('spires', [])}
    district_order = {d['id']: d.get('order', i + 1) for i, d in enumerate(sorted_districts)}
    conduit_curves = {}

    for c_idx, cond in enumerate(spec.get('conduits', [])):
        p_from = spire_locations[cond['from']]
        p_to = spire_locations[cond['to']]
        dx = p_to['lng'] - p_from['lng']
        dy = p_to['lat'] - p_from['lat']
        curve_sign = 1 if c_idx % 2 == 0 else -1

        ctrl1_lnglat = [
            round(p_from['lng'] + dx * 0.33 - dy * 0.28 * curve_sign, 7),
            round(p_from['lat'] + dy * 0.33 + dx * 0.28 * curve_sign, 7)
        ]
        ctrl2_lnglat = [
            round(p_from['lng'] + dx * 0.66 + dy * 0.28 * curve_sign, 7),
            round(p_from['lat'] + dy * 0.66 - dx * 0.28 * curve_sign, 7)
        ]

        conduit_curves[cond['id']] = bezier_curve(
            [p_from['lng'], p_from['lat']],
            ctrl1_lnglat,
            ctrl2_lnglat,
            [p_to['lng'], p_to['lat']],
            steps=28
        )

    # 4a. Edge-scope incident pins are placed first: their position along the arc is
    # semantic (`at`), whereas conduit badges only need to stay out of the way.
    bneck_by_id = {b['id']: b for b in compiled_bottlenecks}
    # Markers keep clear of spires and priority monoliths as well as of each other
    obstacles = [[loc['lng'], loc['lat']] for loc in spire_locations.values()] + \
                [c['coordinates'] for c in compiled_challenges] + \
                [b['coordinates'] for b in compiled_bottlenecks if not b.get('scope')]
    # Plazas are no-go areas for badges and pins: sample their footprint every ~90 m
    for pz in spec.get('plazas', []):
        d = district_centers[pz['district_ref']]
        cs = float(pz.get('cell_size', 80.0))
        cx, cy = (float(v) for v in pz.get('place', [0.0, 0.0]))
        w = cs * len(pz.get('cols', [])) + PLAZA_LABEL_MARGIN_M
        h = cs * len(pz.get('rows', [])) + PLAZA_HEADER_MARGIN_M
        x0, y0 = cx - cs * len(pz.get('cols', [])) / 2 - PLAZA_LABEL_MARGIN_M, d['dy'] + cy - cs * len(pz.get('rows', [])) / 2
        nx, ny = max(1, int(w // 90)), max(1, int(h // 90))
        obstacles += [meters_to_geo(x0 + w * (i + 0.5) / nx, y0 + h * (j + 0.5) / ny) for i in range(nx) for j in range(ny)]
    placed_markers = []
    edge_incidents = {}  # conduit id -> [(bottleneck, curve index)]
    conduit_status = {c['id']: c.get('status', 'operational') for c in spec.get('conduits', [])}
    for bneck in spec.get('bottlenecks', []):
        if bneck.get('scope') != 'edge':
            continue
        for ref in bneck.get('constrains', []):
            curve = conduit_curves[ref]
            preferred = round(float(bneck.get('at', 0.62)) * (len(curve) - 1))
            pt, idx = place_on_curve(curve, placed_markers + obstacles, preferred, min_sep=160.0)
            placed_markers.append(pt)
            edge_incidents.setdefault(ref, []).append((bneck, idx))
            # On a planned road the constraint is the reason it is not built: a barrier, not traffic
            barrier = conduit_status.get(ref) == 'planned'
            bneck_by_id[bneck['id']]['anchors'].append({'kind': 'edge', 'ref': ref, 'coordinates': pt, 'barrier': barrier})

    for c_idx, cond in enumerate(spec.get('conduits', [])):
        curve_coords = conduit_curves[cond['id']]
        midpoint, _ = place_on_curve(curve_coords, placed_markers + obstacles)
        placed_markers.append(midpoint)
        codename = cond.get('codename', cond.get('code', f"HW-0{c_idx+1}"))
        status = cond.get('status', 'operational')
        color = '#00f0ff' if c_idx % 2 == 0 else '#ffb700'
        if status == 'planned':
            color = '#8a93a6'
        from_order = district_order.get(spire_lookup[cond['from']]['district_ref'], 0)
        to_order = district_order.get(spire_lookup[cond['to']]['district_ref'], 0)
        direction = 'north' if to_order > from_order else 'south' if to_order < from_order else 'local'

        conduit_obj = {
            'id': cond['id'],
            'code': cond.get('code', f"HW-0{c_idx+1}"),
            'codename': codename,
            'name': cond['name'],
            'from': cond['from'],
            'from_name': spire_lookup.get(cond['from'], {}).get('title', cond['from']),
            'to': cond['to'],
            'to_name': spire_lookup.get(cond['to'], {}).get('title', cond['to']),
            'type': cond.get('type', 'Data Stream'),
            'bandwidth': cond.get('bandwidth', 'High Bandwidth Pipeline'),
            'description': cond.get('description', ''),
            'color': color,
            'status': status,
            'direction': direction,
            'constrained_by': [b['id'] for b, _ in edge_incidents.get(cond['id'], [])],
            'remedies': [b['id'] for b in spec.get('bottlenecks', []) if cond['id'] in b.get('remedied_by', [])],
            'midpoint': midpoint
        }
        compiled_conduits.append(conduit_obj)

        conduit_features.append({
            'type': 'Feature',
            'properties': conduit_obj,
            'geometry': {'type': 'LineString', 'coordinates': curve_coords}
        })

    # 4b. Constraint primitives (schema v2)
    traffic_features = []  # edge: congestion before the incident, starved or closed after it
    queue_features = []    # node: backlog cubes piled around the constrained spire
    field_features = []    # field: coloured tapes along the borders of affected districts

    for cond_id, incidents in edge_incidents.items():
        if conduit_status.get(cond_id) == 'planned':
            continue  # nothing drives on a road that does not exist yet
        curve = conduit_curves[cond_id]
        last = len(curve) - 1
        for bneck, idx in incidents:
            severity = float(bneck.get('severity', 0.8))
            queue_len = max(3, round(4 + severity * 7))
            q_start = max(0, idx - queue_len)
            # Three graded pieces: amber -> orange -> red as traffic nears the incident
            bounds = [q_start + round((idx - q_start) * k / 3) for k in range(4)]
            for piece, (a, b) in enumerate(zip(bounds, bounds[1:])):
                if b <= a:
                    continue
                traffic_features.append({
                    'type': 'Feature',
                    'properties': {
                        'kind': 'queue', 'conduit_ref': cond_id, 'bottleneck_ref': bneck['id'],
                        'color': ['#ffb000', '#ff6d00', '#ff1744'][piece],
                        'width': round(4.0 + severity * 3.0, 1)
                    },
                    'geometry': {'type': 'LineString', 'coordinates': curve[a:b + 1]}
                })
            after_kind = 'closed' if bneck.get('effect') == 'closure' else 'starved'
            traffic_features.append({
                'type': 'Feature',
                'properties': {'kind': after_kind, 'conduit_ref': cond_id, 'bottleneck_ref': bneck['id'],
                               'color': '#ff1744', 'width': 4.0},
                'geometry': {'type': 'LineString', 'coordinates': curve[idx:last + 1]}
            })

    node_counts = {}
    for bneck in spec.get('bottlenecks', []):
        if bneck.get('scope') != 'node':
            continue
        severity = float(bneck.get('severity', 0.8))
        for ref in bneck.get('constrains', []):
            loc = spire_locations[ref]
            slot = node_counts.get(ref, 0)
            node_counts[ref] = slot + 1
            bneck_by_id[bneck['id']]['anchors'].append(
                {'kind': 'node', 'ref': ref, 'slot': slot, 'coordinates': [loc['lng'], loc['lat']]})
            # Backlog of waiting candidates: an arc of small cubes in front of the spire.
            # Each further bottleneck on the same spire takes the next sector round.
            n_cubes = round(4 + severity * 10)
            sector_start = 200.0 + slot * 150.0
            for k in range(n_cubes):
                ring = k % 2
                ang = math.radians(sector_start + (k // 2) * (110.0 / max(1, n_cubes // 2)))
                r = 82.0 + ring * 22.0
                cx, cy = loc['lng'] + math.cos(ang) * r * DEG_LNG_PER_METER, loc['lat'] + math.sin(ang) * r * DEG_LAT_PER_METER
                h = round(6.0 + ((k * 7) % 5) * 3.0 + severity * 8.0, 1)
                queue_features.append({
                    'type': 'Feature',
                    '_center': [loc['lng'], loc['lat']],  # the backlog scales towards its spire
                    'properties': {
                        'id': f"{bneck['id']}-q{ref}-{k}", 'entity_type': 'queue', 'bottleneck_ref': bneck['id'],
                        'height': h, 'base_height': 0.0,
                        'color': '#ff1744' if k % 3 else '#ff6d00'
                    },
                    'geometry': {'type': 'Polygon', 'coordinates': [create_rectangle(cx, cy, 13.0, 13.0)]}
                })
            if bneck.get('effect') == 'closure':
                collar = create_regular_polygon(loc['lng'], loc['lat'], 70.0, sides=24)
                hole = create_regular_polygon(loc['lng'], loc['lat'], 62.0, sides=24)[::-1]
                queue_features.append({
                    'type': 'Feature',
                    'properties': {'id': f"{bneck['id']}-collar-{ref}", 'entity_type': 'queue',
                                   'bottleneck_ref': bneck['id'], 'height': 26.0, 'base_height': 14.0,
                                   'color': '#ff1744'},
                    'geometry': {'type': 'Polygon', 'coordinates': [collar, hole]}
                })

    # Field constraints: one coloured "hazard tape" per constraint running along the inside of
    # each district border it covers (parallel tapes when several apply), plus a forecast
    # row of clickable icons in the district's north-west corner. Static by design.
    district_fields = {d['id']: [] for d in sorted_districts}
    field_bnecks = [b for b in spec.get('bottlenecks', []) if b.get('scope') == 'field']
    for f_idx, bneck in enumerate(field_bnecks):
        color = FIELD_PALETTE[f_idx % len(FIELD_PALETTE)]
        bneck_by_id[bneck['id']]['color'] = color
        for ref in bneck.get('constrains', []):
            lane = len(district_fields[ref])
            district_fields[ref].append(bneck['id'])
            d = district_centers[ref]
            inset = FIELD_TAPE_INSET_M + lane * FIELD_TAPE_SPACING_M
            field_features.append({
                'type': 'Feature',
                'properties': {'bottleneck_ref': bneck['id'], 'district_ref': ref, 'lane': lane,
                               'effect': bneck.get('effect', 'slowdown'), 'color': color},
                'geometry': {'type': 'LineString', 'coordinates': create_rectangle(
                    d['lng'], d['lat'], DISTRICT_WIDTH - 2 * inset, DISTRICT_HEIGHT - 2 * inset)}
            })
    for dist in compiled_districts:
        dist['fields'] = district_fields.get(dist['id'], [])
        # Forecast row anchor: inside the north-west corner (the south-west one holds the name)
        dist['forecast_anchor'] = meters_to_geo(-DISTRICT_WIDTH / 2 + 30.0,
                                                district_centers[dist['id']]['dy'] + DISTRICT_HEIGHT / 2 - 30.0)
    for bneck in field_bnecks:
        home = bneck['district_ref'] if bneck['district_ref'] in bneck['constrains'] else bneck['constrains'][0]
        ordered = [home] + [r for r in bneck['constrains'] if r != home]
        for ref in ordered:
            dist = next(x for x in compiled_districts if x['id'] == ref)
            bneck_by_id[bneck['id']]['anchors'].append({'kind': 'field', 'ref': ref, 'coordinates': dist['forecast_anchor']})

    for b in compiled_bottlenecks:
        if b['anchors']:
            b['coordinates'] = b['anchors'][0]['coordinates']

    # Risk cascades: "this constraint makes that one more likely" (causes)
    causal_features = []
    for b in compiled_bottlenecks:
        for ref in b['causes']:
            target = bneck_by_id[ref]
            causal_features.append({
                'type': 'Feature',
                'properties': {'from': b['id'], 'to': ref},
                'geometry': {'type': 'LineString', 'coordinates': [b['coordinates'], target['coordinates']]}
            })

    # "You are here": a line across the corridor at the project's current position in time
    now_marker = None
    now_spec = spec.get('city_metadata', {}).get('now_marker')
    if now_spec:
        d = district_centers[now_spec['district_ref']]
        y = d['dy'] - DISTRICT_HEIGHT / 2 + float(now_spec.get('position', 0.5)) * DISTRICT_HEIGHT
        half = DISTRICT_WIDTH / 2 + NOW_LINE_OVERHANG_M
        now_marker = {
            'label': now_spec.get('label', 'NOW'),
            'line': [meters_to_geo(-half, y), meters_to_geo(half, y)],
            'label_point': meters_to_geo(half, y)  # east end: the west side is under the legend panel
        }

    # 4d. Plazas: a data grid painted on the ground (texture drawn by the viewer) with bars per cell
    plaza_meta, plaza_features = [], []
    for pz in spec.get('plazas', []):
        d = district_centers[pz['district_ref']]
        cs = float(pz.get('cell_size', 80.0))
        rows, cols = pz['rows'], pz['cols']
        grid_w, grid_h = cs * len(cols), cs * len(rows)
        cx, cy = (float(v) for v in pz.get('place', [0.0, 0.0]))
        gx0, gy_top = cx - grid_w / 2, d['dy'] + cy + grid_h / 2      # grid west edge, north edge
        frame_w, frame_h = PLAZA_LABEL_MARGIN_M + grid_w + 12.0, PLAZA_HEADER_MARGIN_M + grid_h + 12.0
        fx0, fy_top = gx0 - PLAZA_LABEL_MARGIN_M, gy_top + PLAZA_HEADER_MARGIN_M
        corners = [meters_to_geo(fx0, fy_top), meters_to_geo(fx0 + frame_w, fy_top),
                   meters_to_geo(fx0 + frame_w, fy_top - frame_h), meters_to_geo(fx0, fy_top - frame_h)]
        values = [v for layer in pz.get('layers', []) for row in layer['cells'] for v in row if isinstance(v, (int, float))]
        vmax = max(values) if values else 1
        for layer in pz.get('layers', []):
            for r, row in enumerate(layer['cells']):
                for c, v in enumerate(row):
                    if not isinstance(v, (int, float)) or v <= 0:
                        continue
                    mx, my = gx0 + (c + 0.5) * cs, gy_top - (r + 0.5) * cs
                    ctr = meters_to_geo(mx, my)
                    plaza_features.append({
                        'type': 'Feature',
                        'properties': {'kind': 'bar', 'plaza': pz['id'], 'layer': layer['id'], 'row': r, 'col': c,
                                       'height': round(max(3.0, PLAZA_MAX_BAR_M * v / vmax), 1), 'base_height': 0.0,
                                       'color': pz.get('color', d['color'])},
                        'geometry': {'type': 'Polygon', 'coordinates': [create_rectangle(ctr[0], ctr[1], cs * 0.55, cs * 0.55)]}
                    })
        for h in pz.get('highlight', []):
            mx, my = gx0 + (h['col'] + 0.5) * cs, gy_top - (h['row'] + 0.5) * cs
            ctr = meters_to_geo(mx, my)
            plaza_features.append({
                'type': 'Feature',
                'properties': {'kind': 'highlight', 'plaza': pz['id'], 'style': h.get('kind', 'empty')},
                'geometry': {'type': 'LineString', 'coordinates': create_rectangle(ctr[0], ctr[1], cs - 8.0, cs - 8.0)}
            })
        plaza_features.append({
            'type': 'Feature',
            'properties': {'kind': 'hit', 'plaza': pz['id']},
            'geometry': {'type': 'Polygon', 'coordinates': [corners + [corners[0]]]}
        })
        plaza_meta.append({
            'id': pz['id'], 'district_ref': pz['district_ref'], 'title': pz.get('title', ''),
            'subtitle': pz.get('subtitle', ''), 'description': pz.get('description', ''),
            'row_axis': pz.get('row_axis', ''), 'col_axis': pz.get('col_axis', ''),
            'rows': rows, 'cols': cols, 'layers': pz.get('layers', []), 'highlight': pz.get('highlight', []),
            'color': pz.get('color', d['color']), 'corners': corners,
            'frame': {'width_m': frame_w, 'height_m': frame_h, 'grid_x_m': PLAZA_LABEL_MARGIN_M,
                      'grid_y_m': PLAZA_HEADER_MARGIN_M, 'cell_m': cs},
            'coordinates': meters_to_geo(cx, d['dy'] + cy)
        })

    # 4e. Guided tour: resolve each stop's camera target to coordinates
    def ref_coords(ref):
        if ref in (None, 'city'):
            return [LNG_CENTER, LAT_CENTER]
        if ref in district_centers:
            return [district_centers[ref]['lng'], district_centers[ref]['lat']]
        if ref in spire_locations:
            return [spire_locations[ref]['lng'], spire_locations[ref]['lat']]
        for coll, key in ((compiled_challenges, 'coordinates'), (compiled_bottlenecks, 'coordinates'),
                          (plaza_meta, 'coordinates'), (compiled_conduits, 'midpoint')):
            for item in coll:
                if item['id'] == ref:
                    return item[key]
        return [LNG_CENTER, LAT_CENTER]

    tour = []
    for t_idx, stop in enumerate(spec.get('tour', [])):
        cam = dict(stop.get('camera', {}))
        target = cam.get('target') or (stop.get('focus') or ['city'])[0]
        tour.append({
            'id': stop.get('id', f'stop-{t_idx + 1}'), 'title': stop['title'], 'text': stop['text'],
            'look': stop.get('look', ''), 'focus': stop.get('focus', []),
            'plaza_layers': stop.get('plaza_layers', {}),
            'camera': {'center': ref_coords(target), 'zoom': cam.get('zoom', 15.2),
                       'pitch': cam.get('pitch', 55), 'bearing': cam.get('bearing', -16)}
        })

    # 4c. Routing graph: conduits in both directions (against the flow costs more) plus
    # "walking" links between spires of the same district.
    route_edges = []
    for cond in compiled_conduits:
        penalty = sum(float(bneck_by_id[b]['severity']) for b in cond['constrained_by'])
        base = {'operational': 1.0, 'thin': 1.6, 'planned': 3.0}[cond['status']]
        planned = cond['status'] == 'planned'  # the viewer skips these unless asked to include them
        route_edges.append({'from': cond['from'], 'to': cond['to'], 'kind': 'conduit', 'conduit': cond['id'],
                            'planned': planned, 'cost': round(base + penalty, 2)})
        route_edges.append({'from': cond['to'], 'to': cond['from'], 'kind': 'conduit', 'conduit': cond['id'],
                            'planned': planned, 'against_flow': True, 'cost': round(base + penalty + 2.0, 2)})
    for dist in sorted_districts:
        members = [sid for sid, loc in spire_locations.items() if loc['district_ref'] == dist['id']]
        for a in members:
            for b in members:
                if a != b:
                    route_edges.append({'from': a, 'to': b, 'kind': 'walk', 'cost': 0.6})

    # 5. Spires Metadata Index for HUD & Pager
    spires_index = []
    for spire in spec.get('spires', []):
        loc = spire_locations[spire['id']]
        dist = district_ids[spire['district_ref']]
        spires_index.append({
            'id': spire['id'],
            'code': spire.get('code', 'SP-00'),
            'codename': spire.get('codename', spire.get('code', 'SPIRE')),
            'title': spire['title'],
            'district_ref': spire['district_ref'],
            'district_name': dist['name'],
            'scale_label': dist.get('scale_label', ''),
            'color': dist['color'],
            'coordinates': [loc['lng'], loc['lat']],
            'metrics': spire.get('metrics', {}),
            'abstract': spire.get('abstract', ''),
            'status': spire.get('status', 'done'),
            'kind': spire.get('kind', 'system'),
            'constraints': [b['id'] for b in compiled_bottlenecks
                            if b.get('scope') == 'node' and spire['id'] in b.get('constrains', [])],
            'advances': [c['id'] for c in compiled_challenges if spire['id'] in c.get('advanced_by', [])]
        })

    # Building size: a global vertical scale for every extrusion, times an optional per-city
    # city_metadata.building_scale that shrinks or grows buildings as a whole (height and footprint)
    size = float(spec.get('city_metadata', {}).get('building_scale', 1.0))
    for feat in building_features + queue_features:
        props = feat['properties']
        props['height'] = round(props['height'] * BUILDING_HEIGHT_SCALE * size, 1)
        props['base_height'] = round(props['base_height'] * BUILDING_HEIGHT_SCALE * size, 1)
        center = feat.pop('_center', None)
        if center:
            props['scale_center'] = center  # lets the viewer rescale footprints live (Alt+scroll)
        if size != 1.0:
            feat['geometry']['coordinates'] = [scale_ring(ring, size, center) for ring in feat['geometry']['coordinates']]
    if size != 1.0:
        for feat in wireframe_features:
            feat['geometry']['coordinates'] = scale_ring(feat['geometry']['coordinates'], size)
    buildings_geojson = {'type': 'FeatureCollection', 'features': building_features + queue_features}
    wireframe_geojson = {'type': 'FeatureCollection', 'features': wireframe_features}
    conduits_geojson = {'type': 'FeatureCollection', 'features': conduit_features}

    js_bundle = f"""/**
 * Autogenerated by Metropolis Procedural Spatial Compiler (metropolis-kit)
 * Title: {spec.get('city_metadata', {}).get('title', 'Metropolis')}
 */

window.CITY_CONFIG = {json.dumps({
    'title': spec['city_metadata'].get('title', 'Metropolis'),
    'subtitle': spec['city_metadata'].get('subtitle', ''),
    'theme': spec['city_metadata'].get('theme', 'quantum_crystal'),
    'center': [round(LNG_CENTER, 5), round(LAT_CENTER, 5)],
    'zoom': 15.0,
    'pitch': 60,
    'bearing': -18,
    'scale_axis_label': spec['city_metadata'].get('scale_axis_label', 'Scale Axis'),
    'scale_axis_description': spec['city_metadata'].get('scale_axis_description', ''),
    'hud_tags': spec['city_metadata'].get('hud_tags', []),
    'building_scale': spec['city_metadata'].get('building_scale', 1.0),
    'ui_labels': spec['city_metadata'].get('ui_labels', {})
}, indent=2)};

window.DISTRICTS = {json.dumps(compiled_districts, indent=2)};

window.SPIRES_INDEX = {json.dumps(spires_index, indent=2)};

window.BOTTLENECKS = {json.dumps(compiled_bottlenecks, indent=2)};

window.CHALLENGES = {json.dumps(compiled_challenges, indent=2)};

window.CONDUITS = {json.dumps(compiled_conduits, indent=2)};

window.BUILDINGS_GEOJSON = {json.dumps(buildings_geojson)};

window.WIREFRAME_GEOJSON = {json.dumps(wireframe_geojson)};

window.CONDUITS_GEOJSON = {json.dumps(conduits_geojson)};

window.SCHEMA_VERSION = {json.dumps(spec.get('city_metadata', {}).get('schema_version', '1.0'))};

window.TRAFFIC_GEOJSON = {json.dumps({'type': 'FeatureCollection', 'features': traffic_features})};

window.FIELDS_GEOJSON = {json.dumps({'type': 'FeatureCollection', 'features': field_features})};

window.ROUTE_GRAPH = {json.dumps(route_edges)};

window.TARGETS_GEOJSON = {json.dumps({'type': 'FeatureCollection', 'features': target_features})};

window.CAUSAL_GEOJSON = {json.dumps({'type': 'FeatureCollection', 'features': causal_features})};

window.NOW_MARKER = {json.dumps(now_marker)};

window.PLAZAS = {json.dumps(plaza_meta)};

window.TOUR = {json.dumps(tour)};

window.PLAZAS_GEOJSON = {json.dumps({'type': 'FeatureCollection', 'features': plaza_features})};
"""
    return js_bundle, {
        'districts': len(compiled_districts),
        'building_tiers': len(building_features),
        'conduits': len(conduit_features),
        'bottlenecks': len(compiled_bottlenecks),
        'challenges': len(compiled_challenges),
        'scoped': {scope: sum(1 for b in compiled_bottlenecks if b.get('scope') == scope)
                   for scope in ('edge', 'node', 'field')}
    }

def main():
    parser = argparse.ArgumentParser(description="Metropolis-Kit: Procedural Spatial Compiler")
    parser.add_argument('--spec', required=True, help="Path to input 02-city-spec.json")
    parser.add_argument('--out', help="Path to output city-data.js")
    parser.add_argument('--web-dir', help="Optional web target directory (e.g. docs/ or dist/)")
    parser.add_argument('--validate-only', action='store_true', help="Run schema validation without emitting")
    parser.add_argument('--serve', type=int, nargs='?', const=8080, help="Launch local HTTP server on given port (default 8080)")

    args = parser.parse_args()

    if not os.path.exists(args.spec):
        print(f"[!] Error: Spec file not found at {args.spec}")
        sys.exit(1)

    with open(args.spec, 'r', encoding='utf-8') as f:
        spec = json.load(f)

    errors = validate_spec(spec)
    if errors:
        print("[!] Validation failed with errors:")
        for err in errors:
            print(f"    - {err}")
        sys.exit(1)

    print("[+] Specification validation passed cleanly.")
    for warning in lint_spec(spec):
        print(f"    [warn] {warning}")
    if args.validate_only:
        sys.exit(0)

    js_bundle, stats = compile_metropolis_data(spec)

    out_file = args.out
    if not out_file and args.web_dir:
        out_file = os.path.join(args.web_dir, 'city-data.js')
    elif not out_file:
        out_file = 'city-data.js'

    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(js_bundle)

    print(f"[✓] Compiled {out_file}:")
    print(f"    - {stats['districts']} Districts")
    print(f"    - {stats['building_tiers']} 3D Building Tiers (Spires, Priority Pins, legacy Hazard Towers, Queues)")
    print(f"    - {stats['conduits']} Highways")
    scoped = stats['scoped']
    print(f"    - {stats['bottlenecks']} Bottlenecks (edge {scoped['edge']} · node {scoped['node']} · field {scoped['field']})")
    print(f"    - {stats['challenges']} Strategic Priorities")

    if args.web_dir:
        os.makedirs(args.web_dir, exist_ok=True)
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        src_html = os.path.join(repo_root, 'web', 'index.html')
        dst_html = os.path.join(args.web_dir, 'index.html')
        if os.path.exists(src_html) and os.path.abspath(src_html) != os.path.abspath(dst_html):
            shutil.copyfile(src_html, dst_html)
            print(f"[+] Synced web template to {dst_html}")

    if args.serve:
        serve_dir = args.web_dir if args.web_dir else os.path.dirname(os.path.abspath(out_file))
        print(f"\n[🚀] Starting Metropolis viewer server at http://localhost:{args.serve}/")
        print(f"     Serving directory: {serve_dir}")
        os.chdir(serve_dir)
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", args.serve), handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[+] Server stopped.")

if __name__ == '__main__':
    main()
