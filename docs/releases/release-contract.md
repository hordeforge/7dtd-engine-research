# Releasing 7dtd-engine-research (tag series, what each version means)

**Hub:** [`INDEX.md`](../INDEX.md). **Corpus pin:** V **3.2.0 (b10)**
([`tools/data/stock_facts.json`](../../tools/data/stock_facts.json)).
**Not:** a game release. Nothing here describes a 7 Days to Die build; those
live in [`changelog-3.2.0.md`](changelog-3.2.0.md) and its two predecessors.

This repo has two independent jobs that used to be one release: the **corpus**
(the RE narratives, pinned to a game build) and the **tooling** (the dumpers
and gates under [`tools/`](../../tools)). The tag history carries both in one
list, so the numbers mean different things depending on which series a tag
belongs to. Read the series before choosing the next number.

## The two series

| Series | Form | What the number tracks | When it moves |
|---|---|---|---|
| Corpus | `v3.Y.0` | The studied game build. `v3.1.0` is the corpus for game V3.1.0 b14, `v3.2.0` for V3.2.0 b10. | A TFP update that the corpus is re-pinned to (`make post-update`, then a new `changelog-<game-version>.md`) |
| Tooling | `v0.Y.Z` | This repo's own tooling and docs, independent of any game build. | A tooling or corpus change that does not re-pin the corpus |

A corpus release may carry tooling changes (the `v3.2.0` cut shipped
`tools/steam/`, `research_diff.py` and the drift baselines). That does not make
a tooling release, because the number still says which game build the pins
name. When both move, the corpus series wins, because that is the number a
reader uses to check a pin against.

## Tag history

Annotated tags, newest first, with the subject of the tagged commit:

| Tag | Date | Tagged commit |
|---|---|---|
| `v3.2.0` | 2026-09-21 | `tools: split by domain and share one helper module` (corpus V3.2.0 b10) |
| `v0.2.0` | 2026-09-11 | `Merge pull request #21 from hordeforge/docs/subsystem-folders` (tooling) |
| `v0.1.2` | 2026-08-26 | `Merge pull request #16 from hordeforge/chore/agent-rules-conformance` (tooling) |
| `v3.1.0` | 2026-08-23 | `Merge pull request #2 from hordeforge/tools/cecil-pin-and-test-hardening` (corpus V3.1.0 b14) |
| `v0.1.1` | 2026-08-23 | `Release update: HordeForge branding, path updates, and documentation alignment` (tooling) |
| `v0.1.0` | 2026-08-22 | `docs: wire texture-atlas docs into hub and fix stale 6.23 count test` (tooling) |

`v0.1.0` is the earliest tag; the repo had no versioned releases before it.

### The `v0.3.0` hole

`v0.3.0` was tagged but never released: the tag's CI run was red, the stray
annotated tag that pointed at its commit was deleted on 2026-09-22, and no
GitHub release was ever published for it (`workspace/CHANGELOG.md`, entries
for 2026-09-21 and 2026-09-22). No consumer resolved a `v0.3.0`, but the number
is burned anyway: the next tooling release is **`v0.4.0`**, because reusing
`v0.3.0` would make the tag list disagree with whatever a consumer cached
while the bad tag was up. Never reuse a published tag, deleted or not; cut a
new number.

## Unreleased

**49 commits after `v3.2.0` (2026-09-21) as of 2026-09-28.** The corpus pin is
unchanged at V3.2.0 b10, so this is a tooling-series release. A 0.x series
carries breaking changes without a major bump, so the consumer-visible ones are
listed first; `tests/test_release_contract.py` fails if this section's count
falls behind the commits actually below the last tag.

### Breaking for a consumer

- **Four CLIs changed exit codes and streams.** `asm_body_diff.py` with no
  arguments printed its help to stdout and exited 0; it now exits 2 as a usage
  error, like every other tool. `assignids_dump.py` with the wrong argument
  count exited 1 with the docstring on stdout; it now exits 2 with the docstring
  on stderr (`--help` is the stdout, exit-0 path). `dump_diff.py` and
  `parity/parity_diff.py` moved their usage line from stdout to stderr, so
  `dump_diff.py a b > report` no longer writes the usage text into the report.
  Both now exit 2 on a path that is not a directory/snapshot instead of
  reporting "no drift" and exiting 0.
- **An assembly override that names no install is refused.** `ASM`,
  `SEVENDTD_ASM` and `SEVENDTD_DS_DIR` used to fall through to a probed Steam
  root when the named path held no `Assembly-CSharp.dll`, so a typo silently
  answered with a different install. They now exit 2 naming the variable. A
  working override is unchanged.
