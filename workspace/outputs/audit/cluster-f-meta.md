# Cluster F audit: meta / coverage / methodology docs (V3.0.1)

**Verdict:** Every load-bearing census, surface, reachability, and experimental-delta number reproduces exactly against the DLLs; the only real issues are one overstated completeness sentence in full-surface.md, one broken documented command, and a handful of stale/unclassified minor items. No CRITICAL findings.

Audited: docs/re-methodology.md, docs/full-surface.md, docs/coverage.md, docs/closed-gaps.md, docs/residuals.md, docs/engine-limitations.md, docs/experimental-delta.md, docs/INDEX.md, README.md, AGENTS.md.

Ground truth: `ASM="/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"` (stable V3.0.1). Experimental artifact found locally: `/home/maci/.cache/zdtd-scratch/exp-Assembly-CSharp.dll` (provenance: `fetch_exp.log` in same dir; build id not independently verified, see W8).

---

## Findings

### [W1] MAJOR (overstated completeness language) — full-surface.md "Honest coverage" + "Coverage roadmap (dedicated: done)"

Claim: "**Honest coverage (dedicated codepaths complete):** every codepath a headless server executes is now hand-narrated." and "All dedicated-server codepaths are narrated".

Ground truth: the reachability pass itself is real and reproduces (see C3), but the reached set contains executed-on-server utility/plumbing code that is NOT hand-narrated. Independent cross-filter of Reach output against doc mentions:

```
mono tools/bin/Reach.exe "$ASM" scratch/reach-out.txt   # -> reached methods=28374 reached types=4516
# filter to Assembly-CSharp game types (surface-types.md), >=15 methods, grep docs/ for each name:
UNDOCUMENTED reached game type (72 methods): StringParsers
UNDOCUMENTED reached game type (58 methods): Configuration
UNDOCUMENTED reached game type (49 methods): TEFeatureAbs
UNDOCUMENTED reached game type (140 methods): DiscordManager
... (plus XUiC_*/editor/KCC types, which the doc does classify as out of scope)
```

The doc's own next paragraph (leaves "covered without a doc each") and workspace/CHANGELOG ("reachable-undocumented remainder is utility/data plumbing, framework leaves, client/editor/render, or platform residuals") contradict the literal bolded sentence: utility/data plumbing runs on a headless server and is not hand-narrated. The evidence supports "every reachable dedicated *subsystem* has a narrative; leaves enumerated; utility plumbing intentionally not narrated", not "every codepath ... hand-narrated".

Fix: reword the bolded sentence and roadmap heading to the subsystem-level claim the evidence supports (subsystems narrated, leaves enumerated, plumbing/out-of-scope enumerated only).

### [W2] MINOR (classification omission) — full-surface.md "What is NOT narrated is genuinely not a dedicated codepath"

Claim: the not-narrated remainder is fully classified (client render, audio, editor, vendored libs, native residuals).

Ground truth: `DiscordManager` (140 methods-with-body, reachable per Reach.exe output above) appears in no published doc and in none of the not-narrated categories; its "platform residual (Discord)" classification exists only in workspace/CHANGELOG (2026-07-23 reachability entry), and residuals.md does not list Discord. `mono tools/bin/DumpMethod.exe "$ASM" DiscordManager Init` shows gating on `VoiceHelpers.get_VoiceAllowed`/`PermissionsManager.IsMultiplayerAllowed`, not `IsDedicatedServer`, so "genuinely not a dedicated codepath" is asserted, not shown, for this type.

Fix: add Discord (and the utility-plumbing category) to the not-narrated enumeration in full-surface.md or to residuals.md.

### [W3] MINOR (stale number) — full-surface.md coverage ledger

Claim: "(23 new narratives this pass, 145 diagrams corpus-wide)".

Ground truth: `grep -c '```mermaid' docs/*.md docs/inventories/*.md | awk -F: '{s+=$2} END{print s}'` -> **158** (all in docs/*.md; inventories contain 0). The ledger table was updated with later docs (stealth-smell, dynamic-mesh, parties-factions) but this sentence was not; "this pass" is also dead snapshot language.

Fix: update to 158 (or drop the count) and remove "this pass" phrasing.

### [W4] MINOR (broken documented command) — re-methodology.md §5

Claim: after §0 establishes `cd tools && ./build.sh`, §5 instructs:
`mono bin/NetProtocolCensus.exe "$ASM" il/netpackages-v3.0.1/META.md`

Ground truth: reproduced failure from the tools/ cwd:

```
$ cd tools && mono bin/NetProtocolCensus.exe "$ASM" il/netpackages-v3.0.1/META.md
Unhandled Exception: System.IO.DirectoryNotFoundException ... at NetProtocolCensus.Main
```

`tools/il/` does not exist; the correct path from tools/ is `../il/netpackages-v3.0.1/META.md` (full-surface.md gets this right with `../il/...`). §5b similarly switches cwd convention (`tools/parity/...` implies repo root). The tool itself works with a valid path (verified, see C7).

