# AGENTS.md - 7dtd-engine-research

Stock-game RE for 7 Days to Die dedicated server (V3.2.0 b10). All study of shipped `Assembly-CSharp.dll` lives here: RE narratives, dump tooling, wire/protocol analysis, engine cost/loop RE. Reimplementations/mods live in siblings, linking here for RE facts (see [`hordeforge/.github` AGENTS.md](https://github.com/hordeforge/.github/blob/main/AGENTS.md) boundaries).

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
| [`docs/`](docs) | Engine RE narratives, one folder per subsystem (`meta`, `releases`, `loop`, `entities`, `world`, `network`, `admin`, `gameplay`, `content`, `social`). Hub: [`docs/INDEX.md`](docs/INDEX.md). A new narrative goes in the folder whose subsystem owns it and gets a row in the hub's subsystem map (the link gate fails on an unlinked doc). Basenames are unique corpus-wide; gates resolve a doc by name (`_common.doc()`), never by folder |
| [`docs/inventories/`](docs/inventories) | Raw method/call inventories for the narratives |
| [`docs/meta/threat-model.md`](docs/meta/threat-model.md) | The one doc here that is not stock RE: the attack surface, trust boundaries, and ranked risks of this repo's own tooling. Update it when a tool gains, loses, or moves an entry point |
| [`tools/`](tools) | **Tracked** Mono.Cecil dump tooling ([`tools/README.md`](tools/README.md)) |
| [`tools/data/`](tools/data) | Committed pins (`stock_facts.json`) |
| [`tools/tests/`](tools/tests) | Pin gate, dump-set structural tests, readiness bench |
| [`Makefile`](Makefile) | Gate entry points; `make help` is the index of every target and whether it needs the game |
| [`ruff.toml`](ruff.toml), [`mypy.ini`](mypy.ini), [`.yamllint`](.yamllint) | Static-analysis config for `make lint`; versions pinned in [`ci.yml`](.github/workflows/ci.yml) |
| `il/` | Regenerable Cecil dumps. **git-ignored** (may contain game IL); never redistribute |
| `.scratch/` | Ephemeral probes and gate temp trees (`.scratch/tmp`). **git-ignored**; never the system temp dir, which is tmpfs here |
| [`oss-tools/`](oss-tools) | Third-party server-tool/mod survey notes |
| [`workspace/`](workspace) | Research artifacts only (no product code) |
| [`workspace/outputs/`](workspace/outputs) | Audits, plans, review drafts |
| [`workspace/autoresearch/`](workspace/autoresearch) | Metric session logs (readiness bench notes) |
| [`workspace/CHANGELOG.md`](workspace/CHANGELOG.md) | Lab notebook |

## Rules

1. **Do not redistribute** game assemblies or bulk IL. `il/` dumps are regenerable, git-ignored evidence. Quote at most a few disassembly lines for commentary.
2. **Tooling is tracked, dumps are not.** RE dumpers in `tools/` (tracked); output in `il/` (git-ignored). Never commit `Assembly-CSharp.dll`.
3. **Trace every wire/RE claim to an instruction.** Each field maps to a `ldfld`/`Write` pair. Method: [`docs/meta/re-methodology.md`](docs/meta/re-methodology.md).
4. **Regenerate, do not hand-edit dumps.** After a game update run `make post-update` (stock facts + pins + drift), then `make census`; re-dump only changed families into `il/<label>/`. Commit `tools/data/stock_facts.json` and pin-site doc edits together.
5. **No em dashes; no AI attribution** in shipped text (workspace rule).
6. Mark status honestly, with the vocabulary the corpus already uses: `verified` / `inferred` / **not decoded** for IL-derived fields ([`re-methodology.md`](docs/meta/re-methodology.md) §7), `Closed` / `Partially closed` / `Permanent` for coverage rows ([`coverage.md`](docs/meta/coverage.md)). Residuals beyond IL go in [`docs/meta/residuals.md`](docs/meta/residuals.md), the only table for permanent open items.
7. **A new gate is wired in two places.** A script under `tools/tests/` must be invoked by a Makefile target *and* listed in the `tools/README.md` test table, or `test_readme_test_table.py` fails; a target without a `make help` line fails the same gate. Sibling-repo links and citations have their own targets, which no-op when the siblings are not checked out: `make cross-links` (`../*.md` links) and `make sibling-cites` (bare `doc.md` citations).

## Start here

[`docs/INDEX.md`](docs/INDEX.md) -> [`docs/meta/coverage.md`](docs/meta/coverage.md) (what is mapped) -> family narrative -> `il/` dump. For new RE, the method is in rule 3 and the dumpers in [`tools/`](tools).

Gates: the two CI jobs are `make test-docs` (no DLL needed) and `make lint` (`ruff` check + format, `mypy --strict`, `shellcheck`, `yamllint` over the tracked YAML); with the live game also `make test` and `make verify`. One gate while iterating: `make gate NAME=<gate>.py` (or `python3 tools/tests/<gate>.py`), which takes the script's own flags as `ARGS=`.

`make lint` compares the local `ruff` and `mypy` against the pins in [`ci.yml`](.github/workflows/ci.yml) and exits 2 on a mismatch, before running either. Match the pin first (`uv tool install ruff==<pin>`, `mypy==<pin>`); never edit the local version to make the gate pass.

Python tooling rules: every parameter and return annotated (`mypy --strict` is a gate, not advice); a tool takes the repo root from `tools/tooling.py` (`tooling.REPO`, a `Makefile` + `AGENTS.md` marker walk) and never counts parent directories. Gates under `tools/tests/` import `_common`, which only re-exports that module; tools never import from `tests/`. Temp trees go under `tooling.scratch_dir()` (`.scratch/tmp`).
