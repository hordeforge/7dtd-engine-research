# 7dtd-research

Reverse-engineering research on the **7 Days to Die dedicated server** (V3.0.1),
produced while building and measuring a server performance-optimization suite.
Everything here is written analysis: game-loop structure, per-system cost
anatomy, scaling measurements, and honest negative results.

Start at [`docs/INDEX.md`](docs/INDEX.md).

## Highlights

- **The dedicated game loop, measured** ([`docs/loop.md`](docs/loop.md)):
  `UpdateTick` runs per Unity frame; the full entity-sim/replication tick is
  gated at ~20 Hz regardless of frame rate; network I/O is paced by dedicated
  threads, not frames.
- **Bottleneck catalog with campaign-final attribution**
  ([`docs/bottlenecks.md`](docs/bottlenecks.md)): the tick fully attributed
  (0.4% residual), the walls named - serial entity tick, 20 Hz-locked O(N^2.26)
  replication, engine job fences.
- **Entity/AI + animator anatomy** ([`docs/entity-ai.md`](docs/entity-ai.md)):
  every zombie runs a full Unity Animator on the headless server; the per-zombie
  tick constant fully split (54% world-collision physics, 27% AI).
- **Network, protocol, GC/runtime tuning, aggressive-optimization catalog** -
  each with measurements and refutations.

Companion projects (the tooling and mod the research fed): a Harmony
optimization mod, an APM/profiling suite, and a load generator.

## Scope and legal

- **No game assets, code, or IL dumps are distributed here.** The `il/`
  directory (regenerable Mono.Cecil dump output) is excluded by `.gitignore`
  and must stay that way; docs quote at most a few disassembly lines where
  needed for commentary. Regenerate dumps locally against your own game copy.
- Unaffiliated with The Fun Pimps. "7 Days to Die" is a trademark of The Fun
  Pimps Entertainment LLC. This is independent interoperability/performance
  research on software the authors own.
- Third-party open-source mods referenced in the survey notes are not included;
  see their own repositories.

## License

Documentation is licensed [CC BY 4.0](LICENSE).
