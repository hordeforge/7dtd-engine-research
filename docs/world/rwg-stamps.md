# RWG stamps: the file format and the rasterizers

The RWG stamp pipeline is the step between the tile maps and the height field: `world-generation.md`
3.2 says which stamp a terrain tile gets, and 3.4 says when each layer is rasterized. This doc is the
other half: the stamp file format, the pixel loop, and what the destination values become. It is what
a reimplementation has to reproduce bit for bit, so the arithmetic is written out rather than
described.

**Provenance, read this first.** Every IL claim below was read from the only 7DTD assembly on the
authoring host, the **V3.3.0 b18 client** `Assembly-CSharp.dll` in
`7DaysToDie_Data/Managed/`. The studied pin is **V3.4.0 b10**, which was not available, so treat
each claim as a cross-build read: the shape and arithmetic are what a later `V3.4.0 b10` pass
confirms, and the corpus's own `GenerateTerrainTiles` pin (IL=385, §3.2 of `world-generation.md`)
matches this client body instruction for instruction, which is why the read is worth publishing
rather than discarding. `GenerateTerrainFromTiles` (IL=283) and `GetTerrainProperties` (IL=144)
pinned in `world-generation.md` 3.2 agree with the bodies here line for line.

**Hub:** [`INDEX.md`](../INDEX.md). **Method:** [`re-methodology.md`](../meta/re-methodology.md).

## 1. Verified by instruction

### 1.1 Where stamp files are searched

`PathAbstractions..cctor` builds `RwgStampsSearchPaths` as a three-root
`SearchDefinition` (IL body, V3.3.0 b18):

- user data `LocalStamps`
- mods `Stamps`
- game `Data/Stamps` (read from `gameDataPath`)

The file-name regex is the empty string (every file is a candidate).
`StampManager/<LoadStamps>d__22::MoveNext` (IL=161) then walks the resulting
`AbstractedLocation` list **twice**:

- pass 1 calls `LoadStamp` only for `.raw` and `.exr` (this is the expensive
  pass; it yields every 500 ms),
- pass 2 calls `LoadStamp` for every path, which is how `.png` stamps get in.

`LoadStamp` itself rejects `.exr` (1.3), so an EXR stamp is never loaded in this
build. Shipped set in the local install (`Data/Stamps`, 26 files): `.raw` stamps
of 1,572,864 bytes (512x512) plus `ground_01.raw` at 6,291,456 bytes
(1024x1024); `.png` stamps `filler_biome_01`, `river_01/02`,
`rwg_tile_cap/corner/intersection/straight/t`.

### 1.2 The `.raw` stamp format

`Utils::LoadRawStampFileArray(String)` (IL=127) is the loader for `.raw`
(`StampManager::LoadStamp` IL=334 calls it at IL_0036). The file has **no
header**: it is read whole into a byte array and cut into **6-byte pixels**,
little-endian, in this order

| bytes | channel | meaning |
|---|---|---|
| 0..1 | `R` | height, `u16 / 65535` |
| 2..3 | `A` | alpha, `u16 / 65535` |
| 4..5 | `B` | water, `u16 / 65535` |

Green is left at 0 (`Color.black` then `r`, `a`, `b` assigned). Pixel count is
`length / 6` (integer division, a trailing partial pixel is dropped); the array
index is the read order, and `LoadStamp` sets
`width = height = (int)Mathf.Sqrt(pixelCount)`, so a stamp is assumed square.

The sibling `Utils::LoadRawStampFile` (IL=91) returns a `Texture2D` with
`TextureFormat 20` (`RGBAFloat`) and `Color(r, r, b, a)`; it has **zero call
sites** in V3.3.0 b18.

### 1.3 `LoadStamp`: file to `RawStamp.Data`

`StampManager::LoadStamp(AbstractedLocation)` (IL=334). Key is
`FileNameNoExtension`; an existing key returns immediately. Branches on
`Extension`:

