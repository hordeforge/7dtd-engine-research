#!/usr/bin/env python3
"""Link/citation gates fail loudly on files they cannot read OR cannot resolve.

cross_repo_links.py and zdtd_cite_check.py used to swallow per-file OSError
and continue, so a gate could print "OK: all links resolve" while one or more
files were never checked. Fixtures pin the fixed contracts:

  - an unreadable file (a dangling symlink, so the probe works for root too)
    inside a scanned repo must FAIL the run with an explicit UNREADABLE line
    naming the file - never a silent pass and never a traceback.
  - a BROKEN cross-repo link / research citation must FAIL and name the file
    and the missing target, while the same link/citation aimed at a real
    document passes. Without the broken-vs-real pair a regression in the
    detector (regex, existence check) could never fire and every clean tree
    would keep passing vacuously.
  - a file holding bytes that are not valid UTF-8 is read, not fatal: the
    decode error is a ValueError the OSError handlers never saw, and the gate
    died on a traceback.
  - a link spelled NFD to a document committed NFC resolves: a macOS checkout
    writes the decomposed form, and byte equality reported a live document as
    broken.

Usage: python3 tools/tests/test_gate_unreadable_files.py
"""

import os
import sys
import tempfile
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = str(_common.TOOLS)
CROSS = os.path.join(TOOLS, "cross_repo_links.py")
CITES = os.path.join(TOOLS, "zdtd_cite_check.py")
# A real docs/ file in this repo, used as the resolves-fine citation control.
REAL_DOC = "network.md"


