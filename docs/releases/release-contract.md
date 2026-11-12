# Releasing 7dtd-engine-research (tag series, what each version means)

**Hub:** [`INDEX.md`](../INDEX.md). **Corpus pin:** V **3.4.0 (b10)**
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
| Corpus | `v3.Y.0` | The studied game build. `v3.1.0` is the corpus for game V3.1.0 b14, `v3.2.0` for V3.2.0 b10, `v3.3.0` for V3.3.0 b18, `v3.4.0` for V3.4.0 b10. | A TFP update that the corpus is re-pinned to (`make post-update`, then a new `changelog-<game-version>.md`) |
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
| `v3.4.0` | 2026-11-05 | `docs: restore the release contract count after the rebase` (corpus V3.4.0 b10) |
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

- The `SymType_*` children a shape model carries are corrected: they are empty 39-byte marker
  GameObjects that declare `SymmetryType`, not meshes at other rotation indices, and
  `getVisualMesh` indexes the `LOD*` parts rather than anything symmetry-derived.
- `BlockShapeNew`'s 32-entry `rotationsToQuats` is written down from its own `cctor`
  (`docs/world/block-shapes.md` 2.1): yaw 0..3, pitch about right 4..11 and 16..19, pitch about
  forward 12..15 and 20..23, the 45-degree yaw band 24..27, and identity 28..31. Three traits are
  named because each fails silently in a consumer: 28..31 are not orientations, the free band has
  no tipped entry, and `rotations[3,28]` is a cache of `CalcRotation` rather than a second source.
- Symmetry is a rotation table, not mirrored geometry: `MirrorStatic` returns a rotation index in
  all five arms, `symType` 0 returns it unchanged, `getVisualMesh` is a plain array index, and
  `Prefab` applies the conversion to a cell's rotation while stamping. A shape whose
  `SymmetryType` is 0 does not mirror at all, so a prefab pairing one shape at two rotations
  across a mirror axis is not a mirrored pair.
