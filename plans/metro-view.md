# Plan: Metro-map view (City / Metro switch)

Status: v1 implemented 2026-10-30 (steps 1–4); first target `examples/autoresearch-wild`. Open items at the end.

## Why
The 3D city (heights, perspective, roads, chips) overwhelms some viewers. A schematic
metro map — flat, octilinear lines, horizontal labels, stations and interchanges — shows
the same structure with far less noise.

## Principle: one spec, two layouts
No separate metro JSON. The compiler reads the same `02-city-spec.json` and, besides the
city geometry, computes a schematic layout. Both go into `city-data.js`
(`window.METRO = { lines, stations, interchanges, layout }`). Colours, texts and cards are
shared; the viewer switches views.

## Mapping
| Spec | Metro |
| :--- | :--- |
| District | A coloured line (district colour, district thesis as line name) |
| Spire | A station on its district's line |
| Challenge (R1–R6) | Stations on the theory line, ring coloured by verdict |
| Plaza | A station with a small table icon; card shows the table |
| Cross-district conduit or semantic link | Interchange (shared station or transfer walkway) |
| Constraints | Small warning glyphs beside affected stations/segments (layer off by default) |
| Tour | A ride: stop = station; camera pans along the line |

Station order on a line: spec hint `metro.order` if present, else tour order of first
appearance, else west→east position in the district.

## Optional spec block
```json
"metro": {
  "lines": { "@dist-design": { "order": ["@spire-school-seed-line", "..."] } },
  "interchanges": [
    { "id": "registry", "label": "Registry", "members": ["@spire-reporeg", "..."] }
  ],
  "hide": ["@spire-..."]
}
```
Without the block, interchanges are derived from cross-district conduits only.

## Interchanges for autoresearch-wild (agreed)
1. **Registry** — Population ↔ Lineages, Failure modes, Theory (139 repositories → seed-line,
   54 patterns, prospective audit).
2. **Lineages & ranking** — Design ↔ Failures (seed-line ↔ Tier S, lineage term).
3. **Empty cell & R3** — Design ↔ Theory (design-space plaza ↔ R3).
4. **Judge uncalibrated & R5** — Failures ↔ Theory (the failure that contradicts R5).
5. **Hubs & lineages** — Papers ↔ Design (AI Scientist, Agent Laboratory, AI-Researcher,
   NanoResearch ∈ multi-agent-scientist; MLAgentBench ∈ mlagentbench-derived). Ends the
   isolation of the papers line.

## Layout algorithm (compiler, no external deps)
- Lines run horizontally, stacked south→north like the districts; interchanges pull
  stations of different lines into a shared column.
- Octilinear routing (0°/45°/90°): between fixed interchange columns, stations are spaced
  evenly; vertical/diagonal connectors at interchanges.
- Deterministic; small graph (5 lines, ~45 stations), so a greedy column assignment plus
  local swaps to remove crossings is enough.
- Output in an abstract grid; the viewer scales it to the screen.

## Viewer
- Toggle "City / Metro" in the top bar; remembers choice in localStorage; `#view=metro` link.
- Render with inline SVG (no MapLibre in metro mode): thick rounded lines, white station
  dots, interchange capsules, horizontal labels, legend of lines.
- Click station → same drawer card as in the city; index highlights the station.
- Tour works in both views (metro: pan/zoom SVG to the station, highlight it).

## Steps
1. Spec: optional `metro` block + validation.
2. Compiler: derive lines/stations/interchanges, octilinear layout → `window.METRO`.
3. Viewer: SVG metro renderer, view switch, shared drawer, tour support.
4. autoresearch-wild: add the five interchanges above; check readability.
5. Docs: README, HANDOVER, prompt for Architect agent.

## Implementation notes (v1)
- Compiler: `validate_metro()` and `build_metro()` in `cli/compiler.py` → `window.METRO = {lines, stations, interchanges}`.
  Lines are horizontal rows (district order); interchanges get shared columns; an interchange
  capsule that passes over a non-member line forces that line's stations off the column.
- Viewer: `🏙 City / 🚇 Metro` switch in the top bar; inline SVG renderer (drag to pan, wheel to
  zoom, Overview refits); station click opens the shared card; tour stops highlight and frame
  their focus stations; choice kept in localStorage, `#view=metro` deep link.
- Specs without a `metro` block get interchanges from cross-district roads (sciance 6,
  ai-multiscale 7, mind-matter 1).
- Testing note: headless Chrome with `--virtual-time-budget` hangs on localStorage writes;
  stub `localStorage` in test pages.

## Open items
- Octilinear (45°) routing: v1 uses straight horizontal lines with vertical transfers.
- Long transfers pass over intermediate lines (empty cell, hubs); a row permutation could
  shorten them.
- Labels: fixed 12 px on screen, re-placed on every zoom with greedy collision avoidance (stations, capsules, lines and line names are obstacles); labels that fit nowhere hide until zoom-in and stay in the hover tooltip. Dense spots (failure line around Tier S) show few labels at overview.
- Constraint glyphs on stations are not drawn yet.
- README section and Architect-agent prompt for the `metro` block.