- `.raw` -> `Utils.LoadRawStampFileArray(fullPath)`
- `.exr` -> **`ret` at IL_0050, nothing is loaded**
- anything else -> `TextureUtils.LoadTexture(path, FilterMode 0, false, false,
  null)` then `texture.GetPixels()` (this is the `.png` path)

Then three channels are turned into a possibly-constant array each. The pattern
is the same for red and alpha: take `color[0]` as a candidate constant, scan from
index 1, and if any element differs allocate a `NativeArray<float>` of
`colors.Length` (`Allocator` 4 = `Persistent`, `NativeArrayOptions` 0 =
`UninitializedMemory`) and fill it; otherwise leave the array uncreated and keep
the first value in the scalar.

| field | source | per-pixel value |
|---|---|---|
| `heightConst` | `colors[0].r` | `r * 255` |
| `heightPixels[i]` | `colors[i].r` | `r * 255` |
| `alphaConst` | `colors[0].a` | `a` (no scale) |
| `alphaPixels[i]` | `colors[i].a` | `a` (no scale) |
| `waterPixels[i]` | `colors[i].b` | `b * 255` |

Water is special: it is allocated when **any** pixel has `b != 0`, and it is
skipped entirely when the stamp name `Contains("rwg_tile")`. Alpha and height are
0..1 and 0..255 respectively, water is 0..255 like height. `width` and `height`
are both `(int)Mathf.Sqrt(colors.Length)`.

Consequence for the shipped data: the mountain/plains/hills stamps carry a
constant red (65535, so `heightConst` 255) and put their shape in alpha; a lake
stamp carries red 0, a shaped alpha and a shaped blue; `canyon_01` carries red 0
and alpha only (`heightConst` 0, a lowering stamp).

### 1.4 Alpha smoothing (`RawStamp::SmoothAlpha`)

`RawStamp::SmoothAlpha(Data&, int boxSize)` (IL=4) is a Burst direct call into
`SmoothAlpha$BurstManaged` (IL=106). `LoadStamp` calls it only when
`alphaPixels` exists (alpha actually varies) and the name starts with:

- `mountains_` -> box size 5
- `desert_mountains_` -> box size 3

The kernel is an in-bounds box mean, not a separable blur:

```
sum = 0 (float32); count = 0
for oy in [-1 .. boxSize-1]:
  for ox in [-1 .. boxSize-1]:
    if (uint)(y+oy) < (uint)height and (uint)(x+ox) < (uint)width:
      sum += src[ (x+ox) + (y+oy)*width ]; count++
dst[ x + y*width ] = sum / (float)count
```

The window is shifted one pixel up/left of centre (offsets `-1 .. boxSize-1`),
edges divide by the number of in-bounds samples, and the result goes into a new
`Persistent` array that replaces and disposes the old one. `RawStamp::BoxAlpha`
(IL=106, 4x4 in-place, double accumulator) has **zero call sites**.

### 1.5 Types

`WorldGenerationEngineFinal.RawStamp` is a class holding `string name` and a
nested `struct Data`:

```
Data { float heightConst; NativeArray<float> heightPixels;
       float alphaConst;  NativeArray<float> alphaPixels;
       NativeArray<float> waterPixels; int width; int height; }
```

`RawStamp::Clear` (IL=13) disposes the three arrays.

`WorldGenerationEngineFinal.Stamp` is a *placed* stamp:

```
Stamp { WorldBuilder worldBuilder; TranslationData transform; float alpha;
        bool additive; float scale; Color32 customColor; float alphaCutoff;
        Rect Area; bool isWater; string Name; RawStamp stamp;
        static float cOneByOneScale; }
```

`StampGroup` is `{ string Name; List<Stamp> Stamps; }`.

`TranslationData` is `{ int x; int y; float scale; int rotation; }` with two
ctors: `(x, y, randomScaleMin, randomScaleMax)` which draws
`scale = Rand.Range(min,max)` and `rotation = Rand.Angle()` (IL=19), and
`(x, y, scale, rotation)` which stores both (IL=13).

