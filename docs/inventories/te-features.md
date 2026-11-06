# Tile-entity feature catalog (V3.4.0)

**Kind:** per-feature reference (name -> code-derived role, base, serialized state and behavior fingerprint).
**Framework:** [`../gameplay/tile-entities-power.md`](../gameplay/tile-entities-power.md) owns the TE model + power; this enumerates the `TEFeatureAbs` leaves.
**Regenerate:** `MethodList.exe` grep `TEFeature` + Cecil base-type walk + `DumpType.exe`/`DumpMethod.exe` on each leaf's `Read`/`Write`.
**Hub:** [`../INDEX.md`](../INDEX.md).

`TileEntityComposite` is the modular tile entity: a `BlockCompositeTileEntity` block declares feature modules in its properties, `TileEntityFeatureData.InstantiateModule` builds each `TEFeatureAbs` subclass, and `TileEntityComposite.read`/`write` dispatch every feature's `Read`/`Write` in module order. On the persistent stream each feature first writes its own `UInt16` version (guarded by `Parent.UseLocalVersioning()`, falling back to `GetLegacyForkVersion()`); on the network stream (`_eStreamMode != 0`) the version is skipped. The base `TEFeatureAbs.Read`/`Write` bodies serialize nothing, they only emit a `Log.Warning` when the `DebugLogCTE` flag is set. Descriptions below are code-derived from IL; nothing here is taken from external docs.

The hierarchy is flat: all 11 concrete features derive directly from `TEFeatureAbs` (verified by resolving every base-type chain in the assembly; there are no grandchildren, and no `TEFeaturePowered`/`TEFeatureLootable` types exist. Power stays on the classic `TileEntityPowered` family, and lootability is `TEFeatureStorage`).

**11 features.**

| Feature | Role | base | key methods (Read/Write + behavior) |
|---|---|---|---|
| `TEFeatureAreaRepair` | Area repair station: coroutine walks chunks around the block and repairs blocks, wired to sibling `storageFeature` (materials) and `lockFeature` (access); only its version is serialized, `isRepairing` is runtime state | TEFeatureAbs | Read/Write (version only), RepairAll -> StartCoroutine(repair), repairChunk, repairChunkCheckBounds, repairBlock, OnBlockActivated |
| `TEFeatureCanvas` | Paintable sign canvas: persists a `SignCanvas.CanvasState` (GlobalSignId + blend-mode byte + rotation byte), applies it to the `SignCanvas` component or parks it in `pendingCanvasState`; defers access to sibling lock features | TEFeatureAbs | Read/Write (CanvasState via GlobalSignId.FromStream), GetUprightRotation, SetBlockEntityData, OnBlockActivated |
| `TEFeatureCombine` | Item-combine station UI: activation opens the combine window (`XUiC_CombineGrid`), plays open/close/complete sounds, uses lock events for exclusive access; no `Read`/`Write` override, so it adds no serialized state | TEFeatureAbs | ShowUI, OnBlockActivated, HandlePlayComplete, OnLockedLocal, OnUnlockedServer |
| `TEFeatureDoor` | Door / drawbridge state: persists `isOpen` (network stream adds `animateOnSync` and triggers `HandleDoorAnimation` on change; a configured `autoCloseTime` forces closed on load), drives animation, sounds, movement blocking and see-through queries | TEFeatureAbs | Read/Write (isOpen, +animateOnSync on net), SetOpen, CanOpen, HandleDoorAnimation, IsMovementBlocked, IsSeeThrough, GetStepHeight, OnBlockTriggered, UpdateTick |
| `TEFeatureExplodable` | Explosive block: holds `ExplosionData` from block properties and calls `GameManager.ExplosionServer` at the block entity transform when the block is destroyed, hit by an explosion, starts to fall, or is triggered; serializes version only | TEFeatureAbs | Read/Write (version only), Explode, OnBlockDestroyedBy, OnBlockDestroyedByExplosion, OnBlockStartsToFall, OnBlockTriggered |
| `TEFeatureLandClaim` | Land claim block: persists the `showBounds` toggle, resolves primacy through `PersistentPlayerList.GetLandProtectionBlockOwner`, shows the bounds helper and handles claim deactivation/removal | TEFeatureAbs | Read/Write (showBounds), IsPrimary, HandleDeactivateLandClaim, OnAdded, OnRemove, UpdateTick |
| `TEFeatureLockable` | Ownership lock: persists `locked` flag, `allowedUserIds` list (`PlatformUserIdentifierAbs` per entry) and `passwordHash`; owner checks, password set/verify, allow-list management for sibling features | TEFeatureAbs | Read/Write (locked, allowedUserIds, passwordHash), IsLocked, SetLocked, IsUserAllowed, IsOwner, GetOwner/SetOwner, CheckPasswordHash, SetPasswordHash |
| `TEFeatureLockPickable` | Pickable lock minigame: pick time/break chance/pick item from properties, timer events for success/break/close, fires configured success/failed events and swaps the block via `DowngradeToUnlockedVariant`; serializes version only (`unlockCompletion`, `lockPicksUsed` are runtime state) | TEFeatureAbs | Read/Write (version only), NeedsLockpicking, ShowUI, EventData_Event, EventData_BreakEvent, DowngradeToUnlockedVariant, CanLockLocally |
| `TEFeaturePickup` | Block pickup ("take") command with a configurable `TakeDelay`; serializes version only (versions < 2 read and discard a legacy bool) | TEFeatureAbs | Read/Write (version only), OnBlockActivated, InitBlockActivationCommands, CanLockLocally |
| `TEFeatureSignable` | Editable sign text: persists an `AuthoredText` (text + author) via `AuthoredText.To/FromStream`, renders through `SmartTextMesh` with font/line metrics from properties, hides text from platform-blocked authors | TEFeatureAbs | Read/Write (AuthoredText), SetText, GetAuthoredText, CanRenderString, RefreshTextMesh, UserBlockedStateChanged, ShowUI |
| `TEFeatureStorage` | Loot and storage container inventory: persists loot list name, `containerSize` (2x UInt16), touched flag + `worldTimeTouched` (UInt32), `bPlayerStorage`, Int16 slot count + `ItemStack` array, optional `PreferenceTracker` and `SlotLocks` (`PackedBoolArray`); loot population, loot-stage mod/bonus, jammed/quest-loot flags | TEFeatureAbs | Read/Write (full container state), PopulateTE, AddItem, RemoveItem(s), TryStackItem, UpdateSlot, SetContainerSize, migrateItemsFromOtherContainer, ShouldDestroyOnClose, Reset |

