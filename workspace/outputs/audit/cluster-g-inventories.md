# Cluster G audit: inventory catalogs (docs/inventories/) vs Assembly-CSharp.dll V3.0.1

**Verdict:** 4 of 6 leaf-catalog counts are exactly correct with identical membership; sequence-requirements is wrong (43 claimed vs 38 actual, 5 leaves from an unrelated same-named base), console-command-list is off by one (186 vs 187, `exportprefab` missing), and frame-entries misses 2 nested MonoBehaviours. All spot-checked descriptions, IL sizes, permissions, and field lists match the DLL exactly; nothing fabricated.

Ground truth assembly: `/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` (stable dedicated V3.0.1).

Method: dumped every type + base via a Mono.Cecil script (`TypeBases.exe`, scratchpad), computed transitive closures of each claimed base (`closure.py`, generic-instantiation-aware where noted), and diffed against the doc tables. Command extraction for console commands read `ldstr` operands of each concrete subclass's `getCommands`/`getDescription` (`CmdStrings.exe`). Spot checks used the repo's `tools/bin/DumpMethod.exe` / `DumpType.exe`.

---

## Findings

### [F1] MAJOR: sequence-requirements.md count and membership wrong (43 vs 38; 5 leaves are from a different hierarchy)
- **Doc:** `docs/inventories/sequence-requirements.md`
- **Claim:** "Every `BaseRequirement` subclass (game-event gate ...) ... **43 leaves.**" Contract owner given as `game-events.md`.
- **Ground truth:** transitive closure of `GameEvent.SequenceRequirements.BaseRequirement` = **38** types (`python3 closure.py "GameEvent.SequenceRequirements.BaseRequirement" typebases.txt | wc -l` → 38). Diff against the doc's 43 rows shows exactly 5 doc-only rows: `RequirementBuff`, `RequirementGroup`, `RequirementHolding`, `RequirementLevel`, `RequirementWearing`. Those 5 exist only as `Quests.Requirements.*` deriving from `Quests.Requirements.BaseRequirement` (closure = exactly 5), a quest-offer-gate hierarchy that merely shares the short name `BaseRequirement`. Their listed key methods (`SetupRequirement,CheckRequirement,Clone`) are the quest API, not the sequence API (`OnInit/CanPerform/ParseProperties`) used by every genuine row, so the extractor keyed on simple name and merged two hierarchies.
- **Corroboration:** `grep -n "SequenceRequirements" docs/game-events.md` line 35 itself says the `GameEvent.SequenceRequirements` namespace has 39 types (= abstract base + 38 subclasses), contradicting the "43" its own line 452 cites. `docs/quests-challenges.md` lines 55/141 already document the 5 quest requirements separately, so they are double-counted across catalogs.
- **Fix:** drop the 5 `Quests.Requirements.*` rows, change count to **38**, and update `docs/game-events.md` line 452 ("all 43 requirement leaves" → 38). Optionally note the same-named quest hierarchy lives in quests-challenges.md.

### [F2] MAJOR: console-command-list.md missing `exportprefab` (186 vs 187 concrete commands)
- **Doc:** `docs/inventories/console-command-list.md` ("**186 commands.**", 186 table rows).
- **Ground truth:** transitive closure of `ConsoleCmdAbstract` = 189 types, of which 2 abstract (`ConsoleCmdTeleportsAbs`, `ConsoleCmdTestSystemAbs`) → **187 concrete commands**. Matching every class's `getCommands` `ldstr` strings against the doc rows leaves exactly one unmatched class: `ConsoleCmdExportPrefab`. Its `getCommands` returns a static field instead of a literal:
  - `mono tools/bin/DumpMethod.exe "$ASM" ConsoleCmdExportPrefab getCommands` → `ldsfld String ConsoleCmdExportPrefab::CommandName`
  - `mono tools/bin/DumpMethod.exe "$ASM" ConsoleCmdExportPrefab .cctor` → `ldstr exportprefab`
  So the ldstr-based extractor missed it. `grep -i exportprefab docs/` finds no mention anywhere.
