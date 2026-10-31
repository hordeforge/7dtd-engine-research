# Releasing 7dtd-engine-research (tag series, what each version means)

**Hub:** [`INDEX.md`](../INDEX.md). **Corpus pin:** V **3.3.0 (b18)**
([`tools/data/stock_facts.json`](../../tools/data/stock_facts.json)).
**Not:** a game release. Nothing here describes a 7 Days to Die build; those
live in [`changelog-3.2.0.md`](changelog-3.2.0.md) and its two predecessors.

This repo has two independent jobs that used to be one release: the **corpus**
(the RE narratives, pinned to a game build) and the **tooling** (the dumpers
and gates under [`tools/`](../../tools)). The tag history carries both in one
list, so the numbers mean different things depending on which series a tag
belongs to. Read the series before choosing the next number.

## The two series

| Series | Form | What the number tracks | When it moves |
|---|---|---|---|
| Corpus | `v3.Y.0` | The studied game build. `v3.1.0` is the corpus for game V3.1.0 b14, `v3.2.0` for V3.2.0 b10, `v3.3.0` for V3.3.0 b18. | A TFP update that the corpus is re-pinned to (`make post-update`, then a new `changelog-<game-version>.md`) |
| Tooling | `v0.Y.Z` | This repo's own tooling and docs, independent of any game build. | A tooling or corpus change that does not re-pin the corpus |

A corpus release may carry tooling changes (the `v3.2.0` cut shipped
`tools/steam/`, `research_diff.py` and the drift baselines). That does not make
a tooling release, because the number still says which game build the pins
name. When both move, the corpus series wins, because that is the number a
reader uses to check a pin against.

## Tag history

Annotated tags, newest first, with the subject of the tagged commit:

| Tag | Date | Tagged commit |
|---|---|---|
| `v3.3.0` | 2026-10-25 | `docs: add the v3.3.0 release notes` (corpus V3.3.0 b18) |
| `v3.2.0` | 2026-09-21 | `tools: split by domain and share one helper module` (corpus V3.2.0 b10) |
| `v0.2.0` | 2026-09-11 | `Merge pull request #21 from hordeforge/docs/subsystem-folders` (tooling) |
| `v0.1.2` | 2026-08-26 | `Merge pull request #16 from hordeforge/chore/agent-rules-conformance` (tooling) |
| `v3.1.0` | 2026-08-23 | `Merge pull request #2 from hordeforge/tools/cecil-pin-and-test-hardening` (corpus V3.1.0 b14) |
| `v0.1.1` | 2026-08-23 | `Release update: HordeForge branding, path updates, and documentation alignment` (tooling) |
| `v0.1.0` | 2026-08-22 | `docs: wire texture-atlas docs into hub and fix stale 6.23 count test` (tooling) |

`v0.1.0` is the earliest tag; the repo had no versioned releases before it.

### The `v0.3.0` hole

`v0.3.0` was tagged but never released: the tag's CI run was red, the stray
annotated tag that pointed at its commit was deleted on 2026-09-22, and no
GitHub release was ever published for it (`workspace/CHANGELOG.md`, entries
for 2026-09-21 and 2026-09-22). No consumer resolved a `v0.3.0`, but the number
is burned anyway: the next tooling release is **`v0.4.0`**, because reusing
`v0.3.0` would make the tag list disagree with whatever a consumer cached
while the bad tag was up. Never reuse a published tag, deleted or not; cut a
new number.

## Unreleased

- [`../world/blocks.md`](../world/blocks.md) §1 records how a model's texture travels:
  the renderer's `m_Materials[0]` names a Material whose `_MainTex` names the Texture2D,
  the material is per model and the texture per atlas (`Hollywood_Juniper_15m` binds the
  2048x2048 `Hollywood_Juniper_Atlas`), and the renderer's PPtr is the only reliable
  link because a material and a texture of the same name exist side by side.

**53 commits after `v3.3.0` (2026-10-25) as of 2026-11-01.** The retarget this
section used to describe is published under the tag and in
[`release-v3.3.0.md`](release-v3.3.0.md); what follows is post-cut bookkeeping.

- [`../world/blocks.md`](../world/blocks.md) records the shape-group helper's own
  properties and the `SortOrder2` assignment: each shape numbered from a counter that
  starts at 1, the helper at `"0000"`, plus `SelectAlternates` and the comma-joined
  `PlaceAltBlockValue` list; also the shapes' `ShapeCategories` and the `<categories>`
  order that structure the picker.

