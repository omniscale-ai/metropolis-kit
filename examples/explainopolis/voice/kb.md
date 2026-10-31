# EXPLAINOPOLIS — knowledge base

A map that explains how it was made · metropolis-kit + deckcast

Layout: South to north: a document nobody reads → agents that understand it → a compiler that builds views → voices that tell it → maps already in use.

Every object below has an id in backticks. Pass these ids to the tools (show, highlight, open) to point at the object on the map.

## District `@dist-doc` — 1 · THE DOCUMENT

Thesis: Nobody reads page 47
Real sources that were explained with this kit: a report chapter, a research paper, a project canvas.

### `@spire-src-sciance` — SCIANCE D1.1 — Materials Science chapter
Kind: knowledge.
- Size: ~14,500 words
- What it does: Horizon Europe deliverable
- Where it lives: docx draft, three revisions
- State: Explained in the SCIANCE map
A landscape report chapter on AI in European materials science, revised three times while the map followed it. The kind of document reviewers skim and nobody reads to page 47.

### `@spire-src-paper` — arXiv:2609.11975 — AI-Research Agents in the Wild
Kind: knowledge.
- Size: ~23,000 words · 56 pages
- What it does: 139 repositories · 101 papers
- Where it lives: arXiv preprint + supplementary tables
- State: Explained in ai-research-bench
A meta-study of the public ecosystem of AI-research agents, with six candidate regularities, a prospective audit and three supplementary tables. Its argument lives in tables and caveats.

### `@spire-src-kd` — Knowledge Discovery — CEO status canvas
Kind: knowledge.
- Size: 24 canvas nodes · 3-year roadmap
- What it does: Epics, risks, milestones
- Where it lives: Obsidian canvas + timelines
- State: Explained in a private CEO map
A project status canvas: epics, waiting items, a risk cascade and milestones. A different kind of document — a plan, not a text — explained with the same kit.

### Goal `@chal-minutes` — Minutes, not pages
Understand a 50-page document's argument in a five-minute guided tour — and still be able to open every number.
- Advanced by: Guided tour, Level 1 — narrated dialogue tour

### Data plaza `@plaza-from-doc` — From document to map

Table (Three real sources and the maps compiled from them): rows are SCIANCE chapter, arXiv paper, KD canvas; columns are source, districts, buildings, tour stops.
- SCIANCE chapter: source = 14.5k words; districts = 5; buildings = 16; tour stops = —
- arXiv paper: source = 23k words; districts = 5; buildings = 38; tour stops = 9
- KD canvas: source = 24 nodes; districts = 4; buildings = 18; tour stops = —

## District `@dist-und` — 2 · UNDERSTANDING

Thesis: Agents read, a human approves
Two agents turn a document into a one-page profile and then a semantic spec; a person approves both and a provenance file keeps every number honest.

### `@spire-discovery` — Discovery agent
Kind: system.
- Size: Prompt + LLM
- What it does: Reads the source, proposes the metaphor
- Where it lives: prompts/01-discovery-agent.md
- State: In use
Reads the source document and proposes the city: the axis, the districts, the landmarks, the bottlenecks, the flows. Output is a short domain profile a human can review in minutes.

### `@spire-profile` — Domain profile
Kind: knowledge.
- Size: One YAML page
- What it does: Metaphor, axis, districts, key facts
- Where it lives: 01-domain-profile.yaml
- State: Reviewed by a human
The first gate: one page that states how the document will be mapped and why. Cheap to argue about before anything is built.

### `@spire-architect` — Architect agent
Kind: system.
- Size: Prompt + LLM
- What it does: Writes the semantic city spec
- Where it lives: prompts/02-architect-agent.md
- State: In use
Turns the approved profile into a city spec: stations, flows, constraints, priorities, tour — with no coordinates. Rules in the prompt: numbers only from the source, constraints placed where they act.

### `@spire-spec` — City spec
Kind: knowledge.
- Size: One JSON file
- What it does: Districts · spires · roads · constraints · tour · metro
- Where it lives: 02-city-spec.json, schema v2
- State: Validated by the compiler
The contract between understanding and building. Pure semantics — what exists, what flows where, what blocks what, what the tour says — and every view and every voice is generated from it.

### `@spire-review` — Human review & provenance
Kind: instrument.
- Size: Two gates + a provenance file
- What it does: Paper vs derived vs map choice
- Where it lives: DATA-PROVENANCE.md
- State: Done for the paper map
A person approves the profile and the spec, and a provenance file separates what the source says, what was recounted, and what is a choice of the map. It caught a claim in the paper that its own data do not support.

### Constraint `@bneck-review` — A person must check the spec
- Nature: Honest limit
- Impact: Agents draft the profile and the spec, but numbers and claims need a human read before publishing; the paper map's provenance file exists for that reason.
- Remedy: Keep the two gates and the provenance file; make the review a checklist.