- The RWG biome tile counts are pinned from `CalcBiomeTileBiomeData` (IL=162): the five
  `*BiomeWeight` values summed and multiplied by the pass count, one block of five
  `BiomeTypeData` entries per pass with `fraction = weight / total` and `tileCount = totalTiles`,
  each block sorted by fraction ascending, every entry starting at `totalTiles` (the round-robin
  correction after the sum does not run with the caller's arguments).
- The biome neighbour rules are pinned: `HasBiomeNeighbor` (IL=71) is a four-cardinal test, and
  `GetBiomeFromNeighbors` (IL=91) reads left, right, up, down in that order and returns the first
  neighbour that is neither unset (255) nor wasteland (4), else 255. Wasteland is never inherited.
- The region grower's placement is pinned from `FindBiomeEmptyAndSet` (IL=377): a centre jittered
  by -2..2 on each axis, then a square perimeter walk by increasing radius, top row, bottom row,
  left column and right column, and the first unset cell with a same-type cardinal neighbour is
  set.
- `GenerateTerrain` (IL=128) sets `BiomeSize = WorldSize / 8` and takes the border water
  mask from `Rand.Instance.Int() & 15`; the mask gates the terrain-border stamps, a clear bit
  placing a stamp at that edge and `15` skipping the border task.
- The RWG biome seed and growth rules are pinned: the ring layouts put five entries on a
  40 percent ring around a moving centre (forest or wasteland at the centre, `Circle2`'s
  middle entry jittered and pulled in), growth runs quota passes of
  `1 + int(fraction * 4)` steps per entry, then fill passes for every non-forest biome, and
  every remaining tile becomes forest.
- The terrain-type tile assignment is pinned: per biome group, ratio counts with a random
  top-up, hills as even-aligned 2x2 blocks, mountains chaining to a 4-way neighbour with
  probability 0.8, and plains as single cells. The budget arithmetic behind it is pinned too:
  the zero-sum substitution, the weight-gated top-up fall-through, a plains count that is
  never decremented, the unconditional four-hill charge, and the chain's unset-cell test
  along `directions4way`. A hill budget that lands on one leaves its tile at 255, so the map is
  not guaranteed full and a stamp pass skips every window that holds the cell.
- `GenerateTerrainFromTiles` (IL=283) and `GetTerrainProperties` (IL=144) are pinned: the tile
  window must match the type in every cell, mountains are demoted to plains in a wasteland, the
  first stamp of a cluster is centred and the rest are offset additively at 0.45 strength, the
  biome-mask stamp goes to the biome layer, properties fall back from `{biome}_{terrain}` to
  `{terrain}`, scale is halved, and clusters are `count, radius in 256-block units, strength`.
- The RWG stamp pipeline is pinned from a cross-build read (V3.3.0 b18 client, awaiting a V3.4.0
  b10 pass) in `docs/world/rwg-stamps.md`: the headerless 6-byte-per-pixel `.raw` stamp
  (`u16` height / alpha / water, little endian), the per-name alpha box smoothing, the `Stamp` and
  `StampGroup` shapes, the bilinear `CalcRotatedValue` sampler, the height/watershed rasterizers
  (additive vs lerp, the `1e-05` floor, the 0.1 cutoff), `AdjustHeights`'s floor of 2, the binary
  water finalize at 30, and the `(height - 1) * 257` saved `u16` height map.
- `biomeLayout`'s single writer is pinned: the client's new-world screen, so a dedicated server
  generates `CenterForest` and the other four layouts are client choices.
- `generateTerrainFeature` (IL=652) is pinned for lakes and dry features: the plural group's scale
  times 1.4, a random rotation, the shuffled street-tile candidates (wilderness or unclaimed, not
  mountains, feature-free, more than three neighbours), the water feature's lower-layer plus water
  stamp, and the dry feature's reserving stamp. The river path is still unread.
- The terrain tile walk's condition is corrected: the window flag is cleared on the **first** cell of
  the requested type, so one cell fires a tile, and the earlier "every cell must match" reading is
  recorded as wrong with what it costs (a third of a 6144-block map drawn instead of nine tenths).
- `GenerateBaseStamps`'s base elevation is pinned: it writes `35` into every height cell before any
  stamp draws, so the world is a plain at 35 with stamps as deltas and the water level 30 below it.
  The border task's mask gate and 75-block strip are pinned with it; its wet branch is still unread.
- `generateTerrainFeature` is pinned as read in full: there is no river-specific branch (a river is a
  water feature placed like a lake), and two earlier summaries of it are corrected.
- `Stamp::.ctor` is pinned as the writer of `waterRects`: every stamp built with `isWater` appends its
  `Area`, and the only reader is the dry-feature overlap test.
**43 commits after `v3.4.0` (2026-11-05) as of 2026-11-13.** The build retarget this
section described is published under the tag and in
[`release-v3.4.0.md`](release-v3.4.0.md); what follows is post-cut bookkeeping.

- The client water surface shaders are measured
  ([`light-mesh-water.md`](../world/light-mesh-water.md) §4.10): `7DTD/7DTD_Liquid`
  (voxel surface: refraction, specular, and a thickness colour at `_ThicknessWidth`;
  `QUEUE Transparent+1`) and `Game/Water Surface` (plane: `_MainTex` alpha and two
  scrolling wave layers; `QUEUE Transparent-11`), read from
  `shaders_assets_all.bundle` with `unityz extract --class 48`. No Material in the 18
  `Standalone` bundles names either shader, so the instance values are runtime-set and
  stay open as an IL question.

- The tag history row for `v3.4.0`, the corpus pin in this file's header and the
  reset of this section land after the cut, so the release notes stay the record
  of what shipped and this file stays the contract for what comes next.
- `physicsbodies.xml` is documented: the ragdoll layout's record set and the
  226 collider bindings a body's `DT_PhysicsBodies` row carries.
- A sign group's two down-tree effects are written down: the softness and dilate
  offsets add per layer kind with softness clamped at zero, and the colour modes
  multiply, blend or override innermost first, with the no-op case named.
- The warp chain's packing is narrowed: a layer's warps are pushed in reverse file
  order, rotations reach the shader in radians, and shader ids 11 and 12 read the
  record fields `PushWarps` writes, so the open item is the space or the chain
  order rather than a swapped pair. The shipped records then settle the space: over
  6,529 records in the `[-1, 1]` canvas frame, `Skew`, `Twirl`, `Stretch` and
  `Bulge` displace a layer's corner by a fraction of the canvas (medians 0.27,
  0.005, 0.25 and 0.59 units), while `Arc`'s output is a radius and an angle rather
  than a planar position, which is what the earlier reading mistook for a teleport.
- `PerspectiveWarp`'s branch is located and its shape stated: the dispatch is
  `uint(descriptor.x) < 16u` with `== 16` beside it, not an `== 15` comparison, and the
  body is an inlined Euler matrix, a normalise, a divide by a clamped dot and a doubling.
  The exact expression stays unnamed for a register the dump does not name.
- `KaleidoWarp`'s third field is settled: the branch divides the angle by it and folds the
  fraction onto `[0, k/2]`, so on this path the field is a fan half-width in radians rather
  than a sector count.
- The sign noise fill is decoded: its nine-float record, the seed as `offset = seed * 10`, the
  fractal gradient noise with its hash constants and eight-direction table, and the coverage and
  alpha the branch builds from `softness`, `dilate` and `fade`. A shipped prefab thumbnail then
  constrains it: the sign's eleven fills share `seed="0"`, and the closed form at their shipped
  weights would bury lettering the preview shows legible, so the model is decoded and not
  calibrated, and the thumbnail is the frame to calibrate against.
- The eight sign warp transforms are decoded from the shipped client shader,
  and the two branches the first reading got wrong (`Kaleido`'s third field,
  `Perspective`'s closed form) are marked open rather than described, the
  `[-1, 1]` UV frame the chain runs in is stated from `BakeScheduler.TickOnce`,
  and the record-slot mapping the branch bodies still need is named. The canvas
  tile entity's payload is pinned byte by byte, which is the one feature a
  reimplementation cannot keep as an opaque blob, the canvas decal is shown to
  be authored in its prefab rather than measured at run time, and a composite's
  feature payloads are shown to carry their own length, and the name hash a
  reader matches on is pinned with the values it needs, and a writable sign's
  payload is pinned beside the canvas's, and a canvas is measured in a shipped
  POI prefab with its sign library id.

The next cut is `v0.4.0` (tooling) unless the corpus is re-pinned to a new game
build first, which would be `v3.5.0`.

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