- **New environment variables**, all with defaults, so nothing has to be set:
  `RE_MONO_TIMEOUT` (900 s) bounds every spawned mono/mcs/`fetch_version.sh`
  child, `RE_STEAM_FETCH_TIMEOUT` (21600 s) bounds a `steam_builds.py --fetch`
  depot download, and `SEVENDTD_SERVER_DIR` names the install that
  `make save-roundtrip-all` reads. A non-numeric or non-positive timeout aborts
  rather than meaning "no bound".

### Fixes

- **No tool runs unbounded and no tool child is orphaned.** `tooling.run_bounded`
  is the single spawn point and `tools/bounded-run.sh` does the same for the
  shell entry points; a child that outlives its bound reports the rc and names
  itself instead of hanging a gate, and its grandchildren die with it.
- **Gates no longer pass on input they never read.** Several link, citation and
  inventory gates skipped a file they could not open, and three reported OK
  while proving nothing; a drifted or unreadable input now fails with the reason.
- **Pins stop being lost silently.** Non-finite and over-uint64 values are kept
  out of pinned data, xml pin sections come from one source, the drift baseline
  is keyed to the build it came from (an unstamped or foreign local baseline no
  longer outranks the committed pin), and the census history append is
  race-safe.
- **Reproducible output.** Artifact stamps derive from `SOURCE_DATE_EPOCH`, the
  dumper build is incremental and locale-pinned, and output names are stable, so
  a repeated build is byte-identical.
- **Install discovery works from every Steam root** a supported host has
  (Windows program files, the three Linux homes, the macOS path) through
  `tools/asm_path.py`, which is now the one resolution behind `make`'s `ASM`,
  the shell entry points and the Python tools.
- **Fuzzing and bounds.** The shader sub-program and parameter blob decoders and
  the depot-manifest parser are fuzzed; the manifest parser is bounded.
- `steam_manifest.py` orders manifest history by mtime instead of a truncated
  clock string, and the steam install-integrity verdict was restored after a
  drift.

### Tools and docs

- `tools/release.sh` cuts a release with its checks built in (clean tree, free
  tag, not behind `origin/main`, authenticated `gh`, required notes, `make lint`
  + `make test-docs` green); `--dry-run` prints the plan and changes nothing, and
  `--resume` finishes a run that stopped between steps without repeating the
  ones that landed.
- Docs: the ranged-attack delivery contract is closed (`RangedAttackTarget`
  mapped, `EAILeap` motion pinned, `Animator.StringToHash` identified as
  CRC-32 with its flush chain), the `Leap` census row is marked mapped, a
  census of stock AI task-to-class usage in the V3.2.0 data was added, coverage
  counts were re-pinned to V3.2.0, and this repo's own attack surface is
  recorded in [`../meta/threat-model.md`](../meta/threat-model.md).

The next cut is `v0.4.0` (tooling) unless the corpus is re-pinned to a new game
build first, which would be `v3.3.0`.

## Cutting a release

`tools/release.sh <vX.Y.Z> [--notes FILE] [--dry-run] [--resume]`. It refuses a dirty
worktree, a tag that exists locally or on origin, a branch behind
`origin/main`, an unauthenticated `gh` and a missing notes file; it runs the
DLL-free gates (`make lint`, `make test-docs`) before tagging, then pushes
`main`, tags annotated, pushes the tag and creates the GitHub release. CI runs
the DLL-dependent half on the push.

A run that dies between those steps leaves a half-published version, and the
refusal on an existing tag would leave it that way for good. `--resume` is the
way out: the tag must exist (locally or on origin) and name `HEAD`, the tag and
its push are skipped when they already landed, and the release is created only
when `gh release view` does not find it. Two resumes leave the same state as
one, and a tag on any other commit is refused rather than published under a live
version.

Notes are required and reviewed, not generated: the default path is
`docs/releases/release-<version>.md`, which is a different thing from the
`changelog-<game-version>.md` game digests that sit beside it. A release with
nothing to say still gets notes; the tag has to be explainable from the tree.

`make test-docs` runs before the tag, and it includes
`tests/test_release_contract.py`, so a cut is refused while this file
disagrees with the repository: a tag with no history row, a row for a tag that
no longer exists, an Unreleased section that does not count the commits below
the last tag, or a "next cut" naming a version already published. That gate is
the reason the Unreleased section above states a count instead of a date.

**Hub:** [`INDEX.md`](../INDEX.md).
