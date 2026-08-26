# Adversarial accuracy review: session-written subsystem docs (V3.0.1 corpus)

> **ARCHIVED (2026-08-11):** pre-V3.1.0-retarget research artifact; superseded by the current corpus. Historical record only.

**Reviewer pass:** evidence audit against the shipped DLLs, not a style review.
**Method:** for each of the 28 in-scope docs, the highest-risk verifiable claims
(wire byte layouts, named methods/enums/constants, IL sizes, counts, state-machine
gates) were checked against
`~/.local/share/Steam/.../7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` (stable
V3.0.1) and `~/.cache/zdtd-scratch/exp-Assembly-CSharp.dll` (experimental), using
`tools/bin/{DumpMethod,DumpType,EnumDump,Census,NetProtocolCensus,FullSurface,FindCallers}`.
Raw dumps: the session scratchpad (not committed).
Baseline census re-run: gmUpdate IL=631, WorldState.SaveLoad=884, 193 top-level
NetPackage types, 4401 types / 43901 method bodies. All match `docs/coverage.md`-era
claims.

Verdict scale: **WRONG** (contradicted by IL), **UNSUPPORTED** (asserted as fact, no
IL basis found where the doc places it), **OK-but-imprecise** (substantively right,
detail off).

---

## Summary

The corpus is in much better shape than typical RE write-ups: of roughly 120
spot-checked hard claims (byte layouts, enum values, magic constants, signatures, IL
sizes, namespace censuses), the overwhelming majority verify exactly, including
several non-obvious quirks (UAI integer-division compensation, ChunkAreaBiomeSpawnData
`(maxCount<<8)|count` packing, authorizer order literals, the NetPackageTileEntity
u16-to-i32 widening). However, the audit found **two WRONG core claims** (chat server
routing; experimental-delta CVarOperation attribution), **one WRONG framing of an
entire doc** (crafting server authority), one propagated error (parties-factions
party-chat routing), a completeness gap in the "complete" experimental diff, tool
artifacts leaked into four published files, and recurring count drift between docs
and their own linked inventories.

## Findings (severity-ranked)

### F1. chat.md §2: the server routing state machine is invented, WRONG

> "the server (`ChatMessageServer`) decides the recipient set from the channel"
> "Routed --> Global: EChatType.Global -> all clients / Party -> party members /
> Friends -> friends / Whisper -> recipientEntityIds / Discord -> relay + global"
> "it does not trust the client's recipient list for broadcast channels"
> "A message beginning with the command prefix is instead handed to the console
> dispatcher"

`GameManager.ChatMessageServer` (IL=195, dumped in full) contains **no branch on
`EChatType` at all**. The only routing logic is: after the `ModEvents.ChatMessage`
hook (result != 2), if `_recipientEntityIds != null` send a `NetPackageChat` to each
listed entity id (`ClientInfoCollection.ForEntityId` loop at IL_012B..IL_0177), else
broadcast to all clients (`ConnectionManager.SendPackage` at IL_01B3). The channel
byte is carried, never interpreted. Consequences:

- Party/Friends recipient resolution does not happen on the server; the server sends
  to exactly the client-supplied `recipientEntityIds`. The "does not trust the
  client's recipient list" sentence asserts the opposite of what the IL does.
- There is no command-prefix check in `ChatMessageServer` or
  `NetPackageChat.ProcessPackage` (IL=37, dumped). The `CommandRoute ->
  SdtdConsole.ExecuteAsync` edge is UNSUPPORTED server-side (prefix handling is a
  client chat-UI behavior).
- There is no Discord relay branch; `Discord` is just an enum value on the wire.

The §1 wire body, `Setup` signature, `EChatType` 0..4, and `EnumGameMessages` 0..6
all verify exactly. The doc's §2 needs a rewrite to "recipient-list-or-broadcast,
channel is advisory", which is also a security-relevant fact (a client can address
arbitrary entity ids on any channel).

