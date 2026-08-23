# Documentation audit: 7dtd-engine-research RE corpus (V3.0.1)

**Scope:** 24 narrative docs in `docs/` (incl. INDEX.md), 8 inventories in `docs/inventories/`, `README.md`, 3 files in `oss-tools/`. All 36 files read in full. Oracle values (verified live via Mono.Cecil): top-level types = 4401; methods with body = 43901; NetPackage* top-level types = 194 exactly (199 with nested; 189 = runtime id-map count, a distinct quantity); gmUpdate IL = 631; WorldState.SaveLoad(Stream) IL = 884; GameTimer = 20 Hz/TPS.

**Method:** full read of every file plus cross-file grep scans for the oracle numerics, em dashes, TODO markers, anchors, and duplicate headings. No files were edited.

---

## Findings table (severity-ranked)

| # | Sev | Category | Finding | Files |
|---|-----|----------|---------|-------|
| F1 | High | Numeric contradiction | NetPackage census stated as "~196" in four places; oracle and `netpackages.md` say exactly **194**. `residuals.md` contradicts itself (~194 at line 33, ~196 at line 53) | coverage.md:58, network.md:73, engine-limitations.md:78, residuals.md:33+53, netpackages.md:8, protocol.md:4+125 |
| F2 | High | Internal contradiction | bottlenecks.md §5 correction says a spatial grid does NOT collapse the O(N^2.26) wall ("no safe EfficientServer lever"), but §5 item 1 and Tier 4 #10 in the same file still claim the grid "collapses the O(N^2.26) wall" | bottlenecks.md:210-238 vs 354-358 |
| F3 | High | Internal contradiction | bottlenecks.md §6 "one-line answer" recommends "#5 buffer presize-and-retain" as the next lever, but #5 is struck through and DOWNGRADED earlier in the same section | bottlenecks.md:331-335 vs 360-363 |
| F4 | High | Cross-doc contradiction | Chunk pipeline "~56-60% of instrumented tick in every loaded scenario" (three docs) vs campaign-final attribution "chunk send 5%" (2026-07-21). Never reconciled | bottlenecks.md:36-37,349 vs 204; algorithms.md:115; aggressive-optimizations.md:123,129 |
| F5 | High | Cross-doc contradiction (stale) | algorithms.md and zig-clone.md still frame interest management as "missing spatial index" / claim a grid hash "collapses the 450-500p death spiral", contradicting the 2026-07-20 correction (bottlenecks.md §5, aggressive-optimizations.md §2: "inherent, not an index problem") | algorithms.md:64-65,131; zig-clone.md:217-221 vs bottlenecks.md:217-234, aggressive-optimizations.md:61-64 |
| F6 | High | Internal contradiction | runtime-tuning.md lists `GC_PAUSE_TIME_TARGET` in the honored-env-vars list, then in the very next sentence in the NOT-honored list; the §1 example command sets `GC_MARKERS=4` which the same section says is not honored | runtime-tuning.md:33-38 vs 40-45 |
| F7 | Medium | Numeric inconsistency | The 479 ms megapause heap size is variously "~5.6 GB live heap", "6.9/6.91 GB", and "~7 GB" across five docs | bottlenecks.md:48-49,164 vs 172-173; algorithms.md:140-142; runtime-tuning.md:60; allocation-reuse.md:15-16; zig-clone.md:11; aggressive-optimizations.md:148-149 |
| F8 | Medium | Staleness contradiction | terrain-height.md dump-set table labels `terrain-v3.0.1` as "Dedicated live / **Expanded** on this machine"; coverage.md live pin says live dedi is stock and expanded dumps are historical | terrain-height.md:15-17 vs coverage.md:10 |
| F9 | Medium | Broken anchors | All three cross-doc anchors in protocol.md point at headings that no longer exist in protocol-frames.md (renamed in the 2026-07-20 rewrite); the §8 anchor also lands on RelPos, not the promised "entity packages" section | protocol.md:45,58,206 vs protocol-frames.md:32,61,355 |
| F10 | Medium | Policy self-violation | residuals.md policy: "every residual here is non-managed, native, Unity-settings, content-dependent, or third-party". Two rows are managed-IL items (NetPackage body catalog; region sector codec, "managed methods exist and are dumped") | residuals.md:7-8 vs 31,33 |
| F11 | Medium | Missing provenance | Quantities with no artifact/session pointer: "~15 MB/s at 128p"; "42 findings verified"; "15.16 / 14.84 / 14.52 MB/s"; "~32 s at 334 zombies" and "~15 s" (units/window undefined); join "rate limit ~500 ms per IP"; "66 ms" figure cited in-text without table backing | network.md:137; bottlenecks.md:5,50-51,116; aggressive-optimizations.md:34,61; zig-clone.md:266; measured-scaling.md:144 |
| F12 | Medium | Numeric inconsistency | Same headline measured two ways: "66.6 ms/tick at 64p+340z" vs "66 ms" at "64p + ~300z" | bottlenecks.md:42-43 vs measured-scaling.md:132,144 |
| F13 | Medium | Internal contradiction | allocation-reuse.md §1/§2 correct that the pooled stream buffer is NOT a reuse target, yet §4 table's first row still prescribes "presize + retain" for it | allocation-reuse.md:47-53,63-69 vs 121-123 |
| F14 | Medium | Path staleness | Repo restructure left stale `research/il/`, `research/docs/`, `research/naiwazi/`, `research/7dtd-ServerTools` paths; INDEX/README use `il/` | protocol.md:9,90,142; network.md:90; measured-scaling.md:10; coverage.md:69; loop.md:379,421; entity-ai.md:385; zig-clone.md:512; loop-gmupdate.md:366; terrain-height.md:27-29; aggressive... (none); servertools.md:4; naiwazi.md:118 |
| F15 | Medium | Numeric inconsistency | Host RAM "128 GB" vs "123 GB host" | allocation-reuse.md:6 vs runtime-tuning.md:56-57 |
| F16 | Low | Terminology inconsistency | DamageEntity damageType 16 = "Suffocation" in one doc, "Drown" in the other | protocol.md:276 vs protocol-frames.md:520 |
| F17 | Low | Channel-count tension | "ProcessPackages x2 channels" stated as fact in three docs; protocol.md §9 only establishes channel 0 ("other channels ... treat as later") | bottlenecks.md:31-32; algorithms.md:86; loop-gmupdate.md:297 vs protocol.md:341-344 |
| F18 | Low | Structural | Duplicate `## Changelog` blocks (Related-docs table wedged between two changelogs) in 7 files | coverage.md:83+94; closed-gaps.md:183+194; light-mesh-water.md:105+115; loop.md:417+448; managers.md:115+125; network.md:158+170; world-chunks.md:143+154 |
| F19 | Low | Structural | loop.md appendix is a malformed code block: bare tree text with a stray closing fence and no opening fence | loop.md:428-435 |
| F20 | Low | Structural (merge artifacts) | entity-ai.md: two "See also" sections, two changelogs, second H1 mid-file, and stale self-reference "`SYNTHESIS.md`, this file" | entity-ai.md:369,392,396,402,654,661 |
| F21 | Low | Structural | Duplicated front-matter blocks (two Kind/Prefer headers) in two inventories; deeper.md prefers "entity-ai.md, entity-ai.md" (duplicate) and has two H1s | gmupdate-calls.md:3-10; manager-updates.md:3-10; deeper.md:1-9 |
| F22 | Low | Style rule | Em dashes present: oss-tools/NOTES.md (17 occurrences), oss-tools/servertools.md (9). Zero in docs/ and README.md. No AI-attribution phrasing anywhere | NOTES.md:65,176,204,218,237,257,309,313,315,316,318-321; servertools.md:98,115,132,146,154,162,170,176,180 |
| F23 | Low | Cross-reference claims | "One home per topic" weakened: NetPackage census lives in 3 files with diverging values (see F1); package-band thresholds duplicated verbatim in 5 docs; bottlenecks/algorithms/aggressive-optimizations/allocation-reuse absent from the one-home table | INDEX.md:79-101; loop.md:279; network.md:55-66; closed-gaps.md:§4; protocol-frames.md:§14; zig-clone.md:§7 |
| F24 | Low | Cross-reference | coverage.md family 8 ("Origin / claims") cites only the unpublished product doc as its narrative, so the published corpus has no owning narrative for that family; coverage Related-docs row "`INDEX.md` \| Product RealEarth" reads as a self-reference | coverage.md:37,92 |
| F25 | Low | Editorial leftovers | opt-scan.md auto-dump leftovers: "MISSING `EntityActivity`", "MISSING `Physics`", empty "Callers of `World::AddFallingBlocks`" section; loop-complete.md has many duplicated inventory lines/headings (tool artifact) | opt-scan.md:185,234,272-274; loop-complete.md:11-13,55-64,245+460 |
| F26 | Low | Phrasing inconsistency | AI LOD mid band: loop-gmupdate says dist²<225 → "scale 0.3 **or** 0.1 (branch picks 0.1 vs 0.3)"; entity-ai/loop state <225 → 0.3, else 0.1 | loop-gmupdate.md:283-285 vs entity-ai.md:155-159, loop.md:218-222 |

