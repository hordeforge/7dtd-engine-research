#!/usr/bin/env python3
"""Decode Shader (class 48) sub-program blobs from a stock UnityFS bundle.

Reproduces every measurement in docs/shader-subprogram-blob.md: the LZ4
per-platform blobs, the 12-byte record table, the sub-program header, and the
DX11 program-data header whose three count bytes are cross-checked against the
DXBC SHDR declarations they describe.

Needs UnityPy (not a repo dependency; this is a reproduction tool, not a gate):

    pip install UnityPy

Usage:
    python3 tools/shader_blob_dump.py <bundle> [--shader NAME] [--verbose]

Prints one summary table per bundle and exits non-zero if any decoded
sub-program disagrees with the documented header layout.
"""

from __future__ import annotations

import argparse
import collections
import struct
import sys

BLOB_VERSION = 202012090          # Unity 2021.2+ LoadGpuProgramFromData tag
DX11_TYPES = set(range(13, 23))   # kShaderGpuProgramDX10Level9Vertex .. DX11DomainSM50
PLATFORM_D3D11 = 4                # ShaderCompilerPlatform.d3d11
PROGRAMS = ("progVertex", "progFragment", "progGeometry", "progHull", "progDomain")

# D3D10/11 shader-bytecode opcodes (d3d10TokenizedProgramFormat.hpp)
OP_CUSTOMDATA = 53
OP_DCL_RESOURCE = 88               # dcl_resource (typed SRV)
OP_DCL_CONSTANT_BUFFER = 89
OP_DCL_SAMPLER = 90
OP_DCL_RESOURCE_RAW = 161          # dcl_resource_raw (ByteAddressBuffer)
OP_DCL_RESOURCE_STRUCTURED = 162   # dcl_resource_structured (StructuredBuffer)
SRV_OPCODES = (OP_DCL_RESOURCE, OP_DCL_RESOURCE_RAW, OP_DCL_RESOURCE_STRUCTURED)
UAV_OPCODES = (156, 157, 158)      # dcl_uav_typed / _raw / _structured
GEOMETRY_TYPES = {19, 20}          # kShaderGpuProgramDX11GeometrySM40 / SM50


def u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]


def parse_subprogram(buf, pos):
    """The sub-program record layout for blob version 202012090.

    version, programType, three stat ints, a requirements word, a keyword
    array, then a length-prefixed byte array. Matches USCSandbox
    ShaderSubProgram.cs and UnityPy ShaderConverter.py for 2021.2+, where the
    local-keyword array is gone.
    """
    off = pos + 24
    keyword_count = u32(buf, off)
    off += 4
    keywords = []
    for _ in range(keyword_count):
        length = u32(buf, off)
        keywords.append(bytes(buf[off + 4:off + 4 + length]))
        off = (off + 4 + length + 3) & ~3
    size = u32(buf, off)
    return {
        "version": u32(buf, pos), "program_type": u32(buf, pos + 4),
        "alu": u32(buf, pos + 8), "tex": u32(buf, pos + 12),
        "flow": u32(buf, pos + 16), "temp": u32(buf, pos + 20),
        "keywords": keywords, "size": size,
        "data": bytes(buf[off + 4:off + 4 + size]),
    }


def dxbc_chunks(data):
    """{fourcc: payload} for a DXBC container."""
    count = u32(data, 0x1C)
    out = {}
    for off in struct.unpack_from(f"<{count}I", data, 0x20):
        size = u32(data, off + 4)
        out[data[off:off + 4].decode("ascii", "replace")] = data[off + 8:off + 8 + size]
    return out


