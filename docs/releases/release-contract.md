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

Everything below `v3.2.0` (2026-09-21) as of 2026-09-28. Breaking for a
consumer: none. Pins are unchanged at V3.2.0 b10; the corpus delta docs were
extended, not re-pinned.

- **Docs:** the ranged-attack delivery contract is closed (`RangedAttackTarget`
  mapped, `EAILeap` motion pinned, `Animator.StringToHash` identified as
  CRC-32 with its flush chain), the `Leap` census row is marked mapped, and a
  census of stock AI task-to-class usage in the V3.2.0 data was added.
- **Tooling:** `tools/release.sh` cuts a release with its checks built in
  (clean tree, free tag, not behind `origin/main`, authenticated `gh`, required
  notes, `make lint` + `make test-docs` green); `--dry-run` prints the plan and
  changes nothing, and `--resume` finishes a run that stopped between steps
  without repeating the ones that landed. `steam_manifest.py` orders manifest
  history by mtime instead of a truncated clock string.
- **Docs:** this repo's own attack surface and ranked tooling risks are recorded
  in [`../meta/threat-model.md`](../meta/threat-model.md).

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

**Hub:** [`INDEX.md`](../INDEX.md).