The destination is `WorldBuilder/Data::HeightMap` and `Data::waterDest`, both
`NativeArray<float>` of `WorldSize * WorldSize`, created by `Data::Init` (IL=44)
with `Allocator` 4 (`Persistent`) and `NativeArrayOptions` 1 (`ClearMemory`), so
both start at zero. The Unity enum values are read from the shipped
`UnityEngine.CoreModule.dll`. Indexing is `x + y * WorldSize` (`SetHeight`
IL=25, `ClearWaterUnderTerrain$BurstManaged` IL=43).

### 1.6 Stamp construction

`Stamp::.ctor(WorldBuilder, RawStamp, TranslationData, Color32, float
alphaCutoff, bool isWater, string stampName)` (IL=210) copies
`transform.scale` into `Stamp.scale`, sets `alpha = 1`, `additive = false`, and
computes `Area` as the bounding box of the four rotated corners of a
`(w*scale*1.4) x (h*scale*1.4)` box around `(transform.x, transform.y)`. That
corner rotation (`getRotatedPoint`) calls `Math.Cos/Sin` on the raw rotation
**without** converting degrees to radians, unlike the rasterizer (1.7), and the
`Rect` size is `min - max` (negative). `Area` is not read by any rasterizer in
this build; it is appended to `worldBuilder.waterRects` for water stamps.

### 1.7 The height rasterizer (`DrawStamp$BurstManaged`)

`StampManager::DrawStamp(NativeArray<float>& _dest, Stamp)` (IL=38) forwards to
`DrawStamp(NativeArray<float>&, Data&, x, y, destW, destH, alphaScale, additive,
scale, customColor, alphaCutoff, angle)` (IL=14), a Burst direct call into
`DrawStamp$BurstManaged` (IL=278). Passed values: `destW = destH =
worldBuilder.WorldSize`, `x = transform.x`, `y = transform.y`,
`alphaScale = Stamp.alpha`, `additive = Stamp.additive`,
`scale = Stamp.scale`, `customColor = Stamp.customColor`,
`alphaCutoff = Stamp.alphaCutoff`, `angle = (float)transform.rotation`.

Exact body, in IL order (float32 arithmetic throughout unless noted):

```
// 1. centre the source over the destination cell
x -= (int)((float)src.width  * scale) / 2;    // conv.i4 of the product, then int /2
y -= (int)((float)src.height * scale) / 2;

// 2. angle: float32 degrees -> float32 radians -> double sin/cos -> float32
float rad = 0.01745329f * angle;
float sn = (float)Math.Sin((double)rad);
float cs = (float)Math.Cos((double)rad);

// 3. rotation slack around the source box
int m = (int)Math.Floor( (double)(
            (float)( ((int)Math.Sqrt((double)(src.width*src.width + src.height*src.height))
                      - src.width) / 2 )        // int /2
            * scale) );
int n = (int)Math.Floor( (double)((float)src.width * scale + (float)m) );

// 4. clipped loop bounds, relative to the stamp's top-left (x,y)
int i0 = -m; if (x + i0 < 0)          i0 = -x;
int i1 =  n; if (x + i1 >= destWidth)  i1 = n - (x + i1 - destWidth);
int j0 = -m; if (y + j0 < 0)          j0 = -y;
int j1 =  n; if (y + j1 >= destHeight) j1 = n - (y + j1 - destHeight);

RotateParams p = { sine=sn, cosine=cs, width=src.width, height=src.height,
                   halfWidth=src.width/2, halfHeight=src.height/2, isWater=false };

for (int j = j0; j < j1; j++):
  int row = (y + j) * destWidth;
  float sy = (float)j / scale;                 // source y, measured from the stamp corner
  for (int i = i0; i < i1; i++):
    float sx = (float)i / scale;               // source x
    float a = src.alphaConst;
    if (src.alphaPixels.IsCreated)
        a = CalcRotatedValue(ref p, sx, sy, src.alphaPixels);
    if (a < 1e-05f) continue;
    int idx = x + i + row;
    if (customColor.a > 0) {
        if (a > alphaCutoff)
            dest[idx] = (float)customColor.r;
    } else {
        float h = src.heightConst;
        if (src.heightPixels.IsCreated)
            h = CalcRotatedValue(ref p, sx, sy, src.heightPixels);
        float wgt = a * alphaScale;
        float old = dest[idx];
        if (additive) old = old + h * wgt;              // dest += h * a * alphaScale
        else          old = old + (h - old) * wgt;      // dest = lerp(dest, h, a * alphaScale)
        dest[idx] = old;
    }
```