## Base contract (`TEFeatureAbs`)

The abstract base gives every feature: parent/feature-data accessors (`Parent`, `FeatureData`, `blockValue`, `GetChunk`), lifecycle hooks (`Init`, `OnAdded`, `OnLoad`, `OnUnload`, `OnRemove`, `OnDestroy`, `OnBlockValueChanged`, `OnBlockReset`, `ReplacedBy`, `UpgradeDowngradeFrom`, `UpdateTick`), activation plumbing (`InitBlockActivationCommands`, `AllowBlockActivationCommand`, `OnBlockActivated`, `GetActivationText`, `CommandIs`), lock coordination callbacks shared across features (`CanLockLocally`, `CanLockOnServer`, `OnLockedLocal`, `OnLockedServer`, `OnUnlockedServer`, `IsSharedLock`) and dirty-marking (`SetModified`, `SetUserAccessing`). Representative base `Read` body (debug shim only):

```
IL_0000: ldsfld Boolean TEFeatureAbs::DebugLogCTE
IL_0005: brfalse.s IL_0026
IL_0021: call System.Void Log::Warning(System.String)
```

Cross-feature composition is explicit in the fields: `TEFeatureAreaRepair`, `TEFeatureCanvas`, `TEFeatureDoor`, `TEFeatureLandClaim`, `TEFeatureSignable` and `TEFeatureStorage` each cache sibling `TEFeatureLockable` / `TEFeatureLockPickable` references resolved from the same composite.

### A feature's payload is length-prefixed, so a reader may skip it

`TileEntityComposite.write` (IL=74) frames the module list, and both levels carry a
size marker written by `PooledBinaryWriter.ReserveSizeMarker(4)` and backfilled by
`FinalizeSizeMarker`. The value **includes its own four bytes**, which
[`tile-entities-power.md`](../gameplay/tile-entities-power.md) §2.2 states and which a reader
that treats the marker as the payload length gets wrong: it overruns the frame by four bytes
per feature and desyncs on the next field. Measured on this host's save, where that reading
walks 148 of 148 chunks to their exact body end and the payload-length reading stops at the
thirteenth:

| Order | Field | Encoding |
|---|---|---|
| 1 | base | `TileEntity.write` |
| 2 | version | `u16`, **18** on this build |
| 3 | module list | `u32` marker, backfilled over everything below it |
| 4 | `Block.blockID` | `i32` |
| 5 | owner | `PlatformUserIdentifierAbs.ToStream(owner, bw, false)`, and **null** when `GameManager.IsEditMode()`, so an editor save writes no owner |
| 6 | feature count | `u8` |
| 7 | per feature | `i32` `TileEntityFeatureData.NameHash`, `u32` size marker, then `ITileEntityFeature.Write` |

