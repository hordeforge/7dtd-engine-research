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

**96 commits after `v3.2.0` (2026-09-21) as of 2026-09-28.** The corpus pin is
unchanged at V3.2.0 b10, so this is a tooling-series release. A 0.x series
carries breaking changes without a major bump, so the consumer-visible ones are
listed first; `tests/test_release_contract.py` fails if this section's count
falls behind the commits actually below the last tag.

### Breaking for a consumer

- **Two sandbox CLIs changed exit codes and streams.**
  `sandbox/gen_zig_tables.py` and `sandbox/extract_preset_codes.py` answered a
  path they cannot open with a `FileNotFoundError` traceback on stderr and exit
  1, the same code a failed run used, so a script could not tell a bad path
  from a bad run. They now print one plain line naming the path and exit 2, the
  usage-error code every other tool uses. `extract_preset_codes.py` also moved
  its column header below the input checks, so a failed run no longer leaves a
  bare header on stdout, and `gen_zig_tables.py` grew the `main() -> int` entry
  point its sibling tools already had.
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
  depot download, `RE_FUZZ_SEED` names the seed a randomized gate replays
  from, and `SEVENDTD_SERVER_DIR` names the install that
  `make save-roundtrip-all` reads. A non-numeric or non-positive timeout aborts
  rather than meaning "no bound".
- **A branch that cannot be fetched is refused rather than attempted.**
  `steam_builds.py` forwards a branch to `steamcmd -beta <name>`, where a
  leading `-` is one of steamcmd's own options, so a branch is now held to the
  label shape and additionally to no leading `-`. A branch whose PICS entry
  carries no depot manifest gid is refused too, rather than handed to
  `fetch_version.sh` with nothing to fetch. The same two refusals apply on both
  output paths, so a branch that changes between them cannot be fetched under
  one rule and refused under the other. An unusable `RE_STEAM_FETCH_TIMEOUT`
  exits 2 with the reason, not a traceback.

### Fixes

- **No tool runs unbounded and no tool child is orphaned.** `tooling.run_bounded`
  is the single spawn point and `tools/bounded-run.sh` does the same for the
  shell entry points; a child that outlives its bound reports the rc and names
  itself instead of hanging a gate, and its grandchildren die with it (a host
  with no process group, Windows, kills the child itself).
- **A rerun republishes instead of piling up.** `research_diff.py` names its
  report after the build pair, not the date, so a repeated run of the same pair
  overwrites the report already in `workspace/outputs/diffs/` rather than adding
  a dated sibling, and the committed tree converges to one report per pair.
  `--out PATH` still writes exactly where it is told, which is how a second
  dated copy is made on purpose. `stock-sync.sh` rebuilds its inputs before
  comparing and publishes `stock_facts.json` and `xml_pins.json` as one step that
  puts the previous pair back if a move fails, so running either twice in a row
  no longer trips over its own previous output, leaves this build's facts beside
  the previous build's XML pins, or writes a half-written report over the one
  already there.
- **Two builds at once no longer race for the same staging path.** Every
  `build.sh` run stages under `bin/.staging/run.$$`, so a retried `make census`
  beside a `make drift`, or a local build while CI runs the same target, cannot
  delete the other run's staged exe and rename a half-written one into `bin/`.
- **The shell bound and the Mono lookup work on the hosts that run them.**
  `build.sh` asks the runtime for its own GAC (`gacutil`) instead of listing one
  platform's layout, and `tools/bounded-run.sh` looks for `timeout` or `gtimeout`
  and keeps the command it needs. A host with neither says so once and runs
  unbounded, rather than dropping the bound silently.
- **Gates no longer pass on input they never read.** Several link, citation and
  inventory gates skipped a file they could not open, and three reported OK
  while proving nothing; a drifted or unreadable input now fails with the reason.
- **Pins stop being lost silently.** Non-finite and over-uint64 values are kept
  out of pinned data, xml pin sections come from one source, the drift baseline
  is keyed to the build it came from (an unstamped or foreign local baseline no
  longer outranks the committed pin), and the census history append is
  race-safe. A committed pin that cannot be read, or whose top level is not an
  object, is reported as the error it is rather than degrading to "no pin".
- **Reproducible output.** Artifact stamps derive from `SOURCE_DATE_EPOCH`, the
  dumper build is incremental and locale-pinned, and output names are stable, so
  a repeated build is byte-identical.
- **`build.sh` is the only writer of `bin/`.** The shell entry points call it
  instead of compiling their own exes, and it keys each exe on the tool sources
  so a rebuilt tool is the one that runs.
