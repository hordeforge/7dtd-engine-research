# Shader (class 48) sub-program blob layout

Reference for the compiled-shader container inside a stock UnityFS bundle, as
validated on the stock V3.1.0 b14 install (Unity 2022.3.62f2). Picks up where
[texture-atlas-unityfs.md](texture-atlas-unityfs.md) stops: that page decodes
the container, the SerializedFile header/type/object tables and TextAsset
(class 49); this one decodes Shader (class 48) down to the driver bytecode.
**Hub:** [`INDEX.md`](INDEX.md). **Method:** [`re-methodology.md`](re-methodology.md).

Reproduce every number here with the tracked tool:

```bash
python3 tools/shader_blob_dump.py "$GAME/Data/Bundles/Standalone/Entities/trees"
python3 tools/shader_blob_dump.py "$GAME/7DaysToDie_Data/data.unity3d"
```

## Sample

Two independent stock samples, **7366 d3d11 sub-programs** in total:

| Source | Shaders | d3d11 sub-programs |
|---|---|---|
| `Data/Bundles/Standalone/Entities/trees` | 10 (6 decodable, 4 multi-tier) | 1894 |
| `7DaysToDie_Data/data.unity3d` (player) | built-in set | 5472 |

Multi-tier shaders are skipped, not guessed: blob indices are per hardware
tier, and the parsed form alone does not say which tier a sub-program's index
belongs to. 5 of the 10 `trees` shaders and 1 player shader are skipped for
that reason.

## Object fields

The Shader object carries the compiled code out-of-line from the parsed form:

```text
m_ParsedForm  : SerializedShader (name, properties, sub-shaders, passes)
platforms     : u32[]   ShaderCompilerPlatform; stock is [4, 15, 18]
                        = d3d11, OpenGLCore, Vulkan
offsets            : u32[][]  per platform, then per hardware tier
compressedLengths  : u32[][]  parallel to offsets
decompressedLengths: u32[][]  parallel to offsets
compressedBlob     : u8[]     every platform/tier blob concatenated
```

Each `(platform, tier)` slice of `compressedBlob` is **LZ4 block compressed**
to its `decompressedLengths` entry.

## Blob layout (little-endian)

```text
count          : u32                     number of records
per record     : offset u32, length u32, segment u32   (12 bytes, tiling the payload)
payload        : the records, contiguous from the end of the table
```

The stride is 12, not 8, from Unity 2019.3 on; `segment` is 0 in all 7366
samples. The table tiles the payload contiguously: `count * 12 + 4` is the
first record's offset, and each `offset + length` is the next offset.

A record is either a **parameter blob** (indexed by `m_ParameterBlobIndices`)
or a **code blob** (indexed by `m_BlobIndex` on a sub-program). Both begin with
the same `u32` version tag `202012090` (`ba 75 0a 0c` on disk, which is that
integer and not a magic), so the two kinds are told apart by which index list
reaches them, never by sniffing the bytes. In practice a platform blob holds
its parameter blobs at the low indices and its code blobs above them.

### How the two index spaces line up

This is the part that is easy to get wrong, because one list is not what it
looks like. `m_PlayerSubPrograms` group 3 **mixes platforms**: a single group
holds the d3d11, OpenGLCore and Vulkan variants of the same program back to
back, each carrying an `m_BlobIndex` into *its own* platform blob.

`m_ParameterBlobIndices` group 3 is **parallel to that list, position by
position** - not a list of parameter blobs in its own right. Position `k`'s
parameter blob lives in the same platform blob as position `k`'s sub-program.

Reading `m_ParameterBlobIndices` as a flat set and resolving it against one
platform's table is the natural mistake, and it silently resolves to code
blobs: 2936 of 3403 parameter records "fail to parse" that way, which looks
like a broken format rather than a wrong index space.

## Code-blob record

For version tag `202012090` (Unity 2021.2 and up):

```text
version        : u32    202012090
programType    : u32    ShaderGpuProgramType; 15 = DX11VertexSM40, 17 = DX11PixelSM40
statsALU       : u32
statsTEX       : u32
statsFlow      : u32
statsTempRegister : u32                  (present since Unity 5.5)
keywordCount   : u32
per keyword    : length u32, bytes, padded to 4
programData    : length u32, then that many bytes
align to 4
bindChannels   : ParserBindChannels (below) - closes the record
```

There is **no local-keyword array** at this version: Unity carried one only
between 2019.1 and 2021.2. That is the field whose presence decides whether
the byte array is found at all.

