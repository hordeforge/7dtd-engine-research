#!/usr/bin/env python3
"""check_stock_facts' baseline table and schema gate fire on what they claim to.

The gate's second job, beside matching doc pin sites, is to be the tripwire for a
TFP patch: a pin value that moves off the build the corpus was written against
must be reported by name, and a pin file written for another schema must be
refused before any field is read. Both were inline constants and an unread
`schema` key, so neither could be exercised; this drives the real functions over
synthetic pin files.

  - a drifted value in either table fails, naming the pin path
  - a value missing from the file (a renamed section) fails rather than raising
  - an absent schema is refused by main(); the supported one passes the check
  - a pin that still holds its baseline passes, so the table is not a tripwire
    that fires on the studied build

Usage: python3 tools/tests/test_stock_facts_baseline.py
"""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common
from _common import load_sibling

TOOLS = _common.TOOLS
SCRIPT = TOOLS / "tests" / "check_stock_facts.py"
FACTS = TOOLS / "data" / "stock_facts.json"
PINS = TOOLS / "data" / "xml_pins.json"

checker = load_sibling("check_stock_facts")


def failures(data: dict[str, Any], table: tuple[tuple[str, object], ...]) -> list[str]:
    errors: list[str] = []
    checker.check_baseline("stock_facts", data, table, errors)
    return errors


def run_gate(facts_path: Path) -> tuple[int, str]:
    proc = _common.run_cmd(
        [sys.executable, str(SCRIPT), "--facts", str(facts_path), "--skip-siblings"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    failures_found: list[str] = []

    def expect(condition: bool, label: str) -> None:
        if not condition:
            failures_found.append(label)

    facts = _common.load_json(FACTS)
    pins = _common.load_json(PINS)

    # The committed pins still hold the build the corpus was written against.
    expect(
        not failures(facts, checker.PIN_BASELINE),
        f"committed stock_facts.json fails its own baseline: {failures(facts, checker.PIN_BASELINE)}",
    )
    expect(
        not failures(pins, checker.XML_PIN_BASELINE),
        f"committed xml_pins.json fails its own baseline: {failures(pins, checker.XML_PIN_BASELINE)}",
    )

    # A drifted value is reported by name, with the re-pin command.
    drifted = copy.deepcopy(facts)
    drifted["enums"]["game_prefs_members"] = 318
    drift_errors = failures(drifted, checker.PIN_BASELINE)
    expect(
        any("enums.game_prefs_members" in e and "318" in e for e in drift_errors),
        f"an enum count that moved is not named: {drift_errors}",
    )
    expect(
        any(checker.REPIN_HINT.split("'")[1] in e for e in drift_errors),
        f"a drifted pin carries no re-pin command: {drift_errors}",
    )

    # A float baseline moves by a value the extractor would really write.
    moved_water = copy.deepcopy(facts)
    moved_water["behaviour"]["world_water_level"] = 64.0
    expect(
        any(
            "behaviour.world_water_level" in e for e in failures(moved_water, checker.PIN_BASELINE)
        ),
        "a moved float pin is not reported",
    )
    # Rounding noise below the written precision is not drift.
    same_water = copy.deepcopy(facts)
    same_water["behaviour"]["world_water_level"] = 62.8800004
    expect(
        not any("world_water_level" in e for e in failures(same_water, checker.PIN_BASELINE)),
        "a float pin within FLOAT_TOLERANCE is reported as drift",
    )

    # A renamed section reads as a missing pin, not an AttributeError.
    renamed = copy.deepcopy(facts)
    del renamed["litenet"]
    expect(
        any("litenet.protocol_id" in e for e in failures(renamed, checker.PIN_BASELINE)),
        "a removed section is not reported as a missing pin",
    )

    # A float pin written as a string is a pin of the wrong type, and passes no
    # numeric comparison: the gate that exists to catch a bad pin must not
    # coerce one into agreement.
    for wrong in ("62.88", True):
        mistyped = copy.deepcopy(facts)
        mistyped["behaviour"]["world_water_level"] = wrong
        expect(
            any(
                "behaviour.world_water_level" in e for e in failures(mistyped, checker.PIN_BASELINE)
            ),
            f"a {type(wrong).__name__} pin passed a float baseline: {wrong!r}",
        )

    # Both tables name the same values the docs cite.
    for dotted, _ in checker.XML_PIN_BASELINE:
        expect(
            checker.pin_value(pins, dotted) is not None,
            f"xml_pins.json has no value at {dotted}",
        )
    for dotted, _ in checker.PIN_BASELINE:
        expect(
            checker.pin_value(facts, dotted) is not None,
            f"stock_facts.json has no value at {dotted}",
        )

    # main() refuses a pin file written for another schema, and the committed
    # one carries the version the gate reads.
    with tempfile.TemporaryDirectory(prefix="baseline-schema-", dir=_common.scratch_dir()) as td:
        out = Path(td) / "facts.json"
        bumped = copy.deepcopy(facts)
        bumped["schema"] = checker.STOCK_FACTS_SCHEMA + 1
        out.write_text(json.dumps(bumped), encoding="utf-8")
        rc, text = run_gate(out)
        expect(rc == 1, f"a schema the gate cannot read passed the gate (rc={rc})")
        expect(
            "schema" in text, f"the schema refusal does not name the schema: {text.strip()[:200]}"
        )

        unstamped = copy.deepcopy(facts)
        del unstamped["schema"]
        out.write_text(json.dumps(unstamped), encoding="utf-8")
        rc, text = run_gate(out)
        expect(rc == 1, f"a pin file with no schema passed the gate (rc={rc})")

    for label in failures_found:
        print(f"FAIL: {label}")
    if failures_found:
        return 1
    print(
        f"OK: {len(checker.PIN_BASELINE) + len(checker.XML_PIN_BASELINE)} pinned values baselined"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
