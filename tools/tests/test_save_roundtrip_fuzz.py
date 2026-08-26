#!/usr/bin/env python3
"""Seeded mutation fuzzer for the save-format parsers in save_roundtrip_check.py.

The round-trip verifier is this repo's untrusted-input surface: it parses
stock-written saves that may be truncated or corrupt, and treats crafted slots
as hostile (the capped inflate exists because a slot can request gigabytes).
The fixture-driven robustness gate pins specific malformations; a fuzzer proves
the broader contract holds for arbitrary bytes:

  1. No exception escapes a parser entry point: malformed input degrades to
     check lines (or, for parse_chunk_body, the documented
     ValueError/struct.error its caller catches), never a traceback.
  2. Every call terminates fast: a file-controlled count must never drive a
     minutes-long walk before the next bounds check (pins the spawnList fix).
  3. Verdict consistency: a "byte-exact" line never carries a FAIL marker, and
     re-parsing one input yields identical check lines.
  4. inflate_raw_capped returns bytes or raises ValueError only, preserves
     zlib round-trips, and refuses a deflate bomb over its cap.

Seeds are structure-aware: valid minimal main.ttw tails, .7rg regions carrying
a compressed valid chunk body, chunk bodies, and the small record formats;
seeded mutations (bit flips, truncation, splices, count-field inflation) then
explore around realistic shapes. Deterministic, stdlib-only, seconds to run.

Usage: python3 tools/tests/test_save_roundtrip_fuzz.py
"""

import os
import random
import struct
import sys
import tempfile
import time
import zlib
from collections.abc import Callable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

REPO = str(_common.REPO)
TOOLS = str(_common.TOOLS)
sys.path.insert(0, TOOLS)

import save_roundtrip_check as src

SEED = 0x7D7D1EA
ROUNDS = 240  # mutation rounds per target family
TIME_BUDGET_S = 5.0  # hard ceiling for ONE parser call (hang-class guard)


def netstr(s: str) -> bytes:
    """read_net_string encoding: u8/u32-prefixed UTF-8 (u8 fits fixtures)."""
    raw = s.encode()
    return bytes([len(raw)]) + raw


def build_chunk_body(slot: int) -> bytes:
    """Minimal Chunk.save body that parse_chunk_body accepts byte-exactly."""
    x, z = slot % 32, slot // 32  # C# remainder mapping for slot < 1024

    def chan(bpv: int) -> bytes:
        return b"\x01" + b"\x07" * bpv  # one RLE flag+value per slice

    parts = [struct.pack("<iii", x, 0, z), struct.pack("<Q", 1000)]
    parts.append(b"\x00" * 64)  # 64 layer triples, all absent
    parts.append(chan(1) * 64)  # chnStability
    parts.append(b"\x00" * (256 + 256 + 32 + 256 + 1536))  # HeightMap..BiomeInt
    parts.append(struct.pack("<bb", 1, 2))  # d_biome, am_biome
    parts.append(struct.pack("<H", 0))  # custom block count
    parts.append(b"\x00" * (256 * 3))  # normal maps
    parts.append(chan(1) * 64 + chan(1) * 64 + chan(2) * 64)  # density/light/dmg
    parts.append(chan(6) * 64 + chan(2) * 64)  # textures[0]/water
    parts.append(b"\x00")  # NeedsLightCalculation
    parts.append(struct.pack("<i", 0))  # entities
    parts.append(struct.pack("<i", 0))  # tile entities
    parts.append(b"\x00")  # file-path bool
    parts.append(struct.pack("<B", 0) * 3)  # sleeper/trigger/wall volume counts
    parts.append(struct.pack("<h", 0))  # insideDevices count
    parts.append(b"\x00")  # IsInternalBlocksCulled
    parts.append(struct.pack("<h", 0))  # triggerData count
    return b"".join(parts)


def deflate_raw(data: bytes) -> bytes:
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return c.compress(data) + c.flush()


