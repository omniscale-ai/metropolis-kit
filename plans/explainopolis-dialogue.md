# Explainopolis — dialogue tour

Generated from `examples/explainopolis/02-city-spec.json` (tour[].dialogue, tour[].quiz). Edit the spec, not this file. Actions in brackets fire when the line starts.

## 1. Nobody reads page 47

**Maya:** [warm] Welcome to Explainopolis — a map that explains how it was made. I'm Maya, I'll be your guide.  
  `→ show "@dist-doc"`

**Owen:** [dryly] And I'm Owen. I'll ask what you would ask. So — why a map? What's wrong with the document?

**Maya:** [thoughtful] Nothing, except that nobody reads it. A report keeps its argument in tables, caveats and page forty-seven. These three are real: a materials-science chapter, an arXiv paper, and a CEO's project canvas.  
  `→ highlight ["@spire-src-sciance", "@spire-src-paper", "@spire-src-kd"]`

**Owen:** [skeptical] Three very different documents. One tool for all of them?

**Maya:** [confident] The same kit. This plaza is the evidence. The paper ran to about twenty-three thousand words; its map has thirty-eight buildings and a nine-stop tour.  
  `→ show "@plaza-from-doc"; plaza_cell {"plaza": "@plaza-from-doc", "row": "arXiv paper", "col": "buildings"}`

**Owen:** [dryly] The goal out there says minutes, not pages. Let's see you earn it.  
  `→ highlight ["@chal-minutes"]`

## 2. Agents read, a human approves

**Owen:** [skeptical] Let me guess. You paste the paper into a chatbot and it draws a city?

**Maya:** [amused] Not quite. A discovery agent reads the source and proposes how to map it — the axis, the districts, the landmarks — on a single page.  
  `→ show ["@spire-discovery", "@spire-profile"]`

**Owen:** And who checks that page?

**Maya:** [matter-of-fact] A person. That's the first gate, and it's cheap: you argue about one page before anything is built. Then an architect agent turns the approved profile into a city spec — what exists, what flows where, what blocks what. No coordinates.  
  `→ highlight ["@spire-profile", "@spire-architect", "@spire-spec", "@conduit-approve", "@conduit-specify"]`

**Owen:** [pointed] Agents write numbers. Agents get numbers wrong.

**Maya:** [serious] Which is why the second gate is here: a human review, and a provenance file that separates what the source says, what we recounted, and what is only a choice of the map. On the paper's map it records the one place where the map follows the authors' own audit instead of the printed text.  
  `→ show ["@spire-review", "@spire-spec"]`

**Owen:** [dryly] So that red flag on the spec is a limit you admit, not a bug you hide.  
  `→ highlight ["@bneck-review", "@spire-spec"]`

**Maya:** [warm] Exactly. Every map here draws its limits where they act.

**Quiz — Owen:** [dryly] Your turn. Show me where a human checks the agents' work.

Right answers: @spire-review, @bneck-review, @spire-profile

**Maya (right):** [pleased] Exactly. Agents draft, a person approves, and the provenance file keeps the receipts.

**Maya (wrong):** [gentle] Close. The gates are here: the one-page profile, and the human review with its provenance file.

## 3. One spec, many views

**Maya:** [brisk] From here on, nothing is guessed. The compiler reads the spec, places every building, routes every road, and works out the cameras for this tour.  
  `→ show "@spire-compiler"`

**Owen:** [skeptical] Deterministic? Same spec, same city?

**Maya:** [confident] Same spec, same city. About fifteen hundred lines of plain Python. It refuses a spec with a broken reference, and every change is rendered headless before it ships.  
  `→ highlight ["@spire-compiler", "@spire-validator"]`

**Owen:** [honest] Still, this city is a lot. I'd lose my manager by district two.

**Maya:** [playful] Then switch. Same spec, drawn as a metro map: one line per district, and the interchanges are where the story changes lines.  
  `→ view "metro"; highlight ["@spire-spec", "@spire-compiler", "@spire-metro"]`

**Owen:** [surprised] The same file? Not a second drawing?

**Maya:** [matter-of-fact] The same file. Click an interchange and it tells you why it's there. One spec, every view — that's the goal of this district.  
  `→ highlight ["@chal-one-spec", "@spire-city", "@spire-metro", "@spire-tour"]`

**Owen:** [dryly] And the catch?

**Maya:** [candid] Big districts still need positions by hand. It's marked, right there on the compiler.  
  `→ view "city"; show ["@spire-compiler", "@bneck-layout"]`

## 4. The map talks — and listens

**Owen:** [dryly] Here's my real question. Who is talking right now?

**Maya:** [amused] We are — but neither of us was recorded. This conversation is a script in the same spec, and deckcast turned it into voices.  
  `→ show ["@spire-deckcast", "@spire-narration"]`

**Owen:** [curious] deckcast being?

**Maya:** [brisk] A small tool that compiles a narration script into voiced clips, caches them, and times every line. Those timings are why the map moves exactly when I say — here.  
  `→ highlight ["@spire-cues", "@conduit-cues", "@spire-deckcast"]`

**Owen:** [impressed, grudging] Neat. So this tour is level one. What are two and three?  
  `→ highlight ["@spire-level1", "@spire-level2", "@spire-level3"]`

**Maya:** [excited] Level two: the map asks you — you've met it already — and you answer with a click. Level three: you simply ask, out loud, and an agent answers from the map's own knowledge and flies the camera for you.  
  `→ show ["@spire-level2", "@spire-level3"]`

**Owen:** [skeptical] A live agent in a live demo. What could possibly go wrong.

**Maya:** [candid] The network. That's why it's marked as a limit — and why levels one and two need no live connection at all.  
  `→ highlight ["@bneck-network", "@spire-level3"]`

## 5. Already working

**Owen:** [serious] Last question, and it's the one a jury asks. Is anyone actually using this?

**Maya:** [confident] Yes. The materials-science chapter and the arXiv paper are public maps you can open today.  
  `→ show ["@spire-use-sciance", "@spire-use-paper"]`

**Owen:** And the third one?

**Maya:** [matter-of-fact] A CEO's view of a live project. Private, because it names people and risks — same kit, kept local.  
  `→ highlight ["@spire-use-kd"]`

**Owen:** And deckcast?

**Maya:** Two decks narrated end to end, one with a link where you can talk to the agent.  
  `→ highlight ["@spire-use-decks"]`

**Owen:** [warmer] So the thing explaining itself is built exactly like the things it explains.

**Maya:** [warm] That's the point. One spec, a compiler and a script — and a document nobody reads becomes a place you can walk through. And a place you can ask: press the Ask button, bottom right, and talk to me.  
  `→ show "@dist-use"; ask "pulse"`
