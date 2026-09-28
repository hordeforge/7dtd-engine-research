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

import os
import re
import sys


def parse_shapes(path: str) -> tuple[list[str], set[str]]:
    """Return (all_names_in_order, bulletproof_set)."""
    with open(path, encoding="utf-8-sig") as f:
        xml = f.read()
    all_names: list[str] = []
    bulletproof: set[str] = set()
    for m in re.finditer(r"<shape\s+name=\"([^\"]+)\"([^>]*)/?>", xml):
        name, attrs = m.group(1), m.group(2)
        all_names.append(name)
        if re.search(r'tag="Bulletproof"', attrs):
            bulletproof.add(name)
    return all_names, bulletproof


def parse_blocks(xml: str, shapes: list[str], bulletproof: set[str]) -> list[str]:
    """Return the emitted block names in document order (shape groups expanded).

    Takes the document text, not a path: the caller already holds it for
    `terrain_by_name`, and this file is megabytes that a second read and a
    second full scan would duplicate for nothing.
    """
    out: list[str] = []
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


SHAPE_PROP_RE = re.compile(r'<property\s+name="Shape"\s+value="([^"]+)"')
# Every quoted value in document order, with nothing skipped between them.
# Scanning these is what makes the index complete: a block's element is reached
# from whichever of its quoted values comes first, so a name that first appears
# as a drop name or an Extends value is indexed where it actually appears.
QUOTED_VALUE_RE = re.compile(r'"([^"]+)"')


def terrain_by_name(xml: str) -> dict[str, bool]:
    """Map every quoted name in blocks.xml to whether its element is Shape=Terrain.

    One pass over the file, indexing terrain-ness by name. Searching per block
    name instead costs a full rescan of the multi-megabyte document for each of
    the ~6,600 distinct blocks: 48 s on a stock 3.6 MB blocks.xml against 0.1 s
    here, and the ids it produces are the same.
    """
    out: dict[str, bool] = {}
    for m in QUOTED_VALUE_RE.finditer(xml):
        name = m.group(1)
        # A name repeated later in the document keeps its first element, which
        # is the one a per-name search would have found.
        if name in out:
            continue
        # The element this value sits in runs to the tag's closing `>` and then
        # to the next `</block>`. A self-closing `<block ... />` (a block with
        # no properties) has no body at all, and a body matched to the next
        # `</block>` would hand it the following block's Shape, putting a Cube
        # block into the terrain band.
        tag_end = xml.find(">", m.end())
        if tag_end < 0:
            continue
        if xml[m.end() : tag_end].rstrip().endswith("/"):
            out[name] = False
            continue
        body_end = xml.find("</block>", tag_end)
        body = "" if body_end < 0 else xml[tag_end:body_end]
        pm = SHAPE_PROP_RE.search(body)
        out[name] = pm is not None and pm.group(1) == "Terrain"
    return out


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print((__doc__ or "").strip())
        raise SystemExit(0)
    if len(sys.argv) != 3:
        # Usage is an error here, so it goes to stderr with exit 2; `--help`
        # above is the only path that writes the docstring to stdout.
        print((__doc__ or "").strip(), file=sys.stderr)
        raise SystemExit(2)
    cfg_dir, out_path = sys.argv[1], sys.argv[2]
    for name in ("blocks.xml", "shapes.xml"):
        if not os.path.isfile(os.path.join(cfg_dir, name)):
            print(
                f"assignids_dump: not a stock Data/Config dir: {cfg_dir} (no {name})",
                file=sys.stderr,
            )
            raise SystemExit(2)
    shapes, bulletproof = parse_shapes(f"{cfg_dir}/shapes.xml")
    with open(f"{cfg_dir}/blocks.xml", encoding="utf-8-sig") as f:
        blocks_xml = f.read()
    names = parse_blocks(blocks_xml, shapes, bulletproof)

    fixed = {"air": 0, "water": 240, "terrWaterPOI": 241, "waterdata": 242}
    used = set(fixed.values())
    # Terrain-ness is a property of the block element, so it is indexed in one
    # pass rather than searched for once per name. A `name:shape` variant
    # carries no element, and every shape variant is non-terrain.
    terrain_by_block = terrain_by_name(blocks_xml)

    def is_terrain(n: str) -> bool:
        return n in terrain_by_block and terrain_by_block[n]

    terr_next = 0
    gen_next = 255
    rows: dict[int, str] = {}
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
        f.write(
            "# Source: stock id-assignment pipeline (Block IL), tool: 7dtd-engine-research/tools.\n"
        )
        for i in sorted(rows):
            f.write(f"{i}\t{rows[i]}\n")
    print(f"wrote {len(rows)} entries to {out_path}")


if __name__ == "__main__":
    main()
