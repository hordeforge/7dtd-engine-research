# Re-audit 2: full documentation audit after restructure

**Date:** 2026-07-23. **Repo:** `/home/maci/Desktop/7dtd/7dtd-research`.
**Scope read in full:** docs/*.md (19 files incl INDEX; task premise said 20, see O1), docs/inventories/*.md (8), README.md, AGENTS.md, tools/README.md, tools/re-scratch/README.md, il/README.md, oss-tools/*.md (3). ~10,400 lines.
**Method:** every file read end-to-end; oracle numbers cross-checked in every occurrence; mechanical scans for em/en dashes, AI attribution, multiple H1s (fence-aware), unclosed fences, duplicate H2s, stale-path greps; filesystem existence checks for every cross-repo path class (`../7dtd-optimizer/docs/*`, `../zdtd/docs/zig-clone.md`, `7dtd-optimizer/tools`, `research/`, `7dtd-il`, `tools/legacy/*`).

## Severity-ranked findings table

| # | Sev | File:line | Finding |
|---|-----|-----------|---------|
| H1 | High | `docs/loop-gmupdate.md:9`, `:362` | Regen instructions point at nonexistent old tree AND a dumper tools/README declares broken. Line 9: "**Tool:** `7dtd-optimizer/tools/DumpGmUpdate.cs`"; line 362: "cd 7dtd-optimizer/tools / mcs -r:Mono.Cecil.dll -out:DumpGmUpdate.exe DumpGmUpdate.cs". `../7dtd-optimizer/tools/` does not exist (verified), and `tools/README.md:68-69` says "2 are pre-corrupted: `DumpGmUpdate`, `DumpExtra2`, use `DumpMethod`/`DumpType` instead". The doc's §10 regen recipe cannot work as written, twice over. |
| H2 | High | `il/README.md:3` | The IL policy doc attributes all dumps to the old repo: "Regenerable Mono.Cecil output from `7dtd-optimizer/tools/Dump*.cs`". Dumpers now live in `tools/src/` + `tools/legacy/` of this repo (AGENTS.md layout, tools/README.md). Contradicts AGENTS.md rule 2 ("RE dumpers go in `tools/` (git)"). |
| H3 | High | `docs/closed-gaps.md:177` | Internal contradiction: "§9 Remaining open (still) ... 4. **Region/WorldState** binary formats" vs `docs/residuals.md:49` ("WorldState.SaveLoad structure | save-region.md + dedi-complete §5" in the *closed* table), `docs/terrain-height.md:119` ("WorldState.SaveLoad managed structure | **CLOSED**, save-region (IL=884)"), and `docs/save-region.md` §1-3 which documents it. Only the sector-payload byte codec remains residual. Also conflicts with `docs/INDEX.md:130` declaring residuals.md "the only open-item list". |
| M1 | Medium | `docs/terrain-height.md:20,25-29` | Stale regen path: "Tool: `7dtd-optimizer/tools/DumpTerrain.cs`" and "cd 7dtd-optimizer/tools ... mono DumpTerrain.exe \"$ASM\" ../../7dtd-research/il/terrain-v3.0.1". Directory gone; dumper is now `tools/legacy/DumpTerrain.cs` (verified present), run via `tools/build.sh` + `bin/legacy/`. |
| M2 | Medium | `docs/entity-ai.md:383-387,649` | Stale regen paths: "cd 7dtd-optimizer/tools / mcs ... DumpDeep.cs / mono DumpDeep.exe ... ../../7dtd-il/deep-VERSION" (neither `7dtd-optimizer/tools` nor a `7dtd-il` tree exists), and line 649 "Regenerate: `tools/DumpDeeper.cs`" (actual: `tools/legacy/DumpDeeper.cs`). |
| M3 | Medium | `README.md:3-5,16-19,23-24` | Repo README scope not updated for the doc split. Line 4-5: "Everything here is written analysis: game-loop structure, per-system cost anatomy, scaling measurements..." (cost anatomy + scaling docs moved to 7dtd-optimizer). Line 17: highlight labeled "([`docs/bottlenecks.md`](../7dtd-optimizer/docs/bottlenecks.md))" - the visible label `docs/bottlenecks.md` implies a local doc that no longer exists here. Line 23: "Network, protocol, GC/runtime tuning, aggressive-optimization catalog" - the latter two catalogs are no longer in this repo. |
| M4 | Medium | `docs/re-methodology.md:183-184` | Bare prose mention of a moved doc as if local: "look for `newobj`, `newarr`, boxing, and LINQ closures in hot methods (`allocation-reuse.md`)". It is in code-span (passes link checkers) but reads as a sibling doc; it lives at `../../7dtd-optimizer/docs/allocation-reuse.md`. |
| M5 | Medium | `docs/network.md:136-147` | Unsupported quantitative claims (no artifact pointer in the section): "Where the ~15 MB/s at 128p actually comes from", "it is the **#4** allocator, not #1". The §4b correction block cites RE dates but no RESULTS/measured-scaling anchor for these two measured numbers, unlike loop.md §3 (cites RESULTS §3k) and entity-ai addendum (cites RESULTS §3m-3q). |
| M6 | Medium | `docs/network.md:144-147` | Scope: optimization-lever narrative inside a stock RE doc: "the worthwhile network levers are the send-path scan (shipped, `FastSendPatch`) and a spatial index for the O(N^2) interest all-pairs" plus the deprioritization verdict ("modest reward, real risk - deprioritized"). Per AGENTS.md doc-scope, lever selection/status belongs in `7dtd-optimizer/docs/`; the RE fact (writer-thread serialization) belongs here. |
| M7 | Medium | `docs/entity-ai.md:317-360,622-627,653-684` | Scope: §11 "Cost model (for optim / conductor)", §12 "EfficientServer / conductor hooks" (hook-to-lever table incl. "ES far skip"), §12(second) "Optim ideas derived here", and the addendum's lever/status content ("The animator-LOD lever (v1.15.0) helps only dispersed populations") are optimization-mod content in a stock doc. The measured numbers themselves are properly pointered (RESULTS §3m-3o/§3q), but lever grading/status is optimizer-owned per AGENTS.md. |
| M8 | Medium | `docs/loop-gmupdate.md:236,286,313,343-356` | Scope: EfficientServer/conductor guidance embedded in the phase narrative: line 236 "EfficientServer already targets some presentation; spawn walk is a **candidate** to scope", §9 "Implications for EfficientServer / 'conductor'" (patch-strategy table). Also line 351 bare unlinked "(see SIM_PARALLELISM §5.6.1)". |
| M9 | Medium | `docs/entity-ai.md` (structure) | Merge artifact: two complete numbered section sequences in one file - §1-§15 (lines 14-390), then "Deeper synthesis" restarting at §1-§14 (lines 399-649). Duplicate section numbers make references like "entity-ai §3" ambiguous; two see-also-style sections (§14 "See also" line 369, §14 "File map" line 642). |
| M10 | Medium | `docs/network.md:149-164` | Duplicated closing sections: "## 5. See also" (loop.md, closed-gaps.md, measured-scaling.md, entity-ai.md) immediately followed by "## Related docs" (closed-gaps.md, measured-scaling.md, loop.md) - same links twice. |
| M11 | Medium | `docs/terrain-height.md:93-105,150-171` | Duplicated closing sections ("Related research / product docs" + "See also" with overlapping rows), and a "Product inject lessons (from runtime work)" section that is RealEarth product content (self-declared "Not pure engine RE") in a generic engine doc - AGENTS.md routes product lessons to `7days-realworld/docs/`. |
| M12 | Medium | `oss-tools/naiwazi.md:118`, `oss-tools/servertools.md:4` | Stale old-structure paths: "Local copies under `research/naiwazi/`" and "**Local clone:** `research/7dtd-ServerTools`". No `research/` directory exists in or beside the repo (verified). NOTES.md:4 says clones are "not tracked here", which is the current truth; these two files still point at the pre-restructure location. |
| M13 | Medium | `docs/coverage.md:41-42` | Scope tension: coverage families 12 ("Runtime APM scale ... live APM ... Closed (measured)") and 13 ("Runtime / GC / FPS knobs") are optimizer-owned docs listed as rows of this repo's "dedicated-relevant **managed** surfaces" coverage bar (line 7). Neither is a managed surface of the DLL; INDEX cluster F explicitly exiles those docs. |
| M14 | Medium | `docs/engine-limitations.md:43,124` | Bare unlinked references to optimizer docs as evidence: line 43 evidence "loop.md, ARCHITECTURE"; line 124 evidence "runtime-tuning, FEATURES A7" ("FEATURES" is an optimizer doc never introduced here). Everywhere else this file links full `../../7dtd-optimizer/docs/` paths. |
| L1 | Low | `tools/README.md:40` | One em dash character: "## 1. General dumpers (`src/`) — prefer these". Violates AGENTS.md rule 5 ("No em dashes ... in any shipped text"). Only em dash in the audited corpus. |
| L2 | Low | `oss-tools/naiwazi.md:30,174`, `oss-tools/NOTES.md:369,432` | Four en dashes (U+2013): "20–30+ players", "20–30p", "§5–7" (x2). Not literally banned by the em-dash rule but same style family. Counts: naiwazi.md 2, NOTES.md 2; all other files 0. |
| L3 | Low | `docs/managers.md:28` | Redundant duplication in one cell: "`TwitchManager` | **1585** (IL=1585)". |
| L4 | Low | `docs/aidirector.md:110-113` | Stray tail section "IsDedicatedServer references in Entity* Update methods" (2 bullets) unrelated to the doc's stated ownership ("AIDirector type inventory"); belongs with closed-gaps §5 / frame classification. Also no blank line between it and "## Related docs" (line 113/114). |
| L5 | Low | `docs/INDEX.md:194,222` | Inventories table row "inventories/opt-scan.md | optim OPTIMIZATION_CANDIDATES" is the only unlinked "Prefer" target (opt-scan.md itself links it). Line 222 calls all of `tools/legacy/` "39 per-family dumpers", while tools/README.md distinguishes ~12 canonical family dumpers from ad-hoc helpers/finders. |
| L6 | Low | `docs/inventories/netpackages.md:8` vs table | Definitional imprecision, consistent corpus-wide: "193 wire + NetPackageManager" counts by name prefix, but the 194-row table itself shows 7 rows that are not wire packages (base `NetPackage`, enum `NetPackageDirection`, `NetPackageEntry`, `NetPackageInfo`, `NetPackageLogger`, `NetPackageMeasure`, `NetPackageMetrics` - Object/Enum-based). Matches the oracle phrasing, so no factual error, but "wire packages" overstates ~6 helper types. |
| L7 | Low | `docs/protocol.md:377,410-413` | §11 status table updated "after the protocol-packages.md pass (2026-07-23)" but the Changelog's last entry is 2026-07-20; the 07-23 pass is only recorded in INDEX.md's changelog. |
| L8 | Low | `docs/loop-gmupdate.md:377-380` | Changelog ends 2026-07-16; does not record that its dump tool moved (nor could it, see H1). Same for entity-ai.md changelog (ends 2026-07-16 despite 2026-07-21 addendum being added later; addendum is dated inline, so informational only). |
| L9 | Low | `il/terrain-*-v3.0.1/TERRAIN_auto.md:6` etc. | Regenerable dump artifacts still print old regen hints ("mono DumpTerrain.exe $ASM research/il/terrain-VERSION"). Out of audit scope (git-ignored), but the *tracked* legacy dumpers embed these strings and will reprint them on regen; fix at the dumper if touched. |
| O1 | Observation | task premise | docs/ contains **19** .md files including INDEX, not 20 as stated in the audit request. No file appears missing: INDEX clusters A-E enumerate exactly the 18 non-INDEX docs present. |

## Oracle verification (all pass)

Checked every occurrence of every oracle value; zero numeric contradictions found across the corpus:

- **Top-level types 4401 / methods-with-body 43901:** coverage.md:56-57, re-methodology.md:52-53 ("~4400" prose at re-methodology.md:10). Consistent.
- **NetPackage 194 = 193 wire + NetPackageManager; 189 runtime id-map:** coverage.md:58, network.md:73, protocol.md:126-129 + capture "0xBD = 189" (protocol.md:103, protocol-frames.md:231), residuals.md:53, engine-limitations.md:78, netpackages.md:8 (194 rows counted). Consistent (see L6 for phrasing nuance).
- **gmUpdate IL 631:** loop.md:45/96, loop-gmupdate.md:21/46, coverage.md:60, world-chunks.md:16, opt-scan.md:70, re-methodology.md:56. **14 locals, 1 handler, 6x IsDedicatedServer** (loop-gmupdate.md:47-48) consistent with loop.md:96. gmUpdate 182 ordered calls (loop.md:98) = 182 rows in gmupdate-calls.md and "calls=182" in opt-scan.md:395.
- **WorldState.SaveLoad(Stream) IL 884:** coverage.md:61, loop.md:352, save-region.md:19, terrain-height.md:119, loop-complete.md:56, opt-scan.md:35, re-methodology.md:57.
- **GameTimer 20 Hz:** closed-gaps.md:24-26 (`ldc.r4 20` ctor), loop.md:228/348, coverage.md:59, entity-ai.md, engine-limitations.md:44, re-methodology.md:58.
- **EnumDamageTypes 16 = Suffocation:** protocol.md:279 ("16 Suffocation"), protocol-frames.md:521 ("16 Suffocation (drown)").
- **NetPackageDirection 0=Both/1=ToServer/2=ToClient:** protocol-packages.md:55/261, re-methodology.md:148-149. Direction tally 66+33+7+87 = 193 sums correctly (protocol-packages.md:56-57).
- **6 channel-1 packages:** protocol.md:353-357 and protocol-packages.md:26-36 (identical lists). **8 compressed:** protocol.md:337, protocol-packages.md:44-48 (list of 8 verified). **10 pre-auth:** protocol-packages.md:61-67 (10 names counted).
- **Frame math:** envelope 9-byte header consistent between protocol.md §3 ("1 + 8 + payloadSize") and protocol-frames.md §2 ("frame_len = 9 + payloadSize"); RelPos body 20 / contentLen 22 / full frame 35 (protocol-frames.md §13) and empty-body frame 15 (§2.2) all internally consistent; PosAndRot body 30 / contentLen 32 consistent across protocol.md §6.1 and frames §7.
- **242 MB Update methods:** loop.md:59 matches 242 data rows in inventories/frame-entries.md; closed-gaps.md:148 classification (33 + 96 + 77 = 206 *types*, methods vs types distinction preserved).
- **Host RAM 123.4 GiB / 128 GB:** not asserted anywhere in the audited scope (host topology correctly delegated to optimizer HOST_TUNING). No conflict possible.
- **Chunk save loop 64 / `y & 255` / RegionFileRaw constants / ChunkBlockChannel Read=151,Write=120:** consistent between save-region.md, terrain-height.md, light-mesh-water.md, residuals.md:56.

## Restructure verification (the move landed cleanly at the link level)

- All 6 optimization docs + zig-clone.md **absent** from `docs/` (verified by filesystem).
- Every referenced `../../7dtd-optimizer/docs/*.md` target exists (measured-scaling, bottlenecks, algorithms, aggressive-optimizations, runtime-tuning, allocation-reuse, HOST_TUNING, OPTIMIZATION_CANDIDATES, ARCHITECTURE, SIM_PARALLELISM, OPTIMIZATION_IDEAS, RESULTS). `../../zdtd/docs/zig-clone.md` resolves from `docs/`.
- `7dtd-optimizer/tools/` no longer exists, `tools/legacy/` holds exactly 39 .cs dumpers incl. DumpGmUpdate/DumpTerrain/DumpDeep/DumpDeeper/DumpGaps - which is what makes H1/H2/M1/M2 stale rather than merely cosmetic.
- No multiple-H1 files (fence-aware scan clean; aidirector's former second H1 confirmed fixed), no unclosed fences, no exactly-duplicated H2 headings (the network.md/terrain-height.md issues are semantic duplicates with different titles).
- No AI-attribution phrasing anywhere in scope.

## INDEX coverage check (item 8) - pass with notes

- **Clusters A-E** list exactly the 18 non-INDEX docs, each exactly once: A(4): coverage, residuals, engine-limitations, re-methodology; B(3): loop, loop-gmupdate, managers; C(3): entity-ai, aidirector, closed-gaps; D(4): world-chunks, terrain-height, save-region, light-mesh-water; E(4): network, protocol, protocol-frames, protocol-packages. **Cluster F** correctly holds only external optimizer docs with `../../7dtd-optimizer/docs/` links and an explicit "not this repo" preamble (INDEX.md:167-181).
- **One-home table** (INDEX.md:80-99): 18 rows, one per local doc, complete, no moved doc listed as local. The moved-topics paragraph (INDEX.md:101-105) correctly routes optimizer topics and zig-clone.
- **Inventories table**: all 8 inventory files listed with "Prefer" targets (one unlinked target, L5).
- **Reading paths**: consistent with the moves - external references are labeled ("optimizer `measured-scaling.md`", "optimization mod: `../../7dtd-optimizer/docs/`"). Minor: "Start here" row 6 places the external zig-clone.md in the stock-RE quickstart table (labeled "companion", acceptable).
- **Key state machines** table anchors spot-checked: loop.md §2/§3 (exist), world-chunks.md §4 (exists), network.md §2 (exists), save-region.md §1 (exists), gmUpdate "phases A-J" matches loop.md §2 phase letters A-J.
- **Changelog** (INDEX.md:246-249) records the restructure accurately (clusters, zig-clone move, optimizer-doc move, tools consolidation).

## Per-file detail

### docs/INDEX.md
Findings: L5, O1 context. Otherwise clean: cluster grouping complete (see above); Tools section matches tools/README (build.sh, bin/legacy path, structural gate command); external links labeled. Historical changelog entries mentioning zig-clone.md (line 251) are dated history, not stale claims.

### AGENTS.md
Clean. Doc-scope rule is well-formed and is the yardstick used for M6-M8/M11/M13 above. Referenced `../AGENTS.md` and `../MODDING_BEST_PRACTICES.md` both exist.

### README.md
Findings: M3. Also note the highlights quote measured results (0.4% residual, O(N^2.26), 54%/27% split) - each traceable (bottlenecks.md link, entity-ai addendum with RESULTS pointers), so not unsupported, but the framing sells the repo as containing the measurement program that now lives in 7dtd-optimizer. The Layout block (lines 28-36) is accurate post-restructure; only the prose above it lags.

### docs/coverage.md
Findings: M13. Census table matches oracle exactly. Family rows 1-11 correctly map to local narratives + dump sets. Changelog does not mention the 2026-07-23 restructure (INDEX carries it; acceptable for a leaf doc).

### docs/residuals.md
Clean, and it is the doc closed-gaps §9 contradicts (H3). Closed-items table verified against the owning docs (spot checks all resolve). The "encryption cipher/KDF" and "sector payload codec" residuals correctly survive the protocol-packages pass.

### docs/re-methodology.md
Findings: M4. Census baseline table matches oracle (plus "All types incl nested 7413", unverifiable against provided oracle but not conflicting). §5 enum method matches oracle direction values. §6 correctly draws the structure-vs-cost line and routes cost to optimizer docs with full paths, except the one bare `allocation-reuse.md`.

### docs/loop.md
Clean on numbers; measured block §3 (19.9/59.7 calls/s, recv ~1,200/s, send ~1,600/s, 86-96% gaps <2 ms) carries an explicit artifact pointer ("Full evidence: `7dtd-optimizer/docs/RESULTS.md` §3k" - unlinked prose path, file exists). Mild scope residue: §4 "Optim: optional air-swap..." and §9 "Optim note" column ("dedi skip candidate") are one-line lever hints in a stock doc; §13 is correctly pointers-only. Not escalated beyond the M6-M8 class.

### docs/loop-gmupdate.md
Findings: H1, M8 (+L8, L9-adjacent bare SIM_PARALLELISM ref at line 351). Phase content itself is consistent with loop.md §2 and gmupdate-calls.md (182 calls, same ordering).

### docs/managers.md
Findings: L3. Manager IL table consistent with manager-updates.md and loop.md §10 (spot-checked all shared rows). ModEvents inventory consistent with residuals ("names closed, subscribers residual").

### docs/entity-ai.md
Findings: M2, M7, M9. Threshold constants (64/225/0.1/0.3/1.0, 36, 625/3025, 1225, ±45, 0.05, ≤8 drain, 20 Hz) all consistent with deeper.md §4 constants dump. §3.5 net-interest table honestly labeled "hypothesis". Addendum measured claims all carry RESULTS §3m-3o/§3q pointers (good provenance; scope note under M7). README's "54% world-collision physics, 27% AI" matches addendum's "MoveEntityHeaded 54%, updateTasks 27%".

### docs/aidirector.md
Findings: L4. Component inventory and install order consistent with closed-gaps §2 and loop.md §5. Single H1 confirmed.

### docs/closed-gaps.md
Findings: H3; also line 8 "Tool: `tools/DumpGaps.cs`" - actual location `tools/legacy/DumpGaps.cs` (minor stale, fold into the H1/M1/M2 fix batch). §4 threshold table consistent with network.md §2 and deeper.md constants (2/16/128/256/0.04/100/10, mask 192). §8 lever-map table is borderline scope but explicitly framed as "merged into the optimizer project" with a full link.

### docs/world-chunks.md
Clean. IL numbers consistent with loop.md/opt-scan (828 SetBlock, 550 chunkPosNeedsRegeneration, 448 DetermineChunksToLoad, 216 SendChunks). "EntityFallingBlock OnUpdateEntity 300+" is a rounded version of 344/302 elsewhere - not a contradiction.

### docs/terrain-height.md
Findings: M1, M11. Constant table (256/64/255/16384/4096/16383, ChunkAreaDim 256 never expand) internally consistent and consistent with save-region/light-mesh-water 255/256/64 sites.

### docs/save-region.md
Clean. Write/Read 601/775, layer loop 64, ChunkBlockChannel Write=120/Read=151 (residuals' "IL=151/120" for "Read/Write" agrees), RegionFileRaw constants, `.ttc` ext. Honest "codec not hand-annotated" status matches residuals.

### docs/light-mesh-water.md
Clean. 255/256 site inventory consistent with terrain-height and engine-limitations §5.

### docs/network.md
Findings: M5, M6, M10. §2/§3/§3b consistent with closed-gaps §4, protocol.md, oracle census. The §4b CORRECTION block is exemplary honest-status practice (it names and reverses its own earlier wrong claim).

### docs/protocol.md
Findings: L7. Everything numeric checks out (see oracle section). §8/§9 correctly defer census detail to protocol-packages. Family-counts table (line 133-141) is labeled "Approx" - fine.

### docs/protocol-frames.md
Clean. All offset tables re-computed and verified (challenge 17, envelope 9+ps, empty frame 15, PosAndRot 30/32, RelPos 20/22 and quat-variant 30, AliveFlags 6 + bit table matching protocol.md, LookAt 16, DamageEntity fixed head offsets 0-43, full RelPos frame 35). Anchors used by protocol.md §2/§3/§6 match its headings.

### docs/protocol-packages.md
Clean. The strongest doc in the corpus: every census number matches the oracle, direction tally sums, §8 "Still open" agrees with residuals.md and coverage.md row 6 residual tail.

### docs/engine-limitations.md
Findings: M14. §2 measured walls all carry measured-scaling pointers. Scope is legitimate under AGENTS ("stock ceilings live here"); lever columns reference optimizer by name, mostly linked.

### docs/inventories/* (8 files)
All carry the "Kind / Prefer / Raw" header pointing at the right narrative and dump set. frame-entries: 242 rows (matches loop.md). gmupdate-calls: 182 rows (matches). netpackages: L6. opt-scan: "Prefer: optimizer OPTIMIZATION_CANDIDATES" link resolves (`../../../7dtd-optimizer/...` correct depth); its content is stock IL inventory, so it stays in-scope despite the name. gaps.md: elided-IL placeholders for publication are consistent with the no-redistribution policy; §7 heading "AntiCheat / EAC surface" also contains RegionFile/TileArea/GameEvent types (auto-dump artifact, cosmetic). deeper.md, loop-complete.md: clean; duplicate "dumped" lines are auto-dump noise.

### tools/README.md
Findings: L1; plus it is the source of truth that makes H1 a contradiction (DumpGmUpdate pre-corrupted). Otherwise accurate: 39 legacy dumpers verified on disk; src/ tool list matches INDEX and README; test commands use `uv run`.

### tools/re-scratch/README.md
Clean. Honest about hardcoded paths.

### il/README.md
Findings: H2. Only 9 lines; 1 of them is wrong in the way that matters most for a policy doc.

### oss-tools/naiwazi.md, servertools.md, NOTES.md
Findings: M12, L2. Content is survey-grade with excellent claim hygiene (vendor claims labeled, verification column in naiwazi §4). NOTES.md correctly states clones are "not tracked here". These docs are optimizer-lens surveys ("Purpose: extract architecture and performance lessons for EfficientServer") living in the stock-RE repo - a gray zone the AGENTS.md routing table does not currently assign ("survey notes on third-party server tools/mods" is listed in the repo layout, so treated as sanctioned; noted, not graded).

## Corrections recommended

High priority:
- [ ] `docs/loop-gmupdate.md:9` - change tool reference to `tools/legacy/DumpGmUpdate.cs` and note it is broken; point §10 (lines 359-369) at the supported path: `cd tools && ./build.sh` then `mono bin/DumpMethod.exe "$ASM" GameManager gmUpdate` (per tools/README §2).
- [ ] `il/README.md:3` - replace "`7dtd-optimizer/tools/Dump*.cs`" with "`tools/src/` + `tools/legacy/` (see `../tools/README.md`)".
- [ ] `docs/closed-gaps.md:172-179` - rewrite §9: drop item 4 or restate as "Region sector payload byte codec (residual; managed structure closed in save-region.md)"; ideally replace the whole §9 list with a one-line pointer to residuals.md to honor "only open-item list".

Medium priority:
- [ ] `docs/terrain-height.md:20,22-30` - regen block: `tools/legacy/DumpTerrain.cs`, `cd tools && ./build.sh`, output `../il/terrain-v3.0.1`.
- [ ] `docs/entity-ai.md:383-388,649` - regen block: `tools/legacy/DumpDeep.cs` / `DumpDeeper.cs` via build.sh; output `../il/deep-v3.0.1`; drop `7dtd-il`.
- [ ] `docs/closed-gaps.md:8` - `tools/DumpGaps.cs` -> `tools/legacy/DumpGaps.cs`.
- [ ] `README.md:4-5,17,23` - reword highlights/scope: analysis produced *alongside* the optimization suite; label the bottlenecks link as external (`7dtd-optimizer/docs/bottlenecks.md`); drop or re-attribute "GC/runtime tuning, aggressive-optimization catalog".
- [ ] `docs/re-methodology.md:184` - link `allocation-reuse.md` with its full optimizer path.
- [ ] `docs/network.md:136-147` - add an artifact pointer (RESULTS/measured-scaling anchor) for the 15 MB/s and #4-allocator claims, and trim the lever verdict to a one-line pointer at the optimizer.
- [ ] `docs/network.md:149-164` - merge "See also" and "Related docs" into one table.
- [ ] `docs/terrain-height.md` - merge the two see-also tables; move "Product inject lessons" to `7days-realworld/docs/` leaving a pointer row.
- [ ] `docs/entity-ai.md` - renumber the "Deeper synthesis" sections (e.g. D1-D14) or fold them into the main sequence; trim §12 lever tables to pointers; move the "v1.15.0 lever" status sentence to the optimizer doc.
- [ ] `docs/loop-gmupdate.md:236,343-356` - compress EfficientServer/conductor guidance into a pointer at optimizer ARCHITECTURE/SIM_PARALLELISM; link SIM_PARALLELISM at line 351.
- [ ] `oss-tools/naiwazi.md:118`, `oss-tools/servertools.md:4` - update local-clone locations (or state "clone location: external, not tracked" as NOTES.md does).
- [ ] `docs/coverage.md:41-42` - either move rows 12-13 below the table as "companion (optimizer-owned)" or annotate that they are outside the managed-surface bar.
- [ ] `docs/engine-limitations.md:43,124` - link ARCHITECTURE and FEATURES with full optimizer paths (or drop "FEATURES A7").

Low priority:
- [ ] `tools/README.md:40` - replace the em dash.
- [ ] `oss-tools/naiwazi.md:30,174`, `NOTES.md:369,432` - replace en dashes with hyphens if the style rule is read strictly.
- [ ] `docs/managers.md:28` - drop "(IL=1585)".
- [ ] `docs/aidirector.md:110-114` - move the IsDedicatedServer bullets to closed-gaps/inventories; add blank line before Related docs.
- [ ] `docs/INDEX.md:194` - link the opt-scan Prefer target; `:222` - "39 dumpers (12 canonical per-family + ad-hoc helpers)".
- [ ] `docs/protocol.md` changelog - add the 2026-07-23 backlog-status entry.
- [ ] Optional: qualify "193 wire" once (e.g. in netpackages.md) as "by name prefix; includes base/enum/helper types".
- [ ] When next touching `tools/legacy/DumpTerrain.cs`/`DumpRealEarthSurfaces.cs`, update their embedded `research/il/...` regen hint strings.

## Coverage status

- **Checked directly:** all 33 in-scope files read in full; every oracle value cross-checked at every occurrence; filesystem existence verified for every cross-repo path family, the 39 legacy dumpers, and the absence of the 7 moved docs; fence-aware structural scan (H1s, fences, duplicate H2s); character-level dash and AI-attribution scans; INDEX cluster/one-home/reading-path completeness; anchor spot-checks for the INDEX state-machine table and protocol.md -> protocol-frames.md fragments.
- **Not checked / out of scope:** contents of `../7dtd-optimizer/docs/*` and `../../zdtd/docs/zig-clone.md` (existence verified only, per task focus); `7days-realworld/` private-companion targets (referenced as prose paths by design, not links); il/ dump-set internals beyond the stale-string grep (git-ignored, regenerable); running `tools/tests/*` or `Census.exe` (oracle values supplied by requester as ground truth); rendered-markdown anchor resolution for every fragment link (mechanical link check reported 0-broken by requester; only high-traffic anchors spot-verified).
- **Uncertain:** whether the task's "20 docs" count intended an additional file (none is referenced-but-missing anywhere, so 19 appears correct); whether oss-tools' optimizer-lens surveys should eventually route to the optimizer repo (AGENTS.md currently sanctions the folder here).

---

## Resolution status (2026-07-23, applied)

All High + Medium + Low findings fixed. High/scope/structure by lead; mechanical
batch (H2, M4, M14, L1, L3, L4, L5, L7, M12, L2) by subagent.

| Finding | Status |
|---|---|
| H1 loop-gmupdate regen | FIXED (build.sh + DumpMethod; broken dumper noted) |
| H2 il/README tools path | FIXED (tools/src + tools/legacy) |
| H3 closed-gaps §9 Region/WorldState open | FIXED (managed structure closed; only sector codec residual; pointer to residuals) |
| M1 terrain-height regen | FIXED | M2 entity-ai regen | FIXED |
| M3 README scope | FIXED (stock-only framing; external bottlenecks labeled) |
| M4 re-methodology link | FIXED | M5 network numbers | FIXED (measured share -> optimizer pointer) |
| M6 network lever scope | FIXED | M7 entity-ai lever tables | FIXED (§11 retitled RE; §12 -> pointer + RE notes; addendum lever-status -> pointer) |
| M8 loop-gmupdate §9 conductor | FIXED (retitled "Interception points"; lever selection -> optimizer pointer; SIM_PARALLELISM linked) |
| M9 entity-ai duplicate numbering | FIXED (Deeper synthesis -> D1-D14) |
| M10 network dup closing tables | FIXED (merged) | M11 terrain-height dup + product | FIXED (merged; product lessons -> pointer) |
| M12 oss-tools clone paths | FIXED | M13 coverage families 12-13 | FIXED (split below the managed-surface bar) |
| M14 engine-limitations links | FIXED |
| L1 tools/README em dash | FIXED | L2 en dashes | FIXED | L3 managers | FIXED |
| L4 aidirector stray section | FIXED | L5 INDEX opt-scan link + dumper count | FIXED |
| L7 protocol changelog | FIXED |
| L6 "193 wire" phrasing nuance | left as-is (matches oracle; no factual error) |

Verification: 0 broken links, 0 em/en dashes, all docs single-H1, all touched
files single Changelog.
