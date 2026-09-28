#!/usr/bin/env python3
"""Seeded mutation fuzzer for the byte-level decoders in shader_blob_dump.py.

The sub-program and parameter blobs come out of a stock UnityFS bundle: a
half-copied bundle, a shader from another Unity version, or a truncated
download hands them to the decoder as raw bytes, and every length, count, and
offset inside them is file-controlled. The container is not part of the corpus
here (that needs UnityPy and a live install), so the seeds are the record
shapes themselves, built with the same field layouts the decoders document.

  1. Nothing but ShaderBlobError escapes a decoder. A string length that ran
     backwards, a count of 0xFFFFFFFF, and a DXBC offset pointing past the
     container all used to reach struct.unpack_from or a Python range.
  2. Per-call time budget: a file-controlled count must not turn into a
     minutes-long walk before the next bounds check.
  3. No amplification: a record list is never longer than the bytes that could
     hold it, so a decoder cannot be made to allocate from a 4-byte field.
  4. Round-trip and determinism: a parameter blob re-emits byte for byte, and
     re-emitting a decoded blob is a fixed point, so a decode cannot drift
     between runs or between a read and a write.

Seeds are structure-aware: a real sub-program header, a DXBC container with an
ISGN input signature and an SHDR token stream, parameter blobs carrying
constant buffers, nested structs, and all five entry kinds, and a
ParserBindChannels block. Mutations are bit flips, truncation, count/length
inflation, and sign flips on the length fields. Deterministic, stdlib-only,
DLL-free, seconds to run.

Usage: python3 tools/tests/test_shader_blob_fuzz.py
"""

from __future__ import annotations

import os
import random
import struct
import sys
import time
from collections.abc import Callable
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

sys.path.insert(0, str(_common.TOOLS))

import shader_blob_dump as src

Fields = dict[str, Any]
SEED = 0x5BADE7B0
ROUNDS = 300  # mutation rounds per target family
TIME_BUDGET_S = 5.0  # hard ceiling for ONE decoder call (hang-class guard)

Decoder = Callable[[bytes], object]


class BudgetError(Exception):
    pass


def timed(call: Decoder, data: bytes) -> object:
    t0 = time.monotonic()
    result = call(data)
    if time.monotonic() - t0 >= TIME_BUDGET_S:
        raise BudgetError(f"call took more than {TIME_BUDGET_S}s")
    return result


# --- seeds -----------------------------------------------------------------


def dxbc(chunks: list[tuple[bytes, bytes]]) -> bytes:
    """A DXBC container: magic, 16-byte hash, version, size, count, offsets."""
    table = 0x20 + 4 * len(chunks)
    body = b""
    offsets = bytearray()
    off = table
    for fourcc, payload in chunks:
        offsets += struct.pack("<I", off)
        body += fourcc + struct.pack("<I", len(payload)) + payload
        off += 8 + len(payload)
    head = b"DXBC" + bytes(16) + struct.pack("<III", 1, 0, len(chunks))
    return head + bytes(offsets) + body


def isgn(semantics: list[tuple[bytes, int]]) -> bytes:
    """A DXBC ISGN chunk: element count, 24-byte elements, then the names."""
    table = 8 + 24 * len(semantics)
    entries = b""
    names = b""
    for name, index in semantics:
        entries += struct.pack("<II4I", table + len(names), index, *([0] * 4))
        names += name + b"\x00"
    return struct.pack("<II", len(semantics), 0) + entries + names


def shdr(tokens: list[tuple[int, list[int]]]) -> bytes:
    """A DXBC SHDR chunk: two header dwords, then length-prefixed tokens."""
    words: list[int] = []
    for opcode, operands in tokens:
        words.append(((1 + len(operands)) << 24) | opcode)
        words.extend(operands)
    body = b"".join(struct.pack("<I", w) for w in words)
    return struct.pack("<II", 8 + len(body), len(words)) + body


def code_blob() -> bytes:
    """The bytes a stock d3d11 sub-program carries: header, DXBC, bind channels."""
    container = dxbc(
        [
            (
                b"ISGN",
                isgn([(b"POSITION", 0), (b"NORMAL", 0), (b"TEXCOORD", 0), (b"TEXCOORD", 1)]),
            ),
            (
                b"SHDR",
                shdr(
                    [
                        (src.OP_DCL_RESOURCE, [0, 0, 0]),
                        (src.OP_DCL_RESOURCE_RAW, [0, 0, 0]),
                        (src.OP_DCL_CONSTANT_BUFFER, [0, 16, 0]),
                        (src.OP_DCL_SAMPLER, [0, 0]),
                    ]
                ),
            ),
        ]
    )
    header = bytes([2, 2, 1, 1, 0]) + bytes(33)
    return header + container


