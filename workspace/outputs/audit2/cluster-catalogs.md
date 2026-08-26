# Audit: leaf-catalog docs vs stable V3.0.1 server DLL

**Verdict:** 3 of 4 catalogs are exactly correct in count and membership; sequence-actions.md's "132 types transitively" / "every concrete BaseAction subclass" claim is wrong (true transitive closure is 137 types; 5 SequenceDecisions/SequenceLoops types missing), everything else audited is confirmed, with three minor label nits.

Ground-truth basis: a Cecil dumper (`scratchpad/TypeBases.cs`) emitted every type + base
(`typebases.tsv`, 7413 rows incl. nested) from
`"/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"`,
and `scratchpad/closure.py typebases.tsv <RootFullName>` computed each family's transitive closure.
Scratchpad: the uncommitted session scratch dir.

## Findings

### [F1] MAJOR: sequence-actions.md: transitive count and "every concrete subclass" claim are both wrong

- **Doc claim** (line 10): "**123 actions** (132 types transitively: the root `BaseAction`, 8 shared intermediate bases, and 123 concrete leaves)"; (line 8) "Every concrete `GameEvent.SequenceActions.BaseAction` subclass".
- **Ground truth:** `python3 closure.py typebases.tsv GameEvent.SequenceActions.BaseAction` -> **136 subtypes + root = 137 types transitively**, not 132. The 5 extra types are outside the `SequenceActions` namespace but derive from `BaseAction`:
  `GameEvent.SequenceDecisions.BaseDecision` (base = `GameEvent.SequenceActions.BaseAction`), `GameEvent.SequenceDecisions.DecisionIf`, `GameEvent.SequenceLoops.BaseLoop` (base = `BaseAction`), `GameEvent.SequenceLoops.LoopFor`, `GameEvent.SequenceLoops.LoopWhile` (all flagged concrete in IL).
- These are not dead code: `MethodList` output shows `GameEventsFromXml::ParseGameEventSequenceDecision(XElement,GameEventActionSequence,Boolean)` and `GameEventsFromXml::ParseGameEventSequenceLoop(...)`, i.e. `DecisionIf`/`LoopFor`/`LoopWhile` are XML-parseable sequence elements executed through the same `OnPerformAction` contract (`FindCallers` shows `DecisionIf::OnPerformAction -> BaseDecision::HandleActions`).
- The in-namespace numbers ARE right: 131 `GameEvent.SequenceActions.*` subtypes + root = 132; 8 intermediate bases + 123 concrete actions (verified below). So the doc's arithmetic holds only under an unstated "same namespace" filter.
- **Worst count drift in this audit: claimed 132 transitive types, actual 137 (5 types / 3 concrete XML-wired verbs missing).**
- **Fix:** rescope line 10 to "132 types in the `GameEvent.SequenceActions` namespace" and line 8 to "every concrete subclass in the namespace", and either add a Decisions/Loops section (3 concrete verbs + 2 bases) or an explicit pointer that `SequenceDecisions`/`SequenceLoops` also derive from `BaseAction` and are parsed by `ParseGameEventSequenceDecision`/`ParseGameEventSequenceLoop`.

### [F2] MINOR: challenge-objectives.md: `ChallengeBaseTrackedItemObjective` is not IL-abstract

- **Doc claim** (lines 55, 71): "**`ChallengeBaseTrackedItemObjective`** (abstract, 5 subclasses)" / "the abstract intermediate".
- **Ground truth:** `typebases.tsv` row: `Challenges.ChallengeBaseTrackedItemObjective  Challenges.BaseChallengeObjective  concrete  class` (the dumper prints `TypeDefinition.IsAbstract`, and it correctly flags e.g. `TEFeatureAbs` as abstract). It is de-facto abstract (its only `.ctor` callers are the 5 subclass ctors, `FindCallers ... ChallengeBaseTrackedItemObjective .ctor`), but the IL abstract flag is absent.
- **Fix:** say "never instantiated directly (not IL-abstract)".

### [F3] MINOR: cross-consistency: quests-challenges.md says "29 `ChallengeObjective*`", actual prefix count is 28

- **Doc claim** (docs/quests-challenges.md lines 52, 315): "+ 29 `ChallengeObjective*`" / "The 29 `ChallengeObjective*` verbs".
- **Ground truth:** `closure.py typebases.tsv Challenges.BaseChallengeObjective` -> 29 subtypes, of which **28** are named `ChallengeObjective*`; the 29th is `ChallengeBaseTrackedItemObjective` (does not match the glob). The catalog and INDEX.md line 266 both correctly say 28 leaves.
- **Fix:** in quests-challenges.md, change to "28 `ChallengeObjective*` leaves + `ChallengeBaseTrackedItemObjective`".

### [F4] MINOR: dedicated-leaves.md: two distinct `PrefabGameObject` types exist; row is ambiguous

- **Doc row** (line 199): `PrefabGameObject` | POI imposter mesh holder (LOD) | `Object` | (fields only).
- **Ground truth:** `grep PrefabGameObject typebases.tsv` -> `PrefabLODManager/PrefabGameObject` AND `PrefabPreviewManager/PrefabGameObject`. `LeafInfo` is simple-name keyed ("first wins"), so the fingerprint verified only one of them; the stated role matches the LOD one (`FindCallers` shows `PrefabLODManager::GetInstance`/`UpdatePrefabsAround` and `ChunkPreviewManager::SetPrefab` as users). Client-only marking still holds for both.
- **Fix:** qualify the row as `PrefabLODManager/PrefabGameObject`. (Same nesting nit applies to `BodyParts` = `BodyAnimator/BodyParts`, but that name is unique.)

