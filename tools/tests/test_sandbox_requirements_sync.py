#!/usr/bin/env python3
"""Pin uv.lock to the dependencies pyproject.toml declares.

The uv lock is the repo's dependency inventory and supply-chain gate (exact
versions + sha256 for dnfile/dncil/UnityPy and their transitives). That only
holds while the two files agree: a dep added to pyproject.toml without
re-locking installs from a lock without it; a lock entry stripped of its hashes
silently loses integrity checking. DLL-free, network-free.

Checked here:
  - every declared dep appears in the lock with an exact version
  - every locked registry package carries at least one sha256 (no hash-stripped
    hand edits)
  - the locked version satisfies the bound pyproject.toml declares for it, so
    the floors/ceilings there and the reviewed lock cannot drift apart. The
    bound is a series, not a floor: ~=1.25.0 admits 1.25.x and rejects 1.26
  - every locked package comes from the registry (no git/url/path sources)
  - every dep the lock records for the sandbox project is declared
  - every non-stdlib import under tools/ is declared in pyproject.toml, so no
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
import tomllib
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
PYPROJECT = TOOLS.parent / "pyproject.toml"
LOCK = TOOLS.parent / "uv.lock"
# Every tool source in the tree, not just the sandbox: a tool anywhere under
# tools/ that reaches for a package pyproject.toml never declared rides in on
# an undeclared transitive. LOCAL is the sibling-module set, taken tree-wide
# because tools/ root modules are imported from subdirectories (tests/ imports
# tooling and shader_blob_dump; research_diff imports steam/steam_manifest).
# The sandbox's own .venv is excluded: it holds the installed packages.
IMPORTERS = sorted(p for p in TOOLS.rglob("*.py") if ".venv" not in p.parts)
LOCAL = {p.stem for p in IMPORTERS}

REQ_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(.*)$")
# The only bound forms pyproject.toml may use. Anything else (extras, env
# markers, URLs, wildcards) resolves in ways this gate cannot check, so it is a
# hard error rather than a silently unverified declaration.
SPEC_RE = re.compile(r"^(~=|>=|<=|==|>|<)\s*([0-9][0-9A-Za-z.]*)$")


def canon(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def release(version: str) -> tuple[int, ...]:
    """Dotted numeric version as a tuple; '1.0' and '1.0.0' compare equal."""
    return tuple(int(part) for part in version.split("."))


def bounded(version: str, spec: str) -> tuple[bool, str]:
    """Does a locked version satisfy a declared bound? (ok, reason)."""
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
        # what pyproject.toml promises: a re-lock cannot jump a series under
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


def parse_declared(text: str) -> dict[str, str]:
    """Map canonical dep name -> its bound from pyproject.toml's dependencies."""
    out: dict[str, str] = {}
    for line in tomllib.loads(text)["project"]["dependencies"]:
        m = REQ_RE.match(line.strip())
        if m is None:
            raise ValueError(f"unparseable dependency: {line!r}")
        out[canon(m.group(1))] = m.group(2).strip()
    return out


def parse_lock(text: str) -> tuple[dict[str, dict[str, Any]], set[str]]:
    """(canonical name -> {version, hashes, registry}, the project's direct deps)."""
    pins: dict[str, dict[str, Any]] = {}
    direct: set[str] | None = None
    for pkg in tomllib.loads(text).get("package", []):
        source = pkg.get("source", {})
        if "virtual" in source:
            if direct is not None:
                raise ValueError("more than one project entry in the lock")
            direct = {canon(dep["name"]) for dep in pkg.get("dependencies", [])}
            continue
        artifacts = [pkg["sdist"]] if "sdist" in pkg else []
        artifacts += pkg.get("wheels", [])
        hashes = sum(1 for a in artifacts if str(a.get("hash", "")).startswith("sha256:"))
        pins[canon(pkg["name"])] = {
            "version": str(pkg.get("version", "")),
            "hashes": hashes,
            "registry": "registry" in source,
        }
    if direct is None:
        raise ValueError("no project entry in the lock")
    return pins, direct