The per-feature marker is what makes a reader tractable: a reimplementation that wants
one feature's payload (a canvas's sign, a door's state) reads the name hash and the size,
then **seeks past** every feature it does not implement instead of decoding all eleven in
order. The name hash is `TileEntityFeatureData.NameHash`, so a reader matches the
feature by that value rather than by position, which the block's own property list does
not fix.

**The name hash is Unity's stable string hash.** `TileEntityFeatureData`'s constructor
(IL=23) sets `NameHash = Extensions.GetStableHashCode(Name)`, and `Name` is the key of the
block's `CompositeFeatures` property, which is the feature type's own name:
`<property class="TEFeatureCanvas"/>` yields `Name = "TEFeatureCanvas"`. The hash
(IL=63) is the classic two-accumulator form, with `*` meaning wrap to 32 bits and an
early exit on a zero char:

```
h1 = 5381; h2 = h1
for i in steps of 2:
    h1 = (h1 << 5) + h1 ^ char[i]
    if i is the last index or char[i + 1] == 0: break
    h2 = (h2 << 5) + h2 ^ char[i + 1]
return h1 + h2 * 1566083941
```

The values a tile-entity reader needs, as the `i32` the stream carries:

| Feature | `NameHash` |
|---|---|
| `TEFeatureCanvas` | **3363041421** (-931925875 as `i32`) |
| `TEFeatureSignable` | 924617576 |
| `TEFeatureDoor` | 1390289507 |
| `TEFeatureStorage` | 731446478 |

### What a canvas persists, byte by byte

`TEFeatureCanvas` is the one feature whose payload a reimplementation cannot store as an opaque blob: the sign a canvas draws lives inside it. Its `Write` (IL=23) is the base version then `SignCanvas.CanvasState.Write`, and that body (IL=18) is:

| Order | Field | Encoding |
|---|---|---|
| 1 | `SignId` | `GlobalSignId.ToStream`: `BinaryWriter.Write(string)` for `libraryId` (7-bit length prefix, UTF-8), then the `signGuid`'s 16 bytes from `Guid.TryWriteBytes`, which is .NET's mixed-endian layout, not the textual GUID order |
| 2 | `BlendMode` | one byte (`SignBlendMode`) |
| 3 | `CanvasRotation` | one byte (`CanvasRotationMode`) |
| 4 | `ShowOnImposter` | one byte, a `BinaryWriter.Write(bool)` |

`Read` (IL=88) mirrors it with two gates. The version comes from the parent's `UInt16` when `UseLocalVersioning()`, else from `GetLegacyForkVersion()`, and **no version is written on the network stream** (`_eStreamMode != 0`), where the payload is unconditionally the current shape. A version below **21** takes the pre-fork path: `GlobalSignId.FromStream`, then a byte read and discarded when the version is below **18**, `BlendMode` from **19**, `CanvasRotation` from **20**. On the server stream after parsing, a `SignId` whose `SignData` is gone and which `IsKnownDeleted` is replaced by `SignData.defaultSignDataID`, which is why a deleted sign's canvas draws the default sign rather than nothing. The parsed state goes to the `SignCanvas` component when one exists, else into `pendingCanvasState` until the component appears.

### What a writable sign persists

`TEFeatureSignable.write` (IL=25) is the base, then `u16` version **18** on the
persistent stream only, then `AuthoredText.ToStream` over `signText`. That call (IL=22)
writes `u8 0` for a null text and otherwise `u8 1`, `Write(string)` for the text, then
`PlatformUserIdentifierAbs.ToStream(author, bw, false)`. In edit mode the feature builds a
fresh `AuthoredText(text, null)` first, so an editor save writes the text and no author,
which is the same shape as the canvas's owner field. The author is what stock's per-viewer
moderation filters on (see [signs.md](../gameplay/signs.md) §8); the four text numbers
(`fontSize`, `lineCount`, `lineWidth`, `lineSpacing`) are block properties, not payload.

## Changelog

- 2026-11-06: `TEFeatureSignable`'s payload pinned (version 18, a `hasText` byte, the text string and the author), which is the writable sign's whole state.
- 2026-11-06: `NameHash` pinned as Unity's stable string hash over the feature's type name, with the values for the four features a reader meets first.
- 2026-11-06: `TileEntityComposite.write`'s framing pinned, including that each feature's payload carries its own length, so a reader can skip features it does not implement and find one by `NameHash`.
- 2026-11-06: `TEFeatureCanvas`'s payload pinned byte by byte (version 21 gate, `GlobalSignId` = prefixed string + 16 mixed-endian GUID bytes, blend, rotation, `ShowOnImposter`), with the pre-fork read path and the deleted-sign substitution.
- 2026-07-24: initial catalog from stable V3.0.1 server DLL (11 leaves, flat hierarchy verified).
