# 7dtd-research

Reverse-engineering research on the **7 Days to Die dedicated server** (V3.0.1):
how the stock, unmodified server is built and behaves, and its wire/file formats,
derived from the shipped `Assembly-CSharp.dll`. Produced alongside a server
performance-optimization suite; the cost/scaling **measurement** program and
optimization levers live in the companion `7dtd-optimizer/docs/`, not here (see
[`AGENTS.md`](AGENTS.md) doc scope).

Start at [`docs/INDEX.md`](docs/INDEX.md).

## Highlights

- **The dedicated game loop** ([`docs/loop.md`](docs/loop.md)):
  `UpdateTick` runs per Unity frame; the full entity-sim/replication tick is
  gated at ~20 Hz regardless of frame rate; network I/O is paced by dedicated
  threads, not frames.
- **Wire protocol, fully IL-derived** ([`docs/protocol.md`](docs/protocol.md),
  [`docs/protocol-packages.md`](docs/protocol-packages.md)): LiteNet framing, join
  sequence, per-package channel/compress/direction census, and the encryption
  handshake, every field traced to a `read`/`write` instruction.
- **Entity/AI + animator anatomy** ([`docs/entity-ai.md`](docs/entity-ai.md)):
  every zombie runs a full Unity Animator on the headless server; the per-zombie
  tick chain split by subsystem.
- **RE method + tooling** ([`docs/re-methodology.md`](docs/re-methodology.md),
  [`tools/`](tools/)): the Mono.Cecil dumpers and the dump-to-wire-layout process.
- The named bottlenecks, scaling laws, and optimization levers are cross-linked
  into the companion optimizer docs (e.g. `7dtd-optimizer/docs/bottlenecks.md`).

## Layout

```text
docs/              engine narratives (loop, entities/AI, network, protocol, ...)
docs/INDEX.md      hub: reading paths, one-home-per-topic table
docs/re-methodology.md  how to RE: toolchain, dumping, reading IL into wire layouts
docs/inventories/  raw method/call inventories backing the narratives
tools/             tracked Mono.Cecil dump tooling (build.sh + general dumpers)
oss-tools/         survey notes on third-party server tools and mods
il/                regenerable IL dump output (local only, never committed)
```

RE tooling is first-class here: [`tools/`](tools) holds the tracked Mono.Cecil
dumpers (`Census`, `DumpMethod`, `DumpType`, `DumpNetPackages`,
`NetProtocolCensus`); [`docs/re-methodology.md`](docs/re-methodology.md) documents
the method. Companion projects (the tooling and mod the research fed) are a
Harmony optimization mod, an APM/profiling suite, and a load generator; they link
back here for RE facts rather than hosting their own.

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
