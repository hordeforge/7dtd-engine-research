# Tile-entity feature catalog (V3.1.0)

**Kind:** per-feature reference (name -> code-derived role, base, serialized state and behavior fingerprint).
**Framework:** [`../tile-entities-power.md`](../tile-entities-power.md) owns the TE model + power; this enumerates the `TEFeatureAbs` leaves.
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

## Changelog

- 2026-07-24: initial catalog from stable V3.0.1 server DLL (11 leaves, flat hierarchy verified).