def check(declared: dict[str, str], lock_text: str) -> list[str]:
    bad: list[str] = []
    try:
        pins, direct = parse_lock(lock_text)
    except (ValueError, KeyError, tomllib.TOMLDecodeError) as exc:
        return [f"unparseable lock: {exc}"]
    for dep in sorted(declared):
        if dep not in pins:
            bad.append(
                f"{dep}: declared in pyproject.toml but absent from the lock (re-run uv lock)"
            )
            continue
        ok, reason = bounded(str(pins[dep]["version"]), declared[dep])
        if not ok:
            bad.append(
                f"{dep}: locked {pins[dep]['version']} {reason} "
                "(pyproject.toml and the lock disagree: re-run uv lock)"
            )
    for name, meta in sorted(pins.items()):
        if not meta["registry"]:
            bad.append(f"{name}: locked from a non-registry source")
        elif meta["hashes"] == 0:
            bad.append(f"{name}: locked without any sha256 (integrity check lost)")
    for name in sorted(direct - declared.keys()):
        bad.append(f"{name}: locked as a direct dependency but not declared in pyproject.toml")
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
    """Imports a tool relies on that pyproject.toml does not declare."""
    bad = []
    for path in sources:
        for mod in sorted(third_party_imports(path, local)):
            if canon(mod) not in declared:
                bad.append(f"{mod}: imported by {path.name} but not declared in pyproject.toml")
    return bad


def self_test() -> tuple[list[str], int]:
    """Mutation checks: each crafted defect must be caught, the clean lock must pass."""

    def h64(c: str) -> str:
        return c * 64

    def pkg(name: str, version: str, hashes: str, source: str = 'registry = "x"') -> str:
        return (
            f'[[package]]\nname = "{name}"\nversion = "{version}"\n'
            f"source = {{ {source} }}\n{hashes}\n"
        )

    def project(*deps: str) -> str:
        listed = ", ".join(f'{{ name = "{d}" }}' for d in deps)
        return (
            f'[[package]]\nname = "sandbox"\nversion = "0"\n'
            f'source = {{ virtual = "." }}\ndependencies = [{listed}]\n'
        )

    def sdist(c: str) -> str:
        return f'sdist = {{ url = "u", hash = "sha256:{h64(c)}" }}'

    wheels_bc = f'wheels = [{{ url = "u", hash = "sha256:{h64("b")}" }}, {{ url = "v", hash = "sha256:{h64("c")}" }}]'
    clean = project("alpha") + pkg("alpha", "1.0.0", sdist("a")) + pkg("beta", "2.0", wheels_bc)
    cases = [
        ("clean lock", {"alpha": ""}, clean, []),
        ("clean lock with bounds", {"alpha": "~=1.0", "beta": ">=2.0"}, clean, []),
        (
            "patch release inside the bound series",
            {"alpha": "~=1.0.2"},
            project("alpha") + pkg("alpha", "1.0.9", sdist("a")),
            [],
        ),
        (
            "minor jump outside the bound series",
            {"alpha": "~=1.0.2"},
            project("alpha") + pkg("alpha", "1.1.0", sdist("a")),
            ["outside the ~=1.0.2 series"],
        ),
        (
            "below the bound floor",
            {"alpha": "~=1.0.2"},
            project("alpha") + pkg("alpha", "1.0.1", sdist("a")),
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
            project("alpha") + pkg("alpha", "1.0.0", 'sdist = { url = "u" }'),
            ["alpha"],
        ),
        (
            "transitive hash stripped",
            {"alpha": ""},
            project("alpha") + pkg("alpha", "1.0.0", sdist("a")) + pkg("beta", "2.0", ""),
            ["beta"],
        ),
        (
            "ghost direct",
            {},
            project("alpha") + pkg("alpha", "1.0.0", sdist("a")),
            ["not declared"],
        ),
        (
            "git source sneaks in",
            {"alpha": ""},
            project("alpha") + pkg("alpha", "1.0.0", "", 'git = "https://x/alpha"'),
            ["non-registry source"],
        ),
        (
            "no project entry",
            {"alpha": ""},
            pkg("alpha", "1.0.0", sdist("a")),
            ["no project entry"],
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

    # Import-side mutations: a tool must not reach a package pyproject.toml
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
        declared = parse_declared(PYPROJECT.read_text(encoding="utf-8"))
    except (ValueError, KeyError, tomllib.TOMLDecodeError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        return 1
    lock_text = LOCK.read_text(encoding="utf-8")
    real = check(declared, lock_text)
    for f in real:
        print("FAIL:", f, file=sys.stderr)
    undeclared = undeclared_imports(declared, IMPORTERS, LOCAL)
    for f in undeclared:
        print("FAIL:", f, file=sys.stderr)
    if failures or real or undeclared:
        return 1

    pins, direct = parse_lock(lock_text)
    hashed = sum(1 for m in pins.values() if m["hashes"] > 0)
    print(
        f"OK: sandbox uv.lock matches pyproject.toml ({', '.join(sorted(direct))}); "
        f"{hashed}/{len(pins)} pins sha256-hashed, {len(IMPORTERS)} tools import only "
        f"declared packages; {n_cases} mutations caught"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
