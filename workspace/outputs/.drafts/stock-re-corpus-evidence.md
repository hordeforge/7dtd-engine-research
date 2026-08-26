# Evidence: stock-re-corpus audit

**Date:** 2026-08-05  
**Repo:** `/home/maci/Desktop/7dtd/7dtd-engine-research`  
**Plan:** `workspace/outputs/.plans/stock-re-corpus.md`  
**Note:** Parent wrote this evidence after the async `researcher` idled post-tooling without writing the draft; all rows below cite commands/files re-run in this session.

## A. Policy / repo surface

| Claim | Evidence | Observation | Status |
|---|---|---|---|
| Working tree clean for research | `git status --short` | empty | match |
| No game DLL / bulk IL in git | `git ls-files \| rg -i 'Assembly-CSharp\|\.dll$\|^il/'` | only `il/README.md`; no DLL tracked | match |
| `il/` gitignored | `.gitignore` | `il/*` present | match |
| Narrative + inventory scale | `ls docs/*.md`; `ls docs/inventories/*.md` | 61 narrative md; 22 inventory md | match |

## B. Pin artifact vs live ASM

| Claim | Evidence | Observation | Status |
|---|---|---|---|
| stock_facts V 3.1.0 b14 pins | `tools/data/stock_facts.json` | major=3 minor=10 build=14; tps=20; netpkg=193; ydim=256 layers=64; save=23; SaveLoad IL=926; gmUpdate=631; types=4414; methods=44107; challenge 0xCA size 17; port 26900; TE payload_len_likely_i32=true | match |
| `make stock-check` | `make stock-check` | `OK: research + sibling pins match stock_facts.json` | match |
| Live re-extract equals committed | `StockFacts.exe` → `/tmp/stock_facts_live.json`; python equal_sans_timestamp | True (only `extracted_utc` differs) | match |
| Live Census | `MONO_PATH=tools/bin mono tools/bin/Census.exe "$ASM"` | TopLevelTypes=4414; MethodsWithBody=44107; AllTypes=7432; NetPackage*=193; SaveLoad=926; gmUpdate=631 | match |
| ASM present | Steam dedicated path | ASM_OK | match |

## C. Doc claim vs pin (version drift)

| Claim | Evidence | Observation | Status |
|---|---|---|---|
| Hub pin V3.1.0 | `docs/INDEX.md` L5; `docs/coverage.md` L1-3; `AGENTS.md` | V3.1.0 (b14) | match |
| README version | `README.md` L3 | still says dedicated server **(V3.0.1)** | **mismatch** |
| re-methodology census table | `docs/re-methodology.md` L52-57 | Top-level 4401, methods 43901, SaveLoad **884** labeled “V3.0.1 baseline” in surrounding prose | ambiguous (historical OK if labeled; SaveLoad still 884 while live 926) |
| coverage.md live census table | `docs/coverage.md` L66-71 | Still 4401 / 43901 / SaveLoad **884** under “Census (live dedi)” despite V3.1.0 banner | **mismatch** |
| Families 1-11 Closed | `docs/coverage.md` table | Status Closed for 1-11 | match (doc claim; not re-proved per family) |
| Coverage metric honesty | `docs/coverage.md` L7-8; `tools/src/Coverage.cs` L175+ | Explicitly “not a coverage metric”; mention-overlap tiers | match (prior Critical framing mitigated in tooling/docs) |
| residuals non-IL only | `docs/residuals.md` §1-3 | Unaccounted 0; open = native/Unity/content/optional annotation | match (doc status) |
| WorldInfo hash tail fixed | `docs/protocol-packages.md` §4.2 L222-231 | `i32 count + count × {string,u32}` + explicit NOT byte-length | match (prior C1 fixed) |
| DynamicMesh dead WriteRegion | `docs/dynamic-mesh.md` L208-236 | Live SaveRegion path; WriteRegion documented dead | match (prior C2 fixed) |
| TE wire in protocol-packages | `docs/protocol-packages.md` §6.12 | teBlockId i32 + payloadLen i32; write IL=27 | match |
| TE wire in tile-entities-power | `docs/tile-entities-power.md` ~L129-132 | Still `payloadLen : u16`, **no teBlockId**; parenthetical claims V3.1 teBlockId+i32 | **mismatch (wire-breaking if followed)** |
| TE live IL | `DumpMethod NetPackageTileEntity write` | IL=27: handle u8, Vector3i, **teBlockId Int32**, Length **conv.i4 Write(Int32)**, WriteTo stream | match experimental-delta + protocol-packages; contradicts tile-entities-power layout |
| Title pins still 3.0.1 | `loop-gmupdate.md`, `protocol-packages.md`, `protocol-frames.md` heads | Titles say V3.0.1 | mismatch (cosmetic / framing) |
| Challenge 0xCA in protocol | stock-check + protocol pin grep | present | match |

