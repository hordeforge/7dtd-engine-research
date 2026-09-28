# Threat model: the research tooling in this repository

**Hub:** [`INDEX.md`](../INDEX.md).

**Scope:** the code this repo runs (the `tools/` CLIs, the shell scripts, the CI
workflow) and the inputs it consumes. It is not a model of the stock dedicated
server: the server's own attack surface is RE material, described in
[`protocol.md`](../network/protocol.md) and
[`webserver.md`](../admin/webserver.md).

**Last reviewed:** 2026-09-28, against `tools/` (including `tools/sandbox/`,
`tools/steam/`, `tools/parity/`, `tools/re-scratch/` and the top-level shell
entry points, `tools/release.sh` among them), `.github/workflows/ci.yml` and the
`Makefile` at that commit. Every entry below carries the file it was read
from so the next pass can re-verify it. Where a claim cannot be pinned to a
file, it is marked unknown rather than asserted.

**Not a finding list.** Point vulnerabilities and their fixes belong to the
code owners; this document records the surface, the boundaries, and where a
control exists or does not.

## Risk-ranked summary

| # | Risk | Boundary | Where | Control today |
|---|---|---|---|---|
| 1 | A downloaded or swapped build payload is executed on the operator machine | tool → third-party binary | [`tools/steam/fetch_version.sh`](../../tools/steam/fetch_version.sh), [`tools/build.sh`](../../tools/build.sh) | Mono.Cecil is sha256-pinned ([`tools/data/cecil.pin`](../../tools/data/cecil.pin), checked in [`tools/build.sh:63`](../../tools/build.sh)); the game DLL is never verified before `mcs`/`mono` run over it |
| 2 | A release publishes to the remote with the operator's `gh` token, and only the version string is validated | operator → forge | [`tools/release.sh:138`](../../tools/release.sh) | version regex ([`release.sh:49`](../../tools/release.sh)), dirty-worktree and behind-main refusals, `--dry-run` that contacts nothing, contract pinned by [`tools/tests/test_release_script.py`](../../tools/tests/test_release_script.py) |
| 3 | Crafted save/region bytes drive the parsers in `save_roundtrip_check.py` | file on disk → parser | [`tools/save_roundtrip_check.py`](../../tools/save_roundtrip_check.py) | capped inflate, bounds-checked records, fuzz + robustness gates ([`tools/tests/test_save_roundtrip_fuzz.py`](../../tools/tests/test_save_roundtrip_fuzz.py)) |
| 4 | The pin file (`tools/data/*.json`) is rewritten by a network fetch or a hostile local file | network/disk → repo state | [`tools/steam/steam_builds.py:304`](../../tools/steam/steam_builds.py), [`tools/xml_pins.py`](../../tools/xml_pins.py) | atomic tmp+rename, digest-pinned source identity; no signature over the pin files themselves |
| 5 | CI executes a shellcheck tarball fetched at run time | CI → external host | [`.github/workflows/ci.yml:58`](../../.github/workflows/ci.yml) | sha256 check before extract into a private temp dir; GitHub Actions pinned to commit SHAs; `permissions: contents: read` and `persist-credentials: false` |
| 6 | Untrusted game-supplied names become filesystem paths under the output dir | game data → filesystem | [`tools/sandbox/safe_name.py`](../../tools/sandbox/safe_name.py), [`tools/src/IlFmt.cs`](../../tools/src/IlFmt.cs) | `safe_name` strips separators and refuses `.`/`..`; enforced by [`tools/tests/test_sandbox_safe_name.py`](../../tools/tests/test_sandbox_safe_name.py) |
| 7 | A hostile Steam depot manifest or appinfo JSON exhausts memory or CPU | network/disk → tool | [`tools/steam/steam_manifest.py`](../../tools/steam/steam_manifest.py), [`tools/steam/steam_builds.py`](../../tools/steam/steam_builds.py) | size-bounded protobuf reads (fixed-width fields and varints checked against the block), an 8 MiB ceiling on the appinfo body ([`steam_builds.py:85`](../../tools/steam/steam_builds.py)), fuzz + per-call time ceiling ([`tools/tests/test_steam_manifest_fuzz.py`](../../tools/tests/test_steam_manifest_fuzz.py)); 30 s on the appinfo GET ([`steam_builds.py:201`](../../tools/steam/steam_builds.py)); no global quota on a `--verify` over a full 17 GB install |
| 8 | A hostile depot manifest steers `--verify-install` at files outside the install root, or a network-supplied gid reaches the shell as an argument | network/disk → filesystem, network → argv | [`tools/steam/steam_manifest.py:350`](../../tools/steam/steam_manifest.py), [`tools/steam/steam_builds.py:79`](../../tools/steam/steam_builds.py) | `safe_join` refuses absolute or escaping entry names and `--verify` reports them as `UNSAFE`; `GID_RE` refuses a non-numeric gid before it becomes a `fetch_version.sh` argument |
| 9 | Third-party parsers (UnityPy, dncil, dnfile, Mono.Cecil) run over game-controlled bytes with no size or depth bound | game file → dependency | [`tools/sandbox/extract_mesh_atlas.py`](../../tools/sandbox/extract_mesh_atlas.py), [`tools/sandbox/extract_sandbox_tables.py`](../../tools/sandbox/extract_sandbox_tables.py) | the requirements are hash-pinned ([`tools/sandbox/requirements.txt`](../../tools/sandbox/requirements.txt)); the in-repo parser bounds do not extend into these dependencies, and CI never runs them |
| 10 | Shell injection through operator-supplied values | operator → shell | [`tools/steam/fetch_version.sh:40`](../../tools/steam/fetch_version.sh), [`tools/release.sh:49`](../../tools/release.sh), [`Makefile`](../../Makefile) | label allowlist regex, version regex, quoted expansions, `--notes-file` passed as a filename rather than interpolated, `set -euo pipefail`, shellcheck at style severity (every level) over every tracked `.sh` |