Minor in the same section: "a handler returns false -> drop", the actual mechanism
is `ModEventInterruptible<SChatMessageData>.Invoke` returning
`(EModEventResult, Mod)` with result==2 suppressing the fan-out, not a bool return.
Also note `ChatMessageClient` is invoked locally at IL_0075 regardless of the mod
result; only the network fan-out is gated.

### F2. experimental-delta.md §4: CVarOperation is not new, WRONG

> "New enum **`CVarOperation`** { 0 set ... 7 percentsubtract }, and
> `EntityBuffs.SetCustomVar(name, value, ..., CVarOperation, bool)` **gained the
> operation parameter**. So buff/MinEvent cvar writes can now **arithmetically
> modify** a cvar ... a real behavior change to the effect system."

Stable V3.0.1 already contains `CVarOperation` with the **identical** eight members
0..7 (EnumDump on the stable DLL), and stable `EntityBuffs.SetCustomVar(String,
Single, Boolean _netSync, CVarOperation _operation)` (IL=126) plus
`SetCustomVarNetwork(String, Single, CVarOperation)` already take the operation.
The only experimental change is the added trailing `Boolean _forceSendToClients`
parameter (exp IL=130). The claimed "real behavior change" (arithmetic cvar ops
being new) is wrong; the actual delta is a net-sync forcing flag. §4 must be
rewritten and the buffs/minevents cross-references corrected.

### F3. crafting-recipes.md: server-authority framing, WRONG / UNSUPPORTED

> "Crafting is validated and executed on the server (it consumes real inventory and
> produces real items), so it is a dedicated codepath"
> "**Server-authoritative:** validation, ingredient consumption, output production,
> and XP all happen on the server; the client only drives the UI."
> "backpack crafting runs it on the player"

`FindCallers` shows `Recipe.CanCraft(IList<ItemStack>, EntityAlive, Int32)` has
**exactly one caller in the whole assembly: `XUiC_ItemActionList.SetCraftingActionList`**,
a client UI controller. `RecipeQueueItem` consumers are `CraftingData.Read/Write`
(player save blob), `TileEntityWorkstation` (the genuinely server-ticked queue,
correctly owned by tile-entities-power.md), and `XUi`/`XUiC_*`/`XUiM_Workstation`
(client). On a dedicated server, a remote player's backpack craft queue runs in that
player's own client XUi and reaches the server as inventory/stat deltas; the server
does not re-validate `CanCraft`. The doc's central authority claim inverts this.
The "ingredients reserved" / "Cancelled -> refund reserved ingredients" lifecycle is
also asserted with no cited IL. The recipe model table itself (members, `Read/Write`,
unlock via `RecipeUnlockData`) is fine. The doc needs the honest split: definition +
workstation queue are server-relevant; validation and the backpack queue are client
paths whose results are synced.

### F4. parties-factions.md §2.3: party chat routing, WRONG (propagated from F1)

> "**Party chat.** `EChatType.Party` (channel 2) fans a message to party members
> only, routed server side in `GameManager.ChatMessageServer` ([chat.md] §2)."

Same IL as F1: `ChatMessageServer` does no party-membership resolution; the party
recipient set is whatever entity-id list the sending client provides. Everything
else spot-checked in this large doc verifies exactly: `PartyActions` 0..7 (both
nested enums), `AllyStatus` 0..3, `AllyEvent` 0..10, `Relationship`
{0,200,400,600,800,1001}, `GetPartyXP` = `1 - 0.1 * MemberCountInRange` (IL
constants 1, 0.1), `EnumGameStats` PartySharedKillRange=54 / AutoParty=56 /
BloodMoonDay=58.

### F5. experimental-delta.md §1: census note arithmetic + omitted SaveLoad change, MAJOR

> "methods-with-body 43901 -> **44094** (+193, of which ~72 are the new types and
> **~105 are new methods on existing types**; **29 methods removed**)"

