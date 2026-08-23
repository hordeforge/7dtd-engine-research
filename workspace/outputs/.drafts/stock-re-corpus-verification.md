# Verification report: stock-re-corpus

**Date:** 2026-08-05  
**Role:** Feynman verifier (fresh context; re-checked primary paths)  
**Plan:** `workspace/outputs/.plans/stock-re-corpus.md`  
**Evidence draft:** `workspace/outputs/.drafts/stock-re-corpus-evidence.md`  
**Repo:** `/home/maci/Desktop/7dtd/7dtd-engine-research`  
**ASM:** `$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` (present, 11579904 bytes, mtime Aug 2 21:25)

This report re-runs load-bearing checks. It does not trust the parent summary. Status codes: **pass** / **fail** / **blocked** / **ambiguous**.

---

## Method

1. Read plan + evidence draft.  
2. Re-run `make stock-check`, live `Census.exe`, live `StockFacts.exe`, `DumpMethod NetPackageTileEntity write`.  
3. File reads / greps on docs, `stock_facts.json`, zdtd, loadgen, git policy.  
4. Compare each evidence-draft claim to independent results; flag draft errors.

---

## Claim table

| # | Claim | Source path | Check performed | Result | Citation |
|---|---|---|---|---|---|
| 1 | Working tree has no tracked game DLL / bulk IL | `.gitignore`, git index | `git ls-files \| rg -i 'Assembly-CSharp\|\.dll$\|^il/'` | **pass** | Only `il/README.md` tracked; `.gitignore:2` has `il/*`; no `Assembly-CSharp` |
| 2 | `il/` is gitignored | `.gitignore` | read + rg | **pass** | `.gitignore:2` `il/*` |
| 3 | ~61 narrative docs, ~22 inventory docs | `docs/` | `ls docs/*.md \| wc -l`; inventories | **pass** | 61 narrative md; 22 inventory md |
| 4 | Display version V 3.1.0 (b14): Major=3 Minor=10 Build=14 | `tools/data/stock_facts.json` | python load JSON | **pass** | `version.major=3`, `minor=10`, `build=14`, `display='V 3.1.0'`, `stock_wire='V3.1.0 b14'` |
| 5 | Census pins: types 4414, methods 44107, gmUpdate 631, SaveLoad 926, NetPackage* 193 | stock_facts + live Census | `mono tools/bin/Census.exe "$ASM"` | **pass** | Live: TopLevelTypes=4414; MethodsWithBody=44107; NetPackage*=193; SaveLoad=926; gmUpdate=631. Matches `census` + `save.worldstate_saveload_stream_il` in JSON |
| 6 | Sim 20 TPS / 50 ms | stock_facts, closed-gaps, loop | JSON + rg | **pass** | `sim.constants_ticks_per_second=20`, `tick_duration_sec=0.05`; `docs/closed-gaps.md:24-26`; `docs/loop.md:228` |
| 7 | Chunk 16×256×16, 64 layers × 4 height | stock_facts | JSON | **pass** | `chunk.block_x/y/z_dim=16/256/16`, `block_layers=64`, `layer_height=4` |
| 8 | `CurrentSaveVersion=23` | stock_facts, save-region | JSON + rg | **pass** | `save.current_save_version=23`; `docs/save-region.md:85` |
| 9 | Default port 26900; challenge `0xCA` size 17 | stock_facts, protocol.md, zdtd | JSON + rg | **pass** | `network.default_port=26900`, `challenge_marker_hex='0xCA'`, `challenge_size=17`; `zdtd-server/src/protocol.zig:11-12` |
| 10 | TE wire: teBlockId i32 + payloadLen i32; write IL=27 | live DumpMethod, protocol-packages §6.12, stock_facts | `DumpMethod NetPackageTileEntity write` | **pass** (IL + protocol-packages + JSON) | IL writes `teBlockId Int32`, `Length conv.i4 Write(Int32)`; `docs/protocol-packages.md:698-712`; `tile_entity_package.write_il=27`, `payload_len_likely_i32=true` |
| 11 | `make stock-check` passes against committed JSON | Makefile / stock-sync | `make stock-check` | **pass** | Exit 0: `OK: research + sibling pins match stock_facts.json` |
| 12 | Live StockFacts re-extract equals committed (sans timestamp) | StockFacts.exe | write `/tmp/stock_facts_live.json`; python equality | **pass** | `equal_sans_timestamp True` |
| 13 | Dumpers present; FindCallers broken | `tools/src`, `tools/bin` | ls | **pass** | Census/DumpMethod/StockFacts/Coverage/Xref present; `FindCallers.exe.BROKEN-see-Xref` |
| 14 | Hub pin V3.1.0 (INDEX / coverage / AGENTS) | docs | rg / head | **pass** | `docs/INDEX.md:5`; `docs/coverage.md:1-3`; research `AGENTS.md` scope |
| 15 | README still pins V3.0.1 | `README.md` | head | **fail** (mismatch present) | `README.md:3` "dedicated server **(V3.0.1)**" |
| 16 | coverage.md “Census (live dedi)” uses 3.1.0 numbers | `docs/coverage.md` | read L62-71 vs live Census | **fail** | Table: types **4401**, methods **43901**, SaveLoad **884** under V3.1.0 banner; live is 4414 / 44107 / 926. gmUpdate 631 still correct |
| 17 | re-methodology census table is V3.0.1 baseline | `docs/re-methodology.md` | read L48-57 | **ambiguous** (honest if labeled historical) | Explicitly “V3.0.1 baseline”; values 4401/43901/884; not claimed as live 3.1.0 |
| 18 | Families 1-11 Closed in coverage table | `docs/coverage.md` | read L31-43 | **pass** (doc status only; not re-proved) | Status column Closed for rows 1-11 |
| 19 | Coverage tool is mention-overlap, not true coverage | coverage.md, Coverage.cs | rg | **pass** | `docs/coverage.md:8`; `tools/src/Coverage.cs:175` “This is not a coverage metric.” |
| 20 | residuals: managed unaccounted 0; open = non-IL | `docs/residuals.md` | read §1-3 | **pass** (doc status) | L73 “Unaccounted … **0**”; §1 native/Unity/content only |
| 21 | WorldInfo worldHashes is count-not-length | `docs/protocol-packages.md` §4.2 | read L222-231 | **pass** | “NOT a byte-length blob”; “entry count, not a byte length” |
| 22 | DynamicMesh live path is SaveRegion; WriteRegion dead | `docs/dynamic-mesh.md` | read L208-236 | **pass** | Live `SaveRegion`; “Dead legacy path … WriteRegion … have **no callers**” |
| 23 | protocol-packages §6.12 TE layout matches live IL | protocol-packages + DumpMethod | cross-check | **pass** | §6.12: teBlockId i32, payloadLen i32, write=27; matches IL |
| 24 | tile-entities-power TE package layout matches live IL | `docs/tile-entities-power.md` | read L126-132 vs IL | **fail** | Parenthetical says V3.1 teBlockId+i32, but layout still `payloadLen : u16`, **no teBlockId**, write IL=**23** (stale) |
| 25 | stock-check does not scan TE layout / README version | `tools/tests/check_stock_facts.py` | rg script + green exit | **pass** (as limitation claim) | Greps coverage banner, 0xCA, save version, loadgen GameVersion, zdtd stock_wire; no tile-entities-power / README.md version pin |
| 26 | zdtd version/protocol pins match stock_facts | `zdtd-server/src/version.zig`, `protocol.zig` | rg | **pass** | `stock_wire = "V3.1.0 b14"`; announce `V 3.1.0`; `challenge_marker=0xCA`; size 17; `ticks_per_second=20` |
| 27 | loadgen GameVersion = (1,3,10,14) | `7dtd-loadgen/.../PackageCodec.cs` | rg | **pass** | L87: `new(1, 3, 10, 14) // … V3.1.0 (b14)` |
| 28 | loadgen dual PackageIds fixtures 3.0.1 + 3.1.0; maps=189 | PackageCodec.cs | rg L407-439 | **pass** | Comments + checks: minor=1 build=4 and minor=10 build=14; map count 189 |
| 29 | Package titles still say V3.0.1 (protocol-packages, protocol-frames, loop-gmupdate) | docs heads | head | **fail** (framing drift) | Titles: protocol-packages “V3.0.1”; protocol-frames “V3.0.1”; loop-gmupdate “V3.0.1” while body may mix 3.1 content |
| 30 | max_mp_players_constant=8 is Crossplay refuse, not absolute dedi max | stock_facts, evidence | JSON only here | **ambiguous** | JSON has `max_mp_players_constant: 8`; full semantic not re-proved this run |
| 31 | NetPackage static name census 193 vs ~189 live id-map | coverage.md, loadgen | doc + fixture | **ambiguous** (as stated) | Static Census 193; loadgen fixture maps=189; coverage already labels 189 as runtime observation |

