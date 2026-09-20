#!/usr/bin/env python3
"""steam_manifest.py: manifest decode and local verification.

DLL-free, network-free. Builds depot manifests with a small wire-format encoder
in a temp tree, then checks the reader, the finder, the verifier verdicts, and
the fail-closed paths (bad magic, truncated table). When this machine has a real
cached 294422 manifest plus the installed DLL, it also asserts Steam's SHA-1 for
`Assembly-CSharp.dll` equals the local file; otherwise that part is skipped.

Usage: python3 tools/tests/test_steam_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "parity" / "steam_manifest.py"
MAGIC = 0x71F617D0


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
    return struct.pack("<II", MAGIC, len(table)) + table + trailer


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args], text=True, capture_output=True, check=False
    )


def real_manifest_check() -> str:
    """Assert Steam's SHA-1 for the installed DLL when the cache is present."""
    found = None
    for root in (Path.home() / ".local/share/Steam", Path.home() / ".steam/steam"):
        hits = sorted((root / "depotcache").glob("294422_*.manifest"))
        if hits:
            found = max(hits, key=lambda p: p.stat().st_mtime)
            break
    asm = _common.find_asm()
    if found is None or asm is None:
        return "real manifest not cached here; parser integration skipped"
    result = run("--manifest", str(found), "--find", "Assembly-CSharp.dll")
    assert result.returncode == 0, result.stderr
    row = [line for line in result.stdout.splitlines() if line.endswith("Assembly-CSharp.dll")]
    assert len(row) == 1, result.stdout
    want = hashlib.sha1(asm.read_bytes()).hexdigest()
    assert want in row[0], f"local DLL sha1 {want} not in manifest row: {row[0]}"
    return f"real manifest {found.name}: DLL sha1 matches Steam"


