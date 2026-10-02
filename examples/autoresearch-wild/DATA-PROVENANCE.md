# Data provenance — Autoresearch in the Wild map

What the map is built from, which parts go beyond the text of the paper, and which parts are
choices of the map rather than claims of the study.

## Sources

| Source | Version | Access |
| :--- | :--- | :--- |
| **Paper**: Komissarov & Ustyuzhanin, “AI-Research Agents in the Wild. From GitHub and arXiv to Regularities and Gaps”, [arXiv:2609.11975](https://arxiv.org/abs/2609.11975), incl. Supplementary Tables S1–S3 | v1, 1 Sep 2026 (analytic freeze 10 Jun 2026) | Public |
| **Compendium**: `ad3002/metareview-autoresearch` — registries, coded evidence cards, analysis code (the paper's companion deposit, ref. [21]) | commit `4bd9215` (2026-08-04) | Private on GitHub as of 2026-10-02; the paper states the archival snapshot is deposited with the submitted version |

## 1. Taken directly from the paper

Every number below is printed in the paper; the map only places it.

| Map element | Paper location |
| :--- | :--- |
| 139 repositories, 101 papers (98 unique), freeze 10 Jun 2026 | Abstract, §2.1–2.2 |
| Discovery channels 83 / 30 / 15 / 9 / 1 / 1 | §2.1 |
| 9 lineages, 59 memberships, 52 repositories, 7 in two lineages | §2.3, §4.1 |
| A2 / A3 marginals (85 · 1 · 2 · 4 · 47; 48 · 33 · 19 · 39), 38 records with neither | §2.3 |
| 54 promoted patterns (22 · 7 · 16 · 9), 16 single-artifact | §2.3 |
| 3547 anchors / 3306 verbatim; 538 bindings; 0 contradictions in 176; 10/64 and 10/59 contradicted | §2.5 |
| Authorship: 718 slots, 661 names, ≥18 commit-adjudicated, 58 byline, ≥24/63 excluded | §2.6, §4.3, Table 3 |
| R1–R6 statements, triggers, audit outcome 0/6, current status | §3.1–3.3, Tables 1–2 |
| Tier S patterns and scores, the four weightings | §3.1 (R4), Appendix A.1, Table 5 |
| Post-freeze re-test 962 → 319 → 69 → 15, 11 refuted; virtual-biotech-scientist, XScientist, AgenticOperator, nexus-swarm | §3.4, “Use of Generative AI” |
| Relatedness graph: 212 edges, 64/101, 23/139, top six and their counts, 56.6 %, CIs | §4.2, Appendix A.2, Table 6 |
| “3 of 29 edges have a locatable mention” | §5.6 |
| Cost × ambition plaza, rules (a) and (b), the two counterexamples | §3.1 (R2), Appendix A.3, Table 7 |
| Limitations (engineered sample, private use, single coder, 25 non-random cases, 25 papers without full text) | §5.6, §4.4 |

## 2. Counted or summed by us from the paper's tables

| Map element | How |
| :--- | :--- |
| Lineage sizes (seed-line 19, dr-deep-research-agent 10, rl-post-training 8, multi-agent-scientist 7, clune-lab 5, mlagentbench-derived 4, camel-ai-line 2, dspy-line 2, physical-robotic-automation 2) | Counted from the lineage column of Table S1 (sums to 59) |
| “26 other channels” | 15 + 9 + 1 + 1 from §2.1 |
| “87 records in no lineage” | 139 − 52 (§4.1) |

## 3. Taken from the compendium — not printed in the paper

Both tables below are recounted from the coded evidence cards `wiki/projects/*.md`, excluding the two
cards the paper leaves out of every count (`junshern__MLAgentBench`, a folded fork, and
`mims-harvard__AutoScientists`, whose registry row was never created). `recount_design_space.py`
reproduces the design-space table and checks it against the paper.

| Map element | Fields used | Check |
| :--- | :--- | :--- |
| **Design-space plaza** — full 4 × 5 table, A3 judge × A2 selection signal (district 2) | `axes.primary.judge_type`, `axes.primary.selection_signal` | All row and column totals equal the paper's marginals (§2.3); the two cells the paper mentions (LLM × vector = 0, absent × none = 38) agree |
| Names in the design-space notes: the two vector-signal repositories (gepa, schliff), the three LLM-judged relational systems (AI-CoScientist, open-ai-co-scientist, co-scientist) | same | — |
| **Roles plaza** — role × acceptance gate, 2 × 8 (district 1): 84 coded agents, 55 other artifacts | `axes.primary.tool_category`, `axes.primary.judge_type` (present / `none`) | Row totals 100 / 39 equal the paper's A3 split (139 − 39 absent); role totals sum to 139 |
| Contents of the judge-absent row: 13 curated lists, 10 substrates, 6 benchmarks, 3 libraries, 3 meta-tools, 1 broker, 3 agents (two of them paper stubs) | same | — |
| “84 coded as agents” in tour stop 1 | `tool_category = agent` | — |
| **Lineage towers** (district 2): one tower per promoted lineage, height by member count | Sizes from Table S1 (paper); one-line profiles and member samples from `wiki/schools/*.md`; typical judge/signal per lineage from the members' cards | Sizes sum to 59 memberships over 52 repositories, as in the paper |
| Shared-member roads between lineages: deep research ↔ RL post-training (4), Clune ↔ multi-agent scientist (2), MLAgentBench-derived ↔ RL (1) | Lineage member lists | 7 repositories in two lineages, as in §2.3 |
| **Failure-modes district**: nine antipattern towers, height by number of repositories | Member lists of `wiki/antipatterns/*.md` (judge-uncalibrated: per-record coding instead, see next row); Tier S membership from the paper (Table 5) | Page counts 8 · 4 · 2 · 2 · 1 · 1 · 1 · 1 · 1 match the compendium's declared counts (CLAIM_LEDGER) |
| **Uncalibrated judges by lineage** plaza and the “7 LINEAGES” chip | Per-record coding `axes.modifier.judge.calibration = uncalibrated` (35 canonical records) × Table S1 lineage membership | **Differs from the paper**: v1 says “judge uncalibrated occurs in four lineages”. The authors' claim audit (`paper/CLAIM_LEDGER.md`, T5-12, 2026-07-26) marks that figure UNSUPPORTED: by antipattern-page membership it is 2 lineages, by per-record coding 7 of 9 (11 including candidate clusters). The map uses the coded measure, as the audit recommends |

**Caveat on roles.** `tool_category` is a coded role, not a runnability check. The paper states that
estimating the number of runnable agents requires a separate role-coding pass with an explicit sampling
frame (§2.1, §4.1); the map labels the figure “coded as agents” for that reason.

## 4. Choices of the map, not claims of the study

- **District structure** follows the paper's Figure 1 and RQ1–RQ3; district theses are our one-line summaries.
- **Spire height** encodes the element's weight in the paper's argument (our judgement); hub heights scale with their edge counts.
- **Building kinds**: skyscraper = object from the studied ecosystem; cathedral, observatory and TV tower = the study's own corpora, instruments and intake channels.
- **Spire status**: virtual-biotech-scientist drawn “under construction” (2 of 3 clauses), XScientist and AgenticOperator as ghosts (unreachable / no code) — visual readings of §3.4.
- **Verdict colours** map Table 2 to four words: R1, R3 bounded support; R2, R4 conditional; R5 contradicted (broad form); R6 exploratory.
- **Which limitation sits on which element**, and the red/green arcs between regularities and evidence, are our reading of §3 and §5.6.
- **Tour texts** paraphrase the paper; numbers in them are from §1–§3 above.
- **Expected counts** (“exp”) under the design-space zeros are our addition: row total × column total / 139, i.e. what each cell would hold if judge and signal were independent. They show that a zero in a column with two records is not statistically surprising, so the R3 fence is labelled by attempts (“≥23 near, 0 clean”), not by the count.
- **Hatched “not running a loop” rows** are our reading of the judge-absent records: zeros there are structural (no acceptance gate, mostly non-agent artifacts) rather than findings.
- **Lineage tower placement**: each tower stands west of the design-space plaza, roughly at the row of its members' typical judge — a visual summary, not a coded position.
- **Roles grouping**: the eight `tool_category` values are shown as they are coded; “agent” vs the rest is our one-line summary (84 / 55).
- **`building_scale`**, colours, positions and the empty-cell label “∅ loop” are presentation only.