Fix: prefix `../` and make the cwd convention consistent across §1-§5b.

### [W5] MINOR (wrong path) — AGENTS.md rule 4

Claim: "re-check `docs/coverage.md` census numbers with `tools/Census.exe`".

Ground truth: `ls tools/Census.exe` -> No such file or directory. The binary is `tools/bin/Census.exe` (verified working).

Fix: `tools/bin/Census.exe`.

### [W6] MINOR (UNVERIFIABLE-HERE label) — coverage.md census table

Claim: "NetPackage* types | 194 (193 wire + `NetPackageManager`); **189 in live id-map**".

Ground truth: 194 = 193 + manager is confirmed statically (see C5). The "189 in live id-map" is a runtime observation; no supporting artifact was found in this repo (`/home/maci/.cache/zdtd-scratch/assignids_dump_raw.txt` exists but contains block ids, not NetPackage names: `grep -c NetPackage` -> 0). Not marked wrong, but the doc cites no evidence path for it.

Fix: cite the runtime dump artifact that produced 189, or mark it as a live-observation pin with date.

### [W7] MINOR (polish) — residuals.md §1

Stray empty table row (`| `) after the "XML content semantics" row (line 36), rendering artifact from an earlier edit.

### [W8] MINOR (provenance caveat) — experimental-delta.md

All census/enum/wire deltas verified against `/home/maci/.cache/zdtd-scratch/exp-Assembly-CSharp.dll` (see C4/C6). The doc says "both DLLs local, git-ignored" but does not record the experimental build id/manifest at diff time; if the local artifact were re-fetched after an experimental push, the doc's numbers would silently refer to a different build. Fix: pin the steam manifest/build id in the doc header. (Not a wrong number: every checkable number matched this artifact.)

### Observation (tooling, not a doc claim)

`mono tools/bin/Reach.exe` with no args crashes with IndexOutOfRangeException instead of printing usage; usage lives only in the Reach.cs header comment.

---

## Spot-verified CONFIRMED

**C1. Stable census — all eight numbers exact** (cited in coverage.md §Census, re-methodology.md §1, full-surface.md):

```
$ mono tools/bin/Census.exe "$ASM"
TopLevelTypes                = 4401      # coverage.md, re-methodology.md: 4401 OK
MethodsWithBody (top-level)  = 43901     # 43901 OK
AllTypes (incl nested)       = 7413      # re-methodology.md, full-surface.md: 7413 OK
AllMethodsWithBody           = 53011     # full-surface.md: 53,011 OK
NetPackage* (top-level)      = 193       # excl NetPackageManager (per Census.cs); re-methodology "excl" wording correct
NetPackage* (incl nested)    = 198
WorldState.SaveLoad(Stream)  = 884       # OK
GameManager.gmUpdate IL      = 631       # OK
```

**C2. FullSurface — namespace map numbers exact** (full-surface.md):

```
$ mono tools/bin/FullSurface.exe "$ASM" <outdir>   # wrote surface-types.md (7413 types) + surface-namespaces.md
$ awk -F'|' 'NR>3 && NF>4 {n++; t+=$3; m+=$4; il+=$5} END{print n, t, m, il}' surface-namespaces.md
87 7413 53011 1734742                    # "87 namespaces", "1,734,742 IL" OK
# <global> row: 6276 types / 45222 methods / 1518349 IL  -> "6,276 / 45,222 / 1.52M" OK; 45222/53011 = 85.3% ("85% of the code") OK
```

**C3. Reachability — exact reproduction** (workspace/CHANGELOG claim; INDEX.md §F "verified complete against a call-graph reachability pass"):

```
$ mono tools/bin/Reach.exe "$ASM" reach-out.txt
reached methods=28374 reached types=4516          # claimed 28,374 / 4,516 OK
```

Honesty framing of the lens itself is accurate: re-methodology §8 calls reached-but-undocumented types "a candidate gap" (over-approximation acknowledged; devirtualization visits all overrides, so XUi/editor types appear in the reached set).

**C4. Experimental census delta — exact** (experimental-delta.md §1):

```
$ mono tools/bin/Census.exe /home/maci/.cache/zdtd-scratch/exp-Assembly-CSharp.dll
TopLevelTypes                = 4414      # 4401 -> 4414 (+13) OK
MethodsWithBody (top-level)  = 44094     # 43901 -> 44094 (+193) OK
WorldState.SaveLoad(Stream)  = 926       # 884 -> 926 OK
GameManager.gmUpdate IL      = 631       # unchanged, consistent
```

Method-signature diff (MethodList.exe on both DLLs + comm): removed stable-only = **29** (doc: "29 removed" exact); added exp-only 222 raw, consistent with the doc's "~105 new methods on existing types" after its stated compiler/Burst/new-type filtering. NetPackage type name sets identical between builds (`diff` of `NetPackage*::` prefixes) -> "No packages added/removed" CONFIRMED.

