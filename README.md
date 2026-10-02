# 🏛️ Metropolis-Kit

> **Agentic Framework for Synthesizing Multi-Scale Knowledge Metropolises into Interactive 3D Cyber-Physical Worlds.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](#cli-compiler)
[![MapLibre GL](https://img.shields.io/badge/WebGL-MapLibre%203D-cyan.svg)](#3d-webgl-viewer)
[![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-orange.svg)](#1-click-github-pages-deployment)

Inspired by the structured artifact and traceability architecture of [`studio-kit-sdlc`](https://github.com/constructorfabric/studio-kit-sdlc), **Metropolis-Kit** transforms complex, unstructured scientific surveys, DeepTech grant roadmaps, and technological landscapes into navigable, interactive 3D cities.

---

## 🧭 The Core Problem

Traditional scientific literature reviews, grant deliverables, and technology roadmaps are trapped in 50-page PDF reports, static bullet points, or tangled 2D network graphs. They fail to convey:
1. **Multi-Scale Physics & Cross-Domain Lifecycles**: How sub-atomic electronic potentials ($\text{\AA}$) connect to robotic autonomous labs ($\text{cm}$) and industrial scale-up ($\text{Fab}$).
2. **Physical & Epistemic Bottlenecks**: The real rate-limiting factors (dark data reporting bias, 232-min instrument latencies, synthesizability gaps).
3. **The Coordinate Burden**: Hand-crafting 3D spatial coordinates (`[lng, lat]`, extrusions, Bezier splines) for every paper or milestone is prohibitively brittle and tedious.

**Metropolis-Kit decouples domain semantics from 3D spatial geometry.** You describe your domain in a pure semantic JSON specification; the deterministic procedural compiler builds the 3D city, generates crystalline architectural tiers, and routes energy conduits automatically.

---

## ⚡ Quickstart (30 Seconds)

```bash
# 1. Clone the repository
git clone git@github.com:omniscale-ai/metropolis-kit.git
cd metropolis-kit

# 2. Compile and launch the live showcase
make serve
```

Open **`http://localhost:8080`** in your browser to explore the 3D Metropolis!

---

## 🏗️ The 4-Stage Synthesis Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. DISCOVERY & INGESTION (Human / AI Interview)                             │
│    Input: Raw survey paper, grant proposal (PDF/Markdown), or codebase      │
│    Artifact: 01-domain-profile.yaml (Axes, metaphor, key entities)          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼ Gate 1: Topology & Metaphor Alignment
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. METROPOLIS ONTOLOGY (Semantic City Specification)                        │
│    Input: Domain Profile                                                    │
│    Artifact: 02-city-spec.json (Zero coordinate math, strict @id links)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼ Gate 2: Deterministic Schema & Integrity Check
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. PROCEDURAL SPATIAL COMPILER (Deterministic Layout Engine)                │
│    Input: 02-city-spec.json                                                 │
│    Artifact: city-data.js (Multi-tier crystal polygons, 3D Bezier splines)  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼ Gate 3: Collision-Free Packing Verification
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. VISUAL ADAPTER & RUNTIME (Autonomous WebGL App)                          │
│    Input: city-data.js + web/index.html                                     │
│    Artifact: Standalone, serverless 3D interactive viewer for GitHub Pages  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌆 Spatial Metaphors & City Primitives

| Metropolis Primitive | Scientific Domain Counterpart | Visual Representation |
| :--- | :--- | :--- |
| **Scale Ascension Corridor** | Orders of magnitude progression ($\text{\AA} \to \text{nm} \to \mu\text{m} \to \text{cm} \to \text{Fab}$) | Longitudinal South-to-North highway with glowing runway stencils |
| **Scale Districts** | Sub-disciplines, research themes, or work packages | Neon-bordered ground zones with LOD-fading beacons |
| **Spires & Crystals** | Foundational AI models, datasets, or facilities | Multi-tiered faceted crystals (pedestal, lower prism, mid-shaft, crown, needle) |
| **Hazard Radars** | Physical rate-limiters & dark data bottlenecks | Pulsating crimson radars with impact descriptions & European remedies |
| **Strategic Priorities** | Policy mandates, research frontiers, recommendations | Destination: a pale-gold bullseye on the ground and a gem pin hovering on a light beam (height = impact); the outer ring splits into green arcs (spires that advance it) and red arcs (constraints that block it) |
| **Highways** | Data, model, recipe or material flows between spires | Bezier roads with one-way arrows: ⚡ highways, ⛴️ ferries (weak flows), 🚧 planned roads |

---

## 🚦 Schema v2: Constraints Drawn Where They Act

Borrowing the visual language of navigation maps, a bottleneck is no longer a free-standing tower. It declares a `scope` and the viewer draws it at the place it acts:

| `scope` | Constrains | `effect` | Map metaphor |
| :--- | :--- | :--- | :--- |
| `edge` | `@conduit-*` | `slowdown` · `closure` | Traffic: amber→red congestion approaching an incident pin, starved or closed road after it |
| `node` | `@spire-*` | `slowdown` · `closure` | Queue: backlog cubes and a wait-time chip at the spire, a red collar when closed |
| `field` | `@dist-*` | `slowdown` · `noise` · `blind` | Weather: a coloured hazard tape along the border of every district it covers (colour = which problem, stroke = effect) plus a forecast row of clickable chips in the district corner; selecting one spotlights its coverage |

Further v2 fields: `delay_label` (numbers from the source only), `remedied_by`, conduit `status`, challenge `advanced_by` / `blocked_by`. A conduit's status sets its road type: `operational` = ⚡ highway, `thin` = ⛴️ ferry (weak or episodic flow, dotted line), `planned` = 🚧 planned road (called for, not built; grey dashes). An edge constraint on a planned road is drawn as a ⛔ barrier — the reason it is not built — instead of traffic, and the router skips planned roads unless *include planned roads* is ticked. The compiler derives reverse links, flow direction (one-way arrows), traffic segments and a routing graph; the viewer adds **Traffic / Queues / Weather** layer toggles, relation links on selection, and a **🧭 Route** panel that lists every incident between two spires. All v2 fields are optional: v1 specs still render with legacy hazard towers. Project and paper maps add spire `status` (done / active / planned), constraint `causes`, a `now_marker`, challenge `verdict`, explicit `place` offsets, and **plazas** — data tables painted on the ground with bars, fenced special cells and switchable layers. Spire `kind` picks the building archetype — `system` skyscraper, `knowledge` cathedral, `instrument` observatory, `hub` TV tower. A spec-level `tour` turns the map into a guided story of viewpoints (Space / arrows, `#tour=N` links). `city_metadata.building_scale` sizes a city's buildings; in the viewer Alt/Option + scroll (or `[` / `]`) rescales them live.

---

## 🤖 AI-Assisted Workflow (Pairing with LLMs)

Metropolis-Kit comes equipped with specialized prompt templates in the [`prompts/`](prompts/) directory for use with ChatGPT, Claude, or Google Antigravity:

1. **Step 1: Run the Discovery Agent**
   - Provide your raw PDF / text along with [`prompts/01-discovery-agent.md`](prompts/01-discovery-agent.md).
   - The agent interviews you or parses the text, outputting `01-domain-profile.yaml`.
2. **Step 2: Run the Architect Agent**
   - Pass the approved profile into [`prompts/02-architect-agent.md`](prompts/02-architect-agent.md).
   - The agent synthesizes `02-city-spec.json` with strict reference validation (`@dist-*`, `@spire-*`, `@bneck-*`, `@chal-*`).
3. **Step 3: Compile and Host**
   - Run `python -m cli.compiler --spec my-spec.json --web-dir docs/` and push to GitHub!

---

## 🛠️ CLI Compiler Reference

The built-in Python compiler (`cli/compiler.py`) requires **zero external pip dependencies** (pure standard library):

```bash
# Validate specification integrity without building
python -m cli.compiler --spec my-spec.json --validate-only

# Compile specification to custom output
python -m cli.compiler --spec my-spec.json --out dist/city-data.js

# Compile and sync directly to web folder
python -m cli.compiler --spec my-spec.json --web-dir dist/

# Compile and start live HTTP preview server on port 8080
python -m cli.compiler --spec my-spec.json --web-dir dist/ --serve 8080
```

---

## 🏛️ Included Showcases

### 1. Materials Intelligence Metropolis ([`examples/sciance-materials/`](examples/sciance-materials/))
*Based on the Materials Science chapter of Horizon Europe SCIANCE Deliverable D1.1 (Task 1.1 landscape report, chapter revision v3). First showcase on schema v2.*

**Live:** https://omniscale-ai.github.io/sciance-d1-1-metropolis/ (published from [`omniscale-ai/sciance-d1-1-metropolis`](https://github.com/omniscale-ai/sciance-d1-1-metropolis) with `make publish-sciance`)
- **Axis**: The report's own integrated workflow — atomistic modelling → generative design → characterisation → closed-loop labs → lab-to-fab production. Spire height encodes the maturity the report assigns.
- **Features**: NOMAD·FAIRmat·AiiDA, Alexandria/sAlex25, universal MLIPs, GNoME, MatterGen, 4D-STEM & APT ML, PSPP/ICME microstructure modelling, BIG-MAP, A-Lab, AP-Lab, AM digital twins, SSbD/PFAS.
- **Constraints, drawn where they act**: congestion and incident pins on highways (novelty mirage, vendor lock-in, lab-to-fab gap, the bulk-vs-interface closure of the planned IN-SILICO LOOP); queues at spires (232-min GC & ~3.9% robot faults, middleware silos); border tapes and forecast chips on districts (dark data, OOD fragility, synthetic data fraud).
- **Signature detail**: 4 of 11 highways are feedback or planned roads the report asks for but finds missing — and the Route panel shows every incident between an atom-scale spire and the pilot line.

### 2. MIND-MATTER Cyber-Physical Roadmap ([`examples/mind-matter/`](examples/mind-matter/))
*Based on a DeepTech ARIA / Horizon Europe neuromorphic materials roadmap.*
- **Axis**: Milestone Horizons (M1 Transport Physics $\to$ D3 Integrated CMOS Neuromorphic Foundry).
- **Features**: SCLC transport mechanism verification, autonomous experiment designer agents, 2D memristive crossbars.
- **Bottlenecks**: Physical world fab scheduling, missing orthogonal parameter axes, irreversible metadata loss.

---

### 3. AI Multiscale Modelling Metropolis ([`examples/ai-multiscale/`](examples/ai-multiscale/))
*Based on Maevskiy, Kapitan & Ustyuzhanin, "Artificial Intelligence for Multiscale Modeling in Solid-State Physics and Chemistry: A Comprehensive Review", Advanced Intelligent Systems 8 (2026) e202501219.*
- **Axis**: Scale Ascension from sub-Ångström Kohn–Sham electronic structure (fs) to device-level digital twins and self-driving laboratories.
- **Features**: DeepH/xDeepH, HamGNN, differentiable DFT (D4FT, GradDFT, Jrystal), NequIP/MACE/SevenNet/CHGNet, Phonax, RSMI-NE & multiscale structural complexity, quasicontinuum & Gaussian Phase Packets, MOFDiff/MOFFlow, the Li$_x$CoO$_2$ four-scale pipeline.
- **Bottlenecks**: Benchmark-only validation (MD17/QH9), MLIP overstabilisation of local minima, long-range blindness in GNN phonons, bead mapping vs crystalline symmetry, one-way hierarchical coupling, computational-only ground truth.
- **Signature detail**: 12 highways run northbound and exactly 1 runs back south — the review's finding on the near-absence of bidirectional scale coupling, rendered as geometry.

---

### 4. Autoresearch in the Wild ([`examples/autoresearch-wild/`](examples/autoresearch-wild/))
*An illustration for Komissarov & Ustyuzhanin, "AI-Research Agents in the Wild" (arXiv:2609.11975).*

**Live:** https://omniscale-ai.github.io/ai-research-bench/ — press ▶ Tour for the 8-stop story.
- **Axis**: the paper's own Figure 1 — the population → the design space → the theory on trial → papers ↔ code, each district labelled with its thesis.
- **Features**: R1–R6 as targets coloured by verdict; limitations drawn where they act; the empty vector × LM-judge cell with its near miss (scaffolded) and two ghosts; two **data plazas** — the design space and Table 7's cost × ambition matrix with a switch between evidence rules.

---

## 🚀 1-Click GitHub Pages Deployment

The repository includes a ready-to-run GitHub Actions workflow ([`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)):

1. In your GitHub repository settings, go to **Settings $\to$ Pages**.
2. Select **Source: GitHub Actions**.
3. Push to `main`. Your 3D Metropolis will be live at `https://<org>.github.io/<repo>/` automatically!

---

## 📄 License

Metropolis-Kit is open-source software licensed under the **[MIT License](LICENSE)**.
Created by [Omniscale AI](https://github.com/omniscale-ai) & contributors.
