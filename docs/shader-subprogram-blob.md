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

A record is either a **parameter blob** (constant-buffer and texture-parameter
names, indexed by `m_ParameterBlobIndices`) or a **code blob** (indexed by
`m_BlobIndex` on a sub-program). Both begin with the same `u32` version tag
`202012090` (`ba 75 0a 0c` on disk, which is that integer and not a magic), so
the two kinds are told apart by which index list reaches them, never by
sniffing the bytes.

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
```

There is **no local-keyword array** at this version: Unity carried one only
between 2019.1 and 2021.2. That is the field whose presence decides whether
the byte array is found at all.

This ordering is what both open-source parsers of the format read:
[USCSandbox `ShaderSubProgram.cs`](https://github.com/nesrak1/USCSandbox/blob/main/USCSandbox/Processor/ShaderSubProgram.cs)
and [UnityPy `ShaderConverter.py`](https://github.com/K0lb3/UnityPy/blob/master/UnityPy/export/ShaderConverter.py).

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
38-byte offset, and header bytes 0, 2, 3 and 5. `inferred` for byte 1 (a
binding count that bounds the declaration count from above). **Not decoded:**
the quantity in byte 4, and the meaning of the three empty `m_PlayerSubPrograms`
groups.

## Changelog

- **2026-08-24:** Initial reversal. Container, record table and code-blob
  record cross-read against USCSandbox and UnityPy; the 38-byte DX11 header
  measured over 7366 sub-programs from two independent stock samples, with
  bytes 1 to 3 newly identified as the SRV, constant-buffer and sampler counts
  by walking the DXBC token stream. Reproduction tool:
  [`tools/shader_blob_dump.py`](../tools/shader_blob_dump.py).
