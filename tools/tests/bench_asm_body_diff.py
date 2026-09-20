#!/usr/bin/env python3
"""Deterministic perf gate for the method-body diff lens.

`tools/asm_body_diff.py` is the one slow lens in the research loop (a full
Cecil walk of two 11 MB assemblies). This bench pins its cost with **retired
instructions** (`perf stat -e instructions:u`), which are load-independent and,
for the same mono + pinned Mono.Cecil, machine-independent. It also asserts the
two assembly walks overlap (wall is well below total CPU time) and that the
walk still emits a parseable summary.

Baseline recorded on this host (see RECORDED_* below; re-record only with a new
mono/Cecil pair and update the note):

  asm_body_diff.py p50: 41.8e9 instructions, 3210 ms CPU, 1565 ms wall (ratio 0.49)
  before the hashing rework: 44.2e9 instructions, 2370 ms wall
  before the two-thread walk (still 39.2e9 instructions): 2076 ms wall
  research_diff.py p50 over the same pair: 3182 ms -> 2364 ms

SKIPs (exit 0) without the two local assemblies, without `perf` permission for
user-space counters, or without mono/mcs. Wall clock is reported, never
asserted directly: the parallel ratio is the only timing-shaped assertion, and
it needs >= 2 CPUs.

Usage: python3 tools/tests/bench_asm_body_diff.py
"""

from __future__ import annotations

import os
import re
import resource
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "asm_body_diff.py"
RECORDED_MONO = "6.12.0"
RECORDED_INSTRUCTIONS = 41.8e9
RECORDED_CPU_MS = 3210.0
INSTRUCTION_BAND = 0.15
CPU_BAND = 0.20
MAX_PARALLEL_RATIO = 0.90
RUNS = 3

INSTRUCTIONS_RE = re.compile(r"([\d,]+)\s+instructions:u")


def perf_works() -> bool:
    if shutil.which("perf") is None:
        return False
    probe = subprocess.run(
        ["perf", "stat", "-e", "instructions:u", "true"], capture_output=True, text=True
    )
    return probe.returncode == 0 and "instructions:u" in probe.stderr


def mono_version() -> str:
    probe = subprocess.run(["mono", "--version"], capture_output=True, text=True)
    match = re.search(r"version (\S+)", probe.stdout or "")
    return match.group(1) if match else "unknown"


def run_instructions(old: Path, new: Path) -> float:
    """Retired user-space instructions for one full tool run (perf follows forks)."""
    proc = subprocess.run(
        [
            "perf",
            "stat",
            "-e",
            "instructions:u",
            sys.executable,
            str(TOOL),
            str(old),
            str(new),
        ],
        capture_output=True,
        text=True,
        env=dict(os.environ, MONO_PATH=str(_common.BIN)),
    )
    match = INSTRUCTIONS_RE.search(proc.stderr)
    if proc.returncode != 0 or not match:
        raise RuntimeError(f"perf/asm_body_diff failed: {proc.stderr.strip()[:400]}")
    return float(match.group(1).replace(",", ""))


def run_cpu_wall(old: Path, new: Path) -> tuple[float, float, str]:
    """CPU ms (child rusage, load-independent) and wall ms for one tool run."""
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(TOOL), str(old), str(new)],
        capture_output=True,
        text=True,
        env=dict(os.environ, MONO_PATH=str(_common.BIN)),
    )
    wall = (time.perf_counter() - start) * 1000.0
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = ((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)) * 1000.0
    if proc.returncode != 0:
        raise RuntimeError(f"asm_body_diff failed: {proc.stderr.strip()[:400]}")
    return cpu, wall, proc.stdout


def main() -> int:
    asm = _common.find_asm()
    if asm is None:
        print("SKIP: dedicated Assembly-CSharp.dll not found")
        return 0
    backup = asm.with_name(asm.name + ".re_stock_bak")
    if not backup.is_file():
        print(f"SKIP: retained baseline build not found: {backup}")
        return 0
    if shutil.which("mono") is None or shutil.which("mcs") is None:
        print("SKIP: mono/mcs not on PATH")
        return 0
    if not (_common.BIN / "Mono.Cecil.dll").is_file():
        print("SKIP: tools not built (cd tools && ./build.sh --skip-legacy)")
        return 0
    if not perf_works():
        print("SKIP: perf cannot count user-space instructions (perf_event_paranoid?)")
        return 0

    version = mono_version()
    cpu_count = os.cpu_count() or 1
    if version != RECORDED_MONO:
        print(f"SKIP: mono {version!r} != recorded {RECORDED_MONO!r}; re-record the baseline")
        return 0

    ins = statistics.median(run_instructions(backup, asm) for _ in range(RUNS))
    timings = [run_cpu_wall(backup, asm) for _ in range(RUNS)]
    cpu = statistics.median(t[0] for t in timings)
    wall = statistics.median(t[1] for t in timings)
    summary = next((line for line in timings[0][2].splitlines() if "methods bak=" in line), None)
    if summary is None:
        print("FAIL: asm_body_diff produced no summary line", file=sys.stderr)
        return 1

    problems = []
    if abs(ins - RECORDED_INSTRUCTIONS) > INSTRUCTION_BAND * RECORDED_INSTRUCTIONS:
        problems.append(
            f"instructions {ins / 1e9:.1f}e9 outside ±{INSTRUCTION_BAND:.0%} of "
            f"{RECORDED_INSTRUCTIONS / 1e9:.1f}e9"
        )
    if cpu > (1.0 + CPU_BAND) * RECORDED_CPU_MS:
        problems.append(f"CPU {cpu:.0f} ms above {RECORDED_CPU_MS:.0f} ms +{CPU_BAND:.0%}")
    if cpu_count >= 2 and wall > MAX_PARALLEL_RATIO * cpu:
        problems.append(
            f"wall {wall:.0f} ms is not below {MAX_PARALLEL_RATIO:.0%} of CPU {cpu:.0f} ms: "
            "the two assembly walks are no longer overlapping"
        )
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1

    print(
        f"OK: asm_body_diff p50 {ins / 1e9:.1f}e9 instructions, {cpu:.0f} ms CPU, "
        f"{wall:.0f} ms wall (ratio {wall / cpu:.2f}); {summary.split(',')[0]}; "
        f"{version}, {cpu_count} CPUs"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
