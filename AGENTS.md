# AGENTS.md - 7dtd-research

This repo is the **home of stock-game reverse-engineering** for the 7 Days to Die
dedicated server (V3.1.0). Everything that studies the shipped
`Assembly-CSharp.dll` lives here: RE narratives, dump tooling, wire/protocol
analysis, engine cost/loop RE. Reimplementation code and mods live in their own
sibling repos and link back here for RE facts (see
[`../AGENTS.md`](../AGENTS.md) boundaries).

Workspace root guide: [`../MODDING_BEST_PRACTICES.md`](../MODDING_BEST_PRACTICES.md).

## Doc scope (what a doc here must be)

A doc belongs in this repo **iff** it describes the **stock, unmodified**
dedicated server: how it is built, how it behaves, and what its wire/file formats
are, derived from the shipped `Assembly-CSharp.dll`. The test: *would this still be
true and worth writing if no mod, optimizer, or clone existed?* If yes, it lives
here. If it only makes sense in service of a mod/clone/product, it lives with that
project.

**Lives here (stock RE):**
- Engine structure: frame/sim loop, gmUpdate, entity/AI tick, managers.
- Wire protocol: framing, join, package bodies, channels, encryption handshake.
- On-disk/serialization formats: chunks, regions, save/WorldState.
- World/terrain/light/water/chunk systems as the stock engine implements them.
- Stock ceilings that bind *any* dedicated server (engine-limitations).
- RE method + tooling (`re-methodology.md`, `tools/`), coverage, residuals.

**Does NOT live here (route elsewhere):**
| Content | Home |
|---|---|
| Optimization levers, bottleneck-to-fix catalogs, cost/APM measurements, GC/FPS/process tuning, allocation-reduction | `7dtd-optimizer/docs/` (the mod that ships them) |
| Reimplementation / clone architecture and milestones | the clone repo (`zdtd/`) |
| RealEarth product status, streaming lessons, product surfaces | `7days-realworld/docs/` |
| Load-generation, APM tool internals, server-guard, connect-mod behavior | their own repos |

Measuring or optimizing the game is not stock RE: it is work *about a change to*
the game, and belongs with the tool that makes the change. Describing what the
stock game already does is RE and stays here. When a stock-RE doc is needed to
justify a lever, put the RE here and link to it from the lever doc.

## Layout

| Path | Role |
|---|---|
| [`docs/`](docs) | Engine RE narratives. Hub: [`docs/INDEX.md`](docs/INDEX.md) |
| [`docs/inventories/`](docs/inventories) | Raw method/call inventories backing the narratives |
| [`tools/`](tools) | **Tracked** Mono.Cecil dump tooling ([`tools/README.md`](tools/README.md)) |
| [`tools/data/`](tools/data) | Committed pins (`stock_facts.json`) |
| [`tools/tests/`](tools/tests) | Pin gate, dump-set structural tests, readiness bench |
| `il/` | Regenerable Cecil dump output. **git-ignored** (may contain game IL); never redistribute |
| [`oss-tools/`](oss-tools) | Third-party server-tool/mod survey notes |
| [`workspace/`](workspace) | Research artifacts only (not product code) |
| [`workspace/outputs/`](workspace/outputs) | Audits, plans, review drafts |
| [`workspace/autoresearch/`](workspace/autoresearch) | Metric session logs (readiness bench notes) |
| [`workspace/CHANGELOG.md`](workspace/CHANGELOG.md) | Lab notebook |

## Rules

1. **Do not redistribute** game assemblies or bulk IL. `il/` dumps are
   regenerable evidence, git-ignored. Docs quote at most a few disassembly lines
   for commentary.
2. **Tooling is tracked, dumps are not.** RE dumpers go in `tools/` (git);
   their output goes in `il/` (git-ignored). Do not commit `Assembly-CSharp.dll`.
3. **Trace every wire/RE claim to an instruction.** A documented field maps to a
   specific `ldfld`/`Write` pair. Method: [`docs/re-methodology.md`](docs/re-methodology.md).
4. **Regenerate, do not hand-edit dumps.** After a game update, re-run
   `tools/build.sh` + the dumpers and re-check `docs/coverage.md` census numbers
   with `tools/bin/Census.exe`.
5. **No em dashes; no AI attribution** in any shipped text (workspace rule).
6. **Generic engine only.** RealEarth product status/lessons live in
   `7days-realworld/docs/`, not here. Keep the split.
7. Mark honest status: `verified` / `unverified` / `inferred` / `blocked`.
   Residuals that IL cannot close go in [`docs/residuals.md`](docs/residuals.md).

## Start here

[`docs/INDEX.md`](docs/INDEX.md) -> [`docs/coverage.md`](docs/coverage.md) (what is
mapped) -> family narrative -> `il/` dump. To reverse something new:
[`docs/re-methodology.md`](docs/re-methodology.md) + [`tools/`](tools).
