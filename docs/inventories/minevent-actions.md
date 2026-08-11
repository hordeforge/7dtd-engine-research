# MinEvent action catalog (V3.1.0)

**Kind:** per-leaf behavioral catalog (name -> function, derived from class name/base/code signals; no bodies).  
**Framework:** [`../minevents.md`](../minevents.md) owns the contract; this describes each `MinEventActionBase` leaf.  
**Regenerate:** hint extractor over transitive subclasses.
**Hub:** [`INDEX.md`](../INDEX.md).  

Every `MinEventActionBase` subclass (triggered effect: add buff, modify stat/cvar, spawn, sound, ...). Dispatch: [minevents.md](../minevents.md).

**71 leaves.**

| Leaf | Function | base | key methods |
|---|---|---|---|
| `MinEventActionAddBuff` | Add Buff | MinEventActionBuffModifierBase | Execute,ParseXmlAttribute |
| `MinEventActionAddChatMessage` | Add Chat Message | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionAddHealth` | Add Health | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionAddOrRemoveBuff` | Add Or Remove Buff | MinEventActionAddBuff | CanExecute,Execute |
| `MinEventActionAddPart` | Add Part | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionAddPartFPV` | Add Part FPV | MinEventActionAddPart | CanExecute |
| `MinEventActionAddPartTPV` | Add Part TPV | MinEventActionAddPart | CanExecute |
| `MinEventActionAddProgressionLevel` | Add Progression Level | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionAltSounds` | Alt Sounds | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionAnimatorFireTrigger` | Animator Fire Trigger | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionAnimatorResetTrigger` | Animator Reset Trigger | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionAnimatorSetBool` | Animator Set Bool | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionAnimatorSetFloat` | Animator Set Float | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionAnimatorSetInt` | Animator Set Int | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionAnimatorSetWalkType` | Animator Set Walk Type | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionAttachParticleEffectToEntity` | Attach Particle Effect To Entity | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionAttachPrefabToEntity` | Attach Prefab To Entity | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionAttachPrefabToHeldItem` | Attach Prefab To Held Item | MinEventActionBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionAwardChallenge` | Award Challenge | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionAwardQuestStat` | Award Quest Stat | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionBuffModifierBase` | Buff Modifier Base (Warning: Invalid "Buffs.xml" configuration. User has specified weights outside of range 0-1 and fireOneBuff="false" or missing. When fireOneBuff="false", the weights represent probabilities between 0-1 for the buffs to be added.) | MinEventActionTargetedBase | ParseXmlAttribute,ParseXMLPostProcess,Remove |
| `MinEventActionCVarLogValue` | CVar Log Value | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionCallGameEvent` | Call Game Event | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionExplode` | Explode | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionFadeOutSound` | Fade Out Sound | MinEventActionSoundBase | Execute |
| `MinEventActionGetBuffDuration` | Get Buff Duration | MinEventActionTargetedBase | CanExecute,Execute,ParseXmlAttribute |
| `MinEventActionGiveExp` | Give Exp | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionGiveSkillExp` | Give Skill Exp | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionLogItemData` | Log Item Data | MinEventActionBase | Execute |
| `MinEventActionLogMessage` | Log Message | MinEventActionBase | Execute,ParseXmlAttribute |
| `MinEventActionModifyCVar` | Modify CVar | MinEventActionTargetedBase | Execute,ParseXmlAttribute,CanExecute,GetValueForDisplay |
| `MinEventActionModifyScreenEffect` | Modify Screen Effect | MinEventActionBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionModifyStat` | Modify Stat | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionModifyStats` | Modify Stats | MinEventActionTargetedBase | Execute,executeDelayed,execute,ParseXmlAttribute |
| `MinEventActionPinToolbeltMessage` | Pin Toolbelt Message | MinEventActionBase | Execute,ParseXmlAttribute |
| `MinEventActionPlaySound` | Play Sound | MinEventActionSoundBase | Execute |
| `MinEventActionRagdoll` | Ragdoll | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionRage` | Rage | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionRefreshPerks` | Refresh Perks | MinEventActionBase | Execute,ParseXmlAttribute |
| `MinEventActionRemoveAllNegativeBuffs` | Remove All Negative Buffs | MinEventActionTargetedBase | Execute |
| `MinEventActionRemoveBuff` | Remove Buff | MinEventActionBuffModifierBase | Execute |
| `MinEventActionRemoveCVar` | Remove CVar | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionRemovePart` | Remove Part | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionRemoveParticleEffectFromEntity` | Remove Particle Effect From Entity | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionRemovePrefabFromEntity` | Remove Prefab From Entity | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionRemoveToolbeltMessage` | Remove Toolbelt Message | MinEventActionBase | Execute,ParseXmlAttribute |
| `MinEventActionResetHeldItem` | Reset Held Item | MinEventActionTargetedBase | Execute |
| `MinEventActionResetProgression` | Reset Progression | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetAudioMixerState` | Set Audio Mixer State | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetBigHead` | Set Big Head | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetDancing` | Set Dancing | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetHeadSize` | Set Head Size | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetHeldItemJammed` | Set Held Item Jammed | MinEventActionBase | Execute |
| `MinEventActionSetItemInSlot` | Set Item In Slot | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetItemMetaFloat` | Set Item Meta Float | MinEventActionBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionSetNavObject` | Set Nav Object | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetOverrideLoot` | Set Override Loot | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetPartActive` | Set Part Active | MinEventActionBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionSetPitch` | Set Pitch | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetProgressionLevel` | Set Progression Level | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionSetScale` | Set Scale | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetTransformActive` | Set Transform Active | MinEventActionBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionSetTransformChildrenActive` | Set Transform Children Active | MinEventActionBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionSetTwitchCooldown` | Set Twitch Cooldown | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionSetTwitchProgressionDisabled` | Set Twitch Progression Disabled | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
| `MinEventActionShakeCamera` | Shake Camera | MinEventActionTargetedBase | Execute,stopShaking,CanExecute,ParseXmlAttribute |
| `MinEventActionShowToolbeltMessage` | Show Toolbelt Message | MinEventActionTargetedBase | Execute,CanExecute,ParseXmlAttribute |
| `MinEventActionSoundBase` | Sound Base | MinEventActionTargetedBase | ParseXmlAttribute,GetSoundGroupForTarget |
| `MinEventActionStopSound` | Stop Sound | MinEventActionSoundBase | Execute |
| `MinEventActionTargetedBase` | Targeted Base | MinEventActionBase | CanExecute,ParseXmlAttribute,singleTargetCheck,isValidTarget |
| `MinEventActionUnregisterSequenceLink` | Unregister Sequence Link | MinEventActionTargetedBase | Execute,ParseXmlAttribute |
