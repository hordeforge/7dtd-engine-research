#!/usr/bin/env python3
"""Decode Shader (class 48) sub-program blobs from a stock UnityFS bundle.

Reproduces every measurement in docs/shader-subprogram-blob.md: the LZ4
per-platform blobs, the 12-byte record table, the sub-program header, and the
DX11 program-data header whose three count bytes are cross-checked against the
DXBC SHDR/SHEX declarations they describe.

Needs UnityPy (not a repo dependency; this is a reproduction tool, not a gate):

    uv pip install UnityPy

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
VERTEX_TYPES = {13, 15, 16}        # DX10Level9Vertex, DX11VertexSM40/SM50


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
    }, off + 4


class _Reader:
    """Little-endian reader with Unity's 4-byte string alignment."""

    def __init__(self, buf):
        self.buf, self.pos = buf, 0

    def i32(self):
        value = struct.unpack_from("<i", self.buf, self.pos)[0]
        self.pos += 4
        return value

    def u32(self):
        value = struct.unpack_from("<I", self.buf, self.pos)[0]
        self.pos += 4
        return value

    def string(self):
        n = self.i32()
        value = bytes(self.buf[self.pos:self.pos + n])
        self.pos += n
        self.pos = (self.pos + 3) & ~3
        return value


class _Writer:
    def __init__(self):
        self.out = bytearray()

    def i32(self, v):
        self.out += struct.pack("<i", v)

    def u32(self, v):
        self.out += struct.pack("<I", v)

    def string(self, v):
        self.i32(len(v))
        self.out += v
        while len(self.out) % 4:
            self.out += b"\x00"


def _read_cb_param(r):
    return {"name": r.string(), "type": r.i32(), "rows": r.i32(), "columns": r.i32(),
            "is_matrix": r.i32(), "array_size": r.i32(), "index": r.i32()}


def _write_cb_param(w, p):
    w.string(p["name"])
    for key in ("type", "rows", "columns", "is_matrix", "array_size", "index"):
        w.i32(p[key])


def _read_struct_param(r):
    s = {"name": r.string(), "index": r.i32(), "array_size": r.i32(), "size": r.i32()}
    s["params"] = [_read_cb_param(r) for _ in range(r.i32())]
    return s


def _write_struct_param(w, s):
    w.string(s["name"])
    for key in ("index", "array_size", "size"):
        w.i32(s[key])
    w.i32(len(s["params"]))
    for p in s["params"]:
        _write_cb_param(w, p)


def _read_constant_buffer(r):
    cb = {"name": r.string(), "used_size": r.i32()}
    cb["params"] = [_read_cb_param(r) for _ in range(r.i32())]
    cb["structs"] = [_read_struct_param(r) for _ in range(r.i32())]
    return cb


def _write_constant_buffer(w, cb):
    w.string(cb["name"])
    w.i32(cb["used_size"])
    w.i32(len(cb["params"]))
    for p in cb["params"]:
        _write_cb_param(w, p)
    w.i32(len(cb["structs"]))
    for s in cb["structs"]:
        _write_struct_param(w, s)


# Unity's vertex bind channels: `source` is the mesh channel the engine
# reads, `target` the shader input it feeds. Derived by correlating each
# stock vertex blob's channel list against its own DXBC input signature.
BIND_CHANNEL_SOURCES = {
    ("POSITION", 0): (0, 0),
    ("NORMAL", 0): (1, 1),
    ("TANGENT", 0): (2, 2),
    ("COLOR", 0): (3, 3),
}


def parse_bind_channels(raw):
    """Decode the `ParserBindChannels` block that closes a code-blob record."""
    source_map, count = struct.unpack_from("<ii", raw, 0)
    channels = [struct.unpack_from("<ii", raw, 8 + i * 8) for i in range(count)]
    return {"source_map": source_map, "channels": channels}, 8 + count * 8


def input_semantics(dxbc):
    """`(semantic, index)` per element of a DXBC input signature."""
    isgn = dxbc_chunks(dxbc).get("ISGN")
    if isgn is None:
        return []
    out = []
    for i in range(u32(isgn, 0)):
        name_offset, index = struct.unpack_from("<II", isgn, 8 + i * 24)
        out.append((isgn[name_offset:isgn.index(b"\x00", name_offset)].decode("ascii"), index))
    return out


def expected_channels(dxbc):
    """The channel list a vertex program's input signature implies."""
    channels = []
    for semantic, index in input_semantics(dxbc):
        if semantic == "TEXCOORD":
            channels.append((4 + index, 5 + index))
        elif (semantic, index) in BIND_CHANNEL_SOURCES:
            channels.append(BIND_CHANNEL_SOURCES[(semantic, index)])
    return channels