---

## Oracle conformance summary

| Quantity | Oracle | Corpus status |
|---|---|---|
| Top-level types | 4401 | Matches; single site (coverage.md:56). No conflicts |
| Methods with body | 43901 | Matches; single site (coverage.md:57). No conflicts |
| NetPackage* top-level | **194** | **Conflicts** (F1). Exact 194: netpackages.md:8. "~194": protocol.md:4,125; residuals.md:33; zig-clone.md:41,245,478. "~196": coverage.md:58, network.md:73, engine-limitations.md:78, residuals.md:53. Note protocol.md:127-138 family counts sum to exactly 194 (32+16+12+8+9+6+5+106), corroborating the oracle. "189" appearances (protocol.md:102,125; protocol-frames.md:231; zig-clone.md:245) are correctly labeled as the live id-map count and are legitimate; no doc conflates 189 with the type census |
| gmUpdate IL | 631 | Consistent everywhere (loop.md:45,96; loop-gmupdate.md:21,47; world-chunks.md:16; coverage.md:60; opt-scan.md:70,395; gmupdate-calls.md:8) |
| WorldState.SaveLoad(Stream) IL | 884 | Consistent everywhere (coverage.md:61; loop.md:352; bottlenecks.md:100,127; algorithms.md:120; save-region.md:19; terrain-height.md:119; loop-complete.md:56; opt-scan.md:35) |
| GameTimer | 20 Hz / 20 TPS | Consistent everywhere (closed-gaps.md:24-35; loop.md:228,348; coverage.md:11,59; engine-limitations.md:44,169; README.md:14; etc.) |
| ChunkBlockYDim=256 / ChunkBlockLayers=64 | given | Consistent (coverage.md:10; terrain-height.md:47-52; world-chunks.md:52; save-region.md:76-90; engine-limitations.md:104-108; zig-clone.md:293-297). Only F8 (which dump is "live") conflicts |
| Origin.FixedUpdate dedi no-op | given | Consistent (loop.md:53,362,406; residuals.md:50,62-71; engine-limitations.md:50,181; terrain-height.md:127; INDEX.md:73). residuals.md §3 documents the correction of the old wrong claim; no doc still asserts the wrong version |