Point-by-point:

- **Destination indexing** is row-major `idx = (y + j) * destWidth + (x + i)`. The
  iterated cells are the clipped box `[x+i0, x+i1) x [y+j0, y+j1)`; individual
  cells inside it are skipped by the `1e-05` and cutoff gates.
- **Source sampling is bilinear** with a nearest-corner fallback at the source
  edge (1.8); it is not nearest-neighbour.
- **`_scale`** maps one source pixel to `scale` destination cells, so the covered
  box is about `w*scale + 2m` wide, where `m` is the extra needed for the
  rotated diagonal (`~0.207 * w * scale` for a square). Rotation is about the
  source centre: at `i = w*scale/2`, `sx = halfWidth`.
- **`_alphaScale`** multiplies the sampled alpha to form the blend weight. It is
  `Stamp.alpha`, which the placer sets to the cluster strength, not 1 (1.10).
- **`_additive`** selects `old + h*w` instead of `old + (h-old)*w`.
- **`_customColor`** switches the whole cell to a colour store: when
  `customColor.a > 0` the cell receives `(float)customColor.r` and the height
  channel is not touched. No caller of this float overload passes an alpha > 0
  in this build (all terrain/base `Stamp`s are built with a default `Color32`).
- **`_alphaCutoff`** gates only the colour branch; the height branch is gated
  only by the fixed `1e-05` floor.
- **Numeric range: the destination holds raw `float`, not byte or ushort, and
  there is no clamp in the rasterizer.** Height values enter as 0..255
  (`r*255`) and the additive branch can exceed 255. The only post-pass is
  `AdjustHeights(HeightMap, 2f)` (IL=20 in the Burst body), which is
  `src[i] = Utils.FastMax(src[i], 2f)`, minimum only.

### 1.8 The source sampler (`CalcRotatedValue`)

Two overloads with identical math: `(x1, y1, NativeArray<float>& src, sine,
cosine, width, height, bool isWater)` (IL=174) and
`(RotateParams& p, x1, y1, NativeArray<float>& src)` (IL=177). `RotateParams` is
the same eight fields as the parameter list, with `halfWidth = width/2` and
`halfHeight = height/2`.

```
float CalcRotatedValue(ref p, float sx, float sy, float[] src):
  float fx =  p.cosine * (sx - p.halfWidth) + p.sine   * (sy - p.halfHeight) + p.halfWidth;
  int xi = (int)fx;                          // truncation toward zero
  if ((uint)xi >= (uint)p.width) return 0f;
  float fy = -p.sine  * (sx - p.halfWidth) + p.cosine * (sy - p.halfHeight) + p.halfHeight;
  int yi = (int)fy;
  if ((uint)yi >= (uint)p.height) return 0f;

  int idx = xi + yi * p.width;
  float p00 = src[idx];
  float p10 = (xi + 1 < p.width)                ? src[idx + 1]                  : p00;
  float p01 = (yi + 1 < p.height)               ? src[idx + p.width]            : p00;
  float p11 = (xi + 1 < p.width && yi + 1 < p.height) ? src[idx + p.width + 1]  : p00;

  if (p.isWater && (p00 > 0f || p01 > 0f || p10 > 0f || p11 > 0f))
      return p00;                            // water keeps a hard edge

  fx -= (float)xi;  fy -= (float)yi;         // fractional parts
  p00 = p00 + (p10 - p00) * fx;              // horizontal first
  p01 = p01 + (p11 - p01) * fx;
  p00 = p00 + (p01 - p00) * fy;              // then vertical
  return p00;
```

