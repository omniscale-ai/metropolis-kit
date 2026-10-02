# Showcase: Autoresearch in the Wild (paper illustration)

An evidence map of **“AI-Research Agents in the Wild. From GitHub and arXiv to Regularities and Gaps”**
(Aleksey Komissarov & Andrey Ustyuzhanin, [arXiv:2609.11975](https://arxiv.org/abs/2609.11975), analytic freeze 10 June 2026).
Built only from the public paper, including Supplementary Tables S1–S3.

### Spatial metaphor: the paper's evidence pipeline
South to north the city follows the study's method:

1. **Sources** — discovery channels (curated lists 83, synthesis passes 30, paper references 15, leaderboard 9) and the arXiv corpus
2. **Registries** — 139 repositories, 101 papers, nine lineages (59 memberships), 54 promoted patterns, evidence cards, the 212-edge relatedness graph
3. **Coding & verification** — A1–A5, 3547 anchors, 538 load-bearing bindings, the Tier S ranking, the authorship audit; **design-space plaza**
4. **Theory** — six candidate regularities R1–R6 as targets coloured by verdict; **cost × ambition plaza** (Table 7, rules (a)/(b))
5. **Tests** — the 25-case prospective audit and the post-freeze re-test, with the three cases that bound the empty cell

### How to read it
- **Spire height** — weight of the element in the paper's argument, not sample size. A spire **in scaffolding** meets the empty-cell trigger only in part (virtual-biotech-scientist, 2 of 3 clauses); **ghosts** are things that do not work or cannot be run (XScientist's unreachable pool, AgenticOperator without code).
- **Pins on R1–R6** — green *bounded support*, amber *conditional*, red *contradicted*, grey *exploratory*. Green arcs: supporting evidence; red arcs: counterevidence.
- **Limitations are drawn where they act**: weather over districts (engineered sample, private use unmeasured, single coder), traffic on a road (relatedness is not citation: 3 of 29 edges have a mention), queues at artifacts (25 non-random cases, 10/64 · 10/59 contradicted bindings, 11 of 15 triage flags refuted…).
- **Plazas** — tables painted on the ground. In the design-space plaza only the published marginals and two cells are shown; the rest is marked *n/p* rather than estimated.

### Compilation
```bash
python -m cli.compiler --spec examples/autoresearch-wild/02-city-spec.json --web-dir dist/autoresearch/ --serve 8091
```
