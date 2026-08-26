# Evidence notes: 7DTD dedicated-server RE corpus review

All commands run from `/home/maci/Desktop/7dtd/7dtd-engine-research` with
`ASM="/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"`.

**Conflict of interest:** the reviewer authored this artifact in the same session.
Every finding below was re-derived from the DLL or from disk, not recalled. An
independent `reviewer` subagent was dispatched in parallel as a counterweight; its
output is `.drafts/7dtd-re-corpus-independent-review.md`.

---

## 1. Artifact scale (measured)

| Property | Value | Command |
|---|---:|---|
| Narrative docs | 60 | `ls docs/*.md \| wc -l` |
| Inventory catalogs | 20 | `ls docs/inventories/*.md \| wc -l` |
| Total doc lines | 26,087 | `cat docs/*.md docs/inventories/*.md \| wc -l` |
| Mermaid diagrams | 176 | `grep -rc '```mermaid' docs/` |
| Maintained tools (`src/`) | 16 | `ls tools/src/*.cs` |
| Legacy dumpers | 39 | `ls tools/legacy/*.cs` |
| Tracked files | 158 | `git ls-files \| wc -l` |

## 2. Metric reproducibility: PASS (6/6 exact)

`mono tools/bin/Census.exe "$ASM"` vs the baseline table pinned in
`docs/re-methodology.md` §1:

| Metric | Tool | Doc | Match |
|---|---:|---:|:--:|
| Top-level types | 4401 | 4401 | yes |
| Methods with body (top-level) | 43901 | 43901 | yes |
| All types (incl nested) | 7413 | 7413 | yes |
| `NetPackage*` (top-level) | 193 | 193 | yes |
| `GameManager.gmUpdate` IL | 631 | 631 | yes |
| `WorldState.SaveLoad(Stream)` IL | 884 | 884 | yes |

## 3. Independent claim spot-checks (chosen to NOT overlap the subagent's set)

- **`NetPackageChunk` body** (`protocol-packages.md` §3.1). Claim: `bOverwriteExisting:bool`,
  then `if` set `chunkX/Y/Z:i16`, then `dataLen:i32`, then blob.
  `DumpMethod NetPackageChunk write` shows `ldfld bOverwriteExisting` ->
  `Write(Boolean)` -> `ldfld bOverwriteExisting` -> `brfalse.s IL_0051` -> two
  `Write(Int16)` within the guard. **CONFIRMED** (bool, conditional guard, i16s).
- **`NetPackageEncryptionPublicKey`** (`protocol-packages.md` §2). Claim:
  `ExchangePublicKeyParamsXml:string`, `Hash` as `i32 len + bytes`, `SignedHash` same.
  IL: `ldfld ExchangePublicKeyParamsXml` -> `Write(String)`; `ldfld Hash` ->
  `Write(Int32)`; `ldfld Hash` -> `Write(Byte[])`; `ldfld SignedHash` -> `Write(Int32)`.
  **CONFIRMED**, including the length-then-bytes idiom.
- **`EnumDamageTypes.Suffocation = 16`** (`combat-damage.md` §1). `EnumList` output:
  `EnumDamageTypes.Suffocation=16`. **CONFIRMED**.

## 4. Test gates: PASS

- `uv run python tools/tests/test_dedi_coverage_docs.py` ->
  `OK: dedi coverage docs + dump sets + tools present  docs_checked=11 dump_sets=8 tools=8`.
- `tools/tests/test_re_dump_regen.py` was run earlier in the session; it compiles a
  legacy dumper and regenerates non-empty inventories from the live DLL (exit 0).

## 5. External consumer check (strongest validity evidence)

The sibling `../zdtd-server-server` clone consumes these specs and must interoperate with the stock
client. `cd ../zdtd-server-server && zig build test` -> **PASS**; 11 tests in the
`EntityCreationData` module alone. This is a falsifiable external check: a wrong wire
spec would surface as a failing byte-offset assertion, not just a doc opinion.

## 6. Policy compliance: PASS

`git ls-files | grep -icE '\.(il\.txt|dll|exe)$'` -> **0**. No game IL, assemblies, or
assets are tracked. `.gitignore` covers `il/*`; `tools/.gitignore` was hardened during
the session to exclude ~46k raw dump files that were sitting under `tools/`.

## 7. Provenance quality

13 commits on `re-corpus-audit-tooling`; single human author; **0** AI-attribution
strings in commit bodies (a case-insensitive scan of `git log --format='%B'` for tool-attribution strings).

## 8. WEAKNESS (quantified): "narrated" is a shallow proxy

The headline coverage metric counts a type as **narrated** if its simple name appears
as a whole word anywhere in a non-generated doc. Measuring the actual mention-depth
distribution over type-looking names in hand-written docs (excluding the four
auto-generated bulk lists and the classified set):

| Mentions | Count | Share |
|---|---:|---:|
| exactly 1 (passing mention) | 3,939 | 48% |
| 2-4 | 2,817 | 34% |
| 5-19 | 1,102 | 13% |
| 20+ | 235 | 2% |

**Nearly half of the names counted as "narrated" appear exactly once.** A type
mentioned once in a cross-reference is scored identically to one with its own
section. The corpus *does* disclose this qualitatively ("Name-mention is an upper
bound on narration (a type named in passing counts)") but never quantifies it, so a
reader has no way to discount the headline number.

## 9. Structural checks

- Every `docs/*.md` carries the `**Owns:**` header convention (0 exceptions).
- Thinnest doc is 92 lines (`twitch-integration.md`); no trivially thin padding files.
- 0 broken intra-doc links, 0 odd code fences, 0 em/en dashes (house rule), INDEX
  registration complete (scripted check over `docs/*.md` + `docs/inventories/*.md`).

## 10. Error history (a validity signal, not a defect list)

`workspace/CHANGELOG.md` records 31 dated entries. Two independent audit passes were
run over the corpus during construction. The **second** audit, over docs that had
already been written carefully, still found **3 CRITICAL + 8 MAJOR + 13 MINOR**
errors, including a wire-breaking `EntityCreationData` tail error authored by the
same agent that had correctly analysed the same IL an hour earlier. A later pass
found a **generator/doc drift** (frame-entries dumper emitting 242 vs the audited
244) that would have silently reverted a fix on regeneration.

Reading: the error *rate* in first-draft RE prose is high enough that unaudited
claims in work of this kind should be treated as provisional. The corpus's value
rests substantially on the audit trail, not on the prose alone.

## 11. Known-blocked

- **Experimental-build delta refresh:** `experimental-delta.md` is pinned to a diff
  taken 2026-07-23. Refreshing needs `steamcmd` (not installed) plus Steam
  credentials. `which steamcmd` -> not found. **Verification: BLOCKED** (external
  dependency + user credentials, not a corpus defect). The doc labels itself
  provisional.
- **Live-runtime claims:** a small number of facts are runtime observations (e.g.
  `coverage.md`'s "189 in live id-map") that cannot be re-derived from static IL. The
  corpus marks these; they remain unverifiable in this review.