Notes for a bit-exact port: out-of-range returns 0 before any interpolation;
weights are computed from the truncated integer, so `fx/fy` are in `[0,1)` for
in-bounds samples; the vertical lerp uses the already-horizontal results.

### 1.9 Water and biome variants

**`DrawWaterStamp(Stamp, NativeArray<float>&, int destSize)` (IL=60)** throws
`ArgumentException("DrawWaterStamp called with non-water stamp" + Name)` when
`Stamp.isWater` is false. Source is `RawStamp.data.waterPixels`; when that array
was not created it falls back to `alphaPixels`; when neither exists it returns
without drawing. It calls `DrawWaterStamp$BurstManaged` (IL=206) with
`destW = destH = destSize`, `x/y/rotation` from `transform`, `alpha =
Stamp.alpha`, `scale = Stamp.scale`, and `customColor` filled from
`Stamp.customColor.b` (a single float, not the `Color32`).

```
water body (identical geometry and loop bounds to 1.7), then:
  if (dest[idx] > 0f) continue;                     // first stamp wins
  float v = CalcRotatedValue(ref p, (float)i/scale, (float)j/scale, src);   // p.isWater = true
  if (v < 1e-05f) continue;
  dest[idx] = customColor;                          // the blue scalar, no alpha scale
```

Differences from the height path: channel is `waterPixels` (fallback alpha);
`isWater = true`; the write gate is `dest <= 0` inside the footprint plus
`v >= 1e-5`; the stored value is the stamp's blue scalar with no blend, no
cutoff and no `alphaScale`. The `_alpha` parameter is passed but **never read**
in the body (IL=206, no `ldarg.s _alpha`).

**`DrawStamp(Color32[], Data&, x, y, destW, destH, srcW, srcH, alpha, scale,
customColor, alphaCutoff, angle, isWater)` (IL=184)** is the non-Burst colour
rasterizer used by `DrawStampGroup(StampGroup, Color32[], int, float)` (IL=97).
Same geometry (float `Mathf.Sqrt`/`Mathf.FloorToInt` instead of double), same
clipped bounds, same `CalcRotatedValue` on `alphaPixels` (or `alphaConst`), but
the write is `dest[idx] = customColor` (whole `Color32`) when `alphaCutoff <
alpha`, with no `1e-05` floor, no height channel and no blend. `_alpha` is again
unused.

**`DrawBiomeStamp(Color32[], NativeArray<float>& src, x, y, destW, destH, srcW,
srcH, scale, Color32 destColor, alphaCutoff, angle)` (IL=174)** is the same
colour paint but over a caller-supplied float array: it writes `destColor` where
`CalcRotatedValue(..., isWater = false) > alphaCutoff`. Its single call site is
`GenerateBaseStamps` (`<>c__DisplayClass142_0::b__2`, IL=173, call at IL_0178):
it paints `filler_biome` into `biomeDest` at `BiomeSize` resolution with
`scale = (32/2)/raw.width * 1.5 + Rand.Range(0f, 0.2f)`, rotation
`Range(0,4)*90 + Range(-20,20)`, colour `biomeColors[biome]`, cutoff 0.1.

### 1.10 Group iteration and the destination buffers

`StampManager::DrawStampGroup(StampGroup, NativeArray<float>& _dest, int size)`
(IL=56) ignores `size` entirely and loops `_group.Stamps` in list order:

```
for (int i = 0; i < group.Stamps.Count; i++) {
    Stamp s = group.Stamps[i];
    if (s == null) continue;
    DrawStamp(ref dest, s);                  // uses worldBuilder.WorldSize for both axes
    if (worldBuilder.IsCanceled) break;      // checked after each draw
}
Log.Out("DrawStampGroup '{0}', count {1}, in {2}", group.Name, group.Stamps.Count, ms*0.001f);
```

