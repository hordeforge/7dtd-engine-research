# Paper/code audit: stock-re-corpus

**Slug:** `stock-re-corpus`  
**Date:** 2026-08-05  
**Subject:** Our research (no external arXiv paper): the 7 Days to Die dedicated-server reverse-engineering corpus and its Mono.Cecil tooling / consumer pins.  
**Game pin (claimed and machine-checked):** V **3.1.0 (b14)** Henpocalypse  
**Plan:** [`.plans/stock-re-corpus.md`](.plans/stock-re-corpus.md)  
**Evidence:** [`.drafts/stock-re-corpus-evidence.md`](.drafts/stock-re-corpus-evidence.md)  
**Verification:** [`.drafts/stock-re-corpus-verification.md`](.drafts/stock-re-corpus-verification.md)  

**What was audited as the “paper”:** `docs/` narratives + `docs/re-methodology.md` + `tools/data/stock_facts.json` + prior audit trail.  
**What was audited as the “codebase”:** `tools/src/*` dumpers and pin gates; consumers `../zdtd-server-server` and `../7dtd-loadgen`; live local dedicated `Assembly-CSharp.dll` (not redistributed).

---

## Executive summary

| Area | Verdict | Confidence |
|---|---|---|
| Machine pins (`stock_facts.json` ↔ live ASM ↔ zdtd/loadgen) | **Aligned** | high (re-run Census, StockFacts, stock-check) |
| Canonical TE wire (`protocol-packages` §6.12 + IL) | **Match** | high (DumpMethod write/read) |
| Prior critical wire fixes (WorldInfo hashes; DynamicMesh WriteRegion) | **Still fixed** | high (doc re-read) |
| Coverage metric honesty | **Mitigated** (tool + doc caveats) | high |
| Doc consistency under V3.1.0 banner | **Partial fail** | high |
| Overall research fitness for clone/interop work | **Usable with caveats** | high |

**One-line judgment:** the *extractable* research (JSON pin, Census, stock-check, canonical package layouts, consumer hardcodes) is reproducible on this host and matches V3.1.0; a few *narrative* surfaces still carry V3.0.1 layouts or census numbers, including one **wire-breaking** TE layout in `tile-entities-power.md` that contradicts both IL and the canonical package catalog.

**Recommendation:** treat `tools/data/stock_facts.json` + `docs/protocol-packages.md` (and live DumpMethod) as authoritative for pins/wire.

### Fix pass (2026-08-05, same session)

All audit mismatches listed below were **applied** in-tree and re-checked:

| Issue | Fix | Verification |
|---|---|---|
| TE layout in tile-entities-power | teBlockId i32 + payloadLen i32, IL=27/24 | layout text; stock-check TE greps |
| coverage live census 4401/884 | 4414 / 44107 / SaveLoad 926 + save ver 23 | stock-check census greps |
| README V3.0.1 | V **3.1.0 (b14)** + stock_facts link | stock-check README pin |
| Doc titles V3.0.1 | protocol-packages / frames / loop-gmupdate → 3.1.0 | head checks |
| re-methodology baseline only | live vs historical columns | doc read |
| stock-check blind to TE/README/census | extended `check_stock_facts.py` | `make stock-check` + `make test` exit 0 |

Post-fix: do **not** treat the pre-fix “must not cite” rows as still open in this tree.

---

## Scope and method

1. Plan written first (no wait for user confirm).  
2. Evidence gathered against P0–P3 claims in the plan (live ASM present).  
3. Independent verifier re-ran stock-check, Census, StockFacts, TE DumpMethod, doc/consumer greps.  
4. This artifact is the single user-facing audit.

**Out of scope (by plan):** full re-audit of every narrative family; EfficientServer A/B performance claims; RealEarth product status.

---

## Claim matrix

