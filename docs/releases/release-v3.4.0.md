# 7dtd-engine-research v3.4.0

**Hub:** [`INDEX.md`](../INDEX.md). **Corpus pin:** V **3.4.0 (b10)**.

Corpus re-pinned to **7 Days to Die V3.4.0 (b10)**, Steam build `26310339`,
depot manifest `5022117301453546978`, `Assembly-CSharp.dll` sha256
`00a962dbbb5ef1bb454368322221f9eb4148dc2d548ed2b77244f9bda5ecc167`
(11752960 bytes). The previous pin, V3.3.0 b18, stays in the pin's history, and
that build's Steam branch still resolves.

## The delta, reversed and documented

`docs/releases/changelog-3.4.0.md` carries the b18 to b10 delta with instruction
evidence. The short version:

- **Wire**: two new packages, `NetPackageDroneRecoveryRequest` (id 45) and
  `NetPackageDroneRecoveryResponse` (id 46); every id above 46 moves +2; 190
  registered ids in total. The table was **measured from a live V3.4.0 join**
  (4,069 packets, 158 envelopes, 0 unparsed) rather than inferred from metadata
  order, which is the first time this corpus has had a measured table for the
  current build. No package's byte layout changed.
- **Save format did not move.** Current save version is still 23, `WorldState`
  still 926 IL, and every record version from b18 (`PlayerDataFile` 62,
  `EntityCreationData` 38, `TEFeatureStorage` 20, `Bag` 2, `Equipment` 6,
  `Quest` 9, chunk preamble 47) is unchanged. A b18 world loads on a b10 server.
- **Drone recovery is new** and reaches the server: a client dialog action sends
  the request package, `DroneManager.RecoverDroneForPlayer` scans active,
  unloaded and ownerless drones, teleports the owner's drone back, triggers a
  save and broadcasts a vehicle count. The `actionId` field is unread server-side
  and the response carries no client selector, so the sender check that would
  keep one player away from another player's drone is absent.
- **Dynamic mesh left the server.** Twelve server-side call sites are gone (block
  damage and place, falling blocks, `NetPackageSetBlock`, `chunkreset`,
  `ChunkManager`, `SaveAndCleanupWorld`, `Origin`, distant terrain,
  `DynamicObserver`), prefs 204 to 209 are no longer loaded, and `Init()` is
  console-only. A dedicated server now compiles the subsystem and never runs it.
- **Carry capacity is a flat 96.** The 27/45/48/50 ladder that perks and buffs
  used to grant is gone, so every player carries the same weight.
- **Gear variants and cosmetic sets are client-side.** `GearVariants.GearFitMatrixSO`
  resolves mesh-variant suffixes (`A`, `B`, `C`) per sex and body part; its 24
  mutating and query members have no callers in the dedicated assembly. Cosmetic
  sets resolve on the server only through the equipment maps.
- **Data**: 10 changed `Data/Config` files, 8 cosmetic DLC armor rows, a trader
  drone dialog, and a case-only `music.xml` to `Music.xml` rename, with
  `xmlsToLoad` and every `behaviour` constant unchanged.

## Evidence committed with the pin

- `workspace/outputs/diffs/b18-to-v3.4.0-20261105.md`, the eight-lens report
  (types, signatures, enums, bodies, wire parity, depot manifest, stock facts,
  census) plus the depot content delta (1625 changes, 76 added, 1547 changed).
- `workspace/outputs/parity/parity_v3.4.0.json` and
  `workspace/outputs/wire/netpackage-ids-v3.4.0.json`, the measured id table.
- Refreshed `workspace/outputs/baseline/`, the census-history row, and every
  regenerated inventory under `docs/inventories/`.
- `tools/data/stock_facts.json`, `xml_pins.json` and `steam_builds.json` for the
  new build.

## Verification

`make test-docs` and `make lint` are green. `make test` against the fetched b10
assembly is green except the `zdtd-server` sibling pin check, which is excluded
from this pass on purpose. Both installs were verified byte-exact against their
own Steam depot manifests before any comparison. Headless dedicated boot reaches
`StartGame done` at 60.9 s, saves the world and exits through
`OnApplicationQuit` on SIGTERM, and the whole run names `V 3.4.0 (b10)`.

## Known limits

The six new unknowns are listed in `changelog-3.4.0.md` section 9: the intent of
the drone-recovery broadcast, whether dynamic mesh can still self-start from a
scene `Awake`, the shrunken pool-table blob values, `GetFits`'s declared return
interface, whether the `Music.xml` case rename breaks a case-sensitive reader,
and the 146 registered ids the single join did not exercise.
