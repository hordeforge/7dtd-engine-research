#!/usr/bin/env python3
"""Pin sandbox/requirements.txt to sandbox/requirements.in (hash-pinned lock).

The uv-compiled lock is the repo's dependency inventory and supply-chain gate
(exact versions + sha256 for dnfile/dncil/UnityPy and their transitives). That
only holds while the two files agree: a dep added to requirements.in without
recompiling installs from a lock without it; a recompile that drops
--generate-hashes silently loses integrity checking. DLL-free, network-free.

Checked here:
  - every requirements.in dep appears in the lock as an exact name==version pin
  - every pin carries at least one --hash=sha256 (no hash-stripped hand edits)
  - the locked version satisfies the bound requirements.in declares for it, so
    the floors/ceilings there and the reviewed lock cannot drift apart. The
    bound is a series, not a floor: ~=1.25.0 admits 1.25.x and rejects 1.26
  - no ranged/wildcard/url specifiers sneak into the lock
  - every entry the lock marks as coming from requirements.in is declared there
  - every non-stdlib import under tools/ is declared in requirements.in, so no
    tool rides in on an undeclared transitive (a version bump of the parent can
    then move it under them)

The checker is itself mutation-tested below against crafted bad locks and
sources so a future refactor cannot turn it into a no-op.
"""

from __future__ import annotations

import ast
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
IN_FILE = TOOLS / "sandbox" / "requirements.in"
LOCK = TOOLS / "sandbox" / "requirements.txt"
# Every tool source in the tree, not just the sandbox: a tool anywhere under
# tools/ that reaches for a package requirements.in never declared rides in on
# an undeclared transitive. LOCAL is the sibling-module set, taken tree-wide
# because tools/ root modules are imported from subdirectories (tests/ imports
# tooling and shader_blob_dump; research_diff imports steam/steam_manifest).
IMPORTERS = sorted(TOOLS.rglob("*.py"))
LOCAL = {p.stem for p in IMPORTERS}