def main() -> None:
    help_run = run("--help")
    assert help_run.returncode == 0, help_run
    assert "usage:" in help_run.stdout.lower(), help_run

    with tempfile.TemporaryDirectory(prefix="steam_manifest_", dir=_common.scratch_dir()) as tmp:
        root = Path(tmp)
        install = root / "install"
        (install / "Data" / "Managed").mkdir(parents=True)
        good = b"steady stock bytes\n"
        (install / "Data" / "Managed" / "Good.dll").write_bytes(good)
        (install / "Data" / "Managed" / "Corrupt.dll").write_bytes(b"tampered")
        (install / "Data" / "Managed" / "Short.dll").write_bytes(b"xx")
        note = b""
        (install / "Data" / "note.txt").write_bytes(note)

        entries = [
            entry("Data\\Managed\\Good.dll", good),
            entry("Data\\Managed\\Corrupt.dll", b"original"),
            entry("Data\\Managed\\Short.dll", b"original-bytes"),
            entry("Data\\Managed\\Absent.dll", b"gone"),
            entry("Data\\note.txt", note, chunks=0),
            entry("Data\\Managed", b"", chunks=0),
        ]
        path = root / "294422_1234567890123456789.manifest"
        path.write_bytes(manifest(entries))

        summary = run("--manifest", str(path), "--json")
        assert summary.returncode == 0, summary.stderr
        payload = json.loads(summary.stdout)
        assert payload["gid"] == "1234567890123456789", payload
        assert payload["depot"] == "294422", payload
        assert payload["files"] == 6, payload
        assert payload["trailer_bytes"] == 70, payload

        found = run("--manifest", str(path), "--find", "good.dll")
        assert found.returncode == 0, found.stderr
        assert hashlib.sha1(good).hexdigest() in found.stdout, found.stdout

        verified = run("--manifest", str(path), "--verify", str(install), "--only", "Data")
        assert verified.returncode == 1, verified.stdout
        assert "verify: 1 ok, 1 missing, 2 mismatch" in verified.stdout, verified.stdout
        assert "SHA1 Data\\Managed\\Corrupt.dll" in verified.stderr, verified.stderr
        assert "SIZE Data\\Managed\\Short.dll" in verified.stderr, verified.stderr
        assert "MISSING Data\\Managed\\Absent.dll" in verified.stderr, verified.stderr

        (install / "Data" / "Managed" / "Corrupt.dll").write_bytes(b"original")
        (install / "Data" / "Managed" / "Short.dll").write_bytes(b"original-bytes")
        (install / "Data" / "Managed" / "Absent.dll").write_bytes(b"gone")
        clean = run("--manifest", str(path), "--verify", str(install), "--only", "Data")
        assert clean.returncode == 0, (clean.stdout, clean.stderr)
        assert "verify: 4 ok, 0 missing, 0 mismatch" in clean.stdout, clean.stdout

        bad_magic = root / "294422_9.manifest"
        bad_magic.write_bytes(struct.pack("<II", 0xDEADBEEF, 0) + b"junk")
        assert run("--manifest", str(bad_magic)).returncode == 2

        truncated = root / "294422_8.manifest"
        truncated.write_bytes(struct.pack("<II", MAGIC, 1 << 30) + b"junk")
        assert run("--manifest", str(truncated)).returncode == 2

        older = root / "294422_1111111111111111111.manifest"
        older.write_bytes(
            manifest(
                [
                    entry("Data\\keep.bin", b"keep-old"),
                    entry("Data\\drop.bin", b"drop-me"),
                ]
            )
        )
        newer = root / "294422_2222222222222222222.manifest"
        newer.write_bytes(
            manifest(
                [
                    entry("Data\\keep.bin", b"keep-new"),
                    entry("Data\\fresh.bin", b"brand-new"),
                ]
            )
        )
        drift = run("--manifest", str(newer), "--diff", str(older))
        assert drift.returncode == 0, drift.stderr
        assert "diff: 1 added, 1 removed, 1 changed" in drift.stdout, drift.stdout
        assert "~ Data\\keep.bin: size 8 -> 8" in drift.stdout, drift.stdout
        assert "- " in drift.stdout, drift.stdout
        assert "Data\\drop.bin" in drift.stdout, drift.stdout
        assert "+ " in drift.stdout, drift.stdout
        assert "Data\\fresh.bin" in drift.stdout, drift.stdout

        drift_json = run("--manifest", str(newer), "--diff", str(older), "--json")
        payload = json.loads(drift_json.stdout)
        assert payload["changes"] == {"added": 1, "removed": 1, "changed": 1}, payload["changes"]
        assert payload["old_gid"] == "1111111111111111111", payload

        cross_depot = root / "294421_2222222222222222222.manifest"
        cross_depot.write_bytes(newer.read_bytes())
        refused = run("--manifest", str(newer), "--diff", str(cross_depot))
        assert refused.returncode == 2, refused
        assert "refusing to diff depot" in refused.stderr, refused.stderr

        # Cache history: two manifests plus the client log that pairs build ids.
        steam_root = root / "steam"
        (steam_root / "depotcache").mkdir(parents=True)
        (steam_root / "logs").mkdir()
        old_cached = steam_root / "depotcache" / "294422_1111111111111111111.manifest"
        old_cached.write_bytes(manifest([entry("Data\\a.bin", b"old")]))
        new_cached = steam_root / "depotcache" / "294422_2222222222222222222.manifest"
        new_cached.write_bytes(manifest([entry("Data\\a.bin", b"new"), entry("Data\\b.bin", b"b")]))
        os.utime(old_cached, (1_700_000_000, 1_700_000_000))
        os.utime(new_cached, (1_800_000_000, 1_800_000_000))
        (steam_root / "logs" / "content_log.txt").write_text(
            "[2026-01-01 00:00:00] AppID 294420 finished update, 1 mounted depots "
            "(BuildID 24911252) : 294422 (1111111111111111111),\n"
            "[2026-02-01 00:00:00] AppID 294420 finished update, 1 mounted depots "
            "(BuildID 24994542) : 294422 (2222222222222222222),\n",
            encoding="utf-8",
        )
        history = run("--steam-root", str(steam_root), "--history")
        assert history.returncode == 0, history.stderr
        assert "cached manifests: 2" in history.stdout, history.stdout
        rows = [line for line in history.stdout.splitlines() if line.startswith("2222")]
        assert rows, history.stdout
        assert "24994542" in rows[0], history.stdout
        assert "1111111111111111111" in history.stdout, history.stdout

        history_json = run("--steam-root", str(steam_root), "--history", "--json")
        payload = json.loads(history_json.stdout)
        assert [row["buildid"] for row in payload["cached"]] == ["24994542", "24911252"], payload

        labelled = run(
            "--steam-root",
            str(steam_root),
            "--manifest",
            str(new_cached),
            "--diff",
            str(old_cached),
        )
        assert labelled.returncode == 0, labelled.stderr
        assert "diff: 1 added, 0 removed, 1 changed (build 24911252 -> build 24994542)" in (
            labelled.stdout
        ), labelled.stdout

        empty_root = root / "empty-steam"
        empty_root.mkdir()
        no_history = run("--steam-root", str(empty_root), "--history")
        assert no_history.returncode == 2, no_history

        missing = run("--manifest", str(root / "not-there.manifest"))
        assert missing.returncode == 2, missing

    print(f"OK: steam_manifest decode/find/verify cases pass; {real_manifest_check()}")


if __name__ == "__main__":
    main()
