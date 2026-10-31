# Plan: a self-explaining Metropolis (innovation-challenge demo)

Status: step 1 (the map) built 2026-10-31 — `examples/explainopolis/`; voice levels next. The map explains Metropolis-Kit + deckcast using Metropolis-Kit + deckcast.

## The map
Source documents: README + HANDOVER of metropolis-kit, README of deckcast, the three published maps.

| # | District | Thesis | Stations (examples) |
| :--- | :--- | :--- | :--- |
| 1 | The document | "Nobody reads page 47" | SCIANCE D1.1 report, arXiv:2609.11975, KD canvas; plaza: pages vs minutes-to-understand |
| 2 | Understanding | "Agents read, a human approves" | Discovery agent, domain profile, Architect agent, city spec; constraint: human review |
| 3 | Building | "One spec, many views" | Compiler, city view, metro view, tour, plazas; interchange to "Voice" |
| 4 | Voice | "The map talks" | deckcast: script → ElevenLabs clips → cues; narrated tour; Q&A; live agent |
| 5 | In use | "Already working" | SCIANCE map, ai-research-bench, KD CEO view (private) — each a station linking out |

## One mechanism behind all three levels: actions
Everything the narration can do to the map is an **action** the viewer exposes:
`show(ref)`, `open(ref)`, `tour(n)`, `view(city|metro)`, `highlight(refs)`, `plaza_cell(plaza, row, col)`; later `plaza_layer(id, layer)`.
- Level 1 calls actions from a script.
- Level 2 calls the same actions from pre-recorded answers.
- Level 3 lets the voice agent call the same actions as ElevenLabs *client tools*.
So level 3 is not a new system: it is level 1's action vocabulary handed to a live agent, and
level 2's question/answer pairs become the agent's examples and knowledge.

## Level 1 — scripted dialogue tour
Two voices: **Guide** (knows the system) and **Sceptic** (asks what a reviewer would ask).

Spec change — a tour stop gets `dialogue` instead of / besides `text`:
```json
{"id": "voice", "title": "The map talks",
 "dialogue": [
   {"speaker": "sceptic", "text": "Fine, a pretty map. But who reads a map?"},
   {"speaker": "guide",   "text": "Nobody has to — press play and it walks you through.", "do": [{"show": "@spire-tour"}]},
   {"speaker": "sceptic", "text": "And the voices — recorded by hand?"},
   {"speaker": "guide",   "text": "Generated from this very script by deckcast.", "do": [{"show": "@spire-deckcast"}, {"open": "@spire-deckcast"}]}
 ]}
```
Pipeline:
1. `cli.compiler --export-narration` → `narration.yml` in deckcast format (page = stop, lines = dialogue, speakers → voices).
2. deckcast audio mode → `stop-NN.mp3` + `cues.json` (per line: speaker, start, end, text).
3. Viewer "▶ Narrated": plays stop audio, shows subtitles with speaker names, fires each line's `do` actions at the line's start time, flies to the next stop on end. Works in city and metro.

Deliverables: dialogue for ~8 stops; `--export-narration`; deckcast audio-only mode; viewer player + action dispatcher; also an MP4 (deckcast + headless screenshots) for the application.

## Level 2 — questions to choose from
Each stop gets 2–3 `questions`, each with a short scripted answer (dialogue lines + actions), voiced by
the same pipeline as level 1 (deckcast pages `stop-NN-qK`). The card shows them as chips; clicking pauses
the tour, plays the answer, runs its actions, then offers "continue the tour".
```json
"questions": [{"q": "Is anyone actually using this?",
               "answer": [{"speaker": "guide", "text": "Three maps are live…", "do": [{"show": "@dist-inuse"}]}]}]
```

## Level 3 — talk to the city
- ElevenLabs conversational agent (as in deckcast d2). Knowledge base = compiler export `kb.md`:
  station cards, tour dialogue, level-2 Q&A, provenance.
- Client tools = the action vocabulary (`show`, `open`, `tour`, `plaza_layer`, `view`).
- System prompt: answer only from the knowledge base, name the station that shows it, say when the source has no answer.
- Viewer: mic button (ElevenLabs web SDK, public agent id / signed URL — no API key in the page); pauses the tour; hides itself if the agent is unreachable.

## Order of work
1. Self-explainer spec (districts, stations, kinds) — map without voice.
2. Action vocabulary in the viewer (used by the current tour too). — done 2026-10-31: `show`, `open`, `tour`, `view`, `highlight`, `plaza_cell` (`plaza_layer` deferred to the paper map); `window.metropolis.act`, stop-level `do`, compiler validation.
3. Level 1: dialogue texts → export → deckcast audio → player. Plus MP4. — done 2026-10-31 except the MP4.
4. Level 2: questions + answers through the same pipeline. — changed 2026-10-31 at the user's suggestion: the map asks the reader (answer = click on the map), one quiz after stop 2; done.
5. Level 3: KB export, agent, client tools, mic button. — done 2026-10-31 (`--export-kb`, `cli.voice_agent`, 🎙 Ask).

## Open decisions
- Voices: deckcast's maya (curious → guide) and owen (dry → sceptic); key in ~/git/deckcast/.env.
- ElevenLabs key location; deckcast becomes a git repo and gains an audio-only mode.
- Language of the demo (English for the challenge?).
- Whether the private KD map appears only as a screenshot.
