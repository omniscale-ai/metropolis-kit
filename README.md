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
| **Strategic Priorities** | Policy mandates (CRMA, Chips Act, Net-Zero) | Prismatic amber diamond beacons with horizon targets |
| **Superhighways** | High-throughput data, recipe, or material pipelines | Smooth 3D Bezier neon cables with animated photon pulses |

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
*Based on the Horizon Europe SCIANCE Deliverable D1.1 (Task 1.1 Landscape Report).*
- **Axis**: Scale Ascension across 13 physical orders of magnitude (Sub-atomic Ångström $\to$ Industrial Gigafactory).
- **Features**: NOMAD CoE, CHGNet, MatterGen, ESRF Beamline Edge AI, A-Lab, BIG-MAP, Additive Manufacturing Digital Twin.
- **Bottlenecks**: Negative reporting bias (dark data), synthesizability gap, 232-min GC latency, ~3.9% robotic error rate.

### 2. MIND-MATTER Cyber-Physical Roadmap ([`examples/mind-matter/`](examples/mind-matter/))
*Based on a DeepTech ARIA / Horizon Europe neuromorphic materials roadmap.*
- **Axis**: Milestone Horizons (M1 Transport Physics $\to$ D3 Integrated CMOS Neuromorphic Foundry).
- **Features**: SCLC transport mechanism verification, autonomous experiment designer agents, 2D memristive crossbars.
- **Bottlenecks**: Physical world fab scheduling, missing orthogonal parameter axes, irreversible metadata loss.

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
