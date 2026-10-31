# Showcase: Settings Service — spec ↔ code

A gear from [gears-rust](https://github.com/constructorfabric/gears-rust/tree/main/gears/settings-service) as a city of
its own traceability. Generated, not hand-written: `cli/import_gear.py` reads the gear's PRD, DESIGN, DECOMPOSITION and
FEATURE documents and its Rust sources, and follows the Cypilot `@cpt-*` markers that tie code blocks to spec items.

| District | Buildings | Height |
| :--- | :--- | :--- |
| 1 · Requirements | functional requirements (solid = checked off, ghost = no feature yet); NFRs as goals | priority |
| 2 · Design | components | — |
| 3 · Features | the decomposition's features + the spec ↔ code coverage plaza | number of spec items |
| 4 · Code | Rust modules | lines of code |

Roads: requirement → feature ("covers"), component → feature ("builds"), feature → feature ("depends on"),
feature → module (≥ 3 `@cpt` markers). Red constraints: spec items with no marker in the code, and code with no marker.

```bash
python3 -m cli.import_gear ~/git/gears-rust/gears/settings-service --out examples/settings-service/02-city-spec.json
python3 -m cli.compiler --spec examples/settings-service/02-city-spec.json --web-dir dist/settings-service/ --serve 8083
```

Snapshot of gears-rust as imported on 2026-11-01; re-run the importer to refresh.