---

## Evidence draft audit (false positives / negatives)

| Evidence draft item | Verifier result | Draft error? |
|---|---|---|
| stock-check OK | Confirmed exit 0 | No |
| Live Census 4414/44107/193/926/631 | Confirmed | No |
| Live StockFacts equals committed | Confirmed | No |
| README V3.0.1 mismatch | Confirmed | No |
| coverage.md live census still 4401/43901/884 | Confirmed | No |
| tile-entities-power u16 / no teBlockId | Confirmed; also stale write IL=23 vs live 27 | No (draft understated IL number mismatch) |
| protocol-packages §6.12 correct | Confirmed | No |
| WorldInfo count-not-length fixed | Confirmed | No |
| DynamicMesh WriteRegion dead / SaveRegion live | Confirmed | No |
| zdtd / loadgen pins | Confirmed | No |
| No Assembly-CSharp in git | Confirmed | No |
| re-methodology “ambiguous historical” | Confirmed labeled “V3.0.1 baseline” | No |
| Coverage metric honesty mitigated | Confirmed caveats in doc + tool | No |
| residuals unaccounted 0 | Confirmed as **doc claim**; not re-run Coverage.exe this session | Minor: draft says “match (doc status)” which is correct; do not upgrade to live Coverage proof |
| Families Closed | Doc-only | No overclaim in draft |
| Narrative scale 61/22 | Confirmed | No |
| stock-check blind to TE layout | Confirmed | No |

