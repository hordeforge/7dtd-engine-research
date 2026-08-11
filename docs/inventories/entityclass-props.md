# EntityClass prop-name constants (V3.1.0 b14)

**Kind:** raw reference table (not primary narrative).
**Source:** `EntityClass::.cctor` (IL=394) - each row is a
**Hub:** [`INDEX.md`](../INDEX.md).  
`ldstr <value>` + `stsfld String EntityClass::PropX` pair; non-string
statics (class ids, `FastTags`) listed at the end. Regenerate with
`tools/bin/DumpMethod.exe <asm> EntityClass .cctor`.

**187 rows: 167 `ldstr`+`stsfld` string pairs + 20 non-string statics.**

These are the **XML property names** read by `Entity.*CopyProperties
FromEntityClass` ([entity-ai.md](../entity-ai.md) D8.6-D8.7) and the
spawn/config paths. Note the dashes: `AITask-1`, `AITarget-1`; the
custom-command keys are `CustomCommandName1..10` etc. (the static
concatenated with the index).

| Field | Literal |
|---|---|
| `PropAIFeralSense` | `AIFeralSense` |
| `PropAIGroupCircle` | `AIGroupCircle` |
| `PropAINoiseSeekDist` | `AINoiseSeekDist` |
| `PropAIPackages` | `AIPackages` |
| `PropAIPathCostScale` | `AIPathCostScale` |
| `PropAISeeOffset` | `AISeeOffset` |
| `PropAITargetTask` | `AITarget-` |
| `PropAITask` | `AITask-` |
| `PropAltMats` | `AltMats` |
| `PropArchetype` | `Archetype` |
| `PropArmsExplosionDamageMultiplier` | `ArmsExplosionDamageMultiplier` |
| `PropAttackTimeoutDay` | `AttackTimeoutDay` |
| `PropAttackTimeoutNight` | `AttackTimeoutNight` |
| `PropAvatarController` | `AvatarController` |
| `PropBuffs` | `Buffs` |
| `PropCanBigHead` | `CanBigHead` |
| `PropCanClimbLadders` | `CanClimbLadders` |
| `PropCanClimbVertical` | `CanClimbVertical` |
| `PropCensor` | `Censor` |
| `PropChestExplosionDamageMultiplier` | `ChestExplosionDamageMultiplier` |
| `PropClass` | `Class` |
| `PropColliders` | `Colliders` |
| `PropCompassDownIcon` | `CompassDownIcon` |
| `PropCompassIcon` | `CompassIcon` |
| `PropCompassUpIcon` | `CompassUpIcon` |
| `PropCrouchType` | `CrouchType` |
| `PropCrouchYOffsetFP` | `CrouchYOffsetFP` |
| `PropCustomCommandActivateTime` | `CustomCommandActivateTime` |
| `PropCustomCommandEvent` | `CustomCommandEvent` |
| `PropCustomCommandIcon` | `CustomCommandIcon` |
| `PropCustomCommandIconColor` | `CustomCommandIconColor` |
| `PropCustomCommandName` | `CustomCommandName` |
| `PropDanceType` | `DanceType` |
| `PropDestroyBlockBehavior` | `DestroyBlockBehavior` |
| `PropDismemberMultiplierArms` | `DismemberMultiplierArms` |
| `PropDismemberMultiplierHead` | `DismemberMultiplierHead` |
| `PropDismemberMultiplierLegs` | `DismemberMultiplierLegs` |
| `PropDropInventoryBlock` | `DropInventoryBlock` |
| `PropEntityFlags` | `EntityFlags` |
| `PropEntityType` | `EntityType` |
| `PropExperienceGain` | `ExperienceGain` |
| `PropExplodeDelay` | `ExplodeDelay` |
| `PropExplodeHealthThreshold` | `ExplodeHealthThreshold` |
| `PropFallLandBehavior` | `FallLandBehavior` |
| `PropFood` | `Food` |
| `PropGassiness` | `Gassiness` |
| `PropHandItem` | `HandItem` |
| `PropHandItemCrawler` | `HandItemCrawler` |
| `PropHasDeathAnim` | `HasDeathAnim` |
| `PropHasRagdoll` | `HasRagdoll` |
| `PropHeadExplosionDamageMultiplier` | `HeadExplosionDamageMultiplier` |
| `PropHideInSpawnMenu` | `HideInSpawnMenu` |
| `PropImmunity` | `Immunity` |
| `PropIsAnimalEntity` | `IsAnimalEntity` |
| `PropIsChunkObserver` | `IsChunkObserver` |
| `PropIsEnemyEntity` | `IsEnemyEntity` |
| `PropIsMale` | `IsMale` |
| `PropItemsOnEnterGame` | `ItemsOnEnterGame` |
| `PropJumpDelay` | `JumpDelay` |
| `PropJumpMaxDistance` | `JumpMaxDistance` |
| `PropKnockdownKneelDamageThreshold` | `KnockdownKneelDamageThreshold` |
| `PropKnockdownKneelRefillRate` | `KnockdownKneelRefillRate` |
| `PropKnockdownKneelStunDuration` | `KnockdownKneelStunDuration` |
| `PropKnockdownProneDamageThreshold` | `KnockdownProneDamageThreshold` |
| `PropKnockdownProneRefillRate` | `KnockdownProneRefillRate` |
| `PropKnockdownProneStunDuration` | `KnockdownProneStunDuration` |
| `PropLegCrawlerThreshold` | `LegCrawlerThreshold` |
| `PropLegCrippleScale` | `LegCrippleScale` |
| `PropLegsExplosionDamageMultiplier` | `LegsExplosionDamageMultiplier` |
| `PropLocalAvatarController` | `LocalAvatarController` |
| `PropLookAtAngle` | `LookAtAngle` |
| `PropLootDropEntityClass` | `LootDropEntityClass` |
| `PropLootDropProb` | `LootDropProb` |
| `PropLootList` | `LootList` |
| `PropMapIcon` | `MapIcon` |
| `PropMass` | `Mass` |
| `PropMatColor` | `MatColor` |
| `PropMaxHealth` | `MaxHealth` |
| `PropMaxStamina` | `MaxStamina` |
| `PropMaxTurnSpeed` | `MaxTurnSpeed` |
| `PropMaxViewAngle` | `MaxViewAngle` |
| `PropMesh` | `Mesh` |
| `PropMeshFP` | `MeshFP` |
| `PropModelTransformAdjust` | `ModelTransformAdjust` |
| `PropModelType` | `ModelType` |
| `PropMoveSpeed` | `MoveSpeed` |
| `PropMoveSpeedAggro` | `MoveSpeedAggro` |
| `PropMoveSpeedNight` | `MoveSpeedNight` |
| `PropMoveSpeedPanic` | `MoveSpeedPanic` |
| `PropMoveSpeedPattern` | `MoveSpeedPattern` |
| `PropMoveSpeedRand` | `MoveSpeedRand` |
| `PropNPCID` | `NPCID` |
| `PropNavObject` | `NavObject` |
| `PropNavObjectHeadOffset` | `NavObjectHeadOffset` |
| `PropOnActivateEvent` | `ActivateEvent` |
| `PropPainResistPerHit` | `PainResistPerHit` |
| `PropParent` | `Parent` |
| `PropParticleOnDeath` | `ParticleOnDeath` |
| `PropParticleOnDestroy` | `ParticleOnDestroy` |
| `PropParticleOnSpawn` | `ParticleOnSpawn` |
| `PropPhysicsBody` | `PhysicsBody` |
| `PropPickupItem` | `PickupItem` |
| `PropPickupStressBuff` | `PickupStressBuff` |
| `PropPickupStressCvar` | `PickupStressCVar` |
| `PropPrefab` | `Prefab` |
| `PropPrefabCombined` | `PrefabCombined` |
| `PropPreviousTierZombie` | `PreviousTier` |
| `PropPushFactor` | `PushFactor` |
| `PropRagdollOnDeathChance` | `RagdollOnDeathChance` |
| `PropRightHandJointName` | `RightHandJointName` |
| `PropRootMotion` | `RootMotion` |
| `PropRotateToGround` | `RotateToGround` |
| `PropSearchRadius` | `SearchRadius` |
| `PropSickness` | `Sickness` |
| `PropSightLightThreshold` | `SightLightThreshold` |
| `PropSightRange` | `SightRange` |
| `PropSizeScale` | `SizeScale` |
| `PropSkinTexture` | `SkinTexture` |
| `PropSleeperNoiseToSense` | `SleeperNoiseToSense` |
| `PropSleeperNoiseToSenseSoundChance` | `SleeperNoiseToSenseSoundChance` |
| `PropSleeperNoiseToWake` | `SleeperNoiseToWake` |
| `PropSleeperSightToSenseMax` | `SleeperSightToSenseMax` |
| `PropSleeperSightToSenseMin` | `SleeperSightToSenseMin` |
| `PropSleeperSightToWakeMax` | `SleeperSightToWakeMax` |
| `PropSleeperSightToWakeMin` | `SleeperSightToWakeMin` |
| `PropSoundAlert` | `SoundAlert` |
| `PropSoundAlertTime` | `SoundAlertTime` |
| `PropSoundAttack` | `SoundAttack` |
| `PropSoundDeath` | `SoundDeath` |
| `PropSoundDistressed` | `SoundDistressed` |
| `PropSoundDrownDeath` | `SoundDrownDeath` |
| `PropSoundDrownPain` | `SoundDrownPain` |
| `PropSoundExplodeWarn` | `SoundExplodeWarn` |
| `PropSoundGiveUp` | `SoundGiveUp` |
| `PropSoundHurt` | `SoundHurt` |
| `PropSoundHurtSmall` | `SoundHurtSmall` |
| `PropSoundJump` | `SoundJump` |
| `PropSoundLand` | `SoundLanding` |
| `PropSoundLiving` | `SoundLiving` |
| `PropSoundPlayerLandThump` | `SoundPlayerLandThump` |
| `PropSoundRandom` | `SoundRandom` |
| `PropSoundRandomTime` | `SoundRandomTime` |
| `PropSoundSense` | `SoundSense` |
| `PropSoundSleeperSense` | `SoundSleeperSense` |
| `PropSoundSleeperSnore` | `SoundSleeperBackToSleep` |
| `PropSoundSpawn` | `SoundSpawn` |
| `PropSoundStamina` | `SoundStamina` |
| `PropSoundStepType` | `SoundStepType` |
| `PropSoundTick` | `SoundTick` |
| `PropSoundWaterSurface` | `SoundWaterSurface` |
| `PropStealthSoundDecayRate` | `StealthSoundDecayRate` |
| `PropStompsSpikes` | `StompsSpikes` |
| `PropSwapMats` | `SwapMats` |
| `PropSwimOffset` | `SwimOffset` |
| `PropSwimSpeed` | `SwimSpeed` |
| `PropSwimStrokeRate` | `SwimStrokeRate` |
| `PropTags` | `Tags` |
| `PropTimeStayAfterDeath` | `TimeStayAfterDeath` |
| `PropTokenManager` | `TokenManager` |
| `PropTrackerIcon` | `TrackerIcon` |
| `PropUMAGeneratedModelName` | `UMAGeneratedModelName` |
| `PropUMARace` | `UMARace` |
| `PropUserSpawnType` | `UserSpawnType` |
| `PropWalkType` | `WalkType` |
| `PropWater` | `Water` |
| `PropWeight` | `Weight` |
| `PropWellness` | `Wellness` |
| `droneTag` | `drone` |
| `eliteTag` | `charged,infernal` |
| `fallingBlockClass` | `fallingBlock` |
| `fallingBlocksClass` | `fallingBlocks` |
| `fallingTreeClass` | `fallingTree` |
| `feralTag` | `feral,animalFeral` |
| `itemClass` | `item` |
| `jsonKeyCommandIndex` | `commandId` |
| `jsonKeyId` | `id` |
| `jsonKeyManualSpawnType` | `manualSpawnType` |
| `jsonKeyName` | `name` |
| `junkDroneClass` | `entityJunkDrone` |
| `playerFemaleClass` | `playerFemale` |
| `playerMaleClass` | `playerMale` |
| `playerNewMaleClass` | `playerNewMale` |
| `radiatedTag` | `radiated` |
| `specialTag` | `special` |
| `strongTag` | `strong` |
| `turretMeleeTag` | `turretMelee` |
| `turretRangedTag` | `turretRanged` |

| Other static | Value |
|---|---|
| class ids | `itemClass`, `fallingBlockClass`, `fallingBlocksClass`, `fallingTreeClass`, `playerMaleClass`, `playerFemaleClass`, `playerNewMaleClass`, `junkDroneClass` (Int32, assigned via `EntityClass.FromString`) |
| FastTags | `strongTag` `specialTag` `feralTag` `radiatedTag` `eliteTag` `droneTag` `turretRangedTag` `turretMeleeTag` |
| collections | `sColors`, `list` (DictionarySave), `commaSeparator` (Char[]), `jsonKeyName/Id/CommandIndex/ManualSpawnType` (Byte[]) |
