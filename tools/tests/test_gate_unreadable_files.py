#!/usr/bin/env python3
"""Link/citation gates fail loudly on files they cannot read.

cross_repo_links.py and zdtd_cite_check.py used to swallow per-file OSError
and continue, so a gate could print "OK: all links resolve" while one or more
files were never checked. Fixtures pin the fixed contract: an unreadable file
(a dangling symlink, so the probe works for root too) inside a scanned repo
must FAIL the run with an explicit UNREADABLE line naming the file - never a
silent pass and never a traceback.

Usage: python3 tools/tests/test_gate_unreadable_files.py
"""

import os
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROSS = os.path.join(TOOLS, "cross_repo_links.py")
CITES = os.path.join(TOOLS, "zdtd_cite_check.py")


def run(script, *argv):
    proc = subprocess.run([sys.executable, script, *argv], capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def build_repo(root):
    """A minimal 7dtd-loadgen stand-in: one clean doc, one clean src file."""
    repo = os.path.join(root, "7dtd-loadgen")
    os.makedirs(repo)
    with open(os.path.join(repo, "clean.md"), "w", encoding="utf-8") as f:
        f.write("prose only\n")
    with open(os.path.join(repo, "probe.py"), "w", encoding="utf-8") as f:
        f.write("# no citations\n")
    return repo


def main():
    bad = []
    with tempfile.TemporaryDirectory(prefix="gate-unreadable-") as tmp:
        repo = build_repo(tmp)

        # Positive controls: clean tree passes both gates.
        rc, out = run(CROSS, "--root", tmp)
        if rc != 0 or "UNREADABLE" in out or "Traceback" in out:
            bad.append(f"cross_repo_links failed on a clean tree (rc={rc}):\n{out}")
        rc, out = run(CITES, "--root", tmp)
        if rc != 0 or "UNREADABLE" in out or "Traceback" in out:
            bad.append(f"zdtd_cite_check failed on a clean tree (rc={rc}):\n{out}")

        # Unreadable markdown: the link gate must fail and name the file.
        os.symlink("gone-target", os.path.join(repo, "locked.md"))
        rc, out = run(CROSS, "--root", tmp)
        if rc != 1 or "UNREADABLE" not in out or "locked.md" not in out:
            bad.append(f"cross_repo_links passed despite unreadable md (rc={rc}):\n{out}")
        if "Traceback" in out:
            bad.append(f"cross_repo_links crashed instead of reporting:\n{out}")
        os.unlink(os.path.join(repo, "locked.md"))

        # Unreadable source: the citation gate must fail the same way.
        os.symlink("gone-target", os.path.join(repo, "locked.py"))
        rc, out = run(CITES, "--root", tmp)
        if rc != 1 or "UNREADABLE" not in out or "locked.py" not in out:
            bad.append(f"zdtd_cite_check passed despite unreadable src (rc={rc}):\n{out}")
        if "Traceback" in out:
            bad.append(f"zdtd_cite_check crashed instead of reporting:\n{out}")

    if bad:
        print("FAIL: gate unreadable-file handling")
        for b in bad:
            print("  - " + b)
        return 1
    print(
        "OK: link/citation gates FAIL with an UNREADABLE line on unreadable files; clean trees pass"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
