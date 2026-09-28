# Contributing

Reverse-engineering research on the stock 7 Days to Die dedicated server, built
from the shipped `Assembly-CSharp.dll`. Read [`AGENTS.md`](AGENTS.md) first: it
holds the rules that gate every change here, and the layout map. The research
itself starts at [`docs/INDEX.md`](docs/INDEX.md); the method is
[`docs/meta/re-methodology.md`](docs/meta/re-methodology.md).

## What you need

A clone, a Python 3 interpreter, and `make`. The gates use PEP 604 unions in
runtime annotations, so 3.10 is the floor; the interpreter they are written
against is pinned in [`.python-version`](.python-version) (3.12, the one the
`mypy` config and the CI runner use). Nothing else is needed for the DLL-free
gates, which is all CI runs.

| For | You need | How to get it |
|---|---|---|
| `make test-docs` | python3 | the interpreter on `PATH` |
| `make lint` | `ruff`, `mypy`, `shellcheck`, `yamllint` | `uv tool install ruff==0.16.4`, `uv tool install mypy==2.3.1`, `uv tool install yamllint==1.38.0`; any recent `shellcheck` package |
| `make tools`, `make census`, `make test`, `make verify` | mono with `mcs`, a pinned `Mono.Cecil.dll`, the game | see below |

`make lint` refuses a `ruff`, `mypy`, or `yamllint` whose version is not the CI
pin, and prints the pin to install. Keep the local version and the pin in
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) in step: the rules drift
between releases, so an unpinned local run is not a preview of CI.

The C# dumpers need `mono` (`mcs`) and a `Mono.Cecil.dll` whose SHA-256 matches
[`tools/data/cecil.pin`](tools/data/cecil.pin); `tools/build.sh` searches the
Mono GAC and refuses a mismatch. That refusal is the supply-chain control, not a
setup problem: do not re-pin to make a build go through, read
[`tools/README.md`](tools/README.md) § Build first.

The third-party Python imports are confined to `tools/sandbox/` and
`shader_blob_dump.py`; install them hash-pinned into a venv
(`uv pip install -r tools/sandbox/requirements.txt`). Everything else under
`tools/` is stdlib only.

## The loop

```bash
make help                                  # every target, and which need the game
make gate NAME=test_doc_link_integrity.py  # one gate, while iterating on it
make test-docs                             # the full DLL-free suite (what CI runs)
make lint                                  # ruff + mypy --strict + shellcheck + yamllint
```

`make gate` takes the filename exactly as [`tools/README.md`](tools/README.md)
spells it and passes `ARGS=` to the script. A name that is not a real gate
prints the list and exits 2, so a typo never reads as a pass.

CI runs exactly `make test-docs` and `make lint`, on `ubuntu-latest` with the
analyzer versions pinned in the workflow. Those two commands are the whole
pre-push check; there is no third one.

## With a game install

Most gates and tools discover the dedicated `Assembly-CSharp.dll` themselves
through `tools/asm_path.py` (the Steam roots, then `ASM` / `SEVENDTD_ASM` /
`SEVENDTD_DS_DIR` in that order). Point them somewhere explicitly with
`ASM=/path/to/Assembly-CSharp.dll`, or `GAME_ROOT=` for the install root holding
`Data/Config`. The full table of variables is in
[`tools/README.md`](tools/README.md) § Environment variables.

```bash
make tools     # build the dumpers into tools/bin
make test      # the full suite, DLL-dependent gates included
make verify    # doc links, pins, readiness, facts, XML data
```

`make test` and `make verify` stop with a named message when no install
resolves; they do not fall through to a different build. Every gate also runs
standalone, and a gate whose prerequisite is missing says so and skips rather
than passing vacuously.

## Generated files

Four committed artifacts are produced, not hand-edited:
`docs/inventories/netpackage-bodies.md`, `docs/inventories/console-command-list.tsv`,
`docs/inventories/state-machines.md` and `docs/inventories/coverage-report.md`.
`tools/regen.sh` rebuilds the dumpers, re-dumps the `il/` sets, and refreshes
all four, ending in `make test`. The `il/` dumps themselves are git-ignored and
never committed. After a game patch the order is `make post-update`, then
`make census`, then `make regen-check`; commit the pins and the pin-site doc
edits together.

## House rules

- **No em dashes, and no AI attribution**, in any text that lands here
  ([`AGENTS.md`](AGENTS.md) rule 5). Match the surrounding voice.
- **No game assemblies or IL.** `il/` is git-ignored evidence; quote at most a
  few disassembly lines for commentary.
- **Every wire or RE claim traces to an instruction.** The method, the status
  vocabulary (`verified` / `inferred` / not decoded) and the coverage rows are
  in [`docs/meta/re-methodology.md`](docs/meta/re-methodology.md).
- **Scope is the stock, unmodified server.** A finding that only matters to a
  mod or a clone is linked to that repo, not filed here
  ([`AGENTS.md`](AGENTS.md) § Doc scope).
- A new gate is wired twice: a Makefile target runs it *and* it has a row in
  the [`tools/README.md`](tools/README.md) test table, or
  `test_readme_test_table.py` fails.

## Before you open the pull request

1. `make lint` and `make test-docs` are green.
2. A new or changed claim carries its status word and its pin sites.
3. A new gate is in the Makefile and the [`tools/README.md`](tools/README.md)
   table.
4. A user-visible change to the corpus has a bullet under **Unreleased** in
   [`docs/releases/release-contract.md`](docs/releases/release-contract.md),
   which is what the next release notes are cut from. That section also states
   how many commits sit below the last tag, and
   `test_release_contract.py` fails when that number is behind `HEAD`; every
   commit updates it, so `make release-count` prints the number to write
   before you push rather than after CI tells you.

Cut the change on a branch, not on `main`.
