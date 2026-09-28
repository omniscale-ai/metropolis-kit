# 🏛️ Metropolis-Kit: Session Handover Document

**Date:** 2026-09-27  
**Repository:** [`omniscale-ai/metropolis-kit`](https://github.com/omniscale-ai/metropolis-kit)  
**Local Path:** `/Users/anaderi/git-drive/metropolis-kit`  
**Vault Project Path:** `/Users/anaderi/vault/1-Project/2026-SCIANCE/city-map`

---

## 📌 Executive Summary

We developed, packaged, and released **Metropolis-Kit**: an open-source agentic framework for converting scientific review papers, DeepTech grant proposals, and technological landscapes into interactive 3D WebGL Cyber-Physical Metropolises (inspired by the artifact and traceability architecture of `studio-kit-sdlc`).

The kit is fully deployed to GitHub, zero-dependency in Python, and contains three rich showcases.

---

## 🚀 Showcases in Repository

1. **AI Multiscale Modelling Metropolis** (`examples/ai-multiscale/`):
   - **Source:** A. Maevskiy, V. Kapitan, A. Ustyuzhanin, *"Artificial Intelligence for Multiscale Modeling in Solid-State Physics and Chemistry: A Comprehensive Review"*, Advanced Intelligent Systems (2026).
   - **Corridor:** 6 scale districts (from sub-Ångström Kohn-Sham to device digital twins).
   - **Entities:** 18 spires, 6 bottlenecks, 6 strategic priorities, 13 highways.
   - **Compiled:** 126 3D building tiers. Served by default in `docs/` on port **8080**.

2. **Materials Intelligence Metropolis** (`examples/sciance-materials/` & vault `2026-SCIANCE/city-map`):
   - **Source:** Horizon Europe SCIANCE Deliverable D1.1, Materials Science chapter, revision v3 (`matsci-2026-09-27_v3.docx`, not committed). v3 added the validation hierarchy, the PSPP cross-cutting topic (MatWerk NFDI), realistic material states (bulk vs surfaces/interfaces), predictive synthesizability, benchmark-split critique and agentic SDLs.
   - **Corridor:** The chapter's integrated workflow — Modelling → Design → Characterisation → Closed-Loop → Lab-to-Fab Production.
   - **Schema:** first showcase on **schema v2** (constraints drawn where they act — see below).
   - **Entities:** 16 spires, 9 constraints (4 edge · 2 node · 3 field), 9 priorities, 11 highways (2 planned: FAILURE LOG, IN-SILICO LOOP; 3 thin).
   - Served on port **8088**.

3. **MIND-MATTER Cyber-Physical Roadmap** (`examples/mind-matter/`):
   - **Source:** DeepTech neuromorphic roadmap (ARIA / Horizon Europe).
   - **Corridor:** Milestones M1 through D3.
   - **Entities:** 5 spires, 3 bottlenecks, 2 challenges, 2 highways.

---

## 🛠️ Key Technical Solved Issues & Features

1. **The Missing 3D Buildings Bug (Fixed):**
   - *Root cause:* MapLibre GL JS does **not** support data expressions (`['case', ...]`) on `fill-extrusion-opacity`. When that expression was present, MapLibre aborted adding the entire `buildings-3d` layer, leaving only wireframes visible.
   - *Fix:* Set `'fill-extrusion-opacity': 0.92` (number literal). All 3D crystalline towers, hazard citadels, and priority monoliths now render with full vertical lighting and facet shading.

2. **Punchy 1–2 Word Codenames (No Bland IDs):**
   - Replaced cryptic `BOT-01` and `PRIO-01` markers with punchy codenames:
     - `⚠️ BENCHMARK TRAP`, `⚠️ OOD BASIN`, `⚠️ PHONON BLIND`, `⚠️ ONE-WAY WALL`
     - `🎯 INTERPRET`, `🎯 EXACT PHYSICS`, `🎯 UNCERTAINTY UQ`, `🎯 RG RENORM`
     - `⚡ DFT FEED`, `⚡ HESSIAN LINE`, `⚡ SPIN-LATTICE`, `⚡ MOIRE RAMP`

3. **Interactive Highways (Conduits):**
   - Floating clickable badges at curve apexes (`[ ⚡ DFT FEED ]`).
   - 24px wide invisible hit-area along the spline for easy clicking.
   - Dedicated directory section in the Left Legend: `⚡ HIGHWAYS (N)`.
   - Interactive Detail Drawer with `SOURCE [Fly ➔]` and `TARGET [Fly ➔]` camera jump buttons.

4. **Dynamic 3D Height Calculation** (all heights below are then multiplied by `BUILDING_HEIGHT_SCALE` = 1/1.5 in `cli/compiler.py`):
   - **Spires:** $H = 100\text{ m} + (\text{scale\_level} \times 110\text{ m})$ (120m to 210m, +32m needle).
   - **Bottlenecks:** $H = 75\text{ m} + (\text{severity} \times 95\text{ m})$ (113m to 170m, crimson hexagonal towers).
   - **Priorities:** $H = 85\text{ m} + (\text{impact\_scale} \times 105\text{ m})$ (127m to 190m): top of a pale-gold stepped-octahedron pin on a thin beam above a ground bullseye; outer ring = green arcs per `advanced_by` spire, red arcs per `blocked_by` constraint (arcs clickable).

---

5. **Schema v2 — constraints drawn where they act (navigation-map metaphors):**
   - Bottleneck `scope`: `edge` (traffic congestion + incident pin on a highway), `node` (queue of backlog cubes + wait-time chip at a spire), `field` (coloured border tape per constraint + forecast chips in the district's NW corner, spotlight on selection; static, no animated fill). `effect`: slowdown / closure / noise / blind.
   - `delay_label` (numbers only from the source), `remedied_by`; conduit `status` → road type: operational = ⚡ Highway, thin = ⛴️ Ferry (weak/episodic flow), planned = 🚧 Planned road; challenge `advanced_by` / `blocked_by`.
   - Edge constraints on planned roads render as ⛔ barriers ("blocks construction"), not traffic; the router skips planned roads unless "include planned roads" is ticked. UI term is **Highways** (formerly Superhighways); the schema field stays `conduits`.
   - Scoped constraints have **no towers**. v1 specs without `scope` keep legacy hazard towers (ai-multiscale, mind-matter not yet migrated).
   - Compiler derives reverse links, direction, traffic segments, queue cubes, field overlays, `ROUTE_GRAPH`; places incident pins first, then conduit badges clear of pins, spires and priorities.
   - Viewer: Traffic / Queues / Weather toggles, one-way arrows, relation links on selection, clickable relation chips, legend sections for constraints and priorities, **🧭 Route** panel (Dijkstra over conduits, walking inside a district, against-flow legs penalised) listing incidents on the way. Header now reads title/subtitle from the compiled spec.

## 🔭 Planned Next (agreed, not implemented)

- **`evidence`** on every entity: `{ "section": "7.4.4", "refs": ["Leeman 2024"] }`, shown in the drawer — traceability to the source.
- **`cycle_profile`** on spires: per-stage durations of a design–make–test loop for a "popular times" histogram; only where the source gives numbers.
- Possibly a **validation rung** field on spires, following the v3 validation hierarchy (candidate → … → scale-up).
- Migrate ai-multiscale and mind-matter to schema v2.

## 🌐 Active Servers & Commands

- **AI Multiscale Metropolis:** `http://localhost:8080/`
- **SCIANCE Metropolis:** `http://localhost:8088/` — `make serve-sciance` (builds into git-ignored `dist/sciance/`; override port with `SCIANCE_PORT=…`)
- **Compile command:** `python3 -m cli.compiler --spec <spec.json> --web-dir docs/`
- **Make shortcuts:** `make serve`, `make serve-sciance`, `make build`, `make examples`, `make test`

---

## 📋 Copy-Paste Prompt for the Next Session

```markdown
Привет! Мы продолжаем работу над репозиторием `metropolis-kit` (https://github.com/omniscale-ai/metropolis-kit), расположенным локально в `/Users/anaderi/git-drive/metropolis-kit`.

Прочитай `HANDOVER.md` в корне репозитория. 
В прошлой сессии мы:
1. Запустили и упаковали фреймворк с CLI-компилятором, шаблонами и промптами.
2. Исправили баг с `fill-extrusion-opacity` в MapLibre, благодаря чему появились полноценные 3D-здания (шпили, рубиновые цитадели рисков, золотые монолиты приоритетов).
3. Добавили кликабельные суперхайвеи с бейджами на вершинах дуг и кнопками Source/Target.
4. Внедрили лаконичные кодовые имена (1–2 слова) вместо BOT-01 / PRIO-01.
5. Собрали 3 витрины: `examples/ai-multiscale/` (обзор 2026), `examples/sciance-materials/` (D1.1) и `examples/mind-matter/`.

Я хочу продолжить редактирование. [ЗДЕСЬ ОПИШИТЕ ВАШУ ЗАДАЧУ]
```