### Goal `@chal-trace` — Every number traceable
Each station says where its numbers come from: the source, a recount, or a choice of the map.
- Advanced by: Human review & provenance, City spec
- Blocked by: @bneck-review

## District `@dist-build` — 3 · BUILDING

Thesis: One spec, many views
A deterministic compiler turns the spec into a 3D city, a metro map and a guided tour.

### `@spire-compiler` — Spatial compiler
Kind: system.
- Size: ~1,500 lines · Python stdlib only
- What it does: Spec → geometry, layouts, routing graph
- Where it lives: cli/compiler.py
- State: 25 commits in a month
Deterministic: validates references, places buildings, routes roads, derives traffic, queues, weather, the metro layout and the tour cameras. No coordinates are ever written by hand unless asked.

### `@spire-city` — City view
Kind: system.
- Size: MapLibre 3D, one HTML file
- What it does: Five building kinds, plazas, constraints
- Where it lives: web/index.html
- State: Published
Districts, buildings whose shape says what a thing is, roads with traffic and barriers, data tables painted on the ground.

### `@spire-metro` — Metro view
Kind: system.
- Size: SVG schematic from the same spec
- What it does: Lines, stations, interchanges
- Where it lives: City / Metro switch
- State: New
For readers who find the city too busy: the same spec as a metro map — lines per district, compact interchanges with an explanation card, labels that never overlap.

### `@spire-tour` — Guided tour
Kind: system.
- Size: Stops with focus, camera, items
- What it does: Space / arrows, #tour=N links
- Where it lives: spec "tour"
- State: Nine stops in the paper map
A story told with the map: each stop flies the camera, dims everything else and says one thing. The stops are what the voices will read.

### `@spire-validator` — Validator & render checks
Kind: instrument.
- Size: Reference and schema checks
- What it does: Headless renders, overlap checks
- Where it lives: make test
- State: Every build
Refuses a spec with broken references or impossible combinations, and every change is checked by rendering it headless before it ships.

### Constraint `@bneck-layout` — Dense maps need manual placement
- Nature: Honest limit
- Impact: Automatic placement handles small districts; districts with many buildings or plazas still need explicit positions in the spec.
- Remedy: Smarter packing in the compiler; label placement already avoids overlaps.

### Goal `@chal-one-spec` — One spec, every view
City, metro, tour and voices are all generated from the same spec, so they never disagree.
- Advanced by: Spatial compiler, City view, Metro view
- Blocked by: @bneck-layout

## District `@dist-voice` — 4 · VOICE

Thesis: The map talks — and listens
deckcast voices the tour as a dialogue; then pre-voiced questions; then a live agent that answers and moves the map.

### `@spire-deckcast` — deckcast
Kind: system.
- Size: ~830 lines Python
- What it does: Script → ElevenLabs clips → timeline
- Where it lives: Typer CLI, FFmpeg
- State: Two narrated decks
Compiles a narration script into voiced clips with a cache, measures them and builds a timeline — a video, or per-page audio with line-level cues for a web player.

### `@spire-narration` — Narration script
Kind: hub.
- Size: Pages → lines → speaker, text, emotion
- What it does: Exported from the tour dialogue
- Where it lives: deckcast script (JSON/YAML)
- State: Generated by the compiler
The handover between the map and the voices: one page per tour stop, one line per spoken sentence, two speakers.

### `@spire-cues` — Audio & cues
Kind: hub.
- Size: One mp3 per stop + line timings
- What it does: speaker · start · end · text
- Where it lives: site-audio/cues.json
- State: Working in deckcast d2
Lets the player show subtitles and fire map actions exactly when a line is spoken.

### `@spire-level1` — Level 1 — narrated dialogue tour
Kind: system.
- Size: 5 stops · 39 lines · ~5 min
- What it does: Lines move the map on cue
- Where it lives: maya · owen, deckcast audio
- State: Working
The tour read as a conversation: the sceptic asks what a reviewer would ask, the guide answers and points at the map.

### `@spire-level2` — Level 2 — the map asks
Kind: system.
- Size: One question, after stop 2
- What it does: Answer = a click on the map
- Where it lives: same script, voices and actions
- State: Working
After a stop the sceptic asks a question; the reader answers by clicking on the map, and a recorded line says right or wrong and shows the answer.

### `@spire-level3` — Level 3 — talk to the city
Kind: system.
- Size: ElevenLabs agent, Maya's voice
- What it does: Answers from the map, points with the tour's actions
- Where it lives: knowledge base exported by the compiler
- State: Working — needs the network
Ask anything by voice; the agent answers from the map's own knowledge and flies the camera to the evidence.