Nothing here is internet-facing. The inbound network paths are an HTTPS GET to
`https://api.steamcmd.net/v1/info/294420` in
[`tools/steam/steam_builds.py:62`](../../tools/steam/steam_builds.py) and the
anonymous steamcmd download the operator starts through
[`tools/steam/fetch_version.sh`](../../tools/steam/fetch_version.sh); the rest of
the tooling is local, operator-invoked.

The one outbound, credentialed path is [`tools/release.sh`](../../tools/release.sh),
which pushes tags and creates a GitHub release with whatever `gh` credentials
the operator's shell already holds. It is a forge client, not a game-data
client, and it is the only place a commit in this tree reaches a remote.

## Entry points

| Entry point | Kind | Input trust | Reference |
|---|---|---|---|
| `python3 tools/*.py`, `tools/tests/*.py` CLIs | CLI argv | operator | 90 `add_argument` sites across `tools/`; usage contract gated by [`tools/tests/test_python_cli_usage.py`](../../tools/tests/test_python_cli_usage.py) and [`test_cli_args_wired.py`](../../tools/tests/test_cli_args_wired.py) |
| `tools/*.sh` | CLI argv, env | operator | [`tools/steam/fetch_version.sh`](../../tools/steam/fetch_version.sh), [`tools/build.sh`](../../tools/build.sh), [`tools/post-update.sh`](../../tools/post-update.sh), [`tools/regen.sh`](../../tools/regen.sh) |
| `tools/release.sh <version> [--notes FILE]` | CLI argv, `git` and `gh` subprocesses carrying the operator's credentials | operator | argv parsing at [`tools/release.sh:37`](../../tools/release.sh), `git push origin main` at [`release.sh:118`](../../tools/release.sh), the tag push at [`release.sh:133`](../../tools/release.sh), and `gh release create` from an operator-named notes file at [`release.sh:138`](../../tools/release.sh); the contract is pinned by [`tools/tests/test_release_script.py`](../../tools/tests/test_release_script.py) and [`tools/tests/test_release_contract.py`](../../tools/tests/test_release_contract.py) |
| `tools/parity/drift-check.sh` | CLI argv, env, writes a machine-local baseline | operator, or a cron/CI schedule | [`tools/parity/drift-check.sh`](../../tools/parity/drift-check.sh) names the cron and CI alerting use in its header; `--accept-baseline` writes the local baseline, and `STOCK_SYNC_DRIFT=1` makes [`tools/stock-sync.sh`](../../tools/stock-sync.sh) run it after an extract |
| Environment variables | config | operator | `ASM`, `SEVENDTD_ASM`, `SEVENDTD_DS_DIR`, `GAME_ROOT`, `SEVENDTD_SERVER_DIR`, `SOURCE_DATE_EPOCH`, `RE_FUZZ_SEED`, `RE_MONO_TIMEOUT`, `RE_STEAM_FETCH_TIMEOUT`, `BOUNDED_KILL_GRACE_S`, `MONO_CECIL`, `MONO_CECIL_UNVERIFIED`, `STOCK_SYNC_DRIFT`, `SCRATCH`, `OUT`, `STEAMCMD`, `STEAM_CONTENT`, `BASELINE_DIR`, `COMMITTED_BASELINE`, `PARITY_BASELINE`; the reader and default of each are tabulated in [`tools/README.md`](../../tools/README.md#environment-variables), and a gate fails when a variable the code reads is missing from that table ([`tools/tests/test_env_vars_documented.py`](../../tools/tests/test_env_vars_documented.py)) |
| `save_roundtrip_check.py` region glob | filesystem glob | game-written | [`tools/save_roundtrip_check.py:903`](../../tools/save_roundtrip_check.py) globs `*.7rg` / `*.7rr` inside the save dir the operator passes; there is no save-dir auto-discovery |
| Game install files (`Assembly-CSharp.dll`, `Data/Config/*.xml`) | file parse | third-party binary/data | [`tools/xml_pins.py:185`](../../tools/xml_pins.py) reads the raw bytes and decoded text of each config file; Mono.Cecil dumpers in [`tools/src/`](../../tools/src) read the assembly |
| Save files (`main.ttw`, `.7rg`, `.7rr`) | binary parse | untrusted (may be corrupt or crafted) | [`tools/save_roundtrip_check.py`](../../tools/save_roundtrip_check.py) |
| Steam depot manifest cache, appinfo JSON | binary/JSON parse | Steam, or a local file passed with `--manifest` / `--appinfo` | [`tools/steam/steam_manifest.py`](../../tools/steam/steam_manifest.py), [`tools/steam/steam_builds.py`](../../tools/steam/steam_builds.py) |
| `api.steamcmd.net` appinfo | HTTPS GET | remote | [`tools/steam/steam_builds.py:61`](../../tools/steam/steam_builds.py) |
| steamcmd depot download | outbound HTTPS to a Steam CDN | remote, operator-invoked | [`tools/steam/fetch_version.sh`](../../tools/steam/fetch_version.sh), bounded by [`steam_builds.py:81`](../../tools/steam/steam_builds.py) |
| Unity bundles (`.bundle`, `.unity3d`, `.resource`) and `Assembly-CSharp.dll` | third-party binary parse | game-controlled bytes through a third-party library | [`tools/sandbox/try_extract_presets.py`](../../tools/sandbox/try_extract_presets.py), [`tools/sandbox/extract_mesh_atlas.py`](../../tools/sandbox/extract_mesh_atlas.py) |
| Zig scratch dumpers | binary parse of game assets | game-controlled bytes | [`tools/re-scratch/texdump.zig`](../../tools/re-scratch/texdump.zig), [`tools/re-scratch/ttsdump.zig`](../../tools/re-scratch/ttsdump.zig); no gate runs them |
| Operator-supplied `STEAMCMD` binary | exec | operator | [`tools/steam/fetch_version.sh:88`](../../tools/steam/fetch_version.sh) |
| CI job | build → runtime | GitHub Actions, external download | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) |
| `mono` executing the repo's own compiled dumpers | build → runtime | locally built C# | [`tools/build.sh`](../../tools/build.sh) |

