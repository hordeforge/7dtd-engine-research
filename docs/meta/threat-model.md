# Threat model: the research tooling in this repository

**Hub:** [`INDEX.md`](../INDEX.md).

**Scope:** the code this repo runs (the `tools/` CLIs, the shell scripts, the CI
workflow) and the inputs it consumes. It is not a model of the stock dedicated
server: the server's own attack surface is RE material, described in
[`protocol.md`](../network/protocol.md) and
[`webserver.md`](../admin/webserver.md).

**Last reviewed:** 2026-09-28, against `tools/` (including `tools/sandbox/` and
`tools/re-scratch/`), `.github/workflows/ci.yml` and the `Makefile` at that
commit. Every entry below carries the file it was read
from so the next pass can re-verify it. Where a claim cannot be pinned to a
file, it is marked unknown rather than asserted.

**Not a finding list.** Point vulnerabilities and their fixes belong to the
code owners; this document records the surface, the boundaries, and where a
control exists or does not.

## Risk-ranked summary

| # | Risk | Boundary | Where | Control today |
|---|---|---|---|---|
| 1 | A downloaded or swapped build payload is executed on the operator machine | tool → third-party binary | [`tools/steam/fetch_version.sh`](../../tools/steam/fetch_version.sh), [`tools/build.sh`](../../tools/build.sh) | Mono.Cecil is sha256-pinned ([`tools/data/cecil.pin`](../../tools/data/cecil.pin), checked in [`tools/build.sh:33`](../../tools/build.sh)); the game DLL is never verified before `mcs`/`mono` run over it |
| 2 | Crafted save/region bytes drive the parsers in `save_roundtrip_check.py` | file on disk → parser | [`tools/save_roundtrip_check.py`](../../tools/save_roundtrip_check.py) | capped inflate, bounds-checked records, fuzz + robustness gates ([`tools/tests/test_save_roundtrip_fuzz.py`](../../tools/tests/test_save_roundtrip_fuzz.py)) |
| 3 | The pin file (`tools/data/*.json`) is rewritten by a network fetch or a hostile local file | network/disk → repo state | [`tools/steam/steam_builds.py:249`](../../tools/steam/steam_builds.py), [`tools/xml_pins.py`](../../tools/xml_pins.py) | atomic tmp+rename, digest-pinned source identity; no signature over the pin files themselves |
| 4 | CI executes a shellcheck tarball fetched at run time | CI → external host | [`.github/workflows/ci.yml:37`](../../.github/workflows/ci.yml) | sha256 check before extract; GitHub Actions pinned to commit SHAs |
| 5 | Untrusted game-supplied names become filesystem paths under the output dir | game data → filesystem | [`tools/sandbox/safe_name.py`](../../tools/sandbox/safe_name.py), [`tools/src/IlFmt.cs`](../../tools/src/IlFmt.cs) | `safe_name` strips separators and refuses `.`/`..`; enforced by [`tools/tests/test_sandbox_safe_name.py`](../../tools/tests/test_sandbox_safe_name.py) |
| 6 | A hostile Steam depot manifest or appinfo JSON exhausts memory or CPU | network/disk → tool | [`tools/steam/steam_manifest.py`](../../tools/steam/steam_manifest.py), [`tools/steam/steam_builds.py`](../../tools/steam/steam_builds.py) | size-bounded protobuf reads (fixed-width fields and varints checked against the block), fuzz + per-call time ceiling ([`tools/tests/test_steam_manifest_fuzz.py`](../../tools/tests/test_steam_manifest_fuzz.py)); 30 s on the appinfo GET ([`steam_builds.py:169`](../../tools/steam/steam_builds.py)); no global quota on a `--verify` over a full 17 GB install |
| 7 | A hostile depot manifest steers `--verify-install` at files outside the install root, or a network-supplied gid reaches the shell as an argument | network/disk → filesystem, network → argv | [`tools/steam/steam_manifest.py:338`](../../tools/steam/steam_manifest.py), [`tools/steam/steam_builds.py:78`](../../tools/steam/steam_builds.py) | `safe_join` refuses absolute or escaping entry names and `--verify` reports them as `UNSAFE`; `GID_RE` refuses a non-numeric gid before it becomes a `fetch_version.sh` argument |
| 8 | Third-party parsers (UnityPy, dncil, dnfile, Mono.Cecil) run over game-controlled bytes with no size or depth bound | game file → dependency | [`tools/sandbox/extract_mesh_atlas.py`](../../tools/sandbox/extract_mesh_atlas.py), [`tools/sandbox/extract_sandbox_tables.py`](../../tools/sandbox/extract_sandbox_tables.py) | the requirements are hash-pinned ([`tools/sandbox/requirements.txt`](../../tools/sandbox/requirements.txt)); the in-repo parser bounds do not extend into these dependencies, and CI never runs them |
| 9 | Shell injection through operator-supplied values | operator → shell | [`tools/steam/fetch_version.sh:39`](../../tools/steam/fetch_version.sh), [`Makefile`](../../Makefile) | label allowlist regex, quoted expansions, `set -euo pipefail`, shellcheck at error severity |