**No false positives found** in the evidence draft’s strongest mismatches.  
**No false negatives** on P0 pins: they re-verified.  
**Small draft understatement:** tile-entities-power also cites write IL=23 and omits teBlockId entirely in the layout block, while live IL=27; evidence focused on u16/i32 and missing field (correct severity).

---

## Severity summary

| Severity | Item |
|---|---|
| **Critical (wire)** | `docs/tile-entities-power.md` TE package layout still V3.0.1-shaped (`payloadLen:u16`, no `teBlockId`, IL=23). Following this layout alone yields a wire-incompatible TE reader on V3.1.0. Canonical fix already in `protocol-packages.md` §6.12 + `experimental-delta.md` §2 + live IL. |
| **High (quantitative doc drift)** | `docs/coverage.md` “Census (live dedi)” table still reports 4401 / 43901 / SaveLoad 884 under a V3.1.0 banner. Live Census: 4414 / 44107 / 926. |
| **Medium (framing)** | `README.md:3` still “V3.0.1”; several doc titles (protocol-packages, protocol-frames, loop-gmupdate) still V3.0.1. |
| **Low / process** | `stock-check` green does not imply all wire narratives consistent; gate does not read tile-entities-power layout or README version string. |
| **Info (historical OK)** | re-methodology census table labeled V3.0.1 baseline is acceptable if not quoted as live 3.1.0. |

---

## Claims safe to cite

- Machine pin `tools/data/stock_facts.json` for V 3.1.0 (b14): version triple (3,10,14), tps 20, chunk 16×256×16 / 64×4, save version 23, census 4414/44107/631, SaveLoad IL 926, NetPackage top-level 193, port 26900, challenge 0xCA/17, TE payload_len_likely_i32.  
- Live Census and live StockFacts match that JSON on this host (ASM present).  
- `make stock-check` / `check_stock_facts.py` exit 0.  
- TE **canonical** wire: `docs/protocol-packages.md` §6.12 and live `NetPackageTileEntity.write` IL=27 (handle u8, Vector3i, teBlockId i32, payloadLen i32, payload).  
- WorldInfo `worldHashes` leading i32 is **entry count**, not byte length (`protocol-packages.md` §4.2).  
- DynamicMesh live save is `SaveRegion` / deflate `.group`; `WriteRegion` is dead with no callers (`dynamic-mesh.md`).  
- Consumer pins: zdtd `stock_wire` / challenge / ticks; loadgen `GameVersion = new(1, 3, 10, 14)`.  
- Policy: no Assembly-CSharp or bulk `il/` dumps tracked in git.  
- Coverage tooling disclaimer: not a true coverage metric (mention-overlap).  
- residuals.md **states** managed unaccounted 0 and non-IL-only open list (cite as doc status, not as a re-run Coverage proof unless Coverage.exe is re-executed).