def unaligned_string(value: bytes) -> bytes:
    """The length-prefixed, 4-byte-aligned string the sub-program header carries."""
    out = struct.pack("<i", len(value)) + value
    return out + b"\x00" * (-len(out) % 4)


def subprogram(prog_type: int = 14, keywords: int = 1, body: bytes | None = None) -> bytes:
    data = code_blob() if body is None else body
    out = b"".join(
        struct.pack("<I", word) for word in (src.BLOB_VERSION, prog_type, 12, 3, 4, 5, keywords)
    )
    out += b"".join(unaligned_string(b"MAINLIGHT" + bytes([i])) for i in range(keywords))
    out += struct.pack("<I", len(data)) + data
    return out + b"\x00" * (-len(out) % 4)


def cb_param(name: bytes, rows: int = 1, columns: int = 4) -> Fields:
    return {
        "name": name,
        "type": 2,
        "rows": rows,
        "columns": columns,
        "is_matrix": 0,
        "array_size": 0,
        "index": 0,
    }


def parameter_blob(entries: list[Fields], buffers: list[Fields] | None = None) -> bytes:
    fields: Fields = {
        "version": src.BLOB_VERSION,
        "buffers": buffers
        if buffers is not None
        else [
            {
                "name": b"_UnityPerDraw",
                "used_size": 96,
                "params": [cb_param(b"unity_ObjectToWorld"), cb_param(b"unity_WorldToObject")],
                "structs": [
                    {
                        "name": b"ShadowClip",
                        "index": 0,
                        "array_size": 1,
                        "size": 16,
                        "params": [cb_param(b"plane", rows=4)],
                    }
                ],
            }
        ],
        "entries": entries,
    }
    return src.build_parameter_blob(fields)


def entry(kind: int) -> Fields:
    if kind == 0:
        return {"kind": 0, "name": b"_MainTex", "index": 0, "sampler_index": 0, "extra": 0}
    if kind in (1, 2):
        return {"kind": kind, "name": b"_UnityPerDraw", "index": 0, "array_size": 1}
    if kind == 3:
        return {"kind": 3, "name": b"_RWBuffer", "index": 0, "original_index": 0}
    return {"kind": 4, "name": b"linear_clamp_sampler", "bind_point": 0, "sampler": 0}


def bind_channels(pairs: list[tuple[int, int]], source_map: int | None = None) -> bytes:
    if source_map is None:
        source_map = 0
        for source, _target in pairs:
            source_map |= 1 << source
    out = struct.pack("<ii", source_map, len(pairs))
    for pair in pairs:
        out += struct.pack("<ii", *pair)
    return out


# --- targets ----------------------------------------------------------------

TARGETS: dict[str, tuple[Decoder, list[bytes]]] = {
    "subprogram": (lambda d: src.parse_subprogram(d, 0), [subprogram(), subprogram(13, 3)]),
    "parameter": (
        lambda d: src.parse_parameter_blob(d),
        [
            parameter_blob([entry(k) for k in range(5)]),
            parameter_blob([], []),
            parameter_blob([entry(0)], buffers=[]),
        ],
    ),
    "dxbc": (
        lambda d: src.dxbc_chunks(d),
        [dxbc([(b"ISGN", isgn([(b"POSITION", 0)]))]), dxbc([]), code_blob()[38:]],
    ),
    "isgn": (lambda d: src.input_semantics(d), [code_blob()[38:], dxbc([])]),
    "expected_channels": (lambda d: src.expected_channels(d), [code_blob()[38:]]),
    "shdr": (
        lambda d: src.shdr_declaration_counts(d),
        [
            shdr([(src.OP_DCL_RESOURCE, [0, 0, 0]), (src.OP_DCL_SAMPLER, [0, 0])]),
            shdr([(src.OP_CUSTOMDATA, [0, 0, 4, 7, 5, 0, 0, 0]), (src.OP_DCL_SAMPLER, [0, 0])]),
        ],
    ),
    "bind_channels": (
        lambda d: src.parse_bind_channels(d),
        [bind_channels([(0, 0), (1, 1), (4, 5), (5, 6)]), bind_channels([])],
    ),
}


