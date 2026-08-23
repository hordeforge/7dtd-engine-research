# Full corpus audit: 7dtd dedicated-server RE docs (V3.0.1)

**Date:** 2026-07-24. **Scope:** all 49 narrative docs + 14 inventory catalogs
(~17.8k lines), tooling, policy, and structure. **Method:** deterministic
mechanical/policy pass (lead) + 7 parallel per-cluster correctness reviews that
verify load-bearing claims against the shipped `Assembly-CSharp.dll` IL via
`tools/bin/*` (DumpMethod/DumpType/EnumList/MethodList/FindCallers/Census).
Per-cluster detail: `workspace/outputs/audit/cluster-*.md`.

**Verdict:** the corpus is substantially correct. Across the 7 clusters ~400
load-bearing claims were spot-verified CONFIRMED against IL. Structure and policy
are clean. But the review found **3 CRITICAL** wire/format errors that would break
a clone built from the doc, **~11 MAJOR** wrong-behavior/wrong-location claims, and
**~22 MINOR** count/label drifts. All CRITICALs and the key MAJORs were
independently re-verified by the lead before this report. Verification state:
**verified** (each finding traces to a cited IL command).

---

## 1. Mechanical / policy pass (lead, deterministic) - CLEAN

| Check | Result |
|---|---|
| IL dumps / DLLs tracked by git | none (policy-compliant) |
| `.gitignore` covers `il/*` + payloads | yes |
| Committed docs over-quoting disassembly (>15 IL lines/block) | none |
| INDEX registration (every doc reachable) | complete, 0 dead links |
| Broken intra-doc links | 0 |
| Em/en-dashes | 0 |
| Tool-artifact residue (`</invoke>` etc.) | 0 |
| Mermaid diagrams | 158, all well-formed (`block-beta` is valid) |
| Census-number basis | reconciled: 4401 top-level vs 7413 all-types (both correct; labeled `(incl. nested)` on full-surface) |

---

## 2. CRITICAL findings (wire/format-breaking) - 3

### C1. `protocol-packages.md` §4.2 - `NetPackageWorldInfo` tail mis-specified
- **Claim:** `worldHashesData` = `i32 len + byte[len]`.
- **Truth (IL):** `write` emits the hash blob via `BinaryWriter.Write(byte[])`
  **with no length prefix**; `read` parses `i32 count` then `count x { string
  filename, u32 hash }` into a `Dictionary<string,uint>`, then `i64 worldDataSize`.
  The leading `i32` is an **entry count**, not a byte length.
- **Evidence:** `DumpMethod NetPackageWorldInfo write` (IL_0082 `Write(byte[])`,
  IL_008D `Write(Int64)`); `... read` (IL_0070 `ReadInt32`, loop IL_0085-00A6
  `ReadString`/`ReadUInt32`/`Dictionary.Add`, IL_00A9 `ReadInt64`).
- **Impact:** a clone reading the count as a byte length desyncs the stream and
  misparses `worldDataSize`, breaking join.
- **Fix:** rewrite the tail as `worldHashes: i32 count + count x { filename:string,
  hash:u32 }`, then `worldDataSize:i64`.

### C2. `dynamic-mesh.md` §4 - region persistence documents DEAD code
- **Claim:** `.group` region files are written by `DynamicMeshFile.WriteRegion` /
  `WriteRegionHeaderData` with a version-`160` tag + chunk-position table.
- **Truth (IL):** `WriteRegion`/`WriteRegionHeaderData` have **no external
  callers** (only retry self-recursion). The live producer is
  `DynamicMeshChunkProcessor.RegenerateRegion -> DynamicMeshRegionDataStorage.SaveRegion
  -> DynamicMeshVoxelRegionLoad.SaveRegionToFile`, writing through a
  `Noemax.GZip.DeflateOutputStream` (deflate-compressed, no version-160 tag, no
  chunk-position table).
