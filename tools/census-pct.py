#!/usr/bin/env python3
"""Compute the RE-coverage percentages for the 7dtd-engine-research corpus.

Runs the live census tools against the game assembly and prints how much of
the code is known at each layer:

  1. Reached game types (the dedicated-server RE surface): narrated /
     catalogued / classified / unaccounted percentages.
  2. Whole assembly (100% view): every Assembly-CSharp type and method body is
     accounted - reached game types are narrated/catalogued/classified, and the
     unreached game types (client/editor/Unity-lifecycle-booted/reflection/
     dead) are classified in out-of-scope-surface.md. Compiler-generated and
     third-party/BCL types are excluded by design.

Usage:
  python3 tools/census-pct.py [asm] [docsDir] [--json] [--history FILE]
    asm     path to Assembly-CSharp.dll (default: $ASM or the Steam path
            under ~/.local/share/Steam; same resolution as tools/stock-sync.sh)
    docsDir docs directory to scan (default: docs)
    --json  emit a machine-readable JSON object instead of the human report
    --history FILE  append the percentages to a CSV (default name:
            census-history.csv) so census numbers can be tracked over time
            (date column is UTC so rows from different hosts stay comparable)

Exit code is 0 unless the census itself fails; unaccounted > 0 is reported
loudly but is not a hard failure (this is a report, not a gate).
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

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


def parse_report_accounted(report_path):
    """Grab the whole-assembly 100% rows: accounted types and methods in them."""
    out = {"acct_types": None, "acct_methods": None}
    try:
        with open(report_path, encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"\|\s*Accounted game types \(reached documented \+ unreached classified\)\s*\|\s*\*\*(\d+) / \d+ \(100%\)\*\*\s*\|", line)
                if m:
                    out["acct_types"] = int(m.group(1))
                m = re.match(r"\|\s*Methods in accounted game types\s*\|\s*\*\*(\d+) / \d+ \(100%\)\*\*\s*\|", line)
                if m:
                    out["acct_methods"] = int(m.group(1))
    except OSError:
        pass
    return out


def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Compute the RE-coverage percentages for the corpus (live census).")
    ap.add_argument("asm", nargs="?", default=None,
                    help="path to Assembly-CSharp.dll (default: $ASM or the Steam path, "
                         "same resolution as tools/stock-sync.sh)")
    ap.add_argument("docs", nargs="?", default=None,
                    help="docs directory to scan (default: docs)")
    ap.add_argument("--json", action="store_true",
                    help="emit a machine-readable JSON object instead of the human report")
    ap.add_argument("--history", nargs="?", const="census-history.csv", default=None,
                    metavar="FILE",
                    help="append the percentages to a CSV so census numbers can be "
                         "tracked over time (default name: census-history.csv; "
                         "date column is UTC)")
    return ap.parse_args(argv)


def pct(n, total):
    return 100.0 * n / total if total else 0.0


def main():
    args = parse_args(sys.argv[1:])
    history = args.history
    as_json = args.json
    asm = args.asm if args.asm else default_asm()
    docs = args.docs if args.docs else os.path.join(REPO, "docs")

    if not os.path.isfile(asm):
        print(f"error: assembly not found at {asm}", file=sys.stderr)
        print("pass the path as argv[1] or set $ASM", file=sys.stderr)
        return 2

    # 1. Live coverage census over the docs tree (report to a private temp
    #    file so the scan never sees a stale extra file inside docs/).
    fd, tmp_report = tempfile.mkstemp(prefix="census-pct-coverage-", suffix=".md")
    os.close(fd)
    try:
        rc, _, stderr = run_mono("Coverage.exe", asm, docs, tmp_report)
        if rc != 0:
            print("error: Coverage.exe failed:", file=sys.stderr)
            print(stderr, file=sys.stderr)
            return rc
        cov = parse_coverage(stderr)
        reached_types = parse_report_reached_types(tmp_report)
        accounted = parse_report_accounted(tmp_report)
    finally:
        if os.path.exists(tmp_report):
            os.unlink(tmp_report)

    # 2. Whole-assembly census (for the unreached remainder).
    rc, stdout, census_stderr = run_mono("Census.exe", asm)
    if rc != 0:
        print("error: Census.exe failed:", file=sys.stderr)
        print(census_stderr, file=sys.stderr)
        return rc
    cen = parse_census(stdout)
    all_types = cen.get("AllTypes (incl nested)", 0)
    all_methods = cen.get("AllMethodsWithBody", 0)

    if not as_json:
        g = cov["game_types"]
        print("RE coverage of the 7dtd-engine-research corpus (live census)\n")
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
            print("\nWhole assembly (100% view, Assembly-CSharp only):")
            if accounted["acct_types"]:
                print("  types   %6d total; %d accounted (100%%) - reached documented + unreached classified" % (
                    all_types, accounted["acct_types"]))
            if reached_types:
                print("  reached in the server call graph: %d types / %d methods" % (
                    reached_types, cov["reached_methods"]))
            if accounted["acct_methods"]:
                print("  methods %6d total; %d in accounted game types (100%%)" % (
                    all_methods, accounted["acct_methods"]))
            print("  compiler-generated and third-party/BCL types are excluded by design")

    result = {
        "reached_game_types": cov["game_types"],
        "narrated": cov["narrated"],
        "catalogued": cov["catalogued"],
        "classified": cov["classified"],
        "unaccounted": cov["unaccounted"],
        "not_deeply_narrated": cov["catalogued"] + cov["classified"],
        "all_types": all_types,
        "accounted_types": accounted.get("acct_types"),
        "all_methods": all_methods,
        "accounted_methods": accounted.get("acct_methods"),
        "reached_methods": cov["reached_methods"],
        "narrated_pct": round(pct(cov["narrated"], cov["game_types"]), 1),
    }
    if history:
        row = "%s,%d,%d,%d,%d,%d,%.1f%%\n" % (
            datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
            result["reached_game_types"], result["narrated"], result["catalogued"],
            result["classified"], result["unaccounted"], result["narrated_pct"])
        header = "date,game_types,narrated,catalogued,classified,unaccounted,narrated_pct\n"
        if not os.path.exists(history):
            with open(history, "w") as fh:
                fh.write(header)
        with open(history, "a") as fh:
            fh.write(row)
        # Keep stdout pure JSON under --json: consumers pipe the report
        # straight into a parser.
        print("history appended to", history, file=sys.stderr if as_json else sys.stdout)
    if as_json:
        print(json.dumps(result, indent=2))
        return 0

    if cov["unaccounted"]:
        print("\nWARNING: unaccounted reached game types > 0 - the RE surface is not at 100%.")
    elif not accounted.get("acct_types") or not accounted.get("acct_methods"):
        print("\nWARNING: could not parse the whole-assembly accounting rows from the report.")
    else:
        print("\n100%: every reached game type is narrated/catalogued/classified, and every")
        print("unreached game type is classified (client/editor/lifecycle/reflection/dead).")
        print("Compiler-generated + third-party/BCL types are excluded by design.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