def build_region(slot: int, body: bytes) -> bytes:
    """V2 .7rg: header + location@4096 + timestamp@8192 + one ttc slot."""
    frame = (
        struct.pack("<I", len(body) + 8)
        + b"\x00" * 12
        + b"ttc\x00"
        + struct.pack("<I", 47)
        + deflate_raw(body)
    )
    sector = 4
    data = bytearray((sector + 3) * 4096)
    data[0:3] = b"7rg"
    data[3] = 2
    base = 4096 + slot * 4
    struct.pack_into("<H", data, base, sector)
    data[base + 3] = 1
    struct.pack_into("<I", data, 8192 + slot * 4, 7)
    data[sector * 4096 : sector * 4096 + len(frame)] = frame
    return bytes(data)


def build_ai_blob() -> bytes:
    # version 10, wandering next (horde, bandit), airdrop next, packed freq
    # word, crate count 0, chunkEvent ver/active, bloodMoon last/next/freq/range
    return struct.pack("<iQQQQiiiii2h", 10, 1, 2, 3, 0, 0, 1, 0, 5, 8, 2, 3)


def build_worldstate_tail() -> bytes:
    dyn = bytes([1, 0])
    sleeper = struct.pack("<ii", 0, 1)  # count 0, nextId 1
    empty_vol = struct.pack("<ii", 0, 1)
    weather = struct.pack("<HBB", 4, 60, 0)  # ver, gate, biome count
    ai = build_ai_blob()
    tail = bytes([2]) + struct.pack("<i", 0)  # spawnList ver + count
    tail += struct.pack("<iq", 42, 123456)  # nextEntityID, saveDataLimit
    tail += struct.pack("<i", len(dyn)) + dyn
    tail += struct.pack("<i", len(ai)) + ai
    tail += struct.pack("<ii", 1, len(sleeper)) + sleeper
    tail += struct.pack("<ii", 0, len(empty_vol)) + empty_vol  # triggerVolumes
    tail += struct.pack("<ii", 0, len(empty_vol)) + empty_vol  # wallVolumes
    tail += struct.pack("<i", len(weather) + 4) + weather
    tail += netstr("0123456789abcdef")  # world guid
    return tail


def build_ttw(spawn_count: int | None = None, tail: bytes | None = None) -> bytes:
    head = b"ttw\x00" + struct.pack("<I", 23)
    head += netstr("V3.1.0")
    head += struct.pack("<4i", 1, 3, 10, 14)
    head += struct.pack("<iii", 0, 0, 0)  # pad0, activeGameMode, pad1
    head += struct.pack("<f", 62.88)
    head += struct.pack("<iii", 16, 16, 16)
    head += struct.pack("<iii", 0, 4, 12345)  # chunkCount, providerId, seed
    head += struct.pack("<QQ", 1000, 60000)  # worldTime, timeInTicks
    if spawn_count is not None:
        return head + bytes([2]) + struct.pack("<i", spawn_count)
    return head + (tail if tail is not None else build_worldstate_tail())


def build_record(count: int = 1) -> bytes:
    rec = struct.pack("<QfIB", 99, 62.5, 3735928559, 3)
    return bytes([6]) + struct.pack("<i", count) + rec * count


def build_nim(count: int = 2) -> bytes:
    out = struct.pack("<II", 3, count)
    for i in range(count):
        out += struct.pack("<I", 1000 + i) + netstr(f"block{i}")
    return out


def mutate(rng: random.Random, data: bytes) -> bytes:
    b = bytearray(data if data else b"\x00")
    for _ in range(rng.randint(1, 8)):
        op = rng.choice(("flip", "set", "trunc", "grow", "count"))
        if op == "flip":
            i = rng.randrange(len(b))
            b[i] ^= 1 << rng.randrange(8)
        elif op == "set":
            b[rng.randrange(len(b))] = rng.randrange(256)
        elif op == "trunc":
            del b[rng.randrange(len(b)) :]
        elif op == "grow":
            b += bytes(rng.randrange(256) for _ in range(rng.randint(1, 64)))
        elif op == "count":
            i = rng.randrange(max(1, len(b) - 4))
            b[i : i + 4] = struct.pack(
                "<I", rng.choice((0x7FFFFFFF, 0xFFFFFF7F, 0xFFFF, 0x00FFFFFF))
            )
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


