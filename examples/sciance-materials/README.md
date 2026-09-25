# Showcase: Materials Intelligence Metropolis (SCIANCE D1.1)

This showcase visualizes the **Horizon Europe SCIANCE Deliverable D1.1** landscape report on Artificial Intelligence in European Materials Science.

### Spatial Metaphor: The Scale Ascension Corridor
Rather than a traditional chronological timeline, the city is arranged along the **Scale Ascension Corridor**, moving South to North across 13 physical orders of magnitude:
1. **$10^{-10}\text{ m}$ (Ångström)**: `ATOMISTIC MODELLING & QUANTUM SURROGATES` (DFT, MLIPs, equivariant GNNs)
2. **$10^{-9}\text{ m}$ (Nanoscale)**: `GENERATIVE CRYSTAL & INVERSE DESIGN` (MatterGen, crystal diffusion models)
3. **$10^{-6}\text{ m}$ (Microscale)**: `DATA-DRIVEN CHARACTERISATION & SYNCHROTRONS` (ESRF, TEM, Edge AI)
4. **$10^{-2}\text{ m}$ (Macro / Bench)**: `AUTONOMOUS DISCOVERY & CLOSED-LOOP LABS` (A-Lab, BIG-MAP, MAPs)
5. **$10^{0} - 10^{3}\text{ m}$ (Gigafactory)**: `LAB-TO-FAB & SUSTAINABLE MANUFACTURING` (Additive manufacturing digital twins)

### Included Entities:
- **15 Foundational Spires**: NOMAD CoE, CHGNet, AiiDA, MatterGen, GNoME, ESRF Edge AI, A-Lab, BIG-MAP, Additive Twin, etc.
- **5 Physical & Epistemic Bottlenecks**: Negative reporting dark data, the synthesizability gap, 232-min GC latency, ~3.9% robotic error rate, and industrial IP silos.
- **5 Strategic EU Priorities**: Critical Raw Materials Act (CRMA), European Chips Act, Multi-scale physics coupling, Activity cliffs, and Net-Zero circular chemistry.
- **5 Superhighways (Conduits)**: Inter-scale data streams connecting DFT repositories to robot synthesis and circular LCA.

### Compilation
To compile this showcase into the web preview:
```bash
python -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --web-dir docs/
```
