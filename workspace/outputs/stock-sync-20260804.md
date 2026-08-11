# Stock hardcode sync (2026-08-04)

> **ARCHIVED (2026-08-11):** pre-V3.1.0-retarget research artifact; superseded by the current corpus. Historical record only.

## Delivered
- `tools/src/StockFacts.cs` → `tools/data/stock_facts.json` (committed)
- `tools/stock-sync.sh` + `tools/tests/check_stock_facts.py`
- `make stock-sync` / `make stock-check` / `make test` in research root
- re-methodology §5c documents the process
- Accidental root type dumps removed + gitignored

## Live pin (extracted)
V 3.1.0 (b14): Major=3 Minor=10 Build=14, TPS=20, YDim=256, layers=64,
NetPackage=193, CurrentSaveVersion=23, challenge=0xCA, port=26900.

## Playtest seed-Y (product residual, not RE)
- zdtd: ground clamp + 3x3 spawn pad already on main (`2e2624c` height API)
- 7dtd-playtest (not a git tree): `Helpers.FixtureSeedOrigin` clamps fixture
  seeds when feet Y < surface-2; used by dig/place/block_damage/explosion/power
- Install: `cd 7dtd-playtest && make install`
- Re-score: `make playtest-zdtd` (needs Steam client + free disk)

## Ops after TFP patch
```bash
cd 7dtd-research && make stock-sync   # refresh JSON + pin FAIL sites
# fix docs / loadgen GameVersion / zdtd stock_wire as needed
```
