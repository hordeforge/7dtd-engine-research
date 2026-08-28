# Block behavior catalog (V3.2.0)

**Kind:** per-leaf behavioral catalog (name -> function, derived from class name/base/code signals; no bodies).  
**Framework:** [`../blocks.md`](../blocks.md) owns the contract; this describes each `Block` leaf.  
**Regenerate:** hint extractor over transitive subclasses.
**Hub:** [`INDEX.md`](../INDEX.md).  

Every transitive `Block` subclass (block behavior leaf: doors, plants, powered, traps, loot, hazards, ...). Contract: [blocks.md](../blocks.md).

**65 leaves.**

| Leaf | Function | base | key methods |
|---|---|---|---|
| `BlockActivate` | Activate | Block | Init,LateInit,OnBlockValueChanged,GetActivationText |
| `BlockActivateSingle` | Activate Single | Block | Init,LateInit,OnBlockValueChanged,OnBlockEntityTransformAfterActivated |
| `BlockActivateSwitch` | Activate Switch | Block | Init,LateInit,OnBlockValueChanged,OnBlockEntityTransformAfterActivated |
| `BlockBarbed` | Barbed | BlockDamage | OnEntityCollidedWithBlock |
| `BlockBatteryBank` | Battery Bank | BlockPowerSource | CreateTileEntity,GetPowerSourceIcon |
| `BlockBladeTrap` | Blade Trap | BlockPoweredTrap | Init,ActivateTrap,OnBlockDamaged,OnBlockRemoved |
| `BlockCactus` | Cactus | BlockDamage | Init,GetCollisionAABB |
| `BlockCampfire` | Campfire | BlockWorkstation |  |
| `BlockCollector` | Collector | Block | GetFuelType,GetOutputType,Init,OnBlockAdded |
| `BlockCompositeTileEntity` | Composite Tile Entity | Block | Init,OnBlockAdded,OnBlockRemoved,OnBlockLoaded |
| `BlockDamage` | Damage | Block | Init,GetCollisionAABB,GetClipBoundsList,OnEntityCollidedWithBlock |
| `BlockDeadgrass` | Deadgrass | Block | Init,OnNeighborBlockChange,OnBlockPlaced,OnBlockPlaceBefore |
| `BlockElectricWire` | Electric Wire | BlockPowered | Init,CreateTileEntity,OnBlockAdded,OnBlockDamaged |
| `BlockForge` | Forge | BlockWorkstation | OnBlockEntityTransformAfterActivated,checkParticles,GetActivationText,MaterialUpdate |
| `BlockGameEvent` | Game Event | Block | Init,GetActivationText,OnBlockAdded,OnBlockActivated |
| `BlockGenerator` | Generator | BlockPowerSource | CreateTileEntity,GetPowerSourceIcon |
| `BlockHay` | Hay | Block | GetCollisionAABB,GetClipBoundsList,OnEntityCollidedWithBlock |
| `BlockHazard` | Hazard | BlockParticle | Init,GetLightValue,GetActivationText,OnBlockActivated |
| `BlockInfo` | Info | Block | Init,HasBlockActivationCommands,GetBlockActivationCommands,GetActivationText |
| `BlockJumpPad` | Jump Pad | Block | OnEntityWalking,getInventoryFace |
| `BlockLadder` | Ladder | Block | IsElevator |
| `BlockLauncher` | Launcher | BlockPowered | Init,HasBlockActivationCommands,GetBlockActivationCommands,GetActivationText |
| `BlockLight` | Light | Block | Init,GetLightValue,GetActivationText,OnBlockActivated |
| `BlockLiquidSource` | Liquid Source | Block | LateInit,OnNeighborBlockChange,IsMovementBlocked,GetTickRate |
| `BlockLiquidv2` | Liquidv 2 | Block | LateInit,OnBlockDamaged,IsHealthShownInUI,OnNeighborBlockChange |
| `BlockMine` | Mine | Block | Init,OnEntityWalking,OnBlockDamaged,OnBlockDestroyedByExplosion |
| `BlockModelTree` | Model Tree | BlockPlantGrowing | Init,UpdateTick,OnNeighborBlockChange,OnBlockValueChanged |
| `BlockMotionSensor` | Motion Sensor | BlockPowered | Init,OnBlockEntityTransformAfterActivated,updateState,IsMovementBlocked |
| `BlockMusic` | Music | Block | OnBlockAdded,OnBlockRemoved |
| `BlockParticle` | Particle | Block | Init,OnBlockRemoved,OnBlockAdded,OnNeighborBlockChange |
| `BlockPlant` | Plant | Block | CanPlaceBlockAt,CanGrowOn,OnNeighborBlockChange,UpdateTick |
| `BlockPlantGrowing` | Plant Growing | BlockPlant | LateInit,CanPlaceBlockAt,CanGrowOn,PlaceBlock |
| `BlockPowerSource` | Power Source | Block | Init,GetActivationText,HasBlockActivationCommands,GetBlockActivationCommands |
| `BlockPowered` | Powered | Block | Init,OnBlockLoaded,OnBlockEntityTransformAfterActivated,drawWiresLater |
| `BlockPoweredDoor` | Powered Door | BlockPowered | Init,IsDoorOpen,IsMovementBlocked,IsSeeThrough |
| `BlockPoweredLight` | Powered Light | BlockPowered | Init,GetLightValue,GetActivationText,OnBlockActivated |
| `BlockPoweredTrap` | Powered Trap | BlockPowered | Init,GetCollisionAABB,GetClipBoundsList,updateTrapState |
| `BlockPressurePlate` | Pressure Plate | BlockPowered | Init,updateState,OnEntityCollidedWithBlock,IsMovementBlocked |
| `BlockQuestActivate` | Quest Activate | Block | GetActivationText,OnBlockActivated,EventData_AlternateEvent,EventData_CloseEvent |
| `BlockRallyMarker` | Rally Marker | Block | GetActivationText,OnBlockActivated,HasBlockActivationCommands,GetBlockActivationCommands |
| `BlockRanged` | Ranged | BlockPowered | Init,HasBlockActivationCommands,GetBlockActivationCommands,GetActivationText |
| `BlockSiblingRemove` | Sibling Remove | Block | Init,OnBlockRemoved |
| `BlockSign` | Sign | Block | Init,OnBlockAdded,OnBlockRemoved,RenderDecorations |
| `BlockSleeper` | Sleeper | Block | Init,CanPlaceBlockAt,GetSleeperRotation,ExcludesWalkType |
| `BlockSleepingBag` | Sleeping Bag | BlockSiblingRemove | rotationToAddVector,CanPlaceBlockAt,PlaceBlock,GetOwningPlayer |
| `BlockSolarPanel` | Solar Panel | BlockPowerSource | CreateTileEntity,CanPlaceBlockAt,GetPowerSourceIcon,OnBlockRemoved |
| `BlockSpawnEntity` | Spawn Entity | Block | Init,OnBlockAdded,OnBlockLoaded,OnBlockEntityTransformAfterActivated |
| `BlockSpeaker` | Speaker | BlockPowered | Init,ActivateBlock,OnBlockUnloaded,OnBlockRemoved |
| `BlockSpeakerTrader` | Speaker Trader | Block | Init,PlayOpen,PlayClose,PlayWarning |
| `BlockSpikes` | Spikes | BlockDamage | Init,GetCollisionAABB,IsMovementBlocked,GetStepHeight |
| `BlockSpotlight` | Spotlight | BlockPowered | Init,OnBlockEntityTransformAfterActivated,updateState,IsMovementBlocked |
| `BlockStairs` | Stairs | Block | IsMovementBlocked |
| `BlockSwitch` | Switch | BlockPowered | GetActivationText,OnBlockActivated,updateState,OnBlockEntityTransformAfterActivated |
| `BlockTNT` | TNT | Block | Init,OnBlockDamaged,OnBlockDestroyedByExplosion,explode |
| `BlockTallgrass` | Tallgrass | BlockPlant | CheckPlantAlive,OnBlockPlaceBefore,OnBlockPlaced,CalcMeta |
| `BlockTimerRelay` | Timer Relay | BlockPowered | OnBlockAdded,GetActivationText,OnBlockActivated,HasBlockActivationCommands |
| `BlockTorch` | Torch | BlockParticle | getParticleOffset,OnBlockPickedUp |
| `BlockTorchHeatMap` | Torch Heat Map | BlockTorch | UpdateTick,OnBlockEntityTransformAfterActivated |
| `BlockTrapDoor` | Trap Door | Block | Init,HasBlockActivationCommands,GetBlockActivationCommands,OnBlockActivated |
| `BlockTriggerDowngrade` | Trigger Downgrade | Block | LateInit,OnBlockValueChanged,GetActivationText,OnBlockActivated |
| `BlockTripWire` | Trip Wire | BlockPowered | Init,CreateTileEntity,OnBlockAdded,GetActivationText |
| `BlockTrunk` | Trunk | Block |  |
| `BlockTrunkTip` | Trunk Tip | BlockDamage | RotateVerticesOnCollisionCheck |
| `BlockVendingMachine` | Vending Machine | Block | Init,PlaceBlock,GetActivationText,HasBlockActivationCommands |
| `BlockWorkstation` | Workstation | BlockParticle | Init,OnBlockAdded,OnBlockRemoved,PlaceBlock |