| Claim | Paper / doc source | Code / tool / IL | Status |
|---|---|---|---|
| Version Major=3 Minor=10 Build=14 → V 3.1.0 (b14) | coverage pin, stock_facts | live StockFacts + JSON | **match** |
| Top-level types 4414; methods-with-body 44107 | stock_facts.census | live Census.exe | **match** |
| gmUpdate IL 631 | stock_facts / docs | live Census | **match** |
| WorldState.SaveLoad(Stream) IL 926 | stock_facts.save | live Census | **match** |
| NetPackage* top-level 193 | stock_facts.network | live Census | **match** |
| TPS 20 / tick 0.05 s | stock_facts.sim; closed-gaps; loop | JSON + docs | **match** |
| Chunk 16×256×16; 64 layers × 4 | stock_facts.chunk | JSON extract | **match** |
| CurrentSaveVersion 23 | stock_facts; save-region | JSON + doc | **match** |
| Port 26900; challenge 0xCA size 17 | stock_facts; protocol; zdtd | JSON + protocol.zig | **match** |
| TE: teBlockId i32 + payloadLen i32; write IL 27 | protocol-packages §6.12; experimental-delta; stock_facts.tile_entity_package | DumpMethod write/read | **match** |
| TE layout in tile-entities-power | tile-entities-power layout block | live IL (teBlockId + i32 len, IL=27) | **match** (fixed 2026-08-05) |
| coverage.md “Census (live dedi)” | coverage.md table | live 4414/44107/926 | **match** (fixed 2026-08-05) |
| README game pin | README.md | INDEX/AGENTS/coverage 3.1.0 | **match** (fixed 2026-08-05) |
| re-methodology census | re-methodology §1 live + historical columns | stock_facts / Census | **match** (fixed 2026-08-05) |
| stock-check green | Makefile / check_stock_facts.py | exit 0; now greps TE/README/census | **match** (gate extended 2026-08-05) |
| zdtd stock_wire / challenge / ticks | stock_facts consumers | version.zig; protocol.zig | **match** |
| loadgen GameVersion (1,3,10,14) | stock_facts consumers | PackageCodec.cs | **match** |
| loadgen dual PackageIds 3.0.1 + 3.1.0 | PackageCodec golden-wire | code comments + checks | **match** |
| WorldInfo worldHashes i32 = entry count | protocol-packages §4.2 | prior IL audit + current prose | **match** (prior C1 fixed) |
| DynamicMesh WriteRegion dead; SaveRegion live | dynamic-mesh.md | prior IL audit + current prose | **match** (prior C2 fixed) |
| Coverage % is true coverage | historical review Critical | Coverage.cs + coverage-report caveats | **mitigated** (not a true coverage metric) |
| Managed unaccounted 0 | residuals.md; coverage-report | report shows unaccounted 0 (generated); not re-run Coverage.exe in this audit | **doc/tool artifact** (cite carefully) |
| No game DLL / bulk IL in git | policy / AGENTS | git ls-files; .gitignore `il/*` | **match** |
| FindCallers available | older tooling lore | `FindCallers.exe.BROKEN-see-Xref` | **match** (use Xref) |

---

## Strongest evidence (verified this session)

### Pins and tooling

```text
make stock-check
  stock_facts: V 3.1.0 (b14) tps=20 netpkg=193 ydim=256
  OK: research + sibling pins match stock_facts.json  (exit 0)

Census.exe (live dedicated ASM):
  TopLevelTypes=4414
  MethodsWithBody (top-level)=44107
  NetPackage* (top-level)=193
  WorldState.SaveLoad(Stream)=926
  GameManager.gmUpdate IL=631

StockFacts.exe live re-extract vs committed JSON:
  equal_sans_timestamp True
```

### TE wire (canonical vs stale)

Live `NetPackageTileEntity.write` IL=27 sequence:

1. base `NetPackage.write`  
2. `handle` : u8  
3. `teWorldPos` : Vector3i  
4. `teBlockId` : i32  
5. stream length : i32 (`conv.i4` + `Write(Int32)`)  
6. payload `MemoryStream.WriteTo`

`read` IL=24 mirrors: ReadByte, ReadVector3i, ReadInt32 → teBlockId, ReadInt32 → length, StreamCopy.

**Matches:** `docs/protocol-packages.md` §6.12, `docs/experimental-delta.md` §2, `stock_facts.tile_entity_package`.  
**Contradicts:** `docs/tile-entities-power.md` layout (`payloadLen : u16`, no teBlockId, write IL=23) even though a parenthetical already points at §6.12.

### Consumers