- [`../content/quests-challenges.md`](../content/quests-challenges.md) §9 records the
  tier statics' defaults (`MaxQuestTier = 5`, `QuestsPerTier = 10`), the file's override
  (6), and what `CompleteQuest` credits (`AddsToTierComplete` default true,
  `AddsProgression` = `QuestProgressDay > 0`, points = `DifficultyTier`, no-op on zero).
  `QuestJournal.Write` stores no faction points; a load re-derives them. The daily cap's
  stat default is pinned at 4 (`QuestProgressionDailyLimit`), and the stamp's only
  caller is `ObjectiveReturnToNPC.OnStart`.

- [`../content/npc-dialog.md`](../content/npc-dialog.md) §8 records the `quest_faction`
  parse: written only when the attribute exists, so an absent one is 0.

- [`../gameplay/items.md`](../gameplay/items.md) §4.2 records the exact accuracy decay
  (`9.1 * Clamp01(passive 13, base 0.1)`) and the per-shot bloom
  (`IncrementalSpreadMultiplier`, capped at 5).

- [`../gameplay/crafting-recipes.md`](../gameplay/crafting-recipes.md) §2 records that
  `GetRecipeCraftTime` scales `recipe.craftingTime` with passive 90 at the recipe's own
  tags and clamps at zero.

- [`../gameplay/loot-economy.md`](../gameplay/loot-economy.md) §8.5 records that
  `LootContainer.SpawnItem` scales a spawned count by passive 81 with the spawned item's
  tags plus the container's, truncating once and clamping to the item's stack size.

- [`../gameplay/items.md`](../gameplay/items.md) §4.2 records the melee attack rate:
  `ItemActionDynamicMelee.canStartAttack` and `OnHoldingUpdate` read passive 18 with the
  item's own tags plus `primary`/`secondary`, and a swing waits `60 / rate + 0.1` s; the
  stone shovel's `base_set` is 50.

- [`../gameplay/items.md`](../gameplay/items.md) §4.2 records that the ranged reload has
  no timer in the item data: `AnimatorRangedReloadState` fires `onReloadStart`,
  `onReloadUpdate` and `onReloadStop` (58/59/60), its state exit is the only
  `ItemActionRanged.CompleteReload` call site, and passive 102
  (`ReloadSpeedMultiplier`) is evaluated with base 1 by both avatar controllers into the
  animator's `reloadSpeed` parameter, so it scales the reload clip whose length lives in
  the asset bundles.

- [`../world/world-generation.md`](../world/world-generation.md) §3.5 corrects the
  wilderness-road spawn walk (`createTraderSpawnIfAble`): it creates player spawns, not
  traders, and the zero its biome test compares against is `forest` (the RWG enum runs
  `forest` 0 to `wasteland` 4, `none` 255), so the walk requires a forest column and
  spawns on forest columns whose tile carries only `DifficultyTier <= 1` prefabs.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 records where
  traders come from: the five shipped `trader_*` prefabs are `gateway`-tagged, one
  street tile (`rwg_tile_gateway_straight4`) carries a 60x60 `POISpawn` marker tagged
  `gateway`, and each trader's `prefab_spawn_adjust` names its biome with `bias="20"`,
  `min_count="2"` and `max_count="4"`. `TownshipData.SpawnTrader` is parsed and never
  read, and `createTraderSpawnIfAble` places player spawns, so the marker is the whole
  path.

- [`../world/world-generation.md`](../world/world-generation.md) §3.6 records how the
  builder picks the twelve player spawns: street tiles with no township, no radiation, no
  water, an empty or `wilderness` district, forest when the world weights forest and never
  `Used`, sorted by the distance to the nearest trader and taken with `isFallback: true` so
  nothing else is checked; the full tests (60 block spacing, prefabs at
  `DifficultyTier < 2`, a trader within 900 blocks) apply to the wilderness-road caller
  instead.

- [`../world/world-generation.md`](../world/world-generation.md) §3.5 records how a
  township that spawns no gateway still gets a road out: `RunTownshipDirtRoads` walks only
  the townships whose kind states `spawn_gateway="false"`, takes each unused town exit,
  finds the nearest point on a highway that a country-road A* can reach, draws a
  two-block-radius country path to it, books every tile exit within ten blocks used, and
  appends it to `highwayPaths`.

