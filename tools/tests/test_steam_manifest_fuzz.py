#!/usr/bin/env python3
"""Seeded mutation fuzzer for the hand-rolled protobuf reader in steam_manifest.py.

`<steam>/depotcache/294422_<gid>.manifest` is a plaintext protobuf Steam writes
itself, and it is untrusted input here: a half-written download, a truncated
copy, or a file from a different depot version reaches `read_manifest` as raw
bytes. The reader is hand-rolled (varint, wire types 0/1/2/5), so every field
shape it can be handed is attacker-chosen. `test_steam_manifest.py` pins
specific malformations; this gate covers the space between them:

  1. Nothing but ManifestError escapes read_manifest. A truncated fixed-width
     field used to reach struct.unpack_from and raise struct.error, which no
     caller catches (it is a crash, not a verdict).
  2. Per-call time budget: a file-controlled varint must not turn into an
     unbounded big-int shift loop.
  3. Entry invariants on every successful parse: name non-empty, size/flags
     non-negative, sha1 lowercase hex of 40 chars or absent, chunk count
     non-negative, and the table length arithmetic must agree with the file.
  4. Determinism: identical bytes yield identical entries.

Seeds are structure-aware (valid manifests built by the encoder below, with
whole-file and per-chunk SHA-1 rows, empty and multi-chunk entries), so the
mutations explore around true shapes rather than random noise. Deterministic,
stdlib-only, DLL-free, network-free, seconds to run.

Usage: python3 tools/tests/test_steam_manifest_fuzz.py
"""

from __future__ import annotations

import hashlib
import os
import random
import struct
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

sys.path.insert(0, str(_common.TOOLS / "steam"))
import steam_manifest as src

SEED = 0x71F617D0
ROUNDS = 240  # mutation rounds per seed family
TIME_BUDGET_S = 5.0  # hard ceiling for ONE parse (hang-class guard)
HEX = frozenset("0123456789abcdef")


def varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(out)


def field_bytes(number: int, payload: bytes) -> bytes:
    return varint((number << 3) | 2) + varint(len(payload)) + payload


def field_varint(number: int, value: int) -> bytes:
    return varint(number << 3) + varint(value)


def entry(name: str, data: bytes, flags: int = 0, chunks: int = 1) -> bytes:
    blob = field_bytes(1, name.encode())
    blob += field_varint(2, len(data))
    blob += field_varint(3, flags)
    if data or chunks:
        blob += field_bytes(5, hashlib.sha1(data).digest())
    for _ in range(chunks):
        chunk = field_bytes(1, hashlib.sha1(data).digest())
        chunk += struct.pack("<BI", (2 << 3) | 5, len(data))
        chunk += field_varint(3, 0) + field_varint(4, len(data)) + field_varint(5, len(data))
        blob += field_bytes(6, chunk)
    return field_bytes(1, blob)


def manifest(entries: list[bytes], trailer: bytes = b"\x00" * 70) -> bytes:
    table = b"".join(entries)
    return struct.pack("<II", src.MAGIC, len(table)) + table + trailer


def seed_manifests() -> list[bytes]:
    """True shapes: real entries with whole-file and per-chunk SHA-1 rows."""
    small = b"steady stock bytes\n"
    return [
        manifest(
            [
                entry("Data\\Managed\\Assembly-CSharp.dll", small * 40, flags=1024, chunks=2),
                entry("Data\\note.txt", b"", chunks=0),
            ]
        ),
        manifest(
            [
                entry(f"Data\\Managed\\Mod.{i}.dll", bytes([i]) * 900, chunks=1 + i)
                for i in range(1, 6)
            ],
            trailer=b"",
        ),
        manifest([entry("Data", b"x", chunks=0)], trailer=b"\xff" * 8),
    ]


def mutate(rng: random.Random, data: bytes) -> bytes:
    b = bytearray(data if data else b"\x00")
    for _ in range(rng.randint(1, 8)):
        op = rng.choice(("flip", "set", "trunc", "grow", "length", "wire", "varint"))
        if op == "flip":
            b[rng.randrange(len(b))] ^= 1 << rng.randrange(8)
        elif op == "set":
            b[rng.randrange(len(b))] = rng.randrange(256)
        elif op == "trunc":
            del b[rng.randrange(len(b)) :]
        elif op == "grow":
            b += bytes(rng.randrange(256) for _ in range(rng.randint(1, 64)))
        elif op == "length":
            i = rng.randrange(8, max(9, len(b)))
            b[i : i + 4] = struct.pack(
                "<I", rng.choice((0x7FFFFFFF, 0xFFFFFFFF, 0x00FFFFFF, len(b)))
            )
        elif op == "wire":
            b[rng.randrange(len(b))] = rng.randrange(256) & 0x0F  # key low nibble = wire type
        elif op == "varint":
            i = rng.randrange(len(b))
            b[i : i + 1] = b"\x80" * rng.randint(1, 24)  # overlong / unterminated varint
        if not b:
            b += bytes([rng.randrange(256)])  # keep later ops indexable
    return bytes(b)


