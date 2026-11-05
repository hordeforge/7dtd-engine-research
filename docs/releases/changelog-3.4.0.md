# Changelog 3.4.0: stock dedicated server, V3.3.0 b18 to V3.4.0 b10

**Hub:** [`INDEX.md`](../INDEX.md). **Pin:** V **3.4.0** b10
([`../../tools/data/stock_facts.json`](../../tools/data/stock_facts.json)).
**Diff report:** [`b18-to-v3.4.0-20261105.md`](../../workspace/outputs/diffs/b18-to-v3.4.0-20261105.md)
(eight lenses, regenerable with `tools/research_diff.py`).
**Previous builds:** this build supersedes [`changelog-3.3.0.md`](changelog-3.3.0.md)
(V3.3.0 b18) and its two predecessors. Their claims stay as history.

This build moves the version line from 3.3 to 3.4 and, for a dedicated
server, changes two things that matter: drones gained a recovery path a
client can trigger, and the dynamic-mesh subsystem lost every one of its
server-side call sites. The rest of the delta is a client-side gear-variant
authoring feature, a flattened carry capacity, cosmetic DLC armor rows, and
the usual recompiles.

## 1. Identity

| | V3.3.0 b18 | V3.4.0 b10 |
|---|---|---|
| Version tuple | `(1,3,30,18)` | `(3,40,10)` |
| Display / wire label | `V 3.3.0` / `V3.3.0 b18` | `V 3.4.0` / `V3.4.0 b10` |
| Steam build id (dedicated) | `25661908` | `26310339` |
| Depot 294422 manifest | `3031329678505041777` | `5022117301453546978` |
| `Assembly-CSharp.dll` sha256 | `e16ff9d539b8fbf64904c0bc090d502286a62464742a9396f0455936ad0beb87` | `00a962dbbb5ef1bb454368322221f9eb4148dc2d548ed2b77244f9bda5ecc167` |
| `Assembly-CSharp.dll` bytes | 11697152 | 11752960 |
| Client build id (app 251570) | `25661859` | `26309840` |
| Client `Assembly-CSharp.dll` sha256 | `fceec27300ffd3a1f97b097e43b60f3b07597f441e7ecbc6e1b59eebb234c705` | `cb54022ccc862aa673e0ee55dafe67d842b364c8` |

Both Steam branches exist: on app 294420 the branch `v3.4.0` and `public`
point at build `26310339`, and `v3.3.0` still resolves to `25661908`, so a
downgrade install stays possible. An anonymous `app_update` with no `-beta`
installs `V3.2.0` b10 on this host; the version has to be named.

## 2. Assembly surface

| Measure | b18 | b10 | Delta |
|---|--:|--:|--:|
| Top-level types | 4447 | 4468 | +21 |
| Methods with body (top-level) | 44534 | 44747 | +213 |
| All types (incl. nested) | 7501 | 7549 | +48 |
| All methods with body | 53796 | 54064 | +268 |
| IL instructions | 1749641 | 1754946 | +5305 |
| Top-level `NetPackage*` | 192 | 194 | +2 |

Changed bodies: 927 (522 added, 159 changed, 246 removed). Signature changes:
309 (269 added, 40 removed). Enum changes: 26 (20 added, 6 removed). Type
metadata changes: 186 (72 added, 72 changed, 42 removed).

Two new namespaces: `GearVariants` (the fit matrix) and the global cosmetic-set
types. Removed namespaces: none.

## 3. Wire protocol

The registered-id table was measured from a live V3.4.0 join
(`workspace/outputs/wire/netpackage-ids-v3.4.0.json`, evidence
`.scratch/livejoin-v340/`), not inferred:

- **190 registered ids** (b18: 188). Ids `0..44` are unchanged.
- Two new packages occupy the gap: `NetPackageDroneRecoveryRequest` = **45**
  (body `i32 playerId`, `string actionId`, `ToServer`) and
  `NetPackageDroneRecoveryResponse` = **46** (body `i32 playerId`,
  `i32 droneId`, `ToClient`). Both channel 0, reliable, uncompressed,
  post-authentication, registered by the unchanged reflection walk.
- Every id above 46 is **+2** against b18. `NetPackageLight` moves 185 -> 187.
- Framing, channel assignment, compression, encryption handshake and the
  pre-auth allowed set are unchanged. No package's `read`/`write` byte layout
  changed, though `NetPackageSetBlock::ProcessPackage` and `ItemValue::Read`
  have changed bodies without layout change.
- The +3 offset between the inferred metadata order and the measured table
  found at b18 persists (+4 above `Light`), and the four nested registrations
  still hold.

## 4. Save and on-disk formats

Nothing moved. `Constants.CurrentSaveVersion` is still 23, `WorldState.SaveLoad`
is still 926 IL instructions, and every record version the b18 corpus pinned
(`PlayerDataFile` 62, `EntityCreationData` 38, `TEFeatureStorage` 20, `Bag` 2,
`Equipment` 6, `Quest` 9, chunk preamble 47) is unchanged in the new assembly.
Equipment bytes still reach disk inside `PlayerDataFile` and the wire inside
`NetPackagePlayerEquipment` exactly as b18 did, so a b18 world loads here and
the downgrade rule from b18 is still the one that applies (b18 cannot read a
newer record, which is why the versions have not moved either).

## 5. Data and config

`Data/Config` went 60 files in and 60 out: 10 changed, one case-only rename
(`music.xml` to `Music.xml`). Both installs were verified byte-exact against
their own Steam manifests before the comparison.

- **Carry capacity flattened to 96.** `buffs.xml` and `progression.xml` no
  longer grant 27/45/48/50 through the carry-capacity perks and buffs; the
  item descriptions that printed those numbers move with it. A server now has
  one carry limit for every player.
