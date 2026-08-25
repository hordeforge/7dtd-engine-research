# AGENTS.md - 7dtd-engine-research

Stock-game RE for 7 Days to Die dedicated server (V3.1.0). All study of shipped `Assembly-CSharp.dll` lives here: RE narratives, dump tooling, wire/protocol analysis, engine cost/loop RE. Reimplementations/mods live in siblings, linking here for RE facts (see [`hordeforge/.github` AGENTS.md](https://github.com/hordeforge/.github/blob/main/AGENTS.md) boundaries).

Workspace root: [`hordeforge/.github` MODDING_BEST_PRACTICES.md](https://github.com/hordeforge/.github/blob/main/MODDING_BEST_PRACTICES.md).

## Doc scope

A doc belongs here **iff** it describes the **stock, unmodified** dedicated server: build, behavior, and wire/file formats, derived from shipped `Assembly-CSharp.dll`. Test: *would this still be true and worth writing if no mod, optimizer, or clone existed?* If yes, it lives here. If only serving a mod/clone/product, it lives there.

**Lives here (stock RE):**
- Engine structure: frame/sim loop, gmUpdate, entity/AI tick, managers.
- Wire protocol: framing, join, package bodies, channels, encryption handshake.
- On-disk/serialization formats: chunks, regions, save/WorldState.
- World/terrain/light/water/chunk systems as implemented by stock engine.
- Stock ceilings binding *any* dedicated server (engine-limitations).
- RE method + tooling (`re-methodology.md`, `tools/`), coverage, residuals.

**Does NOT live here (route elsewhere):**
| Content | Home |
|---|---|
| Optimization levers, bottleneck-to-fix catalogs, cost/APM measurements, GC/FPS/process tuning, allocation-reduction | `7dtd-server-optimizer/docs/` (the mod that ships them) |
| Reimplementation/clone architecture and milestones | clone repo (`zdtd/`) |
| RealEarth product status, streaming lessons, product surfaces | `7dtd-realearth/docs/` |
| Load-generation, APM tool internals, server-guard, connect-mod behavior | their own repos |

Measuring/optimizing the game is not stock RE: work *about a change to* the game belongs with the tool making it. Describing stock behavior is RE and stays here. To justify a lever, put stock RE here and link from the lever doc.

## Layout

| Path | Role |
|---|---|
| [`docs/`](docs) | Engine RE narratives. Hub: [`docs/INDEX.md`](docs/INDEX.md) |
| [`docs/inventories/`](docs/inventories) | Raw method/call inventories for the narratives |
| [`tools/`](tools) | **Tracked** Mono.Cecil dump tooling ([`tools/README.md`](tools/README.md)) |
| [`tools/data/`](tools/data) | Committed pins (`stock_facts.json`) |
| [`tools/tests/`](tools/tests) | Pin gate, dump-set structural tests, readiness bench |
| `il/` | Regenerable Cecil dumps. **git-ignored** (may contain game IL); never redistribute |
| [`oss-tools/`](oss-tools) | Third-party server-tool/mod survey notes |
| [`workspace/`](workspace) | Research artifacts only (no product code) |
| [`workspace/outputs/`](workspace/outputs) | Audits, plans, review drafts |
| [`workspace/autoresearch/`](workspace/autoresearch) | Metric session logs (readiness bench notes) |
| [`workspace/CHANGELOG.md`](workspace/CHANGELOG.md) | Lab notebook |

## Rules

1. **Do not redistribute** game assemblies or bulk IL. `il/` dumps are regenerable, git-ignored evidence. Quote at most a few disassembly lines for commentary.
2. **Tooling is tracked, dumps are not.** RE dumpers in `tools/` (tracked); output in `il/` (git-ignored). Never commit `Assembly-CSharp.dll`.
3. **Trace every wire/RE claim to an instruction.** Each field maps to a `ldfld`/`Write` pair. Method: [`docs/re-methodology.md`](docs/re-methodology.md).
4. **Regenerate, do not hand-edit dumps.** After an update, re-run `tools/build.sh` + dumpers and re-check `docs/coverage.md` census via `tools/bin/Census.exe`.
5. **No em dashes; no AI attribution** in shipped text (workspace rule).
6. **Generic engine only.** RealEarth product status/lessons belong in `7dtd-realearth/docs/`, not here.
7. Mark status honestly: `verified` / `unverified` / `inferred` / `blocked`. Residuals beyond IL go in [`docs/residuals.md`](docs/residuals.md).

## Start here

[`docs/INDEX.md`](docs/INDEX.md) -> [`docs/coverage.md`](docs/coverage.md) (what is mapped) -> family narrative -> `il/` dump. For new RE: [`docs/re-methodology.md`](docs/re-methodology.md) + [`tools/`](tools).
