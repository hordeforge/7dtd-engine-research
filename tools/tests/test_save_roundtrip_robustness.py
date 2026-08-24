#!/usr/bin/env python3
"""save_roundtrip_check.py degrades malformed input to FAIL, never a traceback.

The round-trip verifier reads stock-written saves that may be truncated or
corrupt; a hard struct.error/IndexError used to escape as a Python traceback,
aborting the whole run (skipping every remaining file's checks) and printing
no FAIL verdict. These fixtures pin the guard: every malformed file yields a
"parse error" check line and exit 1, and the --shipped mode usage-errors with
exit 2 when its required path argument is missing or absent on disk.

Usage: python3 tools/tests/test_save_roundtrip_robustness.py
"""
import os
import struct
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(TOOLS, "save_roundtrip_check.py")


def run(*argv):
    proc = subprocess.run(
        [sys.executable, SCRIPT, *argv], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout + proc.stderr


def assert_no_traceback(rc, out, label, bad):
    if "Traceback" in out:
        bad.append(f"{label}: raw traceback escaped:\n{out}")
    if rc != 1:
        bad.append(f"{label}: expected exit 1, got {rc}")


def truncated_ttw(path):
    with open(path, "wb") as f:
        f.write(b"ttw\x00\x17\x00\x00\x00V")  # magic + version, header cut mid-string


def corrupt_region_dir(dirpath):
    """Save dir whose .7rg has an in-bounds slot 0 then a slot pointing past EOF."""
    region = os.path.join(dirpath, "Region")
    os.makedirs(region)
    data = bytearray(b"\x00" * (4096 * 12))
    data[0:3] = b"7rg"
    data[3] = 2  # V2: location table @4096, timestamp @8192
    struct.pack_into("<H", data, 4096, 2)  # slot 0 -> sector 2 (in bounds)
    data[4096 + 3] = 1
    base = 4096 + 5 * 4
    struct.pack_into("<H", data, base, 20000)  # slot 5 -> sector 20000 (past EOF)
    data[base + 3] = 1
    with open(os.path.join(region, "badoff.7rg"), "wb") as f:
        f.write(data)


def slot0_past_eof_region_dir(dirpath):
    """Save dir whose only allocated .7rg slot points past EOF.

    The bound check fires before any payload read, so it must produce a
    FAIL-marker line itself (a plain note used to slip through as PASS).
    """
    region = os.path.join(dirpath, "Region")
    os.makedirs(region)
    data = bytearray(b"\x00" * (4096 * 12))
    data[0:3] = b"7rg"
    data[3] = 2
    struct.pack_into("<H", data, 4096, 20000)  # slot 0 -> sector 20000 (past EOF)
    data[4096 + 3] = 1
    with open(os.path.join(region, "slot0bad.7rg"), "wb") as f:
        f.write(data)


def unreadable_region_entry(dirpath):
    """Save dir whose Region/ holds a '*.7rg' that is a DIRECTORY.

    glob matches it, open() raises IsADirectoryError (an OSError, raised even
    for root); run_file_check must degrade that to a parse-error FAIL line,
    not abort the remaining files' checks with a traceback.
    """
    region = os.path.join(dirpath, "Region")
    os.makedirs(os.path.join(region, "dir.7rg"))
    with open(os.path.join(region, "good.7rg"), "wb") as f:
        f.write(b"")


def main():
    bad = []
    with tempfile.TemporaryDirectory(prefix="srt-robustness-") as tmp:
        ttw = os.path.join(tmp, "trunc.ttw")
        truncated_ttw(ttw)
        rc, out = run("--shipped", ttw)
        assert_no_traceback(rc, out, "--shipped truncated.ttw", bad)
        if "parse error" not in out or "\nFAIL:" not in out:
            bad.append(f"--shipped truncated.ttw: no parse-error FAIL verdict:\n{out}")

        save = os.path.join(tmp, "save")
        os.makedirs(save)
        corrupt_region_dir(save)
        rc, out = run(save)
        assert_no_traceback(rc, out, "corrupt region dir", bad)
        if "parse error" not in out or "\nFAIL:" not in out:
            bad.append(f"corrupt region dir: no parse-error FAIL verdict:\n{out}")
        if "main.ttw: MISSING" not in out:
            bad.append("corrupt region dir: missing-main.ttw check not reported")

        save0 = os.path.join(tmp, "save0")
        os.makedirs(save0)
        slot0_past_eof_region_dir(save0)
        rc, out = run(save0)
        assert_no_traceback(rc, out, "slot0 past-EOF region dir", bad)
        if "exceeds file bounds" not in out or "\nFAIL:" not in out:
            bad.append(f"slot0 past-EOF region dir: no bounds FAIL verdict:\n{out}")

        save1 = os.path.join(tmp, "save1")
        os.makedirs(save1)
        unreadable_region_entry(save1)
        rc, out = run(save1)
        assert_no_traceback(rc, out, "directory-named .7rg", bad)
        if "parse error" not in out or "\nFAIL:" not in out:
            bad.append(f"directory-named .7rg: no parse-error FAIL verdict:\n{out}")
        if "main.ttw: MISSING" not in out:
            bad.append("directory-named .7rg: later checks skipped (run aborted early)")

        rc, _ = run("--shipped")
        if rc != 2:
            bad.append(f"--shipped without path: expected exit 2, got {rc}")
        rc, _ = run("--shipped", os.path.join(tmp, "no-such-world"))
        if rc != 2:
            bad.append(f"--shipped nonexistent path: expected exit 2, got {rc}")

    if bad:
        print("FAIL: save_roundtrip robustness")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK: malformed saves degrade to FAIL verdicts; --shipped usage-errors cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