## Trust boundaries

1. **Operator to tool.** The operator supplies argv, env, and paths. The tools
   trust these fully; the mitigations are quoting and label validation in
   [`fetch_version.sh`](../../tools/steam/fetch_version.sh) and the usage gates.
2. **Tool to game install (build to runtime).** Game files are treated as data
   and, in the case of `Assembly-CSharp.dll`, as code to execute: the dumpers
   load it through Mono.Cecil, and `mcs`/`mono` consume it. This is the widest
   gap in the model: the game payload is not digest-checked before execution,
   only recorded afterwards in `stock_facts.json`
   (`source_identity`, see [`tools/xml_pins.py:210`](../../tools/xml_pins.py) and
   [`tools/steam/steam_builds.py:675`](../../tools/steam/steam_builds.py)).
3. **Tool to local untrusted files.** Saves, region files, depot manifests, and
   appinfo JSON are parsed defensively. This boundary has the most explicit
   hardening in the repo, described under mitigations below.
4. **Tool to network.** One HTTPS GET, no credentials, no tokens, no writes
   back into the repo from the network response except through the explicit
   `--record` path.
5. **CI to external hosts.** The lint job downloads shellcheck and verifies its
   sha256 before extracting; the docs job runs `make test-docs` only.
6. **Repo to sibling workspaces.** [`tools/cross_repo_links.py`](../../tools/cross_repo_links.py)
   and [`tools/zdtd_cite_check.py`](../../tools/zdtd_cite_check.py) read outside
   the repo when the siblings are present; the gates fail closed when they are
   absent.