72 + 105 - 29 = 148, not 193. The three sub-figures cannot reconcile with the net
delta as stated (net +193 requires added ≈ 222 with 29 removed). At least one figure
is wrong or the sentence conflates net/gross. Additionally, the doc's own census
lens shows `WorldState.SaveLoad(Stream)` grew **884 -> 926 IL** in experimental (I
re-ran `Census.exe` on both DLLs), i.e. a save-format change, presumably held-entity
state. A doc that owns "the complete reverse-engineered diff" (its own words:
"**Owns:** the complete ... diff") must either list the save-format change or mark
it as an open item. Everything else checked in this doc verifies: TE wire change
(stable `conv.u2`/u16 vs exp `teBlockId:i32` + `conv.i4`/i32, both read and write),
type census 4401->4414, `EnumGamePrefs` Last 315->316 with
`DiscordMuteDmNotifications=315`, `EntitlementSetEnum` HenpocalypseCosmetic=17 /
TwitchWatcherCosmetic=20, `ELogType` (absent in stable; note it is **nested in
`ConsoleCmdGetSandboxOptions`**, which the table could state), grab refactor
(`EntityAlive.InitLocalActivationCommands`/`ClearDistressed` present in exp;
`EntityAnimalRabbit.OnEntityActivated` present in stable, absent in exp;
`ItemClassHeldEntity.StartHolding` present), `ConsoleCmdLogEnvironment` new in exp.

### F6. Tool artifacts leaked into four published docs: MAJOR (hygiene)

`dynamic-mesh.md`, `platform-auth.md`, `loot-economy.md`, `weather-environment.md`
end with literal lines:

> "</content>
> </invoke>"

These are serialization artifacts of the writing tool left in tracked files
(dynamic-mesh.md:359-360, platform-auth.md:481-482, loot-economy.md:330-331,
weather-environment.md:298-299). Trivial to fix, but they are exactly the kind of
"survived from an earlier draft" content an external reader will notice first.

### F7. Count drift between docs and their own linked inventories: MINOR (recurring)

- **console-commands.md**: "the 190-command contract" and "~190 concrete commands"
  vs its own linked catalog line "all 186 commands" and the catalog's own header
  "**186 commands.**" (Independent count: 182 distinct `ConsoleCmd*` type names in
  the type surface, 189 types with a `ConsoleCmd*` base; the doc should pick the
  catalog's number and say how it is counted.)
- **minevents.md**: Evidence says "the **72** concrete `MinEventAction*` leaves",
  §4 says "The 72 leaves", the leaf-catalog link says "all **71** triggered-effect
  leaves". Ground truth: 72 `MinEventAction*` types total, of which 4 are `*Base`
  (Base, TargetedBase, BuffModifierBase, SoundBase), so 68 concrete leaves, or 71
  subclasses-of-the-root counting the three derived bases. 72 is wrong under any
  definition ("concrete leaves" cannot include the root).
- **items.md**: header Not-scope says "the ~122 `Item*` leaves and ~92 `ItemAction*`
  subclasses" while its own Evidence line says "103 `Item*` types, 41 concrete
  `ItemAction*` leaves". These cannot both be right (independent count: 106
  `Item*`-prefixed types, 76 of them `ItemAction*`, 68 with an `ItemAction*` base).
  The wire layout in §2 (`ItemValue.Write`: marker 9, flags, type u16, UseTimes f32,
  Quality u16, Meta u16, metadata, stats i16 pairs, mods/cosmetics recursive,
  Activated u8, SelectedAmmoTypeIndex u8, Seed u16, TextureFullArray bool) was
  verified opcode-by-opcode and is exact, as is the `ItemStack` count>0 gating.

### F8. Assorted OK-but-imprecise details

- **dynamic-mesh.md §4**: "Both save paths retry (up to `tryCount` 5)",
  `WriteRegion` compares against 5, but `WriteRegionHeaderData` compares against
  **10** (`ldc.i4.s 10`). One number, two paths.