## D. Tooling

| Claim | Evidence | Observation | Status |
|---|---|---|---|
| Dumpers present | `tools/src/*.cs` | Census, DumpMethod, DumpType, StockFacts, Coverage, Reach, WireBodies, NetProtocolCensus, Xref, … | match |
| Prebuilt bins | `tools/bin/` | Census/StockFacts/DumpMethod present | match |
| FindCallers | `tools/bin/FindCallers.exe.BROKEN-see-Xref` | Broken; Xref is replacement | match (honest breakage) |
| Coverage numerator | `Coverage.cs` L124-159 | backtick mention in narrative vs inventories vs OOS | match prior critique + current caveat |
| stock pin gate greps limited set | `tools/tests/check_stock_facts.py` | coverage banner, closed-gaps TPS, protocol 0xCA, save version, loadgen GameVersion, zdtd stock_wire, **does not** scan tile-entities-power TE layout or README version | ambiguous (gate passes while stale TE layout remains) |

## E. Consumers

| Claim | Evidence | Observation | Status |
|---|---|---|---|
| zdtd stock_wire | `zdtd-server/src/version.zig` | `stock_wire = "V3.1.0 b14"`; announce `V 3.1.0` | match |
| zdtd challenge/tps | `zdtd-server/src/protocol.zig` | challenge_marker 0xCA; size 17; ticks_per_second 20 | match |
| loadgen GameVersion | `7dtd-loadgen/.../PackageCodec.cs` L87 | `new(1, 3, 10, 14)` | match |
| loadgen dual PackageIds fixtures | PackageCodec golden-wire comments L407-439 | 3.0.1 minor=1 build=4 + 3.1.0 minor=10 build=14; maps=189 | match (doc/TODO) |
| max_mp_players_constant=8 | stock_facts + server-browser-prefabs | Crossplay refuse >8; not absolute dedicated max | ambiguous (name honest if read as constant; easy to misread as hard cap) |

## F. Prior audit residue

| Prior finding | Current status |
|---|---|
| C1 WorldInfo hashes as byte-len | **Fixed** in protocol-packages §4.2 |
| C2 DynamicMesh WriteRegion as live | **Fixed** as dead path in dynamic-mesh.md |
| Coverage % as true coverage | **Mitigated**: Coverage.cs + coverage.md caveat; unaccounted=0 still not “fully narrated” |
| High first-draft error rate | Still relevant process lesson; stock-check does not catch all wire prose |

## Strongest mismatches
1. **`docs/tile-entities-power.md` TE package layout still V3.0.1 (u16, no teBlockId)** while live IL and protocol-packages §6.12 are V3.1.0 i32+teBlockId.
2. **`docs/coverage.md` “Census (live dedi)” table still 3.0.1 numbers** (4401/43901/884) under a 3.1.0 banner.
3. **`README.md` still V3.0.1** while AGENTS/INDEX/coverage pin 3.1.0.
4. Multiple package/loop doc **titles** still V3.0.1.

## Missing code
- None for dumpers required by methodology (except FindCallers → use Xref).
- No public remote “paper URL”; research is local docs + tools.

## Ambiguous defaults
- `max_mp_players_constant: 8` vs configurable ServerMaxPlayerCount / override console cmd.
- re-methodology baseline table: historical vs “live” labeling.
- NetPackage “189 live id-map” runtime observation vs static 193 name census.

## Reproduction risks
1. Third party without Steam dedicated install cannot re-run Census/StockFacts (blocked without ASM).
2. Following `tile-entities-power.md` alone produces a **wire-incompatible** TE reader on 3.1.0.
3. Quoting coverage.md census table as “live 3.1.0” is wrong.
4. stock-check green ≠ all wire narratives consistent.

## Suggested verifier spot-checks
1. Re-read NetPackageTileEntity write IL vs both docs.
2. Confirm stock-check exit 0 and that it does not mention tile-entities-power.
3. Confirm WorldInfo and DynamicMesh fix text still present.
4. Confirm zdtd/loadgen pins still match JSON.
5. Confirm no Assembly-CSharp in git.
