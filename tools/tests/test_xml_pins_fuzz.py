#!/usr/bin/env python3
"""Seeded mutation fuzzer for the config-XML pin parsers in xml_pins.py.

`Data/Config/*.xml` is the operator's install on disk: a modded pack, a
half-synced depot, or a config rewritten by hand reaches these parsers as
arbitrary bytes, and each parser is a regex scan plus a float()/int()
conversion. `test_xml_pins_gate.py` pins specific malformations; this gate
covers the space between them:

  1. No exception escapes a parser or extract(): a value, tag or attribute
     that cannot be read degrades to a named `unparsed` skip, never a
     traceback out of a gate.
  2. Per-call time budget: markup nesting a parser re-scans (a
     <replace_passive_effect> inside a comment, a <traders> open tag inside
     another tag) must not turn into a quadratic walk.
  3. Parsed-value invariants: health keys are plain ints, markups are finite
     floats, and a value that failed to parse is never silently dropped --
     it is in `unparsed` and absent from the parsed dict.
  4. Determinism: the same text yields the same pins twice.
  5. extract() over a whole fake install: the source identity (bytes, sha256)
     agrees with the files on disk, and a garbage config file degrades to a
     named skip instead of aborting the other two sections.

Seeds are structure-aware: real-shaped entityclasses/traders/buffs markup
with the blocks the parsers look for, then mutations that hit the parsers'
boundaries (tag and attribute mangling, numeric-value mangling, nesting,
truncation, adversarial Unicode). Deterministic, stdlib-only, DLL-free.

`RE_FUZZ_SEED` replaces SEED, so a failing round replays from the seed the
FAIL line prints.

Usage: python3 tools/tests/test_xml_pins_fuzz.py
"""

from __future__ import annotations

import hashlib
import math
import os
import random
import sys
import tempfile
import time
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import TypeVar

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

sys.path.insert(0, str(_common.TOOLS))
import tooling
import xml_pins as src

SEED = 0x58B1A25
ROUNDS = 200  # mutation rounds per seed family
TIME_BUDGET_S = 5.0  # hard ceiling for ONE parse (hang-class guard)
SCRIPT = "tools/tests/test_xml_pins_fuzz.py"
T = TypeVar("T")
# The characters a config file can be attacked with, and the ones that decide
# where each regex cuts its input.
HOSTILE = "<>/\"'&;=:![]- \t\n" + "0123456789" + "+.eE"
UNI = "\u00e9\u4e2d\ufffd\u0301\u202e\ufeff\U0001f600"


def health_xml(*pairs: tuple[str, str]) -> str:
    """entityclasses-shaped text with a replace_passive_effect health ladder."""
    body = "".join(f'\n\t\t\t<property name="{n}" value="{v}" />' for n, v in pairs)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n<entities>\n'
        '\t<entity_class name="zombieMale">\n'
        "\t\t<replace_passive_effect>\n"
        f"{body}\n"
        "\t\t</replace_passive_effect>\n"
        "\t</entity_class>\n</entities>\n"
    )


def seeds() -> dict[str, list[str]]:
    """True shapes per config file, one entry per family the parser sees."""
    return {
        "entityclasses.xml": [
            health_xml(
                ("healthSlim", "125"),
                ("healthSlimCharged", "1000"),
                ("healthSlimFeral", "500"),
                ("healthSlim", "125"),
                ("healthSlimCharged", "1000"),
                ("healthSlimFeral", "500"),
            ),
            health_xml(("healthSlim", "125")),
            "<!-- no ladder here -->\n<entities><entity_class name='x'/></entities>\n",
            "",
        ],
        "traders.xml": [
            (
                '<?xml version="1.0"?>\n<traders buy_markup="1.5" sell_markdown="0.2"'
                ' count_inventory_of_trader="3">\n</traders>\n'
            ),
            '<traders buy_markup="0.9"/>\n',
            "not xml at all\n",
        ],
        "buffs.xml": [
            (
                '<?xml version="1.0"?>\n<buffs>\n'
                '\t<buff name="buffStatusHungry01" />\n'
                '\t<property StatComparePercCurrentToMax="true" stat="Food"'
                ' operation="GT" value="0.25" />\n'
                '\t<property StatComparePercCurrentToMax="true" stat="Water"'
                ' operation="GT" value="0.35" />\n</buffs>\n'
            ),
            "<buffs/>\n",
        ],
    }