7. **Repo to third-party Python libraries.** The `tools/sandbox/` extractors
   import UnityPy, dncil, and dnfile, which parse UnityFS bundles and PE
   metadata supplied by the game. Their requirements are hash-pinned
   ([`tools/sandbox/requirements.txt`](../../tools/sandbox/requirements.txt)),
   but no in-repo bound reaches inside those parsers, and no gate runs them, so
   a malformed bundle is an unmitigated parser input on the operator machine.
8. **Operator to the forge.** [`tools/release.sh`](../../tools/release.sh) is the
   only code here that runs with the operator's GitHub credentials: it pushes
   `main` and the tag, and hands an operator-named notes file to
   `gh release create`. The privilege transition is from a local, unprivileged
   analysis run to a published, publicly readable artifact, and the only
   validated input on it is the version string. The `gh` token itself is never
   read, logged, or stored by this repo; it lives wherever the operator's `gh`
   keeps it.
9. **Scheduled runs.** [`tools/parity/drift-check.sh`](../../tools/parity/drift-check.sh)
   is shaped for a cron or CI schedule and writes a machine-local baseline under
   `BASELINE_DIR` when `--accept-baseline` is passed. A scheduled run inherits
   the operator account and whatever `HOME` it gets, so the baseline path and
   the env table are the boundary, not the arguments.

## Assets

- **Research integrity.** The committed pins in `tools/data/`: `stock_facts.json`,
  `steam_builds.json`, the `cecil.pin` digest, and the committed inventories under
  `docs/inventories/`. A silently altered pin makes every downstream claim
  wrong, and the pipeline cannot tell "the game changed" from "the pin changed".
- **The game payload.** `Assembly-CSharp.dll` and the install tree. Not ours,
  and rule 1 of the repo's `AGENTS.md` forbids redistributing it; the tooling
  never copies it into the tree.
- **Operator compute and home directory.** `--verify-install` reads the whole
  17 GB install; a full `make verify` runs the C# dumpers.
- **The docs corpus** and its citations, which downstream repos consume by link.
- **No stored credentials.** Nothing in this repo reads, stores, or requires a
  token, key, or password; the Steam paths are anonymous. The one place a
  credential is *used* is [`tools/release.sh:82`](../../tools/release.sh), where
  `gh auth status` gates a release on the operator's ambient `gh` login. The
  token is never read into the repo, logged, or copied, so there is nothing here
  to rotate, and no secret-storage threat to model. What is worth protecting is
  that token, and it lives outside this tree.

## Threats by boundary

**Operator to tool (argv, env, paths)**
- Tampering / elevation: a `STEAMCMD` value or a `SCRATCH` path redirects
  execution or output to an arbitrary location. No allowlist beyond
  `-x`/label checks.
- Denial of service: `--verify-install` with no `--only` reads 17 GB; a disk-bound
  run is a plausible accidental hang. Unbounded by quota today, though every
  child process sits under a wall-clock bound that kills the process group
  ([`tools/tooling.py:415`](../../tools/tooling.py), SIGKILL of the group at
  [`tooling.py:470`](../../tools/tooling.py)).

