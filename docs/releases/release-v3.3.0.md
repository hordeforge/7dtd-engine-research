# 7dtd-engine-research v3.3.0

Corpus re-pinned to **7 Days to Die V3.3.0 (b18)**, Steam build `25661908`,
depot manifest `3031329678505041777`, `Assembly-CSharp.dll` sha256
`e16ff9d539b8fbf64904c0bc090d502286a62464742a9396f0455936ad0beb87`
(11697152 bytes). The previous pin was V3.2.0 b10, which stays in the pin's
history so a build-id pair still resolves.

## The delta, reversed and documented

`docs/releases/changelog-3.3.0.md` carries the exact b10 to b18 delta with
instruction evidence. The short version:

- The on-disk formats changed. `PlayerDataFile` 59 -> 62, `EntityCreationData`
  37 -> 38, `TEFeatureStorage` 18 -> 20, `Bag` 1 -> 2, `Equipment` 4 -> 6,
  `Quest.FileVersion` 8 -> 9, with `i32`-length blobs where the old record was
  inline. `WorldState` 23 and the chunk preamble 47 did not move. A b18 server
  reads a b10 world, a b10 server cannot read a b18 one.
- The wire registry lost three packages net (187 -> 184 ids): six removed (the
  inventory-data and inventory-transaction pairs, the lock request and the lock
  response) and three added (`NetPackageLockTarget`, `NetPackageSingleSignData`,
  `NetPackageSignDelete`). `NetPackagePlayerInventory` and
  `NetPackagePlayerEquipment` now carry client-serialized save blobs, so the b10
  per-operation inventory transaction gate is gone.
- The inventory model was rebuilt: 13 equipment slots with a backpack, the held
  item moved into `Hand`, `ItemStackGrid` became the storage and serialization
  core, and the toolbelt count comes from the new `Data/Config/toolbelt.xml`
  (10 play slots, 20 in the prefab editor).
- Signs are a new subsystem with server-side per-player libraries, a blob
  version and a sharing mode. Two trust gaps are documented rather than fixed:
  sign upload has no sender check, and the join download ships every player
  library.
- The dedicated server now emits `player_death` and quest analytics over HTTPS
  with no managed opt-out; the release host is not decoded.
- `give` and `listitems` are new console commands, both at permission level 0.
- `AssetManagement` adds a reference-counting handle layer over the existing
  loader; pathing and spawn selection have no server-side change.

## Evidence committed with the pin

- `workspace/outputs/diffs/b10-to-v3.3.0-20261024.md`, the eight-lens report
  (4447 top-level types, 44534 methods with body, 1925 signature changes, 81
  enum-member changes, 5296 body changes, the wire set, and 15 added plus 59
  changed depot files).
- `workspace/outputs/parity/parity_b18.json`, the wire snapshot that
  `drift-check.sh` uses on a fresh checkout.
- Refreshed baselines under `workspace/outputs/baseline/`, and the regenerated
  inventories in `docs/inventories/`.
- `tools/data/stock_facts.json` and `tools/data/xml_pins.json` for the new
  build, with the publish bug in `stock-sync.sh` and the ordering bug in
  `regen.sh` fixed so a retarget completes.

## Verification

`make test-docs` and `make lint` are green; the DLL-bearing suite is green
against the fetched b18 assembly except the sibling pin check for
`zdtd-server`, which was deliberately not retargeted in this pass. The CLI
metadata tables read through a second, independent tool agree with the Cecil
dumps (`TypeDef` 7451 -> 7501, `MethodDef` 56064 -> 56440, `AssemblyRef`
unchanged at 60). The b18 probe save parses byte-exact through the save
round-trip checker, and the b18 server was booted on a b10 `main.ttw` to
confirm the one-way compatibility.

Fourteen sibling repositories were retargeted to the same build in this pass;
see the workspace changelog for the per-repo detail.

## Known limits

No live V3.3.0 join capture was taken, so the registered package-id table is
inferred from metadata order even though the set membership is verified.
Sign-library persistence inside prefab libraries, the release analytics host,
and whether a dedicated host ever acquires an item mesh remain open. Those are
listed with the rest in `changelog-3.3.0.md` §9.