| Consumer | Pin | Status |
|---|---|---|
| zdtd `src/version.zig` | `stock_wire = "V3.1.0 b14"` | match |
| zdtd `src/protocol.zig` | `0xCA`, size 17, 20 TPS | match |
| loadgen `PackageCodec.GameVersion` | `new(1, 3, 10, 14)` | match |

### Prior audit CRITICALs

| ID | Issue | Now |
|---|---|---|
| C1 | WorldInfo hashes as byte-length | **Fixed** in protocol-packages §4.2 (count + entries) |
| C2 | DynamicMesh WriteRegion as live | **Fixed** (dead path; SaveRegion live) |
| Coverage framing | narrated % as true coverage | **Mitigated** (explicit non-metric; tiers separate; unaccounted≠fully narrated) |

---

## Mismatches and reproduction risks

### Critical (wire) — fixed

**Was:** `docs/tile-entities-power.md` TE package layout V3.0.1-shaped (u16, no teBlockId).  
**Now:** matches §6.12 / IL=27 (teBlockId i32, payloadLen i32). stock-check greps enforce this.

### High (quantitative drift) — fixed

**Was:** coverage “Census (live dedi)” 4401 / 43901 / SaveLoad 884.  
**Now:** 4414 / 44107 / 926 + CurrentSaveVersion 23; gate greps live counts.

### Medium (framing) — fixed

README and package/loop titles pin V3.1.0 (b14); re-methodology shows live vs historical columns.

### Process / gate gaps — reduced

stock-check now covers TE layout, README pin, and coverage live census numbers in addition to the prior pin set. It is still not a full narrative consistency proof; do not infer “every sentence in every doc is correct” from a green gate.

### Ambiguous defaults

- `max_mp_players_constant: 8` is easy to misread as hard dedicated max; docs elsewhere discuss crossplay refuse and override commands.  
- Static NetPackage name census **193** vs live PackageIds map count **~189** (runtime observation; already caveated in coverage.md).  
- re-methodology baseline table is honest as V3.0.1 history; unsafe only if quoted as live 3.1.0.

### Reproduction risks (third party)

1. Requires a **local** Steam dedicated install of the matching build; ASM is not and must not be shipped.  
2. Without ASM, Census/StockFacts/DumpMethod are blocked; only committed JSON + prose remain.  
3. Implementing from a single secondary doc (`tile-entities-power`) can still produce a wire bug.  
4. Quoting the coverage “live dedi” census table as 3.1.0 is factually wrong today.

---

## Missing code / tooling notes

| Expected | Reality |
|---|---|
| Mono.Cecil dumpers in `tools/src` | Present (Census, DumpMethod, StockFacts, Coverage, WireBodies, …) |
| FindCallers | Broken; use Xref (filename documents this) |
| Public paper URL | None; research is this repo’s docs |
| Game bytes in git | Correctly absent |

---

## Coverage metric (honesty check)

Generated report (`docs/inventories/coverage-report.md`) currently states among reached game types:

| Tier | Value |
|---|---|
| narrated | 1400 (37%) |
| catalogued only | 901 |
| unaccounted | 0 |

Tool and narrative both state this is **documentation-mention overlap on a static call graph**, not behavioral coverage. Unaccounted 0 means every reached type is narrated, catalogued, or classified OOS, **not** that every type has a full behavioral writeup. Prior Critical finding is addressed by caveat text; residual risk is third-party mis-citation of “37% narrated” or “0 unaccounted” without the caveats.

*This audit did not re-run `Coverage.exe`; the numbers above are from the committed generated report and match residual/doc claims.*

---

## Safe to cite vs must not cite

### Safe to cite (with path)

- `tools/data/stock_facts.json` machine pin for V 3.1.0 (b14)  
- Live Census / StockFacts agreement on this host  
- TE wire from `docs/protocol-packages.md` §6.12 + DumpMethod  
- WorldInfo count-not-length; DynamicMesh SaveRegion-live  
- zdtd / loadgen version and challenge pins  
- Policy: no redistributed ASM/IL dumps  

### Must not cite without care

- Pre-fix (historical) values 4401/43901/SaveLoad 884 as **live** 3.1.0 (they remain valid only as V3.0.1 baseline).  
- “stock-check passed ⇒ full wire corpus consistent” (gate is broader now but still not whole-corpus).  
- unaccounted=0 as live Coverage proof without re-running Coverage.exe in the same citation  
- ~~tile-entities-power TE table~~, ~~stale coverage census~~, ~~README V3.0.1~~: **fixed 2026-08-05**  