- **vehicles-drones-turrets.md §1**: "a `vd.a\0` char signature", the header is
  three chars `'v','d','a'` then a **zero byte**, then version byte 1 (`ldc.i4.s
  118/100/97` + `Write(Char)` x3 + `Write(Byte 0)` + `Write(Byte 1)`). The stray
  dot in "vd.a" does not exist on disk; render it as `"vda" 0x00 0x01`.
- **buffs.md §2**: "`EntityStats.EntityBuffRemoved` recomputes the affected stats",
  the base `EntityStats.EntityBuffRemoved` is an IL=1 no-op; the recompute lives in
  the `PlayerEntityStats` override (IL=63). Fine for players, silently nothing for
  non-players; say so.
- **mod-loading.md §2**: the state names (Discovered / DefinitionLoaded /
  AssembliesLoaded / Initialized / Loaded) are narrative labels; the real
  `Mod.EModLoadState` is {LoadNotRequested, Success, NotAntiCheatCompatible,
  SkippedDueToAntiCheat, DuplicateModName, FailedLoadingAssembly, Failed}. The doc
  names the enum ("Each `Mod` carries an `EModLoadState`") and then draws a machine
  whose states are not those values; either map the labels to members or relabel.
  (`SkipLoadingWithAntiCheat` is a real property; pipeline methods all verified.)
- **spawning.md §3**: the persisted `CountsAndTime` description omits the leading
  entry-count byte (`min(dict.Count, 255)` written as u8 before the entries);
  packing `(maxCount << 8) | count` as u16 + `delayWorldTime:u64` + version byte 2
  all verified exactly.
- **experimental-delta.md §6**: "new enum `ELogType`", true, but it is nested in
  `ConsoleCmdGetSandboxOptions`; worth stating since a reader will not find a
  top-level `ELogType`.

### F9. Docs whose spot-checks all passed (explicit clean list)

For each doc below, every claim I selected for verification checked out against the
IL; no discrepancies found in the sampled set:

- **webserver.md**: Webserver.* = 72 types / 413 method bodies (summed from the
  FullSurface namespace table); named handler/API/permission types all present.
- **server-lifecycle.md**: `StartGame(Boolean)` / `startGameCo`,
  `PlayerSpawnedInWorld(ClientInfo, RespawnType, Vector3i, Int32)`,
  `GameStateManager.{InitGame,OnUpdateTick,nextRound,SetBloodMoonDay}` signatures;
  all seven listed `GameMode*` classes exist.
- **platform-auth.md** (modulo the F6 artifact): all 18 dumped `get_Order` literals
  match the chain table exactly (20/30/41/50/60/70/80/81/150/400/430/450/470/490/
  500/550/600/601) plus `AuthFinalizer` 999; `EAuthorizerSyncResult` 0..3;
  `EKickReason` 8/9/19/24/33/34 names; `EPlatformIdentifier` order.
- **spawning.md**: `EnumSpawnerSource` {Biome=1, StaticSpawner=2, Dynamic=3};
  `AIDirector.CanSpawn` = `GameStats.GetInt(12=EnemyCount) <
  GamePrefs.GetInt(99=MaxSpawnedZombies) * priority`; MaxSpawnedAnimals=129;
  28/54 and 48/70 rings, 4 x 2.5 x 4 anti-stack box, 80 m player rect.
- **buffs.md** (modulo F8): AddBuff/RemoveBuff/AddBuffNetwork/RemoveBuffNetwork/
  RemoveBuffsByTag/HasBuffByTag/RemoveDeathBuffs(FastTags)/Tick signatures;
  `BuffValue.DurationInTicks` property exists.
- **game-events.md**: namespace census 132/39/2/3/3 = 179 types, 747+217+14+20+16 =
  1014 bodies; `ActionCompleteStates` 0..3; `NetPackageGameEventResponse`
  ResponseTypes `Completed = 13`.