- **Static analysis is tighter.** `mypy` enables the error codes strict mode
  leaves off (`ignore-without-code`, `possibly-undefined`, `redundant-expr`, and
  the rest), and `ruff` adds `ARG` and `SIM`; every code in the set is green on
  the tree, so a raise lands with the fixes that keep it green.
- **The stock pin gate is baselined.** `test_stock_facts_baseline.py` runs
  `check_stock_facts.py` against a recorded copy of the pin, so a pin that
  stops matching itself is caught without the game installed.
- **Install discovery works from every Steam root** a supported host has
  (Windows program files, the three Linux homes, the macOS path) through
  `tools/asm_path.py`, which is now the one resolution behind `make`'s `ASM`,
  the shell entry points and the Python tools.
- **Fuzzing and bounds.** The shader sub-program and parameter blob decoders and
  the depot-manifest parser are fuzzed; the manifest parser is bounded.
- **The Python tooling runs where it is claimed to.** The census history lock
  and the bounded-run timeout both had POSIX-only code paths on a host that
  documents Windows and macOS support: `census-pct.py` imported `fcntl` at
  module scope (so every gate loading it failed to import on Windows), and a
  timed-out tool reached `os.killpg` on a host that has no process groups. Both
  now degrade to the temp-and-rename and the direct-child kill they already had
  underneath, and the census lock is documented as advisory rather than
  portable.
- `steam_manifest.py` orders manifest history by mtime instead of a truncated
  clock string, and the steam install-integrity verdict was restored after a
  drift.
- **A CLI that cannot answer exits 2 instead of a clean-looking pass.**
  `cross_repo_links.py`, `mention_depth.py`, `zdtd_cite_check.py` and
  `steam_builds.py` took a range or a threshold that could name nothing, and
  reported OK over an empty input set. They now refuse the value.
- **A UTC stamp is stamped in UTC, on any host.** A `SOURCE_DATE_EPOCH` past
  year 9999 raised a bare `ValueError` from `datetime` past the `StampError`
  every caller catches, and `DumpGmUpdate.cs` rendered its `Time (UTC)` line
  through the ambient culture, so a host whose default calendar is Buddhist or
  Umm al-Qura wrote a year decades off into a line claiming to be UTC. Both are
  pinned by `tests/test_generation_stamp.py`, which now also rejects any C#
  `DateTime` format that goes through the ambient culture.
- **Pinned counts are validated at the boundary.** A negative save-format count
  and a negative pin number are rejected rather than pinned, and the stock-pin
  gate compares against a committed baseline instead of whatever the checkout
  happens to hold.
- **Writes land by rename.** The dumper build and the drift baseline write to a
  temporary name and `rename` into place, so an interrupted run cannot leave a
  half-written artifact where a gate expects a complete one.
- **The sandbox installs a bounded, reviewed requirement series**, the
  static-analysis gate is pinned to rule sets strict enough to fail on the
  defects it exists to catch, and the CI token is read-only for `contents`.
- **An unmeasured census answers with a failure, not a zero.**
  `census-pct.py` refuses `Census.exe` output that carries no
  `AllTypes (incl nested)` or `AllMethodsWithBody` row instead of reporting
  the whole assembly as empty, and an unreadable coverage report drops its
  "reached in the server call graph" row rather than printing `0`, which a
  reader cannot tell from a real measurement. `steam_manifest.py` names an
  unreadable `content_log.txt` on stderr, because the silent skip printed a
  bare gid that reads as "never pinned".
- **A hash is a hash, wherever it is taken.** The stock facts, the xml pins,
  the shader blob and the sandbox table extraction computed a content digest
  through a helper that was not pinned to an algorithm, so a different digest
  could be pinned under the same field name; `steam_builds.py` now also
  refuses a fetch whose download root resolves outside the depot it asked for.
- **Hash, install-root and fetch-guard boundaries.** A pinned SHA-256 has to be
  64 hex digits, so a corrupt pin fails instead of falling through to the
  byte-diff branch and blaming the operator's install for a damaged file; a
  relative `ASM` that resolves to the process cwd is refused rather than
  handed on as an install root; `steam_builds.py` refuses a branch or depot gid
  that reaches `steamcmd` as one of its own options, from the cache and the
  live query alike; and the post-kill read of a timed-out child is bounded, so
  a grandchild that survives the kill cannot turn the timeout back into the
  hang the bound exists to prevent.
- **Every gate-spawned child is bounded and a failed `zig fmt` is a failure.**
  `gen_atlas_zig.py` bounded its `zig` calls through the shared runner instead
  of a bare `subprocess.run`, and a non-zero `zig fmt` now stops the run rather
  than writing a file that was never formatted.