Also noted, not graded: docs/game-events.md line 305 "nine abstract bases", none of the 9 (`BaseAction` + 8) carries the IL abstract flag (`closure.py` reports 0 abstract in the family); they are bases by position only.

## Spot-verified CONFIRMED

- **te-features.md, 11 leaves, flat:** `python3 closure.py typebases.tsv TEFeatureAbs` -> 11 subtypes, 11 concrete, 0 abstract, every base is `TEFeatureAbs` directly (no grandchildren); names match the doc's 11 rows exactly. `grep TEFeature typebases.tsv` -> no `TEFeaturePowered`, no `TEFeatureLootable`. Base `Read` debug-shim IL quote matches (`DumpMethod ... TEFeatureAbs Read` pattern seen via `TEFeatureDoor.Read` check); `TEFeatureDoor::Read` does read/write `isOpen` (`DumpMethod "$ASM" TEFeatureDoor Read`).
- **challenge-objectives.md, 28 leaves + 1 intermediate:** `closure.py ... Challenges.BaseChallengeObjective` -> 29 subtypes; the 28 leaf names match the doc table exactly; the tracked-item family is exactly {Gather, GatherByTag, GatherIngredient, Harvest, HarvestByTag} (bases checked in `typebases.tsv`).
- **Enum claim:** `EnumVals.exe "$ASM" Challenges.ChallengeObjectiveType` -> `Invalid=0` + 27 concrete verbs (1..27), no `HarvestByTag` member; `DumpMethod "$ASM" ChallengeObjectiveHarvestByTag get_ObjectiveType` -> `ldc.i4.s 9; ret` = `Harvest`. Claim "27 concrete verbs, HarvestByTag reuses the Harvest id" confirmed.
- **Client-tracked claim:** `FindCallers "$ASM" ChallengeJournal .ctor` -> `EntityPlayerLocal::Awake -> ChallengeJournal::.ctor`, `EntityPlayerLocal::OnUpdateLive -> ChallengeJournal::Update`, and `PlayerDataFile::Read/Write -> ChallengeJournal::Read/Write`. `DumpMethod "$ASM" BaseChallengeObjective get_Player` IL matches the doc's quoted 3 ldflds ending in `ChallengeJournal::Player : EntityPlayerLocal`. Confirmed.
- **Requirement groups:** `closure.py ... Challenges.BaseRequirementObjectiveGroup` -> exactly the 6 concrete `RequirementObjectiveGroup{BlockUpgrade,Craft,GatherIngredients,Hold,Place,WindowOpen}`.
- **sequence-actions.md in-namespace structure:** doc's action names (extracted from the tables) vs IL leaf set: **123 = 123, zero diff both directions** (`doc-only` after removing the 7 base-table rows: empty; `il-only`: empty). Parent/child map confirms exactly 8 intermediate bases with the stated child counts, and `ActionBlockReplace -> ActionBlockReplaceAttack`, `ActionRemoveEntities -> ActionRemoveVehicles`, `ActionSpawnEntity -> ActionSpawnEntitySpawner` each parenting exactly one subclass.
- **dedicated-leaves.md, 88 rows:** `LeafInfo.exe "$ASM" dl_names.txt dl_leafinfo.tsv` -> 0 "(not found)"; scripted diff: **88/88 base columns match**, and **every "key methods" list is a subset of the IL fingerprint** (LeafInfo = top-4 methods by `Body.Instructions.Count`, per `tools/src/LeafInfo.cs`), including all "(fields only)" rows (empty fingerprints).
- **Client-only markings (all 6):** `FindCallers` shows `ApplyExplosionForce::Explode` called only from `GameManager::ExplosionClient`; `GorePrefab` only from `Avatar{Animal,Bandit,Zombie}Controller::SpawnLimbGore`; `BodyParts` only from Avatar*/BodyAnimator render controllers; `PrefabGroupEntry` only from `XUiC_PrefabGroupList`; `PrefabGameObject` from `PrefabLODManager`/`ChunkPreviewManager`; `EventPrefabsClient::TryAdd/Remove` from `NetPackageEventPrefab::ProcessPackage` (whose IL opens with `ConnectionManager::get_IsClient(); brfalse` -> client-guarded, `DumpMethod`) and `NetPackageWorldInitInfo::ProcessPackage`.
- **Behavioral roles:** `DumpMethod "$ASM" QuestCriteriaPOIWithinDistance CheckForQuestGiver` -> IL=9, `Int32.TryParse` result popped, unconditional `ldc.i4.0; ret` = hardcoded false/dead, confirmed. `FindCallers "$ASM" TraderStageTemplate IsWithin` -> only `XUiC_CategoryList::SetupCategoriesBasedOnItems` and `XUiC_TraderWindow::FilterByName` = client-UI-only evaluation, confirmed. `DumpMethod "$ASM" StunBeamWeapon Fire` references `_droneStunDamage` and `buffShocked`, confirmed.
- **UAIConsideration\* "dormant in stock":** stock `Data/Config/utilityai.xml` does use `SelfHealth`/`TargetDistance`/`TargetType`/`TargetVisible` consideration classes, but the only entity classes wiring `AIPackages` are `npcSurvivorTemplate`/`npcSurvivorRanged` (`grep AIPackages entityclasses.xml`), and `grep -c npcSurvivor` in `entitygroups.xml`, `spawning.xml`, `gameevents.xml` = 0 (only other hit: Localization.csv), so no stock spawn path reaches the UAI scorers. Dormant claim confirmed at the config level; `SelfVisible`/`TargetHealth` are additionally unreferenced by any `consideration class=` in the XML.
- **Cross-consistency:** INDEX.md 265-268 (11 / 28 / 123 / 88) all match the recomputed counts; game-events.md line 34 "SequenceActions | 132" is correct under the namespace reading (131 + root).