**Third-party libraries over game bytes**
- Denial of service: a crafted `.bundle` or a hostile PE drives UnityPy or
  dncil; the in-repo caps in `save_roundtrip_check.py` and
  `steam_manifest.py` do not cover them, and these tools have no fuzz gate.
- Tampering: a swapped bundle changes the extracted tables that
  `tools/sandbox/*.json` and `atlas/*.xml` feed to sibling projects, and the
  extraction step records no digest of its input.

**Tool to game install**
- Tampering / execution: a swapped or patched `Assembly-CSharp.dll` is loaded by
  Mono.Cecil and executed under `mono` by every dump target. Mono.Cecil parses
  the metadata, so a crafted assembly is also a parser input.
- Spoofing: a different build under the same path is accepted silently; the
  digest is recorded, not enforced.
- Information disclosure: `il/` dumps may contain game IL and are git-ignored
  for that reason; `docs/` quotes only short excerpts.

**Tool to untrusted local files**
- Denial of service: a region slot that inflates gigabytes, or a file-controlled
  count driving a long walk. Addressed by [`MAX_INFLATED`](../../tools/save_roundtrip_check.py)
  and the hang-class guard in the fuzz gate.
- Tampering: malformed input is turned into check lines and a FAIL marker rather
  than a crash, so a corrupt save cannot be mistaken for a passing verification.
- Information disclosure: no path is printed from a crafted file without being
  escaped or quoted; the tools print paths they were given, not paths embedded
  in the parsed data.
- Tampering / information disclosure: a depot manifest names the files it
  describes, so a crafted `--manifest` can try to walk `--verify-install` out of
  the install root. `safe_join` is the named control at
  [`tools/steam/steam_manifest.py:350`](../../tools/steam/steam_manifest.py), and
  an escaping name is reported as `UNSAFE` rather than silently skipped. The
  check is lexical: a symlink already inside the install is the operator's own
  tree and stays readable, which is the residual.
- Tampering: an `installdir` in a hostile `appmanifest_294420.acf` would point
  `--verify-install` at an arbitrary tree. A name with a separator, a drive, or
  a bare `.`/`..` is refused outright at
  [`tools/steam/steam_builds.py:262`](../../tools/steam/steam_builds.py).

**Operator to the forge (`release.sh`)**
- Repudiation: the publish is the operator's `git` and `gh` identity, and the
  only record of what was published is the resulting tag and GitHub release.
  A run that pushed `main` and died before `gh release create` leaves a pushed
  tree with no release; `--resume` is the documented repair
  ([`tools/release.sh:68`](../../tools/release.sh)).
- Tampering: `--notes` accepts any path and its content becomes the public
  release body verbatim ([`tools/release.sh:138`](../../tools/release.sh)).
  Nothing checks the prose, only that the file exists
  ([`release.sh:51`](../../tools/release.sh)); the policy that the notes are
  reviewed is prose in [`docs/releases/release-contract.md`](../releases/release-contract.md),
  not code.
- Elevation: `--skip-gates` and `--dry-run` both cut the `make lint` /
  `make test-docs` half of the gate suite ([`tools/release.sh:94`](../../tools/release.sh)),
  so a release can reach the forge without any local gate having run. CI runs on
  the resulting push, which is after the fact.
- Spoofing: the version string is regex-checked
  ([`tools/release.sh:49`](../../tools/release.sh)), but nothing binds a version
  to the game build it documents; a tag can name any commit and the script
  refuses only an existing tag, never a wrong one.
- Information disclosure: `gh release create` publishes under the repository's
  visibility. Nothing in the tool checks that a notes file is free of the game
  excerpts and install paths that `AGENTS.md` rules 1 and 2 keep out of the
  committed tree.

**Scheduled runs (`drift-check.sh`)**
- Tampering: `--accept-baseline` overwrites the machine-local baseline, which
  then outranks the committed one for that machine. The baseline carries the
  sha256 of the assembly it came from, so a baseline that did not come from the
  assembly in hand is ignored, but nothing keeps a stale one from being accepted
  deliberately.
- Elevation: a cron entry runs the script as the operator account. `ASM`,
  `BASELINE_DIR` and the rest of the table are read from whatever environment
  the schedule supplies, and a bad value fails loud rather than scanning a
  different install.