- **Eight cosmetic DLC armors** added to `items.xml`, with left-knuckle
  `onSelfChangedView` parts. They are cosmetic rows, not new server behavior.
- **Trader drone submenu** in `dialogs.xml` (`dialog_trader_statement_drone`;
  the statement's localization key is absent from the shipped
  `Localization.csv`).
- `xmlsToLoad` is unchanged (50 entries, no `Music` row), all nine
  `behaviour` numbers in `stock_facts.json` are unchanged, and `entitygroups.xml`
  differs only in line endings.

## 6. Subsystems

### 6.1 Gear variants and cosmetic sets (client-side)

`GearVariants.GearFitMatrixSO` loads an addressable
`Entities/Player/Common/GearFitMatrix.asset` and holds, per sex and per body
part (`head`, `hands`, `feet`), a sparse table keyed by the *worn* gear prefab;
each key maps body prefabs to a mesh-variant suffix (`A`, `B`, `C` in the
shipped asset). `GearFitNaming` composes `part_variant` mesh names and parses
them back.

The only IL call sites that reach it are the two `getPartNameWithVariant`
helpers, both on the client's gear-visual path; the 24 mutating and query
methods have zero callers in the dedicated assembly. `CosmeticSet` and
`CosmeticSetRegistrar` hold addressable prefixes and mappings, again resolved
client-side. A dedicated server compiles them, never enters them, and nothing in
the spawn, save or replication path touches them.

### 6.2 Drone recovery (new server path)

A client dialog action (`drone_commands_unstuck`) sends
`NetPackageDroneRecoveryRequest`; the server runs
`DroneManager.RecoverDroneForPlayer`, which scans active, unloaded and ownerless
drones for the player, teleports the drone to the owner (head minus forward
offset), triggers a save, and broadcasts `NetPackageVehicleCount`. The response
carries `playerId` and `droneId` and makes the client re-own the entity. The
`actionId` field is not read server-side, and the response is sent with no
client selector, so it is a broadcast in practice. There is no automatic sweep:
the only trigger is the dialog action.

### 6.3 Dynamic mesh cut out of the server paths

Twelve call sites were removed: block damage and placement, world falling
blocks, `NetPackageSetBlock`, `chunkreset`, `ChunkManager`, `SaveAndCleanupWorld`,
`Origin`, distant terrain and `DynamicObserver`. Prefs 204 to 209 are no longer
loaded, and `Init()` is reachable only from the console. `ChunkManager`'s unload
guard lost its dynamic-mesh-thread check because the thread it guarded is gone.
For a headless server this subsystem is now inert unless someone starts it from
the console.

### 6.4 Small changes

- `EntityAlive.MoveEntityHeadedFlying` extracted; `EntityDrone` overrides it and
  gains `MoveTo`. Drone flight behavior is unchanged, the code moved.
- `EffectGroupDescription.GetDescriptionKey` is read only by the skill-perk UI
  and its analytics; not server logic.
- `CameraToggleEventData` is only constructed by the client's
  first-person-view input switch.
- `Block` and `BlockShapeNew` shrank by 22 and 8 IL instructions; the diff
  report lists both with no signature change.

## 7. Where each fact lives

| Fact | Doc |
|---|---|
| Package ids, bodies, directions | [`../network/protocol-packages.md`](../network/protocol-packages.md) |
| Join sequence, framing, channels | [`../network/protocol.md`](../network/protocol.md), [`../network/network.md`](../network/network.md) |
| Drone recovery path | [`../gameplay/vehicles-drones-turrets.md`](../gameplay/vehicles-drones-turrets.md) |
| Dynamic mesh inertness | [`../world/dynamic-mesh.md`](../world/dynamic-mesh.md), [`../world/world-chunks.md`](../world/world-chunks.md) |
| Carry capacity and DLC armor rows | [`../gameplay/progression.md`](../gameplay/progression.md), [`../gameplay/buffs.md`](../gameplay/buffs.md), [`../gameplay/items.md`](../gameplay/items.md) |
| Trader drone dialog | [`../content/npc-dialog.md`](../content/npc-dialog.md) |
| Save record versions | [`../world/save-persistence.md`](../world/save-persistence.md) |
| Coverage and residuals | [`../meta/coverage.md`](../meta/coverage.md), [`../meta/residuals.md`](../meta/residuals.md) |

## 8. Verified against the build

- Both installs verified byte-exact against their Steam depot manifests, and the
  `Assembly-CSharp.dll` hash re-extracted twice with the same result.
- Live V3.4.0 join captured with the updated client (4,069 packets, 158
  envelopes, 0 unparsed), and the id table derived from it rather than from
  metadata order.
- Headless dedicated boot: `StartGame done` at 60.9 s, world saved, clean
  `OnApplicationQuit` on SIGTERM (`V 3.4.0 (b10)` in the log).
- `Data/Config` element-level diff run against both installs, with the XML
  pin hashes re-derived.

## 9. Unknowns left open

- Whether the drone-recovery response is intended as a broadcast or carries a
  selector this decode missed. A second client in the world would settle it.
- Whether the dynamic-mesh subsystem can still self-start from a scene `Awake`
  now that every explicit server call site is gone.
- The shrunken pool-table blob values behind `BlockShapeNew`'s smaller body.
- `GearFitMatrixSO.GetFits`'s declared return interface (the IL mixes a list and
  an empty array).
- Whether `Music.xml`'s case-only rename breaks a case-sensitive config reader
  anywhere outside the server.
- The 146 unobserved registered ids in the join capture; absence is not claimed.