**C5. NetPackage counts** (coverage.md "194 (193 wire + NetPackageManager)", engine-limitations.md §3, residuals.md §2):
Census.cs explicitly excludes `NetPackageManager` from both counts (tools/src/Census.cs lines 23-24); `NetPackageManager` is a top-level type (surface-types.md row present), so 193 + 1 = 194 top-level. surface-types.md has 199 `NetPackage*` rows = 198 incl-nested + manager. Consistent everywhere.

**C6. Experimental wire + enum claims** (experimental-delta.md §2, §3.2, §6):

```
$ mono tools/bin/DumpMethod.exe "$ASM" NetPackageTileEntity write     # stable: u8, Vector3i, conv.u2 -> Write(UInt16), blob
$ mono tools/bin/DumpMethod.exe $EXP NetPackageTileEntity write       # exp: adds ldfld Int32 teBlockId -> Write(Int32); conv.i4 -> Write(Int32)
$ mono tools/bin/EnumList.exe $EXP enums-exp.txt
EntitlementSetEnum.HenpocalypseCosmetic=17; TwitchWatcherCosmetic=20; EnumGamePrefs.DiscordMuteDmNotifications=315; ELogType {LogOnly=0, Console=1, RemoteConsole=2}
```

All exact matches to the doc's field table and enum claims.

**C7. Tool invocations work as documented** (re-methodology.md, full-surface.md, INDEX.md Tools) except W4:
- `mono bin/Census.exe "$ASM"` from tools/ cwd: OK.
- `mono bin/DumpMethod.exe "$ASM" GameManager gmUpdate` -> header `IL=631`; 4-arg form with out-file supported (DumpMethod.cs `a[3]`): OK.
- `mono tools/bin/FullSurface.exe "$ASM" <outdir>`: OK (C2).
- `mono tools/bin/DumpAll.exe "$ASM" <outdir> GamePath` -> "dumped 18 types / 112 method bodies": namespace mode OK. (Full-run "all 7413 types" claim is conditional wording; local il/full-v3.0.1 holds only 804 .il.txt files, i.e. a partial local run, which the doc does not misrepresent.)
- `mono tools/bin/NetProtocolCensus.exe "$ASM" <valid path>`: OK, emits the channel/compress/dir/delivery/auth table.
- `mono tools/bin/EnumList.exe` / `MethodList.exe`: OK (4867 enum lines / 46941 method lines stable).
- `tools/build.sh`, `tools/tests/test_dedi_coverage_docs.py`, `tools/tests/test_re_dump_regen.py`, `tools/parity/{fetch_version.sh,parity_diff.py,ParitySurface.cs}` all exist (steamcmd fetch not exercised here).

**C8. Spot IL sizes cited in closed-gaps.md / engine-limitations.md** (via `mono tools/bin/DumpMethod.exe "$ASM" <Type> <Method>`):
`NetEntityDistributionEntry::updatePlayerList IL=509` (claimed 509); `DynamicMeshManager::Update() IL=404` (claimed 404); `GamePath.ASPPathFinder::Calculate IL=333` (claimed 333); `PlayerStealth::TickServer IL=430` (CHANGELOG: 430); `GameTimer::get_Instance` contains `ldc.r4 20; newobj GameTimer::.ctor(Single)` (claimed GameTimer(20) / 20 Hz). All exact.

**C9. INDEX.md structural integrity:**
- Every file in docs/ and docs/inventories/ (61 besides INDEX) is referenced in INDEX.md (scripted basename check: zero misses).
- Zero dead links in INDEX.md, including cross-repo relative links (`../../7dtd-server-optimizer/docs/*`, `../../zdtd-server/docs/zig-clone.md` all resolve on disk).
- Inventory leaf counts cited in INDEX (65 block / 38 item-action / 71 minevent / 38 quest-objective / 43 sequence-requirement / 186 commands) each match the row count and self-declared header of the corresponding inventories/ file.

**C10. Honesty framing spot-checks that hold:** re-methodology §6 explicitly forbids stating cost percentages as "measured" from IL; full-surface.md states the two hard limits (redistribution, effort) instead of claiming transcription; residuals.md restricts itself to non-IL reasons and its "closed" claims each point at a family doc; coverage.md family table carries residual tails inline (row 6, row 11) rather than claiming clean closure.

## Sources
- Stable DLL: /home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll
- Experimental DLL artifact: /home/maci/.cache/zdtd-scratch/exp-Assembly-CSharp.dll
- Tools: /home/maci/Desktop/7dtd/7dtd-engine-research/tools/bin/{Census,FullSurface,Reach,DumpMethod,DumpAll,NetProtocolCensus,EnumList,MethodList}.exe
- Reach source: /home/maci/Desktop/7dtd/7dtd-engine-research/tools/src/Reach.cs
- Reachability cross-filter artifacts: scratchpad reach-out.txt, surface/, m-stable.txt, m-exp.txt