def mutate(rng: random.Random, text: str) -> str:
    if not text:
        return rng.choice(HOSTILE + UNI) * rng.randint(1, 8)
    b = list(text)
    for _ in range(rng.randint(1, 6)):
        op = rng.choice(("char", "tag", "attr", "value", "nest", "trunc", "insert"))
        if not b:  # a trunc round emptied the text
            b += [rng.choice(HOSTILE + UNI)]
            continue
        i = rng.randrange(len(b))
        if op == "char":
            b[i] = rng.choice(HOSTILE + UNI)
        elif op == "tag":
            end = b.index(">", i) if ">" in b[i:] else len(b)
            b[i:end] = list(rng.choice(("name", "valu", "<replace_passive_effect", ">")))
        elif op == "attr":
            eq = b.index("=", i) if "=" in b[i:] else len(b)
            b[eq : eq + 1] = list(rng.choice(('="', '=" ', '="x', "='", "=", "")))
        elif op == "value":
            end = b.index('"', i) if '"' in b[i:] else len(b)
            b[i:end] = list(
                rng.choice(
                    ("nan", "inf", "-inf", "1e999", "1,5", "0x10", "1_0", "9" * 40, "", "-", "NaN")
                )
            )
        elif op == "nest":
            b[i:i] = list("<replace_passive_effect>" * rng.randint(1, 3))
        elif op == "trunc":
            del b[i:]
        else:
            b[i:i] = list(rng.choice(HOSTILE + UNI) * rng.randint(1, 12))
    return "".join(b)


def parse(spec: src.Section, text: str) -> tuple[dict[str, object], list[str]]:
    unparsed: list[str] = []
    parsed = spec.parse(text, unparsed)
    return parsed, unparsed


def timed(call: Callable[[], T]) -> T:
    t0 = time.monotonic()
    out = call()
    dt = time.monotonic() - t0
    if dt >= TIME_BUDGET_S:
        raise BudgetError(f"call took {dt:.1f}s (budget {TIME_BUDGET_S}s)")
    return out


def check_invariants(
    spec: src.Section, text: str, parsed: dict[str, object], unparsed: list[str], bad: list[str]
) -> None:
    """A parsed value is typed as its section promises, or it is a named skip."""
    for key, value in parsed.items():
        if not key:
            bad.append(f"{spec.name}: empty key survived")
            return
        if spec.name == "entityclasses_health":
            if not isinstance(value, int) or isinstance(value, bool):
                bad.append(f"{spec.name}: {key}={value!r} is not an int")
                return
            if not key.startswith("health"):
                bad.append(f"{spec.name}: key {key!r} is not a health* attribute")
                return
        else:
            if not isinstance(value, float) or not math.isfinite(value):
                bad.append(f"{spec.name}: {key}={value!r} is not a finite float")
                return
    for note in unparsed:
        if not note:
            bad.append(f"{spec.name}: empty unparsed skip")
            return
    again, again_unparsed = parse(spec, text)
    if again != parsed or again_unparsed != unparsed:
        bad.append(f"{spec.name}: parse is not deterministic")
        return
    # Constants are section identity, never parsed: a name of a skipped value
    # must not appear in the parsed dict, or --check would pin a value the
    # install no longer carries.
    for key in unparsed:
        if spec.name == "entityclasses_health" and key.split()[-1] in parsed:
            bad.append(f"{spec.name}: skipped value also pinned: {key!r}")
            return


def fuzz(rng: random.Random, bad: list[str], corpus: tooling.CorpusDigest) -> None:
    families = seeds()
    for spec in src.SECTION_SPECS:
        base = families[os.path.basename(spec.config)]
        for k in range(ROUNDS):
            text = mutate(rng, rng.choice(base)) if rng.random() < 0.85 else base[k % len(base)]
            corpus.add(text.encode("utf-8"))
            label = f"{spec.name} round {k}"
            try:
                parsed, unparsed = timed(partial(parse, spec, text))
            except BudgetError as exc:
                bad.append(f"{label}: {exc}")
                return
            except Exception as exc:
                bad.append(f"{label}: ESCAPED {type(exc).__name__}: {exc}")
                return
            check_invariants(spec, text, parsed, unparsed, bad)
            if bad:
                return


