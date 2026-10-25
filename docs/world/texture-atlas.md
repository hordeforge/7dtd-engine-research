# Texture atlas and minimap colors (V3.2.0 b9 data pin; container re-checked on V3.3.0 b18)

**Owns:** the block texture atlas metadata that feeds the minimap colors:
where the `uvmapping` XML lives (`MeshDescription.MetaData` TextAssets inside
the `meshdescriptions_assets_all.bundle`), the `UVRectTiling`/`TextureAtlas`
parse path, and the `Chunk.CalcChunkColors` ->
`Block.GetMapColor` -> `Block.GetColorForSide` -> `uvMapping[id].color` ->
`Utils.ToColor5` chain that produces the 256-color map pieces for
`NetPackageMapChunks` ([protocol-packages.md §3.3](../network/protocol-packages.md)).
**Not:** the texture atlas textures themselves (rendering), the client minimap
UI, or the `MapChunkDatabase` storage layout (region-map side, see
[save-region.md](../world/save-region.md)).
**Evidence:** `UVRectTiling` IL, `TextureAtlasBlocks` IL,
`MeshDescription::ReloadTextureArrays` IL, `Chunk::CalcChunkColors` IL,
`Block::GetMapColor` IL, `Block::GetColorForSide` IL, `Utils::ToColor5` IL
(dump locally with `tools/src/DumpMethod`).
**Hub:** [`INDEX.md`](../INDEX.md). **Method:** [`re-methodology.md`](../meta/re-methodology.md).

## 1. Where the atlas metadata lives

The block texture atlas metadata is **not** in `Data/Config/*.xml`. Each
`MeshDescription` carries a `MetaData` **TextAsset** whose content is an
`<uvmapping>` XML; the TextAssets are packed into the Addressables bundle

```text
Data/Addressables/Standalone/meshdescriptions_assets_all.bundle
```

A UnityFS v8 bundle (engine 2022.3.62f2, big-endian header, LZ4HC storage
blocks; header layout in [texture-atlas-unityfs.md](../world/texture-atlas-unityfs.md)),
containing one CAB serialized file with 40 objects. Six of them are the atlas
TextAssets (`ta_*`); the mesh descriptions and materials reference them.
Extract them with `tools/sandbox/extract_mesh_atlas.py` (UnityPy reference
parser); the extracted XMLs are committed under `tools/sandbox/atlas/` and
regenerate the clone-side comptime minimap-color table via
[`../../tools/sandbox/gen_atlas_zig.py`](../../tools/sandbox/gen_atlas_zig.py):

| TextAsset | uv entries | Role |
|---|---|---|
| `ta_terrainxml` | 20 | terrain splat textures (mesh 0; blocks.xml `Texture` ids map here) |
| `ta_opaquexml` | 160 | opaque block textures |
| `ta_grassxml` | 29 | grass/plant textures |
| `ta_transparentxml` | 5 | transparent block textures |
| `ta_decalsxml` | 16 | decal textures |
| `ta_waterxml` | 1 | water |

## 2. The uvmapping XML

`TextureAtlasBlocks.LoadTextureAtlasFromMetadata` (IL=80) parses the root
element's `<uv>` children into `TextureAtlas.uvMapping[id]`; each entry is
built by `UVRectTiling::FromXML` (IL=152) which reads the attributes
`texture` (tga file name), `color` ("r,g,b" floats, parsed with
`StringParsers.ParseFloat` into a `Color`), `index`, plus the UV rect
`x/y/w/h`, `blockw/blockh`, `globaluv`, `material`:

```xml
<uvmapping>
  <uv id="1" x="34" y="34" w="247" h="247" blockw="8" blockh="8"
      color="0.2862745,0.282353,0.2862745" globaluv="True" index="0"
      material="stone" texture="stone.tga" />
  ...
</uvmapping>
```

`id` is the **texture id** that block textures reference: blocks.xml `Texture`
property values (e.g. `terrDirt` -> `2`, `terrForestGround` -> `195,570,...`)
are indices into this table. No block in stock blocks.xml sets `MeshIndex`, so
every block resolves its atlas through the terrain mesh (index 0) whose
metadata is `ta_terrainxml`; the other atlases are used by prefab/entity
materials. `color` is the per-texture **map color** (an author-picked tint,
not a texture average).

## 3. Minimap color chain

`Chunk::CalcChunkColors` (IL=231) fills `Chunk.mapColors[256]`:

1. For each of the 16x16 cells (one per block): walk the column from the top
   (`m_BlockLayers[?].GetAt(bx, y, bz)`); the first non-air /
   non-`IsTerrainDecoration` block wins. If the cell's `WaterValue.HasMass()`
   (and nothing solid above), the color is `BlockLiquidv2.Color`.
2. Otherwise `Block.GetMapColor(blockValue, normal, yPos)` (IL=112):
   - if `Block.bMapColorSet` (blocks.xml `MapColor` property): `Block.MapColor`
     + `MapSpecular`;
   - else: if the face normal points up (x,z within +/- 0.5): `GetColorForSide(
     blockValue, BlockFace.Top=0)`; else `GetColorForSide(..., 4)`; then the
     specular adjustment tail.
3. `GetColorForSide` (IL=30): `uvMapping[GetSideTextureId(blockValue, side,
   0)].color` from the block's mesh atlas (terrain atlas for blocks), gray
   when the texture id is out of range.