- **minevents.md** (modulo F7): `MinEventTypes` spot values (0, 7, 19, 24, 42, 43,
  54, 58, 61, 82, 96, 105, 108-110, COUNT=111); `TargetTypes` 0..5 names;
  `SourceParentType` 1..7 mapping.
- **combat-damage.md**: `DamageEntity(DamageSource, Int32, Boolean, Single)`;
  `ProcessDamageResponseLocal` (IL=903); `DamageSource.GetEntityDamageBodyPart*`;
  `AffectedByArmor`; `EnumDamageTypes.Suffocation = 16`.
- **twitch-integration.md**: Twitch namespaces = 108 + 9 = 117 types; named
  connection/vote types present. The doc's honest client/server split is consistent
  with the `IsServer` gating claims it makes.
- **tile-entities-power.md**: `InstantiateFromRead` `switch(type - 3)` with 12
  `newobj` targets + the exact "Dropping TE with unknown/outdated type" string;
  `TileEntityType`, `PowerItemTypes` 1..11, `TriggerTypes` 0..4 enums;
  `PowerManager.Update` literals 0.16 and 120; `TileEntity.write` version u16 = 19;
  `power.dat` / `power.dat.bak` strings in `LoadPowerManager`.
- **loot-economy.md** (modulo F6): `LootContainerOpened` fires MinEvent 101
  (`onSelfOpenLootContainer`) before and 100 (`onSelfLootContainer`) after, remote
  via `NetPackageMinEventFire`; `SandboxOptions` TraderSellPrices=130 /
  TraderBuyPrices=131; GamePrefs LootAbundance=87 / LootRespawnDays=88 /
  DayNightLength=60; PassiveEffects EconomicValue=76 / BarteringBuying=148 /
  BarteringSelling=149; `Rent()` uses the literal 30 (twice).
- **quests-challenges.md**: `QuestState` 0..4; Challenges = 48 types / 509 bodies;
  Quests + Quests.Requirements = 7 types / 48 bodies (1+6, 5+43).
- **progression.md**: `AddLevelExp(Int32, String, XPTypes, Boolean, Boolean, Int32,
  ItemValue)`, `AddLevelExpRecursive`, `SpendSkillPoints(Int32, String)`,
  `ResetProgression(Boolean x3)`, `CanPurchase(EntityAlive, Int32)`,
  `RefreshPerks(String)`, `getLevelFloat`/`GetLevelProgressPercentage`/
  `GetExpForNextLevel` all exist as described.
- **vehicles-drones-turrets.md** (modulo F8): `VehicleManager.Update` IL=297,
  `DroneManager.Update` IL=305, `TurretTracker.Update` IL=45; background
  `vehicleDataSave` thread naming.
- **weather-environment.md** (modulo F6): grace period literal 22000 in
  `GenerateWeatherServerFrameUpdate`; `BiomeWeather.CalcGlobalTemperature` constants
  0.01 / -5 / -7.5.
- **world-generation.md**: GamePrefs GameWorld=33 / WorldGenSeed=171 /
  WorldGenSize=172; `WorldBuilder` = 116 fields / 97 methods / 7090 IL exactly as
  stated.
- **dynamic-mesh.md** (modulo F6, F8): `NetPackageDynamicMesh.write` = X:i32, Z:i32,
  UpdateTime:i32, PresumedLength:i32, bytes; `NetPackageDynamicClientArrive.write`
  = count:i32 then per-item X/Z/UpdateTime:i32; protocol census rows chan 1 /
  compress 1 / dir Both and chan 0 / compress 1 / dir ToServer respectively;
  `DynamicMeshManager.Update` IL=404, `DynamicMeshServer.Update` IL=452,
  `DynamicMeshBuilderManager` 18 methods; `SetDefaultThreads` =
  `min(8, max(procCount-2, 1))` then `min(MaxDyMeshData+1)` verbatim; region
  version tag 160 in both WriteRegion and WriteRegionHeaderData; `MaxActiveSyncs`
  and `MaxMessageSize` fields exist.