def parse_parameter_blob(raw):
    """Decode a parameter blob; returns (fields, bytes consumed).

    Layout per USCSandbox ShaderParams.cs with readBlobVersion=true.
    """
    r = _Reader(raw)
    version = r.i32()
    buffers = [_read_constant_buffer(r) for _ in range(r.i32())]
    entries = []
    for _ in range(r.i32()):
        name = r.string()
        kind = r.i32()
        if kind == 0:      # texture
            e = {"kind": 0, "name": name, "index": r.i32(),
                 "sampler_index": r.i32(), "extra": r.u32()}
        elif kind in (1, 2):   # constant-buffer binding / buffer binding
            e = {"kind": kind, "name": name, "index": r.i32(), "array_size": r.i32()}
        elif kind == 3:    # UAV
            e = {"kind": 3, "name": name, "index": r.i32(), "original_index": r.i32()}
        elif kind == 4:    # sampler
            e = {"kind": 4, "name": name, "bind_point": r.i32(), "sampler": r.u32()}
        else:
            raise ValueError(f"unknown parameter kind {kind}")
        entries.append(e)
    return {"version": version, "buffers": buffers, "entries": entries}, r.pos


def build_parameter_blob(fields):
    """Re-emit a parameter blob. Round-trips stock blobs byte for byte."""
    w = _Writer()
    w.i32(fields["version"])
    w.i32(len(fields["buffers"]))
    for cb in fields["buffers"]:
        _write_constant_buffer(w, cb)
    w.i32(len(fields["entries"]))
    for e in fields["entries"]:
        w.string(e["name"])
        w.i32(e["kind"])
        if e["kind"] == 0:
            w.i32(e["index"])
            w.i32(e["sampler_index"])
            w.u32(e["extra"])
        elif e["kind"] in (1, 2):
            w.i32(e["index"])
            w.i32(e["array_size"])
        elif e["kind"] == 3:
            w.i32(e["index"])
            w.i32(e["original_index"])
        elif e["kind"] == 4:
            w.i32(e["bind_point"])
            w.u32(e["sampler"])
    return bytes(w.out)


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
    rows, skipped, parameters = [], [], []
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
        parameter_indices = set()
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
                    # m_ParameterBlobIndices runs PARALLEL to the sub-program
                    # list, which mixes platforms; a position's parameter blob
                    # lives in the same platform blob as its sub-program, so
                    # only the d3d11 positions index this table.
                    for gi, group in enumerate(program.m_ParameterBlobIndices):
                        subs = (program.m_PlayerSubPrograms[gi]
                                if gi < len(program.m_PlayerSubPrograms) else [])
                        for k, idx in enumerate(group):
                            if k < len(subs) and subs[k].m_GpuProgramType in DX11_TYPES:
                                parameter_indices.add(int(idx))

        for blob_index, gpu_type in sorted(wanted.items()):
            if blob_index >= len(records):
                continue
            offset, length, segment = records[blob_index]
            if offset + 32 > len(data):
                continue
            if u32(data, offset) != BLOB_VERSION or u32(data, offset + 4) != gpu_type:
                continue
            sub, data_offset = parse_subprogram(data, offset)
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
            data_end = (data_offset + sub["size"] + 3) & ~3
            trailing = bytes(data[data_end:offset + length])
            channels = None
            if len(trailing) >= 8:
                channels, _consumed = parse_bind_channels(trailing)
            rows.append({
                "shader": name, "blob_index": blob_index, "gpu_type": gpu_type,
                "segment": segment, "record_length": length,
                "header": code[:38], "chunks": tuple(sorted(chunks)),
                "srv": sum(counts[op] for op in SRV_OPCODES),
                "cbuffer": counts[OP_DCL_CONSTANT_BUFFER],
                "sampler": counts[OP_DCL_SAMPLER],
                "gs_primitive": code[5],
                "trailing": len(trailing),
                "channels": channels,
                "expected_channels": expected_channels(code[38:]),
                "uav": sum(counts[op] for op in UAV_OPCODES),
            })
            if verbose:
                print(f"  {name} blob={blob_index} type={gpu_type} "
                      f"header={code[:6].hex(' ')} srv={counts[OP_DCL_RESOURCE]} "
                      f"cb={counts[OP_DCL_CONSTANT_BUFFER]} smp={counts[OP_DCL_SAMPLER]}")
        for blob_index in sorted(parameter_indices):
            if blob_index >= len(records):
                continue
            offset, length, _segment = records[blob_index]
            raw = bytes(data[offset:offset + length])
            if len(raw) < 8 or u32(raw, 0) != BLOB_VERSION:
                continue
            try:
                fields, consumed = parse_parameter_blob(raw)
            except Exception as exc:
                parameters.append({"shader": name, "blob_index": blob_index,
                                   "status": f"parse failed: {exc}"})
                continue
            rebuilt = build_parameter_blob(fields)
            exact = rebuilt == raw[:len(rebuilt)] and consumed == len(rebuilt)
            parameters.append({
                "shader": name, "blob_index": blob_index,
                "status": "exact" if exact else "re-emit differs",
                "trailing": len(raw) - consumed,
                "buffers": len(fields["buffers"]), "entries": len(fields["entries"]),
                "kinds": collections.Counter(e["kind"] for e in fields["entries"]),
            })

    return rows, skipped, parameters


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
        # Every code-blob record closes with a ParserBindChannels block. A
        # record that lacks it is short by at least those eight bytes, and the
        # runtime refuses the program rather than mis-drawing it.
        if r["channels"] is None:
            bad.append((r, f"no ParserBindChannels block ({r['trailing']} trailing bytes)"))
            continue
        got = [tuple(c) for c in r["channels"]["channels"]]
        # sourceMap is a stored base mask, not a checksum of the channel list:
        # USCSandbox ORs each channel's source bit into it after reading, so
        # the stored value can name channels the program does not bind. The
        # invariant that does hold is containment.
        source_map = 0
        for source, _target in got:
            source_map |= 1 << source
        if r["channels"]["source_map"] & source_map != source_map:
            bad.append((r, (f"sourceMap {r['channels']['source_map']} omits a bound channel "
                            f"(channels imply {source_map})")))
        # A vertex program binds a SUBSET of what its signature declares:
        # only the inputs it actually reads get a channel. Every bound pair
        # must still be one the semantic mapping predicts.
        if r["gpu_type"] in VERTEX_TYPES:
            unexpected = [c for c in got if c not in r["expected_channels"]]
            if unexpected:
                bad.append((r, (f"channels {unexpected} not derivable from the input "
                                f"signature {r['expected_channels']}")))
    return bad, noted


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bundle", help="a stock UnityFS bundle containing Shader objects")
    ap.add_argument("--shader", help="only shaders whose name contains this")
    ap.add_argument("--verbose", action="store_true", help="one line per sub-program")
    args = ap.parse_args(argv)

    try:
        rows, skipped, parameters = decode_bundle(args.bundle, args.shader, args.verbose)
    except ImportError:
        print("UnityPy is not installed; this reproduction tool needs it "
              "(uv pip install UnityPy).", file=sys.stderr)
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
    print(f"bind-channel counts : {dict(collections.Counter(len(r['channels']['channels']) if r['channels'] else -1 for r in rows))}")
    print(f"header versions     : {dict(collections.Counter(r['header'][0] for r in rows))}")
    print(f"header[5] GS prim   : {dict(collections.Counter(r['header'][5] for r in rows))}")
    print()
    print("header byte vs SHDR declaration count:")
    for label, byte, field in (("header[1] SRV declarations   ", 1, "srv"),
                               ("header[2] dcl_constantbuffer ", 2, "cbuffer"),
                               ("header[3] dcl_sampler        ", 3, "sampler")):
        match = sum(1 for r in rows if r["header"][byte] == r[field])
        print(f"  {label}: {match}/{len(rows)}")

    if parameters:
        exact = sum(1 for p in parameters if p["status"] == "exact")
        kinds = collections.Counter()
        for p in parameters:
            kinds.update(p.get("kinds", {}))
        print()
        print(f"parameter blobs      : {len(parameters)}")
        print(f"  re-emitted exactly : {exact}/{len(parameters)}")
        print(f"  trailing bytes     : {dict(collections.Counter(p.get('trailing') for p in parameters))}")
        print(f"  entry kinds        : {dict(kinds)}  (0 texture, 1 cbuffer-binding, 2 buffer, 3 UAV, 4 sampler)")
        for p in parameters:
            if p["status"] != "exact":
                print(f"  PARAMETER BLOB FAIL {p['shader']} blob={p['blob_index']}: {p['status']}")

    bad, noted = check(rows)
    print()
    if noted:
        print(f"documented exceptions: {len(noted)}")
        for r, why in noted:
            print(f"  {r['shader']} blob={r['blob_index']}: {why}")
        print()
    param_bad = [p for p in parameters if p["status"] != "exact"]
    if bad or param_bad:
        print(f"LAYOUT VIOLATIONS: {len(bad)} header, {len(param_bad)} parameter blob")
        for r, why in bad[:10]:
            print(f"  {r['shader']} blob={r['blob_index']}: {why}")
        return 1
    print(f"OK: {len(rows)} sub-programs match the documented layout; "
          f"{len(parameters)} parameter blobs re-emitted byte for byte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