4. `Utils.ToColor5` (IL=29) packs `(r*31+0.5)<<10 | (g*31+0.5)<<5 |
   (b*31+0.5)` into a u16 (RGB555).

The 256 u16 colors per chunk are what `MapChunkDatabase` stores and
`NetPackageMapChunks` ships (17x17 window, 256 colors per piece;
[protocol-packages.md §3.3](../network/protocol-packages.md)).

## 4. The atlas images

The metadata above is only half of the block atlas. The images live in a second
bundle, and they are not one texture:

`Data/Addressables/Standalone/blocktextureatlases_assets_all.bundle` holds nine
`Texture2DArray` objects (class 187), all **407 layers** deep, in three
resolutions and three roles:

| Objects | Resolution | Role |
|---|---|---|
| `ta_opaque_0`, `ta_opaque_n_0`, `ta_opaque_s_0` | 512x512 | diffuse, normal, specular |
| `ta_opaque_1`, `ta_opaque_n_1`, `ta_opaque_s_1` | 256x256 | the same three, half size |
| `ta_opaque_2`, `ta_opaque_n_2`, `ta_opaque_s_2` | 128x128 | the same three, quarter size |

**Verified** on the b18 install: object table from the bundle's `index.json`,
layer counts and pixel sizes from the exports produced by `unityz` (sibling
`hordeforge/unityz`, class-187 support since 0.1.11). The serialized `m_Format`
is a `GraphicsFormat`, not the `TextureFormat` a `Texture2D` carries.

The other five `ta_*` families are **not** arrays. Their images are single
`Texture2D` objects (class 28): `ta_grass`, `ta_transparent`, `ta_decals`,
`ta_water`, `ta_cracks` and `ta_ingredients01`, each with `_n` and `_s` or
`_Packed_*` companions. No object named `ta_terrain` exists anywhere in the
extraction, so the image the eighteen `ta_terrainxml` entries address is still
unidentified; the terrain splat textures in
`terraintextures_assets_all.bundle` (`terrain_filler`, `sidewalk_terrain`) are
not an atlas of that shape.

### The opaque tile space (inferred)

The opaque `uv` entries carry `index` alongside `id`, and `index` is not a
second name for `id`. Sorted by `index`, the 160 opaque entries cover `0..406`
in `w*h` strides (82 entries are 2x2, 78 are 1x1), and the last entry
(`id` 607, `metal_roof.tga`) starts at 403 and ends at **407**, which is exactly
the layer count of every `ta_opaque_*` array. So `index` reads as a packing
cursor into a 407-slot space where each texture owns `w*h` consecutive slots.

Grade: **inferred**. The arithmetic is consistent across all 160 entries and
lands on the array depth, but the sampling path is not decoded: which slot a
face of a 2xN texture reads, and how `globaluv` and `blockw/blockh` turn a UV
into that offset, are open. A shader or mesh-path reading
(`MeshDescription.ReloadTextureArrays` is the named next target) would settle it.

The other families do not share this shape: `ta_terrainxml` gives pixel rects
(239, 247, 495) with `blockw/blockh` of 4 or 8, `ta_grassxml`,
`ta_transparentxml` and `ta_decalsxml` give normalised sizes (0.125, 0.25) with
`index` 0 on every entry, and `ta_waterxml` has no `w` or `h` at all. The rect
attributes should be read per file, not with one shared interpretation.

## Related docs

| Doc | Role |
|---|---|
| [protocol-packages.md](../network/protocol-packages.md) | §3.3 MapChunks wire + window |
| [save-region.md](../world/save-region.md) | MapChunkDatabaseByRegion storage |
| [blocks.md](../world/blocks.md) | block texture properties, GetColorForSide consumers |
| [full-surface.md](../meta/full-surface.md) | whole-assembly map |

## Changelog

- **2026-10-25:** Added §4 on the atlas **images**: the nine `ta_opaque_*`
  `Texture2DArray` objects (512, 256, 128 px, 407 layers each, measured with
  `unityz` on b18), the five families that are single `Texture2D` atlases
  instead, the absent `ta_terrain` image, and the **inferred** opaque tile space
  (`index` as a packing cursor over 407 slots, `w*h` per entry, the last entry
  ending exactly at the array depth). The per-file rect shapes are recorded with
  it: the six XMLs do not share units.
- **2026-10-24:** Container and parse path re-checked on V3.3.0 (b18): the bundle
  path exists, its UnityFS header and file/block tables match
  [texture-atlas-unityfs.md](../world/texture-atlas-unityfs.md), and every type and
  method in the parse chain (`TextureAtlasBlocks`,
  `MeshDescription.ReloadTextureArrays`, `Chunk.CalcChunkColors`,
  `Block.GetMapColor`, `Block.GetColorForSide`, `Utils.ToColor5`) is absent from
  the b10 -> b18 delta report, so the chain is unchanged. The six `ta_*` XMLs were
  **not** re-extracted on b18, so the atlas entry counts and per-texture colors
  stay pinned to the b9 extraction in `tools/sandbox/atlas/`.
- **2026-08-21:** Initial reversal: atlas TextAssets located in
  `meshdescriptions_assets_all.bundle` (UnityFS v8), uvmapping XML format,
  `TextureAtlasBlocks.LoadTextureAtlasFromMetadata` / `UVRectTiling.FromXML`
  parse, the CalcChunkColors -> GetMapColor -> GetColorForSide -> ToColor5
  minimap chain, and the block `Texture` id -> terrain atlas link (no block
  sets MeshIndex; mesh 0 = ta_terrainxml).