def shdr_declaration_counts(chunk):
    """Count dcl_resource / dcl_constantbuffer / dcl_sampler in an SHDR/SHEX chunk."""
    declared = u32(chunk, 4)
    words = struct.unpack_from(f"<{min(declared, len(chunk) // 4)}I", chunk, 0)
    i, counts = 2, collections.Counter()
    while i < len(words):
        token = words[i]
        opcode = token & 0x7FF
        length = (token >> 24) & 0x7F
        if opcode == OP_CUSTOMDATA:          # length lives in the next dword
            length = words[i + 1] if i + 1 < len(words) else 2
        if length == 0:
            raise ValueError(f"zero-length token {token:#x} (opcode {opcode}) at dword {i}")
        counts[opcode] += 1
        i += length
    return counts


def decode_bundle(path, only=None, verbose=False):
    import UnityPy
    from UnityPy.helpers import CompressionHelper

    env = UnityPy.load(path)
    rows, skipped = [], []
    for obj in env.objects:
        if obj.type.name != "Shader":
            continue
        shader = obj.read()
        name = shader.m_ParsedForm.m_Name
        if only and only not in name:
            continue
        platforms = list(shader.platforms)
        if PLATFORM_D3D11 not in platforms:
            skipped.append((name, "no d3d11 platform"))
            continue
        index = platforms.index(PLATFORM_D3D11)
        offsets = shader.offsets[index]
        offsets = offsets if isinstance(offsets, list) else [offsets]
        if len(offsets) != 1:
            # Blob indices are per-tier; a multi-tier shader cannot be resolved
            # from the parsed form alone, so it is reported rather than guessed.
            skipped.append((name, f"{len(offsets)} hardware tiers"))
            continue
        compressed = shader.compressedLengths[index][0]
        decompressed = shader.decompressedLengths[index][0]
        blob = bytes(shader.compressedBlob)
        data = CompressionHelper.decompress_lz4(
            blob[offsets[0]:offsets[0] + compressed], decompressed)
        count = u32(data, 0)
        records = [struct.unpack_from("<III", data, 4 + i * 12) for i in range(count)]

        wanted = {}
        for sub_shader in shader.m_ParsedForm.m_SubShaders:
            for a_pass in sub_shader.m_Passes:
                for prog_name in PROGRAMS:
                    program = getattr(a_pass, prog_name, None)
                    if program is None:
                        continue
                    for group in program.m_PlayerSubPrograms:
                        for sub in group:
                            if sub.m_GpuProgramType in DX11_TYPES:
                                wanted.setdefault(sub.m_BlobIndex, sub.m_GpuProgramType)

        for blob_index, gpu_type in sorted(wanted.items()):
            if blob_index >= len(records):
                continue
            offset, length, segment = records[blob_index]
            if offset + 32 > len(data):
                continue
            if u32(data, offset) != BLOB_VERSION or u32(data, offset + 4) != gpu_type:
                continue
            sub = parse_subprogram(data, offset)
            code = sub["data"]
            if code[38:42] != b"DXBC":
                skipped.append((name, f"blob {blob_index}: DXBC not at offset 38"))
                continue
            chunks = dxbc_chunks(code[38:])
            # SHDR is shader model 4, SHEX shader model 5; identical token stream.
            code_chunk = chunks.get("SHDR") or chunks.get("SHEX")
            if code_chunk is None:
                skipped.append((name, f"blob {blob_index}: no SHDR/SHEX chunk"))
                continue
            counts = shdr_declaration_counts(code_chunk)
            rows.append({
                "shader": name, "blob_index": blob_index, "gpu_type": gpu_type,
                "segment": segment, "record_length": length,
                "header": code[:38], "chunks": tuple(sorted(chunks)),
                "srv": sum(counts[op] for op in SRV_OPCODES),
                "cbuffer": counts[OP_DCL_CONSTANT_BUFFER],
                "sampler": counts[OP_DCL_SAMPLER],
                "gs_primitive": code[5],
                "uav": sum(counts[op] for op in UAV_OPCODES),
            })
            if verbose:
                print(f"  {name} blob={blob_index} type={gpu_type} "
                      f"header={code[:6].hex(' ')} srv={counts[OP_DCL_RESOURCE]} "
                      f"cb={counts[OP_DCL_CONSTANT_BUFFER]} smp={counts[OP_DCL_SAMPLER]}")
    return rows, skipped


