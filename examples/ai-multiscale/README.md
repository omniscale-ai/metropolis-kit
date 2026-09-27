# Showcase: AI Multiscale Modelling Metropolis

Built from **A. Maevskiy, V. Kapitan, A. Ustyuzhanin, _"Artificial Intelligence for Multiscale
Modeling in Solid-State Physics and Chemistry: A Comprehensive Review"_,
Advanced Intelligent Systems 8 (2026) e202501219** ([doi:10.1002/aisy.202501219](https://doi.org/10.1002/aisy.202501219)).

This is the showcase for the case Metropolis-Kit was arguably built for: a review whose
entire subject **is** a scale axis. The paper's own scope statement — lowest scale is atomic,
focus is atomic-to-mesoscale, continuum left for future study — defines the corridor, so the
spatial metaphor is not imposed on the source, it is read off it.

### Spatial Metaphor: Scale Ascension Corridor

South-to-North across six districts, roughly six orders of magnitude in length and fifteen in time:

| # | District | Scale | What lives there |
| :-- | :--- | :--- | :--- |
| 1 | Electronic Structure Foundry | 10⁻¹¹ m / fs | DeepH family & xDeepH, HamGNN, differentiable DFT (D4FT, GradDFT, Jrystal), DM21/SyFES functionals |
| 2 | Interatomic Potential Works | 10⁻¹⁰ m / ps | GAP·SOAP, ACE, MTP, UF3 · NequIP, MACE, SevenNet, M3GNet, CHGNet, Allegro · SpinGNN, DeepSPIN, MagNet |
| 3 | Vibrational & Transport Exchange | 10⁻⁹ m / ps–ns | Phonax & virtual-node GNNs, e-ph SVD compression, superionic screening, thermal surrogates |
| 4 | Coarse-Graining Terraces | 10⁻⁸–10⁻⁷ m | Learned CG force fields, quasicontinuum & Gaussian Phase Packets, RSMI-NE and multiscale structural complexity |
| 5 | Emergent Order Mesoscale | 10⁻⁷–10⁻⁵ m | Chiral domain dynamics, phase-transition cartography, ConvLSTM/GNN fracture and stress fields |
| 6 | Continuum & Autonomous Discovery | 10⁻⁵ m → device | LixCoO₂ four-scale pipeline, MOFDiff/MOFFlow/MSAIGNN, self-driving labs and battery digital twins |

### Design Choices Worth Noting

- **Spire height = scale-bridging reach**, weighted by the accuracy at which the reach is
  demonstrated — not citation count and not speedup. The tallest spires are therefore the
  universal equivariant potentials and the DeepH family, both of which carry information
  across three-plus orders of magnitude at sub-meV or few-meV/atom fidelity.
- **Conduits are the argument.** Twelve superhighways run northbound, and exactly one —
  `HW-13`, the Active-Learning Return Conduit — runs back south. That asymmetry is the
  review's Section 5.1 finding rendered as geometry: almost every implementation surveyed is
  hierarchical, with very limited bidirectional exchange.
- **Bottlenecks are drawn from the per-task "Challenges and Future Outlook" subsections**
  rather than only Section 5, so each district carries the specific failure mode of its own
  methods (benchmark-only validation, transferability beyond the training basin, long-range
  blindness in phonon prediction, bead-mapping vs crystalline symmetry, one-way coupling,
  computational-only ground truth).
- **Strategic priorities encode Table 1's taxonomy** of physics-informed strategies and the
  Section 5 future directions, one per district.
- **Datasets and benchmarks** (Section 3.3 — JARVIS-DFT, MatNavi, MDF, NOMAD, Materials
  Project, MatPES, OQMD, AFLOW, Matbench Discovery/WBM, MD17, QH9, CoRE MOF, BW-DB, ICSD)
  ride in each district's `eu_infrastructures` slot, attached to the scale they anchor.

### Compilation

```bash
# Validate only
python -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --validate-only

# Compile and launch the viewer
python -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --web-dir dist/ --serve 8080
```

Output: 6 districts · 18 spires (90 3D tiers) · 13 superhighways · 6 bottlenecks · 6 priorities.
