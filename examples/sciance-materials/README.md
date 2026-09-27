# Showcase: Materials Intelligence Metropolis (SCIANCE D1.1)

This showcase visualizes the **Materials Science chapter** of the Horizon Europe **SCIANCE Deliverable D1.1**
("State of the art for scientific research using AI for each pilot scientific area"), draft v0.4
(source file `matsci-2026-09-27.docx`; chapter author Andrey Ustyuzhanin, contributor Vitalii Kapitan).

### Spatial Metaphor: The Scale Ascension Corridor
The chapter describes its five research themes as one integrated workflow "from atomistic modeling to industrial
manufacturing". The city follows that workflow from South to North:

1. **10^-10 m (Ångström)**: `AI-ENABLED MATERIALS MODELLING` (MLIPs, universal potentials, FAIR DFT data)
2. **10^-9 m (Unit cell → macromolecule)**: `INTELLIGENT MATERIALS DESIGN` (diffusion inverse design, GNoME, polymers)
3. **10^-9 – 10^-6 m**: `DATA-DRIVEN MATERIALS CHARACTERISATION` (4D-STEM, APT, beamline edge AI)
4. **10^-3 – 10^-1 m (Droplet → bench)**: `CLOSED-LOOP EXPERIMENT ACCELERATION` (SDLs, MAPs, BIG-MAP)
5. **mg → kg → Fab**: `AI FOR RESPONSIBLE & SCALABLE PRODUCTION` (AP-Lab, AM digital twins, SSbD/PFAS)

**Spire height = maturity as graded by the report** (routine > specialist > emerging/PoC). Contested claims sit
at the bottom of their band, so MatterGen (novelty contested) and A-Lab (phase identification questioned) are
deliberately short, while the NOMAD/FAIRmat/AiiDA stack is the tallest tower in the city.

### Included Entities
- **15 Spires**: NOMAD·FAIRmat·AiiDA, Alexandria/sAlex25, Universal MLIPs, GNoME, MatterGen/FlowLLM, Polymer design,
  4D-STEM vision, APT ML, Beamline edge AI, A-Lab & Level-4 SDLs, BIG-MAP, Microfluidic SDLs/AlphaFlow,
  AP-Lab & DAPs, AM Digital Twin, SSbD/PFAS toolkit.
- **8 Bottlenecks**: Dark data, OOD fragility, Novelty mirage (GNoME 80–84% disorder, MatterGen TaCr₂O₆),
  Vendor lock-in, 232-min GC / ~3.9% robot exceptions, Middleware silos (OPC-UA/LADS), Lab-to-fab gap,
  Synthetic data fraud (MAIF).
- **7 Priorities**: meV polymorph accuracy, Sim-to-real, Activity cliffs, Regulatory pacing problem,
  Sovereign foundation models (GenAI4EU), Level-5 autonomy, Federated cloud labs.
- **10 Superhighways**: 7 northbound along the workflow, plus **3 southbound return paths** (failure logs →
  NOMAD, characterisation ground truth → MLIPs, SSbD constraints → generative design). The report asks for these
  feedback paths but describes them as largely missing.

### Compilation
```bash
python -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --web-dir docs/
```
