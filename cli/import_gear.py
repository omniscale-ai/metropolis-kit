#!/usr/bin/env python3
"""Import a gear (gears-rust layout, Cypilot traceability) as a city spec: spec ↔ code.

Reads, deterministically, without an LLM:
  docs/PRD.md                 functional requirements (fr) and non-functional ones (nfr), with their [x] status
  docs/DESIGN*.md             components
  docs/DECOMPOSITION.md       features: which requirements and components each covers, and what it depends on
  docs/features/*.md          each feature's flows, algorithms, states and definitions of done (the spec items)
  <crate>/src, <crate>-sdk    Rust sources: lines, tests, and the @cpt-* markers that tie code to spec items

and writes a 02-city-spec.json with four districts — requirements, design, features, code — roads for every
traceability link, a coverage plaza, honest constraints for the gaps (spec items with no marker in the code,
code with no marker at all), NFRs as goals, and a generated tour.

    python3 -m cli.import_gear ~/git/gears-rust/gears/settings-service --out examples/settings-service/02-city-spec.json
"""
import argparse
import glob
import json
import math
import os
import re
from collections import Counter, defaultdict

ID_LINE = re.compile(r'^\s*-\s*\[( |x)\]\s*`(p\d)`\s*-\s*\*\*ID\*\*:\s*`(cpt-[a-z0-9-]+)`')
REF_LINE = re.compile(r'^\s*-\s*\[( |x)\]\s*`(p\d)`\s*-\s*`(cpt-[a-z0-9-]+)`')
HEADING = re.compile(r'^(#{2,4})\s+(.*)$')
MARK = re.compile(r'@cpt-(begin|end|dod|flow|algo|state)?:?(cpt-[a-z0-9-]+)')
IMPL_KINDS = ('flow', 'algo', 'dod', 'state')

DISTRICT_W, DISTRICT_H = 1100.0, 680.0
MIN_MARKS = 3   # a feature → module road needs at least this many markers (fewer stay in the cards)
METRO_MODULES = 3   # a feature's metro line ends in the modules most specific to it
LINE_COLORS = ['#00f0ff', '#ffb020', '#b44dff', '#00e599', '#ff5c7a', '#4d8dff', '#ffe14d', '#ff8a3d',
               '#7cffb2', '#ff7ad9', '#a0b4ff', '#c8ff4d']


def clean(md):
    """Markdown → plain text for cards."""
    md = re.sub(r'`([^`]*)`', r'\1', md)
    md = re.sub(r'\*\*([^*]*)\*\*', r'\1', md)
    md = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', md)
    md = re.sub(r'&mdash;', '—', md)
    return re.sub(r'\s+', ' ', md).strip()


def shorten(text, n=320):
    text = clean(text)
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(' ', 1)[0]
    return cut.rstrip(',;:') + '…'


def parse_ids(path):
    """Every '- [x] `p1` - **ID**: `cpt-…`' in a markdown file, with its heading and the paragraph after it."""
    lines = open(path, encoding='utf-8').read().split('\n')
    out, heading, section = [], '', ''
    for i, line in enumerate(lines):
        h = HEADING.match(line)
        if h:
            if len(h.group(1)) <= 3:
                section = clean(h.group(2))
            heading = clean(h.group(2))
            continue
        m = ID_LINE.match(line)
        if not m:
            continue
        body = []
        for nxt in lines[i + 1:]:
            if HEADING.match(nxt) or ID_LINE.match(nxt):
                break
            if nxt.strip().startswith('<!--') or nxt.strip().startswith('**ID**'):
                continue
            if nxt.strip():
                body.append(nxt.strip())
            elif body:
                break
        out.append({'id': m.group(3), 'done': m.group(1) == 'x', 'prio': m.group(2),
                    'title': heading, 'section': section, 'text': ' '.join(body)})
    return out


def kind_of(cid, prefix):
    return cid[len(prefix):].split('-')[0]


