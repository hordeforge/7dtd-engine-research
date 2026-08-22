# UnityFS bundle layout (meshdescriptions_assets_all.bundle)

Reference for the `meshdescriptions_assets_all.bundle` container format, as
validated on the stock V3.1.0 b14 operator install (Unity 2022.3.62f2).
Backs [texture-atlas.md](texture-atlas.md); the atlas TextAssets live inside
this bundle.
**Hub:** [`INDEX.md`](INDEX.md). **Method:** [`re-methodology.md`](re-methodology.md).

## Header (big-endian)

```text
signature      : "UnityFS\0"                       (8 bytes)
version        : u32 BE                            (8)
version_player : null-terminated string            ("5.x.x")
version_engine : null-terminated string            ("2022.3.62f2")
size           : i64 BE                            (whole bundle)
compressedBlocksInfoSize    : u32 BE               (5828)
uncompressedBlocksInfoSize  : u32 BE               (14593)
flags          : u32 BE                            (0x243 = LZ4HC + BlocksAndDirectoryInfoCombined)
align to 16
blocks info    : compressedBlocksInfoSize bytes     (LZ4)
```

## Blocks info (decompressed, big-endian)

```text
dataHash       : 16 bytes
blockCount     : i32 BE
per block      : uncompressedSize u32 BE, compressedSize u32 BE, flags u16 BE
                 (flags & 0x3F: 0 none, 1 LZMA, 2 LZ4, 3 LZ4HC)
fileCount      : i32 BE
per file       : offset i64 BE, size i64 BE, flags u32 BE, name null-terminated
                 (offsets are relative to the start of the block data)
```

The storage blocks follow (16-aligned after the blocks info); each block is
decompressed per its flag and concatenated. This bundle: 1445 blocks, two
files - `CAB-<guid>` (serialized file, offset 0) and `CAB-<guid>.resS` (raw
texture data).

## Serialized file (the CAB, mixed endian)

Header (big-endian, 48 bytes):

```text
metadataSize u32 BE (0), fileSize u32 BE (0), version u32 BE (22),
dataOffset u32 BE (0), endianness u8 (0 = little body) + 3 reserved,
metadataSize u32 BE, fileSize i64 BE, dataOffset i64 BE, unknown i64 BE
```

After the header the reader switches to the file's endianness (little):

```text
unity version : null-terminated string
platform      : u32 LE
enableTypeTree: u8 LE
typeCount     : u32 LE
per type      : class_id i32, is_stripped u8, script_type_index i16,
                [script_id 16 if class_id == 114 or script_index >= 0],
                old_type_hash 16,
                [type-tree blob: node_count u32, stringbuffer_size u32,
                 node_count * 32 bytes (hBBIIiiiQ), stringbuffer bytes,
                 type_dependencies count u32 + count * i32]  (when enabled)
objectCount   : u32 LE
per object    : path_id i64 LE (4-aligned), byte_start i64 LE (absolute),
                byte_size u32 LE, type_index u32 LE
```

`type_index` indexes the type table; the class id is
`types[type_index].class_id` (TextAsset = 49). Object bytes live at
`byte_start` (which already includes `dataOffset`). A TextAsset serializes as
`m_Name` (u32 length + bytes, 4-aligned) then `m_Script` (u32 length + bytes
= the XML).

## Changelog

- **2026-08-21:** Initial reversal from the stock operator install; validated
  end-to-end by extracting the six `ta_*` atlas XMLs.