- **Propagation:** `docs/console-commands.md` cites "186" at lines 4, 7, 120, 148.
- **Fix:** add a row for `exportprefab` (perm inherits default; description from its `getDescription`), bump count to **187**, update the four "186" citations, and make the extractor follow `ldsfld` → `.cctor` for command names.

### [F3] MAJOR (low impact): frame-entries.md misses 2 nested MonoBehaviour frame entries
- **Doc:** `docs/inventories/frame-entries.md` ("All MonoBehaviour-like Update/LateUpdate/FixedUpdate", 242 rows, no count claim).
- **Ground truth:** generic-aware transitive closure of `UnityEngine.MonoBehaviour` (419 types, including `SingletonMonoBehaviour\`1<T>` descendants) filtered to zero-arg `Update`/`LateUpdate`/`FixedUpdate` with bodies = **244** methods. Diff vs doc: missing `PerformanceProfiler/FrameTimeCapture::LateUpdate` and `XUiC_ItemActionEntry/TimedAction::Update` (both nested types with base `UnityEngine.MonoBehaviour`, per `grep "FrameTimeCapture\|TimedAction" typebases.txt`). The doc's extractor evidently skipped nested types. Everything else, including the tricky `SingletonMonoBehaviour\`1` descendants (`ConnectionManager`, `SdtdConsole`, `BackgroundMusicMono`, `MumblePositionalAudio`), is correctly present.
- **Fix:** add the 2 nested entries (or state "top-level types only" in the header).

### [F4] MINOR: blocks.md "138 `Block*` types" not reproducible
- **Doc:** `docs/blocks.md` line 16: "(138 `Block*` types, of which about 65 are concrete `Block` behavior subclasses)".
- **Ground truth:** the 65 is exact and correct (see C1). But no natural counting yields 138: top-level full-name prefix `Block*` = 131, simple-name `Block*` anywhere = 142, including nested = 180 (`awk` over typebases.txt). Likely a stale number from an earlier build.
- **Fix:** change to "131 top-level `Block*` types" (or whatever counting rule is intended, stated explicitly).

### [F5] MINOR (label): item-actions.md lists abstract `ItemActionAttack` as a "leaf"
- **Doc:** `docs/inventories/item-actions.md` row `ItemActionAttack`.
- **Ground truth:** `ItemActionAttack` is abstract (typebases.txt flag; only abstract type in any of the four verified closures). Its inclusion is consistent with the doc's own "Every `ItemAction` subclass" rule, so count/membership are fine; only the word "leaf" overreaches for this one row. Same nit applies to intermediate bases listed in other catalogs (e.g. `BaseOperationRequirement`), but those are concrete.
- **Fix:** footnote that the table is the full transitive closure including intermediate/abstract bases.

---

## Spot-verified CONFIRMED