`DrawWaterStampGroup(StampGroup, NativeArray<float>&, int destSize)` (IL=56) is
the same loop over `DrawWaterStamp(stamp, dest, destSize)`. The `Color32[]`
variant (`DrawStampGroup(StampGroup, Color32[], int size, float stampScale)`,
IL=97) additionally scales each stamp's position (as `(int)(transform.x *
stampScale)`, truncation) and its `scale` by `stampScale` before drawing; it logs
`"DrawStampGroup c32 '...'"`.

Call sites in V3.3.0 b18:

| layer | destination | size / scale | call site |
|---|---|---|---|
| `lowerLayer` | `data.HeightMap` | `WorldSize` | `GenerateTerrainLast` b__147_0 IL=001D |
| `terrainLayer` | `data.HeightMap` | `WorldSize` | `GenerateTerrainLast` b__147_0 IL=003F, then `AdjustHeights(2f)` |
| `waterLayer` | `data.waterDest` | `WorldSize` | `GenerateTerrainLast` b__147_1 IL=001D |
| `biomeLayer` | `biomeDest` (Color32[]) | `BiomeSize = WorldSize/8`, scale 0.125 | `DrawBiomeRadStampsToMaps` b__144_0 |
| `radiationLayer` | `radDest` (Color32[]) | `RadSize`, scale 1.0 | `DrawBiomeRadStampsToMaps` b__144_1 |

The two `GenerateTerrainLast` tasks run in parallel (`Task.Start` for
terrain and water), then `ClearWaterUnderTerrain` runs.

### 1.11 Name lookup and variant selection

`TryGetStamp(String baseName, RawStamp& out, Rand rand)` (IL=79) enumerates
`AllStamps` (a `Dictionary<string, RawStamp>`) under `Monitor.Enter` on the
reusable `tempGetStampList`, collecting every key for which
`key.StartsWith(baseName)` (case-sensitive, ordinal). Then:

- zero matches: `out = null`, return false;
- exactly one: that stamp;
- more: `out = list[rand.Range(list.Count)]`, i.e. a uniform pick over the list
  in dictionary order.

`TryGetStamp(String terrainTypeName, String comboTypeName, RawStamp& out)`
(IL=14) tries **`comboTypeName` first, then `terrainTypeName`**. Because the
match is a prefix match on the bare file name, `terrainTypeName = "mountains"`
selects `mountains_01`/`mountains_02` but never `desert_mountains_01`; the combo
name `"desert_mountains"` is what reaches those. `GetStamp(name, rand)`
(IL=14) substitutes `Rand.Instance` when `rand` is null and returns null on a
miss.

### 1.12 Tile to stamp selection

`WorldBuilder::GenerateTerrain()` (IL=128) calls `GenerateBaseStamps()`, then
`GenerateTerrainFromTiles(plains, 1024)`, `(hills, 512)`, `(mountains, 256)`.
`GenerateTerrainFromTiles(TerrainType, int tileSize)` (IL=283):

```
mapSize = WorldSize / 256;  cellsPerTile = tileSize / 256;
terrainName = EnumUtils.ToStringCached(_terrainType);       // "plains" | "hills" | "mountains"
for (x = 0; x < mapSize; x += cellsPerTile)
 for (y = 0; y < mapSize; y += cellsPerTile):
    // every cell of the tile must already carry this terrain type
    all = true;
    for (a = 0; a < cellsPerTile && all; a++)
     for (b = 0; b < cellsPerTile && all; b++)
        if (terrainTypeMap.Get(x+a, y+b) != _terrainType) all = false;
    if (!all) continue;

    BiomeType biome = biomeMap.Get(x, y);       // top-left cell of the tile only
    if (biome == 255) biome = 0;                // RWG BiomeType.none -> forest
    if (_terrainType == mountains && biome == 4 /* wasteland */) {
        terrainTypeMap.Set(x, y, plains);       // and no stamp
        continue;
    }

    int wx = x*256 + tileSize/2, wy = y*256 + tileSize/2;   // tile centre
    string biomeName = EnumUtils.ToStringCached(biome);
    string combo = biomeName + "_" + terrainName;

    GetTerrainProperties(biomeName, terrainName, combo,
        out scaleMinMax, out clusterCount, out clusterRadius,
        out clusterStrength, out useBiomeMask, out biomeCutoff);

    scaleMinMax    *= (float)cellsPerTile;      // Vector2 * float
    clusterRadius  *= cellsPerTile;

    float offsetRadius = 0;
    float alphaScale   = clusterStrength;
    bool  additive     = false;

    for (int c = 0; c < clusterCount; c++) {
        RawStamp raw;
        if (!TryGetStamp(terrainName, combo, out raw)) { /* skip this cluster */ }
        else {
            Vector2 off = Rand.RandomOnUnitCircle() * offsetRadius;
            TranslationData tr = new TranslationData(
                wx + RoundToInt(off.x), wy + RoundToInt(off.y),
                scaleMinMax.x, scaleMinMax.y);      // ctor draws scale and rotation
            var st = new Stamp(worldBuilder, raw, tr, default(Color32) /* a=0 */,
                               0.1f, false, raw.name);
            st.alpha     = alphaScale;
            st.additive  = additive;
            terrainLayer.Stamps.Add(st);

            if (useBiomeMask)
                biomeLayer.Stamps.Add(new Stamp(worldBuilder, raw, tr,
                    biomeColors[biome], biomeCutoff, false, ""));
        }
        offsetRadius = clusterRadius;    // all later clusters sit on the circle
        alphaScale   = clusterStrength * 0.45f;
        additive     = true;
    }