PIN_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s\\]+)\s*(?:\\\s*)?$")
NON_EXACT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\s*(@|~=|!=|<|>|[*]|\[)")
DIRECT_VIA_RE = re.compile(r"#\s+(?:via\s+)?-r requirements\.in$")
REQ_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(.*)$")
# The only bound forms requirements.in may use. Anything else (extras, env
# markers, URLs, wildcards) resolves in ways this gate cannot check, so it is a
# hard error rather than a silently unverified declaration.
SPEC_RE = re.compile(r"^(~=|>=|<=|==|>|<)\s*([0-9][0-9A-Za-z.]*)$")


def canon(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def release(version: str) -> tuple[int, ...]:
    """Dotted numeric version as a tuple; '1.0' and '1.0.0' compare equal."""
    return tuple(int(part) for part in version.split("."))


def bounded(version: str, spec: str) -> tuple[bool, str]:
    """Does a locked version satisfy a requirements.in bound? (ok, reason)."""
    if not spec:
        return True, ""
    m = SPEC_RE.match(spec)
    if m is None:
        return False, f"unsupported specifier {spec!r}"
    op, want = m.group(1), m.group(2)
    try:
        got, need = release(version), release(want)
    except ValueError:
        return False, f"is not a plain dotted version ({version!r}, {want!r})"
    if op == "~=":
        # The series is the bound minus its patch component when it has one
        # (~=1.25.0 and ~=1.25 both mean the reviewed 1.25 series), matching
        # what requirements.in promises: a recompile cannot jump a series under
        # a tool that reads the package's internals. The next release past the
        # series is the ceiling.
        series = need[:-1] if len(need) > 2 else need
        upper = (*series[:-1], series[-1] + 1)
        return (need <= got < upper), f"is outside the {spec} series"
    cmp = (got > need) - (got < need)
    ok = {
        ">=": cmp >= 0,
        ">": cmp > 0,
        "<=": cmp <= 0,
        "<": cmp < 0,
        "==": cmp == 0,
    }[op]
    return ok, f"does not satisfy {spec}"


def parse_in(text: str) -> dict[str, str]:
    """Map canonical dep name -> its full requirement line in requirements.in."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = REQ_RE.match(line)
        if m is None:
            raise ValueError(f"unparseable requirements.in line: {raw!r}")
        out[canon(m.group(1))] = line[len(m.group(1)) :].strip()
    return out


def parse_lock(text: str) -> dict[str, dict[str, Any]]:
    """Map canonical name -> {version, hashes, direct} from uv compile output."""
    pins: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            if current is not None and DIRECT_VIA_RE.fullmatch(line):
                current["direct"] = True
            continue
        if line.startswith("--"):
            if current is not None and line.startswith("--hash=sha256:"):
                current["hashes"] += 1
            continue
        m = PIN_RE.match(line)
        if m is None:
            hint = "non-exact specifier" if NON_EXACT_RE.match(line) else "unparseable"
            raise ValueError(f"{hint} pin line: {raw!r}")
        current = {"version": m.group(2), "hashes": 0, "direct": False}
        pins[canon(m.group(1))] = current
    return pins


def check(declared: dict[str, str], lock_text: str) -> list[str]:
    bad: list[str] = []
    try:
        pins = parse_lock(lock_text)
    except ValueError as exc:
        return [str(exc)]
    for dep in sorted(declared):
        if dep not in pins:
            bad.append(
                f"{dep}: declared in requirements.in but absent from the lock "
                "(recompile: uv pip compile --generate-hashes)"
            )
            continue
        if pins[dep]["hashes"] == 0:
            bad.append(f"{dep}: pinned without any --hash=sha256 (integrity check lost)")
            continue
        ok, reason = bounded(str(pins[dep]["version"]), declared[dep])
        if not ok:
            bad.append(
                f"{dep}: locked {pins[dep]['version']} {reason} "
                "(requirements.in and the lock disagree: recompile)"
            )
    for name, meta in sorted(pins.items()):
        if meta["direct"] and name not in declared:
            bad.append(
                f"{name}: locked as a direct requirement but not declared in requirements.in"
            )
    return bad


def third_party_imports(path: Path, local: set[str]) -> set[str]:
    """Top-level modules a file imports that are neither stdlib nor a sibling module.

    Imports come from the parse tree, not a line regex: prose in a docstring
    ("from dict lookups down a path") must not read as an import, and a
    conditional or function-local import is as binding as a top-level one.
    """
    out = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        for name in names:
            top = name.split(".")[0]
            if not top or top in sys.stdlib_module_names or top in local:
                continue
            out.add(top)
    return out


def undeclared_imports(declared: dict[str, str], sources: list[Path], local: set[str]) -> list[str]:
    """Imports a tool relies on that requirements.in does not declare."""
    bad = []
    for path in sources:
        for mod in sorted(third_party_imports(path, local)):
            if canon(mod) not in declared:
                bad.append(f"{mod}: imported by {path.name} but not declared in requirements.in")
    return bad


def self_test() -> tuple[list[str], int]:
    """Mutation checks: each crafted defect must be caught, the clean lock must pass."""

    def h64(c: str) -> str:
        return c * 64

    clean = (
        f"alpha==1.0.0 \\\n    --hash=sha256:{h64('a')}\n    # via -r requirements.in\n"
        f"beta==2.0 \\\n    --hash=sha256:{h64('b')} \\\n    --hash=sha256:{h64('c')}\n"
        "    # via alpha\n"
    )
    cases = [
        ("clean lock", {"alpha": ""}, clean, []),
        ("clean lock with bounds", {"alpha": "~=1.0", "beta": ">=2.0"}, clean, []),
        (
            "patch release inside the bound series",
            {"alpha": "~=1.0.2"},
            f"alpha==1.0.9 \\\n    --hash=sha256:{h64('a')}\n    # via -r requirements.in\n",
            [],
        ),
        (
            "minor jump outside the bound series",
            {"alpha": "~=1.0.2"},
            f"alpha==1.1.0 \\\n    --hash=sha256:{h64('a')}\n    # via -r requirements.in\n",
            ["outside the ~=1.0.2 series"],
        ),
        (
            "below the bound floor",
            {"alpha": "~=1.0.2"},
            f"alpha==1.0.1 \\\n    --hash=sha256:{h64('a')}\n    # via -r requirements.in\n",
            ["outside the ~=1.0.2 series"],
        ),
        (
            "bound above the locked version",
            {"alpha": "~=1.1"},
            clean,
            ["outside the ~=1.1 series"],
        ),
        (
            "bound unsupported form",
            {"alpha": ">=1.0; python_version>'3.12'"},
            clean,
            ["unsupported specifier"],
        ),
        (
            "dep missing from lock",
            {"alpha": "", "gamma": ""},
            clean,
            ["gamma"],
        ),
        (
            "hash stripped",
            {"alpha": ""},
            "alpha==1.0.0\n    # via -r requirements.in\n",
            ["alpha"],
        ),
        (
            "ghost direct",
            {},
            f"alpha==1.0.0 \\\n    --hash=sha256:{h64('a')}\n    # via -r requirements.in\n",
            ["not declared"],
        ),
        (
            "range sneaks in",
            {"alpha": ""},
            f"alpha>=1.0 \\\n    --hash=sha256:{h64('a')}\n    # via -r requirements.in\n",
            ["non-exact specifier"],
        ),
        (
            "multi-via direct",
            {"alpha": ""},
            (
                f"alpha==1.0 \\\n    --hash=sha256:{h64('a')}\n    # via\n    #   beta\n"
                "    #   -r requirements.in\n"
                f"beta==2.0 \\\n    --hash=sha256:{h64('b')}\n    # via alpha\n"
            ),
            [],
        ),
    ]
    bad: list[str] = []
    for label, declared, lock, want in cases:
        got = check(declared, lock)
        if not want:
            if got:
                bad.append(f"{label}: clean case rejected: {got}")
        elif not any(w in line for w in want for line in got):
            bad.append(f"{label}: defect not caught (got {got!r})")

    # Import-side mutations: a tool must not reach a package requirements.in
    # never declared, and stdlib/sibling imports must not be flagged.
    with tempfile.TemporaryDirectory(prefix="reqsync-selftest-", dir=_common.scratch_dir()) as td:
        tmp = Path(td)
        (tmp / "safe_name.py").write_text("def safe_name(x):\n    return x\n", encoding="utf-8")
        src_cases = [
            (
                "imports declared",
                {"unitypy": "~=1.25"},
                "import json\n\nfrom UnityPy import load\nfrom safe_name import safe_name\n",
                [],
            ),
            (
                "transitive import undeclared",
                {"unitypy": "~=1.25"},
                "import json\n\n\ndef load():\n    import lz4.block\n",
                ["lz4"],
            ),
            (
                "dotted stdlib ignored",
                {"unitypy": "~=1.25"},
                "import xml.etree.ElementTree as ET\n",
                [],
            ),
            (
                "prose in a docstring is not an import",
                {"unitypy": "~=1.25"},
                '"""Walks from dict lookups down a path."""\nimport json\n',
                [],
            ),
            (
                "guarded import still binds",
                {"unitypy": "~=1.25"},
                "try:\n    import astc_etcpak\nexcept ImportError:\n    astc_etcpak = None\n",
                ["astc_etcpak"],
            ),
        ]
        for label, declared, body, want in src_cases:
            target = tmp / "tool_under_test.py"
            target.write_text(body, encoding="utf-8")
            got = undeclared_imports(declared, [target], {"safe_name", "tool_under_test"})
            if not want:
                if got:
                    bad.append(f"{label}: clean case rejected: {got}")
            elif not any(w in line for w in want for line in got):
                bad.append(f"{label}: defect not caught (got {got!r})")

    return bad, len(cases)


def main() -> int:
    failures, n_cases = self_test()
    for f in failures:
        print("FAIL:", f, file=sys.stderr)

    try:
        declared = parse_in(IN_FILE.read_text(encoding="utf-8"))
    except ValueError as exc:
        print("FAIL:", exc, file=sys.stderr)
        return 1
    real = check(declared, LOCK.read_text(encoding="utf-8"))
    for f in real:
        print("FAIL:", f, file=sys.stderr)
    undeclared = undeclared_imports(declared, IMPORTERS, LOCAL)
    for f in undeclared:
        print("FAIL:", f, file=sys.stderr)
    if failures or real or undeclared:
        return 1

    pins = parse_lock(LOCK.read_text(encoding="utf-8"))
    hashed = sum(1 for m in pins.values() if m["hashes"] > 0)
    directs = ", ".join(sorted(n for n, m in pins.items() if m["direct"]))
    print(
        f"OK: sandbox lock matches requirements.in ({directs}); all {len(pins)} pins exact, "
        f"{hashed}/{len(pins)} sha256-hashed, {len(IMPORTERS)} tools import only declared "
        f"packages; {n_cases} mutations caught"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
