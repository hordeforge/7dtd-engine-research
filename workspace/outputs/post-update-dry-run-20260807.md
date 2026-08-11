# Post-update dry-run (2026-08-07)

> **ARCHIVED (2026-08-11):** pre-V3.1.0-retarget research artifact; superseded by the current corpus. Historical record only.

**ASM:** Steam dedicated `Assembly-CSharp.dll` (live install)  
**Committed pin:** V 3.1.0 (b14)  
**Mode:** dry-run (no commit of regenerated facts; no baseline rewrite)

## Stock facts

| Check | Result |
|---|---|
| `StockFacts.exe` → temp JSON | OK |
| Diff vs `tools/data/stock_facts.json` | **0** field diffs (ignoring `extracted_utc`) |
| `make stock-check` | green |

Conclusion: installed dedi still matches committed pin. No pin edits required.

## Drift (`tools/parity/drift-check.sh`)

Baseline cache: `~/.cache/zdtd-scratch/drift-baseline/` (dated ~2026-07-24).

| Surface | Result |
|---|---|
| Parity JSON capture | **fixed** this run: strip mono stdout noise before `parity_diff` |
| NetPackage wire | **drift DETECTED** vs old baseline (not vs committed docs) |

Notable package wire deltas vs July baseline (already documented for V3.1.0):

1. **NetPackageTileEntity:** `ReadUInt16` payload length → `ReadInt32` teBlockId + `ReadInt32` payloadLen (and matching extra Write). Matches protocol-packages §6.12 / stock_facts `tile_entity_package`.
2. **NetPackageDamageEntity:** one extra `ReadBoolean` / `Write` in the mid-body sequence vs baseline capture.

**Do not auto-rebaseline** until a real TFP upgrade is intentional. After a real update: review diffs, update narratives, then:

```bash
# only after review
cp -r "$CUR_SNAPSHOT"/. ~/.cache/zdtd-scratch/drift-baseline/
```

## Tooling fix included

`tools/parity/drift-check.sh`: ParitySurface stdout filtered to JSON object; invalid capture skips package wire diff with a warning instead of `JSONDecodeError`.

## Recommended next real update steps

1. Install new dedi build.
2. `make post-update` (or `--no-drift` first).
3. Fix FAIL pin sites; commit `stock_facts.json` + pins together.
4. Review drift; re-Dump changed families into `il/<set>-$(dump_label_suffix)/`.
5. Re-baseline drift cache after narrative refresh.