def regression_pins(tmp: Path, bad: list[str]) -> None:
    """Pin the shapes a modded or locale-formatted config really produces."""
    health = next(s for s in src.SECTION_SPECS if s.name == "entityclasses_health")
    traders = next(s for s in src.SECTION_SPECS if s.name == "traders_root")

    # Locale comma and an exponent-overflow value: a named skip, not a NaN pin.
    for value in ("1,5", "nan", "inf", "1e999", ""):
        text = f'<traders buy_markup="{value}" />\n'
        parsed, unparsed = parse(traders, text)
        if parsed:
            bad.append(f"traders_root: {value!r} was pinned as {parsed}")
        if value == "1,5" and not unparsed:
            bad.append("traders_root: a locale comma parsed with no unparsed skip")
    parsed, unparsed = parse(traders, '<traders buy_markup="1.5" sell_markdown="0.25" />')
    if parsed != {"buy_markup": 1.5, "sell_markdown": 0.25} or unparsed:
        bad.append(f"traders_root: valid markup mis-parsed as {parsed}, {unparsed}")

    # A health ladder outside replace_passive_effect is not the pinned block.
    text = '<entity_class name="x"><property name="healthSlim" value="999" /></entity_class>'
    parsed, unparsed = parse(health, text)
    if parsed:
        bad.append(f"entityclasses_health: read a ladder outside the block: {parsed}")
    # A health* value that is not an integer is a named skip, not a pinned 0.
    text = health_xml(("healthSlim", "125"), ("healthSlimFeral", "500.5"))
    parsed, unparsed = parse(health, text)
    if parsed != {"healthSlim": 125} or not any("healthSlimFeral" in u for u in unparsed):
        bad.append(f"entityclasses_health: fractional health read as {parsed} ({unparsed})")
    parsed, unparsed = parse(health, health_xml(("healthSlim", "125"), ("healthStrong", "450")))
    if parsed != {"healthSlim": 125, "healthStrong": 450} or unparsed:
        bad.append(f"entityclasses_health: valid ladder mis-parsed as {parsed} ({unparsed})")

    # extract() over a fake install: one garbage config must not take the other
    # two sections down, and the source identity must describe the real bytes.
    game = tmp / "install"
    (game / "Data" / "Config").mkdir(parents=True, exist_ok=True)
    (game / "Data" / "Config" / "entityclasses.xml").write_text(
        health_xml(("healthSlim", "125"), ("healthStrong", "450")), encoding="utf-8"
    )
    (game / "Data" / "Config" / "traders.xml").write_text(
        '<traders buy_markup="1.5" sell_markdown="0.2"/>', encoding="utf-8"
    )
    (game / "Data" / "Config" / "buffs.xml").write_bytes(b"\xff\xfe\x00broken <attr")
    data = src.extract(str(game))
    if data["entityclasses_health"].get("healthSlim") != 125:
        bad.append(f"extract: entityclasses section lost: {data['entityclasses_health']}")
    if data["traders_root"].get("buy_markup") != 1.5:
        bad.append(f"extract: traders section lost: {data['traders_root']}")
    for name, ident in data["source_identity"].items():
        raw = (game / "Data" / "Config" / name).read_bytes()
        if ident["bytes"] != len(raw) or ident["sha256"] != hashlib.sha256(raw).hexdigest():
            bad.append(f"extract: source identity for {name} disagrees with the file")
    # The unreadable section must fail regeneration closed, naming itself.
    refusals = src.refusals(data, str(game))
    if not any("buffs.xml" in r for r in refusals):
        bad.append(f"extract: an unparsed buffs.xml did not block regeneration: {refusals}")


class BudgetError(Exception):
    pass


def main() -> int:
    try:
        seed = tooling.fuzz_seed(SEED)
    except tooling.ConfigError as exc:
        print(f"FAIL: xml_pins fuzz: {exc}")
        return 2
    rng = random.Random(seed)
    bad: list[str] = []
    corpus = tooling.CorpusDigest()
    fuzz(rng, bad, corpus)
    if not bad:
        with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
            regression_pins(Path(td), bad)
    if bad:
        print(f"FAIL: xml_pins fuzz (seed 0x{seed:X}, corpus {corpus.hexdigest()})")
        for b in bad:
            print("  - " + b)
        print(f"  replay: RE_FUZZ_SEED=0x{seed:X} python3 {SCRIPT}")
        return 1
    print(
        f"OK: {ROUNDS} rounds x {len(src.SECTION_SPECS)} xml_pins sections; no escapes, "
        f"hangs, or invariant breaks (seed 0x{seed:X}, corpus {corpus.hexdigest()})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
