# Audit plan: stock-re-corpus

**Slug:** `stock-re-corpus`  
**Date:** 2026-08-05  
**Mode:** paper/code audit of *our* research (not a third-party arXiv paper)  
**Output:** `workspace/outputs/stock-re-corpus-audit.md` (canonical under this repo’s outputs convention)

## What counts as the “paper”

There is no external academic paper. The publishable research surface is:

| Layer | Path | Role |
|---|---|---|
| Hub / claims index | `docs/INDEX.md`, `README.md` | Scope, version pin, reading paths |
| Method | `docs/re-methodology.md` | How IL is dumped and turned into wire layouts |
| Coverage ledger | `docs/coverage.md`, `docs/full-surface.md` | What is mapped; residual honesty |
| Load-bearing narratives | `docs/protocol*.md`, `docs/loop.md`, `docs/save-region.md`, `docs/entity-ai.md`, `docs/residuals.md` | Wire/sim/save claims |
| Pin artifact | `tools/data/stock_facts.json` | Machine-extractable constants consumers must match |
| Prior audits | `workspace/outputs/*audit*`, `7dtd-re-corpus-review.md` | Known critical findings and metric critique |

**Subject of study (not redistributed):** local Steam dedicated `Assembly-CSharp.dll` V 3.1.0 (b14).

## What counts as the “codebase”

| Component | Path | Check against |
|---|---|---|
| Mono.Cecil dumpers | `tools/src/*.cs`, `tools/build.sh` | Method claims in re-methodology |
| Stock pin gate | `tools/src/StockFacts.cs`, `tools/stock-sync.sh`, `tools/tests/check_stock_facts.py`, root `Makefile` | JSON fields vs live ASM when present |
| Coverage tooling | `tools/src/Coverage.cs`, `Reach.cs`, `FullSurface.cs` | Whether “narrated %” measures what docs claim |
| External consumer: zdtd | `../zdtd-server-server/src/version.zig`, `protocol.zig`, wire/TE paths | stock_facts consumers list |
| External consumer: loadgen | `../7dtd-loadgen` PackageIds / GameVersion / golden-wire | Version + package count pins |
| Policy | `.gitignore`, no `il/` in git | No game DLL / bulk IL redistribution |

## Claims to check (priority)

### P0: reproducibility / hard pins
1. Display version `V 3.1.0 (b14)`: Major=3, Minor=10, Build=14 from Constants / stock_facts.
2. Census: top-level types 4414, methods-with-body 44107, gmUpdate IL 631, SaveLoad IL 926, NetPackage* = 193.
3. Sim: 20 TPS / 50 ms tick (`constants_ticks_per_second`, GameTimer).
4. Chunk: 16×256×16, 64 layers × 4 height.
5. Save: `CurrentSaveVersion=23`.
6. Network: default port 26900, challenge marker `0xCA`, challenge size 17.
7. TE wire delta: `NetPackageTileEntity` payload length **i32** (not u16); teBlockId i32 present.

### P1: method / tooling honesty
8. `make stock-check` / `stock-sync --check-only` passes against committed JSON.
9. Dumpers exist and build (`make tools`) without shipping game bytes.
10. re-methodology census table: still V3.0.1 baseline numbers vs V3.1 live pin (doc drift risk).
11. README still says V3.0.1 while INDEX/AGENTS say V3.1.0 (framing mismatch).

### P2: claim vs consumer code
12. zdtd `stock_wire` / version / challenge / ticks match stock_facts.
13. loadgen GameVersion / package map dual-fixture notes match 3.1.0.
14. Coverage metric construction vs prior Critical finding (narrated % denominator/numerator artifacts).

### P3: residual / prior-audit status
15. Prior C1/C2 wire errors (WorldInfo hashes, DynamicMesh dead WriteRegion), fixed in docs or still open?
16. residuals.md: managed unaccounted 0; open items non-IL only?
17. Policy: git has no Assembly-CSharp.dll / bulk il dumps.

## Method

1. **Plan** (this file), written first; do not wait for user confirm.
2. **Researcher** (fresh): gather evidence for P0–P3 from docs, tools, consumers, live ASM if present; command outputs preferred over memory.
3. **Parent synthesis** of mismatches / missing code / ambiguous defaults / reproduction risks.
4. **Verifier** (fresh): re-check load-bearing claims and force inline citations / source paths.
5. **Single artifact** `workspace/outputs/stock-re-corpus-audit.md` with Sources section (local paths + any public URLs).

## Out of scope

- EfficientServer performance A/B claims (optimizer repo) except where RE docs cite them.
- RealEarth product status.
- Full re-audit of all ~60 narrative docs (prior cluster audits exist); this run targets pin/tooling/consumer consistency + known metric honesty.

## Success criteria for the audit artifact

- Every quantitative pin either verified with command/path, marked blocked (e.g. ASM missing), or marked mismatch.
- Explicit table: Claim | Source | Code/tool | Status.
- Clear reproduction risks for a third party with only Steam install + this repo.
- Sources section with paper (docs) and repository URLs/paths.