### Constraint `@bneck-script` — Dialogue is still written, not generated
- Nature: Honest limit
- Impact: The compiler exports the tour as a two-voice script and deckcast voices it, but someone still writes the dialogue lines in the spec.
- Remedy: Draft the dialogue with the architect agent, then review it like the spec.

### Constraint `@bneck-network` — The live agent needs the network
- Nature: Honest limit
- Impact: A live voice agent adds latency and can be unreachable during a demo.
- Remedy: Levels 1 and 2 work offline from files; the mic button hides itself when the agent is unreachable.

### Goal `@chal-ask` — Ask the city
Anyone can ask a question by voice and be shown the answer on the map.
- Advanced by: Level 3 — talk to the city, deckcast
- Blocked by: @bneck-network, @bneck-script

## District `@dist-use` — 5 · IN USE

Thesis: Already working
Maps and narrated decks that exist today.

### `@spire-use-sciance` — SCIANCE materials map
Kind: system.
- Size: Public, GitHub Pages
- What it does: 5 districts · 16 buildings
- Where it lives: sciance-d1-1-metropolis
- State: Followed 3 revisions
The materials-science chapter as a city with constraints drawn where they act.
- Link: Open the SCIANCE map — https://omniscale-ai.github.io/sciance-d1-1-metropolis/

### `@spire-use-paper` — Autoresearch in the Wild
Kind: system.
- Size: Public, GitHub Pages
- What it does: 5 districts · 38 buildings · 9-stop tour
- Where it lives: ai-research-bench
- State: City + metro
The paper as five story districts with lineages, failure modes, six rules on trial, data plazas and a provenance file.
- Link: Open the paper map — https://omniscale-ai.github.io/ai-research-bench/

### `@spire-use-kd` — Knowledge Discovery CEO view
Kind: system.
- Size: Private, local only
- What it does: Epics, waits, risk cascade, milestones
- Where it lives: project status map
- State: Used for a status read-out
A project as a time corridor with a 'you are here' line; kept private because it names people and risks.

### `@spire-use-decks` — deckcast narrated decks
Kind: system.
- Size: 97-second video · 12-slide two-voice site
- What it does: MP4 and self-contained HTML
- Where it lives: deckcast d1, d2
- State: Shared with colleagues
Two decks already narrated end to end, one with a talk-to-the-agent link.

## Roads (flows between objects)

- `@conduit-read` The agent reads the source document: arXiv:2609.11975 — AI-Research Agents in the Wild → Discovery agent. The agent reads the source document.
- `@conduit-propose` A one-page profile proposes the metaphor: Discovery agent → Domain profile. A one-page profile proposes the metaphor.
- `@conduit-approve` A human approves the profile before anything is built: Domain profile → Architect agent. A human approves the profile before anything is built.
- `@conduit-specify` The architect writes the semantic spec: Architect agent → City spec. The architect writes the semantic spec.
- `@conduit-compile` One spec in, every view out: City spec → Spatial compiler. One spec in, every view out.
- `@conduit-city` Geometry for the city: Spatial compiler → City view. Geometry for the city.
- `@conduit-metro` Layout for the metro map: Spatial compiler → Metro view. Layout for the metro map.
- `@conduit-tour` Resolved tour cameras: Spatial compiler → Guided tour. Resolved tour cameras.
- `@conduit-export` The tour becomes a two-voice narration script: Guided tour → Narration script. The tour becomes a two-voice narration script.
- `@conduit-voice` deckcast voices every line: Narration script → deckcast. deckcast voices every line.
- `@conduit-cues` Audio per stop and line timings: deckcast → Audio & cues. Audio per stop and line timings.
- `@conduit-play` The viewer plays the dialogue and moves the map on cue: Audio & cues → Level 1 — narrated dialogue tour. The viewer plays the dialogue and moves the map on cue.
- `@conduit-qa` Questions and answers use the same script, voices and map actions: Level 1 — narrated dialogue tour → Level 2 — the map asks. The quiz uses the same script, voices and map actions.
- `@conduit-kb` Q&A and station cards become the live agent's knowledge; map actions become its tools: Level 2 — the map asks → Level 3 — talk to the city. Q&A and station cards become the live agent's knowledge; map actions become its tools.
- `@conduit-pub1` Live on GitHub Pages: City view → SCIANCE materials map. Live on GitHub Pages.
- `@conduit-pub2` Live on GitHub Pages, city and metro: Metro view → Autoresearch in the Wild. Live on GitHub Pages, city and metro.
- `@conduit-pub3` Served locally only: City view → Knowledge Discovery CEO view. Served locally only.
- `@conduit-decks` Narrated decks: deckcast → deckcast narrated decks. Narrated decks.

## Metro view interchanges