- [`../world/world-generation.md`](../world/world-generation.md) §3.6 records how
  `SmoothRoadTerrainTask$BurstManaged` bends terrain under a road: an influence mask
  built from splat3's red (highway, `255` core, rings `60, 52, 44, 36, 28, 20`) and green
  (country, `200` core, rings `80, 50, 20`), a height lift of `0.0008` on every road cell,
  six clamped-neighbour passes over the highway core with weights 0.5 orthogonal and 0.25
  diagonal normalised by 4, and thirty mask-weighted passes over the blend band with
  `alpha = mask * 0.005` and an outright replace on the country core.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 records how a
  township gains its gateway tiles: `DistrictPlanner.PlanTownship` fills the districts
  first, then walks each `dir4way` direction once (twice for a township named `citybig`,
  not at all for a kind that states `spawn_gateway="false"`), and `GenerateGatewayDir`
  accepts at most one out-of-town neighbour per call, exactly one of whose own neighbours
  carries a township while at least two are valid ground. The accepted tile joins
  `Township.Streets` and `Township.Gateways` with district type `Gateway` (3), a pass
  never starts from a gateway an earlier one made, and a roadside township takes
  `GenerateGateway`, which marks every street. `IsValidForGateway` is
  `IsValidForStreetTile` plus `!HasPrefabs`.

- [`../world/world-generation.md`](../world/world-generation.md) §3.5 records how a
  wilderness POI gets a road: `WildernessPathPlanner.Plan` connects one record per
  spawned-prefab `POIMarkers` volume of marker type 2 (centre and half its larger
  horizontal side), picks the cheapest A* endpoint along a highway within a 250-block
  window sampled every fifth node, sorts records by radius bucket then highway distance,
  and otherwise chains to an already-pathed, wider POI's road within 700 blocks. A road
  of five or more points then tries a trader spawn on a tile whose prefabs are all
  `DifficultyTier <= 1`.

- [`../world/blocks.md`](../world/blocks.md) §1 records where a model block's
  prefab is placed: `BlockShapeModelEntity::Init`'s default `modelOffset` of
  `(0, 0.5, 0)`, `GetRotatedOffset`'s `rot * modelOffset + rot * base` with the
  multi-block centring of `base`, and `Chunk::OnDisplayBlockEntities`'s half-cell
  shift and decoration lift, which together put the prefab root at the block's
  centre rather than its corner. The juniper's `0,-0.3,0` therefore lands at
  `(0.5, -0.3, 0.5)`, and the prefab's own child transforms (the tyre's quarter
  turn) are the block's to apply.

- [`../world/world-generation.md`](../world/world-generation.md) records how a highway picks
  the townships it joins: `HighwayPlanner.ConnectClosest` walks a township's gateways,
  skips one that already carries two exits, orders candidates by the distance from the
  *gateway tile* to each township's centre, tries at most three, penalises a pair that is
  already connected by 1.6x, and books a winner into `highwayPaths` with both connection
  counts incremented. `ConnectSelf` pairs a town's own gateways clockwise.

- [`../world/world-generation.md`](../world/world-generation.md) records what
  `checkresource` on a `biomes.xml` decoration is: an integer Y offset for the ore-noise
  probe (`checkResourceOffsetY`), defaulting to 10000 for a prefab decoration and to
  `int.MaxValue` (no probe) for a block one, read at placement as
  `CheckOreNoiseAt(resourceNoise, x, surfaceY + offset, z)` against
  `PerlinNoise(World.Seed)` cleared at `0.111`. The shipped ore veins' `-7` probes seven
  blocks below the surface, and an absent attribute is still a probe, not a pass.

- [`../world/blocks.md`](../world/blocks.md) §1 records a block's `Model`
  reference: the two shipped forms (`#Bundle?objectPath`, `@:path`), inheritance
  through `Extends`, `ModelOffset`, `MultiBlockDim`, the 6,529-block /
  2,420-reference count, the prefab-to-mesh graph, and the address resolution by
  family segment (`@:Other/Items/...` is `automatic_assets_other/items.bundle`)
  with the sole catalog at `7DaysToDie_Data/StreamingAssets/aa/catalog.json`.