- **entity-stats.md**: `EntityStats.Tick(UInt64)` / `TickWait`,
  `PlayerEntityStats.TickWait` (IL=133), `UpdatePlayer{Food,Water,Health,Stamina}OT`,
  `UpdateWeatherStats(Single, UInt64, Boolean)`, `UpdateNPCStatsOverTime`,
  `UpdateSandboxOptions` all exist with the described roles.
- **stealth-smell.md**: `TickServer` IL=430 and `SmellTickServer` IL=257 exactly as
  cited; every named method (NotifyNoise, AddNoise, CalcVolume, NoiseCleanup,
  SetClientLevels, SetSmellRadiusTarget(Int32, Boolean, Boolean),
  AttractTickServer, CanSleeperAttackDetect, SmellCountItems,
  SmellUpdateItemsAndBlood, SmellTickEat, SmellTickWet, SmellClear, SmellApplyMode)
  exists.
- **uai.md**: UAI = 23 types / 95 bodies; `.cctor` sets MaxEntitiesToConsider=5,
  MaxWaypointsToConsider=5, ActionChoiceDelay=0.2; the §3.2 integer-division
  compensation quirk is real (`ldc.i4.1 / ldc.i4.1 ... div / conv.r4` in
  `UAIAction.GetScore`). This doc's willingness to document engine bugs is exactly
  the right register.
- **blocks.md**: `BlockValue` bit layout verified getter-by-getter (rotation
  shr 16 & 31; meta shr 22 & 15; meta2 shr 26 & 15; meta3 shr 21 & 1; ischild mask
  0x40000000); `BlockValue.Write` = u32 rawData + u16 damage (6 bytes);
  `Block.Init` IL=2136 and `LateInit` IL=275. (The legacy `BlockValueV3` type uses
  different masks; the doc correctly describes the current type.)

## Questions for the author

- [Q1] chat.md: what was the source for the per-channel routing and command-prefix
  claims? If it was legacy (A20/A21) knowledge or client-side code, the doc should
  say so or drop it; nothing in the V3.0.1 server IL supports it.
- [Q2] crafting-recipes.md: was any server-side `CanCraft`/queue caller found that I
  missed (e.g. via reflection or a net package handler)? `FindCallers` says no.
- [Q3] experimental-delta.md: which lens produced "CVarOperation new"? The enum diff
  should have shown it present on both sides; worth re-running lens 4 to check for
  a tooling bug that may have produced other false "new" rows.
- [Q4] experimental-delta.md: what changed in `WorldState.SaveLoad` (884->926)?

## Revision plan (priority order)

1. Rewrite chat.md §2 (and the §2 claim mirrored in parties-factions.md §2.3):
   recipient-list-or-broadcast, channel byte advisory, mod-hook result enum, no
   server-side command parsing. Note the trust implication explicitly.
2. Rewrite crafting-recipes.md framing: client-side validation + backpack queue,
   server-side workstation queue only; delete the unsupported reserve/refund states
   or back them with IL.
3. Fix experimental-delta.md §4 (CVarOperation -> `_forceSendToClients`), fix or
   annotate the census arithmetic, and add the SaveLoad 884->926 delta (or mark it
   an open item); re-run the enum-diff lens to check for more false positives.
4. Strip the `</content></invoke>` tails from the four affected docs.
5. Reconcile counts: console commands (186), MinEvent leaves (68 concrete / 71
   subclasses; pick one definition), items.md header vs evidence numbers.
6. Apply the F8 wording fixes (tryCount 10, "vda\0", PlayerEntityStats override,
   EModLoadState labels, CountsAndTime count byte, ELogType nesting).

## Inline annotations (quick reference)