- Where reading starts: The discovery agent reads the source document — here the arXiv paper — and proposes how to map it. (stations: arXiv:2609.11975 — AI-Research Agents in the Wild, Discovery agent)
- The one contract: Everything downstream is compiled from this one file: the city, the metro, the tour, and the narration script. (stations: City spec, Spatial compiler)
- Where the map starts talking: The tour's stops become the narration script that deckcast voices. (stations: Guided tour, Narration script)
- From build to a live link: A build is a static folder; GitHub Pages turns it into a link anyone can open. (stations: Metro view, Autoresearch in the Wild)

## The guided tour

### Stop 1: Nobody reads page 47
Reports, papers and project plans carry their argument in tables, caveats and page 47. These three were real, and each became a map.
- Maya: Welcome to Explainopolis — a map that explains how it was made. I'm Maya, I'll be your guide.
- Owen: And I'm Owen. I'll ask what you would ask. So — why a map? What's wrong with the document?
- Maya: Nothing, except that nobody reads it. A report keeps its argument in tables, caveats and page forty-seven. These three are real: a materials-science chapter, an arXiv paper, and a CEO's project canvas.
- Owen: Three very different documents. One tool for all of them?
- Maya: The same kit. This plaza is the evidence. The paper ran to about twenty-three thousand words; its map has thirty-eight buildings and a nine-stop tour.
- Owen: The goal out there says minutes, not pages. Let's see you earn it.

### Stop 2: Agents read, a human approves
One agent proposes a one-page profile, another writes the spec. A person approves both, and a provenance file says where each number comes from.
- Owen: Let me guess. You paste the paper into a chatbot and it draws a city?
- Maya: Not quite. A discovery agent reads the source and proposes how to map it — the axis, the districts, the landmarks — on a single page.
- Owen: And who checks that page?
- Maya: A person. That's the first gate, and it's cheap: you argue about one page before anything is built. Then an architect agent turns the approved profile into a city spec — what exists, what flows where, what blocks what. No coordinates.
- Owen: Agents write numbers. Agents get numbers wrong.
- Maya: Which is why the second gate is here: a human review, and a provenance file that separates what the source says, what we recounted, and what is only a choice of the map. On the paper's map it records the one place where the map follows the authors' own audit instead of the printed text.
- Owen: So that red flag on the spec is a limit you admit, not a bug you hide.
- Maya: Exactly. Every map here draws its limits where they act.
- Quiz — Owen asks: Your turn. Show me where a human checks the agents' work. Answer: Human review & provenance, @bneck-review, Domain profile.

### Stop 3: One spec, many views
A deterministic compiler turns the spec into a 3D city, a metro map and this tour. Change the spec, rebuild, and every view agrees.
- Maya: From here on, nothing is guessed. The compiler reads the spec, places every building, routes every road, and works out the cameras for this tour.
- Owen: Deterministic? Same spec, same city?
- Maya: Same spec, same city. About fifteen hundred lines of plain Python. It refuses a spec with a broken reference, and every change is rendered headless before it ships.
- Owen: Still, this city is a lot. I'd lose my manager by district two.
- Maya: Then switch. Same spec, drawn as a metro map: one line per district, and the interchanges are where the story changes lines.
- Owen: The same file? Not a second drawing?
- Maya: The same file. Click an interchange and it tells you why it's there. One spec, every view — that's the goal of this district.
- Owen: And the catch?
- Maya: Big districts still need positions by hand. It's marked, right there on the compiler.

### Stop 4: The map talks — and listens
deckcast voices the script with two speakers. The tour is a dialogue, the map asks you a question, and a live agent answers yours.
- Owen: Here's my real question. Who is talking right now?
- Maya: We are — but neither of us was recorded. This conversation is a script in the same spec, and deckcast turned it into voices.
- Owen: deckcast being?
- Maya: A small tool that compiles a narration script into voiced clips, caches them, and times every line. Those timings are why the map moves exactly when I say — here.
- Owen: Neat. So this tour is level one. What are two and three?
- Maya: Level two: the map asks you — you've met it already — and you answer with a click. Level three: you simply ask, out loud, and an agent answers from the map's own knowledge and flies the camera for you.
- Owen: A live agent in a live demo. What could possibly go wrong.
- Maya: The network. That's why it's marked as a limit — and why levels one and two need no live connection at all.

### Stop 5: Already working
Two public maps, a private CEO view and two narrated decks exist today — and this map was built the same way.
- Owen: Last question, and it's the one a jury asks. Is anyone actually using this?
- Maya: Yes. The materials-science chapter and the arXiv paper are public maps you can open today.
- Owen: And the third one?
- Maya: A CEO's view of a live project. Private, because it names people and risks — same kit, kept local.
- Owen: And deckcast?
- Maya: Two decks narrated end to end, one with a link where you can talk to the agent.
- Owen: So the thing explaining itself is built exactly like the things it explains.
- Maya: That's the point. One spec, a compiler and a script — and a document nobody reads becomes a place you can walk through. And a place you can ask — press Ask, and talk to me.