**Tool to network**
- Spoofing / tampering: the response is TLS-protected but unauthenticated at the
  application layer. A MITM that breaks TLS can feed a fake branch table, which
  then reaches `tools/data/steam_builds.json` only through the operator's
  explicit `--record`.
- Elevation: the response also carries the depot manifest gid, and that value
  becomes an argument to `fetch_version.sh`. `GID_RE.fullmatch`
  ([`tools/steam/steam_builds.py:79`](../../tools/steam/steam_builds.py), checked
  at [`steam_builds.py:421`](../../tools/steam/steam_builds.py)) refuses
  anything non-numeric, which is what keeps a leading `-` from reading as an
  option to steamcmd.
- Denial of service: the appinfo GET is bounded by 30 s and an 8 MiB body cap
  ([`steam_builds.py:201`](../../tools/steam/steam_builds.py),
  [`steam_builds.py:85`](../../tools/steam/steam_builds.py)). The depot fetch
  that follows it is a different bound, 6 h by default and raised only by
  `RE_STEAM_FETCH_TIMEOUT` ([`steam_builds.py:81`](../../tools/steam/steam_builds.py));
  it is deliberately loose because a depot is gigabytes, so a stalled CDN holds
  the run for hours rather than minutes.

**CI**
- Tampering: a compromised release host, mitigated by the sha256 gate on the
  shellcheck tarball; the Actions themselves are SHA-pinned.
- Elevation: CI runs on `push` and `pull_request` with `GITHUB_TOKEN`
  restricted to `contents: read`
  ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)) and
  `persist-credentials: false`, so the token is neither write-capable nor left
  in `.git/config` for a step to use. No secrets are configured. Untrusted PR
  code does reach `make test-docs` on `pull_request`; it is repo-adjacent test
  code, and it runs with a read-only, unpersisted token.

## Mitigations that exist