> chat.md: "Routed --> Party: EChatType.Party -> party members"
**[F1] WRONG**, no such branch; `ChatMessageServer` sends to client-supplied ids or broadcasts.

> chat.md: "it does not trust the client's recipient list for broadcast channels"
**[F1] WRONG**, it sends to exactly that list whenever it is non-null, on any channel.

> chat.md: "CommandRoute --> [*]: SdtdConsole.ExecuteAsync"
**[F1] UNSUPPORTED**, no command-prefix check exists in the server chat path.

> experimental-delta.md: "New enum `CVarOperation` ... gained the operation parameter"
**[F2] WRONG**, enum and parameter exist identically in stable; the new thing is `_forceSendToClients`.

> experimental-delta.md: "+193, of which ~72 ... ~105 ... 29 methods removed"
**[F5] WRONG (arithmetic)**, 72+105-29 = 148 != 193.

> experimental-delta.md: "**Owns:** the complete reverse-engineered diff"
**[F5] OVERCLAIM**, omits the WorldState.SaveLoad 884->926 save-format change its own census lens reports.

> crafting-recipes.md: "validation, ingredient consumption, output production, and XP all happen on the server"
**[F3] WRONG**, `Recipe.CanCraft`'s only caller is `XUiC_ItemActionList` (client UI).

> crafting-recipes.md: "Queued: valid -> RecipeQueueItem enqueued, ingredients reserved"
**[F3] UNSUPPORTED**, no cited IL for reservation/refund semantics.

> parties-factions.md: "`EChatType.Party` (channel 2) fans a message to party members only, routed server side"
**[F4] WRONG**, see F1.

> dynamic-mesh.md / platform-auth.md / loot-economy.md / weather-environment.md: "</content></invoke>"
**[F6]**, leaked tool artifact at EOF.

> console-commands.md: "the 190-command contract" vs "(all 186 commands ...)"
**[F7] INCONSISTENT**, same doc, two counts.

> minevents.md: "the 72 concrete `MinEventAction*` leaves" vs "(all 71 triggered-effect leaves)"
**[F7] INCONSISTENT**, 72 includes the 4 abstract bases; concrete leaves are 68.

> items.md: "~122 `Item*` leaves and ~92 `ItemAction*` subclasses" vs "103 `Item*` types, 41 concrete `ItemAction*` leaves"
**[F7] INCONSISTENT**, both sets differ from the surface census (106 / 76 / 68-with-ItemAction-base).

> dynamic-mesh.md: "Both save paths retry (up to `tryCount` 5)"
**[F8] OK-but-imprecise**, WriteRegion 5, WriteRegionHeaderData 10.

> vehicles-drones-turrets.md: "a `vd.a\0` char signature, a version byte `1`"
**[F8] OK-but-imprecise**, actual bytes: 'v' 'd' 'a' 0x00, then version 0x01.

> buffs.md: "`EntityStats.EntityBuffRemoved` recomputes the affected stats"
**[F8] OK-but-imprecise**, base override is a no-op (IL=1); `PlayerEntityStats` does the work.

> mod-loading.md: "Discovered --> DefinitionLoaded --> ... --> Loaded"
**[F8] OK-but-imprecise**, labels do not correspond to the named `EModLoadState` members.

## Sources

- Local IL dumps in the uncommitted session scratchpad: chat-write.il, chatserver.il, chatproc.il, te-write-stable.il, te-write-exp.il, te-read-exp.il, exp-setcustomvar.il, eb-CustomVar.il, rc.il, vmall.il, iv.il, bv1-3.il, bvw.il, smb.il, cab.il, ord.il, af.il, lco.il, vm.il, pxp.il, uai-gs.il, uai-c.il, wt2.il, wg.il, dmf-wr.il, sdt2.il, META.md, fs/
- `tools/bin/Census.exe` output for both DLLs (stable: 4401/43901/884/631; exp: 4414/44094/926/631)