- **Evidence:** `FindCallers DynamicMeshFile WriteRegion` (self only);
  `MethodList | grep` shows `DynamicMeshRegionDataStorage::SaveRegion`,
  `DynamicMeshChunkProcessor::RegenerateRegion`, `DynamicMeshVoxelRegionLoad::SaveRegionToFile`.
- **Impact:** the entire §4 format spec is for code the server never runs. (Note:
  the earlier peer-review retry-count "fix" (WriteRegion <=5 / HeaderData <=10)
  described this same dead code and must be removed with it.)
- **Fix:** rewrite §4 around the live deflate path; mark `WriteRegion`* as legacy/dead.

### C3. `items.md` §2 - `ItemValue` packing table drops the stat-type byte
- **Claim (table declares itself "authoritative for byte order"):** PassiveEffects
  stats section = two `i16` per entry (raw, boosted).
- **Truth (IL):** each stat entry writes a leading **`Byte` stat-type id** then two
  `i16` with semantics "(0-if-boosted value, boosted-or-0 value)", not "raw then
  boosted".
- **Evidence:** `DumpMethod ItemValue Write` IL_0122/0143 `Write(Byte)` preceding
  IL_0175/017D `Write(Int16)` pairs.
- **Impact:** any parser following the table desyncs when flags bit1 is set.
- **Fix:** add the stat-type `Byte` and correct the i16 semantics.

---

## 3. MAJOR findings (wrong behavior / wrong location) - ~11

| # | Doc | Wrong claim | Truth (IL) |
|---|---|---|---|
| M1 | buffs.md §3 | `AddBuffNetwork`/`RemoveBuffNetwork` are "receive-side, applied without re-broadcast" | They are the **send** side (`Setup`+`SendPackage`/`SendToServer`, ch 192). Receive is `NetPackageAddRemoveBuff.ProcessPackage`, which **re-broadcasts** then applies with `netSync=false`. |
| M2 | console-commands.md §2 | per-command permission enforced in `SdtdConsole.executeCommand` | executeCommand (IL=149) only gates device/main-menu; permission is `ConnectionManager.ServerConsoleCommand -> AdminTools.CommandAllowedFor` + web API. Telnet/stdin bypass per-command levels. |
| M3 | console-commands.md + console-command-list.md | 186 commands | **187** concrete `ConsoleCmdAbstract` (missing `exportprefab`/`ConsoleCmdExportPrefab`, whose name is a static field, invisible to ldstr extraction). |
| M4 | server-lifecycle.md | boot "EAC integrity gate" (`eacIntegrityViolation`) | those strings live **only** in `gmUpdate`'s client-only UI block (never executed on dedicated); real boot checks `GameServerInfo.EACEnabled`/`eacWarning`. |
| M5 | mod-loading.md | `Mod.LoadMod` runs `InitModCode`; `LoadPatchStuff`/atlases in the LoadMods pipeline | `InitModCode` is a separate all-mods pass in `ModManager.LoadMods` after every assembly loads; `LoadPatchStuff`/atlases/localization run from `GameManager.Awake`/`startGameCo`. |
| M6 | items.md | ItemAction leaf count 41 (header/§4.1) vs 38 (own catalog) | self-contradiction; reconcile to the catalog's transitive count. |
| M7 | game-events.md / sequence-requirements.md | "43 requirement leaves" of `BaseRequirement` | **38** transitive; the 5 extra are `Quests.Requirements.*` (unrelated same-named base). Concrete GameEvent leaves = 37 (matches game-events §4 text). game-events.md also self-contradicts (39 vs 43). |
| M8 | dynamic-mesh.md §4 | (legacy body) `WriteRegion` writes `Vector3i` per chunk + voxel meshes to disk | even the dead body writes only x,z (no y) + an undocumented `CreateDate.Ticks` i64, no meshes, never touches disk. (Subsumed by C2 fix.) |
| M9 | combat-damage.md | extra `EnumDamageSource` members | only `External=0`, `Internal=1` exist. |
| M10 | full-surface.md | "every codepath a headless server executes is now hand-narrated" | overstates: reached-but-unnarrated server code exists (DiscordManager 140 methods, StringParsers 72, Configuration 58, TEFeatureAbs 49). Defensible claim = subsystem narration + leaf enumeration. |
| M11 | frame-entries.md | "All" MonoBehaviour frame entries (242) | 244 (misses 2 nested). |