| Control | Covers | Reference |
|---|---|---|
| sha256 pin on Mono.Cecil before use | build → runtime supply chain | [`tools/build.sh:63`](../../tools/build.sh), [`tools/cecil-pin.sh`](../../tools/cecil-pin.sh), gate [`tools/tests/test_cecil_pin.py`](../../tools/tests/test_cecil_pin.py) |
| Capped raw inflate, bounded record walks | save-parser DoS | [`tools/save_roundtrip_check.py:42`](../../tools/save_roundtrip_check.py) (cap), [`save_roundtrip_check.py:66`](../../tools/save_roundtrip_check.py) (enforcement) |
| Seeded mutation fuzzer and per-call time ceiling | parser robustness | [`tools/tests/test_save_roundtrip_fuzz.py`](../../tools/tests/test_save_roundtrip_fuzz.py) |
| Bounded varint and fixed-width protobuf reads, fail-closed on a truncated manifest | depot-manifest parser DoS and crashes | [`tools/steam/steam_manifest.py`](../../tools/steam/steam_manifest.py), gate [`tools/tests/test_steam_manifest_fuzz.py`](../../tools/tests/test_steam_manifest_fuzz.py) |
| Filename sanitisation for game/assembly-supplied names | path traversal from game data | [`tools/sandbox/safe_name.py`](../../tools/sandbox/safe_name.py), [`tools/src/IlFmt.cs`](../../tools/src/IlFmt.cs) |
| `safe_join` rejects depot entry names that are absolute or escape the verify root | `--verify-install` steered outside the install by a crafted manifest | [`tools/steam/steam_manifest.py:350`](../../tools/steam/steam_manifest.py), reported as `UNSAFE` at [`steam_manifest.py:429`](../../tools/steam/steam_manifest.py) |
| `installdir` from a Steam ACF is refused if it holds a separator, a drive, or a bare `.`/`..` | crafted `appmanifest_294420.acf` redirecting the verify root | [`tools/steam/steam_builds.py:262`](../../tools/steam/steam_builds.py) |
| `GID_RE.fullmatch` on the manifest gid before it becomes a script argument | option injection into `fetch_version.sh`/steamcmd from a network response | [`tools/steam/steam_builds.py:79`](../../tools/steam/steam_builds.py), checked at [`steam_builds.py:421`](../../tools/steam/steam_builds.py) |
| Every spawned child runs in its own process group under a wall-clock bound that kills the group | a wedged mono, mcs, or steamcmd hanging the gate that started it | [`tools/tooling.py:415`](../../tools/tooling.py), group SIGKILL at [`tooling.py:470`](../../tools/tooling.py), gate [`tools/tests/test_bounded_runs.py`](../../tools/tests/test_bounded_runs.py) |
| Hash-pinned third-party wheels for the sandbox extractors | dependency substitution in the extract path | [`tools/sandbox/requirements.txt`](../../tools/sandbox/requirements.txt) |
| Regex extraction instead of an XML parser for the pin files | XXE / entity expansion | [`tools/xml_pins.py:60`](../../tools/xml_pins.py) |
| Atomic pin writes (pid-scoped tmp file + `replace`, tmp removed on failure) | partial/corrupt pin files, residue in `tools/data/` | [`tools/steam/steam_builds.py:304`](../../tools/steam/steam_builds.py) |
| Digest-pinned source identity for every committed pin | silent pin drift | `source_identity` in [`tools/xml_pins.py:210`](../../tools/xml_pins.py) |
| SHA-1 verify of a local install against Steam's own manifest | swapped install files | [`tools/steam/steam_manifest.py`](../../tools/steam/steam_manifest.py), [`tools/tests/test_install_integrity.py`](../../tools/tests/test_install_integrity.py) |
| Quoted expansions, `set -euo pipefail`, label allowlist, version regex, shellcheck at style severity | shell injection in operator scripts | [`tools/steam/fetch_version.sh:40`](../../tools/steam/fetch_version.sh), [`tools/release.sh:49`](../../tools/release.sh), `make lint` |
| Release refusals: dirty worktree, tag already local or on origin, branch behind `origin/main`, unauthenticated `gh`, missing notes file, plus a `--dry-run` that changes nothing and consults no remote | a half-published version, a tag on the wrong tree, a release cut from a dirty tree | [`tools/release.sh:56`](../../tools/release.sh), [`release.sh:75`](../../tools/release.sh), [`release.sh:82`](../../tools/release.sh), [`release.sh:91`](../../tools/release.sh), pinned by [`tools/tests/test_release_script.py`](../../tools/tests/test_release_script.py) |
| Baseline provenance digest | a local drift baseline silently outranking the committed one for a different assembly | [`tools/parity/drift-check.sh`](../../tools/parity/drift-check.sh) (`source.sha256`), env row `BASELINE_DIR` in [`tools/README.md`](../../tools/README.md#environment-variables) |
| Read-only CI token scope, `persist-credentials: false` | token misuse from a step running untrusted PR code | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) |
| Git-ignored `il/` dumps, no DLL committed | redistribution of game assets | repo `AGENTS.md` rule 2, [`.gitignore`](../../.gitignore) |

## Gaps, ranked

1. **The game payload is executed before it is verified.** Every dump path
   loads `Assembly-CSharp.dll` into Mono.Cecil and runs the resulting
   executables under `mono`; the sha256 is recorded after the fact, in
   `stock_facts.json`, not checked against an expected value before use. This
   is the only place where a third-party binary reaches execution, and it is
   unauthenticated at the point of execution.
2. **Pin files are trusted on read.** A hostile or corrupted
   `tools/data/stock_facts.json` is compared against the live DLL only when the
   live DLL is present (`make stock-check`); the committed pin itself has no
   signature, and a commit that alters a pin and the docs that cite it is
   indistinguishable from a legitimate post-update run.
3. **No quota on the heavy reads.** `--verify-install` without `--only` and a
   full `make test` are unbounded in bytes; the wall-clock bound on a child
   process stops a hang, not a long legitimate run. A depot fetch is bounded
   only at 6 h by default.
4. **Third-party parsers run over game bytes with no bound and no gate.** The
   `tools/sandbox/` extractors hand UnityFS bundles and PE metadata to UnityPy
   and dncil; neither the in-repo caps nor the fuzz gates cover them, and
   extraction records no digest of the input it read.
5. **The published release body is unvalidated.** `release.sh` hands whatever
   `--notes` names to `gh release create`
   ([`tools/release.sh:138`](../../tools/release.sh)) and refuses only a missing
   file, and `--skip-gates` ([`release.sh:94`](../../tools/release.sh)) lets a
   release reach the forge with no local gate run. The rules that keep game IL
   and install paths out of published prose live in `AGENTS.md` and in the
   prose of [`docs/releases/release-contract.md`](../releases/release-contract.md),
   not in code.
