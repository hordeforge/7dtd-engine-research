# Block stability, structural support and falling blocks

Status: **derived 2026-08-06** from the V3.1.0 b14 disassembly (dedi-complete
dump). Raw IL in [`docs/stability-dump/`](stability-dump/). This is the server
side of the stability model zdtd must match so that unsupported structures
collapse the same way on the authoritative plane and on the stock client.

Related: [world-chunks.md](world-chunks.md) (Stability runs on clients too,
falling-block pump runs off the IsServer guard), [save-region.md](save-region.md)
(`chnStability` optional channel in the chunk file).

## Why the server needs this

`ChunkStabilityEnabled` is a non-persistent GameStats bool defaulting true
(asm.il 1919743), so every stock client runs its own `StabilityCalculator` plus
`StabilityInitializer` (`ChunkCluster::Init` 1125631-1125637) and recomputes the
whole plane locally (`ChunkCluster::CalcStability` 1127044, inside
`LightChunk`). `bNetwork=true` skips the stability channel on the wire, which is
only sound because the client rebuilds it. If the server never models stability,
removing a support makes the client collapse blocks the server still reports as
standing: a desync the client treats as authoritative. The server must run the
same plane math, then convert the same positions to falling blocks.

## The model

The plane is a per-block byte (`Chunk.chnStability`, 0..15). `15` is full
support. `0` is unsupported: the only value that makes a block fall. Non-support
blocks are capped at `1` wherever they sit. A block falls when its byte is `0`
after a support removal and the re-spread cannot lift it back.

### Seed (Chunk::ResetStability, ResetStabilityToBottomMost)

On chunk creation every non-air, non-liquid, non-`StabilityIgnore` block is set
to `15` when `Block.StabilitySupport` is true, else `1`. Note this makes even a
floating structure fully stable until a support change runs: stability is
derived on change, not baked at gen.

### Spread (StabilityInitializer)

`DistributeStability(chunk)` scans y 0..maxHeight per column and calls
`spreadHorizontal(x,y,z,stab)` for every block whose current stability is > 1.
`set_StopStabilityCalculation(false)` at the end marks the chunk done.

`spreadHorizontal(x,y,z,stab)`:
- return if `stab <= 1`; else `stab -= 1`.
- for each of the 4 HORIZONTAL_DIRECTIONS:
  - nbr = (x+dx, y, z+dz); resolve neighbor chunk when crossing the border
    (world coords via `GetBlockWorldPosX/Z`).
  - skip air / `blockMaterial.IsLiquid` / `StabilityIgnore`.
  - `v = stab`; if `v > 1` and the neighbor block is not `StabilitySupport`,
    `v = 1`.
  - if `v > chunk.GetStability(nbr)`: `SetStability(nbr, v)`; and if the
    neighbor is `StabilitySupport`, recurse `spreadHorizontal(nbr, v)` and
    `spreadVertical(nbr, v)`.

`spreadVertical(x,y,z,stab)` has two phases:
- upward from y+1 to 255 with the same `stab` value (`v = min(stab,15)`, capped
  to 1 on non-support blocks); set + recurse horizontally when `StabilitySupport`.
- downward from y-1 with `stab-1` decrementing each step (`v = min(v,15)`, cap 1
  on non-support); same set + recurse.

So: horizontal support decays 1 per block step; vertical support keeps its value
going up and decays 1 per block going down; anything without `StabilitySupport`
never carries more than 1.

### Removal (StabilityCalculator::BlockRemovedAt -> ChannelCalculator)

`StabilityCalculator::BlockRemovedAt(pos)` (126 IL) skips y >= 255, clears
`stab0Positions`, delegates to `ChannelCalculator::BlockRemovedAt(pos, out)` and,
when not remote, walks all 6 neighbors, zeroing the stability of neighbors that
fail `IsBlockSupportedByNeighbor` and collecting them into `stab0Positions`
(positions whose byte goes to 0).

`ChannelCalculator::BlockRemovedAt` (81 IL) skips air/liquid/`StabilityIgnore`,
then runs `CalcChangedPositionsFromRemove(pos, list2, stab0, null)`:

`CalcChangedPositionsFromRemove` is a BFS from the removed position over all 6
directions. For each reached non-air, non-liquid, non-`StabilityIgnore` block it
computes the new stability via `ChangeStability`:
- `v = getMaxStabilityAround(pos, out bFromDownwards)`; when not from a
  downwards neighbor, `v -= 1`; cap `v` at 1 for non-`StabilitySupport` blocks.
- if `v` differs from the current byte, set it.
- when the new value is 0, add the position to `stab0Positions` (it will fall).
- blocks whose computed value is below their old value propagate the BFS; equal
  or higher stops that branch.