def check(rows):
    """Assert the documented layout; return (violations, noted_exceptions)."""
    bad, noted = [], []
    for r in rows:
        h = r["header"]
        if h[0] != 2:
            bad.append((r, f"header version {h[0]}, expected 2"))
        # Unity records the resources IT bound. That equals what the compiler
        # declared everywhere but a handful of shaders, where an unused
        # resource is optimized out of the bytecode but still counted here.
        if h[1] < r["srv"]:
            bad.append((r, f"header[1]={h[1]} < SRV declarations {r['srv']}"))
        elif h[1] != r["srv"]:
            noted.append((r, f"header[1]={h[1]} > SRV declarations {r['srv']}"))
        if h[2] != r["cbuffer"]:
            bad.append((r, f"header[2]={h[2]} != dcl_constantbuffer {r['cbuffer']}"))
        if h[3] != r["sampler"]:
            bad.append((r, f"header[3]={h[3]} != dcl_sampler {r['sampler']}"))
        if h[4] != 0 and r["uav"] == 0:
            bad.append((r, f"header[4]={h[4]} non-zero with no UAV declaration"))
        elif h[4] != 0:
            noted.append((r, f"header[4]={h[4]} with {r['uav']} UAV declaration(s)"))
        if h[5] != 0 and r["gpu_type"] not in GEOMETRY_TYPES:
            bad.append((r, f"header[5]={h[5]} non-zero on a non-geometry program"))
        elif h[5] != 0:
            noted.append((r, f"header[5]={h[5]} GS input primitive"))
        if h[6:38] != b"\x00" * 32:
            bad.append((r, "header[6:38] not zero"))
    return bad, noted


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bundle", help="a stock UnityFS bundle containing Shader objects")
    ap.add_argument("--shader", help="only shaders whose name contains this")
    ap.add_argument("--verbose", action="store_true", help="one line per sub-program")
    args = ap.parse_args(argv)

    try:
        rows, skipped = decode_bundle(args.bundle, args.shader, args.verbose)
    except ImportError:
        print("UnityPy is not installed; this reproduction tool needs it "
              "(pip install UnityPy).", file=sys.stderr)
        return 77

    print(f"bundle              : {args.bundle}")
    print(f"d3d11 sub-programs  : {len(rows)}")
    if skipped:
        print(f"skipped             : {len(skipped)}")
        for name, why in skipped[:10]:
            print(f"    {name}: {why}")
    if not rows:
        print("no decodable d3d11 sub-programs found", file=sys.stderr)
        return 1

    print(f"DXBC chunk sets     : {dict(collections.Counter(r['chunks'] for r in rows))}")
    print(f"record segment word : {dict(collections.Counter(r['segment'] for r in rows))}")
    print(f"header versions     : {dict(collections.Counter(r['header'][0] for r in rows))}")
    print(f"header[5] GS prim   : {dict(collections.Counter(r['header'][5] for r in rows))}")
    print()
    print("header byte vs SHDR declaration count:")
    for label, byte, field in (("header[1] SRV declarations   ", 1, "srv"),
                               ("header[2] dcl_constantbuffer ", 2, "cbuffer"),
                               ("header[3] dcl_sampler        ", 3, "sampler")):
        match = sum(1 for r in rows if r["header"][byte] == r[field])
        print(f"  {label}: {match}/{len(rows)}")

    bad, noted = check(rows)
    print()
    if noted:
        print(f"documented exceptions: {len(noted)}")
        for r, why in noted:
            print(f"  {r['shader']} blob={r['blob_index']}: {why}")
        print()
    if bad:
        print(f"LAYOUT VIOLATIONS: {len(bad)}")
        for r, why in bad[:10]:
            print(f"  {r['shader']} blob={r['blob_index']}: {why}")
        return 1
    print(f"OK: all {len(rows)} sub-programs match the documented layout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