---

## 4. MINOR findings (count/label) - ~22 (representative)

- protocol.md/network.md "193 wire packages" overcounts by ~6 (census includes
  name-prefixed non-wire helpers: `NetPackageDirection`[Enum], `Entry`, `Info`,
  `Logger`, `Measure`, `Metrics`).
- spawning.md attributes 45/55 // 55/70 placement bands to scout+screamer; only
  `AIHordeSpawner` uses them (scouts use 0/8/10).
- vehicles-drones-turrets.md inverts `EntityVehicle`/`EntityDriveable` subtype
  relationship; misspells `SpawnFollowingDronesForPLayer` (actual casing).
- dynamic-mesh.md: "Deleting corrupted file" is in
  `DynamicMeshRegionDataStorage.LoadRegion`, not `DynamicMeshRegion`; `MeshLocation`
  set in `Awake` not `Init`; several evidence line-counts don't reproduce.
- webserver.md: wrong command names (`webpermission`, `invalidatecaches`);
  incomplete REST API + handler tables.
- parties-factions.md: cites wrong nested `PartyActions` member (`AutoJoin` vs
  `JoinAutoParty`).
- managers.md: places `EntityAsyncManager` in phase-B chain (actually phase F).
- re-methodology.md §5: `NetProtocolCensus` command fails from its documented cwd
  (needs `../il/`); AGENTS.md cites nonexistent `tools/Census.exe`.
- full-surface.md "145 diagrams" stale (now 158).
- coverage.md "189 in live id-map" has no citable artifact (UNVERIFIABLE-HERE).

---

## 5. What held up (high-confidence CONFIRMED)

Every census number (4401/43901/7413/53011/193/198/gmUpdate 631/SaveLoad 884/87
ns/1,734,742 IL), the reachability pair (28,374 methods / 4,516 types), and the
full experimental delta (4414/44094/926, NetPackageTileEntity wire change) all
reproduced exactly. Load-bearing wire bodies mostly correct: Chat, the 4
encryption packages, Chunk/ChunkRemove/WorldTime, SetBlock/BlockValue bitfields
+ 6-byte Write, the full EntityCreationData header, the 30+-field DamageEntity
body, PackageIds, PlayerLogin, identity ToStream, NetPackageWeather. Sim logic:
PowerManager 0.16 s tick, party max 8 + `xp*(1-0.1*n)`, faction ladder + 60 s
save, GameTimer 20 Hz, aiActiveScale bands, `Recipe.CanCraft` split-authority,
workstation tick/20, degradation floor 0.05. All 6 clean leaf catalogs
(block-behaviors 65, item-actions 38, minevent-actions 71, quest-objectives 38,
netpackages 194, gmupdate-calls 182) matched by transitive recomputation;
console descriptions are genuinely from each command's `getDescription` (8/8
byte-identical); no fabricated per-leaf content found anywhere.

---

## 6. Remediation (COMPLETED 2026-07-24)

1. **CRITICAL (3):** rewrite NetPackageWorldInfo tail (C1), dynamic-mesh §4 live
   path (C2, removing the dead-code retry note), ItemValue stats byte (C3).
2. **MAJOR (11):** buff net-sync direction, console 186->187 + exportprefab,
   server-lifecycle EAC gate, mod-loading InitModCode location, items ItemAction
   count, sequence-requirements 43->38/37 + game-events reconcile, combat
   EnumDamageSource, full-surface overstatement, frame-entries 244.
3. **MINOR (22):** counts/labels/method-name casing/table completeness.
4. Re-verify corpus health (links/dashes/H1) + record resolution in CHANGELOG.

Findings drive the zdtd clone too: C1/C3 change wire bodies the clone must match;
update `../zdtd-server-server/docs/RE_GAP_CLOSURE.md` §2 rows for WorldInfo and ItemValue.