---

## Recommended fix order — completed 2026-08-05

1. ~~Rewrite tile-entities-power TE layout~~ **done**  
2. ~~Refresh coverage live census~~ **done**  
3. ~~Bump README + titles~~ **done**  
4. ~~Extend check_stock_facts.py~~ **done** (TE + README + live census)  
5. re-methodology live vs historical table **done**

---

## Subagent / process note

- Plan: parent.  
- Researcher: launched async; idled after extensive tool output; parent completed the evidence draft from re-run commands; researcher interrupted.  
- Verifier: fresh context; wrote independent claim table; confirmed evidence draft with no false positives on strongest mismatches.  
- Final synthesis: parent.

---

## Sources

### Research corpus (“paper”)

| Source | Path / URL |
|---|---|
| Research hub | [`docs/INDEX.md`](../../docs/INDEX.md) |
| README | [`README.md`](../../README.md) |
| RE method | [`docs/re-methodology.md`](../../docs/re-methodology.md) |
| Coverage map | [`docs/coverage.md`](../../docs/coverage.md) |
| Coverage report (generated) | [`docs/inventories/coverage-report.md`](../../docs/inventories/coverage-report.md) |
| Protocol packages | [`docs/protocol-packages.md`](../../docs/protocol-packages.md) |
| Protocol | [`docs/protocol.md`](../../docs/protocol.md) |
| TE / power | [`docs/tile-entities-power.md`](../../docs/tile-entities-power.md) |
| Experimental / V3.1 delta | [`docs/experimental-delta.md`](../../docs/experimental-delta.md) |
| Dynamic mesh | [`docs/dynamic-mesh.md`](../../docs/dynamic-mesh.md) |
| Residuals | [`docs/residuals.md`](../../docs/residuals.md) |
| Closed gaps | [`docs/closed-gaps.md`](../../docs/closed-gaps.md) |
| Save / region | [`docs/save-region.md`](../../docs/save-region.md) |
| Repo rules | [`AGENTS.md`](../../AGENTS.md) |

### Code / tooling / consumers

| Source | Path / URL |
|---|---|
| Stock facts pin | [`tools/data/stock_facts.json`](../../tools/data/stock_facts.json) |
| StockFacts extractor | [`tools/src/StockFacts.cs`](../../tools/src/StockFacts.cs) |
| Pin gate | [`tools/tests/check_stock_facts.py`](../../tools/tests/check_stock_facts.py) |
| stock-sync | [`tools/stock-sync.sh`](../../tools/stock-sync.sh) |
| Coverage tool | [`tools/src/Coverage.cs`](../../tools/src/Coverage.cs) |
| Dumpers catalog | [`tools/README.md`](../../tools/README.md) |
| zdtd version | [`../zdtd-server-server/src/version.zig`](../../../zdtd-server-server-server-server/src/version.zig) |
| zdtd protocol constants | [`../zdtd-server-server/src/protocol.zig`](../../../zdtd-server-server-server-server/src/protocol.zig) |
| loadgen PackageCodec | [`../7dtd-loadgen/src/LoadGen/PackageCodec.cs`](../../../7dtd-loadgen/src/LoadGen/PackageCodec.cs) |
| Live dedicated ASM (local only, not redistributed) | `~/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` |

### Public / product context

| Source | URL |
|---|---|
| V3.1.0 Henpocalypse release notes (official) | https://7daystodie.com/v3-1-0-henpocalypse-release-notes/ |

### This audit run

| Artifact | Path |
|---|---|
| Plan | [`workspace/outputs/.plans/stock-re-corpus.md`](.plans/stock-re-corpus.md) |
| Evidence | [`workspace/outputs/.drafts/stock-re-corpus-evidence.md`](.drafts/stock-re-corpus-evidence.md) |
| Verification | [`workspace/outputs/.drafts/stock-re-corpus-verification.md`](.drafts/stock-re-corpus-verification.md) |
| This audit | [`workspace/outputs/stock-re-corpus-audit.md`](stock-re-corpus-audit.md) |