| Doc | Claim | Recomputed | Command |
|---|---|---|---|
| block-behaviors.md | 65 `Block` leaves | **65**, membership identical (diff empty) | `closure.py Block typebases.txt`; `diff` vs doc rows |
| item-actions.md | 38 `ItemAction` leaves | **38**, membership identical | `closure.py ItemAction ...`; `diff` |
| minevent-actions.md | 71 `MinEventActionBase` leaves | **71**, membership identical | `closure.py MinEventActionBase ...`; `diff` |
| quest-objectives.md | 38 `BaseObjective` leaves | **38**, membership identical | `closure.py BaseObjective ...`; `diff` |
| netpackages.md | 194 types with `NetPackage` name prefix | **194** by simple-name prefix (193 global + `Audio.NetPackageAudio`); membership identical | `awk` simple-name prefix count over typebases.txt; `diff` |
| gmupdate-calls.md | 182 ordered calls in `GameManager::gmUpdate` | **182** call/callvirt instructions; all IL offsets identical; all call targets identical (only generic-notation formatting differs) | `mono tools/bin/DumpMethod.exe "$ASM" GameManager gmUpdate`; paste/diff |
| console-command-list.md descriptions | "function text is each command's own `getDescription`" | 8/8 sampled descriptions byte-identical to `getDescription` ldstr (`admin`, `AccDecay`, `kick`, `shutdown`, `spectator`, `teleportplayer`, `weather`, `webtokens`) | `CmdStrings.exe ... getDescription` |
| console-command-list.md permissions | `chunkcache`=1000, `debugweather`=1000, `admin`=blank (default) | matches: `ldc.i4 1000` overrides present; `ConsoleCmdAdmin` has no override | `DumpMethod.exe "$ASM" ConsoleCmdChunkCache get_DefaultPermissionLevel` (and peers) |
| manager-updates.md | per-method IL and MB flags | `AIScoutHordeSpawner::UpdateHorde` IL=229, `AstarManager::UpdateGraphs` IL=185 (MB=True: in MonoBehaviour closure), `AchievementManager`/`AntiCheatServer` MB=False: all match | `DumpMethod.exe`; closure membership check |
| deeper.md | EAI/entity IL sizes | `EAIApproachAndAttackTarget::Update` 846, `EntityAlive::OnUpdateLive` 363, `EAIDestroyArea::Continue` 317: all match | `DumpMethod.exe` |
| gaps.md | `GameTimer` fields (9) + `updateTimer` IL=74 | all 9 field names/types match; IL=74 | `DumpType.exe "$ASM" <dir> GameTimer`; `DumpMethod.exe` |
| loop-complete.md | Tick IL sizes | `AIDirectorBloodMoonComponent::Tick` 170, `AIHordeSpawner::Tick` 210: match | `DumpMethod.exe` |
| opt-scan.md | largest-method IL sizes | `DistantChunkMap::SetChunkTrigger` 4090, `Block::Init` 2136, `EntityVulture::updateTasks` 1344: match | `DumpMethod.exe` |
| Narrative cross-refs | blocks.md (65), items.md (38), minevents.md (71), quests-challenges.md (38) cite catalog counts | all match the verified catalogs | `grep` over docs |
| Labeling | non-console catalogs presented as code-derived, not game text | headers state "derived from class name/base/code signals; no bodies" / "auto dump notes (not primary narrative)"; accurate | doc inspection |

## Inline annotations

> "**43 leaves.**" (sequence-requirements.md)
**[F1] MAJOR:** Actual transitive subclass count of `GameEvent.SequenceRequirements.BaseRequirement` is 38. The extra 5 rows (`RequirementBuff/Group/Holding/Level/Wearing`) derive from `Quests.Requirements.BaseRequirement`, a different hierarchy.

> "**186 commands.**" (console-command-list.md)
**[F2] MAJOR:** 187 concrete `ConsoleCmdAbstract` subclasses exist. `ConsoleCmdExportPrefab` (`exportprefab`, command name stored in a static field, not an inline `ldstr`) is absent from the table.

> "# All MonoBehaviour-like Update/LateUpdate/FixedUpdate (V3.0.1)" (frame-entries.md)
**[F3] MAJOR (low impact):** Not "all": nested `PerformanceProfiler/FrameTimeCapture::LateUpdate` and `XUiC_ItemActionEntry/TimedAction::Update` are missing (242 listed vs 244 actual).

> "(138 `Block*` types, of which about 65 are concrete `Block` behavior subclasses" (blocks.md)
**[F4] MINOR:** 65 is exact; 138 matches no counting rule tried (131 top-level / 142 simple-name / 180 incl. nested).

> "| `ItemActionAttack` | Attack | ItemAction | ..." (item-actions.md)
**[F5] MINOR:** Abstract type presented as a "leaf"; inclusion is correct under the doc's "every subclass" rule, wording is not.

## Sources
- Assembly: `/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll`
- Scratch scripts/artifacts: `/tmp/claude-1000/-home-maci-Desktop-7dtd-7dtd-research/0b44a842-ae93-414f-9c41-1f1f1f54c21b/scratchpad/` (`TypeBases.cs/.exe`, `closure.py`, `CmdStrings.cs/.exe`, `FrameEntries.cs/.exe`, `typebases.txt`, diff lists)
- Repo tools: `tools/bin/DumpMethod.exe`, `tools/bin/DumpType.exe`
