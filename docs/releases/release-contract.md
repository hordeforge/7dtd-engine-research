# Releasing 7dtd-engine-research (tag series, what each version means)

**Hub:** [`INDEX.md`](../INDEX.md). **Corpus pin:** V **3.3.0 (b18)**
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
| Corpus | `v3.Y.0` | The studied game build. `v3.1.0` is the corpus for game V3.1.0 b14, `v3.2.0` for V3.2.0 b10, `v3.3.0` for V3.3.0 b18. | A TFP update that the corpus is re-pinned to (`make post-update`, then a new `changelog-<game-version>.md`) |
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
| `v3.3.0` | 2026-10-25 | `docs: add the v3.3.0 release notes` (corpus V3.3.0 b18) |
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

**10 commits after `v3.3.0` (2026-10-25) as of 2026-10-25.** The retarget this
section used to describe is published under the tag and in
[`release-v3.3.0.md`](release-v3.3.0.md); what follows is post-cut bookkeeping.

- The tag history row for `v3.3.0`, the corpus pin in this file's header, and
  the reset of this section land after the cut, so the release notes stay the
  record of what shipped and this file stays the contract for what comes next.
- [`../gameplay/items.md`](../gameplay/items.md) records that no block item is
  authored in `items.xml`: a block item is constructed from `Block.list`, so the
  id links them, not a shared name.
- [`../world/blocks.md`](../world/blocks.md) records the face order of a
  multi-value `Texture` property: top, bottom, north, west, south, east, with
  rotation permuting the four sides and an out-of-range index falling back to
  the first id.
- [`../world/texture-atlas.md`](../world/texture-atlas.md) gained §4: the block
  atlas images (nine 407-layer `Texture2DArray` objects, the five families that
  are single 2D atlases instead), the opaque tile space, and the per-file rect
  shapes.
- The tile packing in that section is now verified rather than inferred: the
  four slices of a 2x2 entry join with a mean difference of 6 to 8 against 62
  at the next texture, and the order is row-major. Its face-to-slice rule is
  decoded too (`ComputeTaIndexOffsFor`: `index + uIdx + vIdx * baseW`, V flipped
  unconditionally), which agrees with the measured layout. The count in this
  section is corrected with it, since the previous change left it one behind.

The next cut is `v0.4.0` (tooling) unless the corpus is re-pinned to a new game
build first, which would be `v3.4.0`.

## Cutting a release

`tools/release.sh <vX.Y.Z> [--notes FILE] [--dry-run] [--skip-gates] [--resume]`. It
refuses a dirty worktree, a tag that exists locally or on origin, a branch behind
`origin/main`, an unauthenticated `gh` and a missing notes file; it runs the
DLL-free gates (`make lint`, `make test-docs`) before tagging (`--skip-gates`
skips both, and a dry run skips them too, since it changes nothing), then pushes
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

The count is checked only while commits are unreleased. The tag push is the
moment `git rev-list --count <last-tag>..HEAD` returns 0, and the section still
describes the cut that has just happened until the next edit resets it; failing
there would turn every release's own CI run red over prose nobody reads in
between, which is how `v0.3.0` ended up tagged, unreleased and deleted. The
gate takes `--contract` and `--repo`, and
`tests/test_release_contract_gate.py` runs every one of its detectors, this
case included, in a throwaway repository. `make release-count` prints the
number the section must carry, so the count is written before CI reads it
rather than after.

**Hub:** [`INDEX.md`](../INDEX.md).