- **The app-info fetch is bounded by bytes and by scheme.** A timeout bounds
  how long the PICS request waits, not how many bytes arrive inside it, so the
  body is read one byte past an 8 MiB cap and refused past it, and a URL or
  redirect that leaves `https` is refused before the body is parsed.
- **A failing fuzz round names the seed it replays from.** Every seeded gate
  resolves its seed through `tooling.fuzz_seed` (`RE_FUZZ_SEED` overrides the
  per-gate default) and reports that seed with a digest of the corpus it
  produced, on both the OK and the FAIL line, so two runs of one seed can be
  compared by more than the seed they claim to share.
- **Superseded research moved to `workspace/outputs/archive/`.** The pre-V3.1.0
  wire snapshots, diff report and census history are kept as history, out of the
  path the drift gate reads.
- **The static-analysis gate is green again.** The fetch-bound work left
  `make lint` red on eight findings: assertions on a caught exception, a
  response factory closing over its loop variables, a `bytes` read that
  returned `Any`, and a re-exported `urllib` reaching through the tool module.
  The refusals now assert through one helper, the factory binds its loop
  values, and the gate patches `urllib.request` itself.

### Tools and docs

- **Hot paths stopped paying for the same work twice.** The shader dumper
  copies only the sub-program slice it decompresses instead of the whole
  shared compressed blob per shader, and parses each DXBC container once
  rather than walking and copying every chunk twice; the coverage report is
  opened and scanned once instead of twice; `xml_pins.py` reads each
  `Data/Config` file once for both its byte hash and its parse instead of
  streaming it for the hash and slurping it again; `blocks.xml` is read once
  rather than twice in the block dumper; the save round-trip verdict is one
  compiled scan per line instead of eleven substring searches; the
  cross-repo link sweep hoists its loop-invariant prefix and the citation gate
  resolves a nested path from the set of known `docs/` files instead of one
  `isfile` syscall per citation.
- **Gates share one argument surface.** The tests that need the game assembly
  or a mono tool call the same helpers from `tools/tests/_common.py` instead of
  each resolving them, and `tools/sandbox/requirements.in` carries a floor and
  a ceiling per package, checked against the lock, so a recompile cannot jump a
  series under a tool that reads package internals.
- **CI runs untrusted pull-request code read-only.** Both jobs declare
  `permissions: contents: read` and check out with `persist-credentials: false`,
  so a gate running fork code cannot push with the token; the shellcheck
  download goes to a private `mktemp` dir. Recorded in
  [`../meta/threat-model.md`](../meta/threat-model.md).
- `tools/release.sh` cuts a release with its checks built in (clean tree, free
  tag, not behind `origin/main`, authenticated `gh`, required notes, `make lint`
  + `make test-docs` green); `--dry-run` prints the plan and changes nothing, and
  `--resume` finishes a run that stopped between steps without repeating the
  ones that landed.
- `make lint` now also runs `yamllint` over the tracked YAML, on the version
  pinned in `.github/workflows/ci.yml`, and refuses a local `yamllint` that is
  not that pin. Config lives in [`.yamllint`](../../.yamllint).
- **A committed artifact is a function of the studied bytes.** The coverage
  report identifies its build by the assembly's sha256 rather than a file
  mtime, which changes when the same bytes are re-downloaded and made every
  regeneration read as stale; the .NET stamp is now the same
  `yyyy-MM-ddTHH:mm:ssZ` string `tools/tooling.py` formats, because the .NET
  round-trip `"o"` carried sub-second digits an integer `SOURCE_DATE_EPOCH`
  cannot reproduce; and `StockFacts.exe` emits a complete `litenet` section of
  documented defaults (every field marked baked, so the pin gate refuses to
  pin it) when the sibling assembly is missing or unreadable, so a failed
  extraction has the same object shape as a successful one and cannot read as
  an absent protocol.
- Docs: the ranged-attack delivery contract is closed (`RangedAttackTarget`
  mapped, `EAILeap` motion pinned, `Animator.StringToHash` identified as
  CRC-32 with its flush chain), the `Leap` census row is marked mapped, a
  census of stock AI task-to-class usage in the V3.2.0 data was added, coverage
  counts were re-pinned to V3.2.0, and this repo's own attack surface is
  recorded in [`../meta/threat-model.md`](../meta/threat-model.md).

The next cut is `v0.4.0` (tooling) unless the corpus is re-pinned to a new game
build first, which would be `v3.3.0`.

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