## Claims that must not be cited without fix

- Any claim that **`docs/tile-entities-power.md`** is the authoritative V3.1.0 TE package layout (u16 length, no teBlockId).  
- Any claim that **`docs/coverage.md` “Census (live dedi)”** numbers are live V3.1.0 (4401/43901/884 are V3.0.1-era).  
- Any claim that the **repo README** correctly pins the current research game version (still V3.0.1).  
- Package/loop **titles** that say V3.0.1 as if they were the current corpus pin (cosmetic but misleading in bibliographies).  
- “stock-check passed ⇒ all wire docs consistent” (false).  
- Do not cite **unaccounted=0** as live-tool-proved without re-running Coverage against current docs+ASM in the same breath.

## Residual uncertainty

- Full re-proof of all family “Closed” rows was out of scope; only pin/tooling/consumer/known-critical narrative fixes were re-checked.  
- `max_mp_players_constant=8` semantics (Crossplay refuse vs hard dedi max) not re-traced in IL this run.  
- Exact “189 registered wire packages” remains a runtime/id-map observation; static name census is 193.  
- re-methodology baseline table is fine historically; third parties may still confuse it with live pins if they skip the “V3.0.1 baseline” label.  
- Third party without Steam dedicated ASM cannot re-run Census/StockFacts/DumpMethod (blocked).  
- tile-entities-power parenthetical already points at §6.12, so a careful reader can recover; a layout-table skimmer cannot.

---

## Commands run (this session)

```text
make stock-check
  -> OK: research + sibling pins match stock_facts.json (exit 0)

MONO_PATH=tools/bin mono tools/bin/Census.exe "$ASM"
  -> TopLevelTypes=4414 MethodsWithBody=44107 NetPackage*=193
     WorldState.SaveLoad(Stream)=926 GameManager.gmUpdate IL=631

MONO_PATH=tools/bin mono tools/bin/DumpMethod.exe "$ASM" NetPackageTileEntity write
  -> IL=27; Write(Int32) teBlockId; conv.i4 Write(Int32) length; WriteTo stream

MONO_PATH=tools/bin mono tools/bin/StockFacts.exe "$ASM" /tmp/stock_facts_live.json
  -> equal_sans_timestamp True vs tools/data/stock_facts.json

git ls-files | rg -i 'Assembly-CSharp|\.dll$|^il/'
  -> il/README.md only

python3 tools/tests/check_stock_facts.py
  -> OK (exit 0)
```

---

## Sources (local paths)

1. `workspace/outputs/.plans/stock-re-corpus.md`  
2. `workspace/outputs/.drafts/stock-re-corpus-evidence.md`  
3. `tools/data/stock_facts.json`  
4. `tools/tests/check_stock_facts.py`  
5. `tools/stock-sync.sh` / root `Makefile` (`stock-check`)  
6. Live ASM via `tools/bin/Census.exe`, `StockFacts.exe`, `DumpMethod.exe`  
7. `docs/coverage.md`  
8. `docs/protocol-packages.md` (§4.2 WorldInfo, §6.12 TE)  
9. `docs/tile-entities-power.md` (stale TE layout)  
10. `docs/dynamic-mesh.md` (SaveRegion live / WriteRegion dead)  
11. `docs/re-methodology.md` (V3.0.1 baseline census)  
12. `docs/residuals.md`  
13. `docs/experimental-delta.md` (TE wire delta table)  
14. `docs/INDEX.md`, `README.md`  
15. `zdtd-server/src/version.zig`, `zdtd-server/src/protocol.zig`  
16. `7dtd-loadgen/src/LoadGen/PackageCodec.cs`  
17. `.gitignore`, git index  

---

## Parent handoff note

Do **not** treat this file as the final audit artifact. Parent should synthesize `workspace/outputs/stock-re-corpus-audit.md` from plan + evidence + this verification. Highest-priority fix recommendations for a later edit pass (not done here): (1) rewrite tile-entities-power TE layout to match §6.12/IL, (2) refresh coverage.md live census table to 4414/44107/926, (3) bump README (and optional titles) to V3.1.0 (b14), (4) optionally extend stock-check to fail on TE layout / README pin drift.