def mutate(rng: random.Random, data: bytes) -> bytes:
    b = bytearray(data if data else b"\x00")
    for _ in range(rng.randint(1, 8)):
        op = rng.choice(("flip", "set", "trunc", "grow", "count", "sign", "pointer"))
        if op == "flip":
            b[rng.randrange(len(b))] ^= 1 << rng.randrange(8)
        elif op == "set":
            b[rng.randrange(len(b))] = rng.randrange(256)
        elif op == "trunc":
            del b[rng.randrange(len(b)) :]
        elif op == "grow":
            b += bytes(rng.randrange(256) for _ in range(rng.randint(1, 64)))
        elif op == "count":
            i = rng.randrange(0, max(1, len(b) - 3)) & ~3
            b[i : i + 4] = struct.pack("<I", rng.choice((0xFFFFFFFF, 0x7FFFFFFF, 0x10000000)))
        elif op == "sign":
            i = rng.randrange(0, max(1, len(b) - 3)) & ~3
            b[i : i + 4] = struct.pack("<i", -rng.randint(1, 0x40000000))
        elif op == "pointer":
            i = rng.randrange(0, max(1, len(b) - 3)) & ~3
            b[i : i + 4] = struct.pack("<I", rng.choice((0xFFFFFFFF, 0x7FFFFFFF, len(b))))
        if not b:
            b += bytes([rng.randrange(256)])  # keep later ops indexable
    return bytes(b)


# --- invariants -------------------------------------------------------------


# The decoders return different record shapes (Fields, list, tuple, Counter);
# the invariant each target asserts is named in the branch that checks it.
def check_amplification(name: str, data: bytes, parsed: Any, bad: list[str]) -> None:
    """A record list can never be longer than the bytes that could hold it."""
    limit = len(data) // 12 + 1
    lists: list[int] = []
    if name == "subprogram":
        fields, _pos = parsed
        lists.append(len(fields["keywords"]))
    elif name == "parameter":
        fields, _consumed = parsed
        lists.append(len(fields["entries"]))
        for cb in fields["buffers"]:
            lists.append(len(cb["params"]))
            lists.append(len(cb["structs"]))
            for s in cb["structs"]:
                lists.append(len(s["params"]))
    elif name == "dxbc":
        lists.append(len(parsed))
    elif name == "bind_channels":
        lists.append(len(parsed[0]["channels"]))
    for got in lists:
        if got > limit:
            bad.append(f"{name}: {got} records decoded from {len(data)} bytes (limit {limit})")


def check_roundtrip(name: str, data: bytes, parsed: Any, bad: list[str]) -> None:
    if name != "parameter":
        return
    fields, consumed = parsed
    rebuilt = src.build_parameter_blob(fields)
    if len(rebuilt) != consumed:
        bad.append(
            f"parameter: {len(data)}-byte blob re-emits as {len(rebuilt)} bytes, "
            f"parse consumed {consumed}"
        )
    again, consumed_again = src.parse_parameter_blob(rebuilt)
    if consumed_again != len(rebuilt) or src.build_parameter_blob(again) != rebuilt:
        bad.append("parameter: re-emitting a decoded blob is not a fixed point")


def fuzz(rng: random.Random, bad: list[str]) -> None:
    for name, (decode, seeds) in sorted(TARGETS.items()):
        for k in range(ROUNDS):
            data = mutate(rng, rng.choice(seeds)) if rng.random() < 0.85 else seeds[k % len(seeds)]
            label = f"{name} round {k}"
            try:
                parsed = timed(decode, data)
            except BudgetError as exc:
                bad.append(f"{label}: {exc}")
                return
            except src.ShaderBlobError:
                continue  # the documented fail-closed verdict for a bad blob
            except Exception as exc:
                bad.append(f"{label}: ESCAPED {type(exc).__name__}: {exc}")
                return
            check_amplification(name, data, parsed, bad)
            check_roundtrip(name, data, parsed, bad)
            if bad:
                return
            if timed(decode, data) != parsed:
                bad.append(f"{label}: decode is not deterministic")
                return


def valid_seeds(bad: list[str]) -> None:
    """Pair side of every pin: a well-formed blob must still decode unchanged."""
    fields, consumed = src.parse_parameter_blob(parameter_blob([entry(k) for k in range(5)]))
    raw = parameter_blob([entry(k) for k in range(5)])
    if consumed != len(raw) or src.build_parameter_blob(fields) != raw:
        bad.append("seed: a valid parameter blob did not re-emit byte for byte")
    if len(fields["entries"]) != 5 or len(fields["buffers"][0]["structs"]) != 1:
        bad.append("seed: valid parameter blob lost entries or structs")
    sub, pos = src.parse_subprogram(subprogram(), 0)
    if len(sub["data"]) != sub["size"] or pos <= 0:
        bad.append(f"seed: sub-program size {sub['size']} vs data {len(sub['data'])}")
    if sub["version"] != src.BLOB_VERSION or sub["keywords"] != [b"MAINLIGHT\x00"]:
        bad.append(f"seed: sub-program header decoded as {sub}")
    if src.input_semantics(code_blob()[38:]) != [
        ("POSITION", 0),
        ("NORMAL", 0),
        ("TEXCOORD", 0),
        ("TEXCOORD", 1),
    ]:
        bad.append("seed: input signature did not decode")
    if src.expected_channels(code_blob()[38:]) != [(0, 0), (1, 1), (4, 5), (5, 6)]:
        bad.append("seed: expected channels did not follow the signature")
    counts = src.shdr_declaration_counts(
        shdr([(src.OP_DCL_RESOURCE, [0, 0, 0]), (src.OP_DCL_SAMPLER, [0, 0])])
    )
    if counts[src.OP_DCL_RESOURCE] != 1 or counts[src.OP_DCL_SAMPLER] != 1:
        bad.append(f"seed: SHDR counts decoded as {counts}")
    channels, used = src.parse_bind_channels(bind_channels([(0, 0), (1, 1)]))
    if used != 24 or [tuple(c) for c in channels["channels"]] != [(0, 0), (1, 1)]:
        bad.append(f"seed: bind channels decoded as {channels} in {used} bytes")