def run(script: str, *argv: str) -> tuple[int, str]:
    proc = _common.run_cmd(
        [sys.executable, script, *argv],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout + proc.stderr


def build_repo(root: str) -> str:
    """A minimal 7dtd-loadgen stand-in: one clean doc, one clean src file."""
    repo = os.path.join(root, "7dtd-loadgen")
    os.makedirs(repo)
    with open(os.path.join(repo, "clean.md"), "w", encoding="utf-8") as f:
        f.write("prose only\n")
    with open(os.path.join(repo, "probe.py"), "w", encoding="utf-8") as f:
        f.write("# no citations\n")
    return repo


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def dangling(path: str) -> bool:
    """A symlink to a missing target; False when the host refuses symlinks.

    Windows only lets an unprivileged process create a symlink with Developer
    Mode on, so the case is reported as not exercised rather than crashing the
    gate; the rest of the fixtures still run.
    """
    try:
        os.symlink("gone-target", path)
    except OSError:
        return False
    return True


def main() -> int:
    bad: list[str] = []
    skipped: list[str] = []
    with tempfile.TemporaryDirectory(prefix="gate-unreadable-", dir=_common.scratch_dir()) as tmp:
        repo = build_repo(tmp)

        # Positive controls: clean tree passes both gates.
        rc, out = run(CROSS, "--root", tmp)
        if rc != 0 or "UNREADABLE" in out or "Traceback" in out:
            bad.append(f"cross_repo_links failed on a clean tree (rc={rc}):\n{out}")
        rc, out = run(CITES, "--root", tmp)
        if rc != 0 or "UNREADABLE" in out or "Traceback" in out:
            bad.append(f"zdtd_cite_check failed on a clean tree (rc={rc}):\n{out}")

        # Detector liveness: a broken cross-repo link must FAIL and name the
        # file and the missing target; the same link to a real sibling doc
        # must pass (a detector that cannot fire would leave every clean
        # tree green forever). The target doc carries a REAL research-doc
        # name because the citation gate resolves names against this repo's
        # docs/, not against the fixture tree.
        research_docs = os.path.join(tmp, "7dtd-engine-research", "docs")
        os.makedirs(research_docs)
        write(os.path.join(research_docs, REAL_DOC), "link target\n")
        linked = os.path.join(repo, "links.md")
        write(
            linked,
            f"[good](../7dtd-engine-research/docs/{REAL_DOC})\n"
            "[bad](../7dtd-engine-research/docs/ghost.md)\n",
        )
        rc, out = run(CROSS, "--root", tmp)
        if rc != 1 or "BROKEN" not in out or "links.md" not in out or "ghost.md" not in out:
            bad.append(f"cross_repo_links passed despite broken link (rc={rc}):\n{out}")
        write(linked, f"[good](../7dtd-engine-research/docs/{REAL_DOC})\n")
        rc, out = run(CROSS, "--root", tmp)
        if rc != 0 or "BROKEN" in out:
            bad.append(f"cross_repo_links failed on a resolved link (rc={rc}):\n{out}")

        # A link spelled NFD (what a macOS checkout writes) to a document
        # committed NFC: same document, two spellings, and byte equality called
        # it BROKEN.
        accented = "café-notes.md"
        nfd = unicodedata.normalize("NFD", accented)
        assert nfd != accented, "fixture must be a decomposed spelling"
        write(os.path.join(research_docs, accented), "accented link target\n")
        write(linked, f"[a](../7dtd-engine-research/docs/{nfd})\n")
        rc, out = run(CROSS, "--root", tmp)
        if rc != 0 or "BROKEN" in out:
            bad.append(f"cross_repo_links failed on an NFD-spelled link to NFC (rc={rc}):\n{out}")
        write(linked, f"[a](../7dtd-engine-research/docs/{nfd}-ghost.md)\n")
        rc, out = run(CROSS, "--root", tmp)
        if rc != 1 or "BROKEN" not in out:
            bad.append(f"cross_repo_links passed despite a broken NFD link (rc={rc}):\n{out}")
        os.unlink(os.path.join(research_docs, accented))
        write(linked, f"[good](../7dtd-engine-research/docs/{REAL_DOC})\n")

        # Same liveness pair for citations: a missing research doc must FAIL,
        # a citation of a real docs/ file must resolve.
        citer = os.path.join(repo, "cites.py")
        write(citer, f"# RE: {REAL_DOC}\n# RE: ghost-doc.md\n")
        rc, out = run(CITES, "--root", tmp)
        if rc != 1 or "ghost-doc.md" not in out or citer not in out:
            bad.append(f"zdtd_cite_check passed despite broken citation (rc={rc}):\n{out}")
        if f"BROKEN: {os.path.join(repo, 'cites.py')}: cites {REAL_DOC}" in out:
            bad.append(f"zdtd_cite_check flagged the real citation {REAL_DOC}:\n{out}")
        write(citer, f"# RE: {REAL_DOC}\n")
        rc, out = run(CITES, "--root", tmp)
        if rc != 0 or "BROKEN" in out:
            bad.append(f"zdtd_cite_check failed on a resolved citation (rc={rc}):\n{out}")

        # Unreadable markdown: the link gate must fail and name the file.
        locked_md = os.path.join(repo, "locked.md")
        if dangling(locked_md):
            rc, out = run(CROSS, "--root", tmp)
            if rc != 1 or "UNREADABLE" not in out or "locked.md" not in out:
                bad.append(f"cross_repo_links passed despite unreadable md (rc={rc}):\n{out}")
            if "Traceback" in out:
                bad.append(f"cross_repo_links crashed instead of reporting:\n{out}")
            os.unlink(locked_md)
        else:
            skipped.append("unreadable markdown")

        # Unreadable source: the citation gate must fail the same way.
        locked_py = os.path.join(repo, "locked.py")
        if dangling(locked_py):
            rc, out = run(CITES, "--root", tmp)
            if rc != 1 or "UNREADABLE" not in out or "locked.py" not in out:
                bad.append(f"zdtd_cite_check passed despite unreadable src (rc={rc}):\n{out}")
            if "Traceback" in out:
                bad.append(f"zdtd_cite_check crashed instead of reporting:\n{out}")
        else:
            skipped.append("unreadable source")
        if os.path.islink(locked_py):
            os.unlink(locked_py)

        # A markdown file holding a byte that is not valid UTF-8 (a latin-1
        # quote from a Windows editor). Read strictly it raises
        # UnicodeDecodeError, a ValueError the OSError handlers never see, so
        # the gate died on a traceback; both gates decode with errors="replace"
        # and keep checking the rest of the tree.
        latin1 = os.path.join(repo, "latin1.md")
        with open(latin1, "wb") as f:
            f.write(b"caf\xe9 notes\n")
        for script, label in ((CROSS, "cross_repo_links"), (CITES, "zdtd_cite_check")):
            rc, out = run(script, "--root", tmp)
            if "Traceback" in out:
                bad.append(f"{label} crashed on a non-UTF-8 markdown file:\n{out}")
            elif rc != 0:
                bad.append(f"{label} failed on a non-UTF-8 markdown file (rc={rc}):\n{out}")
        os.unlink(latin1)

    if bad:
        print("FAIL: gate unreadable-file handling")
        for b in bad:
            print("  - " + b)
        return 1
    print(
        "OK: link/citation gates FAIL on unreadable files (UNREADABLE line) and "
        "on broken links/citations; resolved ones pass"
    )
    if skipped:
        print(f"note: no symlink permission here, cases not exercised: {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
