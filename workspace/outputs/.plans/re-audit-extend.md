# Plan: Audit all docs + extend RE (slug: re-audit-extend)

Status: substantially complete 2026-07-23.
Objective (user): "audit all docs here. do more RE of all game systems and wire protocols etc"

## Environment (verified 2026-07-23)
- Game DLL present: `~/.local/share/Steam/.../7 Days to Die Dedicated Server/.../Assembly-CSharp.dll` (11.5 MB, V3.0.1, dated 2026-07-17)
- Tooling: mono, monodis, ikdasm, dotnet, Mono.Cecil (in il/zdtd_re_tools/). Dumpers run OK.
- Existing dumps contain NO per-NetPackage Read/Write bodies -> protocol golden bodies so far came from loadgen companion, not IL here. GAP.

## Arm A: Doc audit (25 narratives + 8 inventories)
- [x] Link integrity: 0 broken internal; 381 external refs resolve to sibling companions (won't resolve for public cloner, note).
- [ ] Cross-check quantitative claims vs live DLL (census: 4401 types, 43901 methods, ~196 NetPackage, gmUpdate IL 631, WorldState.SaveLoad 884, GameTimer 20Hz).
- [ ] Internal consistency: numbers repeated across docs agree.
- [ ] Unsupported-claim scan: any "measured" number without artifact provenance.
- [ ] Staleness / contradictions.
- Output: workspace/outputs/re-audit-extend-doc-audit.md

## Arm B: New RE (wire protocol + systems)
- [ ] Build general NetPackage Cecil dumper -> dump Read/write/ProcessPackage bodies for all NetPackage* types.
- [ ] Annotate P0: NetPackageChunk, Entity spawn/create, WorldInfo/WorldTime.
- [ ] Annotate P1: SetBlock(+Response), PlayerInventory/HoldingItem, ChunkRemove.
- [ ] Other systems as time permits.
- Output: new dumps in il/netpackages-v3.0.1/ ; narrative extends docs/protocol.md + protocol-frames.md; annotate workspace/notes/re-audit-extend-wire.md

## Verification
- Every new wire field traces to a specific IL instruction (ldfld/callvirt Write*).
- Reconcile census numbers against DLL, correct docs if drift.
