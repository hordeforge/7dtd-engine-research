#!/usr/bin/env python3
"""Pin files must not carry a non-finite number, and the gates must say so.

`json.loads` accepts `NaN`, `Infinity`, `-Infinity`, and a decimal literal that
overflows binary64 (`1e999`). The C# extractor writes NaN for a float constant
that is not finite, and every numeric pin in the corpus is checked as
`abs(got - want) > tol`: with a NaN on the left that comparison is False, so a
NaN pin passes the gate that exists to catch it. The fix is at the load, in
`tooling.load_json`, and this gate pins that every pin reader goes through it.

Usage: python3 tools/tests/test_json_pins_finite.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

FACTS = _common.TOOLS / "data" / "stock_facts.json"
CHECKER = _common.TOOLS / "tests" / "check_stock_facts.py"
NON_FINITE = ("NaN", "Infinity", "-Infinity", "1e999")


def loads_rejects(tooling: object) -> list[str]:
    bad: list[str] = []
    for literal in NON_FINITE:
        try:
            tooling.loads_json(f'{{"behaviour": {{"world_water_level": {literal}}}}}')  # type: ignore[attr-defined]
        except tooling.NonFiniteNumberError:  # type: ignore[attr-defined]
            continue
        except Exception as exc:
            bad.append(f"{literal}: raised {type(exc).__name__}, want NonFiniteNumberError")
        else:
            bad.append(f"{literal}: accepted as a pin value")
    for literal in ("62.88", "0", "-1.5e-3", "1e5", "300"):
        try:
            tooling.loads_json(f'{{"v": {literal}}}')  # type: ignore[attr-defined]
        except Exception as exc:
            bad.append(f"finite literal {literal} rejected: {exc}")
    return bad


def checker_rejects(bad: list[str]) -> None:
    """A facts file whose water level is NaN must fail the gate, not pass it.

    The gate's own verdict is asserted on the message, not the exit code: a
    checkout without the Mono.Cecil dumpers fails the run for an unrelated
    reason (the assembly cannot be re-read), and that would mask this one.
    """
    text = FACTS.read_text(encoding="utf-8")
    original = json.loads(text)
    wanted = json.dumps(original["behaviour"]["world_water_level"])
    for literal in NON_FINITE:
        probe = text.replace(wanted, literal, 1)
        if probe == text:
            bad.append(f"control substitution failed: {wanted} is not in the committed facts")
            continue
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", dir=_common.scratch_dir(), delete=False
        ) as fh:
            fh.write(probe)
            path = fh.name
        try:
            proc = _common.run_cmd(
                [sys.executable, str(CHECKER), "--facts", path, "--skip-siblings"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        finally:
            os.unlink(path)
        out = (proc.stdout or "") + (proc.stderr or "")
        if "Traceback" in out:
            bad.append(f"world_water_level={literal}: raw traceback escaped:\n{out}")
        elif proc.returncode == 0:
            bad.append(f"world_water_level={literal}: checker passed a non-finite pin:\n{out}")
        elif not any(m in out for m in ("non-finite literal", "overflows to infinity")):
            bad.append(
                f"world_water_level={literal}: failed for another reason, not the "
                f"non-finite load:\n{out}"
            )


def main() -> int:
    import tooling

    bad = loads_rejects(tooling)
    checker_rejects(bad)
    if bad:
        print("FAIL: non-finite pin values")
        for b in bad:
            print(f"  - {b}")
        return 1
    print(f"OK: {len(NON_FINITE)} non-finite pin spellings rejected at the load and by the gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