6. **No security disclosure path.** There is no `SECURITY.md` and no documented
   route from "a problem was reported" to "a fix shipped". Reporting currently
   means an ordinary issue or a direct message to the maintainer.
7. **No audit trail for a pin rewrite.** `stock-sync` and `--record` overwrite
   committed state in place; the previous values are not retained anywhere, so a
   disputed pin change has nothing to diff against except the git history.

## Abuse cases

These are scenarios with the enabling code path named, not tests. Nothing here
was executed against a hostile target.

- **Crafted save inflates memory.** A region slot whose stored length describes
  a deflate stream far larger than the cap reaches
  [`inflate_raw_capped`](../../tools/save_roundtrip_check.py); the cap turns it
  into a check line. Without the cap the same input would allocate
  attacker-chosen memory, which is the reason the cap exists.
- **Crafted count drives a long walk.** A spawn list count is read at
  [`tools/save_roundtrip_check.py:322`](../../tools/save_roundtrip_check.py),
  where a count larger than the remaining buffer raises at
  [`save_roundtrip_check.py:325`](../../tools/save_roundtrip_check.py) rather
  than looping; the fuzzer pins the bound so a crafted count cannot stall the
  gate.
- **Crafted manifest steers the verify root.** A depot manifest whose entry name
  is `../../etc/passwd` reaches the join in
  [`tools/steam/steam_manifest.py:350`](../../tools/steam/steam_manifest.py).
  `safe_join` returns `None`, the entry is counted as `UNSAFE` at
  [`steam_manifest.py:429`](../../tools/steam/steam_manifest.py), and the run
  reports it, so the file is not read and not silently skipped.
- **Crafted gid reaches the shell as an option.** A `gid` of `-someflag` in a
  spoofed appinfo response travels to `fetch_version.sh` as argv. `GID_RE`
  at [`tools/steam/steam_builds.py:421`](../../tools/steam/steam_builds.py)
  refuses it before the fetch is built, which is the difference between a
  non-numeric build id and an option steamcmd would act on.
- **Path escape via a game-supplied name.** A name containing `..` or a
  separator reaches the join in the dumpers; `safe_name` rewrites it and pins a
  leading `_`, so a fragment can never resolve to a parent directory.
- **Fake appinfo becomes a pinned build.** A MITM or a spoofed local appinfo
  file changes the branch table, and the operator's `--record` writes it into
  `tools/data/steam_builds.json`. The subsequent `make stock-check` will then
  fail loudly against the live DLL, but the pin file itself already carries the
  wrong claim.
- **Any path is a release body.** `tools/release.sh --notes <path>` publishes
  that file verbatim through the operator's `gh` token
  ([`tools/release.sh:138`](../../tools/release.sh)). The version regex at
  [`release.sh:49`](../../tools/release.sh) constrains the tag, not the prose,
  and `--skip-gates` removes the one place a doc gate would have read the
  published text before it left the machine.
- **A stale baseline becomes the reference.** A scheduled
  `drift-check.sh --accept-baseline` run over one assembly leaves that
  machine-local baseline outranking the committed one for every later run on
  that machine. The recorded `source.sha256` only rejects a baseline taken from
  a different assembly, not one taken from a different point in time.

## Response readiness

- **Investigation trail.** A pin change is visible in git history; nothing is
  logged when a dump or gate runs, so there is no record of which inputs a
  given `stock_facts.json` was produced from beyond the recorded digests. A
  release leaves the tag and the GitHub release as its record, with no local log
  of the run that produced them.
- **Path from report to fix.** None is written down (gap 6). A fix would follow
  the ordinary commit path, with `make test-docs` in CI and `make test` locally
  when the game is installed.

## Not modelled

Owner, review cadence, and disclosure process are organizational and are left
open here on purpose. The stock dedicated server's own surface (wire protocol,
web admin, auth) is RE material, not a property of this tooling, and is
documented in [`network.md`](../network/network.md) and
[`webserver.md`](../admin/webserver.md).