def run_path_parser(
    parser: Callable[[str, list[str]], None], data: bytes, tmpdir: str
) -> list[str]:
    path = os.path.join(tmpdir, "fuzz.bin")
    with open(path, "wb") as fh:
        fh.write(data)
    checks: list[str] = []
    timed(lambda: src.run_file_check(parser, path, checks))
    return checks


def run_blob_parser(
    parser: Callable[..., object], data: bytes, off: int | None = None
) -> list[str]:
    checks: list[str] = []
    args = (data, off, checks) if off is not None else (data, checks)
    timed(lambda: parser(*args))
    return checks


ALLOWED_CHUNK_BODY = (ValueError, struct.error)


def assert_contract(checks: list[str], label: str, bad: list[str]) -> None:
    for line in checks:
        if "byte-exact" in line and any(m in line for m in src.FAILED_MARKERS):
            bad.append(f"{label}: contradictory line claims byte-exact + FAIL: {line!r}")
            return


def deterministic(checks_factory: Callable[[], list[str]], label: str, bad: list[str]) -> None:
    a = checks_factory()
    b = checks_factory()
    if a != b:
        bad.append(f"{label}: parser not deterministic:\n  {a}\n  {b}")


def fuzz_family(
    name: str,
    seed_builder: Callable[[int], bytes],
    invoker: Callable[[bytes], list[str]],
    rng: random.Random,
    rounds: int,
    bad: list[str],
) -> None:
    seeds = [seed_builder(i) for i in range(3)]
    # parse_chunk_body documents ValueError/struct.error as its caller-caught
    # degradation path; every other surface must swallow malformed bytes whole.
    allowed = ALLOWED_CHUNK_BODY if name == "chunk-body" else ()
    for k in range(rounds):
        data = mutate(rng, rng.choice(seeds)) if rng.random() < 0.85 else seeds[k % 3]
        try:
            checks = invoker(data)
        except BudgetError as exc:
            bad.append(f"{name} round {k}: {exc}")
            return
        except Exception as exc:
            if isinstance(exc, allowed):
                checks = []
            else:
                bad.append(f"{name} round {k}: ESCAPED {type(exc).__name__}: {exc}")
                return
        assert_contract(checks, f"{name} round {k}", bad)
        if bad:
            return
        if k % 8 == 0:

            def rerun(data: bytes = data) -> list[str]:
                try:
                    return invoker(data)
                except allowed:
                    return []

            deterministic(rerun, f"{name} round {k}", bad)
            if bad:
                return


