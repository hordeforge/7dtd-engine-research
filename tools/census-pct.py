#!/usr/bin/env python3
"""Compute the RE-coverage percentages for the 7dtd-research corpus.

Runs the live census tools against the game assembly and prints how much of
the code is known at each layer:

  1. Reached game types (the dedicated-server RE surface): narrated /
     catalogued / classified / unaccounted percentages.
  2. Whole assembly: reached-method and reached-type fractions, and what the
     unreached remainder is (client/editor/third-party, out of RE scope).

Usage:
  python3 tools/census-pct.py [asm] [docsDir]
    asm     path to Assembly-CSharp.dll (default: $ASM or the Steam path
            under ~/.local/share/Steam; same resolution as tools/stock-sync.sh)
    docsDir docs directory to scan (default: docs)

Exit code is 0 unless the census itself fails; unaccounted > 0 is reported
loudly but is not a hard failure (this is a report, not a gate).
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def default_asm():
    env = os.environ.get("ASM")
    if env:
        return env
    home = os.path.expanduser("~")
    cand = os.path.join(
        home,
        ".local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/"
        "7DaysToDieServer_Data/Managed/Assembly-CSharp.dll",
    )
    return cand


def run_mono(exe, *args):
    """Run a tools/bin exe under mono with MONO_PATH set, return stdout+stderr."""
    bin_dir = os.path.join(REPO, "tools", "bin")
    env = dict(os.environ)
    env["MONO_PATH"] = bin_dir
    proc = subprocess.run(
        ["mono", os.path.join(bin_dir, exe), *args],
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr


def parse_coverage(stderr):
    """Parse the Coverage.exe summary line:
    'reached methods=N game types=N narrated=N catalogued=N classified=N unaccounted=N'
    """
    m = re.search(
        r"reached methods=(\d+) game types=(\d+) narrated=(\d+) catalogued=(\d+) "
        r"classified=(\d+) unaccounted=(\d+)",
        stderr,
    )
    if not m:
        raise ValueError("could not parse Coverage.exe summary from stderr:\n" + stderr)
    return {
        "reached_methods": int(m.group(1)),
        "game_types": int(m.group(2)),
        "narrated": int(m.group(3)),
        "catalogued": int(m.group(4)),
        "classified": int(m.group(5)),
        "unaccounted": int(m.group(6)),
    }


def parse_census(stdout):
    """Parse Census.exe key/value lines: 'AllTypes (incl nested)       = 7432'."""
    out = {}
    for line in stdout.splitlines():
        m = re.match(r"([A-Za-z0-9 ().*]+?)\s*=\s*(\d+)", line)
        if m:
            out[m.group(1).strip()] = int(m.group(2))
    return out


def parse_report_reached_types(report_path):
    """Grab 'Reached types (incl. compiler-generated)' from the Coverage report."""
    try:
        with open(report_path, encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"\|\s*Reached types \(incl\. compiler-generated\)\s*\|\s*(\d+)\s*\|", line)
                if m:
                    return int(m.group(1))
    except OSError:
        pass
    return 0


def pct(n, total):
    return 100.0 * n / total if total else 0.0


def main():
    asm = sys.argv[1] if len(sys.argv) > 1 else default_asm()
    docs = sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO, "docs")

    if not os.path.isfile(asm):
        print(f"error: assembly not found at {asm}", file=sys.stderr)
        print("pass the path as argv[1] or set $ASM", file=sys.stderr)
        return 2

    # 1. Live coverage census over the docs tree (report to /tmp so the scan
    #    never sees a stale extra file inside docs/).
    tmp_report = "/tmp/census-pct-coverage-report.md"
    rc, _, stderr = run_mono("Coverage.exe", asm, docs, tmp_report)
    if rc != 0:
        print("error: Coverage.exe failed:", file=sys.stderr)
        print(stderr, file=sys.stderr)
        return rc
    cov = parse_coverage(stderr)
    reached_types = parse_report_reached_types(tmp_report)
    if os.path.exists(tmp_report):
        os.unlink(tmp_report)

    # 2. Whole-assembly census (for the unreached remainder).
    rc, stdout, _ = run_mono("Census.exe", asm)
    if rc != 0:
        print("error: Census.exe failed", file=sys.stderr)
        return rc
    cen = parse_census(stdout)
    all_types = cen.get("AllTypes (incl nested)", 0)
    all_methods = cen.get("AllMethodsWithBody", 0)

    g = cov["game_types"]
    print("RE coverage of the 7dtd-research corpus (live census)\n")
    print("Reached game types (dedicated-server RE surface): %d" % g)
    print("  narrated      %6d  %5.1f%%  (hand-written narrative prose)" % (
        cov["narrated"], pct(cov["narrated"], g)))
    print("  catalogued    %6d  %5.1f%%  (generated inventory: enumerated, not explained)" % (
        cov["catalogued"], pct(cov["catalogued"], g)))
    print("  classified    %6d  %5.1f%%  (verified out-of-scope: client/3rd-party, not dedi work)" % (
        cov["classified"], pct(cov["classified"], g)))
    print("  UNACCOUNTED   %6d  %5.1f%%  (appears nowhere)" % (
        cov["unaccounted"], pct(cov["unaccounted"], g)))

    known = cov["narrated"] + cov["catalogued"] + cov["classified"]
    print("\nAccounted-for reached game types: %d / %d (%.1f%%)" % (
        known, g, pct(known, g)))
    print("Completely unknown (unaccounted):  %d / %d (%.1f%%)" % (
        cov["unaccounted"], g, pct(cov["unaccounted"], g)))
    print("Not deeply narrated (catalogued + classified): %d / %d (%.1f%%)" % (
        cov["catalogued"] + cov["classified"], g,
        pct(cov["catalogued"] + cov["classified"], g)))

    if all_types and all_methods:
        print("\nWhole assembly (Census.exe):")
        if reached_types:
            print("  types   %6d total; %d reached in the server call graph (%.1f%%)" % (
                all_types, reached_types, pct(reached_types, all_types)))
            print("          (reached types include compiler-generated <>c/display classes,")
            print("          which the call graph always touches)")
        print("  methods %6d total; %d reached (%.1f%%)" % (
            all_methods, cov["reached_methods"], pct(cov["reached_methods"], all_methods)))
        print("  unreached remainder: client-only render/UI, editor tools, third-party")
        print("  libraries (structurally mapped by full-surface, not RE-narrated)")

    if cov["unaccounted"]:
        print("\nWARNING: unaccounted types > 0 - the corpus is not at 100%.")
    else:
        print("\nunaccounted = 0: every reached game type is narrated, catalogued, or classified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
