# Showcase: MIND-MATTER Cyber-Physical Roadmap

This showcase demonstrates how **Metropolis-Kit** transforms a DeepTech research project or grant proposal (e.g. ARIA / Horizon Europe) into an interactive 3D metropolis.

### Spatial Metaphor: The Horizon River of Time
- **Axis**: Progressing from fundamental physical mechanism verification (M1) to full wafer-scale CMOS integration (D3).
- **Districts**: Solid-State Physics, Autonomous AI Scientist, In-Memory Computing, 2D Heterostructures, and Wafer Foundry.
- **Bottlenecks**: Demonstrates physical rate-limiters:
  - *The Physical World Rate-Limiter*: Human fab scheduling bottlenecks.
  - *Sparse & Uneven Data*: Missing orthogonal axes in physical parameter space.
  - *Irreversible Metadata Loss*: Unrecorded geometry destroying measurement value.

### Compilation
```bash
python -m cli.compiler --spec examples/mind-matter/02-city-spec.json --web-dir dist/
```
