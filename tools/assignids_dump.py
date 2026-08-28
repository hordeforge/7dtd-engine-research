#!/usr/bin/env python3
"""Regenerate the zdtd AssignIds dump from a stock install's blocks.xml +
shapes.xml by replicating the stock id-assignment pipeline (Block.IL):

1. Expand each `<block shapes="All">` group with every shapes.xml shape name
   and each `shapes="Bulletproof">` group with the tag="Bulletproof" subset,
   interleaved at the group's document position (the group block itself gets
   no id, matching the stock client's id table).
2. fixedBlockIds (Block.cctor): air=0, water=240, terrWaterPOI=241,
   waterdata=242.
3. assignLeftOverBlocks in document order: terrain blocks (Shape=Terrain,
   BlockShapeTerrain::IsTerrain=true) take the next free id scanning up from
   0; every other block takes the next free id scanning up from 255.
4. Emit "id<TAB>name" lines sorted by id.

Usage: assignids_dump.py <Data/Config dir> <out.txt>
Ground truth: the 3.1.0 client capture (2026-07-22, ZDTD_DUMP_BLOCK_IDS)
matches this pipeline; the 3.2.0 regeneration keeps the pins the client
capture had (air 0, terrStone 1, treeDeadTree02, cntWoodenChestClosed,
treeOakSml01) unless a 3.2.0 blocks.xml edit shifted them.
"""

import re
import sys


def parse_shapes(path):
    """Return (all_names_in_order, bulletproof_set)."""
    with open(path, encoding="utf-8-sig") as f:
        xml = f.read()
    all_names = []
    bulletproof = set()
    for m in re.finditer(r"<shape\s+name=\"([^\"]+)\"([^>]*)/?>", xml):
        name, attrs = m.group(1), m.group(2)
        all_names.append(name)
        if re.search(r'tag="Bulletproof"', attrs):
            bulletproof.add(name)
    return all_names, bulletproof


def parse_blocks(path, shapes, bulletproof):
    """Return the emitted block names in document order (shape groups expanded)."""
    with open(path, encoding="utf-8-sig") as f:
        xml = f.read()
    out = []
    for m in re.finditer(r"<block\s+name=\"([^\"]+)\"([^>]*)/?>", xml):
        name, attrs = m.group(1), m.group(2)
        sm = re.search(r'shapes="([^"]+)"', attrs)
        if sm:
            group = sm.group(1)
            if group == "All":
                out.extend(f"{name}:{s}" for s in shapes)
            elif group == "Bulletproof":
                out.extend(f"{name}:{s}" for s in shapes if s in bulletproof)
            else:
                raise SystemExit(f"unknown shapes group {group!r} for {name}")
        else:
            out.append(name)
    return out


def terrain_shape(block_name, xml):
    """True when the block's Shape property resolves to BlockShapeTerrain."""
    # Find the block element and read its Shape property value.
    m = re.search(
        re.escape(block_name) + r'"([^>]*)>(.*?)</block>', xml, re.S)
    if not m:
        return False
    body = m.group(2)
    pm = re.search(r'<property\s+name="Shape"\s+value="([^"]+)"', body)
    return pm is not None and pm.group(1) == "Terrain"


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    cfg_dir, out_path = sys.argv[1], sys.argv[2]
    shapes, bulletproof = parse_shapes(f"{cfg_dir}/shapes.xml")
    with open(f"{cfg_dir}/blocks.xml", encoding="utf-8-sig") as f:
        blocks_xml = f.read()
    names = parse_blocks(f"{cfg_dir}/blocks.xml", shapes, bulletproof)

    fixed = {"air": 0, "water": 240, "terrWaterPOI": 241, "waterdata": 242}
    used = set(fixed.values())
    # Pre-scan terrain-ness once per unique name (shape variants are non-terrain).
    terrain_cache = {}
    def is_terrain(n):
        if n in terrain_cache:
            return terrain_cache[n]
        v = terrain_shape(n, blocks_xml)
        terrain_cache[n] = v
        return v

    terr_next = 0
    gen_next = 255
    rows = {}
    for n in names:
        if n in fixed:
            rows[fixed[n]] = n
            continue
        if is_terrain(n):
            while terr_next in used:
                terr_next += 1
            rows[terr_next] = n
            used.add(terr_next)
            terr_next += 1
        else:
            while gen_next in used:
                gen_next += 1
            rows[gen_next] = n
            used.add(gen_next)
            gen_next += 1

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# V3.2.0 AssignIds id\tname: regenerated from blocks.xml + shapes.xml\n")
        f.write("# Pins: air=0 terrStone=1 (Block.fixedBlockIds + assignLeftOverBlocks).\n")
        f.write("# Source: stock id-assignment pipeline (Block IL), tool: 7dtd-engine-research/tools.\n")
        for i in sorted(rows):
            f.write(f"{i}\t{rows[i]}\n")
    print(f"wrote {len(rows)} entries to {out_path}")


if __name__ == "__main__":
    main()
