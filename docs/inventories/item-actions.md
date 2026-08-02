# Item action catalog (V3.1.0)

**Kind:** per-leaf behavioral catalog (name -> function, derived from class name, base, and code signals; no bodies).  
**Framework:** [`../items.md`](../items.md) owns the contract; this describes each `ItemAction` leaf.  
**Regenerate:** `tools` hint extractor over transitive subclasses.

Every `ItemAction` subclass: the use behavior bound to an item's primary/secondary action (attack, ranged, eat, place, tool, power-wire, ...). Function is derived from the class name and its overridden verb methods.

**38 leaves.**

| Leaf | Function | base | key methods |
|---|---|---|---|
| `ItemActionActivate` | Activate | ItemAction | ExecuteAction,AllowConcurrentActions,IsActionRunning,CancelAction |
| `ItemActionAttachment` | Attachment | ItemAction | ExecuteAction |
| `ItemActionAttack` | Attack | ItemAction | GetDamageEntity,GetDamageBlock,GetDamageMultiplier,GetKickbackForce |
| `ItemActionBailLiquid` | Bail Liquid | ItemAction | CreateModifierData,ExecuteAction,IsActionRunning,OnHoldingUpdate |
| `ItemActionCancel` | Cancel | ItemAction | ExecuteAction |
| `ItemActionCatapult` | Catapult | ItemActionLauncher | ReadFrom,OnModificationsChanged,CreateModifierData,OnScreenOverlay |
| `ItemActionCollectWater` | Collect Water | ItemAction | ReadFrom,CreateModifierData,ExecuteAction,IsActionRunning |
| `ItemActionConnectPower` | Connect Power | ItemAction | CreateModifierData,ReadFrom,StopHolding,StartHolding |
| `ItemActionDisconnectPower` | Disconnect Power | ItemAction | CreateModifierData,ReadFrom,StopHolding,ExecuteAction |
| `ItemActionDumpWater` | Dump Water (Cannot dump water as item is not a WaterContainer) | ItemAction | ReadFrom,CreateModifierData,ExecuteAction,TryFindDumpPosition |
| `ItemActionDynamic` | Dynamic | ItemAction | ReadFrom,ExecuteAction,harvestOnCompletion,OnHoldingUpdate |
| `ItemActionDynamicMelee` | Dynamic Melee | ItemActionDynamic | ExecuteAction,IsActionRunning,OnHoldingUpdate,SetAttackFinished |
| `ItemActionEat` | Eat | ItemAction | CreateModifierData,ReadFrom,CanInteract,NeedPrompt |
| `ItemActionExchangeBlock` | Exchange Block | ItemAction | ReadFrom,ExecuteAction |
| `ItemActionExchangeItem` | Exchange Item | ItemAction | ReadFrom,isFocusingBlock,ExecuteAction,IsActionRunning |
| `ItemActionGainSkill` | Gain Skill | ItemAction | CreateModifierData,ReadFrom,StopHolding,ExecuteAction |
| `ItemActionLauncher` | Launcher | ItemActionRanged | CreateModifierData,ReadFrom,StartHolding,StopHolding |
| `ItemActionLearnRecipe` | Learn Recipe | ItemAction | CreateModifierData,ReadFrom,StopHolding,ExecuteAction |
| `ItemActionMakeFertile` | Make Fertile | ItemActionMelee | ReadFrom,hitTheTarget,GetFocusType |
| `ItemActionMelee` | Melee | ItemActionAttack | CreateModifierData,GetCrosshairType,GetExecuteActionTarget,ExecuteAction |
| `ItemActionOpenBundle` | Open Bundle | ItemAction | CreateModifierData,ReadFrom,StopHolding,ExecuteAction |
| `ItemActionOpenLootBundle` | Open Loot Bundle | ItemAction | CreateModifierData,ReadFrom,StopHolding,ExecuteAction |
| `ItemActionPlaceAsBlock` | Place As Block | ItemAction | ReadFrom,ExecuteAction,decInventoryLater,GetFocusType |
| `ItemActionProjectile` | Projectile | ItemActionAttack | ReadFrom,ExecuteAction |
| `ItemActionQuest` | Quest | ItemAction | CreateModifierData,ReadFrom,StopHolding,ExecuteAction |
| `ItemActionRanged` | Ranged | ItemActionAttack | CreateModifierData,ReadFrom,canShowOverlay,IsSingleMagazineUsage |
| `ItemActionRepair` | Repair | ItemActionAttack | CreateModifierData,ReadFrom,StopHolding,StartHolding |
| `ItemActionReplaceBlock` | Replace Block | ItemActionRanged | CreateModifierData,ReadFrom,ConsumeScrollWheel,checkAmmo |
| `ItemActionSpawnEntity` | Spawn Entity | ItemAction | CreateModifierData,ReadFrom,StartHolding,StopHolding |
| `ItemActionSpawnTurret` | Spawn Turret | ItemAction | CreateModifierData,ReadFrom,StartHolding,setupPreview |
| `ItemActionSpawnVehicle` | Spawn Vehicle | ItemAction | CreateModifierData,ReadFrom,StartHolding,SetupPreview |
| `ItemActionTerrainTool` | Terrain Tool | ItemActionRanged | CreateModel,ReadFrom,CreateModifierData,GetInitialMeta |
| `ItemActionTextureBlock` | Texture Block | ItemActionRanged | CreateModifierData,ReadFrom,getUserData,ItemActionEffects |
| `ItemActionThrowAway` | Throw Away | ItemAction | ReadFrom,CreateModifierData,OnScreenOverlay,StartHolding |
| `ItemActionThrownWeapon` | Thrown Weapon | ItemActionThrowAway | ReadFrom,IsActionRunning,StartHolding,OnHoldingUpdate |
| `ItemActionUseOther` | Use Other | ItemAction | CreateModifierData,ReadFrom,StopHolding,CanExecute |
| `ItemActionVomit` | Vomit | ItemActionLauncher | CreateModifierData,ReadFrom,resetAttack,GetActionEffectsValues |
| `ItemActionZoom` | Zoom | ItemAction | ReadFrom,CreateModifierData,OnModificationsChanged,StartHolding |