class BudgetError(Exception):
    pass


def timed(call: Callable[[], object]) -> None:
    t0 = time.monotonic()
    call()
    dt = time.monotonic() - t0
    if dt >= TIME_BUDGET_S:
        raise BudgetError(f"call took {dt:.1f}s (budget {TIME_BUDGET_S}s)")


def parse(data: bytes, path: Path) -> src.Manifest:
    path.write_bytes(data)
    timed(lambda: src.read_manifest(path))
    return src.read_manifest(path)


def check_invariants(data: bytes, parsed: src.Manifest, label: str, bad: list[str]) -> None:
    if not parsed.entries:
        bad.append(f"{label}: parse succeeded with zero entries")
        return
    table_end = 8 + struct.unpack_from("<I", data, 4)[0]
    if table_end > len(data) or parsed.trailer != len(data) - table_end:
        bad.append(
            f"{label}: trailer {parsed.trailer} disagrees with "
            f"declared table {table_end} vs file {len(data)}"
        )
    for e in parsed.entries:
        if not e.name:
            bad.append(f"{label}: entry with empty name survived: {e}")
        if e.size < 0 or e.flags < 0 or e.chunks < 0:
            bad.append(f"{label}: negative field: {e}")
        if e.sha1 is not None and (len(e.sha1) != 40 or not set(e.sha1) <= HEX):
            bad.append(f"{label}: sha1 is not 40 lowercase hex chars: {e.sha1!r}")


def fuzz(seeds: list[bytes], path: Path, rng: random.Random, bad: list[str]) -> None:
    for k in range(ROUNDS):
        data = mutate(rng, rng.choice(seeds)) if rng.random() < 0.85 else seeds[k % len(seeds)]
        label = f"round {k}"
        try:
            parsed = parse(data, path)
        except BudgetError as exc:
            bad.append(f"{label}: {exc}")
            return
        except src.ManifestError:
            continue  # the documented fail-closed verdict for a bad manifest
        except Exception as exc:
            bad.append(f"{label}: ESCAPED {type(exc).__name__}: {exc}")
            return
        check_invariants(data, parsed, label, bad)
        if bad:
            return
        again = src.read_manifest(path)
        if again.entries != parsed.entries or again.trailer != parsed.trailer:
            bad.append(f"{label}: parse is not deterministic")
            return