Other cross-checked claims that held up: loop.md:59 "242 MB methods" = 242 rows in frame-entries.md; loop.md:98 "182 calls" = 182 rows in gmupdate-calls.md; closed-gaps.md:150 "~33 dedicated-relevant" = 33 in gaps.md:1277; README.md:18 "0.4% residual" = bottlenecks.md:199; README.md:22 "54% ... 27%" = entity-ai.md:690-692; protocol.md envelope math (0x12BC/0x12B8/189, frame=9+payloadSize, RelPos 20/22/35) is internally consistent across protocol.md and protocol-frames.md.

---

## Per-file detail

### docs/coverage.md
- **F1 (High).** Line 58: `| NetPackage* types | ~196 |` in the "Census (live dedi)" table. Every other census row in this table matches the oracle exactly (4401, 43901, 631, 884, 20); this is the lone wrong value, and it sits in the file positioned as the authoritative census. Should be 194 (or "194 top-level / 199 incl. nested").
- **F18 (Low).** Two `## Changelog` headings (lines 83 and 94) with the Related-docs table between them.
- **F14 (Medium).** Line 69: "Open the cited `research/il/...` path" — the published tree is `il/` (INDEX.md:12).
- **F24 (Low).** Line 37: family 8 "Origin / claims" narrative is `realearth-surfaces.md` (private, unpublished); line 92 Related-docs row `` `INDEX.md` | Product RealEarth `` is ambiguous with the hub link two rows above.

### docs/residuals.md
- **F1 (High).** Internal contradiction: line 33 "Full NetPackage body catalog (**~194**)" vs line 53 "NetPackage type census (**~196**)". Same file, two values.
- **F10 (Medium).** Lines 7-8 policy: "every residual here is **non-managed**, **native**, **Unity-settings**, **content-dependent**, or **third-party black box**." Line 33 (NetPackage bodies: "Names + maxIL closed; most write/read bodies not hand-annotated") and line 31 (sector codec: "Managed methods exist and are dumped") are managed-IL annotation backlogs, not non-IL residuals. Either the policy line or the rows need adjusting.
- Positive: §3 (lines 62-71) is a model correction note for the Origin no-op.