def regression_pins(bad: list[str]) -> None:
    """Pin the escapes these decoders had, so a re-loosening shows up as a red gate."""
    pins: list[tuple[str, bytes]] = [
        # A keyword string whose length runs backwards: the position used to
        # rewind and the record walk ran off the front of the buffer.
        (
            "negative string length",
            struct.pack("<IIIIIIIi", src.BLOB_VERSION, 14, 0, 0, 0, 0, 1, -1),
        ),
        # A sub-program whose data size runs past the end of the blob.
        ("sub-program size", struct.pack("<IIIIIIII", src.BLOB_VERSION, 14, 0, 0, 0, 0, 0, 0xFFFF)),
        # A keyword count of 0xFFFFFFFF: an unbounded walk over garbage.
        ("keyword count", struct.pack("<IIIIIII", src.BLOB_VERSION, 14, 0, 0, 0, 0, 0xFFFFFFFF)),
        # A constant-buffer count larger than the blob can hold.
        ("buffer count", struct.pack("<ii", src.BLOB_VERSION, 0xFFFFFF)),
        # A parameter entry of a kind the format does not define.
        ("entry kind 7", struct.pack("<iii4s", src.BLOB_VERSION, 0, 0x7FFFFFF0, b"zzzz")),
        # A DXBC chunk table that claims more chunks than the container holds.
        ("DXBC count", b"DXBC" + bytes(16) + struct.pack("<III", 1, 0, 0xFFFF)),
        # A DXBC chunk offset pointing past the end of the container.
        (
            "DXBC offset",
            b"DXBC" + bytes(16) + struct.pack("<III", 1, 0, 1) + struct.pack("<I", 0xFFFF),
        ),
        # A bind-channel count larger than the trailing block holds.
        ("bind channels", struct.pack("<ii", 3, 0x1000)),
        # An ISGN element whose name offset points past the chunk.
        (
            "ISGN offset",
            dxbc(
                [(b"ISGN", struct.pack("<II", 1, 0) + struct.pack("<II4I", 0xFFFF, 0, *([0] * 4)))]
            ),
        ),
        # An ISGN element whose name is not NUL-terminated.
        (
            "ISGN name",
            dxbc(
                [
                    (
                        b"ISGN",
                        struct.pack("<II", 1, 0) + struct.pack("<II4I", 40, 0, *([0] * 4)) + b"POS",
                    )
                ]
            ),
        ),
    ]
    decoders: dict[str, Decoder] = {
        "negative string length": lambda d: src.parse_subprogram(d, 0),
        "sub-program size": lambda d: src.parse_subprogram(d, 0),
        "keyword count": lambda d: src.parse_subprogram(d, 0),
        "buffer count": lambda d: src.parse_parameter_blob(d),
        "entry kind 7": lambda d: src.parse_parameter_blob(d),
        "DXBC count": lambda d: src.dxbc_chunks(d),
        "DXBC offset": lambda d: src.dxbc_chunks(d),
        "bind channels": lambda d: src.parse_bind_channels(d),
        "ISGN offset": lambda d: src.input_semantics(d),
        "ISGN name": lambda d: src.input_semantics(d),
    }
    for label, data in pins:
        try:
            decoded = decoders[label](data)
        except src.ShaderBlobError:
            continue
        except Exception as exc:
            bad.append(f"{label}: raised {type(exc).__name__} instead of ShaderBlobError: {exc}")
            continue
        bad.append(f"{label}: decoded as {decoded!r} instead of failing closed")


def main() -> int:
    rng = random.Random(SEED)
    bad: list[str] = []
    valid_seeds(bad)
    if not bad:
        fuzz(rng, bad)
    if not bad:
        regression_pins(bad)
    if bad:
        print("FAIL: shader_blob_dump fuzz")
        for b in bad:
            print("  - " + b)
        return 1
    print(
        f"OK: {ROUNDS} mutation rounds over {len(TARGETS)} decoder families; "
        "no escapes, hangs, amplification, or round-trip drift"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
