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

    return errors

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
            (320.0, 30.0, 8)
        ]

        for s_idx, spire in enumerate(dist_spires):
            offset_x, offset_y, sides = spire_offsets[s_idx % len(spire_offsets)]
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
            # Towering 3D Heights: 120m to 210m tall!
            total_height = round(100.0 + scale_lvl * 110.0, 1)
            base_tier_h = round(total_height * 0.35, 1)
            mid_tier_h = round(total_height * 0.72, 1)
            top_tier_h = total_height
            needle_h = round(total_height + 32.0, 1)

            # Saturated, rich district-themed colors for 3D crystal lighting
            color_lower = adjust_color(dist['color'], sat_mult=1.0, light_mult=0.42)
            color_mid = adjust_color(dist['color'], sat_mult=0.95, light_mult=0.68)
            color_crown = dist['color']

            # Tier 0: Ground Foundation Pedestal (radius 56m, height 0 to 5m)
            poly_base = create_regular_polygon(spire_lnglat[0], spire_lnglat[1], 56.0, sides=sides, rotation_deg=15)
            building_features.append({
                'type': 'Feature',
                'properties': {
                    'id': f"{spire['id']}-pedestal",
                    'spire_ref': spire['id'],
                    'entity_type': 'spire',
                    'name': spire['title'],
                    'tier': 'pedestal',
                    'height': 5.0,
                    'base_height': 0.0,
                    'color': dist['color'],
                    'opacity': 0.85
                },
                'geometry': {'type': 'Polygon', 'coordinates': [poly_base]}
            })

            # Tier 1: Lower Crystal Prism (radius 44m, height 5m to base_tier_h)
            poly_t1 = create_regular_polygon(spire_lnglat[0], spire_lnglat[1], 44.0, sides=sides, rotation_deg=0)
            building_features.append({
                'type': 'Feature',
                'properties': {
                    'id': f"{spire['id']}-tier1",
                    'spire_ref': spire['id'],
                    'entity_type': 'spire',
                    'name': spire['title'],
                    'tier': 'body_lower',
                    'height': base_tier_h,
                    'base_height': 5.0,
                    'color': color_lower,
                    'opacity': 0.95
                },
                'geometry': {'type': 'Polygon', 'coordinates': [poly_t1]}
            })

            # Tier 2: Mid Crystalline Shaft (radius 32m, height base_tier_h to mid_tier_h)
            poly_t2 = create_regular_polygon(spire_lnglat[0], spire_lnglat[1], 32.0, sides=sides, rotation_deg=22.5)
            building_features.append({
                'type': 'Feature',
                'properties': {
                    'id': f"{spire['id']}-tier2",
                    'spire_ref': spire['id'],
                    'entity_type': 'spire',
                    'name': spire['title'],
                    'tier': 'body_mid',
                    'height': mid_tier_h,
                    'base_height': base_tier_h,
                    'color': color_mid,
                    'opacity': 0.95
                },
                'geometry': {'type': 'Polygon', 'coordinates': [poly_t2]}
            })

            # Tier 3: Upper Facet Crown (radius 20m, height mid_tier_h to top_tier_h)
            poly_t3 = create_regular_polygon(spire_lnglat[0], spire_lnglat[1], 20.0, sides=sides, rotation_deg=45)
            building_features.append({
                'type': 'Feature',
                'properties': {
                    'id': f"{spire['id']}-tier3",
                    'spire_ref': spire['id'],
                    'entity_type': 'spire',
                    'name': spire['title'],
                    'tier': 'crown',
                    'height': top_tier_h,
                    'base_height': mid_tier_h,
                    'color': color_crown,
                    'opacity': 1.0
                },
                'geometry': {'type': 'Polygon', 'coordinates': [poly_t3]}
            })

            # Tier 4: Needle Antenna (radius 5m, height top_tier_h to needle_h)
            poly_needle = create_regular_polygon(spire_lnglat[0], spire_lnglat[1], 5.0, sides=4, rotation_deg=45)
            building_features.append({
                'type': 'Feature',
                'properties': {
                    'id': f"{spire['id']}-needle",
                    'spire_ref': spire['id'],
                    'entity_type': 'spire',
                    'name': spire['title'],
                    'tier': 'needle',
                    'height': needle_h,
                    'base_height': top_tier_h,
                    'color': '#ffffff',
                    'opacity': 1.0
                },
                'geometry': {'type': 'Polygon', 'coordinates': [poly_needle]}
            })

            # Wireframe outline feature for crisp polygonal facet edges
            wireframe_features.append({
                'type': 'Feature',
                'properties': {'color': dist['color']},
                'geometry': {'type': 'LineString', 'coordinates': poly_t1}
            })
            wireframe_features.append({
                'type': 'Feature',
                'properties': {'color': dist['color']},
                'geometry': {'type': 'LineString', 'coordinates': poly_t2}
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
            'coordinates': coords
        })

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
    chal_offsets = [(470.0, -180.0), (-470.0, 190.0), (480.0, 150.0), (-480.0, -170.0), (0.0, -250.0)]
    for c_idx, chal in enumerate(spec.get('challenges', [])):
        d_center = district_centers[chal['district_ref']]
        off_x, off_y = chal_offsets[c_idx % len(chal_offsets)]
        coords = meters_to_geo(off_x, d_center['dy'] + off_y)
        codename = chal.get('codename', chal.get('code', f"PRIO-0{c_idx+1}"))

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
            'coordinates': coords
        })

        # Generate 3D Golden Priority Monolith (Amber Diamond)
        poly_chal_base = create_regular_polygon(coords[0], coords[1], 38.0, sides=4, rotation_deg=45)
        building_features.append({
            'type': 'Feature',
            'properties': {
                'id': f"{chal['id']}-base",
                'challenge_ref': chal['id'],
                'entity_type': 'challenge',
                'name': chal['title'],
                'codename': codename,
                'tier': 'challenge_base',
                'height': base_h,
                'base_height': 0.0,
                'color': '#b38600',
                'opacity': 0.95
            },
            'geometry': {'type': 'Polygon', 'coordinates': [poly_chal_base]}
        })

        poly_chal_core = create_regular_polygon(coords[0], coords[1], 24.0, sides=4, rotation_deg=0)
        building_features.append({
            'type': 'Feature',
            'properties': {
                'id': f"{chal['id']}-core",
                'challenge_ref': chal['id'],
                'entity_type': 'challenge',
                'name': chal['title'],
                'codename': codename,
                'tier': 'challenge_core',
                'height': core_h,
                'base_height': base_h,
                'color': '#ffb700',
                'opacity': 0.98
            },
            'geometry': {'type': 'Polygon', 'coordinates': [poly_chal_core]}
        })

        poly_chal_needle = create_regular_polygon(coords[0], coords[1], 4.5, sides=4, rotation_deg=45)
        building_features.append({
            'type': 'Feature',
            'properties': {
                'id': f"{chal['id']}-needle",
                'challenge_ref': chal['id'],
                'entity_type': 'challenge',
                'name': chal['title'],
                'codename': codename,
                'tier': 'challenge_needle',
                'height': needle_h,
                'base_height': core_h,
                'color': '#ffe082',
                'opacity': 1.0
            },
            'geometry': {'type': 'Polygon', 'coordinates': [poly_chal_needle]}
        })

    # 4. Superhighways & Conduits with Midpoint Calculation
    conduit_features = []
    compiled_conduits = []
    spire_lookup = {s['id']: s for s in spec.get('spires', [])}

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

        curve_coords = bezier_curve(
            [p_from['lng'], p_from['lat']],
            ctrl1_lnglat,
            ctrl2_lnglat,
            [p_to['lng'], p_to['lat']],
            steps=28
        )

        midpoint = curve_coords[len(curve_coords) // 2]
        codename = cond.get('codename', cond.get('code', f"HW-0{c_idx+1}"))
        color = '#00f0ff' if c_idx % 2 == 0 else '#ffb700'

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
            'midpoint': midpoint
        }
        compiled_conduits.append(conduit_obj)

        conduit_features.append({
            'type': 'Feature',
            'properties': conduit_obj,
            'geometry': {'type': 'LineString', 'coordinates': curve_coords}
        })

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
            'abstract': spire.get('abstract', '')
        })

    buildings_geojson = {'type': 'FeatureCollection', 'features': building_features}
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
    'scale_axis_description': spec['city_metadata'].get('scale_axis_description', '')
}, indent=2)};

window.DISTRICTS = {json.dumps(compiled_districts, indent=2)};

window.SPIRES_INDEX = {json.dumps(spires_index, indent=2)};

window.BOTTLENECKS = {json.dumps(compiled_bottlenecks, indent=2)};

window.CHALLENGES = {json.dumps(compiled_challenges, indent=2)};

window.CONDUITS = {json.dumps(compiled_conduits, indent=2)};

window.BUILDINGS_GEOJSON = {json.dumps(buildings_geojson)};

window.WIREFRAME_GEOJSON = {json.dumps(wireframe_geojson)};

window.CONDUITS_GEOJSON = {json.dumps(conduits_geojson)};
"""
    return js_bundle, {
        'districts': len(compiled_districts),
        'building_tiers': len(building_features),
        'conduits': len(conduit_features),
        'bottlenecks': len(compiled_bottlenecks),
        'challenges': len(compiled_challenges)
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
    print(f"    - {stats['building_tiers']} 3D Building Tiers (Spires + Hazard Radars + Priority Monoliths)")
    print(f"    - {stats['conduits']} Superhighways")
    print(f"    - {stats['bottlenecks']} Bottlenecks")
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