def parse_decomposition(path, prefix):
    """Feature entries: id, title, purpose, depends on, and the refs listed under each '- **X Covered**:' block."""
    text = open(path, encoding='utf-8').read()
    feats = []
    for block in re.split(r'\n### ', text)[1:]:
        m = re.search(r'\*\*ID\*\*:\s*`(cpt-[a-z0-9-]+-feature-[a-z0-9-]+)`', block)
        if not m:
            continue
        title = clean(block.split('\n', 1)[0])
        title = re.sub(r'^\d+(\.\d+)*\s*', '', title)
        prio_word = ''
        if ' — ' in title:
            title, prio_word = title.rsplit(' — ', 1)
        purpose = re.search(r'\*\*Purpose\*\*:\s*(.*)', block)
        deps = re.search(r'\*\*Depends On\*\*:\s*(.*)', block)
        covered = defaultdict(list)
        current = None
        for line in block.split('\n'):
            hm = re.match(r'^-\s*\*\*([^*]+)\*\*:\s*$', line.strip())
            if hm:
                current = hm.group(1)
                continue
            rm = REF_LINE.match(line)
            if rm and current:
                covered[current].append((rm.group(3), rm.group(1) == 'x'))
            elif line.strip().startswith('- **'):
                current = None
        feats.append({'id': m.group(1), 'title': title.strip(), 'priority': prio_word.strip(),
                      'purpose': purpose.group(1) if purpose else '',
                      'depends': re.findall(r'`(cpt-[a-z0-9-]+-feature-[a-z0-9-]+)`', deps.group(1)) if deps else [],
                      'covered': covered})
    return feats


def grid(n, x0, x1, y0, y1):
    """n positions in a grid inside the box (metres from the district centre)."""
    if n == 0:
        return []
    w, h = x1 - x0, y1 - y0
    cols = max(1, round(math.sqrt(n * w / h)))
    rows = math.ceil(n / cols)
    cols = math.ceil(n / rows)
    out = []
    for i in range(n):
        r, c = divmod(i, cols)
        in_row = min(cols, n - r * cols)
        dx = w / cols
        x = x0 + dx * (c + 0.5) + (cols - in_row) * dx / 2
        y = y1 - (h / rows) * (r + 0.5)
        out.append([round(x), round(y)])
    return out


def height(value, top):
    """Spire scale_level from a count: sqrt, so a few giants do not flatten the rest."""
    return round(-0.55 + 1.5 * math.sqrt(value / top), 3) if top else 0.0


