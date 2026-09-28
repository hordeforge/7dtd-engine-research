#!/usr/bin/env python3
"""A randomized gate replays from its seed, and the seed is what it prints.

A fuzz run is only debuggable if the failure names the run that produced it.
The seed used to be a module constant, so the only way back to a failing
mutation stream was to edit the file; the round number in a FAIL line is not a
replay handle, because the stream is shared across families and the family
order is what consumes it. `tooling.fuzz_seed` is the one place a seed is
resolved, `RE_FUZZ_SEED` is its override, and each gate reports both the seed
and a digest of the corpus that seed produced, so two replays can be compared
by more than the seed they claim to share.

Pinned here, DLL-free, network-free:

  1. an unset `RE_FUZZ_SEED` gives the gate its own default, and a set one
     (decimal or hex) replaces it;
  2. a value that is not an integer seed, or one too wide to seed a
     `random.Random`, raises ConfigError rather than falling back to the
     default and running a corpus the caller did not ask for;
  3. the CorpusDigest separates two corpora that concatenate differently;
  4. every seeded gate resolves its seed through `tooling.fuzz_seed` and
     reports a corpus digest, so no gate keeps a private, unnameable seed;
  5. the fast gate run twice on one seed reports one corpus digest, and on
     two different seeds reports two: the same output is determinism, and a
     seed that does not move the corpus is not a seed.

Usage: python3 tools/tests/test_fuzz_seed_replay.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

sys.path.insert(0, str(_common.TOOLS))
import tooling

RE_FUZZ_SEED = tooling.FUZZ_SEED_ENV
TESTS = _common.TOOLS / "tests"
# The gate replayed for real below: the fastest of the seeded gates, and the
# one whose corpus is built entirely in-process.
REPLAYED = TESTS / "test_steam_manifest_fuzz.py"
SEEDED_GATES = (
    "test_save_roundtrip_fuzz.py",
    "test_shader_blob_fuzz.py",
    "test_steam_manifest_fuzz.py",
)
# The f-string a gate formats its verdict with, matched in source so the check
# is a property of the code rather than of one run's output.
SEED_FIELD = "seed 0x{seed:X}"
CORPUS_RE = re.compile(r"corpus [0-9a-f]{16}")
# Two different seeds for the same run, so a digest that ignores the RNG
# stream and hashes a constant would be caught.
SEED_A = "0x51EED1"
SEED_B = "12345"


def run(script: Path, seed: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, RE_FUZZ_SEED=seed)
    return _common.run_cmd(
        [sys.executable, str(script)], env=env, text=True, encoding="utf-8", capture_output=True
    )


def digests(stdout: str) -> list[str]:
    return CORPUS_RE.findall(stdout)


def seed_resolution() -> list[str]:
    bad: list[str] = []
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop(RE_FUZZ_SEED, None)
        if tooling.fuzz_seed(0x7D7D1EA) != 0x7D7D1EA:
            bad.append("unset: default seed not honoured")
        for value, want in (("0", 0), ("42", 42), ("0x2A", 42), ("-1", -1), (" 0x2a ", 42)):
            os.environ[RE_FUZZ_SEED] = value
            got = tooling.fuzz_seed(0x7D7D1EA)
            if got != want:
                bad.append(f"{value!r}: seed {got}, want {want}")
        for value in ("nope", "0x", "1.5", "1e3", str(2**200), "-" + "9" * 40):
            os.environ[RE_FUZZ_SEED] = value
            try:
                got = tooling.fuzz_seed(0x7D7D1EA)
            except tooling.ConfigError:
                continue
            bad.append(f"{value!r}: accepted as seed {got}")
    return bad


def corpus_digest() -> list[str]:
    bad: list[str] = []
    digest = tooling.CorpusDigest()
    digest.add(b"ab")
    digest.add(b"c")
    other = tooling.CorpusDigest()
    other.add(b"a")
    other.add(b"bc")
    if digest.hexdigest() == other.hexdigest():
        bad.append("corpus: 'ab'+'c' and 'a'+'bc' hash alike")
    if digest.count != 2 or not re.fullmatch(r"[0-9a-f]{16}", digest.hexdigest()):
        bad.append(f"corpus: count/format {digest.count} {digest.hexdigest()!r}")
    return bad


def wired_gates() -> list[str]:
    bad: list[str] = []
    for name in SEEDED_GATES:
        path = TESTS / name
        if not path.is_file():
            bad.append(f"{name}: missing")
            continue
        source = path.read_text(encoding="utf-8")
        if "tooling.fuzz_seed(" not in source:
            bad.append(f"{name}: does not resolve its seed through tooling.fuzz_seed")
        if SEED_FIELD not in source:
            bad.append(f"{name}: no output line names the seed it ran on")
        if "corpus {corpus.hexdigest()}" not in source:
            bad.append(f"{name}: no output line reports the corpus its seed produced")
    return bad


def replay() -> list[str]:
    bad: list[str] = []
    first = run(REPLAYED, SEED_A)
    if first.returncode != 0:
        bad.append(f"replay: {REPLAYED.name} rc={first.returncode}: {first.stderr.strip()[:200]}")
        return bad
    again = run(REPLAYED, SEED_A)
    other = run(REPLAYED, SEED_B)
    if again.returncode != 0 or other.returncode != 0:
        bad.append(f"replay: repeated run rc={again.returncode}/{other.returncode}")
        return bad
    left, right, third = digests(first.stdout), digests(again.stdout), digests(other.stdout)
    if not left or not right or not third:
        bad.append(f"replay: no corpus digest reported: {first.stdout.strip()[:200]}")
        return bad
    if left != right:
        bad.append(f"replay: seed {SEED_A} produced {left} then {right}")
    if left == third:
        bad.append(f"replay: seeds {SEED_A} and {SEED_B} produced the same corpus {left}")
    if f"seed 0x{int(SEED_A, 0):X}" not in first.stdout:
        bad.append(f"replay: output does not name seed {SEED_A}: {first.stdout.strip()[:200]}")
    return bad


def main() -> int:
    bad = seed_resolution() + corpus_digest() + wired_gates() + replay()
    if bad:
        print("FAIL: fuzz seed replay")
        for line in bad:
            print("  - " + line)
        return 1
    print(
        f"OK: {len(SEEDED_GATES)} seeded gates resolve one seed, report it with a corpus "
        f"digest, and {REPLAYED.name} replays identically on {SEED_A} and differently on {SEED_B}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
