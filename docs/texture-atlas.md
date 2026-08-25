# Texture atlas and minimap colors (V3.1.0 b14)

**Owns:** the block texture atlas metadata that feeds the minimap colors:
where the `uvmapping` XML lives (`MeshDescription.MetaData` TextAssets inside
the `meshdescriptions_assets_all.bundle`), the `UVRectTiling`/`TextureAtlas`
parse path, and the `Chunk.CalcChunkColors` ->
`Block.GetMapColor` -> `Block.GetColorForSide` -> `uvMapping[id].color` ->
`Utils.ToColor5` chain that produces the 256-color map pieces for
`NetPackageMapChunks` ([protocol-packages.md §3.3](protocol-packages.md)).
**Not:** the texture atlas textures themselves (rendering), the client minimap
UI, or the `MapChunkDatabase` storage layout (region-map side, see
[save-region.md](save-region.md)).
**Evidence:** `UVRectTiling` IL, `TextureAtlasBlocks` IL,
`MeshDescription::ReloadTextureArrays` IL, `Chunk::CalcChunkColors` IL,
`Block::GetMapColor` IL, `Block::GetColorForSide` IL, `Utils::ToColor5` IL
(dump locally with `tools/src/DumpMethod`).
**Hub:** [`INDEX.md`](INDEX.md). **Method:** [`re-methodology.md`](re-methodology.md).

## 1. Where the atlas metadata lives

The block texture atlas metadata is **not** in `Data/Config/*.xml`. Each
`MeshDescription` carries a `MetaData` **TextAsset** whose content is an
`<uvmapping>` XML; the TextAssets are packed into the Addressables bundle

```text
Data/Addressables/Standalone/meshdescriptions_assets_all.bundle
```

A UnityFS v8 bundle (engine 2022.3.62f2, big-endian header, LZ4HC storage
blocks; header layout in [texture-atlas-unityfs.md](texture-atlas-unityfs.md)),
containing one CAB serialized file with 40 objects. Six of them are the atlas
TextAssets (`ta_*`); the mesh descriptions and materials reference them.
Extract them with `tools/sandbox/extract_mesh_atlas.py` (UnityPy reference
parser); the extracted XMLs are committed under `tools/sandbox/atlas/` and
regenerate the clone-side comptime minimap-color table via
[`../tools/sandbox/gen_atlas_zig.py`](../tools/sandbox/gen_atlas_zig.py):

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
[protocol-packages.md §3.3](protocol-packages.md)).

## Related docs

| Doc | Role |
|---|---|
| [protocol-packages.md](protocol-packages.md) | §3.3 MapChunks wire + window |
| [save-region.md](save-region.md) | MapChunkDatabaseByRegion storage |
| [blocks.md](blocks.md) | block texture properties, GetColorForSide consumers |
| [full-surface.md](full-surface.md) | whole-assembly map |

## Changelog

- **2026-08-21:** Initial reversal: atlas TextAssets located in
  `meshdescriptions_assets_all.bundle` (UnityFS v8), uvmapping XML format,
  `TextureAtlasBlocks.LoadTextureAtlasFromMetadata` / `UVRectTiling.FromXML`
  parse, the CalcChunkColors -> GetMapColor -> GetColorForSide -> ToColor5
  minimap chain, and the block `Texture` id -> terrain atlas link (no block
  sets MeshIndex; mesh 0 = ta_terrainxml).