- [`../world/world-generation.md`](../world/world-generation.md) §3.5 records
  `SpawnMarkerPartsAndPrefabsWilderness` (IL=537): the position-string RNG seed,
  the rotated marker list, the `POISpawn` placement alignment and `YOffset`, the
  `PartSpawn` grouping with normalised cumulative chances and one part per group,
  the mirrored rotation and the missing `YOffset`, the absence of any depth,
  bounds or overlap test, and the two corrections it brings: a wilderness
  `POISpawn` does not simply sit at the parent plus the marker start, and the
  parts block is not a flat roll.

- [`../world/world-generation.md`](../world/world-generation.md) §3.5 records
  wilderness POI placement in full: the per-biome counts and their `rwgmixer`
  values, the candidate tile tests, the farthest-from-township low-biased tile
  pick with 20 attempts, the per-tile rotation and 20-block inset, the footprint
  tests (water, biome, 11-block height spread), the median placed height, the
  `RoadExit` path anchor, the wilderness pick's tags and retry, and the
  correction that the low-biased draw is the tile index, not a prefab size.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 records the
  per-tile prefab density budget: the 62 default, `TileMaxDensityScore` filled from
  `rwgmixer`'s `<streettile maxdensity>` (which the shipped file never states), the
  integer `DensityScore` formula, the budget gate and the caller's charge, the three
  retry attempts, what `_distanceScale` really switches, the parts that charge without
  being gated, and the depth-0 neighbour penalty with its 190-unit radius and 1.3
  multiplier.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 records the
  placement arithmetic of `StreetTile.SpawnMarkerPartsAndPrefabs`: the `POISpawn`
  filter and its size-descending sort, one child per group, the shuffle seed that uses
  the parent's height rather than z, the rotation composed from the parent, the prefab's
  `RotationToFaceNorth` and the marker, the flush-to-edge offsets of a turned marker,
  the parts block with its mirrored rotations and bounds refusal, and the gateway block
  that needs this tile's own exit toward a same-township neighbour. It also records the
  nine shipped gateway tiles that carry `highway_transition` markers and that the parts
  loop can add the same marker a second time, since the IL marks none used.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 records the five
  road-shape prefabs, the `RoadShapeExits` static array (**5, 7, 15, 4, 6**, read from
  the assembly's `<PrivateImplementationDetails>` blob) and the direction order that
  makes each mask a shape.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 records how a
  township's RWG biome tag finds its `biomes.xml` row: through `biomemapcolor`
  against the biome colours, so `forest` is `pine_forest` and `burntforest` is
  `burnt_forest`.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 records that
  a district's `tag` and `prefab_name` default to its own name, so the prefab
  pick's district gate applies even to a district that states neither.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 pins the
  prefab pick: the prefab metadata `PrefabData.Init` builds, the loader's tag
  filters, every gate `GetPrefabWithDistrict` applies, the theme and duplicate
  spacing checks, and the score formula with the `prefab_spawn_adjust` defaults.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 pins the
  district fill: the name-derived type and spawn order, the candidates whose
  required township matches and whose weight is above zero, normalised weights and
  reversed avoid links, the quota per district, the neighbour-first pick, and the
  roadside all-gateway case.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 pins how the
  planner chooses a biome while placing: the per-biome candidate list, the
  most-space pick with its lowest-index tie, `nextBiomeType`'s five-index
  advance, and the 80-try and 30-try retry paths.
- [`../world/world-generation.md`](../world/world-generation.md) §3.3 pins how a
  street tile earns its validity: nine slope and radiation samples at ±75 blocks,
  a 3-block stride over the tile for biome and water, the 20-block slope and 90
  percent water thresholds, and the same three checks in
  `IsValidForStreetTile` plus the mountain terrain type.

- [`../world/world-generation.md`](../world/world-generation.md) §3.3 pins the
  town planner's inputs and placement: how a township's `count`, `tiles` and
  `distance` are read (`Towns` is `Default`, tiles default to 1, 1, distance to
  5), the square `IsTooClose` box with its fixed 5 tiles between roadside
  towns, and how `GetStreetLayout` seeds and grows a tile layout while `Grow`
  thins the outskirt ring.

- The tag history row for `v3.3.0`, the corpus pin in this file's header, and
  the reset of this section land after the cut, so the release notes stay the
  record of what shipped and this file stays the contract for what comes next.
- [`../gameplay/items.md`](../gameplay/items.md) records that no block item is
  authored in `items.xml`: a block item is constructed from `Block.list`, so the
  id links them, not a shared name.
- [`../world/blocks.md`](../world/blocks.md) records the face order of a
  multi-value `Texture` property: top, bottom, north, west, south, east, with
  rotation permuting the four sides and an out-of-range index falling back to
  the first id.
- [`../world/texture-atlas.md`](../world/texture-atlas.md) gained §4: the block
  atlas images (nine 407-layer `Texture2DArray` objects, the five families that
  are single 2D atlases instead), the opaque tile space, and the per-file rect
  shapes.
- The tile packing in that section is now verified rather than inferred: the
  four slices of a 2x2 entry join with a mean difference of 6 to 8 against 62
  at the next texture, and the order is row-major. Its face-to-slice rule is
  decoded too (`ComputeTaIndexOffsFor`: `index + uIdx + vIdx * baseW`, V flipped
  unconditionally), which agrees with the measured layout. The count in this
  section is corrected with it, since the previous change left it one behind.
- [`../world/world-generation.md`](../world/world-generation.md) §6 records what
  the sleeper-volume properties do. `SleeperIsLootVolume` sets
  `PrefabSleeperVolume.isPriority`, a placement tie-break for overlapping
  volumes, not a loot marker; `SleeperIsQuestExclude` sets `isQuestExclude`. The
  precedence rule is `Prefab.FindSleeperVolume`'s: the last containing volume
  wins unless a containing volume is marked priority, which returns at once.
  The count above is brought up to date here too, since two commits landed
  without a bump.
- [`../world/block-shapes.md`](../world/block-shapes.md) §7.1 records the two
  layouts a consumer needs for block triggers: the `.tts` trigger section
  (`i16 count`, then `i16 length` + `Vector3i` + body) and `BlockTrigger.Read`'s
  versioned body, plus the `AllowBlockTriggers` filter that drops wiring on a
  block that cannot use it. It also states that nothing between the block payload
  and the triggers is length-prefixed, and how `SimpleBitStream` packs its flags.

The next cut is `v0.4.0` (tooling) unless the corpus is re-pinned to a new game
build first, which would be `v3.4.0`.

## Cutting a release

`tools/release.sh <vX.Y.Z> [--notes FILE] [--dry-run] [--skip-gates] [--resume]`. It
refuses a dirty worktree, a tag that exists locally or on origin, a branch behind
`origin/main`, an unauthenticated `gh` and a missing notes file; it runs the
DLL-free gates (`make lint`, `make test-docs`) before tagging (`--skip-gates`
skips both, and a dry run skips them too, since it changes nothing), then pushes
`main`, tags annotated, pushes the tag and creates the GitHub release. CI runs
the DLL-dependent half on the push.

A run that dies between those steps leaves a half-published version, and the
refusal on an existing tag would leave it that way for good. `--resume` is the
way out: the tag must exist (locally or on origin) and name `HEAD`, the tag and
its push are skipped when they already landed, and the release is created only
when `gh release view` does not find it. Two resumes leave the same state as
one, and a tag on any other commit is refused rather than published under a live
version.

Notes are required and reviewed, not generated: the default path is
`docs/releases/release-<version>.md`, which is a different thing from the
`changelog-<game-version>.md` game digests that sit beside it. A release with
nothing to say still gets notes; the tag has to be explainable from the tree.

`make test-docs` runs before the tag, and it includes
`tests/test_release_contract.py`, so a cut is refused while this file
disagrees with the repository: a tag with no history row, a row for a tag that
no longer exists, an Unreleased section that does not count the commits below
the last tag, or a "next cut" naming a version already published. That gate is
the reason the Unreleased section above states a count instead of a date.

The count is checked only while commits are unreleased. The tag push is the
moment `git rev-list --count <last-tag>..HEAD` returns 0, and the section still
describes the cut that has just happened until the next edit resets it; failing
there would turn every release's own CI run red over prose nobody reads in
between, which is how `v0.3.0` ended up tagged, unreleased and deleted. The
gate takes `--contract` and `--repo`, and
`tests/test_release_contract_gate.py` runs every one of its detectors, this
case included, in a throwaway repository. `make release-count` prints the
number the section must carry, so the count is written before CI reads it
rather than after.

**Hub:** [`INDEX.md`](../INDEX.md).