This ordering is what both open-source parsers of the format read:
[USCSandbox `ShaderSubProgram.cs`](https://github.com/nesrak1/USCSandbox/blob/main/USCSandbox/Processor/ShaderSubProgram.cs)
and [UnityPy `ShaderConverter.py`](https://github.com/K0lb3/UnityPy/blob/master/UnityPy/export/ShaderConverter.py).

## Bind channels

Every code-blob record **ends** with a `ParserBindChannels` block, after the
program data and its alignment. It is easy to miss: the program data is the
last field that looks like content, and a record is 8 to 40 bytes longer than
the program data alone accounts for.

```text
sourceMap : i32   a stored mask of mesh channels
count     : i32
per bind  : source i32, target i32
```

`source` is the mesh channel the engine reads; `target` is the shader input it
feeds. The mapping was derived by correlating every stock vertex blob's
channel list against its own DXBC input signature:

| Semantic | source | target |
|---|---|---|
| `POSITION` 0 | 0 | 0 |
| `NORMAL` 0 | 1 | 1 |
| `TANGENT` 0 | 2 | 2 |
| `COLOR` 0 | 3 | 3 |
| `TEXCOORD` *n* | 4 + *n* | 5 + *n* |

Two things about it are not what they look like:

- **The channel list is a subset of the input signature.** Only the inputs the
  program actually reads get a channel. `Legacy Shaders/Specular` declares
  eight signature elements and binds three.
- **`sourceMap` is not derived from the channel list.** It is a stored base
  mask that a reader ORs each bound channel's bit into
  (`SourceMap |= 1 << channel.Source` in USCSandbox), so the stored value can
  name channels the program never binds - `Nature/SpeedTree Billboard` stores
  63 while binding channels that imply 49. The invariant that holds over both
  samples is containment: every bound channel's bit is set in `sourceMap`.

A **pixel** program writes the block with `sourceMap` 0 and `count` 0 - eight
bytes, still present. Its inputs come from the vertex program's outputs, not
from mesh channels.

This block is why a record that ends at its program data is rejected. Omitting
it produces `Failed to load GpuProgram from binary shader data` from the
runtime - a refusal, not a mis-draw, which is the good failure mode.

## DX11 program-data header

`programData` is **not** bare bytecode. For every d3d11 sub-program it is a
38-byte Unity header followed by a DXBC container. The size follows
USCSandbox's `GetDirectXDataOffset`: a 6-byte base header (5, plus 1 for the
geometry-shader input primitive added in Unity 5.4), plus `0x20` more when the
header version is at least 2. Stock is always header version 2, so
`6 + 32 = 38`, and `DXBC` begins at offset 38 in **7366 of 7366** sub-programs.

| Offset | Size | Field | Evidence over 7366 sub-programs |
|---|---|---|---|
| 0 | u8 | header version, always `2` | 7366/7366 |
| 1 | u8 | SRV count: `dcl_resource` + `dcl_resource_raw` + `dcl_resource_structured` | 7364 equal, 2 where Unity counts more (below) |
| 2 | u8 | constant-buffer count: `dcl_constantbuffer` | 7366/7366 |
| 3 | u8 | sampler count: `dcl_sampler` | 7366/7366 |
| 4 | u8 | UAV-related; zero unless the program declares a UAV | 7364/7366 zero |
| 5 | u8 | geometry-shader input primitive; zero for vertex and pixel programs | 7365/7366 zero |
| 6..37 | 32 B | zero; present only because the header version is at least 2 | 7366/7366 zero |
| 38.. | | the DXBC container | 7366/7366 |

Bytes 1 through 3 were **not** taken from a parser: no parser reads them, both
AssetStudio and UnityPy stop at "shader disassembly not supported on DXBC",
and USCSandbox skips the whole 38 bytes to reach the bytecode. They were
derived by walking the DXBC `SHDR`/`SHEX` token stream of every sub-program
and counting its declaration opcodes. The assignment is discriminated, not
coincidental: pairing the same three bytes against the wrong declaration
counts mismatches 1644, 1651 and 124 times respectively on the `trees` sample
alone.

### The four exceptions, and what each one confirms

Every sub-program that departs from the table above was inspected, and each
one corroborates a field rather than undermining it:

- `Hidden/VR/BlitFromTex2DToTexArraySlice` has `header[5] = 3`. It is the only
  **geometry** sub-program in either sample (`ShaderGpuProgramType` 19), which
  is exactly when USCSandbox's `hasGSInputPrimitive` byte is meaningful.
- `Occlusion/DepthTest` (two sub-programs) has `header[4] = 2`. They are the
  only two declaring a UAV (`dcl_uav_structured`). That byte is UAV-related;
  the exact quantity is **not decoded** - one UAV is declared and the byte
  reads 2 - and it is zero in the other 7364.
- `Game/DistantPOI_TA` (two sub-programs) has `header[1] = 2` against a single
  declared SRV. Unity records what **it** bound, which can exceed what
  survived the compiler's optimization. So byte 1 is Unity's binding count and
  is `>=` the declaration count, with equality in 7364 of 7366.

### DXBC chunks Unity keeps

| Chunk set | Count |
|---|---|
| `ISGN`, `OSGN`, `SHDR` | 7015 |
| `ISGN`, `OSGN`, `SHEX` | 350 |
| `ISGN`, `OSGN`, `SFI0`, `SHEX` | 1 |

Unity **strips `RDEF` and `STAT`** from every container. That is why the
38-byte header exists at all: the reflection data a `RDEF` chunk would carry
lives in Unity's own structures instead - the parameter blobs and the
program's `m_CommonParameters` - and the three count bytes are the runtime's
summary of it. `SHDR` is shader model 4 and `SHEX` shader model 5; the token
stream is identical.

## Parameter blob

The other record kind. It carries the binding table the stripped `RDEF` chunk
would otherwise hold: the constant buffers and their members, and the texture,
buffer, UAV and sampler bindings.

```text
version        : i32    202012090, same tag as a code blob
bufferCount    : i32
per buffer     : name (i32 length + bytes, padded to 4)
                 usedSize i32
                 paramCount i32, then that many constant-buffer params
                 structCount i32, then that many struct params
constant-buffer param:
                 name (padded string), type i32, rows i32, columns i32,
                 isMatrix i32, arraySize i32, index i32
struct param   : name (padded string), index i32, arraySize i32, size i32,
                 paramCount i32, then that many constant-buffer params
entryCount     : i32
per entry      : name (padded string), kind i32, then by kind:
                 0 texture : index i32, samplerIndex i32, extra u32
                             (extra & 1 = multi-sampled, extra >> 1 = dimension)
                 1 cbuffer binding : index i32, arraySize i32
                 2 buffer binding  : index i32, arraySize i32
                 3 UAV             : index i32, originalIndex i32
                 4 sampler         : bindPoint i32, sampler u32
```

Every string is length-prefixed and padded to a 4-byte boundary, and the
record ends exactly on the last field - no trailing padding inside the record.

**Evidence: 3403 of 3403 stock parameter blobs parse and re-emit byte for
byte, with zero trailing bytes** (729 from `trees`, 2674 from the player).
Round-tripping is a stronger check than parsing: a reader can skip a field it
misunderstands and still appear to work, but a writer that misplaces one byte
cannot reproduce the original. `tools/shader_blob_dump.py` performs this
round-trip as a gate and exits non-zero on any difference.

Entry kinds observed: texture and constant-buffer bindings dominate (15200 and
11371 across both samples), with 287 samplers and 58 buffer bindings. No UAV
entry appears in either sample, so kind 3's layout is **taken from the parser,
not measured here**.

This layout is [USCSandbox `ShaderParams.cs`](https://github.com/nesrak1/USCSandbox/blob/main/USCSandbox/Processor/ShaderParams.cs)
with `readBlobVersion` true; up to Unity 2021 the same structure was written
inline after the code blob instead of in a record of its own.

## Sub-program grouping

Compiled variants live in `m_PlayerSubPrograms` on each `SerializedProgram`,
and `m_SubPrograms` is empty (it is editor-only from 2021 on). Shared
parameters moved to `m_CommonParameters`.

`m_PlayerSubPrograms` declares exactly **four** groups and populates only index
**3**, on all 10 `trees` shaders whatever their platform count (always 3) or
tier count (1 to 6). That is an empirical rule over the sample, not an
understood semantic: what the other three slots mean is **not decoded**.

## Walking the SHDR token stream

Counting the declaration opcodes needs one non-obvious rule. The chunk is
`u32 version, u32 lengthInDwords`, then instruction tokens whose length is
bits 24..30 of the token. Opcode **53** (`CUSTOMDATA`, which carries the
immediate constant buffer) is the exception: its length field is zero and the
real length is the **following** dword. Missing that rule stalls the walk on
the first shader that uses an immediate constant buffer - 72 of the 1894
`trees` sub-programs, all of them pixel programs.

## Status

`verified` for the container, the record table, the code-blob record, the
bind-channel block and its semantic mapping, the
38-byte offset, header bytes 0, 2, 3 and 5, the parallel index space between
`m_ParameterBlobIndices` and `m_PlayerSubPrograms`, and the parameter-blob
layout (round-tripped byte for byte over 3403 records). `inferred` for byte 1
(a binding count that bounds the declaration count from above) and for
parameter entry kind 3, whose layout comes from the parser because no UAV
entry appears in either sample. **Not decoded:** the quantity in header byte
4, and the meaning of the three empty `m_PlayerSubPrograms` groups.

## Changelog

- **2026-08-24:** Initial reversal. Container, record table and code-blob
  record cross-read against USCSandbox and UnityPy; the 38-byte DX11 header
  measured over 7366 sub-programs from two independent stock samples, with
  bytes 1 to 3 newly identified as the SRV, constant-buffer and sampler counts
  by walking the DXBC token stream. Reproduction tool:
  [`tools/shader_blob_dump.py`](../tools/shader_blob_dump.py).
- **2026-08-24:** Bind channels decoded - the `ParserBindChannels` block that
  closes every code-blob record, its semantic-to-channel mapping, and the two
  traps in it (the channel list is a subset of the input signature;
  `sourceMap` is a stored base mask, not a derived one). Confirmed by
  construction: a synthesized shader whose records omitted this block was
  refused by a real 2022.3.62f2 runtime with `Failed to load GpuProgram from
  binary shader data`, and adding it made the same shader report
  `Shader.isSupported = true`.
- **2026-08-24:** Parameter blob decoded - the other record kind, carrying the
  binding table the stripped `RDEF` chunk would hold. 3403 of 3403 stock
  parameter blobs re-emit byte for byte. Also documents how
  `m_ParameterBlobIndices` runs parallel to the platform-mixed
  `m_PlayerSubPrograms` list, which is the index space that makes the format
  look broken when read flat.
