# Showcase: Explainopolis — a map that explains how it was made

The self-explaining demo for metropolis-kit + deckcast: the map describes the pipeline that built it.

1. **The document** — real sources explained with the kit (SCIANCE D1.1 chapter, arXiv:2609.11975, the KD project canvas) and a plaza "from document to map".
2. **Understanding** — discovery agent → domain profile → architect agent → city spec, with human review and provenance.
3. **Building** — compiler → city view, metro view, guided tour; checks on every build.
4. **Voice** — deckcast, the narration script and cues as handover files, and three levels of voice (dialogue tour, questions to choose, talk to the city) — levels are planned, see `plans/self-explainer.md`.
5. **In use** — the published maps and narrated decks.

Numbers come from the specs and code in this repository and in deckcast (2026-10-31).

```bash
python -m cli.compiler --spec examples/explainopolis/02-city-spec.json --web-dir dist/explainopolis/ --serve 8082
```
