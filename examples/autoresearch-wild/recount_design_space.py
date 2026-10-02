#!/usr/bin/env python3
"""Recount the design-space plaza (A3 judge × A2 selection signal) from the compendium.

Reads the coded evidence cards wiki/projects/*.md of the metareview-autoresearch compendium
(ref [21] of arXiv:2609.11975), excludes the two cards the paper leaves out of every count,
and prints the 4×5 table with its margins, which must reproduce the paper's printed totals.

    python3 recount_design_space.py ~/git/metareview-autoresearch
"""
import glob
import os
import sys
from collections import Counter

import yaml

# Cards without a canonical registry row (paper, §2.1): a folded MLAgentBench fork, and
# AutoScientists, whose registry row was never created.
EXCLUDED = {'junshern__MLAgentBench', 'mims-harvard__AutoScientists'}
SIGNALS = ['strict-scalar', 'band-tolerant', 'vector-pareto', 'relational', 'none']
JUDGES = ['scorer', 'llm-judge', 'hybrid', 'none']
PAPER_SIGNAL = {'strict-scalar': 85, 'band-tolerant': 1, 'vector-pareto': 2, 'relational': 4, 'none': 47}
PAPER_JUDGE = {'scorer': 48, 'llm-judge': 33, 'hybrid': 19, 'none': 39}


def value(x):
    return x.get('value') if isinstance(x, dict) else x


def primary_axes(path):
    text = open(path, encoding='utf-8').read()
    front = text[4:text.find('\n---', 4)]
    block, inside = [], False
    for line in front.split('\n'):
        if line.startswith('axes:'):
            inside = True
        elif inside and line and line[0] not in ' \t':
            break
        if inside:
            block.append(line)
    return yaml.safe_load('\n'.join(block))['axes']['primary']


def main(root):
    cells = Counter()
    for path in sorted(glob.glob(os.path.join(root, 'wiki', 'projects', '*.md'))):
        if os.path.basename(path)[:-3] in EXCLUDED:
            continue
        axes = primary_axes(path)
        cells[(value(axes['judge_type']), value(axes['selection_signal']))] += 1
    total = sum(cells.values())
    print(f'records: {total}')
    print('judge \\ signal'.ljust(14) + ''.join(s[:13].rjust(14) for s in SIGNALS) + 'total'.rjust(8))
    for j in JUDGES:
        row = [cells[(j, s)] for s in SIGNALS]
        print(j.ljust(14) + ''.join(str(v).rjust(14) for v in row) + str(sum(row)).rjust(8))
    col = {s: sum(cells[(j, s)] for j in JUDGES) for s in SIGNALS}
    row = {j: sum(cells[(j, s)] for s in SIGNALS) for j in JUDGES}
    ok = total == 139 and col == PAPER_SIGNAL and row == PAPER_JUDGE
    print('margins match the paper' if ok else 'MARGINS DIFFER FROM THE PAPER')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/git/metareview-autoresearch')))