def regression_pins(path: Path, bad: list[str]) -> None:
    """Pin the two escapes this reader had, plus the invariants a real parse keeps."""
    # A wire-5 field whose payload is cut short: struct.error used to escape.
    table = varint(1 << 3 | 2) + varint(6) + b"\x0a\x02hi" + struct.pack("<BI", 2 << 3 | 5, 9)
    truncated = struct.pack("<II", src.MAGIC, len(table)) + table
    try:
        src.read_manifest(_write(path, truncated))
        bad.append("trunc32: short fixed32 field parsed instead of failing closed")
    except src.ManifestError:
        pass
    except Exception as exc:
        bad.append(f"trunc32: raised {type(exc).__name__} instead of ManifestError: {exc}")

    # An unterminated varint: previously an unbounded shift loop over big ints.
    overlong = struct.pack("<II", src.MAGIC, 12) + varint(1 << 3 | 2) + b"\x80" * 4096
    try:
        src.read_manifest(_write(path, overlong))
        bad.append("varint: overlong varint parsed instead of failing closed")
    except src.ManifestError:
        pass
    except Exception as exc:
        bad.append(f"varint: raised {type(exc).__name__} instead of ManifestError: {exc}")

    # Pair side of the cap: a 10-byte varint (the uint64 maximum Steam can write)
    # must still decode, and be rejected for being longer than the file.
    huge_size = field_varint(2, 0xFFFFFFFFFFFFFFFF)
    if len(varint(0xFFFFFFFFFFFFFFFF)) != 10:
        bad.append("varint: uint64 max no longer encodes to 10 bytes")
    table = field_bytes(1, b"Game") + huge_size + field_bytes(5, hashlib.sha1(b"x").digest())
    table = field_bytes(1, table)
    body = struct.pack("<II", src.MAGIC, len(table)) + table
    try:
        parsed = src.read_manifest(_write(path, body))
        if len(parsed.entries) != 1 or parsed.entries[0].size != 0xFFFFFFFFFFFFFFFF:
            bad.append(f"varint: 10-byte size varint lost: {parsed.entries}")
    except src.ManifestError:
        bad.append("varint: legitimate 10-byte size varint was rejected")
    except Exception as exc:
        bad.append(f"varint: 10-byte size raised {type(exc).__name__}: {exc}")

    # A tenth byte above bit 63 is a value past uint64: reading it as the low
    # bits would wrap a corrupt length into a plausible one.
    overflow = struct.pack("<II", src.MAGIC, 12) + b"\x08" + b"\x80" * 9 + b"\x02"
    try:
        src.read_manifest(_write(path, overflow))
        bad.append("varint: over-uint64 tenth byte parsed instead of failing closed")
    except src.ManifestError:
        pass
    except Exception as exc:
        bad.append(
            f"varint: over-uint64 raised {type(exc).__name__} instead of ManifestError: {exc}"
        )

    # An entry name that is not UTF-8: the name is the identity --verify matches
    # a local file by, and errors="replace" folded every invalid sequence to
    # U+FFFD, so two different entries could claim the same install path.
    undecodable = field_varint(2, 1) + field_bytes(5, hashlib.sha1(b"x").digest())
    table = field_bytes(1, b"Data\xff\xfe") + undecodable
    table = field_bytes(1, table)
    body = struct.pack("<II", src.MAGIC, len(table)) + table
    try:
        parsed = src.read_manifest(_write(path, body))
        bad.append(f"name: invalid UTF-8 entry name parsed as {parsed.entries}")
    except src.ManifestError:
        pass
    except Exception as exc:
        bad.append(f"name: raised {type(exc).__name__} instead of ManifestError: {exc}")

    # Pair side: a real non-ASCII depot name still decodes.
    good_name = "Data\\Managed\\café.dll"
    body = manifest([entry(good_name, b"x")])
    try:
        parsed = src.read_manifest(_write(path, body))
        if parsed.entries[0].name != good_name:
            bad.append(f"name: non-ASCII name round-tripped as {parsed.entries[0].name!r}")
    except src.ManifestError as exc:
        bad.append(f"name: valid non-ASCII depot name was rejected: {exc}")

    # Pair assertion: a valid manifest must carry the fields the encoder wrote.
    payload = b"steady stock bytes\n"
    good = manifest([entry("Data\\Managed\\Good.dll", payload, flags=1024, chunks=2)])
    try:
        parsed = src.read_manifest(_write(path, good))
    except src.ManifestError as exc:
        bad.append(f"roundtrip: valid seed rejected: {exc}")
        return
    check_invariants(good, parsed, "roundtrip", bad)
    if len(parsed.entries) != 1:
        bad.append(f"roundtrip: {len(parsed.entries)} entries, want 1")
        return
    e = parsed.entries[0]
    if e.name != "Data\\Managed\\Good.dll":
        bad.append(f"roundtrip: name {e.name!r}")
    if e.sha1 != hashlib.sha1(payload).hexdigest():
        bad.append(f"roundtrip: sha1 {e.sha1!r}")
    if e.size != len(payload) or e.flags != 1024 or e.chunks != 2:
        bad.append(f"roundtrip: size/flags/chunks {e.size}/{e.flags}/{e.chunks}")


def _write(path: Path, data: bytes) -> Path:
    path.write_bytes(data)
    return path


def main() -> int:
    rng = random.Random(SEED)
    bad: list[str] = []
    seeds = seed_manifests()
    with tempfile.TemporaryDirectory(
        prefix="steam-manifest-fuzz-", dir=_common.scratch_dir()
    ) as tmp:
        path = Path(tmp) / "294422_1234567890123456789.manifest"
        fuzz(seeds, path, rng, bad)
        if not bad:
            regression_pins(path, bad)
    if bad:
        print("FAIL: steam_manifest fuzz")
        for b in bad:
            print("  - " + b)
        return 1
    print(
        f"OK: {ROUNDS} mutation rounds over {len(seeds)} structure-aware manifest seeds; "
        "no escapes, hangs, invariant breaks, or nondeterminism"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