def main():
    ap = argparse.ArgumentParser(description='Import a gear (spec ↔ code) as a metropolis city spec')
    ap.add_argument('gear', help='Gear directory, e.g. ~/git/gears-rust/gears/settings-service')
    ap.add_argument('--out', required=True)
    ap.add_argument('--repo-url', default='https://github.com/constructorfabric/gears-rust/blob/main')
    args = ap.parse_args()

    gear = os.path.abspath(os.path.expanduser(args.gear))
    slug = os.path.basename(gear)
    prefix = f'cpt-cf-{slug}-'
    short = lambda cid: cid[len(prefix):] if cid.startswith(prefix) else cid
    repo_root = gear
    while repo_root != '/' and not os.path.exists(os.path.join(repo_root, '.git')):
        repo_root = os.path.dirname(repo_root)
    gear_rel = os.path.relpath(gear, repo_root)

    gdl = open(os.path.join(gear, slug, 'gear.gdl'), encoding='utf-8').read() if os.path.exists(os.path.join(gear, slug, 'gear.gdl')) else ''
    gname = (re.search(r'^\s*name\s*=\s*"([^"]+)"', gdl, re.M) or [None, slug.replace('-', ' ').title()])[1]
    gdesc = (re.search(r'^\s*description\s*=\s*"([^"]+)"', gdl, re.M) or [None, ''])[1]

    # ---- spec side
    defs = {}
    doc_of = {}
    for f in sorted(glob.glob(os.path.join(gear, 'docs', '**', '*.md'), recursive=True)):
        for item in parse_ids(f):
            item['doc'] = os.path.relpath(f, gear)
            defs[item['id']] = item
            doc_of[item['id']] = item['doc']
    frs = [d for d in defs.values() if kind_of(d['id'], prefix) == 'fr']
    nfrs = [d for d in defs.values() if kind_of(d['id'], prefix) == 'nfr']
    comps = [d for d in defs.values() if kind_of(d['id'], prefix) == 'component']
    feats = parse_decomposition(os.path.join(gear, 'docs', 'DECOMPOSITION.md'), prefix)

    # spec items (flows, algos, states, DoDs) belong to the feature whose FEATURE doc defines them
    feat_slug = {f['id']: f['id'].split('-feature-', 1)[1] for f in feats}
    items_of = defaultdict(list)
    for d in defs.values():
        if kind_of(d['id'], prefix) in IMPL_KINDS and d['doc'].startswith('docs/features/'):
            fslug = os.path.basename(d['doc'])[:-3]
            fid = next((f for f, s in feat_slug.items() if s == fslug), None)
            if fid:
                items_of[fid].append(d)
    feat_status = {}
    for f in feats:
        st = defs.get(prefix + 'featstatus-' + feat_slug[f['id']])
        feat_status[f['id']] = st['done'] if st else False

    # ---- code side
    crate_dirs = [d for d in (os.path.join(gear, slug), os.path.join(gear, slug + '-sdk')) if os.path.isdir(d)]
    groups = defaultdict(lambda: {'files': 0, 'loc': 0, 'tests': 0, 'marks': Counter(), 'paths': []})
    for crate in crate_dirs:
        for f in sorted(glob.glob(os.path.join(crate, '**', '*.rs'), recursive=True)):
            if '/target/' in f:
                continue
            rel = os.path.relpath(f, gear)
            parts = rel.split('/')
            key = '/'.join(parts[:-1])
            if key.endswith('/tests/common'):
                key = key[:-len('/common')]
            text = open(f, encoding='utf-8', errors='replace').read()
            g = groups[key]
            g['files'] += 1
            g['loc'] += text.count('\n')
            g['tests'] += len(re.findall(r'#\[(?:tokio::)?test\b', text))
            g['paths'].append(rel)
            for m in MARK.finditer(text):
                if m.group(1) != 'end' and m.group(2).startswith(prefix):
                    g['marks'][m.group(2)] += 1
    marked = set(i for g in groups.values() for i in g['marks'])

    # ---- districts
    districts = [
        {'id': '@dist-req', 'name': '1 · REQUIREMENTS', 'scale_label': 'What it must do',
         'description': f'Functional requirements from the PRD ({len(frs)}); non-functional ones ({len(nfrs)}) stand as goals.',
         'color': '#00f0ff'},
        {'id': '@dist-design', 'name': '2 · DESIGN', 'scale_label': 'How it is shaped',
         'description': f'Components from the technical design ({len(comps)}).', 'color': '#00e599'},
        {'id': '@dist-feat', 'name': '3 · FEATURES', 'scale_label': 'What gets built, and in what order',
         'description': f'The decomposition into {len(feats)} features: each covers requirements and components and is specified as flows, algorithms and definitions of done.',
         'color': '#ffb020'},
        {'id': '@dist-code', 'name': '4 · CODE', 'scale_label': 'Where it lives',
         'description': f'{sum(g["files"] for g in groups.values())} Rust files in {len(groups)} modules; @cpt markers tie code blocks to the spec items they implement.',
         'color': '#b44dff'},
    ]
    for i, d in enumerate(districts, 1):
        d.update({'order': i, 'glow': d['color'] + '66', 'eu_infrastructures': []})

    spires, conduits, bnecks, chals = [], [], [], []
    sid = lambda cid: '@spire-' + short(cid)
    feat_cov_fr = defaultdict(list)     # fr -> [(feature, done)]
    feat_cov_comp = defaultdict(list)
    feat_cov_nfr = defaultdict(list)
    for f in feats:
        for block, refs in f['covered'].items():
            for ref, done in refs:
                k = kind_of(ref, prefix)
                if k == 'fr':
                    feat_cov_fr[ref].append((f['id'], done))
                elif k == 'nfr':
                    feat_cov_nfr[ref].append((f['id'], done))
                elif k == 'component':
                    feat_cov_comp[ref].append((f['id'], done))

    # 1 · requirements
    prio_h = {'p1': 0.35, 'p2': 0.05, 'p3': -0.25}
    for n_fr, (fr, pos) in enumerate(zip(frs, grid(len(frs), -500, 500, -290, 290)), 1):
        covered = feat_cov_fr.get(fr['id'], [])
        status = 'done' if fr['done'] else ('active' if covered else 'planned')
        state = {'done': 'Done', 'active': 'In a planned feature, not yet done', 'planned': 'No feature yet (later release)'}[status]
        spires.append({
            'id': sid(fr['id']), 'district_ref': '@dist-req', 'kind': 'knowledge', 'status': status,
            'title': fr['title'], 'code': f'FR-{n_fr:02d}', 'codename': short(fr['id'])[3:].replace('-', ' ').upper()[:28],
            'scale_level': prio_h.get(fr['prio'], 0.0), 'place': pos,
            'metrics': {'scale': fr['prio'], 'acceleration': fr['section'], 'infrastructure': 'PRD.md',
                        'maturity': state},
            'abstract': shorten(fr['text']) or fr['title'],
            'links': [{'label': 'Open in the PRD', 'url': f"{args.repo_url}/{gear_rel}/{fr['doc']}"}],
        })
    # NFRs as goals
    for n in nfrs:
        adv = [sid(f) for f, _ in feat_cov_nfr.get(n['id'], [])]
        chals.append({'id': '@chal-' + short(n['id'])[4:], 'title': n['title'], 'code': 'NFR', 'codename': short(n['id'])[4:].replace('-', ' ').upper()[:22],
                      'district_ref': '@dist-req', 'impact_scale': 0.6, 'type': 'Non-functional requirement',
                      'target': shorten(n['text'], 260) or n['title'], 'advanced_by': adv, 'blocked_by': [],
                      'short': ''})

    # 2 · design components
    for n_c, (comp, pos) in enumerate(zip(comps, grid(len(comps), -500, 500, -290, 290)), 1):
        covered = feat_cov_comp.get(comp['id'], [])
        status = 'done' if comp['done'] else ('active' if covered else 'planned')
        spires.append({
            'id': sid(comp['id']), 'district_ref': '@dist-design', 'kind': 'knowledge', 'status': status,
            'title': comp['title'], 'code': f'C-{n_c:02d}', 'codename': short(comp['id'])[10:].replace('-', ' ').upper()[:28],
            'scale_level': 0.1, 'place': pos,
            'metrics': {'scale': comp['prio'], 'acceleration': comp['section'], 'infrastructure': comp['doc'].replace('docs/', ''),
                        'maturity': {'done': 'Done', 'active': 'Covered by a feature', 'planned': 'No feature yet'}[status]},
            'abstract': shorten(comp['text']) or comp['title'],
            'links': [{'label': 'Open in the design', 'url': f"{args.repo_url}/{gear_rel}/{comp['doc']}"}],
        })

    # 3 · features (left two thirds; the coverage plaza on the right)
    top_items = max((len(items_of[f['id']]) for f in feats), default=1)
    untraced_of = {}
    for n_f, (f, pos) in enumerate(zip(feats, grid(len(feats), -510, 60, -290, 290)), 1):
        items = items_of[f['id']]
        traced = [d for d in items if d['id'] in marked]
        untraced_of[f['id']] = [d for d in items if d['id'] not in marked]
        done_items = sum(d['done'] for d in items)
        status = 'done' if feat_status[f['id']] else ('active' if done_items else 'planned')
        kinds = Counter(kind_of(d['id'], prefix) for d in items)
        spires.append({
            'id': sid(f['id']), 'district_ref': '@dist-feat', 'kind': 'hub', 'status': status,
            'title': f['title'], 'code': f'F-{n_f:02d}', 'codename': short(f['id'])[8:].replace('-', ' ').upper()[:28],
            'scale_level': height(len(items), top_items), 'place': pos,
            'metrics': {'scale': f"{kinds['flow']} flows · {kinds['algo']} algorithms · {kinds['dod']} DoDs",
                        'acceleration': f"{len(traced)} of {len(items)} spec items marked in code",
                        'infrastructure': f"docs/features/{feat_slug[f['id']]}.md",
                        'maturity': ('Done' if status == 'done' else f"{done_items} of {len(items)} items checked") + (f" · {f['priority']}" if f['priority'] else '')},
            'abstract': shorten(f['purpose']) or f['title'],
            'links': [{'label': 'Open the feature spec', 'url': f"{args.repo_url}/{gear_rel}/docs/features/{feat_slug[f['id']]}.md"}],
        })

    # 4 · code modules
    code_keys = sorted(groups, key=lambda k: (k.startswith(slug + '-sdk'), '/tests' in k, k))
    top_loc = max(g['loc'] for g in groups.values())
    code_sid = {k: '@spire-code-' + re.sub(r'[^a-z0-9]+', '-', k.replace(slug + '/src', 'src').replace(slug + '-sdk/src', 'sdk').replace(slug + '/tests', 'tests').lower()).strip('-') for k in code_keys}
    for n_m, (k, pos) in enumerate(zip(code_keys, grid(len(code_keys), -510, 510, -290, 290)), 1):
        g = groups[k]
        label = k.replace(slug + '/src', 'src').replace(slug + '-sdk/src', 'sdk').replace(slug + '/tests', 'tests')
        feats_here = Counter()
        for cid, n in g['marks'].items():
            for f in feats:
                if cid in {d['id'] for d in items_of[f['id']]}:
                    feats_here[f['title']] += n
        is_test = label.startswith('tests')
        spires.append({
            'id': code_sid[k], 'district_ref': '@dist-code', 'kind': 'instrument' if is_test else 'system',
            'title': label + ('/' if not label.endswith('.rs') else ''), 'code': f'M-{n_m:02d}', 'codename': label.split('/')[-1].upper()[:28],
            'scale_level': height(g['loc'], top_loc), 'place': pos,
            'metrics': {'scale': f"{g['loc']:,} lines · {g['files']} files",
                        'acceleration': f"{sum(g['marks'].values())} @cpt markers · {len(g['marks'])} spec items",
                        'infrastructure': f"{g['tests']} tests",
                        'maturity': ', '.join(t for t, _ in feats_here.most_common(3)) or 'No spec markers'},
            'abstract': (f"Implements parts of: {', '.join(t for t, _ in feats_here.most_common())}." if feats_here
                         else ('Integration tests; they exercise the code but carry no spec markers.' if is_test
                               else 'Code with no @cpt marker: nothing ties it to a spec item.')),
            'links': [{'label': 'Open on GitHub', 'url': f"{args.repo_url.replace('/blob/', '/tree/')}/{gear_rel}/{k}"}],
        })

    # ---- roads
    def road(cid, frm, to, name, code, status='operational', typ='Traceability', desc=''):
        conduits.append({'id': '@conduit-' + cid, 'name': name, 'code': code, 'codename': code, 'from': frm, 'to': to,
                         'status': status, 'type': typ, 'bandwidth': '', 'description': desc or name})

    for fr in frs:
        for f, done in feat_cov_fr.get(fr['id'], []):
            road(f"{short(fr['id'])}--{short(f)}", sid(fr['id']), sid(f), f"{fr['title']} → {short(f)[8:]}", 'COVERS',
                 'operational' if done else 'thin', desc='The feature covers this requirement' + ('' if done else ' (not yet checked off)'))
    for comp in comps:
        for f, done in feat_cov_comp.get(comp['id'], []):
            road(f"{short(comp['id'])}--{short(f)}", sid(comp['id']), sid(f), f"{comp['title']} → {short(f)[8:]}", 'BUILDS',
                 'operational' if done else 'thin', desc='The feature builds this component' + ('' if done else ' (not yet checked off)'))
    feat_ids = {f['id'] for f in feats}
    for f in feats:
        for dep in f['depends']:
            if dep in feat_ids:
                road(f"{short(dep)}--{short(f['id'])}", sid(dep), sid(f['id']), f"{short(f['id'])[8:]} depends on {short(dep)[8:]}",
                     'NEEDS', typ='Dependency', desc='Feature order: this feature builds on the other')
    links_fc = []
    for f in feats:
        ids = {d['id'] for d in items_of[f['id']]}
        for k in code_keys:
            n = sum(c for cid, c in groups[k]['marks'].items() if cid in ids)
            if n:
                links_fc.append((n, f, k))
    for n, f, k in [x for x in links_fc if x[0] >= MIN_MARKS]:
        road(f"{short(f['id'])}--{code_sid[k][7:]}", sid(f['id']), code_sid[k], f"{f['title']} → {k}", f'{n} MARKS',
             'operational' if n >= 5 else 'thin', typ='Implementation',
             desc=f'{n} @cpt markers in this module point at spec items of the feature')

    # ---- metro: one line per feature — the requirements it covers, the components it builds,
    # the feature itself, then the modules that carry most of its markers. A station shared by
    # several features becomes an interchange.
    routes = []
    for n_f, f in enumerate(feats):
        frs_f = [sid(r) for b, refs in f['covered'].items() for r, _ in refs if kind_of(r, prefix) == 'fr']
        comps_f = [sid(r) for b, refs in f['covered'].items() for r, _ in refs if kind_of(r, prefix) == 'component']
        # the modules most specific to this feature: its share of the module's markers, not raw size
        # (a module every feature touches, like the REST layer, says little about any one of them)
        total = {k: sum(groups[k]['marks'].values()) for k in code_keys}
        mods = sorted(((n / total[k], k) for n, ff, k in links_fc if ff is f and n >= MIN_MARKS), key=lambda x: -x[0])[:METRO_MODULES]
        items = items_of[f['id']]
        routes.append({'id': 'line-' + short(f['id'])[8:], 'name': f"F-{n_f + 1:02d} · {f['title']}",
                       'sub': f"{len(items)} spec items · {sum(1 for d in items if d['id'] in marked)} marked in code",
                       'color': LINE_COLORS[n_f % len(LINE_COLORS)],
                       'stations': list(dict.fromkeys(frs_f + comps_f + [sid(f['id'])] + [code_sid[k] for _, k in mods]))})

    # ---- gaps
    for f in feats:
        gap = untraced_of[f['id']]
        if gap:
            names = '; '.join(d['title'] for d in gap)
            bnecks.append({'id': '@bneck-untraced-' + short(f['id'])[8:], 'title': f'{len(gap)} spec item(s) with no code marker',
                           'code': 'UNTRACED SPEC', 'codename': 'UNTRACED SPEC', 'district_ref': '@dist-feat',
                           'severity': min(0.9, 0.3 + 0.15 * len(gap)), 'scope': 'node', 'constrains': [sid(f['id'])],
                           'effect': 'slowdown', 'nature': 'Traceability gap',
                           'impact': f'No @cpt marker in the code points at: {names}. Either the code exists unmarked, or the item is not built.',
                           'remedy': 'Mark the implementing code with @cpt-begin/@cpt-end (or @cpt-dod), or record why the item is deferred.'})
    for k in code_keys:
        g = groups[k]
        if not g['marks'] and '/tests' not in k:
            bnecks.append({'id': '@bneck-unmarked-' + code_sid[k][12:], 'title': 'Code with no spec marker',
                           'code': 'UNMARKED CODE', 'codename': 'UNMARKED CODE', 'district_ref': '@dist-code',
                           'severity': 0.4, 'scope': 'node', 'constrains': [code_sid[k]], 'effect': 'slowdown',
                           'nature': 'Traceability gap',
                           'impact': f"{g['loc']:,} lines in {g['files']} files carry no @cpt marker, so the map cannot say which requirement they serve.",
                           'remedy': 'Mark the code with the spec items it implements, or document it as infrastructure.'})

    # ---- coverage plaza
    cols = ['reqs', 'flows', 'algos', 'DoDs', 'marked', 'missing']
    rows, cells = [], []
    for f in feats:
        items = items_of[f['id']]
        kinds = Counter(kind_of(d['id'], prefix) for d in items)
        rows.append(f['title'][:26])
        cells.append([sum(1 for b, refs in f['covered'].items() for r, _ in refs if kind_of(r, prefix) in ('fr', 'nfr')),
                      kinds['flow'], kinds['algo'], kinds['dod'],
                      sum(1 for d in items if d['id'] in marked), len(untraced_of[f['id']])])
    plaza = {'id': '@plaza-coverage', 'district_ref': '@dist-feat', 'title': 'Spec ↔ code coverage', 'place': [300, -10],
             'cell_size': 40, 'row_axis': 'feature', 'col_axis': 'spec items and their markers in code',
             'rows': rows, 'cols': cols,
             'layers': [{'id': 'coverage', 'label': 'Per feature: requirements covered, spec items, and how many carry a @cpt marker in code', 'cells': cells}],
             'highlight': [{'row': r, 'col': 5, 'kind': 'forbidden', 'label': 'gap'} for r, row in enumerate(cells) if row[5]],
             'description': 'Counted from the FEATURE documents and the @cpt markers in the Rust sources.'}

    # ---- tour
    n_done = sum(f['done'] for f in frs)
    n_cov = sum(1 for f in frs if feat_cov_fr.get(f['id']))
    impl_total = sum(len(v) for v in items_of.values())
    impl_marked = sum(1 for v in items_of.values() for d in v if d['id'] in marked)
    loc_total = sum(g['loc'] for g in groups.values())
    files_total = sum(g['files'] for g in groups.values())
    gaps = [b['id'] for b in bnecks]
    tour = [
        {'id': 'req', 'title': 'What it must do',
         'text': f'{len(frs)} functional requirements in the PRD: {n_done} checked off, {n_cov - n_done} covered by a planned feature, {len(frs) - n_cov} left for a later release (drawn as ghosts). Non-functional requirements stand as goals.',
         'look': 'Solid buildings are done; ghosts have no feature yet', 'focus': [s['id'] for s in spires if s['district_ref'] == '@dist-req'],
         'camera': {'target': '@dist-req', 'zoom': 15.2, 'pitch': 55, 'bearing': -16}},
        {'id': 'design', 'title': 'How it is shaped',
         'text': f'{len(comps)} design components. Each road up to the features says which feature builds it.',
         'look': 'Components and the roads to the features that build them', 'focus': [s['id'] for s in spires if s['district_ref'] == '@dist-design'],
         'camera': {'target': '@dist-design', 'zoom': 15.2, 'pitch': 55, 'bearing': -16}},
        {'id': 'feat', 'title': 'Features: the contract between spec and code',
         'text': f'The decomposition splits the work into {len(feats)} features. Each is specified as flows, algorithms and definitions of done — {impl_total} spec items in all — and the plaza counts how many of them the code marks.',
         'look': 'Feature towers (height = spec items) and the coverage plaza', 'focus': [s['id'] for s in spires if s['district_ref'] == '@dist-feat'] + ['@plaza-coverage'],
         'camera': {'target': '@dist-feat', 'zoom': 15.2, 'pitch': 55, 'bearing': -16}},
        {'id': 'code', 'title': 'Where it lives',
         'text': f'{loc_total:,} lines in {files_total} files. {impl_marked} of {impl_total} spec items carry a @cpt marker in the code, so every road from a feature to a module is exact, not guessed.',
         'look': 'Module height = lines of code; roads = @cpt markers', 'focus': [s['id'] for s in spires if s['district_ref'] == '@dist-code'],
         'camera': {'target': '@dist-code', 'zoom': 15.2, 'pitch': 55, 'bearing': -16}},
        {'id': 'gaps', 'title': 'Where the trace breaks',
         'text': f'{impl_total - impl_marked} spec items have no marker in the code, and some code has no marker at all. The map draws each gap where it acts.',
         'look': 'Red constraints: untraced spec items and unmarked code', 'focus': gaps + [b['constrains'][0] for b in bnecks] + ['@plaza-coverage'],
         'camera': {'target': '@dist-feat', 'zoom': 14.6, 'pitch': 50, 'bearing': -16}},
    ]

    spec = {
        'city_metadata': {
            'title': gname.upper(), 'subtitle': f'Spec ↔ code · {gdesc}'.strip(' ·'), 'theme': 'quantum_crystal', 'schema_version': '2.0',
            'scale_axis_label': '', 'scale_axis_description': 'South to north: requirements → design → features → code; roads are traceability links.',
            'building_scale': 0.6, 'target_scale': 0.6, 'road_badges': False, 'road_arrows': 'sparse', 'views': ['city', 'metro'],
            'default_view': {'legend': 'collapsed', 'layers': ['districts', 'spires', 'conduits', 'challenges']},
            'ui_labels': {'metric_scale': 'Size', 'metric_acceleration': 'Trace', 'metric_infrastructure': 'Where', 'metric_maturity': 'State',
                          'abstract_title': 'What it is', 'impact_title': 'Why it matters', 'remedy_title': 'What would fix it',
                          'target_title': 'Requirement', 'spire_badge': 'ITEM', 'priority_badge': 'NFR',
                          'kind_system': 'Code module', 'kind_knowledge': 'Requirement or design', 'kind_instrument': 'Tests', 'kind_hub': 'Feature'},
        },
        'districts': districts, 'spires': spires, 'conduits': conduits, 'bottlenecks': bnecks, 'challenges': chals,
        'plazas': [plaza], 'tour': tour, 'metro': {'routes': routes},
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print(f"[✓] {args.out}: {len(frs)} FR · {len(nfrs)} NFR · {len(comps)} components · {len(feats)} features · "
          f"{len(code_keys)} code modules · {len(conduits)} roads · {len(bnecks)} gaps · {impl_marked}/{impl_total} spec items marked")


if __name__ == '__main__':
    main()
