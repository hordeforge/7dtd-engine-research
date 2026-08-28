# assignids_dump.py — regenerate the zdtd AssignIds dump from a stock install

Replicates the stock block-id assignment pipeline (`Block` IL, V3.2.0 dumps):

1. `<block shapes="All">` expands to every `shapes.xml` shape name in
   document order; `shapes="Bulletproof">` expands to the `tag="Bulletproof"`
   subset. The group block itself gets no id (matches the client table).
2. `fixedBlockIds` (Block.cctor): air=0, water=240, terrWaterPOI=241,
   waterdata=242.
3. `assignLeftOverBlocks` in document order: terrain blocks (`Shape=Terrain`,
   `BlockShapeTerrain::IsTerrain`) take the next free id scanning up from 0;
   every other block takes the next free id scanning up from 255.

## Validation status

The regeneration reproduces the fixed pins exactly (air=0, terrStone=1,
water=240, terrWaterPOI=241, waterdata=242) and keeps the 3.1.0 terrain
relative order, and the 3.1.0-vs-3.2.0 deltas are explained by 3.2.0 edits
(VariantHelper shape removals, terrain removals, insertions). Exactness is
**not yet proven end to end**: the 3.1.0 inputs are gone, so the pipeline
cannot be re-run against the 3.1.0 ground-truth capture. Validate against a
live V3.2.0 client capture (the ZDTD_DUMP_BLOCK_IDS postfix) before trusting
the output byte-for-byte, or re-run against a retained 3.1.0
blocks.xml/shapes.xml pair.

## Usage

```bash
python3 tools/assignids_dump.py \
  "<steam>/7 Days to Die Dedicated Server/Data/Config" assignids_v320.txt
```

The output feeds zdtd's `src/assets/assignids_v314.embed.txt` + the
`assets/fixtures/assignids_v314.txt` fixture (which must stay in sync) and
removes the maxdamage stale-dump allowance once validated.