### docs/network.md
- **F1 (High).** Line 73: "Live census: **~196** types named `NetPackage*`". Conflicts with 194.
- **F14 (Medium).** Line 90: "Full name list: `research/il/dedi-complete-v3.0.1/...`".
- **F11 (Medium).** Line 137: "**Where the ~15 MB/s at 128p actually comes from**" — the 15 MB/s @128p figure appears nowhere else with a session/artifact pointer (measured-scaling's alloc data is 64p + ~300z).
- **F18 (Low).** Two `## Changelog` blocks (158, 170).
- Positive: §4b CORRECTION (lines 126-135) is explicit and dated; zig-clone.md §4.1 agrees with it.

### docs/engine-limitations.md
- **F1 (High).** Line 78: "**~196 NetPackage\* types** | dedi-complete census". The dedi-complete census says 194 (netpackages.md:8).
- Scaling rows (lines 59-66) correctly point to measured-scaling.md; no provenance issue.

### docs/bottlenecks.md
- **F2 (High).** Lines 217-234 (CORRECTION, 2026-07-20): "a spatial grid does **not** collapse `NetEntityDistribution.OnUpdateEntities` ... **there is no safe EfficientServer lever for this wall**." But line 213-215 (§5 item 1, immediately above the correction) still says "Two moves collapse most of the board: **Spatial bucketing** ...", and lines 354-358 (Tier 4 #10) still say "Shared spatial interest grid ... (**collapses the O(N^2.26) wall**) ... Collapses both quadratic walls toward linear". The correction was inserted without updating the surrounding claims.
- **F3 (High).** Lines 331-335: "**~~`PooledExpandableMemoryStream` presize + retain~~ - DOWNGRADED**". Lines 360-363: "After that, **#5 buffer presize-and-retain** for allocation" — recommends the item the same section struck out.
- **F4 (High).** Lines 36-37: "**~56-60% of instrumented tick in every loaded scenario**" (also line 349: "the chunk pipeline is **56-60% of tick**") vs line 204 (§4b campaign-final, 2026-07-21): "**chunk send 5%**, all else < 2%". Even if these reflect different instrumentation eras or load shapes, the doc presents both as current with no reconciliation.
- **F7 (Medium).** Line 48-49: "measured **479 ms megapause** on a **~5.6 GB** live heap" vs line 172-173: "the 479 ms figure is a *forced* full collect on a GC-disabled **6.9 GB** heap". Same number, two heap sizes, same file.
- **F11 (Medium).** Line 5: "**42 findings** verified" (count not derivable from the doc); lines 50-51: "15.16 / 14.84 / 14.52 MB/s across forced / guard / incremental" (no session/RESULTS pointer at that sentence); line 116: "~15 MB/s@128p" (see F11 above).
- **F12 (Medium).** Line 42-43: "**66.6 ms/tick** at 64p+**340z**" vs measured-scaling.md:132/144: heavy standard load "64p + **~300z**", "top CPU section (§1, **66 ms**)".
- **F17 (Low).** Line 31-32: "`ProcessPackages x2 channels x clients`" — see protocol.md §9.

### docs/algorithms.md
- **F5 (High).** Line 64-65: "The missing structure is a spatial bucket (chunk-cell grid)"; line 131: "A single uniform grid keyed on chunk cell would serve all of these **+ network interest**." Both contradict the bottlenecks.md correction (interest already distance-gated; wall is inherent replication) and aggressive-optimizations.md §2 ("inherent, not an index problem").
- **F4 (High).** Line 115: "**~56-60% of instrumented tick** in every loaded scenario" — same stale figure as bottlenecks §1 (vs campaign-final 5%).
- F7 context: lines 140-142 correctly separate "live working heap ~5.6 GB" from "forced full collect of a 6.91 GB heap = 479 ms" — this is the wording bottlenecks §1 #6 garbled.

### docs/runtime-tuning.md
- **F6 (High/Medium).** Lines 33-38 present `GC_PAUSE_TIME_TARGET` and `GC_MARKERS` as usable env vars, with the example `GC_ENABLE_INCREMENTAL=1 GC_PAUSE_TIME_TARGET=5 GC_MARKERS=4 ...`. Lines 40-45 then say honored vars include `GC_PAUSE_TIME_TARGET`, and "**NOT honored:** `GC_MARKERS` / `GC_PAUSE_TIME_TARGET` alone (use `GC_NPROCS` ...)". `GC_PAUSE_TIME_TARGET` appears in both the honored and not-honored lists; the recommended example uses a knob the verification paragraph says does nothing. Needs one authoritative statement.
- **F15 (Medium).** Line 56-57: "On a **123 GB** host divisor `1` is free" vs allocation-reuse.md:6 "Host has **128 GB RAM**".
- Positive: the three A/B paragraphs (lines 65-96) all carry session IDs; §4 is a well-documented correction.

### docs/measured-scaling.md
- Best-provenanced doc in the corpus (session IDs, JSON paths, method description).
- **F12 (Medium).** Line 144: "top CPU section (§1, **66 ms**)" — no 66 ms value exists in §1's tables (they hold exponents only); bottlenecks says 66.6 at a different zombie count.
- **F14 (Medium).** Line 10: `research/il/gaps-v3.0.1/` etc.

### docs/zig-clone.md
- **F5 (High).** Lines 217-221: "Interest (the real stock wall - O(N^2.26) all-pairs, **no spatial index**): grid hash ... **this is the single biggest ceiling raise vs stock (collapses the 450-500p death spiral)**". The 2026-07-20 correction (bottlenecks.md:217-234) argues the wall persists when players cluster because interest is genuinely satisfied, so a grid cannot cull it, for any server. At minimum the clone claim needs the clustered-case caveat; as written it contradicts the correction published the same day.
- **F11 (Medium).** Line 266: "rate limit **~500 ms per IP** on stock (loadgen uses unique 127.x binds)" — no pointer.
- **F14 (Medium).** Line 512: "keep regenerable dumps under `research/il/` policy".
- NetPackage counts (lines 41, 245, 478) use "~194" — consistent with oracle.

### docs/aggressive-optimizations.md
- **F4 (High).** Lines 123, 129: "Chunk pipeline (**56-60% of tick**)", "reclaims most of 56-60% off the tick" — stale vs campaign-final 5%.
- **F11 (Medium).** Line 34: "Entity tick (**~32 s** at 334 zombies)"; line 61: "Network replication (**~15 s**, O(N^2.26))" — units/measurement window (per what interval? aggregate section ms per capture?) are never defined, and no artifact is cited for either number.
- Positive: §2 verdict agrees with the bottlenecks correction; §3 P4 status cites RESULTS §3c-3d.

### docs/allocation-reuse.md
- **F13 (Medium).** Lines 47-53 and 63-69: pooled stream "**mostly self-solved** ... NOT the target — see section 1's correction". Line 121-123 (§4 table, first row): `PooledExpandableMemoryStream byte[] ... | **a** presize + retain | ALLOCATION_UPSTREAM Lever B / this doc` — reinstates the deprecated lever as the first "application to the measured top allocators".
- **F15 (Medium).** Line 6: "128 GB RAM" (vs 123 GB, runtime-tuning).
- **F7 (Medium).** Line 15-16: "one forced collect of a **~7 GB** heap freezes the server **~479 ms**" (third variant of the heap size).

### docs/protocol.md
- **F9 (Medium).** Line 45: `protocol-frames.md#1-challenge-pre-auth-raw-no-envelope` — actual heading is "1. Challenge (raw, before game envelope)" (protocol-frames.md:32); slug does not match. Line 58: `#2-channel-envelope-every-game-message-after-challenge` — actual: "2. Game channel envelope + package stream" (:61). Line 206: `#8-entity-packages-golden-fixed-bodies` — actual §8 is "EntityRelPosAndRot body (!bUseQ) · 20 bytes" (:355); there is no combined "entity packages" section, and §6.1 (PosAndRot, §7 in frames) links to the RelPos section. All three anchors predate the 2026-07-20 frames rewrite.
- **F16 (Low).** Line 276: `damageType:u8 // 3 Bashing, 16 Suffocation, 26 Suicide` vs protocol-frames.md:520 "3 Bash, **16 Drown**, 26 Suicide". One enum, two names for value 16.
- **F14 (Medium).** Lines 9, 90(via network), 142: `research/il/dedi-complete-v3.0.1/`.
- Line 125 "DLL census: **~194**" — the tilde is unnecessary (count is exact) but not wrong; note the family table (lines 129-138) sums to exactly 194.

### docs/protocol-frames.md
- Internally consistent (envelope invariant, §13 full-frame math, §4 hex decode: 0x12BC=4796, 0x12B8=4792, 0xBD=189).
- F16 counterpart (line 520, "Drown").

### docs/loop.md
- **F19 (Low).** Lines 428-435: "## Appendix: key Update caller edges" is followed by a bare ASCII tree (`GameManager.LateUpdate ├─ ...`) that is not opened as a code block but is closed with a stray ``` at line 433. Renders broken.
- **F18 (Low).** Two `## Changelog` blocks (417, 448).
- **F14 (Medium).** Line 379 "not under `research/il/`"; changelog line 421 references `research/docs/`.
- All oracle numbers correct (631, 884, 20 Hz, 189-IL OnUpdateTick, Origin no-op).

### docs/loop-gmupdate.md
- **F26 (Low).** Lines 283-285: "Else if dist² < 225 (~15 m): scale **0.3 or 0.1** (branch picks 0.1 vs 0.3)" — entity-ai.md:155-159 and loop.md:218-222 give the clean bands (<225 → 0.3; else 0.1). The hedged phrasing here reads as a different decode.
- **F17 (Low).** Line 297: "**ProcessPackages** (both channels)".
- **F14 (Medium).** Line 366: example output path `research/il/gmUpdate-v3.0.1`.

### docs/entity-ai.md
- **F20 (Low).** Merge artifacts: §14 "See also" (line 369) plus a second "## See also" (line 392); "## Changelog" (line 396) plus "## Changelog (merged source 2)" (line 661); a second H1 "# Deeper synthesis" mid-file (line 402); line 654: "`SYNTHESIS.md`, this file" — stale name from the pre-merge dump doc.
- **F14 (Medium).** Line 385: regenerate output `../../research/il/deep-VERSION`.
- Addendum measurements (lines 664-695) all cite RESULTS §3m-3q — good provenance; README's 54%/27% claim traces here.

### docs/terrain-height.md
- **F8 (Medium).** Lines 15-17: `../il/terrain-v3.0.1/` = "Dedicated live | **Expanded** on this machine (RealEarth YDim)". coverage.md:10: "**Live pin (2026-07-18 dedi):** stock ... Expanded dumps in `terrain-v3.0.1` are historical." The table's "live/this machine" labels predate the revert to stock; the doc's own line 55 ("Always probe or dump") and changelog line 176 ("note live dedi stock again") acknowledge the issue without fixing the table.
- **F14 (Medium).** Lines 27-29: regenerate paths `../../research/il/terrain-*`.

### docs/closed-gaps.md, docs/world-chunks.md, docs/save-region.md, docs/light-mesh-water.md, docs/managers.md, docs/aidirector.md
- Content numerically consistent with the rest of the corpus (20 Hz decode, AIDirector component order, 64-layer loop, `.ttc`, sector offsets, ModEvents list, manager ILs all cross-check against inventories).
- **F18 (Low).** closed-gaps.md (183+194), world-chunks.md (143+154), light-mesh-water.md (105+115), managers.md (115+125): duplicate `## Changelog` blocks.

### docs/INDEX.md
- **F23 (Low).** "One home per topic" (lines 79-101) omits bottlenecks.md, algorithms.md, aggressive-optimizations.md, allocation-reuse.md (all present in the narratives table, lines 135-139). The NetPackage census effectively has three homes with two different values (network.md ~196, protocol.md ~194, netpackages.md 194) — the ownership table names network.md for "Networking" but the census number was forked. The package-band threshold table is duplicated near-verbatim in five docs (loop.md:279; network.md:55-66; closed-gaps.md §4; protocol-frames.md §14; zig-clone.md §7); only closed-gaps is the declared home.
- Line 4 declares `7days-realworld/` private/unpublished while line 14's tree shows it as a sibling directory; benign but slightly confusing for external readers.

### docs/inventories/*
- **netpackages.md** — the census anchor: line 8 "Count: **194** types with `NetPackage` name prefix in live dedi dump"; table contains exactly 194 rows. Matches oracle. (Note the count includes infrastructure types with the prefix — `NetPackageDirection` (Enum), `NetPackageManager`, `NetPackageEntry`, `NetPackageInfo`, `NetPackageLogger`, `NetPackageMeasure`, `NetPackageMetrics` — which is what "name prefix" honestly states.)
- **gmupdate-calls.md** — **F21 (Low)**: duplicated header blocks (lines 3-5 and 8-10). 182 entries, matching loop.md's claim.
- **manager-updates.md** — **F21 (Low)**: duplicated header blocks (lines 3-5 and 8-11).
- **frame-entries.md** — 242 rows; matches loop.md:59.
- **deeper.md** — **F21 (Low)**: line 4 "Prefer: [`entity-ai.md`], [`entity-ai.md`]" (duplicate); two H1s (lines 1, 9). Threshold constants cross-check against entity-ai.md §3 (0.05, 1225, ±45, 64/225/36/625/3025, updatePlayerList 0.04/2/16/128/192/256/10/100). Consistent.
- **loop-complete.md** — **F25 (Low)**: raw tool output with many duplicated lines (e.g. `AIDirector::ComponentsTick` at 11+13, `WorldState::SaveLoad` x3 at 55-64) and a duplicated section heading (245, 460). Harmless but noisy.
- **gaps.md** — **F25 (Low)**: duplicate headings (`#### callers of AIDirector::.ctor` at 100 and 1515; two `### Annotated EntityFactory::CreateEntity IL=7` at 895/917 for different overloads). Elision placeholders ("raw IL listing elided for publication") are deliberate and fine. §8 classification (33/96/77) consistent with closed-gaps.md §7.
- **opt-scan.md** — **F25 (Low)**: "MISSING `EntityActivity`" (185), "MISSING `Physics`" (234) tool markers; empty "Callers of `World::AddFallingBlocks`" (272-274). IL sizes cross-check cleanly (884, 631, 601, 775, 1236, 846, 1344...).

### README.md
- All highlight numbers trace to in-corpus sources: ~20 Hz (loop.md §3), 0.4% residual (bottlenecks.md:199), 54%/27% (entity-ai.md:690-692), O(N^2.26) (measured-scaling.md §1). No conflicts. Note it inherits F4's tension indirectly by advertising "campaign-final attribution" while three docs still carry the pre-campaign 56-60% figure.

### oss-tools/
- **F22 (Low).** Em dashes: NOTES.md 17 occurrences on lines 65, 176, 204, 218, 237, 257, 309, 313 (x2), 315, 316, 318 (x2), 319, 320, 321 (plus table cells); servertools.md 9 occurrences on lines 98, 115, 132, 146, 154, 162, 170, 176, 180. naiwazi.md: 0. `docs/` and `README.md`: 0.
- No AI-attribution phrasing found anywhere in the corpus (scanned for the usual markers).
- naiwazi.md correctly labels vendor numbers as "Claim only" — good practice. servertools.md:4 and naiwazi.md:118 carry stale `research/...` local paths (F14).

---

## Corrections recommended

- [ ] **F1:** Change "~196" → "194" (or "194 top-level, 199 incl. nested") at coverage.md:58, network.md:73, engine-limitations.md:78, residuals.md:53. Optionally drop the tilde at protocol.md:125 and residuals.md:33 since the count is exact. Keep 189 clearly labeled as the id-map count (already done).
- [ ] **F2:** In bottlenecks.md, rewrite §5 item 1 and Tier 4 #10 to reflect the 2026-07-20 correction (grid helps `GetClosestPlayer`/`SendPackage`, does not collapse the replication wall), or move the old text under a "superseded" marker.
- [ ] **F3:** Fix the bottlenecks.md §6 closing paragraph to not recommend the downgraded #5; promote #6 or #8 instead.
- [ ] **F4:** Reconcile the chunk-pipeline share: either date-scope the 56-60% figure ("pre-campaign instrumentation, 2026-07-19") in bottlenecks.md §1/#9, algorithms.md §5, aggressive-optimizations.md §4, or restate them against the campaign-final 5% with an explanation of the attribution change.
- [ ] **F5:** Update algorithms.md §3/§6 and zig-clone.md §4.2 to carry the "inherent replication / clustered players" caveat from the correction; soften "collapses the 450-500p death spiral".
- [ ] **F6:** In runtime-tuning.md §1, produce a single authoritative honored/not-honored env list and fix the example command (drop `GC_MARKERS`, resolve `GC_PAUSE_TIME_TARGET`'s status).
- [ ] **F7:** Standardize the megapause sentence: "forced full collect of a 6.9 GB (GC-disabled) heap = 479 ms; live working set ~5.6 GB" everywhere (bottlenecks.md:48, allocation-reuse.md:16, runtime-tuning.md:60, zig-clone.md:11).
- [ ] **F8:** Re-label the terrain-height.md dump-set table (terrain-v3.0.1 = historical expanded; live = stock per coverage pin).
- [ ] **F9:** Fix the three anchors in protocol.md to the current protocol-frames.md headings; point PosAndRot (§6.1) at frames §7, RelPos (§6.2) at frames §8.
- [ ] **F10:** Either amend residuals.md's policy sentence to allow "annotation-backlog (managed, dumped, not hand-annotated)" rows, or move the two managed rows into a separate backlog table.
- [ ] **F11:** Add artifact/session pointers (or "unverified" tags) for: ~15 MB/s@128p, 42 findings, 15.16/14.84/14.52 MB/s, ~32 s / ~15 s section costs (define window), ~500 ms join rate limit, the 66 ms in-text figure.
- [ ] **F12:** Pick one form of the UpdateGraphs headline (66 vs 66.6 ms; 340z vs ~300z).
- [ ] **F13:** Remove or annotate the presize+retain row in allocation-reuse.md §4 to match the doc's own correction.
- [ ] **F14:** Sweep the stale `research/il/`, `research/docs/`, `research/naiwazi/`, `research/7dtd-ServerTools` paths to the published layout (`il/`, `docs/`, external).
- [ ] **F15:** Pick 123 or 128 GB for the host RAM.
- [ ] **F16:** Align damageType 16 naming (Suffocation vs Drown) across protocol.md/protocol-frames.md.
- [ ] **F17:** Either substantiate "2 channels" in protocol.md §9 (name channel 1's use) or hedge the "x2 channels" phrasing in bottlenecks/algorithms/loop-gmupdate.
- [ ] **F18:** Merge the duplicate Changelog blocks in the 7 affected docs (fold Related-docs above a single Changelog).
- [ ] **F19:** Fence the loop.md appendix tree properly.
- [ ] **F20/F21:** Clean the merge artifacts in entity-ai.md (single See-also, single Changelog, demote second H1, fix "SYNTHESIS.md, this file"), dedupe front matter in gmupdate-calls.md / manager-updates.md / deeper.md.
- [ ] **F22:** Replace the 26 em dashes in oss-tools/NOTES.md and oss-tools/servertools.md per repo style.
- [ ] **F23:** Add the four missing narratives to the INDEX one-home table; declare closed-gaps.md the single home for band thresholds and netpackages.md for the census, with other docs referencing rather than restating the numbers.
- [ ] **F24:** Note in coverage.md family 8 that the narrative is in the private companion (or add a generic stub); disambiguate the Related-docs INDEX.md row.
- [ ] **F25:** Optionally regenerate/annotate opt-scan.md MISSING markers and the empty callers section.
- [ ] **F26:** Align loop-gmupdate.md §5.4's band phrasing with entity-ai.md §4.

---

## Audit coverage status

- **Read in full:** all 24 `docs/*.md`, all 8 `docs/inventories/*.md`, `README.md`, all 3 `oss-tools/*.md` (36/36 files).
- **Grep-verified corpus-wide:** oracle numerics (194/196/189, 4401, 43901, 631, 884, 20 Hz), em dash character, TODO/FIXME/placeholder markers (none in docs; one benign mention in NOTES.md:186 about placeholder models), `.md#anchor` links (3, all broken), duplicate headings per file, AI-attribution phrasing (none).
- **Not verified (out of scope / not possible from this repo):** external pointers into `7dtd-server-optimizer/docs/RESULTS.md`, `ALLOCATION_UPSTREAM.md`, APM session files, and the private `7days-realworld/` docs — claims delegated to those artifacts were treated as provenanced-if-pointed, unprovenanced otherwise (F11). Link/URL validity was explicitly out of scope per the task ("claims, not links"), except anchors (F9) which are content claims about target sections.

---

## Reconciliation status (2026-07-23, applied)

Ground truth used: `EnumDamageTypes.16 = Suffocation` (DLL); host MemTotal = 123.4 GiB
(128 GB nominal); RESULTS.md:368/484 (56-60% = section-relative, campaign-final
full-tick SendChunks = 5%); RESULTS.md:340 (479 ms = forced collect on 6.9 GB
GC-disabled heap, ~5.6 GB live).

| Finding | Status |
|---|---|
| F1 count 194 | FIXED (coverage/network/engine-limitations/residuals/protocol) |
| F2, F3, F5, F13 | DEFERRED to `7dtd-server-optimizer` (bottlenecks/algorithms/allocation-reuse moved there) |
| F4 chunk % | DEFERRED (moved docs); truth recorded: 56-60% section-relative vs 5% full-tick |
| F6 GC knobs | DEFERRED (runtime-tuning moved) |
| F7 heap size | DEFERRED (moved docs); truth: forced collect 6.9 GB / ~5.6 GB live |
| F8 terrain table | FIXED (relabeled historical/expanded) |
| F9 anchors | FIXED (3 protocol-frames anchors) |
| F10 residuals policy | FIXED (annotation-backlog class added) |
| F11 provenance | PARTIAL: moved-doc cases deferred; 2 stay-doc numbers left flagged (unverified) |
| F12 66 vs 66.6 | DEFERRED (moved docs) |
| F14 stale paths | FIXED (all `research/` -> `il/`/`docs/`/`7dtd-engine-research/`) |
| F15 RAM | DEFERRED (allocation-reuse/runtime-tuning moved); truth: 123.4 GiB / 128 GB nominal |
| F16 damageType 16 | FIXED (Suffocation, DLL-verified) |
| F17 2 channels | RESOLVED (substantiated: channel 1 real, 6 packages) |
| F18-F21, F26 | FIXED (editorial subagent) |
| F22 em dashes | FIXED (oss-tools; 0 repo-wide) |
| F23 one-home | FIXED (INDEX restructure; optimization docs split to companion) |
| F24 family 8 | FIXED (private-companion narrative noted) |
| F25 | SKIPPED (optional auto-dump noise) |

**Scope note:** F2-F7, F12, F13, F15 physically travel with the 6 optimization
docs moved to `7dtd-server-optimizer/docs/`; reconcile them in that repo.
