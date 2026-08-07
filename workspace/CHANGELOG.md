# Workspace changelog — lab notebook

Append-only research log. Not release notes. Each entry: date, active slug/objective,
what changed / what was tried, verification state (`verified` / `unverified` /
`blocked` / `inferred`), and the next recommended step. Read recent entries before
resuming substantial work. Do not log trivial one-shot tasks.

---
## 2026-08-08 - tier-C: activate/zoom + block conversion

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionActivate IL=79 (OnHoldingItemActivated
  hook); ItemActionZoom IL=103 aim toggle.
- ItemClass.OnConvertToBlockValue: base IL=2 passthrough;
  ItemClassTorch IL=20 packs UseTimes into meta/meta2.
## 2026-08-08 - tier-C: water actions + activate/zoom

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionCollectWater IL=89 (fill mass =
  MaxMass-Meta, water-cell raycast, OnHoldingUpdate fill);
  ItemActionDumpWater IL=118 (TryFindDumpPosition, trader-area +
  land-claim gates, OnHoldingUpdate write-back).
- ItemActionActivate IL=79 (OnHoldingItemActivated hook);
  ItemActionZoom IL=103 aim toggle.
## 2026-08-08 - tier-C: water collect + dump actions

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionCollectWater.ExecuteAction IL=89 (fill
  mass = MaxMass - Meta, one-shot latch, water-cell raycast,
  targetPosition/targetMass).
- ItemActionDumpWater.ExecuteAction IL=118 (water-container check,
  Meta>=195, TryFindDumpPosition, trader-area + land-claim owner 3
  gates, OnHoldingUpdate write-back).
## 2026-08-08 - tier-C: collect water action

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionCollectWater.ExecuteAction IL=89 -
  fill mass = MaxMass - Meta (default 19500, <195 return),
  one-shot latch, water-cell raycast (16/4095),
  targetPosition/targetMass latch + fill in OnHoldingUpdate.
## 2026-08-08 - tier-C: exchange + make fertile actions

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionExchangeBlock.ExecuteAction IL=82
  (sourceblock match -> SetBlockRPC(targetBlock)).
- ItemActionMakeFertile.hitTheTarget IL=175: FertileLevel<2 melee
  delegate, dominant-axis adjacent cells -> adjacentBlock
  (DensityTerrain/3) + hit cell -> fertileBlock, AddLevelExp
  xpOther, SetBlocksRPC + soundEnd.
## 2026-08-08 - tier-C: exchange block action

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionExchangeBlock.ExecuteAction IL=82 -
  press-only + Delay/cBuildIntervall gates, sourceblock match ->
  SetBlockRPC(targetBlock) + placeblock sound +
  RightArmAnimationAttack.
## 2026-08-08 - tier-C: repair + terrain tool

Done (V3.1.0 b14 IL):
- items.md: ItemActionRepair.ExecuteAction IL=631 gates (Delay,
  hit distance, passive 177, TP camera, trader-area refusal) +
  repairType; CanRemoveRequiredResource IL=106 upgrade filters +
  UpgradeHitCount/PropUpgradeBlockItemCount + toolbelt/bag count;
  application via crafting queue.
- ItemActionTerrainTool: ExecuteAction IL=46 press/release latch +
  ItemActionEffectsServer forward, GetRange IL=2 fixed 20.
## 2026-08-08 - tier-C: repair action

Done (V3.1.0 b14 IL):
- items.md: ItemActionRepair.ExecuteAction IL=631 gates (Delay,
  hit distance, passive 177, TP camera, trader-area refusal) +
  repairType; CanRemoveRequiredResource IL=106 upgrade filters +
  UpgradeHitCount/PropUpgradeBlockItemCount + toolbelt/bag count;
  GetRepairAmount IL=3 field; application via crafting queue.
## 2026-08-08 - tier-C: block placement + skill book

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionPlaceAsBlock.ExecuteAction IL=353 (gates,
  HitInfo target, OnConvertToBlockValue, BlockPlacement.OnPlaceBlock
  + OnBlockPlaceBefore, keystone lpblock gate vs CanPlaceBlockAt,
  Block.PlaceBlock + MinEvent 44 + BlockPlaced +
  changeItemTo/decInventoryLater); BlockPlacement.OnPlaceBlock
  IL=235 (face snap, face<<2 + ConvertRotationFree, face-offset
  cell); Block.PlaceBlock IL=67 (terrain Density / non-terrain
  DensityAir / deco no-density, keystoneBlock achievement 4).
- ItemActionGainSkill: ExecuteAction IL=24 read latch +
  OnHoldingUpdate IL=143 grant (Level+1 capped at MaxLevel,
  MinEvent 98, DecHoldingItem); ItemActionLearnRecipe shares latch.
## 2026-08-08 - tier-C: block placement (action + math + commit)

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionPlaceAsBlock.ExecuteAction IL=353 (gates,
  HitInfo target, OnConvertToBlockValue, BlockPlacement.OnPlaceBlock
  + OnBlockPlaceBefore, keystone lpblock gate vs CanPlaceBlockAt
  claim check, Block.PlaceBlock + MinEvent 44 + BlockPlaced +
  changeItemTo/decInventoryLater).
- BlockPlacement.OnPlaceBlock IL=235 (ground-cover face snap,
  face<<2 + ConvertRotationFree, face-offset cell); Block.PlaceBlock
  IL=67 (terrain Density / non-terrain DensityAir / deco no-density
  SetBlockRPC, keystoneBlock achievement 4).
## 2026-08-08 - tier-C: loot/quest items + block placement

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionOpenLootBundle IL=183 (Spawn at party
  loot stage); ItemActionQuest IL=87 (GetQuest + repeatable/active
  gate + CanActivate, offer window with QuestLock).
- ItemActionPlaceAsBlock.ExecuteAction IL=353: gates (Delay +
  cBuildIntervall + passive 177), HitInfo target + collider check,
  OnConvertToBlockValue, placement distance + CanPlaceBlockAt,
  BlockPlacement.OnPlaceBlock + OnBlockPlaceBefore, keystone lpblock
  gate vs CanPlaceBlockAt claim check, Block.PlaceBlock + MinEvent
  44 + BlockPlaced + changeItemTo/decInventoryLater + placeblock
  sound.
## 2026-08-08 - tier-C: loot bundle + quest item

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionOpenLootBundle.ExecuteInstantAction
  IL=183 (GetLootContainer + Spawn at party highest loot stage,
  AddItem/ItemDropServer grant).
- ItemActionQuest.ExecuteInstantAction IL=87 (GetQuest +
  FindQuest repeatable/active gate + CanActivate, CreateQuest ->
  XUiC_QuestOfferWindow with stack QuestLock).
## 2026-08-08 - tier-C: loot bundle open

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionOpenLootBundle.ExecuteInstantAction
  IL=183 - GetLootContainer(lootListName) + LootContainer.Spawn at
  party highest loot stage, grant via AddItem/ItemDropServer.
## 2026-08-08 - tier-C: instant eat + bundle open

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionEat.ExecuteInstantAction IL=179 (MinEvent
  24 use start, Consume sip vs full decrement, MinEvent 29 +
  UsedItem, CreateItem refund with UseJarRefund roll +
  AddItem/ItemDropServer).
- ItemActionOpenBundle.ExecuteInstantAction IL=493 (per CreateItem
  entry with CreateItemCount[i] min-max roll, quality items forced
  count 1 + MaxDurabilityModifier 1, AddItem/ItemDropServer grant).
## 2026-08-08 - tier-C: instant eat path

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionEat.ExecuteInstantAction IL=179 - MinEvent
  24 use start, Consume flag -> partial UseTimes sip vs full stack
  decrement, MinEvent 29 + QuestEventManager.UsedItem, CreateItem
  refund with UseJarRefund sandbox roll + AddItem/ItemDropServer
  fallback.
## 2026-08-08 - tier-C: same-class gate + block-item bridge

Done (V3.1.0 b14 IL):
- combat-damage.md: EntityEnemyAnimal.CanDamageEntity IL=17 same-
  class gate; EntityAnimal/EntityEnemy DamageEntity IL=7 base
  delegates.
- items.md 2: ItemClassBlock.GetBlock IL=5 (Block.list[itemId]);
  GetBlockValueFromItemValue IL=15 SelectAlternates ->
  GetAltBlockValue(iv.Meta) else iv.ToBlockValue(false).
## 2026-08-08 - tier-C: same-class damage gate

Done (V3.1.0 b14 IL):
- combat-damage.md: EntityEnemyAnimal.CanDamageEntity IL=17
  same-class gate (no same-species damage); EntityAnimal/
  EntityEnemy DamageEntity IL=7 base delegates.
## 2026-08-08 - tier-C: Hit resolvers

Done (V3.1.0 b14 IL):
- combat-damage.md: GetBlockHit IL=84 (distant-deco fallback,
  multiblock parent); FindHitEntityNoTagCheck IL=49 (E_BP_ body
  part name, FindEntityUpwards, E_Vehicle fallback).
## 2026-08-08 - tier-C: ItemActionAttack.Hit orchestration

Done (V3.1.0 b14 IL):
- combat-damage.md: ItemActionAttack.Hit IL=1614 - attacker
  resolve, AttackHitInfo reset, block branch (BlockValueRef +
  distant-deco fallback, GetBlockDamageScale, Block.DamageBlock)
  vs entity branch (CanDamageEntity gate, DamageSource dismember
  seed, crit roll, DamageEntity, RecordedDamage read-back).
## 2026-08-08 - tier-C: dynamic melee hitTarget

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionDynamic.hitTarget IL=454 - tag
  assembly (action + item/MeleeTag + stance + movement), passive 7
  degradation x ItemDegradationModifier + HandleItemBreak,
  isCriticalHit reset, block/entity dispatch via GetDamageBlock /
  GetDamageEntity.
## 2026-08-08 - tier-C: dynamic melee sweep raycast

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionDynamicMelee.Raycast IL=203 - no
  vehicle, stamina cost on local player, passive 199 penetration
  loop (useExistingRay, 20-iter cap), water particles, hitTarget
  per cast, RayHit avatar bool + whiff MinEvents 26/34.
## 2026-08-08 - tier-C: explosion entity damage + dynamic melee gate

Done (V3.1.0 b14 IL):
- protocol-packages.md 6.14: Explosion.AttackEntites IL=691 -
  passive 20/21 entityDamage/radius, OverlapSphere scan, item-drop
  destruction, E_BP_ root resolve + sleeper wake, Voxel.Raycast
  LOS gate (65536/66), part multipliers (arms/legs/head/chest),
  linear falloff, passive 22 scale, >=3 gate, DamageRecord.
- items.md 4.2: dynamic-melee canStartAttack IL=198 (passives
  18/112/177, TP-camera, jam, stamina); canContinueAttack IL=5
  IsAttackValid; SetAttackFinished IL=53 MinEvents 29/37 + whiff
  31/39.
## 2026-08-08 - tier-C: explosion entity damage

Done (V3.1.0 b14 IL):
- protocol-packages.md 6.14: Explosion.AttackEntites IL=691 -
  passive 20/21 entityDamage/radius, OverlapSphere scan, item-drop
  destruction, E_BP_ root resolve + sleeper wake, Voxel.Raycast
  LOS gate (65536/66), part multipliers (arms/legs/head/chest),
  linear falloff, passive 22 scale, >=3 gate, DamageRecord
  accumulation.
## 2026-08-08 - tier-C: ExplosionData wire + explosion damage model

Done (V3.1.0 b14 IL):
- protocol-packages.md 6.14: ExplosionData Write IL=88 / Read
  IL=82 (ParticleIndex/Duration x10/BlockRadius x20/EntityRadius/
  BlastPower i16, BlockDamage/EntityDamage f32, BlockTags,
  IgnoreHeatMap, DamageType i16, DamageMultiplier, BuffActions);
  ToByteArray IL=21 pooled writer.
- Explosion.AttackBlocks IL=553 damage model: passive 21 radius,
  terrain rise, cubic sweep + occlusion ray march (dir*0.51),
  passive 19 block damage x GetBlockDamageScale+0.5, linear
  falloff (1-dist/radius)/(2r+1), BlockTags filter,
  damagedBlockPositions.
## 2026-08-08 - tier-C: ExplosionData struct wire

Done (V3.1.0 b14 IL):
- protocol-packages.md 6.14: ExplosionData Write IL=88 / Read
  IL=82 - ParticleIndex/Duration x10/BlockRadius x20/EntityRadius/
  BlastPower i16, BlockDamage/EntityDamage f32, BlockTags string,
  IgnoreHeatMap bool, DamageType i16, DamageMultiplier nested,
  BuffActions u8+strings; ToByteArray IL=21 pooled writer; ctor
  from DynamicProperties + effects (ItemActionProjectile.Explosion).
## 2026-08-08 - tier-C: projectile runtime + config

Done (V3.1.0 b14 IL):
- items.md 4.2: ProjectileMoveScript.Fire IL=236 (hitMask 80
  default, passives 71/70 velocity/gravity, ballistic FlyTime<0
  branch, water particles, SetState Flying); FixedUpdate IL=196
  state machine (gravity after FlyTime, ideal-position lerp,
  LifeTime/DeadTime timeouts, sticky-ray revive via Voxel.Raycast);
  SetState IL=33 (Dead hides MeshExplode + light); checkCollision
  IL=616 segment sweep + firer layer exclusion; TryCollect IL=40
  sticky-arrow pickup.
- ItemActionProjectile.ReadFrom IL=51: ExplosionData from props+
  effects, FlyTime/LifeTime/DeadTime/Velocity/CollisionRadius,
  Gravity default -9.81.
## 2026-08-08 - tier-C: projectile runtime

Done (V3.1.0 b14 IL):
- items.md 4.2: ProjectileMoveScript.Fire IL=236 (hitMask 80
  default, passives 71/70 velocity/gravity, ballistic FlyTime<0
  branch, water particles, SetState Flying); FixedUpdate IL=196
  state machine (gravity after FlyTime, ideal-position lerp,
  LifeTime/DeadTime timeouts, sticky-ray revive via Voxel.Raycast);
  SetState IL=33 (Dead hides MeshExplode + light); checkCollision
  IL=616 segment sweep + firer layer exclusion; TryCollect IL=40
  sticky-arrow pickup.
## 2026-08-08 - tier-C: catapult + launcher families

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionCatapult.ExecuteAction IL=163 draw/
  release (strainPercent, reload-block, auto-reload
  ItemReloadServer, break/TP-camera cancel, fire via ranged
  ExecuteAction press+release); GetStrainPercent IL=10;
  CanReload IL=15 cancels drawn bow.
- ItemActionLauncher: fireShot IL=5 stub; instantiateProjectile
  IL=136 ammo resolve + model clone + ProjectileMoveScript wiring
  (owner, actions, launcher value); ItemActionEffects IL=72
  per-burst ProjectileMoveScript.Fire with direction offset +
  hitmask.
## 2026-08-08 - tier-C: catapult bow family

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionCatapult.ExecuteAction IL=163
  draw/release (strainPercent = hold/m_MaxStrainTime, reload-
  block, auto-reload ItemReloadServer, break/TP-camera cancel,
  fire via ranged ExecuteAction press+release); GetStrainPercent
  IL=10 lastAttackStrainPercent; CanReload IL=15 cancels drawn
  bow then ranged gate.
## 2026-08-08 - tier-C: air drop flight logic + SetStorm

Done (V3.1.0 b14 IL):
- aidirector.md: AIAirDrop.Tick IL=193 wait-for-chunks then per-
  path plane + staggered crate spawns; CreateFlightPaths IL=355
  (MakePlayerClusters 30 m, CalcSupplyDropMetrics 1-4 planes,
  crateY min(player.y+180, 276), FindSafePoint >= 600 m from
  players, ClampToMapExtents); SpawnPlane IL=74 supplyPlane entity
  + SetDirectionToFly (20*(len/120+10) ticks); EntitySupplyPlane
  SetDirectionToFly IL=12 (motion = dir*6, unreplicated) +
  OnUpdatePosition IL=49 (ticksToFly countdown -> MarkToUnload).
- weather-environment.md: WeatherManager.SetStorm IL=32 per-biome
  stormWorldTime/stormDuration stamp for named biome or all.
## 2026-08-08 - tier-C: air drop flight logic

Done (V3.1.0 b14 IL):
- aidirector.md: AIAirDrop.Tick IL=193 wait-for-chunks then
  per-path plane + staggered crate spawns; CreateFlightPaths
  IL=355 (MakePlayerClusters 30 m, CalcSupplyDropMetrics 1-4
  planes, crateY min(player.y+180, 276), FindSafePoint >= 600 m
  from players, ClampToMapExtents); SpawnPlane IL=74 supplyPlane
  entity + SetDirectionToFly (20*(len/120+10) ticks);
  EntitySupplyPlane SetDirectionToFly IL=12 (motion = dir*6,
  unreplicated) + OnUpdatePosition IL=49 (ticksToFly countdown ->
  MarkToUnload, engine loop, SetAirBorne).
## 2026-08-08 - tier-C: stat adders + supply crate entity

Done (V3.1.0 b14 IL):
- combat-damage.md: AddHealth IL=12 dead gate (Health<=0 no-op),
  AddStamina IL=17 Stamina!=null + Health>0 gates, AddWater IL=9
  ungated.
- aidirector.md: EntitySupplyCrate fallHitGround IL=15 soft landing
  (speed clamp 5, vertical min -0.75); OnEntityDeath IL=30 map-
  marker removal (type 13) + NetPackageEntityMapMarkerRemove
  broadcast + DropBagServer; OnEntityActivated IL=18 search via
  LockManager LockRequestLocal; canDespawn IL=2 always false.
## 2026-08-08 - tier-C: stat adders

Done (V3.1.0 b14 IL):
- combat-damage.md: EntityAlive.AddHealth IL=12 dead gate
  (Health<=0 no-op, then Health+=v); AddStamina IL=17
  Stamina!=null + Health>0 gates; AddWater IL=9 ungated.
## 2026-08-08 - tier-C: throw family

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionThrowAway.ExecuteAction IL=137
  charge/release + m_ThrowStrength (default vs maxThrowStrength*
  hold/max-strain), avatar itemThrownAwayTriggerHash event;
  throwAway IL=136 empty gate (passive 177) + TP camera gate +
  obstruction ray + ItemDropServer(stack, look*strength, 60,
  true, -1) + DecHoldingItem(1); ItemActionThrownWeapon IL=117
  WeaponPreFire/WeaponFire + jam-sound variant.
## 2026-08-08 - tier-C: ranged reload gate + accuracy machine

Done (V3.1.0 b14 IL):
- items.md 4.2: ItemActionRanged.CanReload IL=93 gate (not
  reloading, no cancel, jammed or below capacity, ammo in
  toolbelt/bag or infinite, passive 9 magazine); CancelReload
  IL=57 flags + cancel effect; updateAccuracy IL=175 target
  factor (passives 25/26/27/28/29/30/13) + AccuracyExpDecay
  exponential ease into the spread cone.
## 2026-08-08 - tier-C: TileEntityComposite envelope

Done (V3.1.0 b14 IL):
- tile-entities-power.md 2.2: TileEntityComposite write IL=74 /
  read IL=479 - version u16 18, outer + per-feature i32 size
  markers, blockId via blockIdMapping remap + BlockCompositeTileEntity
  check, owner (null in edit mode), featureCount u8, per-feature
  NameHash; legacy (<17) count/hash match vs modern GetFeatureIndex
  dispatch, skip-on-unknown, caught module read failures,
  ValidateSizeMarker checks.
## 2026-08-08 - tier-C: NetPackage contract + AddEntityBlockStub

Done (V3.1.0 b14 IL):
- network.md 3a: NetPackage base contract - defaults (channel 0,
  compress false, reliable true, pre-auth false, direction Both),
  ShouldProcess true / HandleSkipped pool-free, PackageId from
  runtime type, send-queue Interlocked refcount,
  ValidEntityIdForSender IL=49 + ValidUserIdForSender IL=29
  guards, override sets (channel-1 big-data, compress-true,
  unreliable entity per-tick, pre-auth handshake, direction split).
- tile-entities-power.md: Chunk.AddEntityBlockStub IL=21 UInt64-
  keyed Set with old-stub queueing into blockEntityStubsToRemove on
  cell collision.
## 2026-08-08 - tier-C: NetPackage base contract

Done (V3.1.0 b14 IL):
- network.md 3a: NetPackage defaults (channel 0, compress false,
  reliable true, pre-auth false, direction Both); ShouldProcess
  true / HandleSkipped pool-free; PackageId from runtime type;
  send-queue Interlocked refcount; ValidEntityIdForSender IL=49 +
  ValidUserIdForSender IL=29 guards; override sets (channel-1
  big-data, compress-true, unreliable entity per-tick, pre-auth
  handshake, direction request/push split).
## 2026-08-08 - tier-C: PropRef wire form

Done (V3.1.0 b14 IL):
- blocks.md 4: PropRef.Read IL=12 - ChunkPos Vector2i + PropId i32
  (prop addressed by prop chunk + per-chunk id).
## 2026-08-08 - tier-C: BlockValueRef wire discriminant

Done (V3.1.0 b14 IL):
- blocks.md 4: BlockValueRef.Read IL=23 - u8 discriminant 0 None /
  1 Block (StreamUtils.ReadVector3i) / 2 Prop (PropRef.Read),
  else ArgumentOutOfRangeException; first field of every
  BlockChangeInfo on the wire.
## 2026-08-08 - tier-C: ChunkBlockLayer storage + BlockChangeInfo wire

Done (V3.1.0 b14 IL):
- world-chunks.md 5.0a: ChunkBlockLayer split-byte layout
  (m_Lower8Bits + lower8BitSameValue compression, m_Upper24Bits
  3 bytes/cell), CalcOffset 1024-cell sub-planes; GetAt word
  assembly + Air fallback; SetAt materialize-on-differing-low-byte,
  pooled alloc/free (10000 cap); blockRefCount/tickRefCount +
  notifyLoadUnload HashSet bookkeeping; bOnlyTerrain +
  CheckOnlyTerrain IL=153 scan.
- blocks.md 4: BlockChangeInfo wire (Write IL=89 / Read IL=76):
  BlockValueRef + changedByEntityId i32 + flags byte (bit 0 value,
  1 damage, 2 density, 3 force-density, 4 update-light, 5 texture)
  + flagged payloads.
## 2026-08-08 - tier-C: ChunkBlockLayer storage

Done (V3.1.0 b14 IL):
- world-chunks.md 5.0a: ChunkBlockLayer split-byte layout
  (m_Lower8Bits + lower8BitSameValue compression, m_Upper24Bits
  3 bytes/cell), CalcOffset IL=12 1024-cell sub-planes; GetAt
  IL=61 word assembly + Air fallback; SetAt IL=294
  materialize-on-differing-low-byte, pooled alloc/free (10000
  cap); blockRefCount/tickRefCount + notifyLoadUnload HashSet
  bookkeeping; bOnlyTerrain + CheckOnlyTerrain IL=153 scan.
## 2026-08-08 - tier-C: ItemClassModifier selection leaves

Done (V3.1.0 b14 IL):
- items.md 2: ItemClassModifier selection - GetItemModWithAnyTags
  IL=53 (installable/disallowed tag filter + shared modIds scratch
  + uniform pick), GetDesiredItemModWithAnyTags IL=67 desired bias,
  GetCosmeticItemMod twin, GetPropertyOverride IL=50 exact-name
  then "*" wildcard entry, HasAllTags/HasAnyTags ModifierTags
  tests.
## 2026-08-08 - tier-C: ItemValue metadata + mod property overrides

Done (V3.1.0 b14 IL):
- items.md 2: ItemValue typed metadata - lazy Metadata dict +
  TypedMetadataValue TypeTag (Float=1/Int=2/String=3);
  SetMetadata IL=86 update-vs-create with tag-mismatch warnings;
  GetMetadata IL=17 / TryGetMetadata typed unbox;
  GetPropertyOverride IL=88 first ItemClassModifier wins over
  Modifications then CosmeticMods.
## 2026-08-08 - tier-C: LootFromXml loader

Done (V3.1.0 b14 IL):
- loot-economy.md 7b: LootFromXml - coroutine entry IL=6;
  LoadLootContainer IL=275 (name/count/size/buff/sounds/flag
  bools/destroy_on_close/on_open_event/open_time, quality template
  check, ParseItemList + Init); ParseItemList IL=334 (prob/
  force_prob/group/name/tags, count only for stackable, quality
  override, mods/mod_chance/requirement/buffs/random_durability);
  LoadLootGroup IL=197 (all -> -1, parentGroup, abundance_type);
  LoadLootQualityTemplate IL=231; LoadLootSetting IL=142
  (POITierMod/POITierBonus).
## 2026-08-08 - tier-C: StreamUtils binary primitives

Done (V3.1.0 b14 IL):
- dedicated-misc-systems.md: StreamUtils - ReadVector3/3i/Quaterion
  component-wise LE; Color32 one-u32 RGBA packing (ReadColor32
  IL=39, WriteColor32 IL=34); null-flagged ReadString IL=8; ReadGuid
  16-byte span + EndOfStream; 7-bit varint pair; Read/Write Int32 LE
  + Byte[] ref-offset variants; StreamCopy chunked copy +
  WriteStreamToFile.
## 2026-08-08 - tier-C: batch block commit machine

Done (V3.1.0 b14 IL):
- blocks.md 4.1: World.SetBlocksRPC IL=6 delegate;
  GameManager.SetBlocksRPC IL=29 ChangeBlocks + NetPackageSetBlock
  broadcast / client request; GameManager.ChangeBlocks IL=530
  (ccChanged lock, acting-player resolve, density derivation
  DensityAir/Terrain, bChangeDamage type guard, SetBlockValue vs
  position path, SetTopSoilBroken neighbor chunks + UncullChunk,
  TE ReplacedBy/RemoveTileEntityAt/UpgradeDowngradeFrom, LockManager
  force-unlock, RemoveBlockTrigger, QuestEventManager.BlockChanged,
  sleeping-bag spawn-point edges + player-data save, texture
  commit/clear).
## 2026-08-08 - tier-C: MemoryPools object pool surface

Done (V3.1.0 b14 IL):
- dedicated-misc-systems.md: MemoryPooledObject stack free list
  (Alloc IL=33 pop + Activator fallback + IMemoryPoolableObject.
  Reset, AllocSync/FreeSync Monitor locks, Cleanup IL=43,
  SetCapacity); InitStatic IL=45 capacities (PoolChunks 1000,
  poolCBL/poolCBC 50000, poolMS 40); full .cctor set
  (poolMemoryStream, binary reader/writer, MemoryPooledArray
  family, CBL bit caches, DynamicObjectPool).
## 2026-08-08 - tier-C: ChunkBlockChannel storage model

Done (V3.1.0 b14 IL):
- save-region.md 2: ChunkBlockChannel storage - 64*bytesPerVal
  layers + sameValue compression, bandStart=(y>>2)*bytesPerVal,
  cellOffs=z*16+x+(y&3)*256 (1024 cells), getData/getSameValue
  byte assembly, GetSet IL=79 no-op/prefill/write,
  checkSameValue + CheckSameValue sweep, pooled CBCLayer,
  ctor IL=27.
## 2026-08-08 - tier-C: TileEntity save preamble + type registry

Done (V3.1.0 b14 IL):
- save-region.md 2: base TileEntity write IL=19 (u16 v19, Vector3i
  chunkPos, u64 heapMapUpdateTime) / read IL=37 (v<=18 legacy i32
  discard, heapMapLastTime = time - AIDirector delay);
  InstantiateFromRead IL=88 type switch (12 concrete ctors,
  unknown dropped); TryReadLegacyType IL=81 legacy types
  4/5/10/11/13/22 -> TileEntityComposite, gore discarded; base
  virtuals stubs.
## 2026-08-08 - tier-C: FastTags bitmask

Done (V3.1.0 b14 IL):
- dedicated-misc-systems.md: FastTags - UInt64[] + singleBit fast
  path; lazy per-group bit registry (GetBit IL=56,
  Interlocked.Increment first-use order, tags/bitTags +
  allInternal growth); Parse comma-split via locked scratch;
  CombineTags 2..5 OR forms; Test_Bit/AllSet/AnySet/IsOnlyBit;
  Remove; GetTagNames/ToString reverse mapping.
## 2026-08-08 - tier-C: ParticleEffect FX record

Done (V3.1.0 b14 IL):
- dedicated-misc-systems.md: ParticleEffect wire layout (Read
  IL=53, ParticleId = name hash, sound names null-normalized,
  attachment u8); SpawnParticleEffectServer IL=41 client/server
  split + channel-192 broadcast; SpawnParticleEffect IL=339 audio
  -> AIDirector noise events, dedicated short-circuit,
  4-instance-per-entity cap, origin-relative world spawn;
  GetParentTransform IL=58 head/pelvis attachment.
## 2026-08-08 - tier-C: vehicle damage machine

Done (V3.1.0 b14 IL):
- vehicles-drones-turrets.md 4.2c: damageEntityLocal IL=31
  DamageResponse build; ProcessDamageResponseLocal IL=120 (Disease/
  Suffocation immunity, blood-moon knockback, External rider splash
  with FriendlyFireCheck skip); ApplyDamage IL=86 explodeHealth
  machine (health-1 or 99999 entry, 20% roll, ExplosionServer),
  3% max-health buffer; ApplyAccumulatedDamage IL=19 fractional
  accumulator; ApplyCollisionDamageToAttached IL=32
  Internal/VehicleInside crash damage; GetBlockDamageScale IL=13.
## 2026-08-08 - tier-C: Inventory held-slot accessors + ForceHoldingItemUpdate

Done (V3.1.0 b14 IL):
- items.md 5: held-slot accessors bare-hand fallbacks
  (get_holdingItem/ItemValue/Stack/Data), slot-count constants
  (INVENTORY_SLOTS=PUBLIC_SLOTS+1, PUBLIC_SLOTS 10 vs 20 prefab
  editor, DUMMY_SLOT_IDX last slot), IsHoldingGun IL=9;
  ForceHoldingItemUpdate IL=91 forced held-item rebuild with 6
  xref callers (HealBeamWeapon.Fire, EntityNetworkStats.ToEntity,
  EModelBase.SwitchModelAndView x2, client initialize-holding
  coroutine, WorldStaticData.ReloadItemModifiers).
## 2026-08-08 - tier-C: StringParsers contract

Done (V3.1.0 b14 IL):
- dedicated-misc-systems.md: StringParsers - Parse vs TryParse,
  substring overloads, float defaults 511 vs integer defaults 7;
  internalParseBool True/False-only, internalParseDouble hex
  rejection, float overflow guard; GetSeparatorPositions scanner
  + findOther; vector/quaternion/color/min-max table; ParseList.
## 2026-08-08 - tier-C: DynamicProperties property bag

Done (V3.1.0 b14 IL):
- dedicated-misc-systems.md: DynamicProperties - six dicts
  (Values/Params1/Params2/Data/Classes/Array), Parse IL=123 class
  recursion + ValidateKey dot ban + ^-token ReplaceProperty + name/
  class collision throw, AddArray IL=70, Load IL=37; Get* silent
  defaults vs Parse* Warning; ParseData/ParseKeyData;
  ParseStringFloatDictWithSubStringKey; CopyFrom/copyKey dotted-path
  exclusions; Clear skips Array; MemoryPack 6-field Deserialize.
## 2026-08-08 - tier-C: vehicle attach slot-claim + detach chain

Done (V3.1.0 b14 IL):
- vehicles-drones-turrets.md 4.2: slot-claim rules in Entity.AttachEntityToSelf
  IL=56 (one occupant per slot, existing-slot reuse, conflicting request
  detaches old occupant, free-slot pick, slot-0 serverPos snapshot +
  isEntityRemote copy), GetAttachFreeCount IL=31; detach chain
  EntityAlive.Detach IL=27 (inventory restore), Entity.Detach IL=79 (exit
  teleport + parent restore), Entity.DetachEntity IL=21 (slot-0 isEntityRemote
  restore), EntityVehicle.DetachEntity IL=157 (delayed-attach cancel + server
  RB wake). First draft landed in dedicated-misc-systems.md then relocated
  (duplicated existing 4.2 content there).
## 2026-08-08 - tier-C: AddChunkObserver

Done (V3.1.0 b14 IL):
- network.md: ChunkManager.AddChunkObserver IL=15 (ChunkObserver build, m_ObservedEntities append, isInternalForceUpdate)

## 2026-08-08 - tier-C: TEFeatureStorage

Done (V3.1.0 b14 IL):
- tile-entities-power.md 4.7: CountItem IL=33 (class-matched sum), AddItem IL=29 (first empty slot, UpdateSlot + SetModified)

## 2026-08-08 - tier-C: lockable password leaves

Done (V3.1.0 b14 IL):
- tile-entities-power.md 4.7: CheckPasswordHash IL=24 (owner/password gates, allowedUserIds add), IsLocked/HasPassword

## 2026-08-08 - tier-C: TEFeatureDoor

Done (V3.1.0 b14 IL):
- tile-entities-power.md 4.7: TEFeatureDoor Write IL=23 (disk v18 + isOpen; net isOpen + animateOnSync cleared), CanOpen IL=29 (lockpick + lock gates)

## 2026-08-08 - tier-C: TraderArea spatial tests

Done (V3.1.0 b14 IL):
- dedicated-leftovers.md: Overlaps IL=38 (ProtectPosition+Size 2D AABB), IsWithinTeleportArea IL=93 (volume world box, sandbox-mode disabled)

## 2026-08-08 - tier-C: TraderArea.SetClosed

Done (V3.1.0 b14 IL):
- dedicated-leftovers.md: SetClosed IL=222 (chunk-span gate, IndexedBlocks TraderOnOff walk, ProtectBounds filter, TEFeatureDoor toggle)

## 2026-08-08 - tier-C: TraderArea blob

Done (V3.1.0 b14 IL):
- dedicated-leftovers.md: TraderArea Write IL=111 / Read IL=91 (pos int32, size int16, padding sbyte -2 x/z, per-volume sbyte+byte), GetReadWriteSize 22+6n, IsWithinProtectArea AABB

## 2026-08-08 - tier-C: damage-scale pick

Done (V3.1.0 b14 IL):
- items.md 4: EntityPlayer.GetBlockDamageScale IL=6 (TerrainDamagePercent vs BlockDamagePercent)

## 2026-08-08 - tier-C: player leaves

Done (V3.1.0 b14 IL):
- combat-damage.md 2: FriendlyFireCheck IL=77 (GameStats 23 modes 0/1/2), GetBreadcrumbPos ring sample, GetFallingSavePosition fallthrough recovery

## 2026-08-08 - tier-C: ItemActionAttack modifiers

Done (V3.1.0 b14 IL):
- items.md 4: difficultyModifier IL=44 (client-controlled scaling, Incoming/EntityIncomingDamageModifier), DegradationModifier IL=14 lerp, harvest-tool bonus IL=43

## 2026-08-08 - tier-C: entity registers + distance family

Done (V3.1.0 b14 IL):
- entity-ai.md: Entity.CheckDistance family (all funnel to magnitude < 1.0)
- entity-ai.md: AddOwnedEntity IL=35 (dedupe, server NetPackageOwnedEntitySync broadcast 192), AddPart/AddParticle IL=17 upsert

## 2026-08-08 - tier-C: water immersion

Done (V3.1.0 b14 IL):
- entity-ai.md: Entity.CalcWaterLevel IL=157 (vertical span scan, 8-dir offset sampling, surface cell 0.6 cap)
- light-mesh-water.md: World.GetWaterPercent IL=14 (GetWater -> GetMassPercent, 0 on missing chunk)

## 2026-08-08 - tier-C: block/tile-entity reads

Done (V3.1.0 b14 IL):
- world-chunks.md: EnableInsideBlockEntities IL=45 + EnableEntityBlocks IL=51 toggles
- tile-entities-power.md: Chunk.GetTileEntity IL=11 TryGetValue read

## 2026-08-08 - tier-C: inside/entity block toggles

Done (V3.1.0 b14 IL):
- world-chunks.md: EnableInsideBlockEntities IL=45 (blockEntityStubs by world-pos key, SetActive on transform)
- world-chunks.md: EnableEntityBlocks IL=51 (name-contains filter, toggled count)

## 2026-08-08 - tier-C: inside-device register + test

Done (V3.1.0 b14 IL):
- world-chunks.md: AddInsideDevicePosition IL=20 (Vector3b + hash set, IsInternalBlocksCulled, dead bv param)
- world-chunks.md: Chunk.isInside IL=12 hash-set membership test

## 2026-08-08 - tier-C: entity stat blobs

Done (V3.1.0 b14 IL):
- entity-stats.md 5: EntityStats/PlayerEntityStats blob (v11, Health + Stamina/Water/Food + CoreTemp/2 sbyte)
- entity-stats.md 5: Stat record v6 (value/maxModifier/baseMax/originalBaseMax/originalValue), <=5 legacy float discard

## 2026-08-08 - tier-C: deco join sync + tick

Done (V3.1.0 b14 IL):
- chunk-providers.md 5: SendDecosToClient IL=32 (write list under lock, sliced NetPackageDecoUpdate loop)
- chunk-providers.md 5: UpdateTick IL=330 (drains add/remove/rect-reset/chunk-reset queues, checkDelayTicks-gated player check)

## 2026-08-08 - tier-C: deco shape hooks + reset

Done (V3.1.0 b14 IL):
- chunk-providers.md 5: BlockShapeDistantDeco OnBlockAdded/Loaded (attach, forced Y / non-remote), OnBlockRemoved (detach), OnBlockValueChanged base-only
- chunk-providers.md 5: ResetDecosForWorldChunk IL=73 (off-main queue, RestoreGeneratedDecos, NetPackageDecoResetWorldChunk broadcast)

## 2026-08-08 - tier-C: deco edit-sync + load

Done (V3.1.0 b14 IL):
- chunk-providers.md 5: DecoManager.SetBlock IL=19 (air removes, else replace via remove + AddDecorationAt)
- chunk-providers.md 5: DecoManager.Read IL=29 (loadedDecos set, int32 count, per-record DecoObject.Read)

## 2026-08-08 - tier-C: deco attach/detach

Done (V3.1.0 b14 IL):
- chunk-providers.md 5: AddDecorationAt IL=142 (off-main queue SAddDecoInfo, terrain Y-snap, bDirty, dedupe by realYPos/bv/rotation)
- chunk-providers.md 5: RemoveDecorationAt IL=52 (disabled/missing -> false, off-main queue, main-thread RemoveDecoObject)

## 2026-08-08 - tier-C: DecoChunk buckets + reads

Done (V3.1.0 b14 IL):
- chunk-providers.md 5: AddDecoObject IL=67 (16x16 bucket, main-thread instantiate, OcclusionManager), GetDecoObjectAt state!=1 scan, ToDecoChunkPos 128-fold, MakeKey16
- chunk-providers.md 5: GetDecorationsOnChunk IL=143 (lazy decorate under lock, null warning, SBlockPosValue output)

## 2026-08-08 - tier-C: decoration.7dt codec

Done (V3.1.0 b14 IL):
- chunk-providers.md 5: DecoManager.Write IL=56 (int32 count + per-record), WriteTask IL=38 stream copy + truncate
- chunk-providers.md 5: DecoObject.Write no-block error + NameIdMapping.AddMapping bookkeeping; Read IL=19 reverse

## 2026-08-08 - tier-C: distant-deco seeding + lazy decorate

Done (V3.1.0 b14 IL):
- chunk-providers.md 5: decorateChunkRandom IL=243 (fixed-size skip, 128x128 cell gates, distant-deco walk prob*2 + ore noise)
- chunk-providers.md 5: GetDecoOccupiedAt IL=87 lazy decorate under lock (seed from chunk XZ), GetDecoOccupiedFromMap IL=26 plain read

## 2026-08-08 - tier-C: DecoOccupiedMap leaves

Done (V3.1.0 b14 IL):
- chunk-providers.md 6.2: Get/Set via CheckPosition (NoneAllowed 8 out-of-bounds), SetArea min-wins rect, CheckArea conflict gate
- chunk-providers.md 6.2: DecoManager.CheckPosition IL=34 index fold (x+halfW) + (z+halfH)*width

## 2026-08-08 - tier-C: FromRaw texture/CRC leaves

Done (V3.1.0 b14 IL):
- chunk-providers.md 4.1: generateHalfResTexture IL=27 (mip-1 half-res, error fallback), GetProviderId=4, ARGB32ToColor copy
- chunk-providers.md 4.1: GetChunkProtectionLevel/GetHeight/GetWorldSize overrides, filesNeedProcessing CRC gate

## 2026-08-08 - tier-C: FromRaw override + CRC leaves

Done (V3.1.0 b14 IL):
- chunk-providers.md 4.1: GetChunkProtectionLevel delegation, GetHeight try/catch, GetWorldSize = dims * scale
- chunk-providers.md 4.1: filesNeedProcessing IL=32 (dtm _processed suffix + 4 splat files + verifyFileHashes)

## 2026-08-08 - tier-C: FromRaw POI overrides + sequence groups

Done (V3.1.0 b14 IL):
- game-events.md: sequence entity-group leaves (AddEntityToGroup Twitch gate, GetEntityGroupLiveCount, ClearEntityGroup)
- chunk-providers.md 4.1: GetPOIBlockIdOverride IL=51 (bFixedWaterLevel liquid suppression), GetPOIHeightOverride IL=66 (m_YPosFill for liquid only, worldScale fold)

## 2026-08-08 - tier-C: sequence target + props

Done (V3.1.0 b14 IL):
- game-events.md: CanPerform IL=44 AND of requirements+actions; SetupTarget IL=97 POIInstance resolution by TargetType; HasTarget IL=41 per-type
- game-events.md: ParseProperties IL=70 knobs (allow_user_trigger, action_type/target_type enums, allow_while_dead, refund_inactivity, single_instance, category)

## 2026-08-08 - tier-C: GameEvent sequence machine

Done (V3.1.0 b14 IL):
- game-events.md: RegisterLink IL=35 first-link-wins + SequenceLink fields, UnRegisterLink IL=25 RemoveAt
- game-events.md: GameEventActionSequence.Update IL=287 (phase dispatch, refund-inactivity 60s, result 3/1+IgnoreRefund -> PhaseOnComplete, 2 -> PhaseOnDenied)

## 2026-08-08 - tier-C: GameEventManager flag + sequence leaves

Done (V3.1.0 b14 IL):
- game-events.md: HandleFlagBuffUpdates IL=69 (1s timer, flag->twitch_buff* map, AddBuff on all players)
- game-events.md: GetSequenceLink IL=38 (CheckLink scan -> OwnerSeq), GetTargetType IL=11 (dict lookup, enum 0 default)

## 2026-08-08 - tier-C: Chunk point finders + height queries

Done (V3.1.0 b14 IL):
- spawning.md 4: FindRandomTopSoilPoint IL=80 (GetHeight+1 world coords, CanMobsSpawnAtPos gate), FindRandomCavePoint IL=95 (down-walk while y>2 && y>relMinY)
- terrain-height.md: IsOpenSkyAbove IL=9 (y >= GetHeight), GetTopMostTerrainHeight IL=28 (max byte)

## 2026-08-08 - tier-C: EntityClass registry + ItemStack.FromString

Done (V3.1.0 b14 IL):
- dedicated-misc-systems.md: EntityClass FromString=GetHashCode, GetId linear scan, GetEntityClassName null fallback, GetEntityClassWithinMaxTier walk
- items.md 2: ItemStack.FromString IL=38 name=count parse

## 2026-08-08 - tier-C: sync create + sleeper gate

Done (V3.1.0 b14 IL):
- entity-ai.md D8.2: Chunk.CanSleeperSpawnAtPos IL=36 (below IsCollideMovement when checkBelow, cell open-space)
- spawning.md 2: EntityFactory.CreateEntity(ecd) IL=7 sync path (Start(true) + CompleteEntity), convenience overload id alloc + ItemValue.None

## 2026-08-08 - tier-C: spawn area sampler

Done (V3.1.0 b14 IL):
- spawning.md 2: GetRandomSpawnPositionInAreaMinMaxToPlayers IL=164 (10 tries, y=GetHeight+1, bedroll/CanMobsSpawnAtPos/isPositionFarFromPlayers/view-cone gates, (0.5, GetTerrainOffset, 0.5) center)
- spawning.md 2: maxDistance parameter UNUSED in this build (placement band is min-only + view-cone)

## 2026-08-08 - tier-C: entity stubs + spawner-class day resolution

Done (V3.1.0 b14 IL):
- server-browser-prefabs.md 3.2: Prefab.CopyEntitiesIntoChunkStub IL=88 (enemy gate, chunk filter, +0.25 y offset, AddEntityStub)
- spawning.md: EntitySpawnerClassForDay.Day IL=87 wrap (mod Count-1, 0->Count-1) / clamp / null-slot fallback to days[0], AddForDay null-pad

## 2026-08-08 - tier-C: Prefab stamping engine

Done (V3.1.0 b14 IL):
- server-browser-prefabs.md 3.2: CopyBlocksIntoChunkNoEntities IL=715 structural flow (AABB clip, density-aware placement, placeholder replace, deco/inside/water/texture/quest-gate, TE + BlockTrigger clones, terrain height)
- server-browser-prefabs.md 3.2: InitTerrainFillers IL=17 (filler block ids from Constants), IsCullThisPrefab IL=5 (!bExcludePOICulling)

## 2026-08-08 - tier-C: POI container + color registry

Done (V3.1.0 b14 IL):
- chunk-providers.md 4.1: WorldGridCompressedData.Contains IL=25 bounds test, GetData IL=18 world-to-grid fold
- chunk-providers.md 3.3: getPoiForColor TryGetValue + AddPoiMapElement first-wins registration by m_uColorId

## 2026-08-08 - tier-C: POI InitData + WaterFloodFill

Done (V3.1.0 b14 IL):
- chunk-providers.md 4.1: <InitData>d__15 coroutine IL=774 (poiCols grid, water16x16Chunks, water_info.xml, default PoiMapElement id 5, splat4 format 5 check, splat3 load, m_Poi wrap)
- chunk-providers.md 4.1: WaterFloodFill IL=196 BFS (colWater mark, per-16x16 chunk height byte, 100k cap)

## 2026-08-08 - tier-C: deco cell layout + PoiMapElement picks

Done (V3.1.0 b14 IL):
- chunk-providers.md: EnumDecoAllowed cell bit layout (slope bits 0-1, size 2-3, street bit 4; AllowBig = size 0, AllowSmall = size < 2, Nothing >= 2)
- chunk-providers.md 3.3: PoiMapElement.GetRandomBlockOnTop/GetRandomDecal IL=26 prob test, GetDecal bounds-checked

## 2026-08-08 - tier-C: density constants + deco field writers

Done (V3.1.0 b14 IL):
- terrain-height.md: MarchingCubes density sentinels (Air 127/AirHi 100/Terrain -128/TerrainHi -100), GetDecorationOffsetY clamp formula
- chunk-providers.md: Chunk.SetDecoAllowedSizeAt/SetDecoAllowedStreetOnlyAt IL=19 (Ensure + read-modify-write via SetDecoAllowedAt)

## 2026-08-08 - tier-C: terrain snap engine

Done (V3.1.0 b14 IL):
- chunk-providers.md 3.3: ChunkCluster.snapTerrainToPosition IL=113 (air-above-terrain lift, density clamp to DensityTerrain or half, SetBlockRPC routing)
- chunk-providers.md 3.3: SnapTerrainToPositionAroundRPC IL=49 (4 cardinal neighbors, liftUp=false halfDensity=true)

## 2026-08-08 - tier-C: POI query + water leaves

Done (V3.1.0 b14 IL):
- server-browser-prefabs.md 3.2: GetPrefabsAtXZ IL=70 AABB scan via PrefabBinarySearch IL=58 (xMin-200 lookback, resort gate)
- light-mesh-water.md: WaterUtils.GetVoxelKey 3D IL=10 (+y), TryOpenChunkForUpdate IL=33 (ScopedChunkWriteAccess, InProgressWaterSim volatile)

## 2026-08-08 - tier-C: DynamicPrefabDecorator decorate path

Done (V3.1.0 b14 IL):
- server-browser-prefabs.md 3.2: DecorateChunk IL=70 (thread-local list, GetPrefabsAtXZ +15 span, prefabInstanceSizeComparison descending x*z)
- server-browser-prefabs.md 3.2: SortPrefabs IL=38 allPrefabsSorted rebuild; CopyIntoChunk IL=34 (entity stubs gated on IsEditor || GameStats 24)

## 2026-08-08 - tier-C: sub-biome noise fold

Done (V3.1.0 b14 IL):
- chunk-providers.md 3.3: GetSubBiomeIdxAt IL=79 (FBM(x+ox, z+oz, freq)*0.5+0.5, cached per freq/offset, y unused, noiseMin<=v<noiseMax)
- chunk-providers.md 3.3: GetBiomeOrSubAt IL=24 wrapper (y slot hard-coded 0)

## 2026-08-08 - tier-C: radiation map + fill loops

Done (V3.1.0 b14 IL):
- chunk-providers.md 4.1: InitData radiation branch corrected (<=512x512 -> radiationMapSmall from red channel; >512 -> Radiation ignored log, not tiled)
- chunk-providers.md 4.1: LoadRadiationMap/TileArray machinery + FillRadiationResult IL=83 / FillRadiationFileBackedArray IL=104 layouts

## 2026-08-08 - tier-C: PrefabCache + PrefabInstance registration

Done (V3.1.0 b14 IL):
- server-browser-prefabs.md 3.2: PrefabCache.GetPrefab IL=47 load-or-cache; GetPrefabRotated IL=79 rotation&=3, Prefab[4] slots, dead fixChildblocks flag
- server-browser-prefabs.md 3.2: PrefabInstance.GetOccupiedChunks IL=65 (bb -> chunk key range), AddWorldPrefab IL=32 (allPrefabs/worldPrefabs/poiPrefabs + isSortNeeded)

## 2026-08-08 - tier-C: EventPrefabs + NetPackageEventPrefab

Done (V3.1.0 b14 IL):
- server-browser-prefabs.md 3: EventPrefabs TryPlaceAt IL=122 (GetPrefabRotated, TryResetChunks gate, AddEventPrefab, NetPackageEventPrefab, needsSaving)
- server-browser-prefabs.md 3: Load IL=125 eventprefabs.dat format, Save IL=70 (version 1, ThreadedFileWriterQueue)
- server-browser-prefabs.md 3: NetPackageEventPrefab write/read/ProcessPackage IL=48 (op 0 TryAdd / 1 Remove, client-gated)
- server-browser-prefabs.md 3: PrefabInstance.Serializable (id/name/pos/rot, GetLength = 17 + name.Length)

## 2026-08-08 - tier-C: Prefab terrain snap + volume realization

Done (V3.1.0 b14 IL):
- chunk-providers.md 3.3: Prefab.SnapTerrainToArea IL=65 (footprint + 1-cell rim, SnapTerrainToPositionAtLocal y-1, perimeter flag)
- server-browser-prefabs.md 3.2: CopyVolumesIntoWorldCommon IL=208 (chunk-overlap filter, sandbox trader skip types 1/3, FindOrCreateWorldVolume, per-chunk AddWorldVolume walk)

## 2026-08-08 - tier-C: SleeperVolume persistence

Done (V3.1.0 b14 IL):
- entity-ai.md D8.4: SleeperVolume Write/Read blob v21 (group/box/respawn/numSpawned, flags u16 bits + int32 minScript bit 16, counted lists)
- entity-ai.md D8.4: Read version gates (groupId>=16, legacy u64<=13, legacy i32>7, respawnMap>=8, flags>=18, spawnPointIndex>=17, groupName>=21, passive ids)
- entity-ai.md D8.4: SpawnPoint Write/Read (pos, rot, block name; legacy triples <20, name >14)

## 2026-08-08 - tier-C: chunk-event blob + entity creation builders

Done (V3.1.0 b14 IL):
- spawning.md 5: AIDirectorChunkEvent Write/Read v2 blob (pos, Value, EventType byte, Duration; v1 legacy uint64 discard)
- spawning.md 2: EntityFactory.SetupEntityCreationData overloads (nextEntityID alloc, itemStack vs blockValues/textureFullArrays)
- spawning.md 2: CreateEntityOperation.Start IL=25 id allocation (auto-id -1, else max bump) + LoadAssets

## 2026-08-08 - tier-C: chunk-heat component + AIDirectorChunkData

Done (V3.1.0 b14 IL):
- spawning.md 5: NotifyEvent IL=22 + StartCooldownOnNeighbors IL=55 (5x5 region grid, neighbors table)
- spawning.md 5: AIDirectorChunkEventComponent Write/Read v1 (outer>=5), int64 region keys
- spawning.md 5: AIDirectorChunkData AddEvent merge, DecayEvents, Tick, FindBestEventAndReset (240 cooldown), neighbor 180/720, SetLongDelay 1320, blob v2

## 2026-08-08 - tier-C: EntitySpawner persistence + Spawn wrapper

Done (V3.1.0 b14 IL):
- terrain-height.md: Chunk terrain-normal storage (m_NormalX/Y/Z x127 clamp, GetTerrainNormalY /127)
- spawning.md 4: EntitySpawner Write/Read blob v3 layout + invalid-class fallback, ModifySpawnCountByGameDifficulty EnemySpawnMode gate
- spawning.md 4: Spawn IL=31 wrapper + stock precondition/position callbacks (bIgnoreTrigger, GetClosestPlayer 160, cave/ground spawn)

## 2026-08-08 - tier-C: BiomeImageLoader + PerlinNoise

Done (V3.1.0 b14 IL):
- chunk-providers.md 4.1: BiomeImageLoader <Load>d__11 (GetPixelData, block grid SetSameValue/SetValue, MicroStopwatch frame-slice), GetBiomeId cache, ARGB/RGBA pack, BiomeIdToColor32
- chunk-providers.md 6.1: PerlinNoise Lattice perm/gradient hash, Smooth/Lerp, Noise 2D/3D clamp, Noise01, FBM 2-octave

## 2026-08-08 - tier-C: splat loader + InitData coroutine

Done (V3.1.0 b14 IL):
- chunk-providers.md 4.1: loadSplatMaps IL=883 (splat1/2/3 png, 12-channel dominance chain -> splatMapMaxValue, splatScaleDiv = worldWidth/splatW)
- chunk-providers.md 4.1: ProcessColor IL=22 channel fold, InitData coroutine (biomes.tga/png, BiomeImageLoader, radiation.png/tga, >512 tiled branch)

## 2026-08-08 - tier-C: POI stamping + ore-noise gate

Done (V3.1.0 b14 IL):
- chunk-providers.md 3.3: WorldDecoratorPOIFromImage.DecorateChunkOverlapping IL=472 (poi color -> PoiMapElement, decal, water fill, GetRandomBlockOnTop)
- chunk-providers.md 3.3: LoadWaterInfo IL=127 XML format, GetWaterChunks16x16, InitData coroutine stub
- chunk-providers.md 6.1: GameUtils.GetOreNoiseAt IL=23 (0.05 scale, -0.333 rebase, x3) + CheckOreNoiseAt

## 2026-08-08 - tier-C: WorldDecoratorBlocksFromBiome driver + decoratePrefabs

Done (V3.1.0 b14 IL):
- chunk-providers.md 3.3: DecorateChunkOverlapping IL=245 (rwlock, per-chunk seed, biomePositions buckets, sub-biome fold, trader/POI-liquid cells)
- chunk-providers.md 3.3: decorateSingleBlocks IL=56 + decorateSingleBlock IL=139 cell gates
- chunk-providers.md 3.3: decoratePrefabs IL=403 biome-prefab path (cache lookup, footprint fit, rotation, CopyIntoLocal)

## 2026-08-08 - tier-C: WorldBiomeProviderFromImage + DecoUtils cluster

Done (V3.1.0 b14 IL):
- world-generation.md 3.1: GetBiomeAt scale/offset fold, humidity/temperature stubs, GetRadiationAt, GetTopmostBlockValue splat switch, worldCoordsToTileCoords
- chunk-providers.md 6.1: decorateSingleBlockTryPlaceDeco IL=287 gate order (slope/fertility/ore-noise/placeholder/replace)
- chunk-providers.md 6.1: DecoUtils radius/flag leaves, CanPlaceDeco 4/7-arg, ApplyDecoAllowed + big-deco scanners

## 2026-08-08 - tier-C: WorldBlockFiller + BiomeLayer

Done (V3.1.0 b14 IL):
- chunk-providers.md 3.3: WorldBlockFiller grid ((x<<4|z)<<8|y, 255 untouched), fillChunk IL=66, fillLevel IL=192 placement loop
- chunk-providers.md 3.3: setDecorationBlock IL=152 depth pick + 3x3 prob-gated cluster + center write
- world-generation.md 3.1: BiomeLayer AddResource IL=34 running sum / MaxResourceProb

## 2026-08-08 - tier-C: WeatherGroup Probabilities table

Done (V3.1.0 b14 IL):
- weather-environment.md 1.2: Probabilities List<Vector3>[5] table, AddProbability IL=14, Normalize IL=62
- weather-environment.md 1.2: GetRandomValue IL=54 dual-draw weighted+lerp, CalcMinMaxPossibleValue IL=44

## 2026-08-08 - tier-C: BiomeDefinition weather surface

Done (V3.1.0 b14 IL):
- weather-environment.md 1.2: AddWeatherGroup IL=57 (stormLevel, s->ms), SetupWeather IL=53 normalize
- weather-environment.md 1.2: WeatherRandomize/SelectWeatherGroup/Find*/GetValue/SetValue/GetDuration leaves

## 2026-08-08 - tier-C: ChunkAreaBiomeSpawnData blob layout

Done (V3.1.0 b14 IL):
- spawning.md 3: persisted budget blob v2 (byte ver 2, count<=255, int32 id, uint16 (maxCount<<8)|count, uint64 delayWorldTime)
- spawning.md 3: read v1 legacy discard; BeforeWrite pooled stream into ccd.data

## 2026-08-08 - tier-C: WorldBiomes lookups + ParseWeather

Done (V3.1.0 b14 IL):
- world-generation.md 3: GetBiome(byte/string) lookups, m_Name2BiomeMap
- world-generation.md 3: ParseWeather (IL=211) weathergroup parse mapping

## 2026-08-08 - tier-C: Chunk coordinate fold

Done (V3.1.0 b14 IL):
- world-chunks.md 2: Chunk.IsInChunk (IL=30) bounds test 0<=x<16/0<=y<256/0<=z<16
- world-chunks.md 2: Chunk.ToLocalPosition (IL=23) world-to-local mask x&15/y&255/z&15

## 2026-08-08 - tier-C: ToWorldPos

Done (V3.1.0 b14 IL):
- world-chunks.md 2: Chunk.ToWorldPos (IL=14/20/16) origin
  (m_X*16, m_Y*256, m_Z*16) + local offset.

## 2026-08-08 - tier-C: deco extractors

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: GetDecoAllowedSizeAt / GetDecoAllowedStreetOnlyAt
  (IL=6 each) field reads.

## 2026-08-08 - tier-C: deco-cell accessors

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: GetDecoAllowedAt (IL=44) occupancy downgrade;
  SetDecoAllowedAt (IL=49) stricter-field merge.

## 2026-08-08 - tier-C: deco array alloc

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: EnsureDecoBiomeArray (IL=8) 256-entry lazy alloc.

## 2026-08-08 - tier-C: deco slope gate

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: GetDecoAllowedSlopeAt (IL=6) / SetDecoAllowedSlopeAt
  (IL=19) with WithSlope rewrite.

## 2026-08-08 - tier-C: spawn-data build

Done (V3.1.0 b14 IL):
- spawning.md 6.2: GetChunkBiomeSpawnData (IL=40) lazy build via bspd.main
  custom-data; IsTraderArea (IL=22) world probe.

## 2026-08-08 - tier-C: area-master grid

Done (V3.1.0 b14 IL):
- spawning.md 6.2: ToAreaMasterChunkPos (IL=19) /5*5 snap; IsAreaMaster
  (IL=14) %5; corner-load gate (IL=44); dominant-biome init (IL=107).

## 2026-08-08 - tier-C: chunk tick gate

Done (V3.1.0 b14 IL):
- world-chunks.md 6: get_NeedsTicking (IL=13) TE/sleeper gate; GetTickRefCount
  (IL=13) layer tickRefCount.

## 2026-08-08 - tier-C: inside-device enable

Done (V3.1.0 b14 IL):
- tile-entities-power.md 1: EnableInsideBlockEntities (IL=45) stub SetActive
  pass over insideDevices.

## 2026-08-08 - tier-C: block-entity removal

Done (V3.1.0 b14 IL):
- tile-entities-power.md 1: removeBlockEntitesMarkedForRemoval (IL=133)
  occlusion + cleanup + pooling drain.

## 2026-08-08 - tier-C: only-terrain flag

Done (V3.1.0 b14 IL):
- world-chunks.md 2: IsOnlyTerrain (IL=8) / IsOnlyTerrainLayer (IL=24)
  bOnlyTerrain layer flag.

## 2026-08-08 - tier-C: entity-block/cull leaves

Done (V3.1.0 b14 IL):
- tile-entities-power.md 1: EnableEntityBlocks (IL=51) name-filter toggle;
  AddInsideDevicePosition (IL=20) culled path flag.

## 2026-08-08 - tier-C: entity-stub leaves

Done (V3.1.0 b14 IL):
- tile-entities-power.md 1: AddEntityStub (IL=5); RemoveEntityBlockStub (IL=30)
  packed-key remove + not-found warn.

## 2026-08-08 - tier-C: wall-volume registry

Done (V3.1.0 b14 IL):
- entity-ai.md: AddWallVolume (IL=69) + NetPackageWallVolume broadcast 192,
  AddWallVolumeAt (IL=50), GetWallVolume (IL=30) throw, FindWallVolume (IL=29),
  GetAllWallVolumes (IL=49).

## 2026-08-08 - tier-C: wall-volume links

Done (V3.1.0 b14 IL):
- terrain-height.md: Chunk.AddWallVolumeId (IL=18) 255 cap, GetWallVolumes
  (IL=3).

## 2026-08-08 - tier-C: trigger links

Done (V3.1.0 b14 IL):
- entity-ai.md trigger registry: Chunk.AddTriggerVolumeId (IL=18) 255 cap,
  GetTriggerVolumes (IL=3).

## 2026-08-08 - tier-C: sleeper links

Done (V3.1.0 b14 IL):
- entity-ai.md sleeper section: Chunk.AddSleeperVolumeId (IL=18) dedupe +
  255 cap error; GetSleeperVolumes (IL=3); GetTileEntities (IL=3).

## 2026-08-08 - tier-C: TE registry writes

Done (V3.1.0 b14 IL):
- tile-entities-power.md 1: AddTileEntity (IL=7) Set; RemoveTileEntityAt
  (IL=28) / RemoveTileEntity (IL=29) OnRemove wrap + isModified.

## 2026-08-08 - tier-C: indexed blocks + save ids

Done (V3.1.0 b14 IL):
- world-chunks.md 5: recalcIndexedBlocks (IL=26) rebuild; saveBlockIds (IL=53)
  nameIdMapping mark under lock.

## 2026-08-08 - tier-C: IsWater gate

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: Chunk.IsWater (IL=9) GetWater().HasMass().

## 2026-08-08 - tier-C: RecalcHeightAt

Done (V3.1.0 b14 IL):
- terrain-height.md: Chunk.RecalcHeightAt (IL=55) downward rescan writes
  m_HeightMap at first non-air/water cell.

## 2026-08-08 - tier-C: trigger store

Done (V3.1.0 b14 IL):
- entity-ai.md trigger section: Chunk triggerData DictionaryList,
  GetBlockTriggers (IL=3) + GetBlockTrigger (IL=9).

## 2026-08-08 - tier-C: SetLight nibble write

Done (V3.1.0 b14 IL):
- light-mesh-water.md 1: Chunk.SetLight (IL=56) sun/block nibble merge +
  NeedsRegenerationAt + isModified; ResetLights (IL=6).

## 2026-08-08 - tier-C: damage channel write

Done (V3.1.0 b14 IL):
- world-chunks.md 2: Chunk.SetDamage (IL=9) chnDamage long write.

## 2026-08-08 - tier-C: damage channel read

Done (V3.1.0 b14 IL):
- world-chunks.md 2: Chunk.GetDamage (IL=8) chnDamage int read.

## 2026-08-08 - tier-C: voxel-read core

Done (V3.1.0 b14 IL):
- world-chunks.md 2: Chunk.GetBlock (IL=100) POI-filler + damage overlay;
  GetBlockNoDamage (IL=73); GetBlockId (IL=17); GetBlockColumn (IL=101).

## 2026-08-08 - tier-C: face-extract reads

Done (V3.1.0 b14 IL):
- world-chunks.md 2: Chunk.GetBlockFaceTexture (IL=19) 8-bit extract; prefab
  variant (IL=29) 6-bit slots.

## 2026-08-08 - tier-C: biome lookup surfaces

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: GetBiome Color32-pack (IL=34) / byte id (IL=5) / name
  (IL=12) / TryGetBiome (IL=11).

## 2026-08-08 - tier-C: poi-map add

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: WorldBiomes.AddPoiMapElement (IL=13) color-keyed
  add, duplicate skip.

## 2026-08-08 - tier-C: heightmap accessors

Done (V3.1.0 b14 IL):
- terrain-height.md: GetHeight (IL=9/5) m_HeightMap, GetTerrainHeight
  (IL=9) m_TerrainHeight + PrefabChunk scans, SetTerrainHeight (IL=10).

## 2026-08-08 - tier-C: sky body

Done (V3.1.0 b14 IL):
- light-mesh-water.md 1: Chunk.IsOpenSkyAbove (IL=9) y >= GetHeight.

## 2026-08-08 - tier-C: poi color lookup

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: WorldBiomes.getPoiForColor (IL=10) m_PoiMap
  TryGetValue.

## 2026-08-08 - tier-C: water-grid probe

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: World.GetWaterAt (IL=53) poiFromImage grid + poi
  color -> block type 240.

## 2026-08-08 - tier-C: Chunk.GetWater

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: Chunk.GetWater (IL=8) FromRawData channel read;
  PrefabChunk prefab route.

## 2026-08-08 - tier-C: Chunk.SetWater

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: Chunk.SetWater (IL=13) = SetWaterRaw +
  WakeNeighbours; ResetWaterSimHandle (IL=4).

## 2026-08-08 - tier-C: face-slot texture write

Done (V3.1.0 b14 IL):
- world-chunks.md 2: Chunk.SetBlockFaceTexture (IL=48) clear-or-insert face
  byte + isModified.

## 2026-08-08 - tier-C: SetWaterRaw

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: Chunk.SetWaterRaw (IL=55) flow gate, channel write,
  dirty flags, sim mirror, heightmap raise.

## 2026-08-08 - tier-C: Chunk.SetDensity

Done (V3.1.0 b14 IL):
- world-chunks.md 2: Chunk.SetDensity (IL=10) chnDensity.Set ulong write,
  PrefabChunk no-op.

## 2026-08-08 - tier-C: texture read

Done (V3.1.0 b14 IL):
- world-chunks.md 2: GetTextureFullArray (IL=22 pos / IL=17 bvRef) Default
  fallbacks + throw.

## 2026-08-08 - tier-C: painted-texture write

Done (V3.1.0 b14 IL):
- world-chunks.md 2: ChunkCluster.SetBlockFaceTexture (IL=61) chunk write +
  regen flag.

## 2026-08-08 - tier-C: block-data store

Done (V3.1.0 b14 IL):
- world-chunks.md 2: AddBlockData (IL=6) / ClearBlockData (IL=6) complete the
  per-position dict pair.

## 2026-08-08 - tier-C: SetMetadata core

Done (V3.1.0 b14 IL):
- items.md 2: SetMetadata (IL=86) lazy dict, SetValue update with type-mismatch
  warning + stack, TryCreate/Add new keys.

## 2026-08-08 - tier-C: held-item leaves

Done (V3.1.0 b14 IL):
- items.md 6: DecHoldingItem (IL=45) consume + flashlight-off/clear/update/
  notify; GetBestQuickSwapSlot (IL=50) remembered-then-scan.

## 2026-08-08 - tier-C: switch entries

Done (V3.1.0 b14 IL):
- items.md 6: SetHoldingItemIdx / NoHolsterTime (IL=5) setHeldItemByIndex
  bool flag.

## 2026-08-08 - tier-C: updateHoldingItem

Done (V3.1.0 b14 IL):
- items.md 6: updateHoldingItem (IL=172) OnHoldingReset re-arm vs
  StopHolding/StartHolding switch with MinEventContext teardown.

## 2026-08-08 - tier-C: notifyListeners

Done (V3.1.0 b14 IL):
- items.md 6: notifyListeners (IL=24) onInventoryChanged hook + listener
  hash-set fan-out.

## 2026-08-08 - tier-C: Inventory.SetItem core

Done (V3.1.0 b14 IL):
- items.md 6: SetItem (IL=166) held-redraw, class-change rebuild
  (createHeldItem/createInventoryData), preferred-slot bookkeeping, clone
  store, updateHoldingItem + notify.

## 2026-08-08 - tier-C: clearSlotByIndex

Done (V3.1.0 b14 IL):
- items.md 6: clearSlotByIndex (IL=41) Empty-store + model teardown
  (HoldingItemHasChanged, unparent, destroy, null).

## 2026-08-08 - tier-C: stat cleanup

Done (V3.1.0 b14 IL):
- items.md 2: HasStats (IL=5), ClearStats (IL=4), RemoveUnusedStats (IL=77)
  zero-drop compaction.

## 2026-08-08 - tier-C: World.IsWater

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: IsWater(x,y,z) (IL=31) chunk-local gate with y>=256
  / missing-chunk false; Vector3i/Vector3 overload forwards.

## 2026-08-08 - tier-C: pre-installed mod roll

Done (V3.1.0 b14 IL):
- items.md 2: createDefaultModItems (IL=187) descending-chance install,
  Modifications None-fill, cosmetic fallback via GetCosmeticItemMod.

## 2026-08-08 - tier-C: ItemValue mod queries

Done (V3.1.0 b14 IL):
- items.md 2: get_HasModSlots (IL=6) capacity; HasMods / HasCosmetics (IL=30)
  occupancy scans.

## 2026-08-08 - tier-C: mod clones

Done (V3.1.0 b14 IL):
- items.md 2: CloneModsTo / CloneCosmeticModsTo (IL=34 each) array copy with
  per-entry Clone.

## 2026-08-08 - tier-C: ItemValue metadata store

Done (V3.1.0 b14 IL):
- items.md 2: HasMetadata (IL=25), typed TryGetMetadata overloads (IL=17) +
  object core (IL=36), GetMetadata (IL=17, boxed-false quirk), RemoveMetaData
  (IL=12).

## 2026-08-08 - tier-C: durability-modifier accessors

Done (V3.1.0 b14 IL):
- items.md 7: get_MaxDurabilityModifier (IL=9) meta-or-1; setter (IL=13)
  remove-at-1 else SetMetadata.

## 2026-08-08 - tier-C: ModMaxUseTimes

Done (V3.1.0 b14 IL):
- items.md 7: ModMaxUseTimes (IL=24) DurabilityModifier meta scaling, min 1,
  no-op on <= 0 base.

## 2026-08-08 - tier-C: MaxUseTimes chain

Done (V3.1.0 b14 IL):
- items.md 7: get_MaxUseTimesBase (IL=25) DegradationMax passive;
  get_MaxUseTimes (IL=5) ModMaxUseTimes(base); get_MaxUseTimesUI (IL=3) base
  only.

## 2026-08-08 - tier-C: holding dispatch reads

Done (V3.1.0 b14 IL):
- items.md 4.1: GetHoldingPrimary (IL=6) Actions[0] / GetHoldingSecondary
  (IL=6) Actions[1] confirm the slot convention.

## 2026-08-08 - tier-C: Chunk.GetMaxHeight

Done (V3.1.0 b14 IL):
- terrain-height.md: Chunk.GetMaxHeight (IL=29) max of m_HeightMap bytes.

## 2026-08-08 - tier-C: ItemValue classification

Done (V3.1.0 b14 IL):
- items.md 1: get_ItemClassOrMissing (IL=9), get_HasQuality (IL=17),
  get_IsMod (IL=12), get_IsShapeHelperBlock (IL=12).

## 2026-08-08 - tier-C: GameStats accessors

Done (V3.1.0 b14 IL):
- sandbox-options.md 6.1: typed getters (GetInt/Float/Bool IL=34, GetString
  IL=18) with cast-failure fallbacks; client sandbox-reference read path.

## 2026-08-08 - tier-C: water leaves

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: HasMass (IL=5) mass > 195; GetVoxelKey2D (IL=8)
  hash; IsVoxelOutsideChunk (IL=15); IsChunkSafeToUpdate (IL=16) flags gate.

## 2026-08-08 - tier-C: biome-id accessors

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: Chunk.GetBiomeId (IL=9) / SetBiomeId (IL=10)
  m_Biomes[x + z*16] byte.

## 2026-08-08 - tier-C: cluster water accessors

Done (V3.1.0 b14 IL):
- light-mesh-water.md 4.2: ChunkCluster.GetWater (IL=23) Empty fallbacks;
  SetWater (IL=34) chunk write + regen flag.

## 2026-08-08 - tier-C: biome oracle query

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: World.GetBiomeInWorld (IL=23) GetBiomeAt, null without
  cache/provider.

## 2026-08-08 - tier-C: slot action lookups

Done (V3.1.0 b14 IL):
- items.md 4.1: GetItemActionInSlot (IL=32) / GetItemActionDataInSlot (IL=18)
  held-vs-slot split over Actions / actionData.

## 2026-08-08 - tier-C: ItemValue id accessors

Done (V3.1.0 b14 IL):
- items.md 2: GetItemOrBlockId (IL=12) split at ItemsStartHere; GetItemId
  (IL=5) item-space subtraction.

## 2026-08-08 - tier-C: Inventory.DecItem

Done (V3.1.0 b14 IL):
- items.md 6: DecItem (IL=132) type scan, ignoreModdedItems skip, stackable
  min-take + removedItems record, non-stackable whole-slot, returns removed.

## 2026-08-08 - tier-C: World height queries

Done (V3.1.0 b14 IL):
- terrain-height.md: GetHeightAt (IL=22) generator oracle; GetTerrainHeight
  (IL=21) chunk byte heightmap.

## 2026-08-08 - tier-C: trader-area queries

Done (V3.1.0 b14 IL):
- loot-economy.md 4: get_TraderAreas (IL=12) / GetTraderAreaAt (IL=14);
  IsWithinTraderPlacingProtection (IL=20 pos / IL=29 bounds+4) with
  SandboxUseTraderArea gate.

## 2026-08-08 - tier-C: trigger registry

Done (V3.1.0 b14 IL):
- entity-ai.md trigger section: AddTriggerVolume (IL=49) next-id + VolumeKey
  TryAdd, duplicate -1; GetTriggerVolume (IL=30) throw-on-miss;
  FindTriggerVolume (IL=29) VolumeKey map or -1.

## 2026-08-08 - tier-C: sleeper registry

Done (V3.1.0 b14 IL):
- entity-ai.md sleeper section: World.GetSleeperVolume (IL=30) locked
  TryGetValue with throw-on-miss; GetAllSleeperVolumes (IL=43) tuple copy.

## 2026-08-08 - tier-C: gun spread

Done (V3.1.0 b14 IL):
- items.md 4.2: getDirectionRandomOffset (IL=86) SpreadDegreesHorizontal (32)
  / Vertical (31) passives, accuracy-scaled uniform cone + Euler rotate.

## 2026-08-08 - tier-C: Prefab leaf queries

Done (V3.1.0 b14 IL):
- spawning.md 8: IsPosInSleeperVolume (IL=47) strict AABB + Used gate;
  FindSleeperVolumeFreeGroupId (IL=31) max+1; HasAnyQuestTag (IL=5);
  IsAllowedZone (IL=5) case-insensitive.

## 2026-08-08 - tier-C: density setters

Done (V3.1.0 b14 IL):
- world-chunks.md 5: ChunkCluster.SetDensity (IL=14) full SetBlock path vs
  SetDensityRaw (IL=27) silent Chunk.SetDensity.

## 2026-08-08 - tier-C: delayed-regen batch

Done (V3.1.0 b14 IL):
- world-chunks.md 5.1: ChunkPosNeedsRegeneration_DelayedStop (IL=48) count
  down + NeedsRegenerationOrBits apply + clear; start/stop nesting defer.

## 2026-08-08 - tier-C: ItemActionEat leaves

Done (V3.1.0 b14 IL):
- items.md 4.2: NeedPrompt (IL=13) UsePrompt gate; IsValidConditions (IL=94)
  ConditionBlockTypes ray gate + water sentinel 240; PercentDone (IL=24)
  animation-delay fraction.

## 2026-08-08 - tier-C: underground spawn finder

Done (V3.1.0 b14 IL):
- spawning.md 6: FindRandomSpawnPointNearPositionUnderground (IL=135) 5-try
  random xz within maxDistance/2, exact-y CanMobsSpawnAtPos or
  FindSpawnPointAtXZ fallback, playfield gate.

## 2026-08-08 - tier-C: ranged reload

Done (V3.1.0 b14 IL):
- items.md 4.2: ConsumeAmmo (IL=9) Meta -= 1; loadNewAmmunition (IL=20)
  ammo-type index reset + isChangingAmmoType latch.

## 2026-08-08 - tier-C: IsEmptyPosition

Done (V3.1.0 b14 IL):
- server-lifecycle.md 3.1: World.IsEmptyPosition (IL=117) trader-protection
  reject, non-survival pass, LandClaimSize-neighborhood lpblock scan.

## 2026-08-08 - tier-C: density compaction

Done (V3.1.0 b14 IL):
- world-chunks.md 2: CheckSameDensity (IL=4) + HasSameDensityValue (IL=5)
  chnDensity layer compaction probes (PrefabChunk stub).

## 2026-08-08 - tier-C: decoration gate

Done (V3.1.0 b14 IL):
- light-mesh-water.md 1: IsNeighbourChunksDecorated (IL=26) NeedsDecoration
  twin of the lit gate; CheckSameLight (IL=4) CheckSameValue compaction.

## 2026-08-08 - tier-C: texture word + neighbour-lit

Done (V3.1.0 b14 IL):
- world-chunks.md 2: 64-bit texture word = eight 8-bit face indexes
  (Value64FullToIndex shift, TextureIdxToTextureFullValue64 replicate).
- light-mesh-water.md 1: IsNeighbourChunksLit (IL=26) NeedsLightCalculation
  gate.

## 2026-08-08 - tier-C: neighbour-lit gate

Done (V3.1.0 b14 IL):
- light-mesh-water.md 1: Chunk.IsNeighbourChunksLit (IL=26) all non-null
  neighbours cleared NeedsLightCalculation, null fails.

## 2026-08-08 - tier-C: legacy item readers

Done (V3.1.0 b14 IL):
- items.md 2: ItemValue.ReadOld (IL=1) empty; ItemStack.ReadOld (IL=10) no-op
  + i16 count.

## 2026-08-08 - tier-C: World availability/water queries

Done (V3.1.0 b14 IL):
- world-chunks.md 4.0b: IsPositionAvailable (IL=43) 3x3 chunk neighborhood
  GetAvailable gate.
- light-mesh-water.md 4.2: GetWaterPercent (IL=14) GetMassPercent, 0 on null
  cache.

## 2026-08-08 - tier-C: ItemValue stat leaves

Done (V3.1.0 b14 IL):
- items.md 2: GetStatPercent (IL=12) 1 base; StatModifyValue (IL=47) stat
  point = 0.5% multiplier; IsStatLowerBetter (IL=9) StaminaLoss/TargetArmor;
  HasAnyBoostedStats (IL=26).

## 2026-08-08 - tier-C: biome-intensity storage

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: Chunk.GetBiomeIntensity (IL=16) 6-bytes-per-column
  offset (x+z*16)*6, Default fallback; ResetBiomeIntensity (IL=19) 6-byte
  write; CalcDominantBiome (IL=55) 256-byte histogram argmax.

## 2026-08-08 - tier-C: thrown weapon

Done (V3.1.0 b14 IL):
- items.md 4.2: instantiateProjectile (IL=122) model clone +
  ThrownWeaponMoveScript binding + MinEventContext + event 82;
  throwAway (IL=96) StaminaLoss (112) * StaminaUsageMultiplier cost, Fire,
  DecHoldingItem(1).

## 2026-08-08 - tier-C: MakeMotionMoveToward

Done (V3.1.0 b14 IL):
- entity-ai.md: MakeMotionMoveToward (IL=69) root-motion scale into
  [minMotion, maxMotion] band vs moveDirection + isMoveDirAbsolute.

## 2026-08-08 - tier-C: wandering-horde leaves

Done (V3.1.0 b14 IL):
- aidirector.md: get_OtherHordesAreActive (IL=9) blood-moon / chunk-event
  spawns gate; SetNextTime (IL=13) Bandits->BanditNextTime, Horde->HordeNextTime.

## 2026-08-08 - tier-C: EntityAlive yaw step

Done (V3.1.0 b14 IL):
- entity-ai.md: UpdateRotation (IL=36) shortest-arc wrap into (-180,180],
  clamp to +-maxIncr, cur + delta.

## 2026-08-08 - tier-C: falling-block batch/cancel

Done (V3.1.0 b14 IL):
- stability.md: AddFallingBlocks (IL=18) fan-out; ClearFallingBlocksForChunks
  (IL=111) queue drain, chunk-set drops + resetTempPositions rebuild.

## 2026-08-08 - tier-C: decorator POI queries

Done (V3.1.0 b14 IL):
- spawning.md 8: chooseClosestPrefab (IL=35) shrinking-bound nearest pick;
  IsEntityInPrefab (IL=40) listsLock + Contains across allPrefabs.

## 2026-08-08 - tier-C: EntityItem stick

Done (V3.1.0 b14 IL):
- loot-economy.md 6b: CheckStick (IL=93) stickPercent damp, stickT record +
  layer-0 colliders + SoundStick; get_IsDistractionActive (IL=5);
  PhysicsMasterBecome (IL=6) gravity recheck.

## 2026-08-08 - tier-C: SleeperVolume accessors

Done (V3.1.0 b14 IL):
- entity-ai.md sleeper section: SetMinMax (IL=19) BoxMin/Max + Center half-sum;
  GetPlayerTouchedToUpdateId/TriggerId (IL=13) entity id or -1; GetSpawnPoints
  (IL=3); SetScript (IL=15) MinScript null-or-set.

## 2026-08-08 - tier-C: enemy intent-to-attack

Done (V3.1.0 b14 IL):
- aidirector.md: EntityEnemy.OnEntityTargeted (IL=21) fires
  NotifyIntentToAttack for non-remote, non-Dynamic-spawned enemies targeting a
  player; IsDrawMapIcon (IL=2) true; GetMapIconScale (IL=5) (0.75, 0.75, 1).

## 2026-08-08 - tier-C: EntityAnimal distress

Done (V3.1.0 b14 IL):
- entity-ai.md: SetDistressed (IL=16) flags + bounds + playerId + timer 2.5;
  getEntityPlayerLocal (IL=16) primary-player id gate; isGameMessageOnDeath
  (IL=2) false.

## 2026-08-08 - tier-C: PrefabInstance leaves

Done (V3.1.0 b14 IL):
- spawning.md 8: GetCenterXZ (IL=24) bbox center Vector2; IsBBInSyncWithPrefab
  (IL=24) lastCopied pos/size/rotation match gate.

## 2026-08-08 - tier-C: Bag leaves

Done (V3.1.0 b14 IL):
- items.md: TryStackItem (IL=75) CanMoveTo gate + CanStackPartly merge scan
  (fullyPlaced, changed); ReadInto (IL=93) version/count/items/LockedSlots/
  Touched/preferences wire format; get_SlotCount (IL=10);
  onBackpackChanged (IL=8) null-guarded invoke.

## 2026-08-08 - tier-C: Equipment leaves

Done (V3.1.0 b14 IL):
- items.md 6: updateInsulation (IL=32) waterProof sum of equipped WaterProof;
  GetTotalInsulation/Waterproof (IL=3); DropItemOnGround (IL=21) ItemDropServer
  1-count 60s; GetArmorGroupLowestQuality (IL=13) group info; HasAnyItems
  (IL=22) slot scan.

## 2026-08-08 - tier-C: ItemAction base gates

Done (V3.1.0 b14 IL):
- items.md 3: CanRepair (IL=37) status codes 0/1/2 (no-degradation, modifier
  headroom thresholds); CanCancel (IL=2) false base; IsEndDelayed base false /
  ItemActionEat true; IsAimingGunPossible base true / Ranged NotReloading.

## 2026-08-08 - tier-C: AIDirector leaves

Done (V3.1.0 b14 IL):
- aidirector.md: GetActivityWorldTimeDelay (IL=16) clamp(TimeOfDayIncPerSec/6,
  0.2, 5)*1000; ComponentsInitNewGame (IL=20) per-component InitNewGame;
  NotifyIntentToAttack (IL=1) empty residual.

## 2026-08-08 - tier-C: GameEventManager flag store

Done (V3.1.0 b14 IL):
- game-events.md 7: SetGameEventFlag (IL=94) add/update-duration/remove +
  HandleFlagChanged(true, true/false); CheckGameEventFlag (IL=23) linear scan.

## 2026-08-08 - tier-C: AddDroppedId

Done (V3.1.0 b14 IL):
- loot-economy.md 6b: EntityClass.AddDroppedId (IL=33) lazy itemsToDrop[event]
  list + SItemDropProb row (name, min, max, prob, 1, stickChance,
  toolCategory, tag).

## 2026-08-08 - tier-C: Quest leaves

Done (V3.1.0 b14 IL):
- quests-challenges.md 2: SetupQuestCode (IL=48) hash of time_ID_owner_giver;
  SetupTags (IL=41) objective OwnerQuest/vars/tag + NeedsNPCSetPosition OR;
  get_HasPosition (IL=10); GetActionIndex/GetObjectiveIndex (IL=23); 
  get_IsShareable (IL=18) gates.

## 2026-08-08 - tier-C: GameUtils classification leaves

Done (V3.1.0 b14 IL):
- raycast-pathing.md: IsBlockOrTerrain (IL=22) tag set; GetDirByNormal
  (IL=11/22) NeighborsEightWay index; GetClosestDirection (IL=74) 90-limited
  4-way / full 8-way quantization.
- tile-entities-power.md 1: UInt64ToVector3i (IL=27) exact inverse of the
  16-bit pack.

## 2026-08-08 - tier-C: GameUtils time conversions

Done (V3.1.0 b14 IL):
- aidirector.md time gates: DaysToWorldTime (IL=15) (day-1)*24000;
  DaysToWorldTimeMidnight (IL=6) +16000; WorldTimeToTotalSeconds (IL=4) *3.6;
  WorldTimeToTotalMinutes (IL=7) *0.06; TotalMinutesToWorldTime (IL=7) /0.06;
  WorldTimeToHourMinutesString (IL=14) D2:D2.

## 2026-08-08 - tier-C: World sky/water queries

Done (V3.1.0 b14 IL):
- light-mesh-water.md 1: World.IsOpenSkyAbove (IL=23) chunk-local delegation
  (x>>4, z>>4 / x&15, z&15), null-cache true; World.IsWaterInBounds (IL=74)
  integer cell walk [floor(min), floor(max)+1) with IsWater probe.

## 2026-08-08 - tier-C: PPL registry leaves

Done (V3.1.0 b14 IL):
- server-lifecycle.md 3: GetEntityPlayerFromUserId (IL=18) PlayerToEntityMap +
  GetEntity; SetPlayerData (IL=43) Players/ m_lpBlockMap reindex + MapPlayer
  (UnmapPlayer on -1); SpawnPointRemoved (IL=28) ClearBedroll match;
  HandlePlayerDetailsUpdate (IL=14) PlayerName.Update.

## 2026-08-08 - tier-C: player breadcrumb + vicinity

Done (V3.1.0 b14 IL):
- server-lifecycle.md: GetBreadcrumbPos (IL=27) 32-slot ring index
  (breadcrumbIndex - round(distance)) & 31 (>=31: +1); SetPrefabsAroundNear
  (IL=26) prefabsAroundNear copy; GetLayerForMapIcon layers 19/20.

## 2026-08-08 - tier-C: cave sampler

Done (V3.1.0 b14 IL):
- spawning.md 6: Chunk.FindRandomCavePoint (IL=95) downward scan from surface
  up to relMinY (stop y<=2), accept CanMobsSpawnAtPos(false,true), world y+1.

## 2026-08-08 - tier-C: top-soil bitmap

Done (V3.1.0 b14 IL):
- world-chunks.md 5.1: Chunk m_bTopSoilBroken 32-byte bitmap (idx
  (x+z*16)/8, bit (x+z*16)%8); IsTopSoil (IL=31) bit-clear test,
  SetTopSoilBroken (IL=36) set; GetTopSoil (IL=3) / SetTopSoil (IL=21) /
  GetTopMostTerrainHeight (IL=28) max heightmap; PrefabChunk stubs.

## 2026-08-08 - tier-C: spawn column probe

Done (V3.1.0 b14 IL):
- spawning.md 6: Chunk.FindSpawnPointAtXZ (IL=54) downward scan from endY
  while y > startY, accept GetLightValue(x,y,z,darknessV) <= maxLightV and
  CanMobsSpawnAtPos(ignoreCanMobsSpawnOn, true), y+1 on success.

## 2026-08-08 - tier-C: top-soil sampler

Done (V3.1.0 b14 IL):
- spawning.md 6: Chunk.FindRandomTopSoilPoint (IL=80) numTrys retry loop,
  local RandomRange(15) xz, GetHeight y, reject y<2 and
  !CanMobsSpawnAtPos(x,y,z,false,true), world x+m_X*16 / y+1 / z+m_Z*16.

## 2026-08-08 - tier-C: world clamps + spawn sampler

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: ClampToValidWorldPos (IL=82) Navezgane/90-inset clamp
  all-axes; ClampToValidWorldPosForMap (IL=28) raw-extent-only contrast.
- spawning.md 6: World.GetRandomSpawnPointPositions (IL=74) chunk-array
  RandomRange(count)==1 gate + FindRandomTopSoilPoint(x,y,z,5) fill, zero
  remainder.

## 2026-08-08 - tier-C: WeatherManager leaves

Done (V3.1.0 b14 IL):
- weather-environment.md 4: SeaLevel (IL=2) constant 0;
  GetCurrentTemperatureValue (IL=2) GetTemperature forward;
  GetCurrentCloudThicknessPercent (IL=4) *0.01; EntityRemovedFromWorld (IL=1)
  empty; IsStorming (IL=15) biome stormState >= 2.

## 2026-08-08 - tier-C: ItemActionRanged ammo leaves

Done (V3.1.0 b14 IL):
- items.md 4.2: GetMaxAmmoCount (IL=25) MagazineSize passive vs
  BulletsPerMagazine; checkAmmo (IL=12) InfiniteAmmo || Meta>0; HasInfiniteAmmo
  (IL=24) passive 188; GetBurstCount (IL=23) passive 15; IsAmmoUsableUnderwater
  (IL=19) magazine item class flag; requestReload (IL=12) ItemReloadServer;
  isJammed (IL=5) scGunIsJammed metadata.

## 2026-08-08 - tier-C: VehicleManager save path

Done (V3.1.0 b14 IL):
- vehicles-drones-turrets.md 2: SaveAndClear (IL=15) flush + clear + null
  singleton; WaitOnSave (IL=11) 30ms thread join; SaveThread (IL=41)
  vehicles.dat.bak rotation + pooled stream write + byte log; GetServerVehicleCount
  (IL=13) active+unloaded vs replicated static.

## 2026-08-08 - tier-C: world bounds consumers

Done (V3.1.0 b14 IL):
- chunk-providers.md 1: World.IsPositionInBounds (IL=66) BoundsInt from
  GetWorldExtent, Navezgane fixed +-2900, non-playtesting 90-block inset;
  ClampToValidWorldPosForMap (IL=28) extent clamp; IsPositionWithinPOI (IL=15)
  decorator prefab probe.

## 2026-08-08 - tier-C: NavObjectManager leaves

Done (V3.1.0 b14 IL):
- map-objects.md 7: unregister overloads (ByEntityID IL=16 / ByOwnerEntity
  IL=18 / ByPosition IL=19) are closure predicates funneled through
  unRegisterNavObjects; GetNavObjectByEntityID (IL=34) backward scan, null when
  absent.

## 2026-08-08 - tier-C: Progression leaves

Done (V3.1.0 b14 IL):
- progression.md 2: GetDict (IL=4) + CalcId (IL=4) name-id registry;
  GetPerkList (IL=40) Perk/Book under parent skill; addProgressionCurrency
  (IL=85) Skill-type scale via passive 86 SkillExpGain, cost/level cycle with
  CalculatedCostForLevel carry-over, MaxLevel clamp; ToBytes/FromBytes (IL=28/
  31) pooled Write/Read wrappers; ClearProgressionClassLinks (IL=27).

## 2026-08-08 - tier-C: QuestJournal leaves

Done (V3.1.0 b14 IL):
- quests-challenges.md 9: AddQuestFactionPoint (IL=34) GlobalFactionPoints +
  QuestFactionPoints[id] += tier (tier-0 no-op); GetQuestFactionMax (IL=20)
  QuestsPerTier tier-sum; HasCraftingQuest (IL=29) craftingTag intersect;
  HasActiveQuestByQuestCode (IL=30) QuestState.InProgress; GetObjectiveForQuest
  (IL=43) phase + type match.

## 2026-08-08 - tier-C: ItemClass leaves

Done (V3.1.0 b14 IL):
- items.md 1: CreateItemValue (IL=17) ItemValue(id, quality, quality, false,
  null, 1f); GetForId (IL=15) list index; CanCollect base true vs
  ItemClassTimeBomb Meta!=0 refuse; HasAllTags per-subclass tag source;
  IsGun/IsDynamicMelee Actions[0] isinst; IsLightSource; held/dropped pose
  corrections ((90,0,0) block held, (-90,0,0) dropped non-block);
  GetLocalizedItemName field vs Block delegate.

## 2026-08-08 - tier-C: TEFeatureLockable gates

Done (V3.1.0 b14 IL):
- tile-entities-power.md 4.7: InitBlockActivationCommands (IL=37) lock/unlock/
  keypad commands; AllowBlockActivationCommand (IL=93) owner/ally gates per
  command; get_TriggerRole (IL=2) role 1; OnBlockTriggered (IL=10) unlocks on
  triggeredBy.Unlock.

## 2026-08-08 - tier-C: TEFeatureStorage migration

Done (V3.1.0 b14 IL):
- loot-economy.md TEFeatureStorage surface: migrateItemsFromOtherContainer
  (IL=94) clone-clamped items + overflow DroppedLootContainer drop at
  ToWorldCenterPos + y0.9 + slot-lock clone/resize; SetContainerSize (IL=48)
  rebuild-or-empty; HasItem (IL=26) type scan; UpdateSlot (IL=10) clone +
  NotifyListeners; GetContainerSize + LootStageMod/Bonus field reads.

## 2026-08-08 - tier-C: vending autobuy

Done (V3.1.0 b14 IL):
- loot-economy.md 6: TileEntityVendingMachine.SetAutoBuyTime (IL=21) nextAutoBuy
  +24000 ticks from worldTime (initial) or prior nextAutoBuy (renewal);
  get_IsRentable (IL=5) TraderInfo.Rentable; get_RentTimeRemaining (IL=9)
  rentalEndDay - WorldTimeToDays; get_RentalEndDay / GetUsers / GetPasswordHash
  (IL=3) field reads.

## 2026-08-08 - tier-C: TileEntity transfer family

Done (V3.1.0 b14 IL):
- tile-entities-power.md 1: ChangeBlocks TE handoff (oldTE.ReplacedBy(newBV,
  oldBV, newTE); air -> RemoveTileEntityAt; else newTE.UpgradeDowngradeFrom
  (oldTE)); base IL=3 _other.OnDestroy; TileEntityComposite IL=34 Owner +
  module fan-out; TileEntityCollector IL=73 worldTimeTouched + cloned Items;
  TileEntityVendingMachine IL=29 ILockable copy (locked/owner/users/password);
  UseLocalVersioning (IL=15) readVersion -1 gate / >= 18.

## 2026-08-08 - tier-C: ItemActionAttack modifiers

Done (V3.1.0 b14 IL):
- combat-damage.md leaf types: difficultyModifier (IL=44) PvE scalers
  IncomingDamageModifier / EntityIncomingDamageModifier only in mixed
  client/server matchups; calculateHarvestToolDamageBonus (IL=43) first
  toolCategory match -> Damage else 1; GetDamageMultiplier (IL=3),
  GetIdealAIRange (IL=3), base CanReload/ReloadGun/GetKickbackForce stubs,
  GetEntityFromHit (IL=6) GetHitRootEntity.

## 2026-08-08 - tier-C: drone heal/repair/ownership

Done (V3.1.0 b14 IL):
- vehicles-drones-turrets.md 5: TargetCanBeHealed (IL=14) healWeapon gate;
  GetNearestHealTargetInRange (IL=40) party scan sorted nearest; HealRequest
  (IL=50) no-item tooltip + userRequestedHeal -> healTargetServer; performRepair
  (IL=23) full heal + UseTimes 0 + SendSyncData(16); GetRepairAmountNeeded
  (IL=6) + RepairParts (IL=7); belongsToPlayerId (IL=5); isValidForPlayer
  (IL=14/23) one-drone-per-player gate; GetStoredItemCount (IL=4).

## 2026-08-08 - tier-C: turret leaves

Done (V3.1.0 b14 IL):
- vehicles-drones-turrets.md 6.1: EntityTurret get_AmmoCount/set_AmmoCount
  (IL=4/5) store ammo in OriginalItemValue.Meta (gun-magazine style); InitTurret
  (IL=8) FireController.Init(EntityClass.Properties, this); get_IsTurning
  (IL=15) IsOn && (yaw || pitch turning).

## 2026-08-08 - tier-C: vehicle ownership/password/fuel

Done (V3.1.0 b14 IL):
- vehicles-drones-turrets.md 4.2b: SetOwner/GetOwner (IL=5/4) OwnerId,
  SetLocked (IL=4), IsUserAllowed (IL=11); password chain HasPassword (IL=7),
  GetHashForPassword (IL=3) Utils.HashString, SetPasswordHash (IL=33) clears
  AllowedUsers + first-owner lock, CheckPasswordHash (IL=29) adds user +
  SendSyncData(2); fuel: GetFuelCount (IL=7) floor(level*25), needsFuel (IL=12),
  takeFuel (IL=67) inventory-then-bag DecItem, AddFuelFromInventory (IL=45)
  25-per-item refill.

## 2026-08-08 - tier-C: Inventory take/return leaves

Done (V3.1.0 b14 IL):
- items.md 6: TryTakeItem (IL=83) deposit scan (empty slot whole clone /
  CanStackPartly until consumed); CanTakeItem (IL=37) + CanStackNoEmpty (IL=24)
  affordance probes; ReturnItem (IL=36) via PreferredItemSlot; PreferredItemSlot
  (IL=23) preferredItemSlots scan; GetSlotWithItemValue (IL=25); UsingBareHand
  (IL=6) + GetBareHandItemValue (IL=3).

## 2026-08-08 - tier-C: GameStats + EntityTrader leaves

Done (V3.1.0 b14 IL):
- sandbox-options.md 6.1: GameStats.initDefault (IL=29) seeds
  propertyValues from PropertyDecl.defaultValue; GetStatType (IL=31) linear
  scan -> EnumType? null when unregistered.
- npc-dialog.md 5: EntityTrader.GetQuestFactionPoints (IL=4) =
  QuestJournal.GlobalFactionPoints; CanDamageEntity (IL=2) hard false;
  get_IsValidAimAssistSnapTarget (IL=2) hard false.

## 2026-08-08 - tier-C: safe-zone chunk lock

Done (V3.1.0 b14 IL):
- spawning.md 6.2: EntityPlayer.onSpawnStateChanged (IL=52) safe-zone lock on
  respawn reasons NewGame/Died/EnterMultiplayer (non-remote/non-editor +
  IsSafeZoneActive): LockAreaMasterChunksAround(worldTime +
  PlayerSafeZoneHours*1000); World.LockAreaMasterChunksAround (IL=71) 5x5
  area-master grid (dx,dz in [-2,2] * 80, ToAreaMasterChunkPos):
  DelayAllEnemySpawningUntil on loaded spawn-data chunks (isModified set) else
  areaMasterChunksToLock deferred map; lastRespawnReason normalized to
  Unknown(6) unless Teleport(3).

## 2026-08-08 - tier-C: WorldBiomes + EntityStats leaves

Done (V3.1.0 b14 IL):
- world-generation.md 3.1: WorldBiomes runtime registry (m_Color2BiomeMap /
  m_Id2BiomeArr), GetBiomeCount (IL=9) 0-before-load, GetBiomeMap (IL=3),
  GetTotalBluffsCount (IL=31) m_DecoBluffs sum.
- entity-stats.md 1: EntityStats.SimpleClone (IL=7) Health-only vs
  PlayerEntityStats.SimpleClone (IL=26) Health/Stamina/Water/Food/CoreTemp;
  ResetStats (IL=1) empty virtual.

## 2026-08-08 - tier-C: EntityBuffs cvar leaves

Done (V3.1.0 b14 IL):
- buffs.md: SetCustomVarNetwork (IL=33) NetPackageModifyCVar wire half (192
  broadcast / SendToServer); IncrementCustomVar (IL=8) add-op; HasCustomVar /
  CountCustomVars / EnumerateCustomVars; RemoveCustomVar (IL=21) + TrackCustomVar
  (IL=39) tracking logs; SetBuff (IL=17) AddBuff/RemoveBuff dispatcher;
  UnPauseAll (IL=19); ClearBuffClassLinks (IL=21).

## 2026-08-08 - tier-C: PPD leaves + quest notifiers

Done (V3.1.0 b14 IL):
- server-lifecycle.md 3.1: PersistentPlayerData get_OfflineHours/Minutes (IL=14
  each, -1 while in-world else since LastLogin), get_HasBedrollPos (IL=8,
  int.MaxValue y sentinel) + ClearBedroll (IL=37, nav object + map marker
  remove), AddLandProtectionBlock (IL=11), ProcessBackpacks (IL=21) +
  TryUpdateBackpackPosition (IL=19, keeps timestamp).
- quests-challenges.md 1: notifier pattern (BlockChanged/ItemAdded/
  HarvestedItem/OpenedContainer null-guarded invokes) + CheckResetQuestTrader
  (IL=24) ForceResetQuestTrader gate.

## 2026-08-08 - tier-C: ChunkCluster helpers

Done (V3.1.0 b14 IL):
- world-chunks.md 2: ChunkCluster ToWorldPosition (IL=5) / ToLocalPosition
  (IL=29) / ToLocalVector (IL=2) / ToLocalKey (IL=24) coordinate rebasing;
  IsOnBorder (IL=32) fixed-size edge test.
- world-chunks.md 5.0: notifyBlocksOfNeighborChange (IL=23) fans all 6
  AllDirections offsets; notifyBlockOfNeighborChange (IL=24) skips remote,
  calls Block.OnNeighborBlockChange for non-air neighbors.

## 2026-08-08 - tier-C: party leaves + player visibility

Done (V3.1.0 b14 IL):
- parties-factions.md 2: EntityPlayer.IsPartyLead (IL=11) Party.Leader == this;
  GetTeamColor (IL=5) Constants.cTeamColors[TeamNumber].
- server-lifecycle.md: EntityPlayer.VisiblityCheck (IL=48) 5-tick throttle,
  FastMin(12, GetViewDistance())*16-1 maxDist, bModelVisible = distSqr < maxDist^2,
  SetVisible when alive.

## 2026-08-08 - tier-C: prop-change wire + water RPC

Done (V3.1.0 b14 IL):
- world-chunks.md 5.1: GameManager.ChangeProps (IL=121) lock + per-PropChangeInfo
  SetProp nullable tuple, delayed regen start/stop; SetPropsRPC (IL=29) +
  SetPropsOnClients (IL=13) NetPackageSetProp fan-out channel 192.
- light-mesh-water.md: GameManager.SetWaterRPC (IL=41) ApplyChanges +
  SetSenderId + rebroadcast 192 / SendToServer.

## 2026-08-08 - tier-C: ItemValue.MergeBest

Done (V3.1.0 b14 IL):
- items.md 2: ItemValue.MergeBest (IL=115) donor merge: CombineOnly/Both sums
  remaining durability vs larger MaxUseTimes; plain-repair mode adopts donor
  only when strictly better (quality/durability), copying Quality,
  MaxDurabilityModifier and donor UseTimes; then MergeBestStats, clone mods +
  cosmetics, resize Modifications to CalcModSlotCount.
- MergeBestStats (IL=109): null donor no-op; missing own array copies donor;
  else per-stat better-value upgrade (IsStatLowerBetter) or append.

## 2026-08-08 - tier-C: time hooks + biome oracle

Done (V3.1.0 b14 IL):
- aidirector.md time gates: World.DuskDawnInit (IL=13) writes DuskHour/DawnHour
  from GameStats DayLightLength via CalcDuskDawnHours; World.SetTimeJump (IL=14)
  SetTime + SkyManager.bUpdateSunMoonNow + server
  AIDirectorBloodMoonComponent.TimeChanged(isSeek).
- chunk-providers.md 1: World.IsPositionRadiated (IL=24) GetRadiationAt > 0;
  World.GetBiomeIntensity (IL=28) chunk.GetBiomeIntensity with
  NeedsLightCalculation gate, BiomeIntensity.Default fallback.

## 2026-08-08 - tier-C: loot group roll + bag unlock

Done (V3.1.0 b14 IL):
- loot-economy.md 8.4: LootContainer.SpawnItemsFromGroup (IL=84) outer group
  roll (loop numToSpawn times while slotsLeft > 0; count via RandomSpawnCount
  or RandomCountFromSandbox with sandboxApplied feedback; OR of pass results);
  GetRewardItem (IL=45) quest-reward single-spawn probe returning first stack
  or ItemStack.Empty.
- loot-economy.md 6b: EntityLootContainer.OnUnlockedServer (IL=7) kills the
  container when the bag IsEmpty on unlock.

## 2026-08-08 - tier-C: ItemStack/ItemValue leaves

Done (V3.1.0 b14 IL):
- items.md 2: ItemStack.ReadDelta (IL=15) / WriteDelta (IL=23) delta wire pair
  (full ItemValue body + i16 count delta, last.count synced on write);
  ItemValue.ReadOrNull (IL=13) marker-first null sentinel.
- items.md 2: StackTransferCount (IL=21) partial transfer count;
  EqualsForMerging (IL=47) merge gate (RepairType CombineOnly/Both, same
  durability extreme, equal Stats); CalcModSlotCount (IL=29) ModSlots passive
  from Quality-1 clamped 255.
- items.md 7: AdjustForSandboxOptions (ItemValue IL=7 / ItemStack IL=8)
  strips DurabilityModifier meta when perma-degradation off (DegradeOnDeathType
  MaxDurability/Both or ItemMaxDegrationAmount > 0).

## 2026-08-08 - tier-C: dismount recall + fall rescue

Done (V3.1.0 b14 IL):
- EntityPlayer.FindValidExitPosition (IL=14) + GetFallingSavePosition (IL=161)
  in entity-ai.md D4: dismount bookkeeping (lastVehiclePositionOnDismount,
  timeOfVehicleDismount, forcedDetach); recall window returns dismount position
  while Time.time - timeOfVehicleDismount < vehicleTeleportThresholdSeconds and
  not forcedDetach; fell-through-world path logs [FELLTHROUGHWORLD], picks the
  closest non-empty chunk from ChunkObserver.chunksAround (center +8 probe,
  min sqrMagnitude), clamps x/z into [origin+0.5, origin+16-1], y =
  GetTerrainHeight + 0.5.

## 2026-08-08 - tier-C: velocity-per-second + CanHeal

Done (V3.1.0 b14 IL):
- Entity.GetVelocityPerSecond (IL=21) / EntityPlayer.GetVelocityPerSecond
  (IL=13) in entity-ai.md D4: attached delegate, physicsRB.velocity, else
  motion * 20 (20 TPS scale); player override uses averageVel * 20.
- EntityPlayer.CanHeal (IL=12) in combat-damage.md leaf types: gate
  Health > 0 && Health < GetMaxHealth().

## 2026-08-08 - tier-C: range-checked damage + safe zone

Done (V3.1.0 b14 IL):
- EntityPlayer.ServerNetSendRangeCheckedDamage (IL=27) narrated in
  combat-damage.md 2.2: builds NetPackageRangeCheckDamageEntity (Setup with
  origin/maxRange/source/strength/critical/buffActions/context/particleEffect)
  and SendPackage excluding the victim on channel 192.
- EntityPlayer.IsSafeZoneActive (IL=14) narrated in spawning.md 6.2: active iff
  Level <= GamePrefs.PlayerSafeZoneLevel and spawnPoints.Count == 0.

## 2026-08-08 - tier-C: game stage family

Done (V3.1.0 b14 IL):
- EntityPlayer game-stage family completed in progression.md 5:
  get_unModifiedGameStage (IL=45) = Floor(GetValue(passive 157, (Level +
  daysLived) * GameStageDefinition.DifficultyBonus)) with no biome/quest terms,
  no GlobalGameStageModifier and no min-1 clamp; GetTraderStage(tier) (IL=46) =
  FastMax(1, Floor(GetValue(passive 158, Level * (1 + TraderManager.QuestTierMod[
  clamp(tier-1)])) * GlobalTraderStageModifier)); get_HighestPartyGameStage
  (IL=10) = Party.get_HighestGameStage (IL=26), max over MemberList of member
  get_gameStage (0 for empty party), else own get_gameStage.

## 2026-08-08 - tier-C: BlockPlaceholderMap.Replace

Done (V3.1.0 b14 IL):
- BlockPlaceholderMap.Replace 9-arg core (IL=292) narrated in blocks.md 5:
  registry miss returns unchanged; questResetPlaceholders alternate list picks
  first QuestTag.Test_AnySet match; biome (case-insensitive) + sandboxOption
  boolean-gate filtering; survivors in stack Span, weighted draw on Prob;
  rotation = Has45DegreeRotations ? RandomRange(8) with >3 mapped +20 :
  RandomRange(4), else keep; equals-input collapses to BlockValue.Air sentinel;
  ischild/parent restored. No GameRandom -> Utils.RandomFromSeedOnPos at chunk
  origin + block coords (+parent offset) with World.Seed, freed on exit. Also
  the 5-arg wrapper (GetChunkFromWorldPos, blockY 0, rotation allowed), the
  BlockValueRef overload (None/Prop -> air, Block -> replace at BlockPosition,
  else ArgumentOutOfRangeException), and the IsReplaceableBlockType probe.

## 2026-08-08 - tier-C: BlockHazard state bit

Done (V3.1.0 b14 IL):
- BlockHazard.IsHazardOn (IL=29, multiblock child->parent recursion) and
  SetHazardState (IL=15) use the same meta bit 1 as BlockLight - the
  trigger/light/hazard states share the low meta bits. block-shapes.md 7.3.

## 2026-08-08 - tier-C: BlockLight state bits

Done (V3.1.0 b14 IL):
- BlockLight.IsLightOn (IL=7) = (meta & 2) != 0; SetLightState (IL=15) =
  (meta & ~3) | (isOn ? 2 : 0) - the light-on flag in meta bit 1, sharing
  low bits with the trigger state. light-mesh-water.md.

## 2026-08-08 - tier-C: per-block OnTriggered family

Done (V3.1.0 b14 IL):
- block-shapes.md 7.3: Block.OnTriggered variants - ActivateSwitch (IL=24)
  meta toggle, GameEvent (IL=60) target-type Block gate + HandleAction +
  destroyOnEvent damage, Hazard (IL=49) toggle + sounds, Light (IL=26)
  SetLightState toggle, TrapDoor (IL=26) self-destroy, Downgrade (IL=15),
  CompositeTileEntity (IL=53); each mutating variant appends BlockChangeInfo.

## 2026-08-08 - tier-C: BlockTrigger.CheckIsTriggered

Done (V3.1.0 b14 IL):
- BlockTrigger.CheckIsTriggered (IL=59) narrated in block-shapes.md: OR
  mode any TriggeredByIndices channel in TriggeredValues; AND mode all
  channels required. Trigger combination logic complete.

## 2026-08-08 - tier-C: BlockTrigger.OnTriggered

Done (V3.1.0 b14 IL):
- block-shapes.md 7.3: BlockTrigger.OnTriggered (IL=27) - latch channel,
  CheckIsTriggered OR/AND combination gate, chunk.GetBlock + Block.OnTriggered
  callback, TriggeredValues clear; BlockTriggerDowngrade (IL=15) adds
  HandleDowngrade. Trigger system listener path complete.

## 2026-08-08 - tier-C: PrefabTriggerData.Trigger fan-out

Done (V3.1.0 b14 IL):
- block-shapes.md 7.3: PrefabTriggerData.Trigger overloads (IL=63/85/90)
  - per fired channel, TriggeredByDictionary listeners OnTriggered + sleeper
  volumes OnTriggered (player gate), UpdateBlocks when changes non-empty;
  needs-trigger update list with 3 s timer (HandleNeedTriggers IL=33),
  Refresh/RefreshForQuest/Reset (IL=22), AddTriggeredBy (IL=34) channel
  indexing of sleeper volumes.

## 2026-08-08 - tier-C: BlockTrigger.HasAnyTriggers

Done (V3.1.0 b14 IL):
- BlockTrigger.HasAnyTriggers (IL=6) = TriggersIndices.Count > 0 - the
  TriggerBlocks gate. block-shapes.md.

## 2026-08-08 - tier-C: Block.HandleTrigger

Done (V3.1.0 b14 IL):
- Block.HandleTrigger (IL=41) narrated in block-shapes.md 7.3: client
  sends NetPackageBlockTrigger, server resolves the chunk's BlockTrigger
  and calls TriggerBlocks(player, player.prefab, trigger) when valid.

## 2026-08-08 - tier-C: TriggerManager.TriggerBlocks

Done (V3.1.0 b14 IL):
- block-shapes.md 7.3: TriggerManager.TriggerBlocks block overload (IL=17)
  HasAnyTriggers gate + PrefabDataDict[instance].Trigger; TriggerVolume
  overload (IL=27) same gate + null-instance 'Cannot do TriggerBlocks...'
  warning.

## 2026-08-08 - tier-C: BlockTrigger registry accessors

Done (V3.1.0 b14 IL):
- block-shapes.md 7.1: Chunk.AddBlockTrigger (IL=10) triggerData.Set +
  isModified; GetBlockTriggers (IL=3) field read; GetBlockTrigger (IL=9)
  dict TryGetValue (null when absent).

## 2026-08-08 - tier-C: Vector3iToUInt64

Done (V3.1.0 b14 IL):
- GameUtils.Vector3iToUInt64 (IL=29) narrated in tile-entities-power.md:
  each axis (coord+32768) & 0xFFFF, x<<32|y<<16|z - the position key pack
  also used on the chunk-provider wire packedPos.

## 2026-08-08 - tier-C: Chunk.GetBlockEntity

Done (V3.1.0 b14 IL):
- tile-entities-power.md: Chunk.GetBlockEntity Vector3i (IL=10) = dict
  keyed Vector3iToUInt64; Transform (IL=30) = linear scan; PrefabChunk
  null stubs; ChunkCluster (IL=12) resolve + delegate.

## 2026-08-08 - tier-C: Entity.FindAttachSlot

Done (V3.1.0 b14 IL):
- Entity.FindAttachSlot (IL=27) narrated in vehicles-drones-turrets.md:
  walks attachedEntities[] for the matching index, -1 when absent - the
  IsAttached primitive.

## 2026-08-08 - tier-C: Entity.IsAttached

Done (V3.1.0 b14 IL):
- Entity.IsAttached (IL=8) = FindAttachSlot(entity) >= 0;
  EntityDrone.IsAttachedToVehicle (IL=11) = AttachedToEntity is
  EntityVehicle. vehicles-drones-turrets.md 4.2.

## 2026-08-08 - tier-C: seat slot definition

Done (V3.1.0 b14 IL):
- EntityVehicle.GetAttachedToInfo (IL=158) narrated in
  vehicles-drones-turrets.md 4.2: slot defaults (visible + inventory
  replace, pitch/yaw restrictions, enter pose (0,0,-0.201)), seat<idx>
  DynamicProperties position/rotation overrides, exit list split on '~'
  with TransformDirection + y+0.02 + yaw math, fallback -2*right exit.

## 2026-08-08 - tier-C: generic attach pipeline

Done (V3.1.0 b14 IL):
- vehicles-drones-turrets.md 4.2: StartAttachToEntity (IL=43) client
  package + server broadcast; Entity.AttachToEntity (IL=64) pose parent +
  model hide for remote; EntityAlive (IL=60) Idle tag + inventory swap via
  bReplaceLocalInventory; EntityPlayer (IL=21) model pos stash; PlayerLocal
  (IL=88) camera + Driving + waypoints + RunLoop sound; EntityVehicle (IL=2)
  always -1. Repaired the AttachEntityToSelf continuation splice.

## 2026-08-08 - tier-C: Voxel.Raycast wrappers

Done (V3.1.0 b14 IL):
- raycast-pathing.md: Voxel.Raycast wrappers - 5-arg fills layer mask
  -538488845; bool overload hitMask = 66 | (transparent?1:0) |
  (nonCollidable?4:0); 6-arg forwards to raycastNew (IL=525); visibility
  chain calls the 6-arg with -1612492829 + 64.

## 2026-08-08 - tier-C: EntityDrone.FindCollisionEntity

Done (V3.1.0 b14 IL):
- EntityDrone.FindCollisionEntity (IL=13) narrated in entity-ai.md:
  null-guarded GetComponent<EntityDrone> - the E_Enemy hit resolve in the
  visibility ray chain.

## 2026-08-08 - tier-C: EntityDrone.IgnoreCollisionEntity

Done (V3.1.0 b14 IL):
- EntityDrone.IgnoreCollisionEntity (IL=38) narrated in entity-ai.md:
  drone + PhysicsTransform layers saved, both set to 2, ray re-run, layers
  restored - returns whether something behind the drone still blocks.

## 2026-08-08 - tier-C: EntityVehicle.FindCollisionEntity

Done (V3.1.0 b14 IL):
- EntityVehicle.FindCollisionEntity (IL=18) narrated in entity-ai.md:
  transform GetComponent<EntityVehicle> or parent CollisionCallForward's
  Entity cast to EntityVehicle - the vehicle-hit resolve in the visibility
  ray chain.

## 2026-08-08 - tier-C: GameUtils.GetHitRootTransform

Done (V3.1.0 b14 IL):
- GameUtils.GetHitRootTransform (IL=29) narrated in entity-ai.md: E_BP_
  prefixed tags re-root via RootTransformRefEntity (component RootTransform
  or FindEntityUpwards), E_Vehicle via CollisionCallForward.FindEntity,
  other tags unchanged - the CanEntityBeSeen hit re-rooting.

## 2026-08-08 - tier-C: Block conversions

Done (V3.1.0 b14 IL):
- blocks.md: Block.ToBlockValue (IL=8) = new BlockValue { type = blockID };
  BlockLiquidv2.WaterDataToBlockValue (IL=28) - mass > 195 -> water block
  type 240, damage 0, meta 2, meta2 = MAX_EMISSIONS, rotation 8, else Air.

## 2026-08-08 - tier-C: Block.GetBlockByName

Done (V3.1.0 b14 IL):
- Block.GetBlockByName (IL=19) narrated in blocks.md: null nameToBlock
  (uninitialized registry) -> null; else nameToBlockCaseInsensitive or
  nameToBlock TryGetValue (null when absent) - the block name registry.

## 2026-08-08 - tier-C: Block alternate resolution

Done (V3.1.0 b14 IL):
- blocks.md: Block.GetAltBlock (IL=19) = placeAltBlockClasses[typeId] with
  Block.list[0] fallback; GetAltBlocks (IL=39) lazy name-to-class resolve;
  GetAltBlockValue (IL=5) wrap; GetAltBlockNames (IL=3) field read.
  Completes the ToBlockValue alternate path.

## 2026-08-08 - tier-C: ItemValue.ToBlockValue

Done (V3.1.0 b14 IL):
- ItemValue.ToBlockValue (IL=26) narrated in blocks.md section 2: item
  type at/above Block.ItemsStartHere -> BlockValue.Air; else type copy,
  allowAlternates + SelectAlternates -> Block.GetAltBlockValue(Meta).
  Completes the block/item conversion pair.

## 2026-08-08 - tier-C: BlockValue.ToItemValue

Done (V3.1.0 b14 IL):
- BlockValue.ToItemValue (IL=6) narrated in blocks.md section 2: new
  ItemValue with type copied from the BlockValue type field - the block to
  item conversion (same id space, Block.ItemsStartHere offset aside).

## 2026-08-08 - tier-C: Entity.IsSpawned

Done (V3.1.0 b14 IL):
- Entity.IsSpawned (IL=2) base always true; EntityAlive.IsSpawned (IL=3)
  reads the bSpawned flag set in OnAddedToWorld. spawning.md.

## 2026-08-08 - tier-C: Entity.IsIgnoredByAI

Done (V3.1.0 b14 IL):
- Entity.IsIgnoredByAI (IL=3) field read; EntityDrone.IsIgnoredByAI (IL=2)
  always true - drones never AI targets; the flag behind EAITarget.check /
  NotifyNoise / horde member scan. entity-ai.md.

## 2026-08-08 - tier-C: Entity.GetMapObjectType

Done (V3.1.0 b14 IL):
- Entity.GetMapObjectType (IL=2) narrated in map-objects.md: base 0,
  EntitySupplyCrate override 13 - the special crate type handled by the
  MapObjectType == 13 branch in World.RemoveEntityFromMap.

## 2026-08-08 - tier-C: Entity.HasUIIcon

Done (V3.1.0 b14 IL):
- Entity.HasUIIcon (IL=13) narrated in map-objects.md: true when any of
  mapIcon / trackerIcon / compassIcon (EntityClass config) is non-null - the
  AddEntityToMap gate.

## 2026-08-08 - tier-C: World.worldToBlockPos

Done (V3.1.0 b14 IL):
- World.worldToBlockPos (IL=11) narrated in world-chunks.md: Vector3i of
  Fastfloor x/y/z - the floor-based world-to-block conversion; repaired a
  sentence dropped by an intermediate edit.

## 2026-08-08 - tier-C: Utils.GetAngleBetween

Done (V3.1.0 b14 IL):
- Utils.GetAngleBetween (IL=34) narrated in entity-ai.md: XZ-plane Atan2
  yaw difference x 57.29578, wrapped to [-180, 180] - the view-cone and
  IsInFrontOfMe half-angle test.

## 2026-08-08 - tier-C: EntityAlive.CanEntityBeSeen

Done (V3.1.0 b14 IL):
- EntityAlive.CanEntityBeSeen (IL=133) narrated in entity-ai.md: head
  vector, seeDist scaled by player DetectUsScale (stealth), view-cone gate,
  ray from head + dir*-0.1 with self model layer switched to 2, Voxel.Raycast
  (-1612492829, 64, 0); E_Vehicle seen iff target attached,
  E_Enemy drone pass-through, E_BP_ body-part re-root, seen iff hit
  transform == other.transform.

## 2026-08-08 - tier-C: EntityClass lookup leaves

Done (V3.1.0 b14 IL):
- spawning.md: EntityClass.GetEntityClass (IL=7) = list.TryGetValue,
  GetEntityClassName (IL=10) = entityClassName or 'null' string; repaired
  the LoadAssets paragraph split by an edit splice (GetEntityClassWithinMaxTier
  + GetPreviousTierEntity already covered by the Tier substitution section).

## 2026-08-08 - tier-C: SetSmellEat

Done (V3.1.0 b14 IL):
- PlayerStealth.SetSmellEat (IL=21) narrated in stealth-smell.md:
  smellEatRadius += distance capped 100, smellEatTicks = 1800 decay timer,
  smellRadius floored at 1, smellUpdateItemsTicks reset. The eat-smell
  trigger behind eating and the dysentery path.

## 2026-08-08 - tier-C: SmellTickWet

Done (V3.1.0 b14 IL):
- PlayerStealth.SmellTickWet (IL=19) narrated in stealth-smell.md:
  _wetnessrate cvar -> smellWetRate; rate >= 0.01 accumulates into
  smellWet (the wetness that suppresses item smell). Also restored the
  SmellTickEat paragraph displaced in an intermediate edit.

## 2026-08-08 - tier-C: SmellTickEat

Done (V3.1.0 b14 IL):
- PlayerStealth.SmellTickEat (IL=36) narrated in stealth-smell.md: eat
  radius decays 0.007142858 (1/140) per tick while smellEatTicks runs
  (cap 1640); full fade ~140 ticks (~7 s); zeroes radius + update ticks at
  the bottom.

## 2026-08-08 - tier-C: SmellCountToRadius

Done (V3.1.0 b14 IL):
- PlayerStealth.SmellCountToRadius (IL=18) narrated in stealth-smell.md:
  count -= 5 free threshold, negative -> 0, FastLerp(10, 100, count/45) -
  linear radius from 10 m at threshold to 100 m at full smell.

## 2026-08-08 - tier-C: SmellUpdateItemsAndBlood

Done (V3.1.0 b14 IL):
- PlayerStealth.SmellUpdateItemsAndBlood (IL=79) narrated in
  stealth-smell.md: dead or smellWet<3 -> SmellClear + client stealth
  package; dysenterySmell cvar -> SetSmellEat(35); wet (smellWetRate >=
  0.01) suppresses item smell; smellRadiusTarget = max(SmellCountToRadius(
  items), smellEatRadius); shelterPercent > 0 -> x0.2 + smellSheltered.

## 2026-08-08 - tier-C: PlayerStealth.SmellCountItems

Done (V3.1.0 b14 IL):
- PlayerStealth.SmellCountItems (IL=110) narrated in stealth-smell.md:
  carried-smell total = ItemClass.Smell * count summed over the drag-and-
  drop stack (local UI), toolbelt slots, and bag slots; clamped to 50,
  returned as int.

## 2026-08-08 - tier-C: Entity.GetBrightness

Done (V3.1.0 b14 IL):
- Entity.GetBrightness (IL=53) narrated in stealth-smell.md: chunk from
  position (missing -> 0), sample y = floor(pos.y - yOffset + boxHeight *
  0.66) - 66% up the bounding box - then world.GetLightBrightness. The
  ambient light source for the stealth light level.

## 2026-08-08 - tier-C: Inventory.HoldingItemHasChanged

Done (V3.1.0 b14 IL):
- Inventory.HoldingItemHasChanged (IL=51) narrated in items.md: cancels
  avatar events WeaponFire / PowerAttack / UseItem / ItemUse + UpdateBool
  Reload=false when the held item changes - drops in-flight action poses.

## 2026-08-08 - tier-C: ItemClass.CanStack

Done (V3.1.0 b14 IL):
- ItemClass.CanStack (IL=6) = Stacknumber > 1; ItemClassQuest.CanStack
  (IL=2) always false - quest items never stack. Completes the stack-cap
  story in items.md.

## 2026-08-08 - tier-C: ItemClass.get_MaxCount

Done (V3.1.0 b14 IL):
- ItemClass.get_MaxCount (IL=23) narrated in items.md: stack cap = min(
  FastRoundToInt(Stacknumber * MaxStackSizeModifier), 30000) when
  MaxStackSizeModifier != 1 AND !HasQuality AND CanStack; else raw
  Stacknumber. The 30000 hard cap bounds even scaled stacks.

## 2026-08-08 - tier-C: entity removal side

Done (V3.1.0 b14 IL):
- spawning.md removal side: World.RemoveEntity (IL=16) GetEntity +
  MarkToUnload + unloadEntity; RemoveEntityFromMap (IL=123) client
  vehicle/drone waypoint clear (local owner, reason 1/2/3) +
  ObjectOnMapRemove; MapObjectType 13 special case only on reason 2.

## 2026-08-08 - tier-C: Chunk entity membership

Done (V3.1.0 b14 IL):
- Chunk.AddEntityToChunk (IL=116) + RemoveEntityFromChunk (IL=41) narrated
  in entity-ai.md section 7: volatile hasEntities, wrong-chunk-position
  error log, Y-slice clamp(floor(pos.y/16), 0, 15), addedToChunk +
  chunkPosAddedEntityTo stamp, entityLists[slice] add; remove marks
  isModified and recomputes hasEntities from the 16 slices.

## 2026-08-08 - tier-C: PlayerStealth.NoiseCleanup

Done (V3.1.0 b14 IL):
- PlayerStealth.NoiseCleanup (IL=43) narrated in stealth-smell.md: walk the
  noise list, decrement ticks per entry, RemoveAt when reaching 1 - the
  fade-out half of the event-driven noise lifecycle.

## 2026-08-08 - tier-C: PlayerStealth.CalcVolume

Done (V3.1.0 b14 IL):
- PlayerStealth.CalcVolume (IL=68) narrated in stealth-smell.md: sum =
  Sigma noises[i].volume * 0.6^i (geometric decay, head dominates); stored
  noiseVolume = ((sum * 2.35) ^ 0.86) * 1.5 * passive 88; method returns the
  raw weighted sum, shaped value feeds detection thresholds.

## 2026-08-08 - tier-C: PlayerStealth.AddNoise

Done (V3.1.0 b14 IL):
- PlayerStealth.AddNoise (IL=35) narrated in stealth-smell.md: volume-
  descending insertion (first entry with volume <= new event, append when
  smallest); CalcVolume reads the head so loudest live events dominate.

## 2026-08-08 - tier-C: PlayerStealth.NotifyNoise

Done (V3.1.0 b14 IL):
- PlayerStealth.NotifyNoise (IL=71) narrated in stealth-smell.md: volume
  <= 0 false; AddNoise queue with (int)(duration*20) tick lifetime;
  volume >= 11 arms sleeperNoiseWaitTicks = 20; volume > 60 superlinear
  60 + (v-60)^1.4; passive 88 EffectManager scale; sleeperNoiseVolume
  accumulate, >= 360 clamp + true - the sleeper-wake signal consumed by
  AIDirector.NotifyNoise.

## 2026-08-08 - tier-C: AIDirector.NotifyNoise

Done (V3.1.0 b14 IL):
- AIDirector.NotifyNoise (IL=84) + OnSoundPlayedAtPosition (IL=17) narrated
  in aidirector.md: noise-table lookup (unknown clip silent), enemy /
  IsIgnoredByAI / ThrowableDecoy exclusions, tracked-player state lookup,
  crouch volumeScale *= muffledWhenCrouched, volume = noise.volume * scale
  -> PlayerStealth.NotifyNoise -> CheckSleeperVolumeNoise on accept, then
  heat-map NotifyActivity(3, pos, heatMapStrength * scale, 240).

## 2026-08-08 - tier-C: SmellMarker model

Done (V3.1.0 b14 IL):
- AIDirectorSmellMarker.Tick (IL=71) narrated in aidirector.md (was a
  stub): ttl/validTime decay clamped at 0, m_time capped at lifetime;
  effective radius = speed > 0 ? min(radius, speed*time) : radius (smell
  cloud expansion); effective strength = strength * (1 - time/lifetime)
  linear decay.

## 2026-08-08 - tier-C: MarkerManagementComponent

Done (V3.1.0 b14 IL):
- AIDirectorMarkerManagementComponent.Tick (IL=7) + TickMarkers (IL=43)
  narrated in aidirector.md (was a stub): reverse sweep of markers, per
  marker Tick(dt), removed + Release() to pool when TimeToLive <= 0 or the
  owning player died.

## 2026-08-08 - tier-C: BlockFaceFlags.FrontSidesFromPosition

Done (V3.1.0 b14 IL):
- BlockFaceFlags.FrontSidesFromPosition (IL=70) narrated in block-shapes.md:
  entity position relative to the block cell sets face bits - entity < block
  low-side x=8/y=2/z=16, entity >= block+1 high-side x=32/y=1/z=4; the faces
  the entity is outside of and crossing into.

## 2026-08-08 - tier-C: Block.IsMovementBlocked dispatch

Done (V3.1.0 b14 IL):
- block-shapes.md section 3 extended: Block.IsMovementBlocked single-face
  (IL=70) multiblock child->parent resolve with child-parent error log,
  !IsCollideMovement false, BlocksMovement byte short-circuit (==1) vs shape
  deferral (==0, BlockShape base GetStepHeight > 0.5); BlockFaceFlag sides
  (IL=90) AND across flagged faces (0 = all 255); entity-pos (IL=94) via
  FrontSidesFromPosition; IsMovementBlockedAny OR twin. Overrides: liquids /
  mines / motion sensor / pressure plate / spotlight / stairs(unless child)
  false; spikes true; BlockPoweredDoor !IsDoorOpen(meta); composite TE
  IFeaturePhysicalCapabilities modules when OverridesPhysicalChecks.

## 2026-08-08 - tier-C: Block.IsCollideMovement

Done (V3.1.0 b14 IL):
- Block.get_IsCollideMovement (IL=7) narrated in block-shapes.md section 3:
  (BlockingType & 2) != 0 - bit 1 of the blocking-type mask; the flag behind
  the GetStepHeight/IsMovementBlocked shape defaults.

## 2026-08-08 - tier-C: KickPlayerForClientInfo

Done (V3.1.0 b14 IL):
- GameUtils.KickPlayerForClientInfo (IL=24) narrated in platform-auth.md:
  NetPackagePlayerDenied.Setup(kickData) to client, 'Kicking player' log,
  ThreadManager coroutine disconnectLater(0.5 s) - deny package reaches the
  client before the disconnect.

## 2026-08-08 - tier-C: ProtocolManager.LateUpdate

Done (V3.1.0 b14 IL):
- ProtocolManager.LateUpdate (IL=35) narrated in network.md: fans
  LateUpdate() to every registered INetworkServer then INetworkClient;
  ConnectionManager.LateUpdate (IL=4) is the entry hook - post-frame
  network flush separate from the Update drain. (Also restored a sentence
  dropped in an intermediate edit.)

## 2026-08-08 - tier-C: Chunk.SpawnEntityAsync

Done (V3.1.0 b14 IL):
- Chunk.SpawnEntityAsync (IL=40) narrated in spawning.md: InProgressUnloading
  guard logs 'Spawning entity onto chunk which is unloading' + no-op;
  otherwise EntityAsyncManager.StartCreateEntity + pendingEntityCreateOps
  HashSet add (drained by OnUnload via WaitForComplete).

## 2026-08-08 - tier-C: ItemClass name resolution

Done (V3.1.0 b14 IL):
- ItemClass.GetItemClass (IL=15) nameToItem / nameToItemCaseInsensitive
  dict lookup; GetItem (IL=13) wraps hit into new ItemValue(class.Id) or
  ItemValue.None - the WorldBiomes.GetBlockValueForName resolution. items.md
  section 1.

## 2026-08-08 - tier-C: World entity lookups

Done (V3.1.0 b14 IL):
- entity-ai.md D7 entity lookups: World.GetEntity (IL=17) - async
  EntityAsyncManager.EnsureEntity when present, then Entities.dict
  TryGetValue (null when absent); World.GetEntityAliveCount (IL=31) -
  walk EntityAlives, count (entityFlags & mask) == flags.

## 2026-08-08 - tier-C: ChunkCluster read hops

Done (V3.1.0 b14 IL):
- world-chunks.md read surface extended: ChunkCluster.GetBlock (IL=21)
  y >= 256 -> Air guard + null chunk -> Air; GetBlockEntities (IL=59)
  IndexedBlocks[key] sweep across chunks with world-pos BlockEntityData
  collection; GetBlockEntity (IL=12) null on missing chunk;
  GetBlockFaceTexture (IL=23) 0 on missing chunk.

## 2026-08-08 - tier-C: block read surface

Done (V3.1.0 b14 IL):
- world-chunks.md section 2 block read surface: World.GetBlock (IL=13)
  ChunkCache null -> Air else ChunkCluster.GetBlock; WorldBase.GetBlock
  Vector3i/BlockValueRef (IL=4) IBlockAccess DefaultGetBlock; GetBlockData
  (IL=10) blockData dict; WorldBiomes.GetBlockValueForName (IL=15) name
  resolve + 'not found' throw + ToBlockValue.

## 2026-08-08 - tier-C: Equipment armor-group bookkeeping

Done (V3.1.0 b14 IL):
- Equipment.ResetArmorGroups (IL=51) + AddArmorGroup (IL=36) narrated in
  items.md: rebuild of ArmorGroupEquipped from m_slots (per ItemClassArmor
  ArmorGroup name with Quality); AddArmorGroup Count++ + LowestQuality min,
  new entry Count=1; set bonuses scale off worst piece.

## 2026-08-08 - tier-C: Equipment container

Done (V3.1.0 b14 IL):
- Equipment narrated in items.md section 6: SetSlotItem (IL=191) - empty
  value null under isLocal, IsEquipping wrap, same-value path fires only
  onSelfEquipStart (54); changed path tears down old item: activated items +
  mods fire onSelfItemDeactivate (92) + clear Activated (gated on the 91
  trigger), then onSelfEquipStop (57); preferredItemSlots store,
  slotsSetFlags/slotsChangedFlags bit set, bPlayerEquipmentChanged +
  ResetArmorGroups + OnChanged, IsEquipping false. SetSlotItemRaw (IL=13)
  silent store. SetCosmeticSlot class (IL=50): EquipSlot < 4,
  HasCosmeticUnlocked gate, ArmorGroup[0] dedupe, local changed flag; id
  variant (IL=72) CosmeticMappingIDString resolve, id 0 clears.

## 2026-08-08 - tier-C: Bag.GetItemCount mirror

Done (V3.1.0 b14 IL):
- Bag.GetItemCount type/tag overloads (IL=68/75) noted in items.md as the
  backpack mirror of the Inventory versions: same type-or-ItemTags match,
  seed/meta filters, ignoreModdedItems, over GetSlots().

## 2026-08-08 - tier-C: GameRandom Next overloads

Done (V3.1.0 b14 IL):
- GameRandom.Next family narrated in dedicated-misc-systems.md: Next() =
  InternalSample; Next(max) = (int)(Sample()*max) with negative throw;
  Next(min,max) validates min<=max, Sample()*range when fits int else
  GetSampleForLargeRange; NextBytes = InternalSample()%256 per byte.

## 2026-08-08 - tier-C: GameRandom seeding

Done (V3.1.0 b14 IL):
- GameRandom.SetSeed (IL=4) -> InternalSetSeed (IL=118) narrated as the
  .NET Random ctor verbatim: abs(seed) with int.MinValue -> int.MaxValue,
  mj = 161803398 - seed into SeedArray[55], (21*i)%55 scramble with mk =
  mj - mk walk, 5 mixing passes, inext = 0 / inextp = 21. Completes the
  portability claim in dedicated-misc-systems.md.

## 2026-08-08 - tier-C: GameRandom algorithm

Done (V3.1.0 b14 IL):
- GameRandom internals narrated in dedicated-misc-systems.md: classic .NET
  Random (Knuth subtractive) implemented inline - InternalSample (IL=61)
  56-entry SeedArray with inext/inextp wrap to 1, value = a[i]-a[i+21]
  style subtract with int.MaxValue clamp/rewrap; Sample (IL=6) x 2^-31;
  PeekSample (IL=50) non-advancing; GetSampleForLargeRange (IL=22)
  double-draw sign flip + (v+2147483646)/4294967293. Seeded sequences
  identical to System.Random - deterministic and portable.

## 2026-08-08 - tier-C: GameRandomManager

Done (V3.1.0 b14 IL):
- GameRandomManager narrated in dedicated-misc-systems.md: CreateGameRandom()
  (IL=5) seeds from baseSeed; CreateGameRandom(seed) (IL=8) = pooled
  AllocSync(false) + SetSeed. Callers: AIDirector.Init, GameEventManager
  ctor, ItemValue procedural ctor, DynamicMusicManager.Init,
  EModelInstanceAssets.Load.

## 2026-08-08 - tier-C: ItemStack size checks

Done (V3.1.0 b14 IL):
- ItemStack.CanStack (IL=19) = count + stack.count <= ItemClass.MaxCount
  (empty always true); CanStackPartly (IL=24) = FastMin(MaxCount - count,
  incoming) and > 0; CanStackPartlyWith (IL=15) seeds ref from other.count
  then partial path. Completes the CanStackWith family in items.md.

## 2026-08-08 - tier-C: ItemClass.CanMoveToLocation

Done (V3.1.0 b14 IL):
- ItemClass.CanMoveToLocation (IL=41) narrated in items.md: slotNumber >= 0
  requires CanMoveToSlot; bRestrictedMove requires locationType in
  restrictedTo StackLocationTypes list; both must hold. Completes the
  ItemStack.CanMoveTo chain.

## 2026-08-08 - tier-C: GameRandom surface

Done (V3.1.0 b14 IL):
- GameRandom narrated in dedicated-misc-systems.md: RandomFloat (IL=4) =
  (float)NextDouble() [0,1); RandomRange float overloads (IL=7/12) =
  NextDouble()*(max[-min])+min, max-exclusive; int overloads (IL=4/8) =
  Next(max[-min])+min. All gameplay callers funnel through these.

## 2026-08-08 - tier-C: group pick helpers

Done (V3.1.0 b14 IL):
- EntityGroups.NormalizeWorkingList (IL=51) narrated in spawning.md: sum
  probs, divide each by total (sum 1), non-positive total untouched.
- GetRandomFromGroupList (IL=37): RandomFloat roll, walk accumulating sum,
  return first entry with roll <= sum and prob > 0, else -1 (cumulative
  distribution weighted pick).

## 2026-08-08 - tier-C: spawn-group max-tier selection

Done (V3.1.0 b14 IL):
- EntityGroups.GetRandomEntityFromGroupMaxTier (IL=120) narrated in
  spawning.md (was a stub): group lookup with default world GameRandom,
  per-entry GetEntityClassWithinMaxTier tier clamp (null skip) + isEnemy /
  isAnimal flag filters, unknown-id error log return -1, static scratch
  workingGroupList rebuild with original weights, NormalizeWorkingList,
  weighted GetRandomFromGroupList up to 3 tries avoiding a repeat of the
  caller's lastClassId, winner stored back.

## 2026-08-08 - tier-C: BloodMoon component + party

Done (V3.1.0 b14 IL):
- aidirector.md BloodMoon bodies narrated (previously method-name stubs):
  Component.Tick (IL=170) - IsBloodMoonTime edge Start/EndBloodMoon, GameStats
  int 58 blood-moon-day change warn, GameStats bool 24 gate, AddPlayerToParty
  for spawned unpartied players, round-robin party ticks with delay = 1/Count
  window and nextParty rotation, KillPartyZombies on empty.
- Party.Tick (IL=162) - InitParty, 1.8 s ManagedZombie seek cadence, spawner
  canSpawn + CanSpawn(1.9) gates, groupIndex change -> spawnBaseDir += 120 +
  CalcBestDir, alive cap FastMin(maxAlive, enemyActiveMax), round-robin up to
  min(members,3) players.
- SpawnZombie (IL=181) - CalcSpawnPos, GetRandomEntityFromGroupMaxTier with
  50% attached -> animalZombieVultureRadiated override, CreateEntity +
  SetSpawnerSource(3) + SpawnEntityInWorld, horde/BM/observer flags,
  timeStayAfterDeath/3, bonus loot every bonusLootEvery scaled by LootBonusScale,
  AstarManager.AddLocation(40), structured log.
- CalcSpawnPos (IL=28) - radius rotated +-45 deg, GetMobRandomSpawnPosWithWater
  ring 10-30 m.

## 2026-08-08 - tier-C: SetBlock entry chain

Done (V3.1.0 b14 IL):
- blocks.md section 4 entry chain: World.SetBlock (IL=9) ->
  ChunkCluster.SetBlock IL=13 -> 10-arg dispatcher IL=48 switching on
  BlockValueRefType (BlockPosition -> 828-IL main body; PropReference ->
  SetProp via SetBlockValue IL=32); SetBlockRaw (IL=25) GetChunkSync +
  null no-op + chunk.SetBlockRaw. SetBlocksRPC (IL=6) ->
  gameManager.SetBlocksRPC; SetBlockRPC overloads (IL=7-8) wrap
  BlockChangeInfo variants.

## 2026-08-08 - tier-C: Chunk.GetLight nibbles

Done (V3.1.0 b14 IL):
- Chunk.GetLight (IL=28) narrated in light-mesh-water.md: x/z masked & 15
  to chunk-local, chnLight byte read, Sun = low nibble (light & 15),
  Block = high nibble (light >> 4). ChunkCluster.GetLight (IL=21) world
  wrapper: chunk lookup, null -> 0, else delegate.

## 2026-08-08 - tier-C: light query chain

Done (V3.1.0 b14 IL):
- Chunk.GetLightBrightness (IL=10) = GetLightValue / 15 (0-15 grid
  normalized); Chunk.GetLightValue (IL=30) = max(sun - darknessValue,
  blockLight): Sun channel read, darkness subtracted, returned when != 15,
  else max with Block channel; PrefabChunk stubs constant 15 / 1.0.
  Completes the World.GetLightBrightness chain in light-mesh-water.md.

## 2026-08-08 - tier-C: World.GetLightBrightness

Done (V3.1.0 b14 IL):
- World.GetLightBrightness (IL=32) narrated in light-mesh-water.md section 1:
  chunk present -> chunk.GetLightBrightness(toBlockXZ(x), toBlockY(y),
  toBlockXZ(z), 0); chunk missing -> IsDaytime() ? 0.65 : 0.1 ambient.
  Callers: particle spawn brightness, AutoTurretFireController.Fire,
  BlockModelTree fall effects.

## 2026-08-08 - tier-C: ItemStack stacking predicates

Done (V3.1.0 b14 IL):
- ItemStack.CanStackWith (IL=46) narrated in items.md section 2: both
  non-empty + same type + block texture equality (IsShapeHelperBlock
  exemption below Block.ItemsStartHere); allowPartialStack -> CanStackPartly
  vs CanStack. CanMoveTo (IL=15): ItemClass.CanMoveToLocation delegation,
  default true - the AddItem toolbelt gate.

## 2026-08-08 - tier-C: Inventory.AddItem

Done (V3.1.0 b14 IL):
- Inventory.AddItem (IL=121 + IL=5 wrapper) narrated in items.md section 6:
  CanMoveTo(Toolbelt, -1) gate, stack-merge pass (same type + CanStackWith)
  then empty-slot pass via SetItem(notify=true), notifyListeners +
  bPlayerStatsChanged = !isEntityRemote, out slot index.
- AddItemAtSlot (IL=84): PUBLIC_SLOTS bound, merge or CanMoveToSlot gate +
  SetItem, notify + stats-changed + HoldingItemHasChanged when held slot.

## 2026-08-08 - tier-C: EntityBuffs.AddBuff

Done (V3.1.0 b14 IL):
- EntityBuffs.AddBuff (IL=238) narrated in buffs.md: BuffStatus codes
  (Added..FailedGameStat enum-confirmed), electrical instigator swap to -1,
  gates: GetBuff miss, editor (AllowInEditor), RequiredGameStat != 81 sentinel
  + GetBool, netSync immunity, DamageType friendly-fire via FriendlyFireCheck;
  existing-buff merge by StackType (Ignore clear Remove / Replace reset
  ticks / Duration max(InitialDurationMax, duration, duration-remaining) /
  Effect StackEffectMultiplier++), each fires onSelfBuffStack (4); new-buff
  path: local player buffLegBroken achievement stat 15, DurationMax from
  duration or InitialDurationMax, BuffValue append. AddBuffNetwork (IL=34):
  NetPackageAddRemoveBuff Setup + SendPackage flags 192 (server) or
  SendToServer (client).

## 2026-08-08 - tier-C: SdtdConsole.Update pump

Done (V3.1.0 b14 IL):
- SdtdConsole.Update (IL=60) narrated in console-commands.md: FIFO drain of
  m_commandsToExecuteAsync at one command per frame under Monitor lock;
  CommandSenderInfo with NetworkConnection = entry.sender, executeCommand
  (exceptions -> Log.Exception), result SendLines back to sender,
  RemoveAt(0); N queued commands take N main-thread frames.

## 2026-08-08 - tier-C: Inventory.setHeldItemByIndex

Done (V3.1.0 b14 IL):
- Inventory.setHeldItemByIndex (IL=132) narrated in items.md section 5:
  BeginSwapHoldingItem, negative/oversized index wrap by slots.Length,
  flashlightOn+IsHoldingFlashlight capture, HoldingItemHasChanged, avatar
  itemHasChangedTriggerHash, BroadcastStop of ItemActionAttack GetSoundStart
  sounds, m_HoldingItemIdx = m_FocusedItemIdx = idx, remote ->
  updateHoldingItem direct, local -> ShowHeldItem(0.2 or 0, true), flashlight
  re-toggle SetFlashlight(false) + currActiveItemIndex=-1 + flashlight_toggle
  one-shot. SetHoldingItemIdx / NoHolsterTime are 5-IL wrappers passing
  applyHolsterTime true/false.

## 2026-08-08 - tier-C: Inventory.updateHoldingItem

Done (V3.1.0 b14 IL):
- Inventory.updateHoldingItem (IL=172) narrated in items.md section 5:
  same-item OnHoldingReset shortcut; teardown StopHolding + FireEvent
  onSelfEquipStop (57) when not in ignoreWhenHeld + model hide under
  inactiveItems; draw: QuestEventManager.HeldItem, StartHolding,
  MinEventContext ItemValue (seed copied) + Transform, ShowRightHand,
  FireEvent onSelfHoldingItemCreated (83) + onSelfEquipStart (54);
  OnHoldingItemChanged + lastDrawn cache refresh.
- ShowHeldItem (IL=19): stop + restart delayedShowHideHeldItem coroutine
  (hideFirst, waitTime) on GameManager.

## 2026-08-08 - tier-C: Inventory notify + read accessors

Done (V3.1.0 b14 IL):
- Inventory.notifyListeners (IL=24) narrated in items.md section 6:
  onInventoryChanged hook + HashSet<IInventoryChangedListener> fan-out.
- Read accessors: GetItemInSlot/GetItemDataInSlot bare-hand fallback,
  GetItemCount type overload (IL=92) and tag overload (IL=86) with
  texture/seed/meta/ignoreModded filters, XUiM_PlayerInventory backpack+
  toolbelt summing wrappers (IL=19).

## 2026-08-08 - tier-C: Inventory.SetItem

Done (V3.1.0 b14 IL):
- Inventory.SetItem (IL=166) narrated in items.md section 6: held-slot write
  ShowHeldItem(0.2, true) on value change, bounds guard, missing item class
  warning + Clear, preferredItemSlots type memory (new type on notify, old
  type otherwise), class-change rebuild via clearSlotByIndex +
  createHeldItem(CanHold)/createInventoryData, Clone-store + count, then
  updateHoldingItem on held slot and notifyListeners when requested;
  SetItem(idx, ItemStack) IL=9 wrapper passes notifyListeners=true.

## 2026-08-08 - tier-C: EntityPlayer.Update

Done (V3.1.0 b14 IL):
- EntityPlayer.Update (IL=179) narrated in loop.md Path B: generalTags
  cache, game-started gate, totalTimePlayed minutes accumulation with
  hourly GameSparks SetValue (GSDataKey 6, < 301 min) for local player,
  ChunkObserver SetPosition per frame + mapDatabase.Add on chunk change,
  avatar SetHeadAngles/SetArmsAngles (held item CanHold -> x+90),
  currentLife/longestLife tracking with QuestEventManager.TimeSurvived +
  achievement stat 9 on new minutes, HasUpdated = true at end.

## 2026-08-08 - tier-C: SetPosition width/height/depth source

Done (V3.1.0 b14 IL):
- Entity width/height/depth getters (all IL=6) pinned as scaledExtent x/y/z
  x 2 in entity-ai.md D7, tying SetPosition boundingBox rebuild to the
  SetupBounds half-extents; fixed a sentence lost in the previous edit.

## 2026-08-08 - tier-C: Entity.SetPosition

Done (V3.1.0 b14 IL):
- Entity.SetPosition (IL=111) narrated in entity-ai.md D7: position store,
  boundingBox rebuild from width*0.5/depth*0.5, yOffset/ySize base and
  +height top, recursion into attachedEntities with bUpdatePhysics=false;
  physics mirror: PhysicsTransform.position = pos - Origin.position,
  physicsPos = (pos-Origin)+physicsBasePos on physicsRBT, physicsTargetPos =
  PhysicsTransform.position. Overrides: EntityDrone base-only, EntityPlayerLocal
  Origin/FPController/camera (client), EntityVehicle ModelTransform for local.

## 2026-08-08 - tier-C: EAISetNearestCorpseAsTarget

Done (V3.1.0 b14 IL):
- EAISetNearestCorpseAsTarget.CanExecute (IL=110) narrated in entity-ai.md:
  investigate/sleep rejects, 1/rndTimeout probabilistic throttle, living
  player target kept 95% of the time, search radius 7 when sleeper else
  maxXZDistance, World.GetEntitiesAround into static scratch + nearest sorter,
  first dead EntityAlive wins (dead animals only with ZombiesEatAnimalCorpses).

## 2026-08-08 - tier-C: EAIMeleeAttackTarget

Done (V3.1.0 b14 IL):
- EAIMeleeAttackTarget narrated in entity-ai.md: CanExecute (IL=69) gates -
  not dancing, cooldown drain via executeWaitTime, IsAttackValid, target
  null/dead reject, IsAnyLegMissing / (startAnimType>=0 and arm missing)
  rejects, InRange + CanSee. SetData (IL=70) keys: slot, itemType,
  startAnimType, releaseDelay, cooldown, duration, min/max/unreachableRange,
  sndStart/sndRelease. Update (IL=107) 0.05 s state machine: wind-up look +
  SeekYawToPos(30); state 0 -> anim action 2 -> ContinueAnimAction(start+3001)
  + sndRelease play; state 1 -> releaseDelay; state 2 -> UseHoldingItem(false)
  and elapsedTime = float.MaxValue when item use ends.

## 2026-08-08 - tier-C: EntityAlive.SetLookPosition

Done (V3.1.0 b14 IL):
- EntityAlive.SetLookPosition (IL=43) narrated in entity-ai.md: early-out
  when sqrMagnitude of delta < 0.0016 (4 cm); store lookAtPosition;
  SendPacketToTrackedPlayers with NetPackageEntityLookAt(entityId, pos);
  forward to avatarController.SetLookPosition (cosmetic aim).

## 2026-08-08 - tier-C: EAILook.Continue + MinEvent name

Done (V3.1.0 b14 IL):
- EAILook.Continue (IL=116) narrated in entity-ai.md EAI leaves: stun gate,
  alert timers - 14-tick yaw seek SeekYaw(rotation.y + rand*120-60, 0, 35),
  40-tick look point SetLookPosition(headPos + Euler(rand*60-30,
  rand*120-60, 0) * forward*20); ends on waitTicks expiry.
- progression.md: MinEventTypes value 5 named as onSelfProgressionUpdate
  (EnumDump) in the Progression.Update cadence narration.

## 2026-08-08 - tier-C: Progression.Update + sandbox recompute

Done (V3.1.0 b14 IL):
- Progression.Update (IL=32) narrated in progression.md: 1-second cadence
  MinEvent fire (type 5) on timer<=0 then timer=1, else timer-=dt; every
  frame Buffs.SetCustomVar(_expdeficit, ExpDeficit, netSync, op, forceSend).
- Progression.UpdateForSandbox (IL=22) -> ProgressionClass.UpdateForSandbox
  (IL=52): backward walk of DisplayDataList, Enabled from HandleCheckEnabled,
  MaxLevel from QualityStarts top entry of first enabled display row.

## 2026-08-08 - tier-C: Entity.animateYaw

Done (V3.1.0 b14 IL):
- Entity.animateYaw (IL=54) narrated in entity-ai.md SeekYaw block as the
  per-frame interpolation half: while yawSeekTimeMax>0 accumulate
  yawSeekTime+=dt and rotation.y = Lerp(yawSeekAngle, yawSeekAngleEnd,
  Clamp01(yawSeekTime/yawSeekTimeMax)); on window expiry snap to
  yawSeekAngleEnd and zero yawSeekTimeMax (IsSeekYaw gate); denormal-tiny
  positive timeMax snaps immediately.

## 2026-08-08 - tier-C: Entity physics hooks

Done (V3.1.0 b14 IL):
- Entity.FixedUpdate (IL=71) narrated in loop.md Path B: ApplyFixedUpdate
  then wasFixedUpdate=true; velocity/angularVelocity damped x0.9 per step;
  physicsPos = Lerp(rbt.position, physicsTargetPos+physicsBasePos, 0.4),
  physicsRot = Slerp(rot, Euler(0,yaw,0), 0.3), SetPositionAndRotation;
  CrouchHeightFixedUpdate when physics capsule on EntityAlive.
- Entity.PhysicsMasterTargetFrameUpdate (IL=52): elapsed/time ratio lerp of
  physicsMaster FromPos/TargetPos and FromRot/TargetRot, SetPosition(pos,true)
  + qrotation, mirrored into physicsRB origin-space, targetTime zeroed on
  completion so next frame reverts to updateTransform.

## 2026-08-08 - tier-C: Entity.updateTransform

Done (V3.1.0 b14 IL):
- Entity.updateTransform (IL=183) narrated in loop.md Path B: attach/ragdoll
  early-outs, ApplyFixedUpdate first; position lerp via physicsRBT-physicsBasePos
  scaled by physicsPosMoveDistance*dt/fixedDt, or origin-space
  position-Origin.position by dt*updatePositionLerpTimeScale; isRotateToGround
  pitch from groundSurface.normal (flat override, clamped to up outside
  0.7..0.99 dot), smoothed pitchVel = vel*0.86 + DeltaAngle*0.8*dt; plain yaw
  LerpAngle path; remote PhysicsTransform position mirror.

## 2026-08-08 - tier-C: Entity.Update base + updateNetworkStats

Done (V3.1.0 b14 IL):
- Base Entity.Update (IL=105) narrated in loop.md Path B: bWasDead snapshot,
  animateYaw, PhysicsMasterTargetFrameUpdate vs updateTransform on
  physicsMasterTargetTime>0, chunk-observer lazy create + SetPosition per
  frame vs Dispose on flag drop, animatorAudioMonitoringDictionary sweep
  (stop + remove finished handles).
- EntityAlive.updateNetworkStats (IL=55): drains networkStatsUpdateQueue one
  entry per call - m_NetworkStats -> EntityNetworkStats.ToEntity + return;
  m_HoldingData -> SetItem when slot differs + SetHoldingItemIdxNoHolsterTime
  when held index changed.

## 2026-08-08 - tier-C: EntityAlive frame hooks

Done (V3.1.0 b14 IL):
- loop.md 3.3 Path B body narrated: EntityAlive.Update (IL=171) order - base
  Entity.Update, updateNetworkStats, root-motion speedForward lerp (dead
  constant ternary 0.06935714/0.01942 artifacts noted), _underwater cvar
  sync, full MinEventContext refresh (Area/Biome/ItemValue/BlockValue/
  ItemInventoryData/Position/Seed=entityId+Abs(World.Seed)/Transform/Tags
  CombineTags of class+item+stance+movement), Progression.Update, renderFade
  MoveTowards + SetFade + SetVisible(fade>0.01). LateUpdate (IL=6) copies
  entityStats into startOfFrameStats. OnDeathUpdate (IL=76): corpse timer
  capped at timeStayAfterDeath, snap when DeathHealth <= -DeadBodyHitPoints
  (>0), then particleOnDestroy spawn at head position (local, not unloaded).

## 2026-08-08 - tier-C: Entity.SetupBounds

Done (V3.1.0 b14 IL):
- Entity.SetupBounds (IL=90) narrated in entity-ai.md D7: called from
  Entity.Awake (IL_0052) and EntityHuman.TurnIntoCrawler (IL_0049); three
  cases - BoxCollider (scaledExtent = size*localScale*0.5, nativeCollider,
  disabled when isDetailedHeadBodyColliders), CharacterController (radius
  half-widths, height*0.5 half-height), fallback unit box; boundingBox
  origin-relative, recentered by SetPosition (IL_0065) and
  aabbEntityCollision (IL_0180/02A2).

## 2026-08-08 - tier-C: BoundsUtils.ClipBoundsMove + decoration offset

Done (V3.1.0 b14 IL):
- BoundsUtils.ClipBoundsMove (IL=67) + 6 per-axis clippers (IL=72-114)
  narrated in entity-ai.md D4: dispatcher clips move Y->X->Z translating the
  box after each axis; per-axis logic: move==0 skip, lateral overlap gate,
  face-flush Clamp on positive/negative move, Y-only 0.2 step allowance when
  collider top protrudes < 0.2 into box bottom, Abs(move)<0.0001 zero-snap
  with early loop exit in the IList variants bounded by numColliders.
- MarchingCubes.GetDecorationOffsetY (IL=12) = FastClamp(-0.0035 *
  (densY + densYm1), -0.4, 0.4) - terrain collision decoration offset.

## 2026-08-08 - tier-C: Block.GetCollidingAABB

Done (V3.1.0 b14 IL):
- Block.GetCollidingAABB (IL=33) narrated as the shape-box wrapper behind
  World.GetCollidingBounds: clears staticList_IntersectRayWithBlockList,
  fills via GetCollisionAABB with distortedAddY, copies entries that
  Intersects the query AABB into the caller list.

## 2026-08-08 - tier-C: World.GetCollidingBounds

Done (V3.1.0 b14 IL):
- World.GetCollidingBounds (IL=391) narrated in entity-ai.md D4: padded
  ranges (0.5 X/Z, 1 Y), chunk walk with cached chunk + GetChunkFromWorldPos,
  IsInPlayfield false -> whole-chunk GetAABB obstacle, fill pass into scratch
  collBlockCache/collDensityCache (3D, offset reads +1), AABB pass filtered by
  IsCollideMovement with terrain decoration offsetY via
  MarchingCubes.GetDecorationOffsetY, entity pass via 0.25-expanded
  GetEntitiesInBounds + own box, 50-iteration cap per loop with NBB warning
  strings (Log.Warning) and partial-list return.

## 2026-08-08 - tier-C: FastTags query + CanCollideWith

Done (V3.1.0 b14 IL):
- FastTags Test_Bit (IL=46) + Test_AnySet (IL=68) narrated in entity-ai.md
  D8.6b: empty-query semantics, singleBit fast paths, word-AND over
  Mathf.Min word count; Entity.HasAnyTags (IL=5) = cachedTags.Test_AnySet.
- CanCollideWith family (13 overloads) in D7 predicates: base true, EntityAlive
  false when dead or vs EntityItem/EntitySupplyCrate, falling blocks only vs
  EntityAlive, EntityItem true, falling tree/supply crate false;
  CanCollideWithBlocks matrix (EntityAlive false while sleeping, car/homerun/
  supplycrate/supplyplane false).

## 2026-08-08 - tier-C: GetEntitiesInBounds family

Done (V3.1.0 b14 IL):
- Narrated World.GetEntitiesInBounds (4 overloads, IL=68-75) + Chunk
  GetEntitiesInBounds (3 overloads, IL=85-86) in entity-ai.md D7: World
  tier computes chunk (x,z) range from AABB padded +-5 then /16, fans via
  GetChunkSync into chunk tier; Entity overloads reuse shared
  entitiesWithinAABBExcludingEntity scratch list (cleared per call), FastTags
  and Type overloads append into caller list. Chunk tier maps padded Y range
  to slice band clamped [0,15], per-slice entityLists scan with
  boundingBox.Intersects on the unpadded box; filters: exclude + isAlive +
  CanCollideWith, HasAnyTags, IsAssignableFrom.

## 2026-08-08 - tier-C: GamePrefs.Save paths

Done (V3.1.0 b14 IL):
- GamePrefs.Save() (IL=78) narrated in save-persistence.md: walks
  s_propertyList, writes IsPersistent prefs to SdPlayerPrefs keyed by cached
  enum name (Int/Float/String via typed setters, Bool as SetInt 0/1, Binary as
  ToBase64 string), then SdPlayerPrefs.Save + CommitAsync + log. Dedicated
  shutdown path (SaveAndCleanupWorld IL_06B0, ConsoleCmdGfx/SetTempUnit,
  GameManager.Awake). Save(file) (IL=29) + Save(file, list) (IL=92) SDF
  variant: SdfFile typed Set per EnumType, client-menu callers only.

## 2026-08-08 - tier-C: FastTags bit model

Done (V3.1.0 b14 IL):
- FastTags<T> bit model completed in entity-ai.md D8.6b: GetBit (IL=56)
  trims + looks up static tags dict, miss assigns Interlocked.Increment(next)
  and registers tags/bitTags pairs, rebuilds allInternal all-ones mask when
  (bit>>6)+1 exceeds it; GetTag (IL=4) wraps GetBit into single-bit FastTags;
  GetTagNames (IL=78) resolves singleBit or walks 64-bit words collecting
  set-bit names. Note: GetBit dict writes unsynchronized outside Parse lock.

## 2026-08-08 - tier-C: FastTags.Parse

Done (V3.1.0 b14 IL):
- FastTags<T>.Parse (IL=90) narrated in entity-ai.md D8.6b: single-tag
  shortcut via GetTag, multi-tag path splits on ',', each tag maps to a bit
  index via GetBit, bit>>6 selects a 64-bit maskList word (grown with zeros),
  maskList[bucket] |= 1UL << (bit & 63); whole multi-tag path under Monitor
  on the static scratch list, Clear() after ToArray() into the FastTags.

## 2026-08-08 — tier-C: World.Cleanup

Done (V3.1.0 b14 IL):
- World.Cleanup IL=162: prefab cache, chunk manager, audio, conductor, light,
  entity GO destroy, Entities/EntityAlives clear, biomes.
## 2026-08-08 — tier-C: World.UnloadWorld

Done (V3.1.0 b14 IL):
- World.UnloadWorld IL=62: environment destroy, chunk cluster cleanup,
  UnloadEntities(all, true), EntityFactory.Cleanup, selection categories,
  deco/block unload hooks.
## 2026-08-08 — census refresh 8

Done:
- Coverage.exe re-run: narrated 1509, catalogued 811, unaccounted 0.
## 2026-08-08 — tier-C: ShutdownMultiplayerServicesNow

Done (V3.1.0 b14 IL):
- ShutdownMultiplayerServicesNow IL=33: advertise stop, AuthorizationManager.
  ServerStop, master announcer + ServerInformationTcpProvider stop, lobby
  exit, EndOnlineMultiplayer.
## 2026-08-08 — tier-C: GameStateManager.EndGame

Done (V3.1.0 b14 IL):
- EndGame IL=13: GameState Loading, bDirty, bGameStarted/bServer cleared.
## 2026-08-08 — tier-C: SaveAndCleanupWorld ordered chain

Done (V3.1.0 b14 IL):
- SaveAndCleanupWorld IL=499: WorldShuttingDown mod event first, async create
  drain, server save block (vehicles/drones/quests/player/world/persistent),
  nameIdMapping saves, client map DB async, multiplayer shutdown, world
  teardown (UnloadWorld + Cleanup), singleton cleanup sweep, GamePrefs.Save.
## 2026-08-08 — tier-C: GamePrefs.notifyListeners

Done (V3.1.0 b14 IL):
- GamePrefs.notifyListeners IL=24: IGamePrefsChangedListener fan-out + static
  OnGamePrefChanged action.
## 2026-08-08 — tier-C: EntityFallingBlock.SetBlockValue

Done (V3.1.0 b14 IL):
- SetBlockValue IL=32: isTerrain from shape, terrainScale rand(0.3, 0.98),
  collider selection.
## 2026-08-08 — tier-C: EntityItem init leaves

Done (V3.1.0 b14 IL):
- EntityItem.Init IL=10 (itemRB), PostInit IL=37 (PhysicsSetRB, stickPercent
  from StickPercent prop, itemWorldData), InitLocalActivationCommands IL=15
  (take/search).
## 2026-08-08 — tier-C: Entity.AddVelocity

Done (V3.1.0 b14 IL):
- Entity.AddVelocity IL=10: motion += vel + SetAirBorne(true); noted on the
  NetPackageEntityAddVelocity row.
## 2026-08-08 — tier-C: SeekYaw turning helper

Done (V3.1.0 b14 IL):
- Entity.SeekYaw IL=136: 360 wrap, MaxTurnSpeed (water-scaled), quadratic
  slow-down near target (min 20), arms yawSeek* interpolation; IsSeekYaw IL=5.
## 2026-08-08 — tier-C: EntityEnemy.PostInit blood moon flag

Done (V3.1.0 b14 IL):
- EntityEnemy.PostInit IL=13: server IsBloodMoon from BloodMoonComponent.
## 2026-08-08 — tier-C: EntityAnimal.OnEntityDeath

Done (V3.1.0 b14 IL):
- EntityAnimal.OnEntityDeath IL=24: physics transform off, base, waypoint
  removal for local player.
## 2026-08-08 — tier-C: EntityPlayer.OnUpdateLive

Done (V3.1.0 b14 IL):
- EntityPlayer.OnUpdateLive IL=13: stamina regen zero, base, see-cache clear,
  CheckSleeperTriggers.
## 2026-08-08 — tier-C: StartStopLivingSound

Done (V3.1.0 b14 IL):
- EntityAlive.StartStopLivingSound IL=55: soundLiving loop gate (spawned/
  alive/health), soundSpawn once unless SleeperSupressLivingSounds.
## 2026-08-08 — census refresh 7

Done:
- Coverage.exe re-run: narrated 1505, catalogued 815, unaccounted 0.
## 2026-08-08 — tier-C: SetBlocksRPC wrapper

Done (V3.1.0 b14 IL):
- GameManager.SetBlocksRPC IL=29: ChangeBlocks commit + NetPackageSetBlock
  replicate (SetBlocksOnClients on server / SendToServer).
## 2026-08-08 — tier-C: PickupBlockServer replacement

Done (V3.1.0 b14 IL):
- GameManager.PickupBlockServer IL=77: type-verify gate, local/client split,
  PickupSource replacement (or Air) via SetBlocksRPC.
## 2026-08-08 — tier-C: InitCommandLine + pref collisions

Done (V3.1.0 b14 IL):
- GameStartupHelper.InitCommandLine IL=85: version banner, PrintSystemInfo,
  LaunchPrefs start/end, parsedGamePrefs, ParseCommandLine.
- GameEntrypoint.HasPrefCollisions IL=53: LaunchPref/GamePref name collision
  abort.
## 2026-08-08 — tier-C: GameEntrypoint.FirstFrameInit

Done (V3.1.0 b14 IL):
- FirstFrameInit IL=65 boot chain: pref collisions abort, GamePrefs decls,
  InitCommandLine, automation logging, user data paths, platform/service init,
  analytics start, targetFrameRate = refresh rate.
## 2026-08-08 — tier-C: ApplyParsedGamePrefs commit

Done (V3.1.0 b14 IL):
- ApplyParsedGamePrefs IL=57: SetObject each parsed pref, dedicated GameName
  validation (quit on invalid), SetDedicatedServerSettings on success.
## 2026-08-08 — tier-C: GamePrefs.Parse typed conversion

Done (V3.1.0 b14 IL):
- GamePrefs.Parse IL=45: PropertyDecl.type switch (Int32 TryParse/Float/Bool/
  String, unknown -> null); ParseGamePref IL=24 stores to parsedGamePrefs or
  reports Could not parse config value.
## 2026-08-08 — tier-C: config file load + pref parse

Done (V3.1.0 b14 IL):
- GameStartupHelper.LoadConfigFile IL=146: ServerSettings XML -> Dynamic
  Properties -> ParsePref per key; missing/unparseable quits.
- ParsePref IL=74: LaunchPrefs lookup -> ParseLaunchPref; EnumGamePrefs
  TryParse -> ParseGamePref; unknown ignored on cmdline, error in config.
## 2026-08-08 — tier-C: GameStartupHelper boot leaves

Done (V3.1.0 b14 IL):
- ParseCommandLine IL=82: configfile load (+.xml), ParsePref each, dedicated
  NoGraphicsMode 139, dedicated quits without a config file.
- InitGamePrefs IL=36: GameVersion = cVersionInformation.LongStringNoBuild,
  ApplyParsedGamePrefs.
- SetDedicatedServerSettings IL=51: boot logs, all prefs non-persistent,
  OpenMainMenuAfterAwake = false.
## 2026-08-08 — census refresh 6

Done:
- Coverage.exe re-run: narrated 1500, catalogued 815, unaccounted 0.
## 2026-08-08 — tier-C: SetEntityName

Done (V3.1.0 b14 IL):
- EntityAlive.SetEntityName IL=20: store + bPlayerStatsChanged when server-
  owned + HandleSetNavName.
## 2026-08-08 — tier-C: max-tier zombie substitution

Done (V3.1.0 b14 IL):
- EntityClass.GetEntityClassWithinMaxTier IL=30 (tier walk) and
  GetPreviousTierEntity IL=73 (PreviousTierZombieName chain, random pick);
  MaxEntityTier degradation documented in spawning §7.
## 2026-08-08 — tier-C: CreateEntityOperation.LoadAssets

Done (V3.1.0 b14 IL):
- LoadAssets IL=100: class resolve, MaxEntityTier substitution + id rewrite,
  isPlayer/isLocalPlayer detection, EntityInstanceAssets/EModelInstanceAssets
  async load.
## 2026-08-08 — tier-C: CreateEntityOperation.Start

Done (V3.1.0 b14 IL):
- Start IL=25: id alloc (nextEntityID++ or max(+1)), LoadAssets(isSync) async
  kickoff; added to spawning §7.
## 2026-08-08 — tier-C: GetLookVector + GetMaxViewAngle

Done (V3.1.0 b14 IL):
- EntityAlive.GetLookVector IL=40: facing from yaw/pitch trig; GetMaxViewAngle
  IL=5 = maxViewAngle field.
## 2026-08-08 — tier-C: SetModelLayer

Done (V3.1.0 b14 IL):
- EntityAlive.SetModelLayer IL=7 = Utils.SetLayerRecursively on the model
  transform (LOS ray self-exclusion).
## 2026-08-08 — tier-C: switchModelView

Done (V3.1.0 b14 IL):
- EntityAlive.switchModelView IL=11: SwitchModelAndView(view==0, IsMale) +
  ReassignEquipmentTransforms.
## 2026-08-08 — tier-C: EntityAlive init chain

Done (V3.1.0 b14 IL):
- EntityAlive.Init IL=13 (base + InitStats + switchModelView + InitPostCommon);
  InitPostCommon IL=97 (ServerHelper.SetupForServer, character controller,
  seen-by-player 20 ticks, UAI wiring, class buffs, invisible flags);
  PostInit IL=34 (ApplySpawnState, LOD 0.003, fall disabled, HandleSpawn
  Modifier); InitInventory IL=9.
## 2026-08-08 — tier-C: SetAlive chain + game-stage born-at clock

Done (V3.1.0 b14 IL):
- Entity.SetAlive IL=34 (physics layers 20/3/15), EntityAlive IL=46
  (lastAliveTime), EntityPlayer IL=31 (gameStageBornAtWorldTime advance by
  DaysAliveChangeWhenKilled*24000 or reset on fresh respawn).
## 2026-08-08 — tier-C: EntityAlive.OnAddedToWorld

Done (V3.1.0 b14 IL):
- OnAddedToWorld IL=27: occlusion add (7), m_addedToWorld, bSpawned (server),
  MinEvent 61 for non-players, StartStopLivingSound.
## 2026-08-08 — tier-C: InitBreadcrumbs

Done (V3.1.0 b14 IL):
- EntityPlayer.InitBreadcrumbs IL=6: Utils.Fill(breadcrumbs, position).
## 2026-08-08 — census refresh 5

Done:
- Coverage.exe re-run: narrated 1498, catalogued 817, unaccounted 0.
## 2026-08-08 — tier-C: AddCustomVar

Done (V3.1.0 b14 IL):
- EntityBuffs.AddCustomVar IL=8 = SetCustomVar(netSync, Set, no force).
## 2026-08-08 — tier-C: cvar readers

Done (V3.1.0 b14 IL):
- EntityBuffs.GetCustomVar IL=10 (CVars TryGetValue else 0) and
  GetCustomVarId IL=3 (GetHashCode); noted in buffs.md.
## 2026-08-08 — tier-C: GetCVar

Done (V3.1.0 b14 IL):
- EntityAlive.GetCVar IL=10: Buffs.GetCustomVar or 0.
## 2026-08-08 — tier-C: hazard contact damage

Done (V3.1.0 b14 IL):
- BlockDamage.OnEntityCollidedWithBlock IL=126: DamageSourceEntity with
  AttackingItem/BlockPosition, ignore-consecutive, hit transform for humans,
  DamageEntity(damage, false, 1).
## 2026-08-08 — tier-C: walk-trigger block overrides

Done (V3.1.0 b14 IL):
- Block.OnEntityWalking base no-op; BlockJumpPad IL=5 motion.y=3; BlockMine
  IL=113: LandMineImmunity 137 skip, spectator skip, trigger sound, delay 171,
  entity damage 172 (TrapIncomingDamage), scheduled detonate delay*20.
## 2026-08-08 — tier-C: GamePrefs.GetObject

Done (V3.1.0 b14 IL):
- GamePrefs.GetObject IL=20: bounds check -> null, else propertyValues (no
  sandbox routing in the pref getter).
## 2026-08-08 — tier-C: GamePrefs.SetObject

Done (V3.1.0 b14 IL):
- GamePrefs.SetObjectInternal IL=38: bounds check, null/equal skip, store +
  notifyListeners.
## 2026-08-08 — tier-C: GameStats.SetObject

Done (V3.1.0 b14 IL):
- GameStats.SetObject IL=12: propertyValues store + OnChangedDelegates invoke;
  Set overloads box only (writes do not touch sandbox refs).
## 2026-08-08 — tier-C: GameStats.GetInt sandbox routing

Done (V3.1.0 b14 IL):
- GameStats.GetInt IL=34: server reads sandboxReferences first (GetIntValue)
  then raw propertyValues; sandbox overrides live in the read path.
## 2026-08-08 — tier-C: addEntityComponent

Done (V3.1.0 b14 IL):
- EntityFactory.addEntityComponent IL=5/11: Type.GetType + AddComponent cast
  Entity; null on bad type (CompleteEntity generic path).
## 2026-08-08 — census refresh 4

Done:
- Coverage.exe re-run: narrated 1497, catalogued 818, classified 1384,
  unaccounted 0.
## 2026-08-08 — tier-C: SetSupplyCratePosition cache

Done (V3.1.0 b14 IL):
- AIDirectorAirDropComponent.SetSupplyCratePosition IL=30: SupplyCrateCache
  blockPos update by entityId, warning when missing.
## 2026-08-08 — tier-C: EnumStat mapping

Done (V3.1.0 b14 IL):
- NetPackageEntityStatChanged/EnumStat pinned: Health 0, Stamina 1, Sickness 2,
  Gassiness 3, SpeedModifier 4, Wellness 5, CoreTempOLD 6, Food 7, Water 8.
## 2026-08-08 — tier-C: stat max getters

Done (V3.1.0 b14 IL):
- Stat.get_ModifiedMax IL=6 = baseMax + maxModifier; ModifiedMaxPercent
  clamp01; EntityAlive.GetMaxHealth IL=6 = (int)Health.Max.
## 2026-08-08 — tier-C: SetBareHandItem + GetInitialMetadata

Done (V3.1.0 b14 IL):
- Inventory.SetBareHandItem IL=23: bareHandItemValue/ItemClass + inventory
  data from CreateInventoryData(stack 1, gm, entity, 0).
- ItemClass.GetInitialMetadata IL=14: Actions[0].GetInitialMeta or 0.
## 2026-08-08 — tier-C: SetupStartingItems grant

Done (V3.1.0 b14 IL):
- EntityPlayerLocal.SetupStartingItems IL=39: itemsOnEnterGame granted to
  slots 1..N with GetInitialMetadata, holding index 0 (D8.6 step 8 consumer).
## 2026-08-08 — tier-C: CompleteEntity pref 44 correction

Done:
- CompleteEntity GUIHUDEntityName gate pref 44 = DebugMenuShowTasks (not an
  entity-name display pref); spawning.md §7 corrected.
## 2026-08-08 — tier-C: EntityAnimal distress loop

Done (V3.1.0 b14 IL):
- EntityAnimal.OnUpdateLive IL=57: see-cache clear, distress sound timer
  rand(min,max), animal waypoint update for local player.
## 2026-08-08 — tier-C: WorldTimeToElements

Done (V3.1.0 b14 IL):
- GameUtils.WorldTimeToElements IL=29: (day, hour, minute) = (wt/24000+1,
  (wt/1000)%24, (int)(wt*0.06)%60); noted in aidirector time gates.
## 2026-08-08 — census refresh 3

Done:
- Coverage.exe re-run: narrated 1496, catalogued 817, unaccounted 0.
## 2026-08-08 — tier-C: Stat.Tick regen + change flag

Done (V3.1.0 b14 IL):
- Stat.Tick IL=301: MaxPassive base, gain/loss passive clamp for
  Health/Stamina, regenAmount cap, food/water drain passives 127/119/126/120,
  UI regen, lastValue.
- Stat.SetChangedFlag IL=15: m_changed || floor(new)!=floor(old).
## 2026-08-08 — tier-C: Stat.set_Value + entity stat setters

Done (V3.1.0 b14 IL):
- Stat.set_Value IL=19: clamp 0..ModifiedMax + SetChangedFlag; EntityAlive
  set_Health/set_Stamina/set_Water one-line forwards (IL=7/6/6).
## 2026-08-08 — tier-C: Constants pins

Done (V3.1.0 b14 IL):
- Constants.cctor values pinned: cDefaultMonsterSeeDistance 48 (D8.6b),
  cDefaultPort 26900, cSendWorldTickTimeToClients 1.5,
  cItemDroppedOnDeathLifetime 300, cPlayerInteractDistance 5,
  cDigAndBuildDistance 4, cCollectItemDistance 2, cSneakDamageMultiplier 2,
  cMaxEntitiesPerMobSpawner 8.
## 2026-08-08 — tier-C: ItemClass.GetItem resolver

Done (V3.1.0 b14 IL):
- ItemClass.GetItem IL=13 / GetItemClass IL=15: nameToItem(case-insensitive)
  dicts -> ItemValue(class.Id) or None; noted in D8.6 hand item.
## 2026-08-08 — tier-C: entity tier calc + flags parse

Done (V3.1.0 b14 IL):
- EntityClass.CalculateEntityTier IL=49: tag priority elite/radiated/feral/
  special/strong -> EntityTierTypes 5..1 else Normal.
- ParseEntityFlags IL=49: comma OR of EntityFlags (ignore-case).
## 2026-08-08 — tier-C: EntityClass.Init config source

Done (V3.1.0 b14 IL):
- EntityClass.Init IL=1465 phase map (entity-ai D8.6b): censor, mandatory
  prefab + combined flag, mesh/gore paths, type resolution (classname,
  modelType EModelCustom), alt mats, particles, ragdoll, classification flags,
  lootDrops weighted normalize, sleeper senses defaults, MassKg *0.454,
  PhysicsBodyLayout.Find, damage model (dismember/knockdown/explosion mults),
  pain resist vec, AIPackages -> UseAIPackages, Buffs ';' list, Tags,
  explosionData, userSpawnType, token manager config, CalculateEntityTier.
## 2026-08-08 — tier-C: CreateEntityOperation.CompleteEntity

Done (V3.1.0 b14 IL):
- EntityFactory/CreateEntityOperation.CompleteEntity IL=639: asset load gates;
  prefab instantiate; player (local +Local/remote +GUIHUDEntityName,
  holding item, team, skin), item (EntityItem), falling block/group/tree
  paths; generic path (unknown class log, GUIHUD pref 44, collider layer 14,
  LargeEntityBlocker/Physics tags); convergence: ApplyToEntity, Delete source
  destroy, lifetime/id/pos/rot/onGround, scale/head size, PostInit.
## 2026-08-08 — tier-C: RemoveChunkObserver force pass

Done (V3.1.0 b14 IL):
- ChunkManager.RemoveChunkObserver IL=29: id-match remove + isInternalForceUpdate.
## 2026-08-08 — census refresh 2

Done:
- Coverage.exe re-run: narrated 1493, catalogued 820, classified 1386,
  unaccounted 0. completion-bar + handoff updated.
## 2026-08-08 — tier-C: survival-mode Init overrides

Done (V3.1.0 b14 IL):
- GameModeSurvival/MP/SP/PvP Init overrides: spawn window off, limits off,
  score mults 1/0/-5, spawn-near-other off, horde meter on, flying = pref 58,
  AutoParty off (survival); SP forces DropOnQuit 0, max players 1, not public,
  default port.
## 2026-08-08 — tier-C: GameModeAbstract.Init GameStats bootstrap table

Done (V3.1.0 b14 IL):
- Init IL=205 full GameStats <- GamePrefs seed table (53 rows) added to
  server-lifecycle §2.1: GS 24/23/15/20/18/37/59/60/61/42/72-76/51/53/35/33/34/
  39-41/43-50/63/54/66/68/71/57/62/65/67 <- matching prefs; GS 14/27/19/21/22/
  4/2/6 consts; GS 11 = 24000/(DayNightLength*60); GS 77-80 const 100.
## 2026-08-08 — tier-C: GameMode.StartRound per mode

Done (V3.1.0 b14 IL):
- Survival/Creative/Edit StartRound IL=4 = GameStats.Set(GameState, Running);
  Deathmatch IL=62 / ZombieHorde IL=53 = 4-state round-index switches
  (time/frag limits, LoadScene transitions).
## 2026-08-08 — tier-C: GameStateManager.InitGame mode instantiation

Done (V3.1.0 b14 IL):
- InitGame IL=50: GameState Running, mode from pref 29 type (default fallback)
  via Activator; GameModeId = GetID; server: round 0, timeRoundStarted,
  mode.Init + StartRound(0), bDirty.
## 2026-08-08 — tier-C: chunk data expiry + unload skip rules

Done (V3.1.0 b14 IL):
- Chunk.removeExpiredCustomChunkDataEntries IL=61: expire <= worldTime,
  OnRemove + key removal.
- World.UnloadEntities IL=36: backward unloadEntity(reason 1), skip
  bWillRespawn entities (or attached-main bWillRespawn) unless force.
## 2026-08-08 — tier-C: chunk load/unload lifecycle

Done (V3.1.0 b14 IL):
- Chunk.OnLoadedFromCache IL=90 (flags clear, saved entities -> entityStubs);
  OnLoad IL=97 (stub respawn via SpawnEntityAsync, layer OnLoad ->
  OnBlockLoaded, TE OnLoad); OnUnload IL=188 (async create WaitForComplete
  drain, UnloadEntities, TE OnUnload, RemoveBlockEntityTransforms, layer
  OnUnload -> OnBlockUnloaded, waterSimHandle.Reset).
- ChunkBlockLayer OnLoad/OnUnload IL=66 each (locked notifyLoadUnloadCallback
  Blocks fan-out).
## 2026-08-08 — tier-C: supply plane server motion

Done (V3.1.0 b14 IL):
- EntitySupplyPlane.SetDirectionToFly IL=12 (ticks, motion = dir*6, no
  replication) and OnUpdatePosition IL=49 (advance motion*partial, unload at
  0, plane loop sound, SetAirBorne).
## 2026-08-08 — tier-C: air-drop flight path build + plane spawn

Done (V3.1.0 b14 IL):
- AIAirDrop.CreateFlightPaths IL=355: cluster pick, altitude min(y+180,276),
  drop point 30-750, start/end ± (150-700)/2+(1500-2000)/2, FindSafePoint
  25/600, crate spacing length/n, crate y = plane-10 or ground+15,
  ClampToMapExtents 25, first crate re-aim, Delay = |start-drop|/120,
  ChunkObserver(3,-1), cluster.Delay += rand(25,120).
- AIAirDrop.SpawnPlane IL=74: supplyPlane entity at path.Start yaw Angle,
  SetDirectionToFly(dir, 20*(len/120)+10), SpawnEntityInWorld.
## 2026-08-08 — tier-C: air-drop flight-path pump

Done (V3.1.0 b14 IL):
- AIAirDrop.Tick IL=193: CreateFlightPaths first call; spawningCrates latch on
  chunk-loaded; per-path Delay -> SpawnPlane; per-crate Delay -> SpawnSupplyCrate
  + RemoveAt; done = flightPaths == null.
## 2026-08-08 — tier-C: air-drop crate landing tick

Done (V3.1.0 b14 IL):
- EntitySupplyCrate.OnUpdateEntity IL=103: parachute show/close countdowns 10,
  hide when (onGround||inWater) && close<=0; landing -> supply_crate_impact
  particle + SetSupplyCratePosition + RefreshCrates(-1) on server.
## 2026-08-08 — tier-C: sleeper disturbed level + ranged range

Done (V3.1.0 b14 IL):
- EntityAlive.GetSleeperDisturbedLevel IL=38: pct = dist/sightRangeBase; wake
  2 / groan 1 / 0 with Lerped threshold ranges.
- ItemActionRanged.GetRange IL=23: EffectManager.GetValue(MaxRange 11, base
  Range, holder).
## 2026-08-08 — tier-C: class-id + item-stack parse pins

Done (V3.1.0 b14 IL):
- EntityClass.FromString IL=3 = String.GetHashCode: entityClass ids in save/
  wire are .NET string hash codes (noted in entity-ai D8.6).
- ItemStack.FromString IL=38: "ItemName[=Count]", count default 1.
---
## 2026-08-08 — tier-C: chunk force-update + ground-align leaves

Done (V3.1.0 b14 IL):
- ChunkManager.IsForceUpdate IL=8 (isInternalForceUpdate || isChunkClusterChanged),
  ForceUpdate IL=4, GroundAlignFrameUpdate IL=42 (alternating 0/1 buckets,
  Block.GroundAlign per BlockEntityData).
---
## 2026-08-08 — tier-C: EnumGameState pinning

Done (V3.1.0 b14 IL):
- EnumGameState pinned (Off -1 / Loading 0 / Running 1 / Over 2): pause path
  sets GameState Over(2) / Running(1); vulture prologue ret on Over(2);
  inventory note added.
---
## 2026-08-08 — tier-C: EntityVulture helper leaves

Done (V3.1.0 b14 IL):
- StartAttackReposition IL=104 (fatigue 80-180 break vs reposition waypoint
  +3..7 y / -motion / 50% reverse), AttackAndAdjust IL=53 (attackDelay 18,
  motion 0.7/0.6, attackCount 5 or 0.25 -> reposition), FindTarget IL=69
  (BM no-LOS fallback; 80/lightMin 26; water 0.6 -> noisePlayer; health gate),
  IsCourseTraversable IL=102 (step bounds), StartHome IL=10, ClearTarget
  IL=11, AdjustWaypoint IL=46 (air probe, y <= 250).
---
## 2026-08-08 — tier-C: EntityVulture flight AI

Done (V3.1.0 b14 IL):
- EntityVulture.updateTasks IL=1344 full narration: prologue gates (pref 46,
  GameState 2, CheckDespawn), sleeper wake scan (disturbed >= 2), buffShocked ->
  Stun dive, revenge/attackTarget switch, state table Attack/AttackReposition/
  AttackStop/Home/Stun/WanderStart/Wander (enum pinned), home guard, move update
  4+rand(5), accel table by dir.y (0.35/0.95/0.55, BM 2.5, aggro/moveSpeed),
  gliding anim, talons strike + Voxel.Raycast 0.83 mask 1082198968, vomit
  attack2 (range, 20/25 deg gates, muzzle, numVomits -> reposition).
---
## 2026-08-08 — tier-C: activation command defaults/reorder

Done (V3.1.0 b14 IL):
- Entity.InitLocalActivationCommands base no-op; EntityAlive adds grab/hand when
  PickupItem != ""; drone adds full command table.
- Entity.ReorderActivationCommands base no-op; drone storage-after-heal,
  vehicle storage-after-horn (owner allowed).
- MoveActivationCommandAfter IL=64 reorder helper.
---
## 2026-08-08 — census refresh

Done:
- Coverage.exe re-run: narrated 1488 -> 1491, catalogued 822 -> 821,
  classified 1387, unaccounted 0. completion-bar + handoff census updated.
---
## 2026-08-08 — tier-C: GameStats/GamePrefs index tables

Done (V3.1.0 b14 IL):
- New inventory docs/inventories/gamestats-gameprefs.md: full EnumGameStats (82)
  + EnumGamePrefs (317) index tables; cross-checked against corpus usages
  (GS 25 IsSpawnNearOtherPlayer, GS 62 AllowedViewDistance, GS 71 SandboxCode,
  GP 190 ServerMaxAllowedViewDistance, GP 235 OptionsAutoPartyWithFriends, ...).
- Corrected GetViewDistance: pref 33 is GameWorld (not a graphics pref).
---
## 2026-08-08 — tier-C: SendChunksToClients streaming body

Done (V3.1.0 b14 IL):
- ChunkManager.SendChunksToClients IL=216: per-observer removes flush;
  loads capped at 3/tick with chunk-exists + !NeedsLightCalculation gate;
  reloads walked backwards; mapDatabase GetMapChunkPackagesToSend; flags 192.
- ResendChunksToClients IL=55: non-visual-mesh observers AddRange reload.
---
## 2026-08-08 — tier-C: DynamicProperties k=v parse format

Done (V3.1.0 b14 IL):
- DynamicProperties.ParseData IL=82: ';' split then '=' split (equalSeparator/
  semicolonSeparator statics); single k=v without ';'; error log partial dict.
- ParseKeyData IL=29: Data.TryGetValue -> ParseData; null when absent.
- D8.7 ParseTasks entry format corrected to `ClassName k1=v1;k2=v2`.
---
## 2026-08-08 — tier-C: EntityClass prop-name table + activation commands

Done (V3.1.0 b14 IL):
- New inventory docs/inventories/entityclass-props.md: 187 EntityClass Prop*
  statics from .cctor (IL=394) with literal values; class-id/tag statics noted.
- Corrected D8.7 AI task keys: AITask-1..N / AITarget-1..N (dash, not no-dash);
  D8.6a custom-command keys: CustomCommandName<i> etc. (not CustomCommand<i>).
- Entity.GetActivationCommands IL=51: cache + InitLocalActivationCommands +
  customCmds + ReorderActivationCommands.
---
## 2026-08-08 — tier-C: PlayerSpawnedInWorld full body

Done (V3.1.0 b14 IL):
- GameManager.PlayerSpawnedInWorld IL=127: id/entity/type guards; Died+remote
  SetAlive; Enter/JoinMultiplayer JoinedGame message; PlayerInteractions;
  waypoint refresh on NewGame/Loaded/Enter/Join (not Died/Teleport/Unknown);
  ModEvents.PlayerSpawnedInWorld + OnClientSpawned; log.
---
## 2026-08-08 — tier-C: base Entity config copy

Done (V3.1.0 b14 IL):
- Entity.CopyPropertiesFromEntityClass IL=238: RootMotion/HasDeathAnim/
  entityFlags; entityType enum default 0; lootDropProb/lootList; map/compass/
  tracker icons; isRotateToGround; customCmds from CustomCommand<i> 1..10 keys
  (commandId/icon/eventName/iconColor white|hex/activateTime -1|float/enabled);
  activation command cache reset fields.
- EntityPlayer override IL=3 pure base; EntityPlayerLocal IL=21 adds
  dropInventoryBlock key.
---
## 2026-08-08 — tier-C: ECD builder, chunk observer attach

Done (V3.1.0 b14 IL):
- EntityFactory.SetupEntityCreationData IL=31/36/12/10: ECD fill (itemStack,
  blockValues/textureFullArrays, lifetime, belongsPlayerId, spawnById/Name);
  defaults None/1/float.MaxValue/-1; (et,pos) overloads nextEntityID++.
  CreateEntity(ecd) = Start(true)+CompleteEntity; async = Start(false).
- ChunkManager.AddChunkObserver IL=15: ctor + m_ObservedEntities + 
  isInternalForceUpdate = true.
- PersistentPlayerList.GetPlayerDataFromEntityID IL=10: EntityToPlayerMap.
---
## 2026-08-07 — tier-C: spawn sampler, walk type, view distance

Done (V3.1.0 b14 IL):
- World.GetRandomSpawnPositionMinMaxToPosition IL=240: square (dx/dz
  -min..min, |max| gate) vs circle (unit-circle*range then +maxRange dir) modes;
  height+1, bedroll/CanMobsSpawn|CanPlayersSpawn/terrain/POI/water/land-claim
  rejects; isPositionFarFromPlayers; accept center + (0.5, terrainOffset+0.5).
- EntityAlive.GetSpawnWalkType IL=9: ParseInt WalkType prop default 0.
- GameUtils.GetViewDistance IL=10: pref 33 "Empty" -> 12 else GameStats 62.
---
## 2026-08-07 — tier-C: EAIManager AI task config parse

Done (V3.1.0 b14 IL):
- EAIManager.CopyPropertiesFromEntityClass IL=213: feralSense/groupCircle/
  noiseSeekDist/seeOffset; pathCostScale rand over AIPathCostScale (1,1);
  partialPathHeightScale = 1-pathCostScale (ASPPathFinder.Calculate xref);
  AITask string or AITask1..N keys -> tasks; AITarget / AITargetTask1..N ->
  targetTasks; CreateInstance/Init/SetData/AddTask.
- ParseTasks IL=111: pipe-delimited "ClassName [params]" entries, priority 1+.
---
## 2026-08-07 — doc structure pass: numbering, D-order, stability dump policy

Done:
- Fix duplicate section numbers: server-lifecycle (land-claim packages -> ##6,
  analytics -> ##7, EOS filters -> ##8), quests-challenges (criteria -> ##9,
  net packages -> ##10), managers 1.1b, save-region 1.1b; protocol-packages
  cross-ref updated to section 6.
- entity-ai.md: D8.5/D8.6 blocks moved after D8.4 (D8.1..D8.6 now in order);
  restored dropped D8.2b header; stray "D8.4 Sleeper wake" renamed to
  "Sleeper wake / stealth / triggers"; second "5.1b updateTasks" -> 5.1c.
- stability-dump: 12 raw IL dumps moved docs/stability-dump/ -> il/stability-v3.1.0/
  (git-ignored, aligns with AGENTS rule 1); stability.md links + INDEX dump-set
  row updated.
- Root junk dirs EnumGameStats/, Platform.DeviceFlag/ removed and gitignored.

Verification: make stock-check OK; test_dedi_coverage_docs OK; zero duplicate
numbered headers across docs/.
---
## 2026-08-07 — tier-C: CopyPropertiesFromEntityClass, pause state, disconnect path

Done (V3.1.0 b14 IL):
- EntityAlive.CopyPropertiesFromEntityClass IL=1128: hand item, faction, sight +
  sleeper thresholds, attack timeout/speed/jump/weight fields, sound table,
  itemsOnEnterGame (creative items skipped on device flag 56), fallBehaviors +
  destroyBlockBehaviors parse, distraction passives 65.
- GameManager.updatePauseState: Pause(false) on dedi; save-on-pause
  (SaveLocalPlayerData + SaveWorld); GameStats 0 2/1; timeScale 0/1.
- GameManager.PlayerDisconnected: dedi GC.Collect + MemoryPools.Cleanup;
  LastLogin/EntityId -1; NetPackagePersistentPlayerState reason 2 flags 192;
  SavePersistentPlayerData; DisconnectClient. HandlePersistentPlayerDisconnected.
- protocol.md post-spawn fix: spawn-near-friend mode 2 (InForest) accepts only
  BiomeType 2..3 (Forest/PineForest), not rejects; teamNumber local hard 0.
---
## 2026-08-07 — tier-C: DropContentOf TE + local inventory send + handoff

Done (V3.1.0 b14 IL):
- DropContentOfLootContainerServer lock/open/drop bag; CheckDestroyTileEntity.
- doSendLocalPlayerData/Inventory dirty flags; IsSafeToDisconnect; player count scan.
- FinishGameMessageServer mod interrupt flags 192; HandleFirstSpawnInteractions party invite.
- Handoff/TODO: workspace/notes/tierc-handoff.md
---
## 2026-08-07 — tier-C: SaveLocalPlayerData and RequestToSpawnEntityServer

Done (V3.1.0 b14 IL):
- SaveWorld World.Save; SaveLocalPlayerData FromPlayer + map async.
- RequestToSpawnEntityServer fallingTree dedupe; backpack AddDroppedBackpack.
---
## 2026-08-07 — tier-C: bedroll range and CanMobsSpawnAtPos

Done (V3.1.0 b14 IL):
- isPositionInRangeOfBedrolls GamePrefs 160; isPositionFarFromPlayers.
- GetTerrainOffset MarchingCubes; CanMobsSpawnAtPos y 2..251 trader/water/floor.
- SendToPlayers tracked set exclude.
---
## 2026-08-07 — tier-C: GetRandomSpawnPositionMinMaxToRandomPlayer

Done (V3.1.0 b14 IL):
- 10 tries unit-circle min..max band; height+1; bedroll/CanMobsSpawn/min-dist/CanSee rejects.
- Success center + terrainOffset.
---
## 2026-08-07 — tier-C: nextRound and DecoManager.UpdateTick

Done (V3.1.0 b14 IL):
- nextRound EndRound/wrap GameStats 10; SetBloodMoonDay GameStats 58 dirty.
- DecoManager.UpdateTick drain add/remove/rect/chunk queues.
---
## 2026-08-07 — tier-C: block ticker execute and GameStateManager gates

Done (V3.1.0 b14 IL):
- WorldBlockTicker.execute type-match UpdateTick; AddScheduledBlockUpdate replace hash.
- GameStateManager OnUpdateTick: time/day/frag gates; NetPackageGameStats dirty broadcast.
---
## 2026-08-07 — tier-C: WorldBlockTicker and SpawnManagerDynamic

Done (V3.1.0 b14 IL):
- tickScheduled max 100; reschedule 30..45 if chunk not area-loaded.
- tickRandom 1200 tick period; countPerFrame active/100.
- RestoreCulledBlocks edge face flags; SpawnManagerDynamic 64..96 night ES.
---
## 2026-08-07 — tier-C: updateChunksToUncull restore path

Done (V3.1.0 b14 IL):
- updateChunksToUncull: RestoreCulledBlocks; neighbor regenerate flags; 5 ms budget.
---
## 2026-08-07 — tier-C: WorldEventUpdateTime and POI uncull

Done (V3.1.0 b14 IL):
- WorldEventUpdateTime blood-moon day/hour window; BloodMoonParticipation.
- checkPOIUnculling every 38 ticks; GameStats 57; Overlaps radius 6.
---
## 2026-08-07 — tier-C: TickEntitiesSlice and SaveDecorations

Done (V3.1.0 b14 IL):
- TickEntitiesSlice advances tickEntityIndex; Flush drains remainder.
- TickEntities rebuilds list + EntityActivityUpdate path.
- SaveDecorations DecoManager.Save; AIDirector.AddEntity players only.
- Census pin narrated 1488 / catalogued 822.
---
## 2026-08-07 — tier-C: UpdateTick and GroupFallingBlocks

Done (V3.1.0 b14 IL):
- UpdateTick: elapsedTicks==0 slice path; partial*20; save 40 ticks / deco 60s.
- SetBlocksOnClients flags 192 except placer.
- GroupFallingBlocks BFS size-limited groups into fallingGroups.
---
## 2026-08-07 — tier-C: support pos and land claim offline hours

Done (V3.1.0 b14 IL):
- FindSupportingBlockPos elevator/blocked/supportOrder octant.
- AdjustBoundsForPlayers 50+80*pad clamp; IsLandProtectionValidForPlayer offline days.
- Chunk.GetEntitiesAround y buckets; FindRandomSpawnPointNearPlayer wrapper.
---
## 2026-08-07 — tier-C: Chunk player spawn and land claim bounds

Done (V3.1.0 b14 IL):
- Chunk.CanPlayersSpawnAtPos y 2..251; CanPlayersSpawnOn floor; solid/water reject.
- InBoundsForPlayersPercent 50+80 edge fade; IsLandProtectedBlock lpblock deadZone.
- GetPlayersAround / GetEntitiesAround chunk ring scan.
---
## 2026-08-07 — tier-C: spawn pos helpers and falling groups

Done (V3.1.0 b14 IL):
- CanPlayersSpawnAtPos chunk gate; FindRandomSpawnPointNearRandomPlayer dist 32.
- GetClosestLocalPlayer multi-local min dist; CheckEntityCollisionWithBlocks.
- CanPlaceLandProtectionBlockAt bounds 0.5 + claim scan; CreateFallingBlockGroup.
---
## 2026-08-07 — tier-C: Uncull and IsWorldEvent blood moon

Done (V3.1.0 b14 IL):
- UncullChunk queues culled chunks; UncullPOI AddChunksToUncull.
- GetTraderAreaAt DynamicPrefabDecorator; IsWorldEvent only event 0 blood moon.
---
## 2026-08-07 — tier-C: AddMotion and crouch height fixed update

Done (V3.1.0 b14 IL):
- AddMotion root-motion xz accumulate.
- Dropped backpack list helpers; ExecuteDestroyBlockBehavior stub false.
- CrouchHeightFixedUpdate elevator 1.3 / default 1.06; sphere-cast push; SetHeight.
---
## 2026-08-07 — tier-C: enclosure light and armor material

Done (V3.1.0 b14 IL):
- GetAmountEnclosed: 1 - max(blockLight y/y+1)/15.
- GetChestTransformPosition eyeHeight*0.25 crouch/stun else 0.95.
- GetArmorMaterial SurfaceCategory; impact graze/hit sounds; CameraFOV pref 16.
---
## 2026-08-07 — tier-C: eye height and block damage scale

Done (V3.1.0 b14 IL):
- GetBlockDamageScale BM vs entity percents.
- GetDropPosition parachute/jetpack up*0.3; GetEyeHeight crawler 0.15 / 22=0.6.
- CanCollideWithBlocks sleeping false; CanLockLocally dead false.
---
## 2026-08-07 — tier-C: block walk fall and ForceBigHead

Done (V3.1.0 b14 IL):
- updateCurrentBlockPosAndValue: stability-0 CanFallBelow AddFallingBlock; loot stage check.
- ForceBigHead HeadState 2; ForceResetHead; InitInventory ctor.
---
## 2026-08-07 — tier-C: GetActivatableItems MinEvent 91

Done (V3.1.0 b14 IL):
- GetActivatableItems: HasTrigger(91) on item and mods.
- DeathHealth/Died setters dirty bPlayerStatsChanged; PlayGiveUpSound.
---
## 2026-08-07 — tier-C: HoldingItem force and grab activation

Done (V3.1.0 b14 IL):
- set_IsBreakingBlocks dirties bPlayerStatsChanged when local.
- ForceHoldingWeaponUpdate HoldingItem S2C/C2S.
- EnqueueNetworkHoldingData queue; grab AllowActivationCommand bare-hand PickupItem.
- CollectActivatableItems holding + equipment slots.
---
## 2026-08-07 — tier-C: Electrocuted and stamina helpers

Done (V3.1.0 b14 IL):
- get/set Electrocuted via avatar remaining and StartAnimationElectrocute(0.6).
- AddStamina health gate; AddWater; HarvestingAnimation; simple field getters.
---
## 2026-08-07 — tier-C: CanNavigatePath and swim/ragdoll helpers

Done (V3.1.0 b14 IL):
- CanNavigatePath: ground/swim/elevator/climb only.
- CalcIfSwimming thresholds 0.5 air vs 0.7 grounded/jumping.
- BeginDynamicRagdoll; FaceJumpTo 90-degree snap; ApplySpawnState dismember.
- CalculateBlockDamage stompsSpikes tag 6 -> 999 bypass.
---
## 2026-08-07 — tier-C: AddEnemyToWorld and stealth UI percent

Done (V3.1.0 b14 IL):
- AddEnemyToWorld: source 3, passive sleeper, particle, optional WakeAttackLater.
- AddSpawnPoint cap 255; EntitySpawner runtime reset fields.
- PlayerStealth ValuePercentUI formula (light+noise+stress+smell+alert).
---
## 2026-08-07 — tier-C: destroy-pos reuse and jump headroom

Done (V3.1.0 b14 IL):
- GetExistingDestroyPos / FindExistingDestroyPos ally share within 20 m.
- CheckJumpBlocked headroom at y+2.35; CalcBlockedDistanceSq planar.
- IsTriggerAndNoRespawn flags&7==3; WakeAttackLater async iterator.
- BloodmoonZombiesRemain / IsMemberOfParty.
---
## 2026-08-07 — tier-C: BossEvent switch and package Process leaves

Done (V3.1.0 b14 IL):
- NetPackageBossEvent eventType 0..5 GameEventManager table.
- LandClaimRepair beginRepair server RepairAll vs client clear IsRepairing.
- BlockLimitTracking client-only; CloseAllWindows modal close; EmitSmell no-op.
---
## 2026-08-07 — tier-C: SearchForDestroyPos and GetAttackHitInfo

Done (V3.1.0 b14 IL):
- GetAttackHitInfo: 30% stun MassKg*0.4 else *0.2 ragdoll; damageMpy 0 null hit.
- IsABlockSideOpen: 4 cardinals movement blocked check.
- SearchForDestroyPos: destroyData patterns, column scan, open-side score.
---
## 2026-08-07 — tier-C: MoveHelper Push, area block, side-step

Done (V3.1.0 b14 IL):
- Push: MassKg*0.05 strength ragdoll type 3.
- CheckAreaBlocked edge fan; CalcObstacleSideStep arcs.
- SetSwimValues duration clamp 3..20; IsMoveToAbove 1.9; focusTicks 5.
---
## 2026-08-07 — tier-C: MoveHelper entity block, door open, attack push

Done (V3.1.0 b14 IL):
- CheckEntityBlocked sphere-cast layer 524288; radius sum +0.41 pad.
- CheckForDoorAndOpen: path door tag 2, unlocked TEFeatureDoor SetOpen.
- AttackPush: damage type 3 + Attack press/release.
- StartSwimStroke SetSwimValues; FindDestroyPos refresh 500; SelectBestHit 0.7.
---
## 2026-08-07 — tier-C: IsAlert and SetMoveTo path expiry

Done:
- get_IsAlert remote vs local; SetAlertTicks stores only.
- SetMoveTo path overload expiry 40 vs point 10; nextMoveToPos.
---
## 2026-08-07 — tier-C: CheckBlocked and CheckBlockedUp

Done (V3.1.0 b14 IL):
- CheckBlocked: ray cap, slope normal.y 0.643 / horizontal dot -0.7 skip,
  BlockedFlags baseY bit, tempMoveToPos.
- CheckBlockedUp: flags=4, obstacleCheckTickDelay=12.
---
## 2026-08-07 — tier-C: SetRevengeTarget and IsInFrontOfMe

Done:
- SetRevengeTarget: revengeTimer 500 when set.
- IsInFrontOfMe: half maxViewAngle cone.
- Recovered spawning.md after accidental wipe in bda930c (fix 2eff428).
---
## 2026-08-07 — tier-C: CalcPartyLevel and IsSpawnNeeded

Done (V3.1.0 b14 IL):
- CalcPartyLevel: sort stages; StartingWeight 1.0; DiminishingReturns 0.5; FloorToInt.
- ChunkAreaBiomeSpawnData.IsSpawnNeeded: missing group / under max / past delay.
---
## 2026-08-07 — tier-C: DigUpdate phase table

Done (V3.1.0 b14 IL):
- DigUpdate: digForTicks countdown; digActionTicks 18/4/14; move abort 0.25 sqr;
  DigTrigger then organic Hit type 3; digForwardCount 2; ray 1.1/1.4.
---
## 2026-08-07 — tier-C: StartJumpSwimMotion and KillLootContainer

Done (V3.1.0 b14 IL):
- StartJumpSwimMotion: water 0.65 gate; gravity/pow swim scale formula.
- IsWalkTypeACrawl: walkType >= 20.
- KillLootContainer: snap deathUpdateTime to linger-1 when corpse block present.
---
## 2026-08-07 — tier-C: trader eject teleport and dynamic ragdoll

Done (V3.1.0 b14 IL):
- checkForTeleportOutOfTraderArea: protect vs closed volumes, streak, NetPackageTeleportPlayer, game_on_trader_teleport.
- UpdateDynamicRagdoll / ActivateDynamicRagdoll flag bits 1/2/4, impulse x20.
---
## 2026-08-07 — post-update dry-run + tier-C crawler/SpawnParticle

Dry-run (live V3.1.0 b14 dedi):
- StockFacts extract matches committed stock_facts.json (0 field diffs).
- stock-check green.
- drift: baseline is stale vs live (expected until re-baseline after review);
  fixed ParitySurface stdout pollution so parity_diff no longer sees non-JSON.

Tier-C (IL):
- EntityHuman.TurnIntoCrawler: BoxCollider center/size, SetupBounds, no ladders.
- AvatarHumanController.TurnIntoCrawler: isCrawler, walkType 21, trigger.
- SleeperVolume.SpawnParticle: y+0.5, air-above skip, light brightness FX.
- UpdateSpawn correction: GameStats index 12 log-only, not a spawn gate.
---
## 2026-08-07 — layout: workspace/autoresearch + readiness make target

Done:
- Move root autoresearch session files into workspace/autoresearch/ (README, results.jsonl, run.sh).
- Remove empty accidental SleeperVolume/ dir; gitignore root dump mistakes and local caches.
- AGENTS.md layout table: tools/data, tools/tests, workspace subpaths.
- make readiness; tools/README points at workspace/autoresearch.

Verification: make stock-check; make readiness.
---
## 2026-08-07 — autoresearch: version-update tooling readiness

Done (branch autoresearch/version-update-tooling):
- Baseline readiness 83.04 → best 100.0 in 5 keep iterations.
- check_stock_facts: no fixed 3.1.0 soft accept paths (facts-driven only).
- tools/post-update.sh + make post-update; stock-sync STOCK_SYNC_DRIFT hook.
- stock_facts schema: update/pins/behaviour (Constants cctor extract).
- test_dedi_coverage_docs DUMP_SETS from stock_facts dump_label_suffix.
- Bench: tools/tests/bench_version_update_tooling.py; session autoresearch.md/jsonl.

Verification: make stock-check OK; test_dedi_coverage_docs OK; readiness=100.0.
---
## 2026-08-07 — tier-C: SetupCrawler and HeadshotMode

Done (V3.1.0 b14 IL):
- SetupCrawler: walkType 21; height 0.5; crawler hand item; TurnIntoCrawler.
- SetWalkType: crawler lock; before-crouch stash; avatar SetWalkType.
- IsCrippled flags 12288; HeadshotMode 1/2; CelebrateMode 1/2.
- Census pin narrated 1485 / catalogued 824.
---
## 2026-08-07 — tier-C: GetDismemberChance and ExecuteDismember

Done (V3.1.0 b14 IL):
- GetDismemberChance: primary mult head/arms/legs; passive 143; source*damagePer*mult; debug force.
- GetTotalPhysicalArmorRating: passive 41 then 163 penetration.
- ExecuteDismember: walkType 5 on cripple leg; DismemberLimb; SetupCrawler.
- BodyDamage leg/arm missing masks 480/510.
- sleepingOrWakingUp: IsSleeping only (name overclaims).
---
## 2026-08-07 — tier-C: CheckDismember crawler and Equipment.CalcDamage

Done (V3.1.0 b14 IL):
- GetDamageFraction: damage/maxHealth; Disintegrate: timeStayAfterDeath=0.
- CheckDismember: leg stun/sleep skip; chance roll; LegCrawlerThreshold; LegCrippleScale flags 4096/8192.
- Equipment.CalcDamage: physical armor rating vs passive 43 elemental.
- FireAttackedEvents: MinEvent type 8; buff-sourced uses Progression only.
---
## 2026-08-07 — tier-C: CalcIfInElevator and onNewBiomeEntered

Done (V3.1.0 b14 IL):
- onNewBiomeEntered: store biomeStandingOn.
- CalcIfInElevator: require bCanClimbLadders; sample stand block and y+1 IsElevator.
---
## 2026-08-07 — tier-C: updateCurrentBlockPosAndValue and radiation

Done (V3.1.0 b14 IL):
- updateCurrentBlockPosAndValue: air/child resolve; biome enter; elevator; walk buffs; OnEntityWalking.
- isRadiationSensitive: always true base.
- Census pin narrated 1484 / catalogued 825 / unaccounted 0.
---
## 2026-08-07 — tier-C: UpdateFall set_Crouching and aabb collision

Done (V3.1.0 b14 IL):
- UpdateFall: onGround triggers fallHitGround; airborne accumulates distance.
- set_Crouching: stance tag + _crouching cvar + avatar.
- ApplyFixedUpdate: physics RB position/rotation sync thresholds.
- aabbEntityCollision: ClipBoundsMove colliding bounds; onGround resolve.
- ConditionalScalePhysicsAddConstant: identity.
---
## 2026-08-07 — tier-C: entityCollision Move and crouch/climb

Done (V3.1.0 b14 IL):
- entityCollision: ragdoll fall track else CC or AABB.
- Move: AI-disable skip; absolute vs relative motion add with maxVelocity clamp.
- ConditionalScalePhysicsMulConstant: identity.
- IsCrouching: Crouching || CrouchingLocked; set_Climbing movement tags.
---
## 2026-08-07 — tier-C: JumpMove MaxVelocity and speed passives

Done (V3.1.0 b14 IL):
- JumpMove: collision then gravity; state3 full Gravity else *0.025 + 0.91 damp.
- MaxVelocity: 5.
- GetPassiveEffectSpeedModifier: crouch/run table passives 133-135 with Constants bases.
- ccEntityCollision: start/results; motionMultiplier when slowed.
---
## 2026-08-07 — tier-C: SetMovementState and MoveEntityHeaded

Done (V3.1.0 b14 IL):
- getNextStepSoundDistance: 1.5 m.
- SetMovementState: idle/walk/run/aggro by speed vs moveSpeed/moveSpeedAggro; strafe 1234 sentinel.
- internalPlayStepSound: water swim; material sides; passive 165 mute.
- MoveEntityHeaded: JumpMove/root motion/DefaultMoveEntity.
- DefaultMoveEntity: 0.91/0.546 friction; gravity*0.025; jump factor 0.163.
---
## 2026-08-07 — tier-C: OnUpdatePosition step/speed and fall stub

Done (V3.1.0 b14 IL):
- ExecuteFallBehavior: always false (stub).
- OnUpdatePosition: avg lastTickPos; step sound if unattached; local speed update.
- updateSpeedForwardAndStrafe: *0.5 decay; yaw-relative accumulate; SetMovementState.
- updateStepSound: distance/yaw budgets; internalPlayStepSound.
---
## 2026-08-07 — tier-C: ChooseFallBehavior and FallHitGround destroy

Done (V3.1.0 b14 IL):
- ChooseFallBehavior: height/difficulty filter; weighted pick; ExecuteFallBehavior.
- PlayHitGroundSound: volume Lerp(0.3,1,speed); land/thump/default.
- EAI FallHitGround: wake 0.8; destroy-area path 2.5 + UnreachablePercent; ally spread.
- SetMoveForward / WithModifiers speed and root scale.
---
## 2026-08-07 — tier-C: UpdateJump states and fallHitGround

Done (V3.1.0 b14 IL):
- UpdateJump: fly cancel; states 2 windup / 3 air / 4 land / 5-6 swim; jumpTicks 200/100.
- fallHitGround: distance>2 damage (-vy-0.85)*160; fall DamageSource; land anim; EAI FallHitGround.
---
## 2026-08-07 — tier-C: StartJumpMotion and DurationInSeconds

Done (V3.1.0 b14 IL):
- StartJump: jumpState 2 land / 5 swim; default distance 1; disable fall until ground.
- StartJumpMotion: ticks = 5+(jumpDistance*8)^0.5; motion from gravity and heightDiff.
- get_Jumping: passive 132 gate; EndJump land anim mode 1.
- DurationInSeconds: durationTicks/20.
---
## 2026-08-07 — tier-C: DigStop CalcMoveDist and BuffClass.Tick

Done (V3.1.0 b14 IL):
- DigStop: EndTrigger; ClearTempMove.
- CalcMoveDist/Temp: full 3D Euclidean to move targets.
- set_Jumping: StartJump/EndJump + movement tags; flags dirty.
- BuffClass.Tick: DurationTick; Finished when past DurationMax.
---
## 2026-08-07 — tier-C: DigStart DigUpdate and StartJump

Done (V3.1.0 b14 IL):
- DigStart: digActionTicks 18; DigStartTrigger; CanBreakBlocks gate.
- DigUpdate: move-away stop 0.5 m; DigTrigger; raycast break residual.
- StartJump: ground/elevator; not electrocuted; SetJumpDistance.
- ClearBlocked / ResetStuckCheck field clears.
- Census pin narrated 1483 / catalogued 826.
---
## 2026-08-07 — tier-C: Wandering TickNextTime and MoveHelper gates

Done (V3.1.0 b14 IL):
- Wandering Tick: playtest skip; TickActiveSpawns; TickNextTime horde.
- TickNextTime: stats 32/24; 28000 bootstrap; 7h other-horde push; StartSpawning.
- ChooseNextTime: bandit 12k-24k+2k; horde 12k-24k.
- UpdateMoveHelper: !IsActive/expiry/root-motion/dig/stun early structure.
---
## 2026-08-07 — tier-C: ClearParties and CalcNextDay

Done (V3.1.0 b14 IL):
- ClearParties: nextParty 0; clear parties; null player.bloodMoonParty.
- CalcNextDay: step = Frequency + Random(0..Range); walk last; optional seek keep.
- SetDay: GameStateManager.SetBloodMoonDay + log.
---
## 2026-08-07 — tier-C: Start/EndBloodMoon and KillPartyZombies

Done (V3.1.0 b14 IL):
- IsBloodMoonTime: GameUtils with dusk/dawn/bmDay.
- StartBloodMoon: ClearParties; clear IsBloodMoonDead; delay 0; enemies IsBloodMoon + stay/3.
- EndBloodMoon: override day; CalcNextDay; ClearParties; clear observer/horde/BM flags.
- KillPartyZombies: DecSpawnCount; Kill each; clear list; IsEmpty = no members.
---
## 2026-08-07 — tier-C: BloodMoonComponent.Tick and party ctor

Done (V3.1.0 b14 IL):
- Party ctor: BloodMoonHorde spawner; random spawnBaseDir; groupIndex -1.
- PlayerLoggedOut: RemoveMember keep ID; nextPlayer clamp.
- BloodMoonComponent.Tick: BM edge Start/End; stats 58/24; delay; party attach; round-robin Tick with delay=1/N.
- AIDirector.Tick: ComponentsTick + DebugTick.
---
## 2026-08-07 — tier-C: CreateNewParty and RemovePlayer pool

Done (V3.1.0 b14 IL):
- CreateNewParty: BloodMoonParty(player, component, BloodMoonEnemyCount).
- RemovePlayer: management Reset+Free; BM players list + all parties PlayerLoggedOut.
- AddMember/RemoveMember: members list + optional memberIDs hash.
---
## 2026-08-07 — tier-C: AIDirector AddPlayer and BM party join

Done (V3.1.0 b14 IL):
- AIDirector.Add/RemoveEntity: players only.
- AddPlayer -> PlayerManagement tracked state + BloodMoonComponent players list.
- AddPlayerToParty / TryAddPlayer: join within sqr 6400 (80 m) or CreateNewParty.
---
## 2026-08-07 — tier-C: NetEntityDistribution SEnts and Remove

Done (V3.1.0 b14 IL):
- SEnts table: Player/Vehicle infinite; Enemy/NPC 80; Item 64; Falling 120; Supply 1200; Turret 60.
- Add: type match -> entry; player updates all entries.
- Remove: reason 1 unload vs destroy packages; AIDirector.AddEntity players only.
---
## 2026-08-07 — tier-C: SpawnEntityInWorld and BuffValue ticks

Done (V3.1.0 b14 IL):
- SpawnEntityInWorld: map/Entities/chunk; EntityAlives; vehicle/drone/turret track; audio/weather/light; net Add; player list; AIDirector.
- BuffValue.DurationTick: updateRate gate; Tick -> BuffClass.Tick or Remove.
---
## 2026-08-07 — tier-C: DamageEntity consecutive 30 and resist bank

Done (V3.1.0 b14 IL):
- DamageEntity: type 26 limb cleanup; consecutive ignore 30 ticks non-Internal; FF; entityFlags&2 block; god.
- Passive 161 attacking-item bonus mult; passive 40 resist fraction into accumulatedDamageResisted.
---
## 2026-08-07 — tier-C: pathFollow radii and ImprovePath

Done (V3.1.0 b14 IL):
- pathFollow: arrive max(0.15/0.33/0.49, radius*0.6); swim 0.9/0.7; elevator dy 0.2; advance sq 0.04.
- ImprovePath: ProjectToGround all; first-step snap if dy < 0.6.
- IsPathUsageBlocked default false; hasHome max>=0; detachHome -1.
---
## 2026-08-07 — tier-C: CheckPath and moveSpeed passives

Done (V3.1.0 b14 IL):
- EAIManager.CheckPath: reject if any executing task IsPathUsageBlocked.
- GetSeeDistance: distance - seeOffset.
- GetMoveSpeed: night/BM passive 133 moveSpeedNight else 135 moveSpeed.
- GetMoveSpeedAggro: night/BM 134 aggroMax else 133 aggro; Panic always 134.
- ASP SetPath ImprovePath; UpdateNavigation pathFollow + SetMoveTo path.
---
## 2026-08-07 — tier-C: EAILeap SetMoveTo and RandomPositionGenerator

Done (V3.1.0 b14 IL):
- EAILeap.CanExecute: limb/blocked/path; leapDist 2.8..jumpMax; y band; clear ray.
- SetMoveTo: aggro speed; expiry 10 (pos) / 40 (path); Stop clears path.
- CalcInDir/Around swim retry; CalcAway 80 deg; CalcAround 30 air/home tries.
---
## 2026-08-07 — tier-C: DestroyArea ApproachSpot and Dodge

Done (V3.1.0 b14 IL):
- DestroyArea.CanExecute: CanBreakBlocks; unreachable/pathCostScale long-path gates; sample focus.
- ApproachSpot: investigate + supporting block; path 40+R20; scout AddLocationLine 32.
- Dodge: tag bounds + IsAnimationToDodge; look head first half.
- isWithinHomeDistance: max<0 always; else home distSq.
---
## 2026-08-07 — tier-C: BreakBlock AttackBlock and FindEnemy

Done (V3.1.0 b14 IL):
- AttackBlock: zombie ally +0.2 in 1.7x1.5x1.7; delay (0.25+r*0.8[+0.5 unreachable]+0.75)*20; hitDelegate.
- FindEnemy: type bounds by see distance; CanSee/stealth nearest.
- RunAway.Update: path end 1.21; pathTicks 60 FindPath.
---
## 2026-08-07 — tier-C: EAITarget.check Wander and Ranged CanExecute

Done (V3.1.0 b14 IL):
- EAITarget.check: home distance; optional CanSee; player CanSeeStealth.
- EAIWander.CanExecute: lookTime/stun/fade+120 ticks; executePercent; CalcInDir 90.
- EAIRangedAttackTarget: cooldown; IsAttackValid; limbs; InRange+CanSee; Update anim states UseHoldingItem.
---
## 2026-08-07 — tier-C: EAISetAsTargetIfHurt and Approach CanExecute

Done (V3.1.0 b14 IL):
- EAIApproachAndAttackTarget.CanExecute: sleep/stun/jump; targetClasses assignable + chaseTimeMax.
- EAISetAsTargetIfHurt: revenge type filters; 66% keep attack; else SearchRadius*0.35 investigate + clear revenge.
- CalcInvestigateTicks: ticks / passive 183 (self Tags).
---
## 2026-08-07 — tier-C: EntityActivityUpdate top-N and cloth radii

Done (V3.1.0 b14 IL):
- EntityActivityUpdate: clear aiClosest; assign closest player; sort; N=FastClamp(60/P,4,20).
- Scale bands 1.0 / 0.3 / 0.1 at 64/225; jiggle under 36.
- Cloth: 625 (25 m) / 3025 (55 m) when AimingGun; skip attached others.
---
## 2026-08-07 — tier-C: EntityDied ClearedUpdate and AddScore weights

Done (V3.1.0 b14 IL):
- NotifySleeperVolumesEntityDied: lock + EntityDied all volumes.
- EntityDied: remove respawnMap/list; ClearedUpdate if not spawning.
- ClearedUpdate: pref 88 days * 24000 -> respawnTime; wasCleared.
- GetMaxAttackTime: 10 ticks.
- AddScore: GameStats 28/29/30 weights; achievements 6/7/10/14; HandleClientDeath nop.
---
## 2026-08-07 — tier-C: ClientKill OnDeathUpdate FireEvent

Done (V3.1.0 b14 IL):
- NotifySleeperDeath: server sleeper -> NotifySleeperVolumesEntityDied.
- ClientKill: SetDead; Buffs.OnDeath crushing default; Progression.OnDeath; OnEntityDeath; celebrate passive 181.
- OnDeathUpdate: deathUpdateTime++; DeadBodyHitPoints force stay; particleOnDestroy.
- FireEvent: class Effects, Progression, challenges, inv, equip, Buffs.
- SetCVar: Buffs.SetCustomVar netSync true.
---
## 2026-08-07 — tier-C: SetRevengeTarget and AwardKill magnum

Done (V3.1.0 b14 IL):
- SetRevengeTarget: revengeTimer 500 when non-null.
- DamagedByEntity: EAIDestroyArea.Stop.
- SetStun/ClearStun: CurrentStun + _stunned cvar.
- Kill: NotifySleeperDeath; death sound; ClientKill.
- AwardKill: type 1/2 counters; magnum44 score flag 2; AddScoreServer.
---
## 2026-08-07 — tier-C: UseHoldingItem and path FindPath enqueue

Done (V3.1.0 b14 IL):
- UseHoldingItem: attack-anim gate; IsAttackValid; attack sound on release; attackingTime=60; ExecuteAction.
- AStar FindPath: Monitor lock + wait handle pulse; ASP FindPath: no lock overwrite.
---
## 2026-08-07 — tier-C: CanSee ray and Attack target-now

Done (V3.1.0 b14 IL):
- CanSee(Vector3): view cone + 0.2 origin pull; Voxel.Raycast clear LOS.
- CanSeeStealth: light threshold FastLerp by dist/sightRange.
- Attack: UseHoldingItem(0); timeout day/night; GetTargetIfAttackedNow range+0.3 and E_BP_/E_Vehicle.
---
## 2026-08-07 — tier-C: CheckDespawn source bands and IsAttackValid

Done (V3.1.0 b14 IL):
- CheckDespawn: remote/chunk-observer unload; 20-tick cadence; source 1/2/3 early and switch bands (48/80/96/128 m; 60/80/100/1800 ticks).
- IsAttackValid: electrocute/stun 1-2; attack prevented; painResist>=1 free; hasBeenAttackedTime gate; hit anim.
- GetAttackTargetLocal remote uses attackTargetClient.
---
## 2026-08-07 — tier-C: isBestTask MutexBits and OnUpdateEntity path

Done (V3.1.0 b14 IL):
- areTasksCompatible: MutexBits AND == 0.
- isBestTask: higher priority non-continuous blocks; incompatible lower/equal blocks.
- OnUpdateEntity: Buffs.Tick then OnUpdateLive then inventory; radiation damage residual.
- get_maxAlive: spawnGroup.maxAlive.
---
## 2026-08-07 — tier-C: GetAliveCount and BloodMoonParty.Tick

Done (V3.1.0 b14 IL):
- GetAliveCount: sum(groupCounts)-numSpawned+respawnMap.Count.
- FindLabel: command==2 name match.
- SetScaling: FastLerp(1,2.5,(s-1)/3).
- BloodMoonParty.Tick: updateDelay 1.8 SeekTarget; CanSpawn 1.9; +120 baseDir; min(3,members) spawn tries.
---
## 2026-08-07 — tier-C: MinScript.Tick opcodes and CalcBestDir bins

Done (V3.1.0 b14 IL):
- MinScript.Tick: sleep 0.05 steps; cmds 1 log, 2 nop, 3 loop, 4 sleep, 40 sound, 50 AddSpawnCount, 51 wait alive, 52 trigger.
- CalcBestDir: 16x22.5 deg; 9 samples; score (s+2)/3; *3 if within 60 of spawnBaseDir; random among max.
- InitParty IL=49 confirmed scaling path.
---
## 2026-08-07 — tier-C: IsPlayerATarget and MinScript.Run

Done (V3.1.0 b14 IL):
- IsPlayerATarget: dead/spawned/id; IgnoreAI; Level<=1 or IsBloodMoonDead reject.
- FindPartyTarget: reverse partyMembers nearest sqr among targets.
- MinScript.Run: store player/countScale; curIndex=0 sleep=0; IsRunning curIndex>=0.
---
## 2026-08-07 — tier-C: SeekTarget 1200 and SleeperVolume.Reset

Done (V3.1.0 b14 IL):
- SeekTarget: 150 m teleport/kill branch; 100 m SetAttackTarget 1200; else investigate 1200; lootDropProb=0 on cull.
- SleeperVolume.Reset: full field clear table + CancelPendingSpawns + minScript.Reset.
- Census pin narrated 1480 / catalogued 829 / unaccounted 0.
---
## 2026-08-07 — tier-C: UpdatePlayerTouched mult and SpawnZombie vulture

Done (V3.1.0 b14 IL):
- UpdatePlayerTouched: early return gates; quest SpawnMultiplier * difficultyTierScale; banditTag 0.2; default counts 5..6; minScript.Run.
- TriggerSleeperPose: pose!=5 physicsHeight 0.85; look dir from spawn; ResumeSleeperPose.
- Static padding chunk/trigger/unpadding; difficultyTierScale len 7.
- SpawnZombie IL=181: mounted 50% animalZombieVultureRadiated skips bonus loot; Astar 40.
---
## 2026-08-07 — tier-C: SleeperVolume.Spawn async and SetSleeper helpers

Done (V3.1.0 b14 IL):
- Spawn: pos +0.502/0.501; zombieArlene fallback; ExcludesWalkType fail; async create + pending maps; TickSpawnCount++.
- CompletePendingSpawns WaitForComplete; CancelPendingSpawns Destroy RootTransform.
- Despawn only sleeping respawnMap entities; DespawnAndReset = Despawn+Reset.
- SetSleeper pathCostScale+0.2; SetSleeperSight defaults; SetSleeperHearing 1/percent scale.
---
## 2026-08-07 — tier-C: CanSleeperSpawn floor/solid and CalcGameStageAround

Done (V3.1.0 b14 IL):
- Chunk.CanSleeperSpawnAtPos: below must collide; cell not collide/solid.
- CalcGameStageAround: players within 100 m same prefab; CalcPartyLevel.
- AddSpawnCount: RandomRange min..max fractional ceil; min>0 forces at least 1.
- RemoveSpawnAvailable: linear remove by index value.
---
## 2026-08-07 — tier-C: FindFathestSpawn and ResetSpawnsAvailable

Done (V3.1.0 b14 IL):
- FindFathestSpawnFromPlayers: max of min-player-dist among CanSleeperSpawnAtPos points.
- ResetSpawnsAvailable: skip spawnMode 2 unless infestedTag refresh.
- CanSleeperSpawnAtPos: chunk local CanSleeperSpawnAtPos.
- GetGameStageAround: CalcGameStageAround.
---
## 2026-08-07 — tier-C: SpawnPointIsHidden rays and stealth setters

Done (V3.1.0 b14 IL):
- SpawnPointIsHidden: center+0.5; pose5 offsets; per-player head rays layer 71; any clear LOS fails hidden.
- SetSmellRadiusTarget: radius/eating/sheltered; radius<0 clears.
- SetClientLevels + SetBarColor green/alert UI.
---
## 2026-08-07 — tier-C: SmellCountItems radius and EntityStealth bits

Done (V3.1.0 b14 IL):
- SmellCountItems: drag+inventory+bag ItemClass.Smell*count, min 50.
- SmellCountToRadius: (count-5)/45 Lerp 10..100.
- SetSmellEat: eatRadius+dist cap 100, ticks 1800.
- NetPackageEntityStealth: server smell-target vs crouch; client SetClientLevels.
---
## 2026-08-07 — tier-C: SmellUpdateItemsAndBlood wet and shelter

Done (V3.1.0 b14 IL):
- SmellTickWet: _wetnessrate cvar accumulates smellWet when >= 0.01.
- SmellClear: zero radius/eat/wet/sheltered fields.
- SmellUpdateItemsAndBlood: wet>=3 or dead clears; dysenterySmell -> SetSmellEat(35); items radius; shelter *0.2.
---
## 2026-08-07 — tier-C: CheckSleeperVolumeNoise and Attract/Smell ticks

Done (V3.1.0 b14 IL):
- CheckSleeperVolumeNoise: GameStats 24; y+0.1; per-volume CheckNoise.
- CheckNoise: hasPassives AABB pad 0.9; TouchGroup(null, true) unless mode 1.
- AttractTickServer: every 40 ticks stress cvar radius; 20% roll; attract timeout 80.
- SmellTickServer outline: radius ease, cvar smell, emit flags 6 every 40 ticks.
- FindNoise: noisySounds TryGetValue.
---
## 2026-08-07 — tier-C: NotifyNoise heat map and AddNoise sort

Done (V3.1.0 b14 IL):
- AddNoise: insert sorted descending by volume.
- NotifyNoise (PlayerStealth): duration*20 ticks; vol>=11 sleeper wait 20; soft cap 60+(v-60)^1.4; passive 88; sleeperNoiseVolume max 360.
- AIDirector.NotifyNoise: ignore enemies/decoys; crouch muffling; CheckSleeperVolumeNoise; heat NotifyActivity type 3 duration 240.
- OnSoundPlayedAtPosition -> NotifyNoise.
---
## 2026-08-07 — tier-C: CalcVolume noise formula and stealth light

Done (V3.1.0 b14 IL):
- CalcVolume: 0.6 successive decay, (sum*2.35)^0.86 * 1.5 * passive 88.
- NoiseCleanup: decrement ticks or RemoveAt.
- GetStealthLightLevel: y+1.68 sample + moving lights; selfLight out.
- BlockTrigger.OnTriggered: flag + Block.OnTriggered + clear values.
- SleeperVolume.OnTriggered: already D8.2b (triggerState + UpdatePlayerTouched).
---
## 2026-08-07 — tier-C: PlayerStealth.TickServer and PrefabTriggerData

Done (V3.1.0 b14 IL):
- SleeperWokeUp: zero all targetTasks executeTime.
- SleeperWakeup/PassiveChange Process: remote-only apply.
- TickServer: speedAverage, light crouch 0.6, cvars _lightlevel/_noiselevel, passive 89, lightLevel 0..200.
- PrefabTriggerData.Trigger: BlockTrigger.OnTriggered + SleeperVolume.OnTriggered by index.
---
## 2026-08-07 — tier-C: sleeper wake net and crouch detect

Done (V3.1.0 b14 IL):
- ConditionalTriggerSleeperWakeUp: clear sleep/passive; pose -1/-2; SleeperWokeUp; NetPackageSleeperWakeup 192.
- SetSleeperActive: clear passive only; NetPackageSleeperPassiveChange 192.
- CanSleeperAttackDetect: crouch Lerp(3,15,lightAttackPercent) distance gate.
- TriggerManager.TriggerBlocks: PrefabTriggerData for BlockTrigger/TriggerVolume.
---
## 2026-08-07 — tier-C: TouchGroup/Touch wake and GetClosestPlayerSeen

Done (V3.1.0 b14 IL):
- TouchGroup: same groupId fan-out Touch; solo Touch.
- Touch setActive: stealth detect wake+SetAttackTarget 400; trigger4 wake; wandering countdown 10.
- Touch !setActive: playerTouchedToUpdate, ticksUntilDespawn 900/200, respawnTime bump.
- CheckTrigger: unpadding vs triggerPadding; home delay +24000; UncullPOI.
- TriggerVolume.Touch: isTriggered + TriggerBlocks.
- GetClosestPlayerSeen: lightLevel >= lightMin and CanSee.
---
## 2026-08-07 — tier-C: CalcSenseScale FeralSense and volume CheckTouching

Done (V3.1.0 b14 IL):
- CalcSenseScale: FeralSense 1=day, 2=dark, 3=always -> 1 else 0.
- SleeperVolume.CheckTouching: y+0.8; hasPassives pad 0.3; trigger pad 0.1; TouchGroup.
- TriggerVolume.CheckTouching: y+0.8 strict AABB then Touch.
- GetClosestPlayer: distMax<0 => inf; dead match + Spawned; min distSq.
---
## 2026-08-07 — tier-C: GetSeeDistance senseScale and DetectUsScale

Done (V3.1.0 b14 IL):
- GetSeeDistance: sleeperSightRange vs sightRangeBase * (1 + CalcSenseScale*feralSense).
- DetectUsScale: 0.3 after 60s in DifficultyTier>=1 prefab vs Dynamic EntityEnemy.
- IsInViewCone: sleeperLookDir/sleeperViewAngle vs look vector.
- CheckSleeperVolumeTouching: GameStats 24 gate; chunk sleeper list + lock.
- CheckTriggerVolumeTrigger: chunk trigger list + lock (no EnemySpawnMode gate).
---
## 2026-08-07 — tier-C: FriendlyFireCheck PvP modes and CanEntityBeSeen

Done (V3.1.0 b14 IL):
- EntityPlayer.FriendlyFireCheck: GameStats 23 modes 0/1/2 ally/stranger gates.
- CanEntityBeSeen: see distance * DetectUsScale, view cone, ray mask -1612492829.
- CheckSleeperTriggers: sleeper + trigger volumes on server alive players.
- EntityAlive.HasImmunity always false.
---
## 2026-08-07 — tier-C: HasImmunity passive 197 and CanSee caches

Done (V3.1.0 b14 IL):
- HasImmunity: dead+RemoveOnDeath; parent HasImmunity; passive 197 roll; infection InfectionChance.
- CanSee: positive/negative HashSet caches; CanEntityBeSeen; client-controlled updates lastTimeSeenAPlayer.
- Base FriendlyFireCheck always true (IL=2).
---
## 2026-08-07 — tier-C: AddBuff BuffStatus gates and ResetDespawnTime

Done (V3.1.0 b14 IL):
- AddBuff IL=238: status 0 success, 1 unknown, 2 immune, 3 FF, 4 editor, 5 gamestat; stack event 4.
- Despawn/ForceDespawn; ResetDespawnTime clears ticksNoPlayerAdjacent + seeCache seen time.
---
## 2026-08-07 — tier-C: CheckDespawn distance/timer bands

Done (V3.1.0 b14 IL):
- CheckDespawn every 20 ticks: 130/20 m far-flag; bands 48/80/96/128 m with 60/80/100/1800 tick timers.
- EntityEnemy.canDespawn: horde zombies stay while players online.
---
## 2026-08-07 — tier-C: CalcSpawnPos and unloadEntity pipeline

Done (V3.1.0 b14 IL):
- CalcSpawnPos: radius yaw ±45°; GetMobRandomSpawnPosWithWater 0/10/30.
- MarkToUnload: EntityAlive copies timeStayAfterDeath -> deathUpdateTime.
- unloadEntity: delegates, OnEntityUnload, dict/map/chunk, vehicle/drone/turret, NED/path/AIDirector.
- RemoveBuff: mark Remove + optional RemoveBuffNetwork.
---
## 2026-08-07 — tier-C: SeekTarget kill gates and OnEntityUnload

Done (V3.1.0 b14 IL):
- SeekTarget: 60 m no-player kill; 150 m / 70 m repath; 50% DecSpawnCount kill.
- OnEntityUnload: OcclusionManager + clear navigator/look/move/see.
- RemoveEntity MarkToUnload+unloadEntity; EntityRemove Process always RemoveEntity.
- BuffClass.canRun Requirements.IsValid.
---
## 2026-08-07 — tier-C: BuffClass.FireEvent canRun and StartSequence

Done (V3.1.0 b14 IL):
- BuffClass.FireEvent: Effects null / canRun gate then MinEffectController.FireEvent.
- StartSequence: StartTime = Time.time only.
---
## 2026-08-07 — tier-C: EntityBuffs.Tick MinEvent order

Done (V3.1.0 b14 IL):
- Tick: Invalid drop; Finished->event 2; Remove->event 3; Start event 0; Tick; Update event 1.
- FireEvent skips paused; CanExecute Requirements.IsValid or true.
---
## 2026-08-07 — tier-C: interest enter package order

Done (V3.1.0 b14 IL):
- updatePlayerEntity enter: Spawn, AliveFlags, PlayerStats/Twitch/Equipment, Speeds, optional Velocity.
- Census pins: narrated 1479 / catalogued 830 / unaccounted 0.
---
## 2026-08-07 — tier-C: explode ExplodeGroup delay and FrameUpdate

Done (V3.1.0 b14 IL):
- explode: ExplodeGroup delay=3; IsExplosionAffected fallings; heat map OnSoundPlayedAtPosition.
- ExplodeGroupFrameUpdate: budget max(1,min(n,20*0.73^n)); DropItems 0.5; fallingBlock velocity.
---
## 2026-08-07 — tier-C: AttackEntites body mult and DamageRecord

Done (V3.1.0 b14 IL):
- AttackEntites: passives 20/21/22; Legs/Head/ChestExplosionDamageMultiplier; DamageRecord sum.
- Apply: DismemberChance 0.5; damage vs 0.1 maxHealth; center sqr 0.67; stun bands 0.6/0.85.
---
## 2026-08-07 — tier-C: LootDropPick weighted and OnBlockStartsToFall

Done (V3.1.0 b14 IL):
- LootDropPick: <2 entries -> [0]; else cumulative weight RandomFloat pick entityClass.
- OnBlockStartsToFall base: SetBlockRPC Air; tree/composite overrides.
---
## 2026-08-07 — tier-C: DropBagServer lootDrops vs bag

Done (V3.1.0 b14 IL):
- DropBagServer: server-only; y+0.9; class lootDrops pick OR DroppedLootContainer from bag.
- quests BlockDestroyed changelog pin; dropItemOnDeath passive 80 already committed.
---
## 2026-08-07 — tier-C: dropItemOnDeath passive 80 and BlockDestroyed

Done (V3.1.0 b14 IL):
- dropItemOnDeath: passive 80 scales lootDropProb from killer hold; * LootBagChance; DropBagServer roll.
- BlockDestroyed: BlockDestroy event; HandleTrigger via closest player within 500 m.
---
## 2026-08-07 — tier-C: GetCountMultiplier enum and BM weather defer

Done (V3.1.0 b14 IL):
- GetCountMultiplierFromSandbox: types 1..11 map to count modifiers; else -1.
- CalcGlobalWeatherType: bloodMoon + push stormWorldTime by 5000 when near.
---
## 2026-08-07 — tier-C: RandomCountFromSandboxTags category table

Done (V3.1.0 b14 IL):
- RandomCountFromSandboxTags: food/drink/ammo/medical/junk/armor/melee/ranged/dukes/mag/books modifiers.
- RandomCountFromSandbox: abundanceType mult then RandomSpawnCount.
---
## 2026-08-07 — tier-C: GetSandboxProb and RandomSpawnCount

Done (V3.1.0 b14 IL):
- GetSandboxProb: treasureTags -> TreasureMapChance else 1.
- RandomSpawnCount: RandomRange(min-0.49,max+0.49)*abundance with frac ceil.
---
## 2026-08-07 — tier-C: getProbability and SpawnLootItemsFromList

Done (V3.1.0 b14 IL):
- getProbability: requirements, lootProbTemplate stage bands, passive 79, GetSandboxProb.
- SpawnLootItemsFromList: numToSpawn -1 all, weighted unique pick, sandbox counts.
- MemberCountInRange: other members Distance < GameStats 54.
---
## 2026-08-07 — tier-C: party highest loot stage wrappers

Done (V3.1.0 b14 IL):
- GetHighestPartyLootStage -> Party.GetHighestLootStage max over members.
- GetHighestLootStage: max GetLootStage(containerMod, containerBonus).
---
## 2026-08-07 — tier-C: GetLootStage POI/biome formula

Done (V3.1.0 b14 IL):
- GetLootStage: POITierMod/Bonus, biome LootStageMod/Bonus/Min/Max, passives 159/160, GameStats 66 clamp, GlobalLootStageModifier.
- SharedPartyKill: server SharedKillServer scale 1; client SharedKillClient.
- EntityAddExpServer: AddLevelExp only when isEntityRemote with _xpOther type 8.
---
## 2026-08-07 — tier-C: get_gameStage formula and GameStage statics

Done (V3.1.0 b14 IL):
- EntityPlayer.get_gameStage: daysLived clamp to Level, biome/quest mods, passive 157, GlobalGameStageModifier.
- GameStageDefinition.cctor: DifficultyBonus=1, StartingWeight=1, DiminishingReturns=0.5, DaysAliveChangeWhenKilled=2.
---
## 2026-08-07 — tier-C: CalcPartyLevel diminishing returns and setState

Done (V3.1.0 b14 IL):
- CalcPartyLevel: sort, weighted sum high-to-low with StartingWeight/DiminishingReturns.
- CalcStageSpawnMax: sum group spawnCounts.
- checkTeleportPos 32 m success log; setState lastState + owned clear + heal clear.
- CanSpawn named EnemyCount / MaxSpawnedZombies.
---
## 2026-08-07 — tier-C: CanSpawn cap, SetPartyLevel scaling, teleportState

Done (V3.1.0 b14 IL):
- CanSpawn: GameStats 12 < GamePrefs 99 * priority.
- SetPartyLevel: gsScaling; GetStage uses unscaled arg; bonusLootEvery.
- ModifySpawnCountByGameDifficulty: EnemySpawnMode off -> 0 only.
- teleportState: Teleport state, closest free group slot, Idle.
- targetCanBeHealed / isTargetBleeding; empty exitAttack/onHealDone.
---
## 2026-08-07 — tier-C: SetupGroup and heal type priority

Done (V3.1.0 b14 IL):
- SetupGroup: interval, nextStageTime=worldTime+duration*1000, difficulty-scaled numToSpawn.
- ResetPartyLevel: CalcPartyLevel then optional mod remainder.
- findNeededHealType: types 2/3/4 priority for medical vs bleeding.
- TeleportOutOfRange: exit attack/heal then teleportState.
---
## 2026-08-07 — tier-C: drone weapon Fire paths and PartySpawner Tick

Done (V3.1.0 b14 IL):
- MachineGunWeapon: passives 16/11/199/200/9/7, raycast Hit, ammo, UseTimes.
- StunBeam: _droneStunDamage quality cvar + buffShocked.
- HealBeam: inventory UseOther action1 + buffJunkDroneHealCooldownEffect.
- AIDirectorGameStagePartySpawner Tick/canSpawn/IncSpawnCount; isValidDronePos NaN.
---
## 2026-08-07 — tier-C: AIHordeSpawner.Tick and Weapon cooldown

Done (V3.1.0 b14 IL):
- AIHordeSpawner.Tick IL=228: party init, day 45/55/45 night 55/70/55, one spawn/tick, investigate 2400.
- Weapon.Fire stores target + RefreshCooldown (actionTime+cooldown).
- VehicleDataSync Process: ReadSyncData; server GetSyncFlagsReplicated + SendPackage 192.
---
## 2026-08-07 — tier-C: scout Update finish, Horde.Tick, drone CanAttack

Done (V3.1.0 b14 IL):
- AIScoutHordeSpawner.Update finish: no players or SpawnUpdate done + empty horde.
- SpawnUpdate: AttackDelay=2, IsHorde/Scout/chunkObserver flags, 6000 investigate.
- Horde.Tick: _destroy or nested AIHordeSpawner finish/Cleanup.
- CanAttack bans Heal/Attack/Shutdown; Weapon.canFire = cooldown<=0.
- updateTransitionState heal server path and cooldown refresh.
---
## 2026-08-07 — tier-C: TickActiveSpawns drain and heal medical gate

Done (V3.1.0 b14 IL):
- TickActiveSpawns reverse scout/horde lists; HasAnySpawns = horde only.
- CheckToSpawn FIFO one chunk per 5 s pulse.
- HealBeamWeapon need: max-HealDamageThreshold or <0.67 ModifiedMax; medicalRegHealthAmount==0.
- IsAttackValid: activeWeapon.canFire.
---
## 2026-08-07 — tier-C: drone group slots and follow repath

Done (V3.1.0 b14 IL):
- GetGroupPositions: 5 horizontal slots from chest/look; ScanVolume fallback.
- DoMoveIntoFollowPos: GetPath when empty; repath seekDist+1 / +1.414; success dist.
- TickPlayerState: Dead mirror only from Player.IsDead.
---
## 2026-08-07 — tier-C: investigate pos and neighbor cooldown delays

Done (V3.1.0 b14 IL):
- Set/ClearInvestigatePosition; alert ticks (20-35)*20, zombie half.
- StartNeighborCooldown 180/720 s; SetLongDelay 1320 s; drone underwater surface seek.
---
## 2026-08-07 — tier-C: trackTarget ranges, canHitEntity, FindScoutStartPos

Done (V3.1.0 b14 IL):
- trackTarget chest/head lerp + yaw/pitch range gates.
- canHitEntity raycast E_ tag must match target.
- FindScoutStartPos 80 m ring, 15 tries, 30 m player avoid; neighbor cooldown grid.
---
## 2026-08-07 — tier-C: turret ignore flags, Fire ammo, spawnHordeNear

Done (V3.1.0 b14 IL):
- shouldIgnoreTarget: ally/party/owner/stranger/enemy flags; always skip traders/turrets/drones.
- Fire: passives 16/11, rayCount Hit path, AmmoCount--, UseTimes.
- spawnHordeNear: CreateHorde, base 5, 12% reduce, SpawnMore; healTargetServer.
---
## 2026-08-07 — tier-C: scout horde update and drone state IL

Done (V3.1.0 b14 IL):
- Scout SpawnUpdate: CanSpawn, investigate 6000 ticks, random pos radius 6.
- UpdateHorde: AttackDelay 18s, investigate 2000/6000, spawnHordeNear.
- Drone idle/follow/sentry distance gates; MiniTurret findTarget raycast.
---
## 2026-08-07 — tier-C: chunk activity decay and liquid Flow/Evap packing

Done (V3.1.0 b14 IL):
- AddEvent merges same-type Value; DecayEvents proportional; best event cooldown 240s.
- Evap damage 0..45; Flow = damage-50; PhysicsWakeNear 20 m wake.
---
## 2026-08-07 — tier-C: liquid ChangeThis pack and SpawnScouts bands

Done (V3.1.0 b14 IL):
- ChangeThis: rotation 8, meta2 emissions, damage=evap+flow, WBT 60/1/1000.
- CheckUpdate rate limit; CheckDeepWater 6-stack; NotifyEvent checkChunks.
- SpawnScouts 120 m player, Scouts1/2/Feral/Radiated by gamestage.
---
## 2026-08-07 — tier-C: NotifyActivity gates and liquid Emissions/ChangeToAir

Done (V3.1.0 b14 IL):
- NotifyActivity: GameStats 32/24, heat mod, skip BM/Twitch; chunk NotifyEvent.
- CheckToSpawn: ActivityLevel 25, 20% SpawnScouts + neighbor cooldown.
- BlockLiquidv2 Emissions rotation/meta2; ChangeToAir splash+WBT; HasHoles.
---
## 2026-08-07 — tier-C: PlantGrowing, TorchHeatMap, WorldBlockTicker execute

Done (V3.1.0 b14 IL):
- PlantGrowing lightLevelGrow, CanGrowOn, biome type remap, meta grow-on-top.
- TorchHeatMap AIDirector.NotifyActivity enum 6 strength*0.4 duration 720.
- WBT execute type-match; AddScheduled replace; Chunk.UpdateTick TE-only.
---
## 2026-08-07 — tier-C: DecoManager.UpdateTick thread queues and ring

Done (V3.1.0 b14 IL):
- Drain add/remove/reset queues under lock; checkDelayTicks reset to 20.
- Player deco-chunk ring via GamePrefs 173; start UpdateDecorationsCo.
---
## 2026-08-07 — tier-C: Chunk.SetBlockRaw silent write path

Done (V3.1.0 b14 IL):
- SetBlockRaw IL=386: y>=255 air, water flow, IndexedBlocks, heightmap, tickedBlocks.
- Dirty flags bMapDirty/isModified/bEmptyDirty; no light/mesh/stability RPC.
---
## 2026-08-07 — tier-C: IsLandProtectedBlock and map-edge soft bounds

Done (V3.1.0 b14 IL):
- IsLandProtectedBlock: primary lpblock, deadZone, self allow, ally keystone flag.
- InBoundsForPlayersPercent: edge inset 50 / span 80, min axis, threshold 0.5.
---
## 2026-08-07 — tier-C: World.CanPlaceBlockAt claim and trader gates

Done (V3.1.0 b14 IL):
- CanPlaceBlockAt: trader area, InBoundsForPlayersPercent 0.5, GameStats 1/44 claim ring.
- CanPickupBlockAt: trader deny then CanPlaceBlockAt(traderAllowed=false).
---
## 2026-08-07 — tier-C: getMaxStabilityAround and vehicle attach

Done (V3.1.0 b14 IL):
- getMaxStabilityAround: AllDirections, StabilitySupport max, bFromDownwards.
- ChangeStability recursive stab-1 with non-support cap 1.
- TurretTracker.Update save every 120s; Attach/Detach seat pose and driver flags.
---
## 2026-08-07 — tier-C: Stability queueStabilityAvail cap 200

Done (V3.1.0 b14 IL):
- BlockPlacedAt enqueues avail recompute only when queue count < 200.
- BlockRemovedAt neighbor re-queue uses the same 200 hard cap.
---
## 2026-08-07 — tier-C: FallingBlock crush damage and land drops

Done (V3.1.0 b14 IL):
- AddFallingBlock dedupe/stability/oversized gates; OnBlockStartsToFall -> Air.
- FallingBlock/Blocks hit damage min(40, massKg*-vy*0.05)*passive 164, max 3 hits.
- Land: vel^2 < 0.0625; DropItemsOnEvent; SetDead.
---
## 2026-08-07 — tier-C: updateTasks freeze and GroupFallingBlocks BFS

Done (V3.1.0 b14 IL):
- updateTasks GamePrefs[46] freeze (non-drone); aiActiveDelay LOD; path apply order.
- EAIManager interestDistance FastMoveTowards(10, 1/120).
- GroupFallingBlocks 6-neighbor BFS size clamp; CreateFallingBlockGroup spawn.
---
## 2026-08-07 — tier-C: EAI BreakBlock/Wander/RunAway/Ranged/FindTarget leaves

Done (V3.1.0 b14 IL):
- EAIBreakBlock ally damageBoost +0.2 and attack delay formula.
- EAIWander CanExecute 120 no-player / executePercent / CalcInDir 90.
- EAIRunAway path end 1.21 and pathTicks 60; panic speed subclasses.
- EAIRangedAttackTarget look/SeekYaw then UseHoldingItem state machine.
- FindTarget see-distance, breadcrumb 15/24, bounds expand +4.
---
## 2026-08-07 — tier-C: EAIApproachAndAttackTarget Update phases

Done (V3.1.0 b14 IL):
- Home return FindPath 0.8 aggro, homeTimeout 0.05, give-up + sleeper pose.
- Relocate/target vel EMA; eat DamageEntity 35; chase FindPath + CanSee look.
- CanExecute sleep/stun/jump-swim and targetClasses chaseTimeMax.
---
## 2026-08-07 — tier-C: DropItemsOnEvent and PartyQuestChange

Done (V3.1.0 b14 IL):
- DropItemsOnEvent IL=246 drop table, stick place vs ItemDropServer, scrap half.
- PartyQuestChange fan-out; HandlePlayer location rect or 15 m; ChangeStatus.
---
## 2026-08-07 — tier-C: EntityItem OnUpdateEntity lifetime and collect

Done (V3.1.0 b14 IL):
- OnUpdateEntity: lifetime -= 0.05, ground counter 10, distraction/Y death.
- OnCollectServer: RemoveEntity reason 2 only.
---
## 2026-08-07 — tier-C: AddKillXP and SharedKillServer party XP split

Done (V3.1.0 b14 IL):
- AddKillXP: ExperienceValue, passive 193, modifier, GetPartyXP, _xpFromKill.
- SharedKillServer: same base XP; other members within GameStats[54]; _xpFromParty.
- Killer skipped in SharedKill loop; SharedKillClient quest EntityKilled hook.
---
## 2026-08-07 — tier-C: console 300-char reject, EntityAliveFlags bits

Done (V3.1.0 b14 IL):
- ServerConsoleCommand rejects cmd length > 300 before resolve; deny msgServer25.
- EntityAliveFlags Process bit setters corrected (god DataItem, alert remote-only).
---
## 2026-08-07 — tier-C: LockRequestServer 5-target cap and lock maps

Done (V3.1.0 b14 IL):
- LockRequestServer IL=239: stale unlock, max 5 targets, single vs shared maps.
- CanLockOnServer gate; OnLockedServer; NetPackageLockResponse flags 192.
- ForceUnlockLockTarget walks single+shared holders and force-unlocks.
---
## 2026-08-07 — tier-C: EntityTrader OnUpdateLive + DropContent multi-bag

Done (V3.1.0 b14 IL):
- EntityTrader.OnUpdateLive IL=315 quest list, 10m bounds unload/greet, open-close.
- DropContentInLootContainerServer multi-bag by loot container size, y+0.25.
---
## 2026-08-07 — tier-C: GetLandClaimOwner self/ally/other + offline hours

Done (V3.1.0 b14 IL):
- Outer GetLandClaimOwner GameStats[1] off / trader area / claim size GameStats[44].
- Per-chunk lpblock primary TEFeatureLandClaim; deadZone half-extent.
- Enum self=1 ally=2 other=3; IsLandProtectionValidForPlayer GameStats[46]*24h.
---
## 2026-08-07 — tier-C: MinEvent GiveExp, loot override, rage, jam

Done (V3.1.0 b14 IL):
- GiveExp/GiveSkillExp AddLevelExp + dirty flags; SetProgressionLevel max/-1.
- AwardChallenge/QuestStat EntityPlayerLocal only via QuestEventManager.
- SetItemInSlot armor EquipSlot gate; ResetHeldItem; SetHeldItemJammed metadata.
- Rage StartRage/StopRage on EntityHuman; SetOverrideLoot server comma list.
---
## 2026-08-07 — tier-C: full UAI task Start+Update table (5 types)

Done (V3.1.0 b14 IL):
- Enumerated all concrete UAITask* types (only 5).
- Start+Update for MoveToTarget, Wander, AttackTargetEntity/Block, FleeFromTarget.
- Flee sets home area radius 10 on path end; Attack dual Attack(false/true) pattern.
---
## 2026-08-07 — tier-C: EntityStatChanged, StatsBuff, TE Process, QuestObjective

Done (V3.1.0 b14 IL):
- EntityStatChanged Process IL=88 self-echo skip, Health FireEvent 9, rebroadcast.
- EntityStatsBuff Process IL=76 remote Buffs.Read + server flags 192 fan-out.
- NetPackageTileEntity Process IL=103 teBlockId drop + stream mode + rebroadcast.
- QuestObjectiveUpdate eventType 0/1/2; HandlePlayer distance 15 treasure count.
---
## 2026-08-07 — tier-C: sleeper TickSpawnCount, CheckSpawnPos, HandleFuel re-pin

Done (V3.1.0 b14 IL):
- TickSleeperVolumes zeros TickSpawnCount under lock; Tick gates UpdateSpawn <2.
- CheckSpawnPos chunk readiness; FindSpawnIndex hidden + farthest fallback.
- HandleFuel: not-burning early return; 0.01s quantize; fuel[0] consume path.
- Corrected mid-wave restart: vanished mapped entity (GetEntity null), not live.
---
## 2026-08-07 — tier-C: damageEntityLocal, ProcessDamage, EffectManager.GetValue

Done (V3.1.0 b14 IL):
- damageEntityLocal IL=484 DR build (armor, dismember, StunProne/Knee thresholds).
- ProcessDamageResponse IL=86 net fan-out; ProcessDamageResponseLocal IL=903.
- EffectManager.GetValue IL=372 stack; ItemValue.FireEvent IL=107 recursion.
---
## 2026-08-07 — tier-C: GameTimer formula, ThreadManager drain, Astar merge 76

Done (V3.1.0 b14 IL):
- GameTimer.updateTimer IL=74 stopwatch/timeScale/ticksPerSecond formula.
- ThreadManager.UpdateMainThreadTasks double-buffer swap + invoke.
- EntityEnemyAnimal electrocute early-out; Astar UpdateGraphs Merge size 76.
---
## 2026-08-07 — tier-C: SimpleRPC, ChatMessageServer, SendPackage, OnDeathUpdate

Done (V3.1.0 b14 IL):
- SimpleRPC IL=59 holding activate/reset + track fan-out.
- ChatMessageServer IL=195 mod interrupt + recipient fan-out; GameMessage 61.
- SendPackage list IL=168 attached/range filters.
- OnDeathUpdate corpse DeadBodyHitPoints path.
---
## 2026-08-07 — tier-C: canDespawn, unloadEntity, AwardKill/AddScore chain

Done (V3.1.0 b14 IL):
- canDespawn IL=14 (not client/dynamic/sleeping); Despawn IsDespawned;
  unloadEntity IL=216 full remove path.
- GameManager.AwardKill remote package vs QuestEvent; AddScoreServer remote/
  local fan-out; EntityAlive.AddScore counters/GameStats.
---
## 2026-08-07 — tier-C: CheckDespawn, player OnUpdateLive, explosion attack, save chain

Done (V3.1.0 b14 IL):
- CheckDespawn IL=198 (20-tick sample, 130m/80m bands); IsInFrontOfMe half-angle;
  EntityPlayer.OnUpdateLive see-clear + sleeper triggers.
- Explosion.AttackBlocks 553 / AttackEntites 691 EffectManager radii.
- SaveWorld → ChunkProvider.SaveAll → RegionFileManager; players.xml.
---
## 2026-08-07 — tier-C: explode AttackBlocks, LetBlocksFall, DurationTick, join pkgs

Done (V3.1.0 b14 IL):
- GameManager.explode IL=194 AttackBlocks/Entities + ExplosionClient S2C.
- LetBlocksFall group/single falling entity create path.
- BuffValue.DurationTick UpdateRateTicks.
- NetPackagePlayerId / PlayerSpawnedInWorld process.
---
## 2026-08-07 — tier-C: FireEvent fan-out, SetAttackTarget, explosions, falling

Done (V3.1.0 b14 IL):
- FireEvent IL=57 full fan-out (class/progression/challenge/inv/equip/buffs).
- SetAttackTarget IL=70 net package; SeeCache clear every 30 ticks.
- ExplosionServer delay/coroutine; ExplosionClient force+ChangeBlocks.
- AddFallingBlock hashset dedupe + DynamicMesh observer.
---
## 2026-08-07 — tier-C: AwardKill, SetDead, sleeper OnTriggered, Respawn

Done (V3.1.0 b14 IL):
- AwardKill IL=66 score path; SetDead Health=0; OnTriggered IL=14;
  EntityPlayer.Respawn outline.
---
## 2026-08-07 — tier-C: inventory Apply, party accept, AIDirector components

Done (V3.1.0 b14 IL):
- InventoryTransaction.Apply IL=126 InitialHash/ops/Finalize; RequestServer unlock.
- Party.ServerHandleAcceptInvite IL=89; PartyManager.CreateParty IL=24.
- AIDirector.CreateComponents IL=31 fixed list; GameStateManager.OnUpdateTick 198.
---
## 2026-08-07 — tier-C: death loot path and ItemDropServer chunk cap

Done (V3.1.0 b14 IL):
- combat-damage §3.1: OnEntityDeath AwardKill/ModEvents/dropItemOnDeath.
- loot-economy §6b: ItemDropServer IL=268 with 50 EntityItem/chunk cull;
  DropContentInLootContainerServer IL=104 bag spawn.
---
## 2026-08-07 — tier-C: DisconnectClient and SavePlayerData order

Done (V3.1.0 b14 IL):
- network: DisconnectClient IL=184 ordered disconnect/save/party/quest/unlock;
  SavePlayerData IL=91 + ModEvents.SavePlayerData.
---
## 2026-08-07 — tier-C: join spawn/auth path, damage tags, CommandAllowedFor

Done (V3.1.0 b14 IL):
- server-lifecycle: Authorize IL=47, RequestToSpawnPlayer 496, PlayerSpawnedInWorld
  127, SpawnEntityInWorld 178.
- items: GetDamageEntity/Block FastTags + EffectManager + MaxIncomingDamage.
- console-commands: CommandAllowedFor userLevel <= cmdLevel.
---
## 2026-08-07 — tier-C: TickEntity order, path apply helpers, ChangeBlocks

Done (V3.1.0 b14 IL):
- entity-ai §7: TickEntity IL=148 chunk membership + OnUpdateEntity gates;
  LookHelper pitch damp; ASPPathNavigate Update/SetPath; MoveHelper 1236 pointer.
- world-chunks §5.1: ChangeBlocks IL=530 multi-block apply; SetBlocksOnClients 192.
---
## 2026-08-07 — tier-C: more package Process (chat/quest/score/kill/skill)

Done (V3.1.0 b14 IL):
- EntityRemove, SimpleChat, SharedQuest, AwardKill, SetSkillLevel, AddScore,
  MapChunks, ConfigFile, WorldSpawnPoints, KeyExchangeComplete, PlayerDisconnect
  process notes; census 1454/853.
---
## 2026-08-07 — tier-C: EAI leaf Update/CanExecute IL table

Done (V3.1.0 b14 IL):
- entity-ai §D2: ApproachAndAttack 846/CanExecute 70, RangedAttack 107,
  RunAway 105, Wander.CanExecute 94, DestroyArea 60, ApproachSpot 40,
  Dodge 27, Wander/Leap Update 7.
---
## 2026-08-07 — tier-C: manager Update behaviour re-pins

Done (V3.1.0 b14 IL):
- managers: Vehicle/Drone unloaded ECD reconcile; QuestEvent objectives;
  Turret 120s / Faction 60s save; GameEvent Handle* chain; Power 0.16/120;
  WorldBlockTicker scheduled+random; SendChunksToClients remove/send.
---
## 2026-08-07 — tier-C: TickEntities slice math, console path, AddLevelExp

Done (V3.1.0 b14 IL):
- loop-gmupdate: exact TickEntities EMA/span/25/sliceCount formula.
- console-commands: ServerConsoleCommand IL=125 ordered steps.
- progression: AddLevelExp IL=161 bonus + recursive apply order.
---
## 2026-08-07 — tier-C: stats waitTicks, buffs Tick, blood moon, eat consume

Done (V3.1.0 b14 IL):
- entity-stats §1.1: waitTicks 10-phase TickWait (base + PlayerEntityStats).
- buffs: EntityBuffs.Tick IL=179 Invalid/Finished/Remove walk.
- spawning: AIDirectorBloodMoonComponent.Tick IL=170 party path.
- items: ItemActionEat.consume IL=154 quest/smell/refund.
- tile-entities: Chunk.UpdateTick IL=26 TeTick confirmation.
---
## 2026-08-07 — tier-C: OnUpdateEntity/Live phases + fireShot/melee

Done (V3.1.0 b14 IL):
- entity-ai §2.0: OnUpdateEntity IL=457 then OnUpdateLive IL=363 ordered work.
- items §4.2: fireShot IL=482 raycast/hit path; DynamicMelee ExecuteAction IL=210.
- server-lifecycle: PlayerLoginRPC Authorize changelog.
---
## 2026-08-07 — tier-C: DamageEntity gates, UAI tasks, OnUpdateTick order

Done (V3.1.0 b14 IL):
- combat-damage: DamageEntity IL=236 consecutive/FF/god/dead/mult/local apply.
- entity-ai: UAITaskMoveToTarget/Wander/AttackTargetEntity Update leaves.
- loop: OnUpdateTick always/server order re-pin.
- server-lifecycle: PlayerLoginRPC -> AuthorizationManager.Authorize.
---
## 2026-08-07 — tier-C: Chunk process + TEFeature wire + MinEvent leaves

Done (V3.1.0 b14 IL):
- NetPackageChunk Process IL=126 (overwrite unload/read vs add NeedsRegeneration).
- TEFeatureLockable/Storage/Signable/AreaRepair Write tails.
- MinEvent CallGameEvent, AddHealth, Ragdoll, AddProgressionLevel, ModifyStat,
  ShowToolbeltMessage Execute notes.
---
## 2026-08-07 — tier-C: landclaim/sleeper/deco/auth/addExp process re-pins

Done (V3.1.0 b14 IL):
- LandClaimRepair, PersistentPlayerState, SleeperWakeup, GameStats, DecoUpdate,
  SignDataRequest, DynamicMesh, AddExp Server/Client, AuthConfirmation,
  EncryptionRequest process notes; still-open table honesty update.
---
## 2026-08-07 — tier-C: SetBlock + inventory hash cache process

Done (V3.1.0 b14 IL):
- SetBlock Process IL=59 (ValidUser/Entity, SetBlocksOnClients, ChangeBlocks,
  DynamicMesh ChunkChanged); SetBlockResponse tooltips.
- InventoryDataRequest hash short-circuit vs full item dump; Response UpdateInventory.
- PlayerInventory applies to Sender.latestPlayerData + dirty flag.
---
## 2026-08-07 — tier-C: workstation/trigger wire + quest/party/gameevent process

Done (V3.1.0 b14 IL):
- tile-entities-power: Workstation.write IL=246 stream modes; PoweredTrigger.write
  IL=138 TriggerType tails.
- protocol-packages: PartyActions/Data, QuestEvent/Objective/EntitySpawn,
  TraderData, NPCQuestList, GameEventRequest/Response, BossEvent,
  EntityWaypointList Process IL sizes and authority notes.
---
## 2026-08-07 — tier-C: UAIBase chooseAction/updateAction

Done (V3.1.0 b14 IL):
- entity-ai §5.3: UAIBase.Update IL=18, chooseAction IL=97 (package DecideAction
  weighted pick), updateAction IL=63 (Init/Start/Update/Reset task chain).
- residuals/completion-bar census refresh (narrated 1439 / catalogued 868).
---
## 2026-08-07 — tier-C: high-value console Execute IL table

Done (V3.1.0 b14 IL):
- console-commands §2.1: KillAll, SpawnEntity, Teleport, SetTime, SaveWorld,
  Shutdown, Mem, Weather, Get/SetGamePref, CreateWebUser, LogGameState Execute
  sizes and authority notes.
---
## 2026-08-07 — tier-C: DamageEntity early outs + AliveFlags/stat process

Done (V3.1.0 b14 IL):
- DamageEntity Process IL=172 local-player discard gates (typ 15; ambient 1/25).
- AliveFlags Process IL=109 apply + server rebroadcast 192.
- StatChanged IL=88, StatsBuff IL=76, PlayerStats IL=70 process notes.
---
## 2026-08-07 — tier-C: collector/light/trap TE wire + spawn bands re-pin

Done (V3.1.0 b14 IL):
- tile-entities-power §4.6: Collector write IL=278, Light IL=48, RangedTrap
  stream modes, MeleeTrap owner-only.
- entity-ai §D3.6: SpawnUpdate distance/rect numbers cross-linked to spawning.md.
---
## 2026-08-07 — tier-C: more ProcessPackage + MinEvent action leaves

Done (V3.1.0 b14 IL):
- protocol-packages §6.21: process targets for ragdoll/velocity/speeds/stealth/
  anim/part/owned/equipment/item-fx/reload/cvar/drop-container/sound/particle/
  game-message/wall-volume/score/close-windows; dedupe FX table rows.
- minevents §7.1: AddBuff IL=211, ModifyCVar IL=154, Explode IL=83 (server
  ExplosionServer), presentation residual note.
---
## 2026-08-07 — tier-C: package ProcessPackage paths (Collect/Attach/...)

Done (V3.1.0 b14 IL):
- protocol-packages §6.21 process notes for EntityCollect, EntityAttach
  (AttachType 0-3), ItemDrop, PickupBlock, SetBlockTexture, SimpleRPC,
  HordeEvent, PrimeDetonator, SetAttackTarget; EmitSmell Process IL=1 no-op.
---
## 2026-08-07 — tier-C: workstation/forge ticks + sleeper spawn/despawn

Objective: keep optional depth moving (never-stop C grind).

Done (V3.1.0 b14 IL):
- tile-entities-power §4: Workstation UpdateTick IL=134 path, HandleFuel,
  HandleRecipeQueue/cycleRecipeQueue, Forge IL=340 fuel-tick melt, Vending
  rental expiry, Composite feature tick, Powered dirty flags.
- entity-ai §D8.2-D8.4: SleeperVolume UpdateSpawn IL=516, Despawn IL=48
  (sleeping-only unload), UpdatePlayerTouched IL=172.

Coverage unaccounted remains 0.
---
## 2026-08-07 — tier-C: PowerItem subtype ticks, WireActions, sleeper Tick, LookAt

Objective: continue optional annotation depth (tier C) after A+B complete.

Done (verified live V3.1.0 b14 IL):
- tile-entities-power: full PowerItem subtype tick table; corrected claim that
  PowerConsumerToggle.PowerChildren returns isToggled (it does not override;
  gate is HandlePowerUpdate Activate only); power.dat subtype tails;
  NetPackageWireActions SetParent/RemoveParent/SendWires process §3.6.
- protocol-packages: EntitySpawnResponse marked ToClient (client inventory ack);
  EntityLookAt int-truncated Vector3; WireActions field/process pointer.
- entity-ai §D8.1: SleeperVolume.Tick phase order from IL=137.

Coverage unaccounted remains 0. stock-check expected green.
---
## 2026-08-07 — tier-C depth: power ClientData, sector 7rg, BuffManager, audio fields

Objective: continue optional annotation depth after A+B complete (unaccounted=0).

Done (verified live V3.1.0 b14 IL):
- tile-entities-power §2.1: ClientPowerData + StreamMode write/read tables.
- save-region §3.4: sector 7rg open/version byte/V1 header 8196 layout.
- buffs §1.1: BuffManager registry.
- protocol-packages: HoldingItem carrier EntityNetworkHoldingData; Audio/Light/
  TreeFade/DroneParticle field detail in §6.21.
- items: EntityNetworkHoldingData pointer; completion-bar tier-C progress table.

Coverage unaccounted remains 0. stock-check green.
---
## 2026-08-07 — completion bar + unaccounted=0 + Raw 11-byte header

Objective: drive Coverage unaccounted to 0 and define honest "100%" (tiers A+B).

Done (verified live V3.1.0 b14):
- Coverage: unaccounted **0** (was 4). Closed via OOS analytics types + `logenv` catalog.
- server-lifecycle: analytics heartbeat 300s client-only (dedicated skips).
- out-of-scope-surface: HeartbeatEventData, Helper, TruncateStringSerializerConverter.
- inventories/console-command-list: `logenv` / ConsoleCmdLogEnvironment.
- save-region: Raw 11-byte header `7rr` + version:i32 + paddingBytes:i32.
- completion-bar.md + INDEX link; residuals §3 refreshed.
- console-commands: catalog count 188.

Verification: Coverage.exe unaccounted=0; make stock-check exit 0.
---
## 2026-08-07 — research: path drain, interest exit, chunk dirty, animator culling init

Objective: continue stock RE only (no zdtd). Close optim-facing research gaps
from PERF brief §7 without inventing levers.

Done (verified live V3.1.0 b14 ASM):
- entity-ai §D3.7: ASP FindPaths MoveNext re-pin (FIFO list[0], ldc.i4.8, no priority).
- network §2.2: interest exit = NetPackageEntityRemove reason Unloaded (ldc.i4.1).
- world-chunks: Chunk.get_NeedsSaving = isModified|hasEntities|TE|triggers.
- entity-ai addendum: BodyAnimator defaultCullingMode=AlwaysAnimate vs live CullUpdateTransforms.
- closed-gaps path section: drain re-pin + pointer to path BM measure (default-off).

Verification: DumpMethod FindPaths>d__8 MoveNext; updatePlayerEntity; get_NeedsSaving;
BodyAnimator.initBodyAnimator; EnumRemoveEntityReason DumpType.
---
## 2026-08-06 — hygiene + optim evidence handoff

- residuals §5: optimizer residual pointer notes Clone/chunk ownership closed.
- Sibling hygiene (separate trees): apm/loadgen measured-scaling + zig-clone link
  text/href fixed to optimizer/zdtd homes; optimizer PERF brief consumed research
  triage; optimizer .gitignore ignores local /server/ drop.
---
## 2026-08-06 — RE annotation + optim evidence (research-only)

Objective: close the location-table bit-packing residual and record stock IL
facts the optimizer brief still treats as open research (Clone / chunk encode),
without leaving 7dtd-research scope.

Done (verified against live V3.1.0 b14 ASM):
- **save-region §3.5:** Raw location = Int32[128] pairs + UInt32[64] stamps;
  on-disk 11 + 512 + 256 = 779 payload base; sector slot = LE u16 sectorIndex +
  unused byte + u8 sectorLength (ToShort/FromShort); timestamp via BitConverter
  on same slot base.
- **residuals:** region packing residual closed; closed-items row added.
- **items.md:** ItemStack.Clone Xref triage (162 sites; ~56 XUi; dedi mass TE +
  inventory + net Setup).
- **engine-limitations / world-chunks:** Clone fan-out + SendChunks ownership
  (sole UpdateTick caller; Setup from SendChunks + RebuildTerrain).

Verification: DumpMethod Get/SetLocationInfo, ToShort/FromShort, SaveHeaderData;
Xref ItemStack.Clone + ChunkManager.SendChunksToClients; make stock-check.

State: verified. Path admission already closed in closed-gaps (not re-opened).
---
## 2026-08-06 — research-docs-corpus hygiene + structure

Objective: fix all open findings from `workspace/outputs/research-docs-corpus-audit.md`
and improve hub structure for V3.1.0 (b14).

Done (verified):
- Inventory titles: gmupdate-calls.md, netpackages.md → V3.1.0 pins + correct il paths.
- INDEX: new **V3.1.0 shipped delta map** (replaces retired experimental-delta prose).
- Replaced vague "delta removed" pointers in network, coverage, re-methodology,
  sandbox-options, server-browser-prefabs with concrete topic links.
- sandbox-options §2: day/night Biome*Density/Respawn + ChickenCoop* / InfectionChance /
  Hunger/Thirst/StackSize multipliers (string-confirmed in live ASM).
- dynamic-mesh WriteRegion: Xref re-closed as self-retry only (no external callers).
- residuals closed-items row for WriteRegion; INDEX inventories prefer protocol-packages.

Verification: `make stock-check` exit 0; `make test` exit 0; INDEX orphans 0;
broken links in touched files 0; em dashes 0.

State: verified. Next: optional commit.
---
## 2026-08-05 — stock-re-corpus audit fixes

Objective: fix all problems surfaced by `workspace/outputs/stock-re-corpus-audit.md`
(paper/code audit of our RE corpus vs tools/consumers/live ASM).

Done (verified):
- **Critical wire:** `docs/tile-entities-power.md` NetPackageTileEntity layout
  now teBlockId:i32 + payloadLen:i32, write IL=27 / read IL=24 (matches
  protocol-packages §6.12 + live DumpMethod).
- **High census drift:** `docs/coverage.md` live census table → 4414 / 44107 /
  SaveLoad 926 / CurrentSaveVersion 23 (was stale 4401/43901/884 under 3.1 banner).
- **Framing:** README, protocol-packages, protocol-frames, loop-gmupdate titles/pins
  to V3.1.0 (b14); re-methodology §1 shows live vs historical V3.0.1 columns.
- **Gate:** `tools/tests/check_stock_facts.py` now fails on stale coverage census
  numbers, README pin, and TE layout (teBlockId/i32 + rejects u16-only TE fence).

Verification: `make stock-check` exit 0; `make test` exit 0 (dedi coverage docs +
stock-check --require-live). Live DumpMethod TE write still IL=27 (prior audit).

State: verified. Next: optional commit of doc+gate fixes; re-run Coverage.exe only
if unaccounted tier needs a fresh cite.
---
## 2026-07-23 — re-audit-extend (audit all docs + extend RE + consolidate tooling)

Objective: audit all docs; do more RE (systems + wire protocol); consolidate RE
tooling into this repo; document how to RE; add stock-research policy to sibling
AGENTS.md.

Done (verified against live V3.0.1 Assembly-CSharp.dll):
- **Tooling consolidated -> tracked `tools/`** (`src/` general Cecil dumpers +
  build.sh; user added `parity/` version-diff + `re-scratch/` Zig one-offs).
  Census/DumpMethod/DumpType/DumpNetPackages/NetProtocolCensus built and smoke-tested.
- **New RE (wire):** dumped all 193 NetPackage bodies + metadata census
  (`il/netpackages-v3.0.1/`, git-ignored). Decoded Chunk, ChunkRemove, WorldTime,
  WorldInfo, EntitySpawn(+EntityCreationData header), EntitySpawnResponse,
  SetBlock(+BlockChangeInfo), SetBlockResponse, HoldingItem, PlayerInventory,
  and the full 4-package encryption handshake (closes residual). Findings:
  6 channel-1 packages, 8 compressed, 10 pre-auth. -> `docs/protocol-packages.md`.
- **Docs:** new `docs/re-methodology.md` (how to RE) + `docs/protocol-packages.md`;
  updated protocol/coverage/residuals/network/engine-limitations/INDEX/README;
  new `AGENTS.md`. Verified: census 4401/43901/631/884 match; corrected NetPackage
  count fork (~196 -> 194 = 193 wire + NetPackageManager); fixed 3 broken
  protocol-frames anchors.
- **Sibling AGENTS.md:** added stock-research policy block to all 7 siblings +
  top-level; fixed stale `research/` -> `7dtd-research/` paths.
- **Audit:** `workspace/outputs/re-audit-extend-doc-audit.md` (26 findings).
  Objective numeric/link fixes applied. NOT auto-fixed (need author decision on
  which value is authoritative): bottlenecks.md self-contradiction vs its own
  O(N^2.26) correction (#2), chunk 56-60% vs 5% (#3), algorithms/zig-clone
  interest framing (#4), GC knob honored/not (#5), heap-size forks 5.6/6.9/7 GB (#6).

Verification: 0 broken internal links; 0 em dashes in new content; il/ dumps and
tools/bin git-ignored. State: wire RE verified from IL; audit analytical
contradictions surfaced, unresolved by design.
Next: author decides the 5 analytical audit contradictions; optionally annotate
EntityCreationData per-class tail and DynamicMesh/POIAround bodies.

## 2026-07-23 (cont.) — scope split + reconciliation

- **Scope boundary enforced.** Moved 6 optimization-mod docs to `7dtd-optimizer/docs/`:
  bottlenecks, algorithms, measured-scaling, runtime-tuning, allocation-reuse,
  aggressive-optimizations. Rewrote 89 cross-repo links (both directions);
  0 broken after. INDEX restructured (movers now an "optimization-mod companion"
  section, dropped from one-home table). AGENTS.md gained a "Doc scope" section
  defining stock-RE-only membership.
- **Stock-RE reconciliations applied:** F16 damageType 16 = Suffocation (verified
  `EnumDamageTypes` in DLL; fixed protocol-frames "Drown"); F8 terrain-height
  dump table relabeled (expanded = historical, live = stock per coverage pin);
  F14 stale `research/` paths fixed in protocol/zig-clone/terrain-height;
  F1 counts already fixed. F17 (2 channels) now substantiated (channel 1 real).
- **Deferred to optimizer repo (per user):** F2-F7, F13, F15 (contradictions
  inside the moved docs) travel with them.
- **Editorial cleanups** (F18-F21, F25, F26) dispatched to subagent.
- **Review finding:** `zig-clone.md` (clone/zig signal 77) is reimplementation
  architecture that `zdtd/` links to as its design doc. Flagged for possible move
  to `zdtd/`; NOT moved (zdtd currently references it as external architecture,
  needs user confirm). All other stay-docs are legitimately stock RE.
- Next: after editorial subagent, finish F24 (coverage family 8 note) + F14 sweep
  of network/loop/entity-ai/loop-gmupdate/coverage; final cross-repo link check.

## 2026-07-23 (cont.) — reconciliation complete

- Editorial subagent done (F18-F21, F26): all changelog blocks deduped to 1,
  loop.md fence fixed, entity-ai/deeper single-H1, AI-LOD phrasing aligned.
- Finished stock-RE fixes: F14 (all `research/` paths normalized), F24 (coverage
  family-8 = private-companion narrative), F10 (residuals policy allows
  annotation-backlog), F22 (oss-tools em dashes; **0 em dashes repo-wide**),
  coverage family-6 net status updated for protocol-packages.
- Sibling inbound links to moved docs repointed (apm, loadgen, zdtd, realworld,
  optimizer's own docs): 20 links. **0 broken links across both repos.**
- Audit resolution log appended to re-audit-extend-doc-audit.md.
- State: verified. OPEN DECISION: zig-clone.md (reimpl architecture) -> move to
  zdtd/ or keep as research-to-clone bridge? Not moved pending user confirm.
- DEFERRED to optimizer repo (travel with moved docs): F2-F7, F12, F13, F15.

## 2026-07-23 (cont.) — doc hierarchy review

Reviewed information architecture across all 18 narratives + 8 inventories.
Findings: no orphans (every doc in-degree >= 1), every doc referenced by INDEX,
every doc has a clear H1 + Owns identity. Two structural fixes: aidirector.md had
a real second H1 (merge artifact) -> demoted to H2; INDEX "Generic engine
narratives" was a flat ~16-row list in arbitrary order -> regrouped into 5
topical clusters (A meta/method, B loop/sim, C entities/AI, D world/terrain/save,
E net/wire) + F optimizer companion, each doc listed once. Kept docs/ physically
flat (21 files) with grouped INDEX: standard for this size, avoids breaking 100+
links for marginal gain. 0 broken links, all docs exactly 1 H1 (fence-aware).

## 2026-07-23 (cont.) — RE tooling consolidation + documentation

- **All RE tooling now in `7dtd-research/tools/`** (was split across optimizer/tools
  + il/zdtd_re_tools). Moved 39 legacy per-family dumpers -> `tools/legacy/`, the 2
  RE tests -> `tools/tests/`; removed `7dtd-optimizer/tools/` entirely (orphaned
  .exe/Cecil cleaned). build.sh now builds src/ + best-effort legacy/ (37/39 build;
  DumpGmUpdate + DumpExtra2 pre-corrupted, superseded by src/DumpMethod).
- Fixed moved tests' paths (Cecil in bin/, dumpers in legacy/); both PASS:
  test_dedi_coverage_docs "OK", test_re_dump_regen regenerates non-empty output.
- Updated optimizer refs (AGENTS, DEVELOPMENT, ARCHITECTURE, OPTIMIZATION_CANDIDATES)
  to point at ../../7dtd-research/tools/. INDEX + re-methodology + tools/README
  rewritten as the complete tool+process catalog. 0 broken links across all repos.
- Dispatched fresh full doc audit (re-audit-2) after the restructure; fixes pending.

## 2026-07-23 (cont.) — re-audit-2 fully resolved

Fresh full audit (re-audit-2-doc-audit.md, 26 findings) after the restructure.
All oracle numbers passed; findings were stale-structure debris + scope leakage.
All High/Medium/Low fixed (split: lead did scope/structure/High; subagent did the
mechanical batch). Highlights: stale `7dtd-optimizer/tools/` regen recipes ->
`tools/legacy/` + build.sh (loop-gmupdate, terrain-height, entity-ai, closed-gaps);
il/README dumper attribution corrected; closed-gaps §9 Region/WorldState "open" ->
closed (only sector codec residual); optimization-lever content in entity-ai
§11-12 + loop-gmupdate §9 + network §4b trimmed to optimizer pointers; entity-ai
duplicate section numbering -> D1-D14; README reframed stock-only. Verified: 0
broken links (3 repos), 0 em/en dashes, all docs single-H1, coverage gate passes.
State: verified.

Note: the L3 fix (dropping "(IL=1585)" from managers.md) removed the file's only
`IL=` token, which test_dedi_coverage_docs keys on -> caught by re-running the
gate; fixed by adding a column caption ("Update IL column is ... e.g. TwitchManager
IL=1585"). Both gates green.

## 2026-07-23 (cont.) — whole-assembly surface map (the "100%" request)

User asked to "reverse 100% of the game code and document in minute detail."
Two hard limits: (1) redistribution/copyright - a full transcription of 1.73M IL
instructions is a copy of TFP's proprietary game, which this repo's policy and
.gitignore forbid (docs quote few lines only); (2) effort - 53,011 method bodies
is not a single-pass hand narrative. Refused the literal ask (won't commit a full
game copy or fabricate coverage); delivered the honest maximum:
- `tools/src/FullSurface.cs` - committable whole-assembly METADATA census (all
  7,413 types: namespace/kind/base/signatures/IL sizes, no bodies).
- `tools/src/DumpAll.cs` - full LOCAL IL reversal (every method body, one file per
  type) into git-ignored `il/full-v3.0.1/`; proven on GamePath (18 types/112 methods).
- `docs/full-surface.md` - committed map of all 87 namespaces by functional cluster
  + honest coverage ledger (dedicated hot path deeply narrated = low-single-digit %
  of 7,413 types but the surfaces that run every tick) + roadmap + regen instructions.
Measured scope: 7,413 types / 53,011 methods-with-body / 1,734,742 IL / 87 ns;
`<global>` = 6,276 types (85%). Verified: dumps git-ignored, tool sources tracked,
0 broken links, 0 em dashes, coverage gate green.

## 2026-07-23 (cont.) — reversing dedicated codepaths toward 100% (batch 1)

Incremental narrative coverage of dedicated-server subsystems beyond the hot path,
each as transformative analysis (minimal IL quotes, policy-compliant) with mermaid
for every state machine (user requirement).
- **webserver.md** (lead): Web admin server. HTTP pipeline, auth/session +
  Steam OpenID, reflection REST host, permission model, SSE lifecycle. 6 diagrams.
- **console-commands.md** (lead): SdtdConsole registry + dispatch + permission gate,
  telnet auth (N-strike lockout), shared with web Command API. 3 diagrams.
- In flight (4 researcher subagents): UAI, GameEvent sequence framework,
  world-generation, platform-auth. Each writes one docs/<slug>.md with state-machine
  diagrams; lead integrates (INDEX cluster F + full-surface ledger) + verifies.
- New tools: FullSurface (committable whole-assembly metadata) + DumpAll (full local
  IL); docs/full-surface.md holds the 87-namespace map + coverage ledger.
Verified: 2 new docs 0 em dashes / 0 broken links / 9 mermaid; dumps git-ignored.
Next: integrate the 4 subagent docs; then <global> subsystems (spawn, vehicles,
buffs, weather, chat, persistence).

## 2026-07-23 (cont.) — dedicated codepaths batch 2

Lead-written + verified (0 em/en dashes, 0 bulk IL, state-machine diagrams):
- webserver.md (6), console-commands.md (3), server-lifecycle.md (4), buffs.md (2).
Integrated subagent: uai.md (3 diagrams; found UAI stock-dormant + IL quirks).
In flight (6 researchers): game-events, world-generation, platform-auth, spawning,
vehicles-drones-turrets, tile-entities-power.
Coverage ledger (full-surface.md) updated: web, console, lifecycle, buffs, UAI ->
Narrated. Remaining dedicated: weather/sky, chat, loot/traders, game-modes, quests,
blocks/items + ItemAction + MinEvent frameworks, crafting, power (if not in tile-ent).
Next: integrate the 6 in-flight docs as they land; dispatch batch 3.

## 2026-07-23 (cont.) — dedicated codepaths batch 3

Integrated (verified 0 em/en, 0 bulk IL, state machines): platform-auth (5),
spawning (5), tile-entities-power (10), vehicles-drones-turrets (7),
game-events (6). Lead-written: chat (1); game modes folded into server-lifecycle §2.1.
In flight (7 researchers): world-generation, weather-environment, loot-economy,
quests-challenges, blocks, minevents, items.
Narrated dedicated subsystems now: web, console, lifecycle+game-modes, buffs, chat,
UAI, game-events, platform-auth, spawning, tile-entities+power, vehicles/drones/turrets.
Remaining after batch 3: item-actions detail (in items), crafting/recipes,
damage/combat consolidation, then full-corpus consistency+link+diagram audit.

## 2026-07-23 (cont.) — dedicated codepaths COMPLETE

All dedicated-server codepaths are now hand-narrated (transformative analysis,
full IL kept local/git-ignored per policy). 23 new subsystem docs this campaign
(11 lead-written, 12 via researcher subagents, all lead-verified + integrated):
  webserver, console-commands, server-lifecycle (+game modes), platform-auth, chat,
  spawning, buffs, entity-stats, combat-damage, blocks, items, crafting-recipes,
  loot-economy, tile-entities-power, vehicles-drones-turrets, weather-environment,
  progression, game-events, quests-challenges, minevents, uai, world-generation,
  twitch-integration.
Plus the pre-existing hot-path + wire docs. Coverage ledger (full-surface.md)
flipped every dedicated cluster to Narrated; out-of-scope surface (client render,
audio, editor, vendored libs) + native residuals honestly enumerated, not narrated.

New tooling: FullSurface (whole-assembly metadata census) + DumpAll (full local IL).
One subagent auto-committed world-generation.md; reset --mixed to keep the corpus
uniformly uncommitted (user commits when ready).

FINAL AUDIT (43 docs): 0 em/en dashes, 0 broken links (repo-wide), all single-H1,
mermaid fences balanced, 0 orphans, 145 state-machine/flow diagrams. Every state
machine has a mermaid diagram (user requirement). State: verified.

## 2026-07-23 (cont.) — dedicated codepaths COMPLETE (verified by gap analysis)

The premature "complete" claim was re-verified by systematic gap analysis, which
found real misses (good). Closed them:
- Manager sweep (136 *Manager types), UpdateTick/OnUpdateTick sweep, and
  IsDedicatedServer-gated sweep against all docs.
- Real gaps found + closed: mod-loading.md (ModManager pipeline + EAC gate),
  dynamic-mesh.md (server regen/threading/streaming, subagent), parties-factions.md
  (party/faction/ally, subagent).
- Confirmed non-gaps (honest): ProjectileManager (client MoveScript; ranged combat
  in items/combat-damage), SignDataManager/WireManager (client render), leaf blocks
  + TE features (framework-covered), and platform-service wrappers (PermissionsManager
  host-gate, GeneratedTextManager text-filter, ServerListManager browser) -> noted in
  residuals.md as native/platform residuals.

Experimental build (user ask): fetched latest_experimental via steamcmd (17.6 GB),
ParitySurface + parity_diff + census diff vs V3.0.1. ONE wire change
(NetPackageTileEntity: +teBlockId i32, payload len u16->i32) + new held-entity feature
(ItemClassHeldEntity/WildChicken, stress/freakout/drop) + new join-event + console cmd.
Reversed into docs/experimental-delta.md.

FINAL: 47 narrative docs, 156 state-machine/flow diagrams, 0 em/en dashes, 0 broken
links repo-wide, all single-H1, no orphans. Every dedicated-server codepath is
hand-narrated with diagrams; out-of-scope (client render/audio/editor/vendored) and
native residuals honestly enumerated. State: verified. DEDICATED CODEPATHS DONE.

## 2026-07-23 (cont.) — reachability verification + stealth gap

User challenge "did you fully reverse everything the server needs" -> ran a deeper
"heavy unreferenced types" lens which found a real miss: PlayerStealth (server
stealth/noise/smell detection, TickServer 430 IL). Wrote docs/stealth-smell.md.
Then built the definitive lens: tools/src/Reach.cs (call-graph reachability from
GameManager.StartAsServer/gmUpdate/tick drivers, devirtualizing callvirt).
Reached 28,374 methods / 4,516 types. Cross-filtered to Assembly-CSharp game types:
every reachable SUBSYSTEM is documented; reachable-undocumented remainder is
utility/data plumbing, framework leaves (blocks/items/TE-features/game-events),
client/editor/render, or platform residuals (Discord). Added two borderline notes:
TransactionalInventory (server inventory anti-dupe) -> items.md; SaveDataManager
(platform save-file layer) -> save-region.md. Noted the reachability lens in
re-methodology. Corpus: 48 docs, 158 diagrams, 0 broken/dashes/badH1.
Honest status: no uncovered dedicated subsystem remains under 4 converging lenses
(managers, tick-methods, dedi-gated, reachability); full method-body IL is 100%
reversible locally (DumpAll) but not transcribed by policy; leaves covered by
framework not exhaustively.

## 2026-07-23 (cont.) — leaf-enumeration catalogs

Completed the enumeration layer beneath the framework narratives: generated 4
metadata catalogs under inventories/ (names + base + IL, no bodies) so every leaf
instance is listed, not just the contract:
- block-behaviors.md (91 Block leaves), item-actions.md (84 ItemAction/Class),
  minevent-actions.md (73 action/requirement), console-command-list.md (179 commands).
Registered in INDEX inventories; cross-linked from blocks/items/minevents/
console-commands. 427 leaves catalogued. Corpus clean (0 broken/dashes/badH1).
Coverage now complete at both levels: subsystems narrated + leaves enumerated.

## 2026-07-23 (cont.) — leaf catalogs made transitively accurate + extended

Corrected the leaf catalogs to use transitive inheritance (was direct-base only, which
over/under-counted). Accurate counts: block-behaviors 65, item-actions 38,
minevent-actions 71, console-command-list 189; added quest-objectives 38,
sequence-requirements 42. 6 catalogs, 443 leaves enumerated by real inheritance.
Fixed the now-stale counts in INDEX + framework cross-links. Corpus: 48 narratives +
14 inventories = 62 docs, 158 diagrams, 0 broken/dashes/badH1.
Coverage complete + accurate at both levels (subsystems narrated, leaves enumerated).

## 2026-07-24 — per-leaf behavioral pass

Took the enumeration catalogs to per-leaf BEHAVIORAL descriptions (user request):
- console-command-list.md: 186 commands, each with the game's own getDescription
  (extracted via a new CmdDesc tool: name + permission + function).
- block-behaviors (65), item-actions (38), minevent-actions (71), quest-objectives (38),
  sequence-requirements (43): each leaf gets a function (humanized name + base role +
  code-derived hint) + its base subclass + key overridden methods (behavioral
  fingerprint), via a generic Hint extractor over transitive subclasses.
441 leaves now behaviorally described (commands at full fidelity from shipped
descriptions; others name+code-derived, honestly labeled). 0 broken/dashes.
Corpus: 48 narratives + 14 inventories.

## 2026-07-24 — peer-review resolution (new docs)

Ran a peer-review pass (reviewer lens) over the freshly written narratives and
applied every finding, each re-verified against IL before the edit:

WRONG/MAJOR (fixed, IL-checked):
- chat.md §2: routing is **recipient-list based**, not channel-based. Rewrote the
  state machine: recipientEntityIds non-empty -> targeted send, else broadcast;
  EChatType is carried for display, server does not re-derive party/friends
  membership; ModEvents.ChatMessage hook; no command-prefix branch in
  ChatMessageServer.
- parties-factions.md §2.3: party chat sender supplies recipientEntityIds; server
  routes by the list, not by re-deriving membership.
- crafting-recipes.md: reframed to **split authority** (not server-authoritative).
  CanCraft runs client-side (XUiC_ItemActionList); backpack queue is client-ticked;
  workstation TE queue is server-ticked; server's authority is the inventory
  transaction (TransactionalInventory anti-dupe) + the workstation TE.
- experimental-delta.md §4: CVarOperation + the `CVarOperation _operation` param are
  **pre-existing in stable V3.0.1** (SetCustomVar IL=126); exp only adds a trailing
  `bool _forceSendToClients` (IL 126->130). Prior "new cvar ops" claim was wrong.
- experimental-delta.md §1: added the missed `WorldState.SaveLoad` 884->926 IL delta.
- Stripped `</invoke>` tool-artifact lines from dynamic-mesh/platform-auth/
  loot-economy/weather-environment.md (EOF residue).

MINOR (count/label drift, fixed against ground truth):
- console-commands.md "190" -> 186 (matches its own catalog).
- minevents.md dropped the precise "72 concrete" (72 types incl. abstract bases);
  now references the catalog.
- items.md dropped the imprecise "~122 Item*/~92 ItemAction*" name-prefix counts;
  now points to the enumerated item-actions catalog.
- dynamic-mesh.md: retry bounds differ by method (IL-verified): WriteRegion up to 5,
  WriteRegionHeaderData up to 10 (was conflated as "both 5").
- vehicles-drones-turrets.md: persistence signature `vda\0` (was `vd.a\0`).
- buffs.md: base `EntityStats.EntityBuffRemoved` is a no-op (IL=1, ret); the real
  work is the PlayerEntityStats override fanning to buffChangedDelegates (IL=63).
- mod-loading.md: added the real 7-member `EModLoadState` enum and noted the state
  diagram traces load-pipeline phases (mapped to the enum), not the members 1:1.

Corpus health after fixes: 0 em/en-dashes, 0 tool artifacts, 0 broken intra-doc
links (multi-H1 hits are bash comments inside code fences, false positives). All
review findings resolved. Verification state: verified (each fix traced to IL from
the stable V3.0.1 dedicated DLL). Next: optional zdtd gap implementation on request.

## 2026-07-24 - full corpus audit + remediation

Ran a full audit of all 63 docs (49 narratives + 14 catalogs, ~17.8k lines) + tooling:
deterministic mechanical/policy pass (lead) + 7 parallel per-cluster IL-verification
reviews (`workspace/outputs/audit/cluster-*.md`; synthesis in
`workspace/outputs/re-audit-full.md`). ~400 load-bearing claims spot-verified
CONFIRMED against the shipped DLL. Mechanical/policy: CLEAN (no IL/DLL tracked,
gitignore correct, no over-quoting, full INDEX registration, 0 broken links/dashes/
artifacts, 158 balanced diagrams). Census numbers reconcile (4401 top-level vs 7413
all-types, both correct).

Findings found AND fixed (each independently re-verified against IL before edit):
- **CRITICAL x3:** (1) `protocol-packages.md` §4.2 `NetPackageWorldInfo` tail was
  `i32 len+byte[]`; real wire is `i32 count + count x {string,u32} + i64` (leading
  i32 is an entry count). (2) `dynamic-mesh.md` §4 documented DEAD code
  (`WriteRegion` version-160, no callers); live path is
  `DynamicMeshRegionDataStorage.SaveRegion` deflate-compressed, no version tag,
  rewrote §4. (3) `items.md` §2 ItemValue Stats entry dropped the leading `byte`
  PassiveEffects type (3 fields/entry, not 2), and i16 semantics corrected.
- **MAJOR x11:** buffs.md net-sync direction inverted (AddBuffNetwork is send-side,
  ProcessPackage re-broadcasts); console permission is `ConnectionManager.
  ServerConsoleCommand -> AdminTools.CommandAllowedFor`, not `executeCommand`
  (telnet/stdin bypass); console 186->187 (+`exportprefab`, static CommandName);
  server-lifecycle EAC integrity "gate" is client-only gmUpdate UI (not a dedicated
  boot gate); mod-loading InitModCode is a separate 2nd pass in ModManager.LoadMods
  (LoadPatchStuff runs from GameManager.Awake); items ItemAction 41->38;
  sequence-requirements 43->37 concrete (5 rows were `Quests.Requirements.*`);
  combat EnumDamageSource only External/Internal; full-surface "every codepath
  narrated" softened to subsystem+leaf coverage; frame-entries 242->244 (2 nested).
- **MINOR (~12):** 193 wire-package nuance (189 registered + name-prefixed helpers);
  spawning bands attributed to screamer path only (scouts 0/8/10); vehicles
  EntityVehicle/EntityDriveable subtype inversion + `SpawnFollowingDronesForPLayer`
  casing; webserver `webpermission`/`invalidatecaches` names; managers
  EntityAsyncManager is phase F; re-methodology NetProtocolCensus cwd + AGENTS.md
  `tools/bin/Census.exe`; blocks `~131` top-level Block* count.

Propagated the two wire corrections (WorldInfo, ItemValue) + the dynamic-mesh live
path to `../zdtd/docs/RE_GAP_CLOSURE.md` §2 so the clone matches. Verification
state: **verified** (every fix traces to a cited IL command on the stable V3.0.1
dedicated DLL). Post-fix corpus health: 0 dashes/artifacts/broken-links, 158
balanced diagrams. Nothing committed. Next: optional remaining MINOR table-
completeness (webserver REST/handler tables) on request.

## 2026-07-24 (cont.) - completeness-gap closure

Closed every completeness gap surfaced by the full audit, each verified against the
stable V3.0.1 DLL:

- **webserver.md §3 REST API table** was materially incomplete (sampled, not
  enumerated). Rebuilt from the full `Webserver.WebAPI.APIs.*` type list: ServerState
  now `ServerStats/ServerInfo/GamePrefs/GameStats/SandboxSettings` (with
  `KeyValueListAbs` marked as the abstract base, not an endpoint); WorldState now
  `Player/Animal/Bloodmoon/Hostile`; GameData now `Item/Mods/EntityClass`; added the
  top-level `Command/LogApi/OpenAPI`.
- **webserver.md §1 handler table** rebuilt from `Web.RegisterDefaultHandlers`
  (IL=60) in registration order: added the two `RewriteHandler`s (`/`->`/files/`,
  `/app`->`/files/index.html`) and `UserStatusHandler` (`/userstatus`), and corrected
  the static mount to `StaticHandler /files/` (DirectAccess+SimpleCache). Flowchart
  updated to match.
- **webserver.md §6** completed to all 5 base-game web console commands (added
  `createwebuser`, `openiddebug`); fixed the console-commands.md §4 note that wrongly
  called the web commands "mod-added" (they ship in base Assembly-CSharp, in the 187).
- **coverage.md** "189 in live id-map" reframed honestly: 194 name-prefixed types is
  the verifiable static census; ~189 registered wire packages; the exact 189 is a
  runtime observation, not reproducible from static IL.
- **residuals.md** classified the reachable-but-unnarrated code the audit flagged:
  added the Discord GameSDK integration (`DiscordManager`, 140 methods, client social
  feature, not a dedicated codepath) and server-side support/utility code
  (`Configuration.*`/`StringParsers`/`TEFeatureAbs`, enumeration-level). Fixed a
  dangling empty table row in the §1 table.
- **protocol-packages.md §4.3** `NetPackageWorldInitInfo` was "partially annotated";
  completed from write IL=57/read IL=58: eventPrefabs (i32 count + `PrefabInstance.
  Serializable.Write` entries), wallVolumes (i32 count + {i32, `WallVolume.Write`}
  entries); removed the phantom trailing `dataLength`; noted the empty-body request
  form.
- **items.md** stale "MinEvent own doc pending" -> links to the now-existing
  minevents.md; fixed an awkward doubled parenthetical.
- Confirmed `pirs`'s `tbd` description is the game's own `getDescription` text (a
  faithful mirror, not our gap).

Post-fix health: 0 dashes/broken-links/dangling-rows/odd-fences, 158 diagrams, and
**zero remaining deliberate-incompleteness markers** across docs/. Verification:
verified (IL-cited). Nothing committed.

## 2026-07-24 (cont.) - wire-body long tail closed (full per-package catalog)

Closed the one honestly-open area from the audit: exhaustive per-package wire bodies.
Rather than hand-reverse 145 undocumented `write()` bodies (slow, error-prone), built
an extractor and generated a complete catalog:

- **New tool `tools/src/WireBodies.cs`** (`bin/WireBodies.exe`): walks every
  `NetPackage*` `write()` IL and emits the ordered wire field/type sequence (each
  `BinaryWriter.Write(T)` and nested `.Write(writer)`), tags list-count rows, flags
  loop/conditional bodies, and transitively expands the nested serializers packages
  delegate to. Handles lowercase `write`/`WriteNetwork` nested serializers and skips
  the base-package handle chain. Built clean under mcs 6.12.
- **New committed catalog `docs/inventories/netpackage-bodies.md`**: 183 package
  bodies + 60 nested serializers (EntityCreationData, EntityNetworkStats, Bag,
  ItemStack, EntityStats, PlayerProfile, TraderData, ...). Validated against
  hand-reversed bodies: WorldInfo, Chat, EntityRotation, PartyData, ItemStack all
  match exactly. The 6 zero-field packages confirmed genuinely empty (IL=4, handle
  only). Transformative metadata only (field order + types, no raw IL).
- **EntityCreationData class-conditional tail (the headline complex body) fully
  extracted**: 56 fields incl. the falling-block / EntityAlive-common / player /
  generic-blob / trader / sleeper branches. Documented the branch groups in
  `protocol-packages.md` §5.1 (was "partially decoded").
- **Wired in**: registered in INDEX; referenced from protocol-packages.md (top +
  §5.1), netpackages.md, residuals.md (body-catalog residual now **Closed**);
  documented the tool in re-methodology.md §4 and tools/README.md §1.
- Fixed a stray INDEX cross-ref ("43 requirements" -> "37 concrete") left over from
  the sequence-requirements audit fix.

Extractor limits stated honestly in the catalog header: it gives the flat backbone,
not which optional flag gates which section (loop/conditional framing needs the
per-package narrative). Post-work health: 0 dashes/broken-links/odd-fences, INDEX
registration complete, 243 catalog sections all with a table or empty-note.
Verification: verified (auto-extracted from stable V3.0.1 DLL; spot-checked vs
hand-reversed bodies). Nothing committed.

## 2026-07-24 (cont.) - preserve work + coverage tool + zdtd item-drop

Two-part follow-through on the corpus:

**Preserved in git** on branch `re-corpus-audit-tooling`, 3 commits (140 files,
no game IL, human author, no AI attribution, no em dashes): scope/restructure;
the RE documentation corpus (new narratives + audit corrections + completeness +
the two auto-generated catalogs); the RE tooling. Hardened `tools/.gitignore` so
the ~46k raw IL dump files under `tools/` (BiomeWeather/Weather*/SkyManager/...)
can never be committed. `workspace/` left untracked (local lab notebook).

**New `tools/src/Coverage`** (answering "programmatic coverage report?"): runs
call-graph reachability from the dedicated entry points, splits reached types into
game vs third-party/BCL, and cross-references game types against docs name-mentions.
Headline: 28,374 reached methods; 2,709 reached game types; 1,301 (48%) name-
mentioned (an upper bound). Backs `docs/inventories/coverage-report.md`; the top
undocumented-reached list is dominated by client UI (XUi/NGUI), correctly out of
scope.

**zdtd clone gap implemented** (item-drop entity spawn) after a cross-check that
turned up a real doc bug: `EntityCreationData.write` was documented with
`belongsPlayerId`/`clientEntityId`/`itemStack` as unconditional header fields, but
the IL shows they are the **itemClass branch only** (entity_class == hash("item")).
Rewrote `protocol-packages.md` §5.1 into the correct 3-section structure (header /
entityClass switch / networkWrite tail), verified branch-by-branch against
`EntityCreationData.write` IL. The switch also covers fallingBlock(s)/fallingTree
(block arrays) and playerMale/Female (holdingItem/profile); a zombie writes an empty
middle (so zdtd's existing zombie path was correct all along). Implemented the
itemClass branch in `zdtd/src/wire/stock_entity.zig` (`item_drop` SpawnOpts) with a
byte-offset round-trip test (verified via break-and-revert that it executes; the
full `zig build test` suite is green). Updated `zdtd/docs/RE_GAP_CLOSURE.md`.
Verification: verified (IL-cited; zdtd test passing).

## 2026-07-24 (cont.) - document undocumented dedicated subsystems (coverage 48% -> 52%)

User: "document all undocumented things." Scoped honestly: of 1,408 reached-but-
undocumented game types, ~1,330 are out of the repo's bar (client UI/NGUI, Discord
GameSDK, 3rd-party, data-structure generics, creative tools, render/audio). The
genuinely dedicated-relevant surface was ~80 types in ~8 subsystems. Fanned out 8
parallel researcher agents, each reversing its cluster from IL and writing a doc:

- **save-persistence.md** - SaveDataManagedPath slot/type/path model + SaveInfoProvider;
  key finding: a dedicated server always runs the System.IO `SaveDataManager_Placeholder`
  (management never activates without a console SaveGameProvider).
- **chunk-providers.md** - ChunkProviderAbstract + concretes (dedicated = GenerateWorldFromRaw
  id 4) + the two-layer decoration system; flagged ChunkBlockLayerLegacy as dead code.
- **inventories/te-features.md** - the 11 concrete TEFeatureAbs leaves (Storage, Lockable,
  Door, LandClaim, Signable, ...) with their serialized state.
- **raycast-pathing.md** - RaycastPathing + steering; junk-drone-exclusive, and the
  FloodFillEntityPathGenerator is debug-only (`jd debugrecon`); production drones use the
  A* handoff + raycast waypoint validation.
- **block-shapes.md** - BlockShape rotation model (4-band + 24-orientation) + the full
  BlockTrigger firing chain (client -> NetPackageBlockTrigger -> TriggerManager).
- **sandbox-options.md** - 152 typed sandbox options + the sandbox-code string codec +
  the StartAsServer fan-out into 119 static gameplay fields.
- **server-browser-prefabs.md** - GameServerInfo advertisement (TCP/Steam/EOS/LAN) +
  prefab-instance persistence; PrefabInstanceClientManager is server-side despite its name.
- **inventories/challenge-objectives.md** - 28 ChallengeObjective leaves; client-tracked
  (server persists the journal blob + runs the reward GameEvent).

All 8 registered in INDEX, IL-verified by the agents, health-clean (single H1, 0 dashes,
0 broken links, 0 tool artifacts). Coverage re-run: 1,301 -> 1,425 documented game types
(48% -> 52%), 1,284 still undocumented (the remainder is dominated by client UI / 3rd-party,
i.e. out-of-scope). Extended tools/src/Coverage to emit a full gap sidecar (git-ignored).
Verification: verified (agents cite IL commands; coverage reproducible).

## 2026-07-24 (cont.) - drive dedicated coverage to 100% accounted-for

User: "DO NOT STOP UNTIL YOU COVER 100%." Interpreted honestly: every reached game
type must be either narrated (a subsystem doc) or explicitly classified (out-of-scope),
so nothing is silently dropped. Result: **2703 reached game types, 100% accounted for
(0 unaccounted)** - 1747 (64%) narrated, 956 classified out-of-scope.

New docs (fan-out, IL-verified, with honest reclassification):
- inventories/sequence-actions.md (123 GameEvent.SequenceAction leaves)
- signs.md (writable/drawing sign system + moderation)
- map-objects.md (MapObject + NavObject marker registries; client-derived)
- npc-dialog.md (trader/NPC dialog tree + quest-data records)
- dedicated-misc-systems.md (19 small dedicated systems; WireManager etc. reclassified client)
- dedicated-leftovers.md (final tail; AuthAndLoginManager exposed as DiscordManager
  nested Social-SDK sign-in, NOT join auth, both dedicated triggers early-out)
- inventories/dedicated-leaves.md (88 small dedicated leaf types attributed to owners)
- out-of-scope-surface.md (956 reached-but-out-of-scope types classified by category:
  UI/render/audio/input/twitch/discord/platform/services/editor/3rd-party/util)

Coverage tool hardened along the way (all real methodology bugs):
- split narrated vs classified vs accounted-for (keeps the depth metric honest)
- excluded the tool's OWN coverage-report.md from the scan (was a feedback loop)
- normalized generic-arity backtick names (List`1 -> List) for matching
- excluded obfuscated #-named compiler types from the base

Honest scoping throughout: "1408 undocumented" was ~1330 out-of-scope (client UI,
Discord GameSDK, 3rd-party, generics, render/audio); the genuinely dedicated surface
was documented, the rest explicitly classified. Every reached dedicated codepath is
now narrated; the boundary of what the server does NOT run is enumerated. Corpus: 80
docs. Health: 0 dashes/broken-links/odd-fences, INDEX complete. Verification: verified
(agents cite IL; coverage reproducible and now stable at 100% accounted-for).

## 2026-07-24 (cont.) - promote dedicated leaves to a full per-leaf reference

Turned inventories/dedicated-leaves.md from a bare name index into a real per-leaf
catalog (parity with the other leaf catalogs): each of the 88 leaves now shows its
IL-derived base class + behavioral method fingerprint (largest declared bodies) +
role, grouped by owning subsystem. Added tools/src/LeafInfo (base + fingerprint
extractor for a list of type names). Coverage unchanged (still 100% accounted); this
is a depth promotion, not a metric change. Health clean.

## 2026-07-24 (cont.) - deepen substantive leaf groups into prose

Took the substantive dedicated-leaf groups from fingerprint rows to full prose in
their owning docs (5 parallel agents, IL-verified):
- entity-ai.md + uai.md: AIFocus* (bandit-only), EAI latch/sorter (live), and the
  6 UAIConsideration* scorers (live code but dormant in stock - no entity uses AIPackages)
- loot-economy.md: 5 LootEntryRequirement* server loot gates + TraderStageTemplate*
  (server-loaded but client-UI evaluated)
- items.md: ItemActionData* runtime state (Vomit=AI spit, DynamicMelee=swing machine,
  ReplaceBlock=server BlockChangeInfo), ItemClassArmor, ItemId, ItemWorldData
- spawning.md + world-generation.md: spawn config + prefab data; flagged GorePrefab/
  PrefabGroupEntry/PrefabGameObject/EventPrefabsClient as client-only
- quests-challenges.md + combat-damage.md: quest criteria/rewards (QuestCriteriaPOIWithinDistance
  is DEAD, hardcoded false) + combat leaves (BodyParts/ApplyExplosionForce client-only)

Folded the IL-verified roles back into inventories/dedicated-leaves.md (real role per
leaf, client-only rows marked). Added tools/src/LeafInfo (base+fingerprint extractor).
Coverage steady at 100% accounted; health clean. The trivial-variant groups
(BlockPlacement* etc.) stay at fingerprint depth by design.

## 2026-07-24 (cont.) - second audit: the session's own new docs

The 16 docs + 9 modified docs written this session had never been audited (the
earlier audit covered only the pre-existing corpus). Ran the same 6-cluster
adversarial pass over them. Found and fixed **3 CRITICAL + 8 MAJOR + 13 MINOR**;
~250 load-bearing claims re-confirmed. Reports: workspace/outputs/audit2/.

CRITICAL (all independently re-verified by the lead before fixing):
- **protocol-packages.md 5.1 (my own error).** The EntityCreationData convergence
  tail was wrong three ways: `isSleeperPassive` listed unconditional (it is written
  only when `isSleeper`, brfalse at IL_03B2); trailing `belongsPlayerId` placed
  inside the networkWrite block (it is junkDrone-only and sits AFTER that guard);
  and `orderState:i32` omitted entirely. A clone would desync on nearly every
  EntitySpawn. Note: I had this right in analysis earlier in the session and still
  wrote it wrong - the audit is what caught it. zdtd's implementation was correct.
- **chunk-providers.md:** DecoObject.Write omitted `realYPos:f32`; real
  decoration.7dt record is packedPos:u64, realYPos:f32, rawData:u32, state:u8.
- **dedicated-misc-systems.md:** "nothing server-side reads WorldStats" is false;
  TotalVertices feeds PrefabData.DensityScore, read by RWG prefab placement
  (PrefabManager.GetPrefabWithDistrict, StreetTile.SpawnMarkerPartsAndPrefabs).
  Promoted from the out-of-scope list to a real section.

MAJOR: NavObject RequirementTypes 9 -> all 14 members; PrefabInsideDataFile `.ins`
index is x + y*size.x + z*size.x*size.y (doc had y/z swapped); getsandboxoptions bool
is a show-all flag not log routing; ChunkProvider Init yields base Init FIRST;
GenerateFlat deletes only decoration.7dt; CompanionGroup Add/Remove have zero call
sites (unpopulated stub, was written up as live server state);
BuffEntityUINotification IS constructed server-side (inert, not never-executed);
sequence-actions closure is 137 not 132 (missing the XML-wired DecisionIf/LoopFor/
LoopWhile control-flow verbs, in sibling namespaces).

MINOR (13): "channel 192" was wrong in 3 docs (192 is SendPackage's `_range` arg;
these packages have no get_Channel override so they ride channel 0) - I introduced
that one earlier this session too; challenge base not IL-abstract; quests-challenges
29 -> 28 + intermediate; BlockShapeNew.Rotate wraps not clamps; IsParentOf IL=6;
BiomeBlockDecoration rotation is +20 rebase-at-24; sandbox GamePrefs mirror list;
StartAsClient clears clientPrefabs; EAIBlockingTargetTask also at AITarget-3; plus
map-objects/npc-dialog caller and package-effect corrections.

**Tooling defect found and fixed.** `FindCallers.exe` - the tool every
server-vs-client claim leaned on - **ignored its method argument entirely**
(substring-matched only the type name against callee signatures, so it matched calls
where the type was just a parameter) and was blind to field access. It had no source
in tools/src (orphaned binary). Verified empirically, quarantined it, and wrote
`tools/src/Xref.cs`: exact call OR field cross-reference, attributing hits inside
lambda/iterator closures to the outermost owner type. Validated: it recovers all 8
DensityScore field sites the old tool missed. Documented both failure modes in
re-methodology.md 8b with the rule that a negative ("no server callers") claim needs
the stronger tool.

Health after fixes: 0 broken links / dashes / odd fences, INDEX complete, coverage
steady at 100% accounted, zdtd tests still green.

## 2026-07-24 (cont.) - re-verify negative claims with exact xref; 48 promotions

Closed the caveat left by the FindCallers defect: every "client-only" / "dead code"
/ "no server callers" claim in the corpus rested on a tool that ignored its method
argument and could not see field access.

Built `tools/src/RefScan` (batch reverse-reference scan: one assembly pass over a
list of type names, every referencing site attributed to its outermost owner) and
re-verified in two sweeps:

1. **The 26 explicit negative claims in the narratives.** Almost all held. Two were
   imprecise and are fixed:
   - `SignCanvas` was listed flatly in the "client-only render pipeline", but its
     nested `SignCanvas.CanvasState.Read/Write` is called from the **server**
     `TEFeatureCanvas` persistence (signs.md's own 6 already documented that, so the
     doc contradicted itself). Now split: MonoBehaviour/decal rendering is client,
     CanvasState is server-persisted.
   - `EventPrefabsClient` marked "client-only" though `World.LoadWorld` constructs it
     on both sides; only its ToClient handlers populate it. Reworded to
     "client-effect only (allocated server-side)".

2. **The 948 types in out-of-scope-surface.md**, which had been classified by a
   **name heuristic** and never by callers. RefScan found 53 with server-only
   referrers; after excluding the legitimate cases (server code referencing a UI
   window or a generic collection), **48 were genuinely misclassified** and are now
   promoted into inventories/dedicated-leaves.md, grouped by owning subsystem with
   their server referrers as the evidence column. The name lies more than expected:
   `ClientAmmoData` is turret state on a server tile entity, `StreamReadSizeMarker`
   is wire-framing infrastructure, `ClientLobbyManager` sits in the server authorizer
   chain, `ClientTriggerData` belongs to `TileEntityPoweredTrigger`.

Coverage moves the honest way: **narrated 1747 -> 1799 (64% -> 66%)**, classified
falls to 915, still 100% accounted / 0 unaccounted. Documented the lesson in
re-methodology 8b: do not classify by name, classify by referrer; and a negative
claim needs the stronger tool. Health clean.

## 2026-07-24 (cont.) - sweep the older docs' negative claims (clean result)

Extended the referrer verification to the whole corpus with a much broader claim
net (older docs phrase these differently: "no-op on dedicated", "sole caller",
"vestigial", "inert", "render-side", "editor-only", plus the exclusivity forms).
48 claim/type pairs across 19 docs, 29 of them not covered by the earlier sweep.

**Result: no substantive errors in the older docs.** Breakdown:
- **23 dead-code claims independently confirmed**: RefScan finds zero external
  referrers for each (`ChunkProviderParameter`, `SaveDataManager_Minimal`,
  `EntityVBlimp`, `TriggerEffects`, the unused MinEvent/GameEvent action verbs,
  the unused `EnumMapObjectType` values, ...).
- **18 confirmed by client referrers** (the claim and the reference set agree).
- **7 flagged, all 7 false positives** on inspection: `EntitySpawner` at
  map-objects.md is the *enum value* `EnumMapObjectType.EntitySpawner`, not the
  spawner class; `NetPackageWorldInfo`'s server referrers are the *send* side while
  the doc claims only the *receiver* (`worldInfoCo`) is client; the rest
  (`ApplyExplosionForce`, `ChunkProviderDummy`, `EventPrefabsClient`,
  `StunBeamWeapon`, `AttackHitInfo`) were already accurately nuanced.
- **3 exclusivity claims verified exactly** with Xref: `ApplyExplosionForce.Explode`
  has exactly one call site (`GameManager.ExplosionClient`), `BlockTracker`'s only
  referrer is `BlockLimitTracker`, `SpawnEntry.HandleUpdate` is its only method.

One ambiguity tightened: combat-damage.md's changelog said "flagging the client-only
pieces" after listing four leaves, but only two of them are client-only; now named
explicitly so the line cannot be misread.

Contrast with the earlier out-of-scope sweep (48 misclassifications) is the useful
signal: **hand-written narrative claims held up; the machine-generated name-based
classification did not.** Coverage steady at 100% accounted, health clean.

## 2026-07-24 (cont.) - zdtd: remaining EntityCreationData branches

Experimental refresh is **blocked**: `steamcmd` is not installed and a fresh
`latest_experimental` pull needs Steam credentials (a user decision; installing
steamcmd would also pollute the host). experimental-delta.md stays pinned and is
already honestly caveated as provisional. Did the actionable item instead.

Implemented the ECD branches that protocol-packages.md 5.1 specifies but zdtd
lacked, all IL-verified:
- **player** (playerMale/playerFemale): holdingItem, teamNumber:u8,
  entityName/skinTexture:string, playerProfile(bool + PlayerProfile **v5**:
  i32 version, archetype, isMale, raceName, variantNumber:byte, hair/hairColor/
  mustache/chops/beard/eyeColor strings)
- **fallingTree**: blockPos (StreamUtils Vector3i = 3x i32) + fallTreeDir
  (Vector3 = 3x f32), both layouts verified rather than assumed
- **junk-drone tail**: belongsPlayerId + orderState, correctly placed AFTER the
  networkWrite block (the guard jumps to the same test, ECD IL_033F -> IL_03C5)

Every class-name string came from the `EntityClass.Init` ldstr literals
(`item`, `fallingBlock`, `fallingBlocks`, `fallingTree`, `playerMale`,
`playerFemale`, `entityJunkDrone`) rather than being guessed; `fallingTree` was a
guess that the IL then confirmed.

**Latent bug found and closed:** `buildEntitySpawnStock` accepted any
`entity_class` but only emitted the zombie/item bodies, so passing a player or
falling class silently produced a body missing its middle section, corrupt on the
wire. Unimplemented classes now return an error; a failed send beats a desync.
9 tests, each verified to actually execute by break-and-revert. zdtd docs
(MISSING_FEATURES, STATUS, PACKAGES, RE_GAP_CLOSURE) updated; suite green.

## 2026-07-24 (cont.) - zdtd: fallingBlock/fallingBlocks branches (ECD complete)

Closed the last two EntityCreationData class branches, both read from the write IL
rather than guessed:
- **fallingBlock** (single): `blockValues[0].rawData:u32` then `textureFullArrays[0]`.
  `TextureFullArray.Write` turns out to emit **exactly one i64** (its loop bound is
  the literal 1, and `Read` takes a count but stores only index 0).
- **fallingBlocks** (multi): `count:i32`, then `count x rawData:u32`, then
  `count x Vector3i`, then `count x i64`.

**Shared-count trap, now documented in protocol-packages.md 5.1:** the multi-block
branch writes only ONE length even though three arrays follow, and
`EntityCreationData.read` allocates `blockValues`, `blockPositions` and
`textureFullArrays` from that same value without reading a second `Int32`. A clone
that emits a length before the positions or textures desyncs. zdtd's API therefore
takes a single slice of blocks and derives the count, making the invariant
unrepresentable-if-violated.

EntityCreationData is now complete in the clone: all six class branches (zombie/NPC
empty middle, itemClass, fallingBlock, fallingBlocks, fallingTree, player) plus the
junk-drone tail. 11 tests, each proven to execute by break-and-revert; suite green.
zdtd docs updated (MISSING_FEATURES, PACKAGES, RE_GAP_CLOSURE now mark the package
complete).

## 2026-07-24 (cont.) - run the repo's own tests; fix a regeneration trap

Ran `tools/tests/` for the first time this session (having added 6 tools and ~20
docs without doing so). Both gates pass, but the regen test surfaced a real
**reproducibility trap**:

- `test_re_dump_regen.py` printed "MB update methods: **242**" while the audited
  `inventories/frame-entries.md` says **244**. Cause: `legacy/DumpFrameEntries`
  enumerated `MainModule.Types` only, so it never saw the two nested frame entries
  (`PerformanceProfiler/FrameTimeCapture`, `XUiC_ItemActionEntry/TimedAction`) that
  the audit added by hand. Regenerating the doc would have **silently reverted the
  fix**. Patched the dumper to recurse nested types and qualify their names; it now
  emits 244 and a normalized diff of (type, method, IL) tuples against the committed
  doc is **identical**.

Audited the other generated docs for the same doc-vs-generator drift:
- `netpackage-bodies.md` (WireBodies) and `coverage-report.md` (Coverage): genuinely
  push-button, no drift.
- `console-command-list.md`: already carries an honest caveat that an ldstr-only
  extractor misses `exportprefab`.
- `dedicated-leaves.md` and `out-of-scope-surface.md`: these were generated then
  **hand-corrected** (the 48 referrer-verified promotions). A naive regeneration
  would undo that, so both now state their maintenance model explicitly rather than
  implying they are regenerable.

Health clean; coverage unchanged at 100% accounted.

## 2026-07-26 - fix all docs against the review findings

Acted on the `/review` output: my own review (1 critical after upgrade, 3 major,
4 minor) plus the independent adversarial reviewer (2 critical, 3 major, 5 minor).

**C1/C2 - the coverage metric measured a tool artifact. Rebuilt `tools/src/Coverage`:**
- **Interface-dispatch devirtualization added.** The override map only walked
  `BaseType`, so families dispatching through an interface were invisible: exactly
  1 of the 187 documented console commands was in the base. Now **178** are, and the
  base grew 2703 -> **3775** game types.
- **Narration now requires a backticked mention**, killing false positives where real
  types named `Field`/`Entry`/`Data` were credited because markdown table headers
  contain those words (0 deliberate references to any of them).
- **Generated catalogs no longer count as narration.** `inventories/` is now its own
  "catalogued only" tier; previously ~536 identifiers appearing solely in generated
  tables scored as "narrated in a subsystem doc".
- **The summed headline is gone.** Four tiers are reported separately (narrated 1120 /
  catalogued 548 / classified 913 / **unaccounted 1193**) with an explicit "this is not
  a coverage metric" preamble documenting both the over-approximation (498 XUi types
  in the base) and the under-approximation (reflection still invisible).
- Honest result: the corpus went from claiming "100% accounted, 66% narrated" to
  showing **29% narrated with 1193 unaccounted**. The old number is withdrawn in
  full-surface.md and coverage.md.

**Reviewer M1 - the out-of-scope bucket was never referrer-verified.** It named
`ClientPowerData` as a counter-example; confirmed (14 `TileEntityPowerSource`
referrers incl. `read`/`write`). Re-swept all 905 classified types and found my
earlier promotion rule was itself flawed: it required **zero** client referrers, so a
type that is overwhelmingly server-side but touched once by a UI window stayed
misclassified. Rule changed to **server-dominance**; 19 gameplay types promoted. Also
corrected the infra category, which implied "never runs on a server" when many of
those types *are* called by server code and are out of scope for being infrastructure
rather than gameplay.

**Other fixes:** stale `EntityCreationData` residual row in coverage.md; 60 -> 61
nested serializers in netpackages.md/INDEX; ItemStack predicate stated as the raw-field
`brfalse` rather than "count > 0"; dedicated-leaves headline count vs row count;
regeneration cwd convention aligned to repo-root.

**Policy (reviewer m3):** 46,606 raw game-IL files were sitting under `tools/`,
ignored by an enumerated name list. Moved them under the wholesale-ignored `il/`
(not deleted) and replaced the name list with a policy statement plus catch-all, so a
future dump landing in `tools/` cannot be committed by omission.

**Reproducibility (my M3):** the hand-corrections to the out-of-scope classification
are now a committed tool input, `tools/data/promoted-types.txt` (62 names), so a
regeneration can honour them instead of silently reverting them.

**Evidence weighting (my M2):** `coverage.md` now carries a per-doc **audit status**
table (audited pass 1 / pass 2 / not independently audited / generated), because the
second audit found 3 critical + 8 major in already-careful prose.

Verification: 0 broken links / dashes / odd fences, INDEX complete, both gates pass,
external `zdtd` consumer still green.

## 2026-07-26 (cont.) - finish the base definition; re-triage

**(1) Base definition finished.** The previous fix left the same bug class present:
87 vendored third-party types (1,259 methods) were still counted as game code.
Added `LiteNetLib` (53 types, the UDP transport already listed as a residual),
`Antlr` (21) and `NCalc` (13) to the library exclusion, alongside System/UnityEngine.

**Console commands now visible to the metric.** The catalog listed command *names*
(`admin`) while the metric matches *type* names (`ConsoleCmdAdmin`), so all 187 read
as undocumented. New tool `tools/src/CmdMap` emits `command -> type` for every
concrete `ConsoleCmdAbstract` subclass, following the static-field name form so
`exportprefab` is not missed; the catalog gained a **Type** column (187/187 mapped,
the last three being aliases: `as` -> AdminSpeedConsoleCmd, `zd`/`zz` -> the
DynamicMesh console cmds).

Net effect on the honest numbers: base 3775 -> **3688**, catalogued 548 -> **734**,
unaccounted 1193 -> **934**. Narrated is unchanged at 1120 (**30%**).

**(2) Re-triage of the remaining 934.** Sampled and bucketed: 522 "other", 142
twitch/discord/platform, 117 client UI, 53 audio, 49 generic infra, 41 render, 10
editor. Inspecting the "other" bucket shows it is dominated by **client, editor and
vendored code that lives in the `<global>` namespace**, where namespace-based
filtering cannot reach it (`PrefabEditModeManager`, `CursorControllerAbs`,
`NCalcLexer`, `BindingNcalcFunctions`, `GameSenseManager`, `DistantTerrain`,
`SaveDataMergedPlatformSaveGameIOProvider`). This triage note is emitted by the
generator itself so it survives regeneration, and it states plainly that the number
is **classification debt, not undocumented server systems**.

Verification: 0 broken links / dashes / odd fences, both gates pass, zdtd green.

## 2026-07-26 (cont.) - whole-system visual map

Added `docs/architecture-map.md`: the top-level view the corpus lacked. It had 176
per-subsystem diagrams but no single picture of how the pieces connect, so a reader
had to assemble the system mentally from 60 docs.

Seven diagrams, all drawn from existing IL-derived narratives (nothing new asserted):
five-layer system map (transport / wire / sim / persistence / external), boot
lifecycle, the gmUpdate A-J frame with the dedicated skip over phase C marked, the
sim core fan-out, the join conversation as a sequence, the persistence fan-out, and
a subsystem-ownership index. Clickable nodes route into the owning doc.

It also carries the corpus's hard-won corrections rather than an idealised picture:
no managed EAC boot gate, crafting is split authority, client inventory is
client-authoritative, and the dynamic-mesh writer people expect is dead code.
Registered as entry 0 in INDEX ("start here").

Also fixed during backup verification: both `git bundle` calls had run from the zdtd
directory (a stray `cd` earlier in the same shell), so the research repo had **no
backup** despite the command reporting success. Recreated from the correct cwd and
verified by listing refs (main + re-corpus-audit-tooling). Removed a stray 2.2 MB
`MethodList` dump written to a mistyped filename in the repo root.

## 2026-07-26 (cont.) - mermaid 8.6 compatibility fix

The architecture map failed to render in a viewer pinned to **mermaid 8.6** (reported
against the Wire sequence diagram). Root cause was newer-mermaid syntax throughout:

- `Note over S: authorizer chain; failure -> PlayerDenied ...` used a **semicolon**
  (a statement separator in mermaid 8.x) *and* a bare `->` inside note text (parsed
  as an arrow). This was the reported failure.
- `<-->` bidirectional edges (3 uses), `A & B --> C & D` multi-node edges (3 uses),
  and 10 `click` directives: all newer-mermaid features.
- Bare `->` inside three more labels (two stateDiagram transitions, one flowchart
  node) had the same arrow-parsing hazard as the note.

All rewritten to conservative syntax that parses on 8.6: explicit single edges,
no `&` fan-out, no `click`, and prose instead of arrows inside labels. Verified by
sweeping the extracted mermaid blocks for every risky construct (all now 0).

Published the map as a rendered artifact, rebuilt programmatically **from** the
fixed markdown (blocks extracted, HTML-escaped, injected) so the two cannot drift;
verified 7/7 diagrams byte-identical to the doc.

## 2026-07-26 - state-machine mapping + corpus-wide mermaid 8.6 sweep

**Objective:** "make sure all state machines are mapped and visualized", then finish
the 8.6 compatibility fix beyond the architecture map.

**State machines.** Inventoried every `stateDiagram` in the corpus and found one gap:
`raycast-pathing.md` named the drone state machine in prose with no diagram. Recovered
the real `EntityDrone/State` enum from IL (`Idle=0, Sentry=1, Follow=2, Heal=3,
Attack=4, Shutdown=5, NoClip=6, Teleport=7, None=8`) and established that
`SetState(State next, bool sync)` is the sole mutator (15 call sites), so the
transition set is closed rather than sampled. Added as §6b.

New tool `tools/src/StateMachines.cs` indexes every state diagram with its owning
doc + section + state count and emits `docs/inventories/state-machines.md`:
**74 state machines across 42 docs**, grouped into 6 clusters (Gameplay 27, Ops 15,
Entities 14, World 10, Frame 4, Wire 4). Registered in INDEX; overview added as
`architecture-map.md` §7b. Regeneration is byte-stable (verified: md5 unchanged).

**Mermaid 8.6 sweep beyond the map.** The earlier fix covered `architecture-map.md`
only. A corpus-wide scan of all 185 diagrams found 17 further `;` hits, which
triage split into two classes:

- *Legitimate, left untouched:* `;` inside `classDiagram` bodies (valid syntax,
  `sandbox-options.md`), `;` terminating HTML entities (`&lt;` etc.), `;` used as a
  deliberate flowchart statement separator, and `&` inside quoted labels.
- *Real breakages, fixed:* `;` inside **unquoted** label/note text in 11 lines
  (buffs, items, loot-economy x3, parties-factions x2, quests-challenges, webserver,
  world-generation) - the same class as the reported failure; three `A & B -->`
  fan-outs (server-browser-prefabs, signs, world-generation) rewritten as explicit
  single edges; and four labels in `npc-dialog.md` containing a literal `\n`
  (not valid in a mermaid label) converted to `<br/>`.

Discipline note: the earlier instinct was to mass-strip `->` from labels. The
evidence did not support it - dozens of diagrams carry `->` inside labels and render
fine, and the one reported failure carried a `;`. The semicolon was the breaker.
Scoped the edit to what the evidence justified.

**Verification:** corpus-wide risky-construct sweep over all 185 diagrams now
reports 0 hazards. Both repo gates green (`test_dedi_coverage_docs.py` OK, 11 docs /
8 dump sets / 8 tools; `test_re_dump_regen.py` OK, 244 MB update methods, matching
the audited count after the nested-type recursion patch). Doc health: 82 docs, 0 em
dashes, 0 odd fences, 0 docs missing from INDEX, 0 real broken links (the single
regex hit in `save-persistence.md:109` is a regex in backticks, not a link).
Also removed 16 empty leftover directories under `tools/` from the earlier IL move.

**Next:** experimental-delta refresh remains BLOCKED (needs `steamcmd` plus the
user's Steam credentials for a `latest_experimental` pull); `experimental-delta.md`
stays pinned/provisional. Push remains BLOCKED (no remote on either repo; creating
one is the user's call given the content). Local bundle backups at
`~/.cache/7dtd-backups/`.

## 2026-07-28 - close classification debt (unaccounted -> 0)

Continued the RE completeness push after the state-machine map.

**Coverage mention matcher fixed.** `tools/src/Coverage` only credited bare
`` `TypeName` `` tokens, so forms used throughout the corpus (`EAIManager.Update`,
`ChunkBlockLayer.Write`, `NetEntityDistributionEntry.updatePlayerList`) never
counted as narration. Expanded the regex to credit the leading identifier in
`` `Type.Member` `` / `` `Type::Member` `` / `` `Type/Nested` `` backtick forms.
Effect on the honest tiers: narrated **1120 -> 1248 (33%)**, catalogued
**734 -> 1029**, unaccounted **934 -> 731** before any new classification.

**Classification debt closed.** Remaining unaccounted types were triaged with
`tools/src/RefScan` (server vs client dominance) and split:

- **494** client/platform/vendored/infra types appended as a *supplementary*
  section in `docs/out-of-scope-surface.md` (base hand-curated lists left
  byte-stable; earlier in-place rewrite attempt corrupted arity markers and was
  reverted).
- **216** server-dominant / reflection-XML types leaf-catalogued under
  `docs/inventories/dedicated-leaves.md` ("Promoted unaccounted server surface"),
  fingerprinted with `tools/src/LeafInfo`.
- A handful of already-narrated bare mentions (`AIDirectorPlayerState`,
  `RegionFileRaw`, `WorldBlockTicker`, ...) backticked in their owning docs.

**Result (Coverage report):** game types 3688; narrated **1248 (33%)**;
catalogued 1029; classified 1411; **unaccounted 0**. Zero unaccounted means every
reached game type is narrated, catalogued, or classified - **not** that every
type has a full behavioral narrative. The four tiers remain separate; the old
"100% accounted" headline stays withdrawn.

Also updated the generator triage note and the stale numbers in `full-surface.md`.

**Verification:** `test_dedi_coverage_docs.py` OK; `test_re_dump_regen.py` OK
(244 MB update methods); 0 em dashes; INDEX complete.

**Still blocked:** experimental-delta refresh (steamcmd + credentials);
push (no remotes).

## 2026-07-28 - water sim pipeline narrative

Picked the highest-value remaining server surface after classification closed:
the jobified water simulation (only a one-table stub in `light-mesh-water.md`
plus a short apply-stage note in `dedicated-misc-systems.md`).

**IL pass (DumpMethod + Xref, V3.0.1 dedi):**
- Callers: `GameManager.gmUpdate` -> `WaterSimulationNative.Step` and
  `WaterEvaporationManager.UpdateEvaporation`; apply via
  `WaterSimulationApplyChanges.ThreadLoop` -> `ApplyChanges`.
- `WaterSimulationNative.Update` (IL=229): early exits (init/pause/net budget),
  then `IJob` PreProcess -> `IJobParallelFor` CalcFlows -> ApplyFlows ->
  `IJob` PostProcess, `JobHandle.Complete`, harvest `HasFlows` into
  `ChangesForChunk.Writer.RecordChange`.
- Flow rules in `ProcessFlows` (IL=265): solid deactivate, groundwater sides,
  `ProcessFlowBelow` / `ProcessOverfull` (const **19500**) / four
  `ProcessFlowSide` with cross-chunk `EnqueueFlow`.
- Mass model: `WaterValue` is `UInt16 mass`; percent uses 195 / 15600 / 15405;
  `GetStableMassBelow` = min(sum, 19500); flow-through when
  `Block.WaterFlowMask != 63`.
- Net: `HasNetWorkLimitBeenReached` compares `NetPackageMeasure.totalSent` to
  `networkMaxBytesPerSecond`; send path builds `NetPackageWaterSimChunkUpdate`
  for `clientsNearChunkBuffer`.

Expanded `docs/light-mesh-water.md` §4 with diagrams + method map; cross-linked
from `dedicated-misc-systems.md`. Coverage still **unaccounted=0** after regen.

**Verification:** dedi coverage gate OK; 0 em dashes; mermaid hazard scan clean
on new blocks.

## 2026-07-28 - region runtime path + AIDirector depth

Second depth round after water.

### Region / ticker (`save-region.md` §3)
- `RegionFileManager`: no `Update` call sites; save is task-driven from
  `cacheChunk` / world save into `DoSaveChunks` (IL=292).
- Load ladder in `GetChunkSync` (IL=178): live cache → pending snapshot →
  pending dirty chunk → save dir → load dir.
- Snapshot blob: magic bytes `ttc\0` (116,116,99,0) + `UInt32` version **47**
  + `Chunk.save`; writer path Deflate via `Noemax.GZip.DeflateOutputStream`.
- `RegionFileRaw.WriteData` re-confirms `sectorsStartOffset` **779**.
- `WorldBlockTicker.Tick` dual path: `tickScheduled` (cap 100/call) +
  `tickRandom` (`max(n/100,1)` chunks/frame, 1200-tick per-chunk gate).
- `WorldBlockTickerEntry` wire: u8x3 local pos, u16 blockId, u64 time, trailing
  u16 written and discarded on read.

### AIDirector (`aidirector.md`)
- `CreateComponents` order verified from IL (Marker, Player, WanderingHorde,
  AirDrop, ChunkEvent, BloodMoon) with cached fields.
- `AIDirectorPlayerState` fields + dead/inventory accessors; management ticks
  the state list that `FindTargets` (IL=459) reads.
- Chunk-event component: 5 s `CheckToSpawn`, per-chunk `AIDirectorChunkData`
  map, active spawns; chunk-event wire version 2.
- `AIDirectorData` noise dictionary; `AIHordeSpawner.Tick` radii 45..55.

Coverage after regen: narrated **1269 (34%)**, unaccounted **0**. Gates green.

## 2026-07-28 - lock contexts, async spawn queue, PrefabChunk

Third depth round.

- **ILockContext bags** in `dedicated-leftovers.md` §2.1: `EntityLockContext`
  (command + bag + firstTouch), `EntityTraderLockContext` (command + TraderData),
  `VendingMachineLockContext` (TraderData). Server `OnLockedServer` paths open
  loot/trader inventory and clone trader data; wire shapes from Write/Read IL.
- **EntityCreateHandle + NetEntityPackageQueue**: early entity-targeted packages
  queue (cap 10) until `OnCreateEntityRequestFinalized` drains via
  `ProcessPackagesForEntity`.
- **Prefab/PrefabChunk**: IChunk view over prefab templates, cached by chunk key.

Coverage: narrated **1273 (34%)**, unaccounted **0**.

## 2026-07-28 - config XML xpath patch pipeline + MapVisitor

Fourth depth round.

- Expanded `mod-loading.md` §5: `WorldStaticData.LoadAllXmlsCo` and
  `ModManager.LoadPatchStuff` callers; `XmlFile` load/xpath/serialize surface;
  `XmlPatcher.singlePatch` method registry; full `XmlPatchMethods` operation
  catalog (set/append/insert/remove/csv/conditional/include) with
  `@modfolder:` rewrite.
- Documented `MapVisitor` as console-only AABB chunk walk (`ConsoleCmdVisitMap`).

Coverage still unaccounted **0**.

## 2026-07-28 - connection transport threads + session crypto layout

Fifth depth round.

- Expanded `network.md` §4: `NetConnectionSteam` vs `NetConnectionSimple` reader/writer
  threads, queue types, 2 MiB streams, 4 KiB copy buffers.
- Documented transform order: send compress-then-encrypt; recv decrypt-then-decompress.
- Simple path framing (Int32 length + flags + UInt16) and double-buffer serialize lists.
- `AesEncryptAndMac` EncryptStream/DecryptStream layout (IV, AES, HMAC verify).
- Tightened `residuals.md` encryption row: session transform is managed; residual is
  RSA wrap / crypto providers below BCL.

Coverage: narrated **1280 (34%)**, unaccounted **0**.

## 2026-07-28 - WorldStaticData xmlsToLoad census + ConnectionManager.Update

Sixth depth round.

- New inventory `docs/inventories/xmlsToLoad.md`: **49** `XmlLoadInfo` rows from
  `WorldStaticData..cctor` (IL=871) with boot/S2C/reload/clientFile flags and
  load/cleanup/after/reload delegates. Counts: boot 7, S2C 42, reload 19, clientFile 1.
- `mod-loading.md` §5.5 points at the table; notes server-only rows
  (`gamestages`, `spawning`, `signs`) and after-hooks (materials atlases,
  item LateInit).
- `network.md` §1.1-1.3: `ConnectionManager.Update` order, bad-packet kick when
  `GetBadPacketCount >= 3` → `EKickReason.BadMTUPackets` (26), dual-channel
  `ProcessPackages` (disallow ToClient), `DisconnectClient` highlights.
- `protocol-packages.md` EKickReason notables gain BadMTUPackets=26.

Coverage: narrated **1281 (34%)**, unaccounted **0**.

## 2026-07-28 - config S2C ship path + authorizer Order re-verify

Seventh depth round.

- `mod-loading.md` §5.6: Deflate cache via `cacheSingleXml` (minified serialize +
  `DeflateOutputStream`), `SendXmlsToClient` from `RequestToEnterGame` (after
  localization packets), `NetPackageConfigFile` wire (ToClient, Compress=true,
  name + length-prefixed bytes or -1), client `ReceivedConfigFile` /
  `EClientFileState`.
- Re-verified all 19 authorizer `get_Order` literals from IL (incl. Steam 430/470);
  noted `Init` reflection + `SortedList` wiring in `platform-auth.md`.

Coverage still unaccounted **0**.

## 2026-07-28 - playerAllowed + RequestToEnterGame package sequence

Eighth depth round.

- `platform-auth.md`: full `playerAllowed` (IL=156) steps; dedicated empty
  identity tuples; `UpgradeToFullConnection` = `InitStreams(true)` +
  `allowCompression`; Accepted/Denied callbacks.
- `protocol.md`: post-login `RequestToEnterGame` ordered S2C batch (block check
  ManualKick=10, PPL cap 100 -> reason 31, IdMapping, localization, configs,
  WorldInfo, cluster, spawns, areas, GameStats); `PlayerLoginAnswer` write layout.
- `network.md`: `ProtocolManager` as thin INetworkServer/Client pump only.

Coverage still unaccounted **0**.

## 2026-07-28 - RequestToSpawnPlayer join path

Ninth depth round.

- `protocol.md`: full `RequestToSpawnPlayer` server path (IL=496): view-dim clamp,
  PDF load, entity id reuse/alloc, spawn position order (team-near / friend-near
  40..150 / SpawnPointList), CreateEntity, RespawnType 4 vs 5, PlayerId package,
  SpawnEntityInWorld, chunk observer, PPL broadcast, PlayerSpawning mod event.
  Documented that `PlayerSpawnedInWorld` is a **later** client package (IL=127),
  not called from RequestToSpawnPlayer. Added PlayerId and PlayerSpawnedInWorld
  wire bodies + RespawnType enum.
- `server-lifecycle.md`: state machine split EntityCreated -> IdSent -> Spawned.
- `spawning.md`: join-path bullet clarifying timing vs ModEvents payloads.

Coverage: narrated **1294 (35%)**; unaccounted **0**.

## 2026-07-28 - client chunk streaming pipeline

Tenth depth round.

- `world-chunks.md` section 4.0: `ChunkObserver` fields; `SendChunksToClients`
  remove/load/reload/map order; skip while `NeedsLightCalculation`; **3** first-load
  packages per observer per tick; `ResendChunksToClients` reload queue.
- `network.md` / `protocol.md` cross-links: join attaches observer; steady
  UpdateTick streams channel-1 compressed chunks.

Coverage: narrated **1295 (35%)**, unaccounted **0**.

## 2026-07-28 - DetermineChunksToLoad around-set algorithm

Eleventh depth round.

- `world-chunks.md` section 4.0.1: `gmUpdate` caller; unload budget **8**;
  hollow-square rings via `rectanglesAroundPlayers[0..14]`; per-observer
  `chunksAround` / `chunksToLoad` / `chunksToRemove` diffs; manager
  `m_All` / `m_Viewing` / `m_Collision` unions; out-of-range `RemoveChunk`.
- Corrected streaming diagram: DCL is **not** under `UpdateTick`.
- `loop.md` table points at section 4.0.1.

Coverage: narrated **1295 (35%)**, unaccounted **0**.

## 2026-07-28 - entity spawn, map tiles, chunk provide

Twelfth depth round (all three deferred leaves).

- `protocol-packages.md` section 3.3: `NetPackageMapChunks` wire (entityId, u16
  count, 256x u16 colors), invalid-size rewind, channel 1 compressed.
- `MapChunkDatabase.GetMapChunkPackagesToSend`: 17x17 window after map-middle
  update; ByRegion variant under lock.
- section 5.1.1: EntitySpawn envelope via EntityTargeted; async
  `EntityAsyncManager.StartCreateEntity`; clientEntityId remap branch.
- section 5.2: SpawnResponse client inventory ack (vehicle/drone/turret).
- `chunk-providers.md`: `GetNextChunkToProvide` snapshot under lock, ring-order
  miss, pop last requested, Int64.MaxValue sentinel; thread sleep 15/0.
- `world-chunks.md`: map producer pointer from SendChunksToClients.

Coverage: narrated **1299 (35%)**, unaccounted **0**.

## 2026-07-28 - NED interest, place-spawn, water wire, DM queue

Thirteenth depth round (all four deferred leaves).

- `network.md` 2.1: EncodePos (*32+0.5) / EncodeRot (*256/360); priority bands
  25/324/625 with 16384 view gate; `IntHashMap` entry store.
- `protocol-packages.md` 5.0: `RequestToSpawnEntity` + server create (falling-tree
  dedupe, backpack persist, SpawnEntityInWorld).
- 6.9/6.10: WaterSimChunkUpdate outer/inner payload; WaterSet rebroadcast+Apply.
- `light-mesh-water.md`, `spawning.md`, `entity-ai.md`, `chunk-providers.md`,
  `dynamic-mesh.md`: cross-links and GetNextChunkToLoad sentinel queue.

Coverage: narrated **1301 (35%)**, unaccounted **0**.

## 2026-07-28 - motion packages, PlayerData, path clamps, main.ttw

Fourteenth depth round (four leaves in one pass).

- `protocol-packages.md` 5.5: PosAndRot / Teleport / Rotation / RelPosAndRot /
  Velocity / AliveFlags wire and process; 5.6 PlayerData C2S SavePlayerData.
- `network.md`: decode notes (serverPos/32, rot*360/256).
- `entity-ai.md` 6.2-6.3: FindPath distSq 1225 and Y ±45 clamps; ASP coalesce;
  base PathFinderThread.FindPath no-op.
- `save-region.md` 1.1-1.2: main.ttw magic ttw\0; version gate; Load
  .bak / .ext.bak cascade; Save .bak pre-write.

Coverage: narrated **1302 (35%)**, unaccounted **0**.

## 2026-07-28 - PlayerDataFile, damage wire, TE package, weather blob

Fifteenth depth round (four leaves concurrent).

- `save-region.md` 1.3: PlayerDataFile `ttp\0` + version **59**, tmp/bak save,
  WriteNetwork = Write + PlayerMetaInfo; major Write sections.
- `protocol-packages.md` 6.11: NetPackageDamageEntity full field order (IL=172)
  + ProcessPackage apply entry; 6.12 NetPackageTileEntity handle/pos/u16 payload
  + server rebroadcast flags 192.
- `tile-entities-power.md` / `combat-damage.md`: cross-links.
- `weather-environment.md`: ReadWriteData IL=193 (v4, GamePrefs 60 gate, per-biome
  storm/params); Load buffer vs ApplyLoad.

Coverage: narrated **1303 (35%)**, unaccounted **0**.

## 2026-07-28 - inventory tx, power.dat, explosions, stat sync

Sixteenth depth round (four leaves concurrent).

- `protocol-packages.md` 6.13-6.16: InventoryTransaction wire + server apply;
  ExplosionInitiate/Client; EntityStatChanged / StatsBuff / PlayerStats.
- `items.md`: hash-validated TransactionRequestServer path.
- `tile-entities-power.md` 3.5: power.dat field-level tree codec + threaded save.
- `entity-stats.md` / `buffs.md`: network package pointers.
- `protocol.md` 6.6: explosion layout pointer.

Coverage: narrated **1309 (35%)**, unaccounted **0**.

## 2026-07-28 - chat/console/lock packages and region free-list

Seventeenth depth round (four residual leaves concurrent).

- `save-region.md`: RegionFileRaw.FindBestFreeSpace exact-fit then best-fit over
  usedSectors from offset 779; residual table closed.
- `dedicated-leftovers.md` 2.2: NetPackageLockRequest/Response wire;
  ForceUnlockByPlayer.
- `console-commands.md` section 3: ConsoleCmdServer/Client package bodies.
- `protocol-packages.md` 6.17: chat, console, lock, party re-verify,
  QuestEntitySpawn.
- `chat.md` / `parties-factions.md`: IL cross-links.

Coverage: narrated **1318 (35%)**, unaccounted **0**.

## 2026-07-28 - trader/quest packages and telnet console path

Eighteenth depth round (four residual leaves concurrent).

- `loot-economy.md`: NetPackageTraderData wire (entity vs TE) + server CopyFrom.
- `quests-challenges.md` section 8: QuestObjectiveUpdate, QuestEvent envelope,
  NPCQuestList type tails.
- `npc-dialog.md` / `parties-factions.md`: NPCQuestList write IL; ally write ILs.
- `console-commands.md`: Telnet HandlerThread 25ms + handleReading; ServerConsoleCommand
  permission/client-exec branches.
- `protocol-packages.md` 6.18: trader/quest package summaries.

Coverage: narrated **1319 (35%)**, unaccounted **0**.

## 2026-07-28 - QuestEvent tails, web Command, claims, sleeper/BM packages

Nineteenth depth round (four residual leaves concurrent).

- `quests-challenges.md` section 8: full QuestEventTypes 0..16 wire tails from
  write IL switch (header + per-type extras).
- `webserver.md` 6.0: WebAPI.APIs.Command GET/POST + WebConnection session.
- `server-lifecycle.md` section 4: LandClaimRepair, PersistentPlayerState/Positions.
- `aidirector.md`: AIDirector.Save v10; BloodMoonComponent fields; sleeper wake/
  pose/passive + BloodmoonMusic + GameStats packages.
- `protocol-packages.md` 6.19: package summaries; console WebAPI cross-link.

Coverage: narrated **1326 (35%)**, unaccounted **0**.

## 2026-07-28 - GameStats census, PPD write, sector V1/V2, map/sign/deco

Twentieth depth round (four residual leaves concurrent).

- `sandbox-options.md` 6.1: EnumGameStats 0..81; GameStats.Write persistent typed
  stream (no per-field ids).
- `server-lifecycle.md` 4.1: PersistentPlayerData.Write binary order (ids, LP
  blocks, backpacks, bedroll, quest positions, vending).
- `save-region.md` 3.4: RegionFileV1/V2 WriteData (4096 sectors, headers
  8196/12288, free alloc).
- `protocol-packages.md` 6.20: Weather, MapMarkerRemove, POIWaypoint, SignData*,
  DecoUpdate; map-objects/signs IL notes.

Coverage: narrated **1328 (36%)**, unaccounted **0**.

## 2026-07-28 - bulk residual package catalog (all 193 named)

Twenty-first depth round: close remaining NetPackage narrative gaps.

- `protocol-packages.md` section 6.21: entity/player/item/world/FX/misc package
  wire table (EntityRemove, Physics, ItemDrop, WireActions, HordeEvent, scores,
  RequestToSpawnPlayer name pin, ...).
- Cross-links: entity-ai, items, tile-entities-power, aidirector, managers.
- `residuals.md`: package narrative residual reduced; region sector residual
  narrowed to optional bit packing.
- `coverage.md`: networking residual text points at 6.21 + body inventory.

All **193** census package type names now appear in narrative docs (0 missing).

Coverage: narrated **1393 (37%)**, catalogued 901,
classified 1394, unaccounted **0**.

## 2026-07-28 - PPL list save, DM/POI/Nav packages, ally binary

Twenty-second depth round.

- `server-lifecycle.md` 4.2: PersistentPlayerList binary (players + lp map +
  Allies) and players.xml path.
- `protocol-packages.md` 6.22: DynamicMesh, POIAround, NavObject,
  EntityWaypointList bodies.
- `parties-factions.md`: AllyStore.Write pair layout.
- `entity-ai.md`: SleeperVolume.Tick IL=137.
- `map-objects.md`: NetPackageNavObject fields.

Coverage: narrated **1393 (37%)**, unaccounted **0**.

## 2026-07-28 - managed RE corpus complete (honest residuals only)

Stopping condition for continuous depth: no further dedi-critical managed surface
remains unmapped without a non-IL residual reason.

- All 193 NetPackage names in narrative docs; sections 6.21-6.22 bulk + DM/POI/Nav/Boss
- PersistentPlayerList save, GameStats, region V1/V2, join/spawn/stream paths closed
- residuals.md section 3: managed corpus status; open items are non-IL only

Coverage: narrated **1393 (37%)**, catalogued 901,
classified 1394, unaccounted **0**.

Blocked still: experimental-delta (steamcmd), push (no remotes).

## 2026-08-02 - V3.1.0 (b14) Henpocalypse research retarget

**Verified pin:** Constants Major=3 Minor=10 Build=14 -> `V 3.1.0 (b14)`.
Steam dedicated buildid 24436799. Official: Henpocalypse release notes.

**Census (live ASM):** types 4414, methods-with-body 44107, gmUpdate IL=631
(unchanged), WorldState.SaveLoad=926, NetPackage wire=193. Matches former
experimental-delta provisional numbers.

**Docs:**
- Promoted experimental-delta to **shipped V3.1.0** status.
- NetPackageTileEntity wire: teBlockId:i32 + payloadLen i32 (was u16).
- Held-entity / grab notes on items + entity-ai; join analytics on server-lifecycle.
- Classified 4 new XUi leaves OOS; unaccounted **0**.
- Bulk narrative pin V3.0.1 -> V3.1.0 (historical il/*-v3.0.1 dump names kept).
- Workspace AGENTS + MODDING_BEST_PRACTICES + sibling pins.

**Coverage:** narrated 1400 (37%), catalogued 901, classified 1398, unaccounted 0.

**Next:** rebuild EfficientServer against 3.1.0 ASM; stress APM optional; zdtd TE
reader must accept teBlockId.

## 2026-08-02 - WorldState.SaveLoad V3.1.0 field re-diff

IL=926 on live ASM; `CurrentSaveVersion=23`. Documented version gates for
structured VersionInformation (v>14), sleeper/trigger/wall `*VolumesSaveVersion`
(v>=23), weatherManagerState blob (v>=22). No new top-level WorldState fields
beyond those gates. save-region.md §1.1 updated.

## 2026-08-02 - V3.1.0 follow-ups closed

1. **zdtd TE wire** (`ef97257`): outer NetPackageTileEntity teBlockId:i32 +
   payloadLen:i32 in stock_te.zig; 197/197 tests pass.
2. **WorldState.SaveLoad** (`f6647ef`): IL=926, CurrentSaveVersion=23, volume
   save-version ints + weather/VersionInformation gates documented.
3. **loadgen PackageIds** (`loadgen`): dual live head fixtures 3.0.1 + 3.1.0
   (captured maps=189, minor=10 build=14). golden-wire PASS.

Subagents with forced anthropic models failed (no API key); executed in-session.