Nothing here is internet-facing. The inbound network paths are an HTTPS GET to
`https://api.steamcmd.net/v1/info/294420` in
[`tools/steam/steam_builds.py:61`](../../tools/steam/steam_builds.py) and the
anonymous steamcmd download the operator starts through
[`tools/steam/fetch_version.sh`](../../tools/steam/fetch_version.sh); the rest of
the tooling is local, operator-invoked.

## Entry points

| Entry point | Kind | Input trust | Reference |
|---|---|---|---|
| `python3 tools/*.py`, `tools/tests/*.py` CLIs | CLI argv | operator | 87 `add_argument` sites across `tools/`; usage contract gated by [`tools/tests/test_python_cli_usage.py`](../../tools/tests/test_python_cli_usage.py) and [`test_cli_args_wired.py`](../../tools/tests/test_cli_args_wired.py) |
| `tools/*.sh` | CLI argv, env | operator | [`tools/steam/fetch_version.sh`](../../tools/steam/fetch_version.sh), [`tools/build.sh`](../../tools/build.sh), [`tools/post-update.sh`](../../tools/post-update.sh) |
| Environment variables | config | operator | `ASM`, `SEVENDTD_ASM`, `SEVENDTD_DS_DIR`, `GAME_ROOT`, `SOURCE_DATE_EPOCH`, `RE_MONO_TIMEOUT`, `RE_STEAM_FETCH_TIMEOUT`, `SCRATCH`, `OUT`, `STEAMCMD`, `STEAM_CONTENT`, `SEVENDTD_SERVER_DIR`, `MONO_PATH`; inventoried in [`tools/README.md`](../../tools/README.md#environment-variables), read in [`tools/tooling.py`](../../tools/tooling.py), [`Makefile:3`](../../Makefile) |
| `save_roundtrip_check.py` region glob | filesystem glob | game-written | [`tools/save_roundtrip_check.py:864`](../../tools/save_roundtrip_check.py) globs `*.7rg` / `*.7rr` inside the save dir the operator passes; there is no save-dir auto-discovery |
| Game install files (`Assembly-CSharp.dll`, `Data/Config/*.xml`) | file parse | third-party binary/data | [`tools/xml_pins.py:38`](../../tools/xml_pins.py), Mono.Cecil dumpers in [`tools/src/`](../../tools/src) |
| Save files (`main.ttw`, `.7rg`, `.7rr`) | binary parse | untrusted (may be corrupt or crafted) | [`tools/save_roundtrip_check.py`](../../tools/save_roundtrip_check.py) |
| Steam depot manifest cache, appinfo JSON | binary/JSON parse | Steam, or a local file passed with `--manifest` / `--appinfo` | [`tools/steam/steam_manifest.py`](../../tools/steam/steam_manifest.py), [`tools/steam/steam_builds.py`](../../tools/steam/steam_builds.py) |
| `api.steamcmd.net` appinfo | HTTPS GET | remote | [`tools/steam/steam_builds.py:61`](../../tools/steam/steam_builds.py) |
| steamcmd depot download | outbound HTTPS to a Steam CDN | remote, operator-invoked | [`tools/steam/fetch_version.sh`](../../tools/steam/fetch_version.sh), bounded by [`steam_builds.py:332`](../../tools/steam/steam_builds.py) |
| Unity bundles (`.bundle`, `.unity3d`, `.resource`) and `Assembly-CSharp.dll` | third-party binary parse | game-controlled bytes through a third-party library | [`tools/sandbox/try_extract_presets.py`](../../tools/sandbox/try_extract_presets.py), [`tools/sandbox/extract_mesh_atlas.py`](../../tools/sandbox/extract_mesh_atlas.py) |
| Zig scratch dumpers | binary parse of game assets | game-controlled bytes | [`tools/re-scratch/texdump.zig`](../../tools/re-scratch/texdump.zig), [`tools/re-scratch/ttsdump.zig`](../../tools/re-scratch/ttsdump.zig); no gate runs them |
| Operator-supplied `STEAMCMD` binary | exec | operator | [`tools/steam/fetch_version.sh:84`](../../tools/steam/fetch_version.sh) |
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
   (`source_identity`, see [`tools/xml_pins.py:169`](../../tools/xml_pins.py) and
   [`tools/steam/steam_builds.py:601`](../../tools/steam/steam_builds.py)).
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
- **No credentials.** Nothing in this repo reads, stores, or requires a token,
  key, or password; the Steam paths are anonymous. There is nothing to rotate,
  and no secret-storage threat to model.

## Threats by boundary

**Operator to tool (argv, env, paths)**
- Tampering / elevation: a `STEAMCMD` value or a `SCRATCH` path redirects
  execution or output to an arbitrary location. No allowlist beyond
  `-x`/label checks.
- Denial of service: `--verify-install` with no `--only` reads 17 GB; a disk-bound
  run is a plausible accidental hang. Unbounded by quota today, though every
  child process sits under a wall-clock bound that kills the process group
  ([`tools/tooling.py:31`](../../tools/tooling.py)).

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
  [`tools/steam/steam_manifest.py:338`](../../tools/steam/steam_manifest.py), and
  an escaping name is reported as `UNSAFE` rather than silently skipped. The
  check is lexical: a symlink already inside the install is the operator's own
  tree and stays readable, which is the residual.
- Tampering: an `installdir` in a hostile `appmanifest_294420.acf` would point
  `--verify-install` at an arbitrary tree. A name with a separator, a drive, or
  a bare `.`/`..` is refused outright at
  [`tools/steam/steam_builds.py:205`](../../tools/steam/steam_builds.py).

**Tool to network**
- Spoofing / tampering: the response is TLS-protected but unauthenticated at the
  application layer. A MITM that breaks TLS can feed a fake branch table, which
  then reaches `tools/data/steam_builds.json` only through the operator's
  explicit `--record`.
- Elevation: the response also carries the depot manifest gid, and that value
  becomes an argument to `fetch_version.sh`. `GID_RE.fullmatch`
  ([`tools/steam/steam_builds.py:78`](../../tools/steam/steam_builds.py)) refuses
  anything non-numeric, which is what keeps a leading `-` from reading as an
  option to steamcmd.
- Denial of service: the appinfo GET is bounded by 30 s at
  [`steam_builds.py:169`](../../tools/steam/steam_builds.py). The depot fetch
  that follows it is a different bound, 6 h by default and raised only by
  `RE_STEAM_FETCH_TIMEOUT` ([`steam_builds.py:332`](../../tools/steam/steam_builds.py));
  it is deliberately loose because a depot is gigabytes, so a stalled CDN holds
  the run for hours rather than minutes.

**CI**
- Tampering: a compromised release host, mitigated by the sha256 gate on the
  shellcheck tarball; the Actions themselves are SHA-pinned.
- Elevation: CI runs with the default token and no secrets on `push` and
  `pull_request`. Untrusted PR code does reach `make test-docs` on
  `pull_request`; it is repo-adjacent test code, not a fork-publishable secret
  path.

## Mitigations that exist

| Control | Covers | Reference |
|---|---|---|
| sha256 pin on Mono.Cecil before use | build → runtime supply chain | [`tools/build.sh:33`](../../tools/build.sh), [`tools/cecil-pin.sh`](../../tools/cecil-pin.sh), gate [`tools/tests/test_cecil_pin.py`](../../tools/tests/test_cecil_pin.py) |
| Capped raw inflate, bounded record walks | save-parser DoS | [`tools/save_roundtrip_check.py:41`](../../tools/save_roundtrip_check.py) |
| Seeded mutation fuzzer and per-call time ceiling | parser robustness | [`tools/tests/test_save_roundtrip_fuzz.py`](../../tools/tests/test_save_roundtrip_fuzz.py) |
| Bounded varint and fixed-width protobuf reads, fail-closed on a truncated manifest | depot-manifest parser DoS and crashes | [`tools/steam/steam_manifest.py`](../../tools/steam/steam_manifest.py), gate [`tools/tests/test_steam_manifest_fuzz.py`](../../tools/tests/test_steam_manifest_fuzz.py) |
| Filename sanitisation for game/assembly-supplied names | path traversal from game data | [`tools/sandbox/safe_name.py`](../../tools/sandbox/safe_name.py), [`tools/src/IlFmt.cs`](../../tools/src/IlFmt.cs) |
| `safe_join` rejects depot entry names that are absolute or escape the verify root | `--verify-install` steered outside the install by a crafted manifest | [`tools/steam/steam_manifest.py:338`](../../tools/steam/steam_manifest.py), reported as `UNSAFE` at [`steam_manifest.py:423`](../../tools/steam/steam_manifest.py) |
| `installdir` from a Steam ACF is refused if it holds a separator, a drive, or a bare `.`/`..` | crafted `appmanifest_294420.acf` redirecting the verify root | [`tools/steam/steam_builds.py:205`](../../tools/steam/steam_builds.py) |
| `GID_RE.fullmatch` on the manifest gid before it becomes a script argument | option injection into `fetch_version.sh`/steamcmd from a network response | [`tools/steam/steam_builds.py:78`](../../tools/steam/steam_builds.py), checked at [`steam_builds.py:728`](../../tools/steam/steam_builds.py) |
| Every spawned child runs in its own process group under a wall-clock bound that kills the group | a wedged mono, mcs, or steamcmd hanging the gate that started it | [`tools/tooling.py:31`](../../tools/tooling.py), [`tools/tooling.py:223`](../../tools/tooling.py), gate [`tools/tests/test_bounded_runs.py`](../../tools/tests/test_bounded_runs.py) |
| Hash-pinned third-party wheels for the sandbox extractors | dependency substitution in the extract path | [`tools/sandbox/requirements.txt`](../../tools/sandbox/requirements.txt) |
| Regex extraction instead of an XML parser for the pin files | XXE / entity expansion | [`tools/xml_pins.py:39`](../../tools/xml_pins.py) |
| Atomic pin writes (tmp file + `replace`) | partial/corrupt pin files | [`tools/steam/steam_builds.py:249`](../../tools/steam/steam_builds.py) |
| Digest-pinned source identity for every committed pin | silent pin drift | `source_identity` in [`tools/xml_pins.py:169`](../../tools/xml_pins.py) |
| SHA-1 verify of a local install against Steam's own manifest | swapped install files | [`tools/steam/steam_manifest.py`](../../tools/steam/steam_manifest.py), [`tools/tests/test_install_integrity.py`](../../tools/tests/test_install_integrity.py) |
| Quoted expansions, `set -euo pipefail`, label allowlist, shellcheck error-severity | shell injection in operator scripts | [`tools/steam/fetch_version.sh:39`](../../tools/steam/fetch_version.sh), `make lint` |
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
5. **No security disclosure path.** There is no `SECURITY.md` and no documented
   route from "a problem was reported" to "a fix shipped". Reporting currently
   means an ordinary issue or a direct message to the maintainer.
6. **No audit trail for a pin rewrite.** `stock-sync` and `--record` overwrite
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
- **Crafted count drives a long walk.** A spawn list with a large count is read
  at [`tools/save_roundtrip_check.py:301`](../../tools/save_roundtrip_check.py),
  where a count larger than the remaining buffer raises rather than looping;
  the fuzzer pins the bound so a crafted count cannot stall the gate.
- **Crafted manifest steers the verify root.** A depot manifest whose entry name
  is `../../etc/passwd` reaches the join in
  [`tools/steam/steam_manifest.py:423`](../../tools/steam/steam_manifest.py).
  `safe_join` returns `None`, the entry is counted as `UNSAFE`, and the run
  reports it, so the file is not read and not silently skipped.
- **Crafted gid reaches the shell as an option.** A `gid` of `-someflag` in a
  spoofed appinfo response travels to `fetch_version.sh` as argv. `GID_RE`
  at [`tools/steam/steam_builds.py:728`](../../tools/steam/steam_builds.py)
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

## Response readiness

- **Investigation trail.** A pin change is visible in git history; nothing is
  logged when a dump or gate runs, so there is no record of which inputs a
  given `stock_facts.json` was produced from beyond the recorded digests.
- **Path from report to fix.** None is written down (gap 5). A fix would follow
  the ordinary commit path, with `make test-docs` in CI and `make test` locally
  when the game is installed.

## Not modelled

Owner, review cadence, and disclosure process are organizational and are left
open here on purpose. The stock dedicated server's own surface (wire protocol,
web admin, auth) is RE material, not a property of this tooling, and is
documented in [`network.md`](../network/network.md) and
[`webserver.md`](../admin/webserver.md).