`StabilityInitializer::BlockRemovedAt(worldX, worldY, worldZ)` (106 IL) is the
plane recompute path: set the removed cell's byte to 0, then `unspreadHorizontal`
(clear the affected region via `clearHorizontal`/`clearDown` with a stop value,
then re-spread from the remaining supported anchors).

### Placement (StabilityCalculator::BlockPlacedAt / ChannelCalculator::BlockPlacedAt)

`ChannelCalculator::BlockPlacedAt(pos, isForceFullStab)` (154 IL) with
`getMaxStabilityAround(pos, out bFromDownwards)`: the new block's stability is
`maxStabilityAround - 1` (or `maxStabilityAround` when the max comes from below),
capped 1 for non-support blocks, then propagated (`BlockPlacedAt` also has a
force-full path used by MultiBlockManager).

### The fall trigger (StabilityCalculator/UpdatePhysics + physicsIsolation)

`UpdatePhysics::MoveNext` (126 IL) is a coroutine on `updatePeriod`: while
`queueStabilityEmpty` is non-empty it dequeues a position, runs
`physicsIsolation(pos)`, and for every position in `hashSetIsolation` calls
`World::AddFallingBlock(pos, false)`.

`physicsIsolation(pos)` (125 IL) is a 6-direction flood: skip air, liquid,
`StabilityIgnore` and already-processed cells; a non-child cell whose chunk
stability byte is `0` is added to `hashSetIsolation` (capped at 1000 positions),
and every reached cell is enqueued for the flood regardless of its byte. The
flood runs through the whole connected non-air region, so removing one support
collects every now-unsupported block of the structure.

### Falling blocks (World::AddFallingBlock / LetBlocksFall)

`World::AddFallingBlock(pos, includeOversized)` (38 IL): skip if already queued,
or the block is air / child / `StabilityIgnore`, or oversized without
`includeOversized`; otherwise enqueue into `World.fallingBlocks` and add to
`fallingBlockSet` (dedupe), plus `DynamicMeshManager::AddFallingBlockObserver`.

`World::LetBlocksFall` (220 IL, run from `GameManager::UpdateTick` outside the
IsServer guard, so clients run it too): when `EntityFallingBlocks::Enabled` is
set it first groups via `GroupFallingBlocks` (up to 2 groups per pump), then
dequeues individual positions, skipping processed/grouped ones, reads the block
value, the texture array and any tile entity, and spawns the falling-block
entity (`EntityFallingBlocks` for groups, `EntityFallingBlock` for singles) via
`EntityFactory::CreateEntity(EntityClass::FromString("fallingBlock"))`.

## The stability viewer BFS (GetBlockStability)

`GetBlockStability(pos, newBV)` (293 IL) is the debug/UI measure (StabilityViewer
F9 overlay) and the `GetBlockStabilityIfPlaced` preview; it is not the fall
decision. It runs a 25-iteration BFS from the position over
`Vector3i.AllDirectionsShuffled`:

- `mass` = sum of `blockMaterial.Mass` of every reached block.
- `downTotal` = sum of `GetForceToOtherBlock` over reached blocks' neighbors
  with stability > 0; `GetForceToOtherBlock(other)` =
  `FastMin(StabilityGlue(block), StabilityGlue(other))` (10 IL). A neighbor
  directly below with stability >= 1 sets `downTotal = 100000` (direct support
  dominates; masses are small, so the structure is stable).
- result `1 - mass / (downTotal * 1.01)` when `downTotal > 0`, `1` when no
  support was reached, `0` when `mass > downTotal`.

## Remaining detail to pin down before implementing

- `ChannelCalculator::getMaxStabilityAround` (61 IL) exact 6-neighbor ordering
  and the `bFromDownwards` rule.
- `StabilityInitializer::unspreadHorizontal` / `clearHorizontal` / `clearDown`
  exact stop conditions and the re-spread entry points.
- `EntityFallingBlock::OnUpdateEntity` / `OnContactEvent` landing: which position
  it re-places into, damage applied on impact, and the block removal timing
  (44 methods dumped, not yet translated).
- `Block.StabilitySupport`, `Block.StabilityIgnore`,
  `MaterialBlock.StabilityGlue` and `MaterialBlock.Mass` data sources in
  blocks.xml (properties on `<block>` and `<material>`), to be loaded into the
  block/material tables.

## Chunk file note

`Chunk.write` writes the optional `chnStability` channel (save-region.md) but the
wire skips it (`bNetwork=true`). zdtd's ZCH3 chunk format has no stability
channel today; the plane can be recomputed on load with
`ResetStability` + `DistributeStability` semantics instead of persisting it.

## Changelog

- 2026-08-06: derived plane seed/spread/removal/fall paths from
  `StabilityCalculator`, `StabilityInitializer`, `ChannelCalculator`,
  `World::AddFallingBlock/LetBlocksFall` and `EntityFallingBlock(s)`; dumps in
  `docs/stability-dump/`.