def main() -> int:
    rng = random.Random(SEED)
    bad: list[str] = []
    with tempfile.TemporaryDirectory(prefix="srt-fuzz-", dir=_common.scratch_dir()) as tmp:
        families = [
            (
                "main.ttw",
                lambda i: build_ttw(),
                lambda d: run_path_parser(src.check_main_ttw, d, tmp),
            ),
            (
                "region-v2",
                lambda i: build_region(i, build_chunk_body(i % 1024)),
                lambda d: run_path_parser(src.check_region_v2, d, tmp),
            ),
            (
                "region-raw",
                lambda i: b"7rr" + struct.pack("<ii", 3, 0) + bytes([i]) * 64,
                lambda d: run_path_parser(src.check_region_raw, d, tmp),
            ),
            (
                "decoration-7dt",
                lambda i: build_record(i + 1),
                lambda d: run_path_parser(src.check_decoration_7dt, d, tmp),
            ),
            (
                "multiblocks-7dt",
                lambda i: build_record(i),
                lambda d: run_path_parser(src.check_multiblocks_7dt, d, tmp),
            ),
            (
                "nim-mapping",
                lambda i: build_nim(i + 1),
                lambda d: run_path_parser(src.check_nim_mapping, d, tmp),
            ),
            (
                "chunk-body",
                lambda i: build_chunk_body((i * 37) % 1024),
                lambda d: run_blob_parser(src.parse_chunk_body, d, 3),
            ),
            (
                "worldstate-tail",
                lambda i: build_worldstate_tail(),
                lambda d: run_blob_parser(src.check_worldstate_tail, d, 0),
            ),
            (
                "sleeper-volumes",
                lambda i: struct.pack("<i", 1) + bytes([i % 256]) * 96,
                lambda d: run_blob_parser(src.check_sleeper_volumes, d),
            ),
            (
                "ai-director",
                lambda i: build_ai_blob(),
                lambda d: run_blob_parser(src.check_ai_director_blob, d),
            ),
            (
                "weather",
                lambda i: struct.pack("<HBB", 4, 60, 1) + bytes(40),
                lambda d: run_blob_parser(src.check_weather_blob, d),
            ),
        ]
        for name, seed_builder, invoker in families:
            fuzz_family(name, seed_builder, invoker, rng, ROUNDS, bad)
            if bad:
                break

        # Regression pin: crafted spawnList count used to drive a minutes-long
        # arithmetic walk before the next bounds check fired.
        ttw = os.path.join(tmp, "hang.ttw")
        with open(ttw, "wb") as fh:
            fh.write(build_ttw(spawn_count=0x7FFFFFFF))
        checks: list[str] = []
        try:
            timed(lambda: src.run_file_check(src.check_main_ttw, ttw, checks))
        except BudgetError:
            bad.append("spawnList regression: crafted count still walks unbounded")
        if not any("parse error" in c for c in checks) or not src.any_failed(checks):
            bad.append(f"spawnList regression: no FAIL degradation: {checks}")

        # Happy-path pin: a fully valid ttw + region must come back byte-exact
        # with a green verdict, so the seeds above start from a true shape.
        save = os.path.join(tmp, "good-save", "Region")
        os.makedirs(save)
        with open(os.path.join(tmp, "good-save", "main.ttw"), "wb") as fh:
            fh.write(build_ttw())
        with open(os.path.join(save, "r.7rg"), "wb") as fh:
            fh.write(build_region(0, build_chunk_body(0)))
        checks = []
        good_ttw = os.path.join(tmp, "good-save", "main.ttw")
        src.run_file_check(src.check_main_ttw, good_ttw, checks)
        src.run_file_check(src.check_region_v2, os.path.join(save, "r.7rg"), checks)
        joined = " ".join(checks)
        if src.any_failed(checks) or "full WorldState parse byte-exact" not in joined:
            bad.append("happy path: valid ttw no longer byte-exact:\n" + "\n".join(checks))
        if "1/1 chunks parse byte-exactly" not in joined:
            bad.append("happy path: valid region chunk no longer byte-exact")

    # Codec boundary pair: inflate_raw_capped inverts zlib RAW_DEFLATE exactly,
    # refuses a bomb past MAX_INFLATED, and only ever raises ValueError.
    unit = b"\x00" * (1 << 20)
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    bomb = bytearray()
    for _ in range(src.MAX_INFLATED // (1 << 20) + 1):
        # Keep each chunk: dropping compress() output corrupts the stream on
        # CPython 3.14 (buffer lifetime regression), which would masquerade as
        # a parser bug here.
        bomb += c.compress(unit)
    bomb += c.flush()
    try:
        src.inflate_raw_capped(bytes(bomb))
        bad.append("inflate: bomb over cap was not rejected")
    except ValueError:
        pass
    except Exception as exc:
        bad.append(f"inflate: bomb raised {type(exc).__name__} instead of ValueError")
    probe = bytes(rng.randrange(256) for _ in range(4096))
    try:
        if src.inflate_raw_capped(deflate_raw(probe)) != probe:
            bad.append("inflate: round-trip mismatch")
    except ValueError:
        bad.append("inflate: valid stream rejected")
    except Exception as exc:
        bad.append(f"inflate: raised {type(exc).__name__}: {exc}")

    if bad:
        print("FAIL: save_roundtrip fuzz")
        for b in bad:
            print("  - " + b)
        return 1
    print(
        f"OK: {ROUNDS * len(families)} mutation rounds across "
        f"{len(families)} parser surfaces; no escapes, hangs, or verdict drift"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