```

So a qualifying tile gets one centred, non-additive stamp at
`alpha = clusterStrength` and `clusterCount - 1` (default 3 total) additive
stamps on a circle of radius `clusterRadius` around the tile centre, each at
`alpha = clusterStrength * 0.45`. Every one uses the same scale range draw per
stamp (the ctor draws its own scale and its own random angle per stamp), and the
biome colour stamp shares the same `TranslationData`, so it lands in exactly the
same place.

`GetTerrainProperties` (IL=144), default values first:

| out | default | rwgmixer keys (combo, then terrain) | parse |
|---|---|---|---|
| `scaleMinMax` | `Vector2.one` | `scale` | `StringParsers.ParseVector2`, then `* 0.5f` |
| `clusterCount` | 3 | `clusters` | `ParseVector3`, `.x` truncated to int |
| `clusterRadius` | 85 | `clusters` | `.y * 256` truncated to int |
| `clusterStrength` | 1.0 | `clusters` | `.z` |
| `useBiomeMask` | false | `use_biome_mask` | `ParseBool` |
| `biomeCutoff` | 0.1 | `biome_mask_min` | `ParseFloat` |

A key present under the combo name wins; an empty combo value falls back to the
same key under the terrain name. With the later `* cellsPerTile`, the default
radius is `85 * tileSize / 256` (85 cells for mountains, 170 for hills, 340 for
plains), and `scaleMinMax = parsed * 0.5 * tileSize / 256`, i.e. a 512-px stamp
at `scale = 1` covers exactly one tile.

**Tile type 255:** the tile-wide "all cells are my type" scan fails, so a 255
tile gets no stamp from any of the three passes. That matches 3.2. Biome 255
inside an otherwise qualifying tile is remapped to 0 (forest) for property and
colour lookup only. Mountains over wasteland are converted to plains cells and
skipped.

### 1.13 What the destination values become

- `AdjustHeights` runs once after both height layers: `height = FastMax(height,
  2f)`, minimum only, no ceiling.
- `ClearWaterUnderTerrain` (IL=43, and called again from
  `DrawBiomeRadStampsToMaps`): `if (height[i] - 0.5f > waterDest[i])
  waterDest[i] = 0f;`
- `FinalizeWater$BurstManaged` (IL=35) then rewrites every cell:
  `waterDest[i] = (height[i] - 0.5f > waterDest[i]) ? 0f : WaterHeight;` with
  `WaterHeight = 30` (ctor literal). So the final water map is binary 0 / 30;
  the stamp blue (also 30) only decided *where* water survives.
- `serializeRawHeightmap` -> `HeightMapUtils::SaveHeightMapRAW(Stream, float[],
  offset)` (IL=37) with `offset = -1`: `v = (int)((height + offset) * 257)`,
  `v = FastClamp(v, 0, 65535)`, written as two little-endian bytes. So the
  saved height map is `u16 = clamp((height - 1) * 257, 0, 65535)`, i.e. block
  heights 1..256 map to 0..65535 with 257 units per block, height 0 or below
  saves as 0, and float heights above 256 clamp at 65535 on save.
- Water stamp colour is `new Color32(0, 0, (byte)WaterHeight, 255)`, i.e. the
  blue scalar is 30, and that is what `DrawWaterStamp` writes into
  `waterDest`. Both the lake/river path (`generateTerrainFeature`) and the base
  `water_border` stamps build it that way, so the clearance test in
  `ClearWaterUnderTerrain` is effectively `height - 0.5 > 30`.
- `SerializeWater` (IL=81) writes `(byte)waterDest[i]` into the blue channel of
  a `Color32[]`.

## 2. Inferred

- `Rand.Angle()` (IL=5) is `gameRandom.RandomRange(360)` -> `GameRandom.Next(360)`
  -> `(int)(Sample() * 360)`, so rotation is `[0, 360)`. The `Next(Int32)` body
  was read; that the unit is degrees is inferred from the rasterizer's
  `0.01745329f * angle`.
- `Rand.RandomOnUnitCircle()` is `(cos t, sin t)` with `t = (float)NextDouble() *
  6.283185f` (`GameRandom.get_RandomOnUnitCircle`, IL=12). So clusters sit
  exactly on the radius, not inside it.
- The `.png` branch depends on the imported texture being readable; the IL only
  calls `TextureUtils.LoadTexture` then `GetPixels()`. Whether the shipped PNG
  stamps import as readable is not checked here.
- For the shipped square stamps (512x512, 1024x1024) the float-sqrt colour
  path and the double-sqrt Burst path compute the same `m` and `n`. This is
  arithmetic reasoning, not an execution.
- `ParseVector2` on a one-number `scale` string presumably yields `(v, v)`;
  rwgmixer content semantics are out of scope for this doc.
- The biome index 4 special case is `wasteland` per
  `WorldGenerationEngineFinal.BiomeType` (`forest 0, burntForest 1, desert 2,
  snow 3, wasteland 4, none 255`), read from the same assembly. The intent
  ("no mountains in wasteland") is inferred from the branch, not from a comment.

## 3. Not decoded

- **Why `.exr` is rejected.** `LoadStamp` returns at IL_0050 for `.exr`, and
  `SaveEXR` (IL=41, `Data/Stamps/<name>.exr`, `ImageConversion.EncodeToEXR`)
  writes such files. No reader for them exists in V3.3.0 b18, so either the
  path is unfinished or EXR stamps are consumed by tooling outside the
  assembly. Not established which.
- `RawStamp::BoxAlpha` (IL=106) and `Utils::LoadRawStampFile` (IL=91) have zero
  call sites. Dead code, purpose unknown.
- Why the `SmoothAlpha` window is offset to `[-1, boxSize-1]` rather than
  centred, and why the two name prefixes use 5 and 3. Behaviour is pinned, the
  author's intent is not.
- `Stamp::getRotatedPoint` (IL=46) uses `Math.Cos/Sin(angle)` on the raw
  degree value. Whether `Area` is a deliberate conservative bound or a bug is
  not established; `Area` is not read by any rasterizer here.
- Whether any build variant (server, or V3.4.0 b10) changed the `1.4` factor,
  the `0.45` cluster alpha, the `1e-05` floor, the `257` save scale or the
  `0.01745329f` constant. Every one is a literal in V3.3.0 b18 and needs a
  re-dump against the studied build.
