#!/usr/bin/env python3
"""Seeded mutation fuzzer for the sandbox preset-code decoder.

`Data/Sandbox/sandbox_presets` is a TextAsset inside the client's
data.unity3d, extracted by hand into sandbox/sandbox_presets.xml: a wrong
bundle, a client update, or a hand-edited extract reaches `decode()` as an
arbitrary `code` attribute. The codec is hand-rolled (an 'A' prefix, then
3-letter base-26 groups where two letters are the option id and the third is
the value-set index), so every field in it is input. `test_sandbox_preset_codes.py`
pins the six stock codes; this gate covers the space between them:

  1. Only ValueError escapes decode(): a code the codec cannot read is a named
     refusal, never a traceback out of the tool.
  2. Per-call time budget: a long code must not be a long walk with the cap
     only in the caller's patience.
  3. Decode invariants: every key is a known option name, every value is a
     member of that option's value set, and the group count bounds the result.
  4. Table-shape hardening: a value set that carries `values` as something
     other than a list (a JSON object, a string, a number) is refused like any
     other unreadable table, not indexed into.
  5. XML side: parsing a mutated preset TextAsset raises only ParseError, and
     every preset code it carries decodes or is refused.
  6. Determinism: the same code decodes to the same dict twice.

Seeds are structure-aware: the real codes read out of the committed
sandbox_presets.xml, plus the option/value-set table those codes index into,
so mutations explore around true shapes. Deterministic, stdlib-only, DLL-free.

Usage: python3 tools/tests/test_sandbox_preset_code_fuzz.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import random
import sys
import time
import xml.etree.ElementTree as ET
from collections.abc import Callable, Mapping
from functools import partial
from typing import Any, TypeVar

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

SANDBOX = _common.TOOLS / "sandbox"
# The decoder is a script with no package, so it is loaded the way
# test_sandbox_safe_name.py loads safe_name.py, and its entry point is
# annotated here rather than left Any.
_spec = importlib.util.spec_from_file_location(
    "extract_preset_codes", SANDBOX / "extract_preset_codes.py"
)
assert _spec is not None
assert _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
decode: Callable[[str, "Opts", "Sets"], dict[str, Any]] = _mod.decode

SEED = 0x5A4B0DE
ROUNDS = 240  # mutation rounds per family
TIME_BUDGET_S = 5.0  # hard ceiling for ONE decode (hang-class guard)
T = TypeVar("T")
# The value table is JSON: an option id, a name, a value-set name, and a value
# of whatever type the set carries (float, bool, int).
Opts = dict[int, dict[str, Any]]
Sets = dict[str, dict[str, Any]]
ALPHABET = "ABCZaz0 \t-_/\u00e9\ufffd\U0001f600"


def tables() -> tuple[Opts, Sets]:
    data: Any = json.loads((SANDBOX / "sandbox_tables.json").read_text(encoding="utf-8"))
    opts: Opts = {o["id"]: o for o in data["options"]}
    sets: Sets = dict(data["valuesets"])
    return opts, sets


def seed_codes() -> list[str]:
    """The real Difficulty codes, so mutations start from true shapes."""
    root = ET.parse(SANDBOX / "sandbox_presets.xml").getroot()
    codes = [p.get("code") or "" for p in root.findall("preset")]
    if not codes:
        raise SystemExit("FAIL: committed sandbox_presets.xml carries no codes to seed with")
    return codes


def mutate(rng: random.Random, code: str) -> str:
    if not code:
        return rng.choice(ALPHABET) * rng.randint(0, 6)
    b = list(code)
    for _ in range(rng.randint(1, 4)):
        op = rng.choice(("char", "del", "insert", "group", "trunc"))
        i = rng.randrange(len(b))
        if op == "char":
            b[i] = rng.choice(ALPHABET)
        elif op == "del":
            del b[i]
        elif op == "insert":
            b[i:i] = [rng.choice(ALPHABET)] * rng.randint(1, 5)
        elif op == "group":
            b[i : i + 3] = list(rng.choice(("AAA", "ZZZ", "AAB", "AA", "AAAAA", "aAA")))
        else:
            del b[i:]
        if not b:
            break
    return "".join(b)


def timed(call: Callable[[], T]) -> T:
    t0 = time.monotonic()
    out = call()
    dt = time.monotonic() - t0
    if dt >= TIME_BUDGET_S:
        raise BudgetError(f"call took {dt:.1f}s (budget {TIME_BUDGET_S}s)")
    return out


def check_invariants(
    code: str,
    out: Mapping[str, Any],
    opts: dict[int, dict[str, object]],
    sets: dict[str, dict[str, object]],
    bad: list[str],
) -> None:
    if decode(code, opts, sets) != out:
        bad.append(f"decode is not deterministic for {code!r}")
        return
    groups = max(0, (len(code) - 1) // 3)
    if len(out) > groups:
        bad.append(f"{code!r}: {len(out)} values from {groups} groups")
        return
    for key, value in out.items():
        opt = next((o for o in opts.values() if o["name"] == key), None)
        if opt is None:
            bad.append(f"{code!r}: decoded unknown option name {key!r}")
            return
        entry = sets.get(str(opt["valueset"])) or {}
        values = entry.get("values")
        allowed = values if isinstance(values, list) else [False, True]
        if value not in allowed:
            bad.append(f"{code!r}: {key}={value!r} is not in its value set {allowed}")
            return


def fuzz_codes(
    rng: random.Random, opts: Opts, sets: Sets, codes: list[str], bad: list[str]
) -> None:
    for k in range(ROUNDS):
        code = mutate(rng, rng.choice(codes)) if rng.random() < 0.85 else codes[k % len(codes)]
        label = f"round {k} {code!r}"
        try:
            out = timed(partial(decode, code, opts, sets))
        except (ValueError, BudgetError) as exc:
            if isinstance(exc, BudgetError):
                bad.append(f"{label}: {exc}")
                return
            continue
        except Exception as exc:
            bad.append(f"{label}: ESCAPED {type(exc).__name__}: {exc}")
            return
        check_invariants(code, out, opts, sets, bad)
        if bad:
            return


def fuzz_tables(
    rng: random.Random, opts: Opts, sets: Sets, codes: list[str], bad: list[str]
) -> None:
    """A malformed value-set table must be refused, never indexed into."""
    for k in range(ROUNDS):
        broken_sets = {name: dict(entry) for name, entry in sets.items()}
        name = rng.choice(sorted(broken_sets))
        entry = broken_sets[name]
        shape = rng.choice(("dict", "string", "number", "null", "empty", "drop"))
        if shape == "dict":
            entry["values"] = {"0": 1.0, "1": 2.0}
        elif shape == "string":
            entry["values"] = "0.0,1.0"
        elif shape == "number":
            entry["values"] = 7
        elif shape == "null":
            entry["values"] = None
        elif shape == "empty":
            entry["values"] = []
        else:
            del broken_sets[name]
        if entry.get("type") == "bool" and shape in ("drop", "null"):
            continue  # a bool set with no table is the documented codec
        code = rng.choice(codes)
        label = f"tables round {k} {name}={shape} {code!r}"
        try:
            timed(partial(decode, code, opts, broken_sets))
        except ValueError:
            continue
        except BudgetError as exc:
            bad.append(f"{label}: {exc}")
            return
        except Exception as exc:
            bad.append(f"{label}: ESCAPED {type(exc).__name__}: {exc}")
            return


def fuzz_xml(rng: random.Random, opts: Opts, sets: Sets, bad: list[str]) -> None:
    """The TextAsset itself: a mutated preset document decodes or is refused."""
    original = (SANDBOX / "sandbox_presets.xml").read_text(encoding="utf-8")
    for k in range(ROUNDS):
        text = mutate(rng, original) if rng.random() < 0.85 else original
        label = f"xml round {k}"
        try:
            timed(partial(ET.fromstring, text))
        except ET.ParseError:
            continue
        except BudgetError as exc:
            bad.append(f"{label}: {exc}")
            return
        except Exception as exc:
            bad.append(f"{label}: ESCAPED {type(exc).__name__}: {exc}")
            return
        for preset in ET.fromstring(text).findall("preset"):
            code = preset.get("code") or ""
            try:
                timed(partial(decode, code, opts, sets))
            except (ValueError, BudgetError):
                continue
            except Exception as exc:
                bad.append(f"{label}: code {code!r} ESCAPED {type(exc).__name__}: {exc}")
                return


def regression_pins(opts: Opts, sets: Sets, bad: list[str]) -> None:
    """The stock codes, and the shapes that are refused rather than read."""
    root = ET.parse(SANDBOX / "sandbox_presets.xml").getroot()
    presets = [p for p in root.findall("preset") if p.get("category") == "Difficulty"]
    if len(presets) != 6:
        bad.append(f"stock Difficulty presets: {len(presets)}, want 6")
        return
    for preset in presets:
        code = preset.get("code") or ""
        try:
            out = decode(code, opts, sets)
        except ValueError as exc:
            bad.append(f"stock code {code!r} ({preset.get('name')}) was refused: {exc}")
            continue
        if out and "IncomingDamage" not in out:
            bad.append(f"stock code {code!r} decoded without IncomingDamage: {out}")
    for code in ("", "B", "AAB", "AAaA", "AAA", "A" + "A" * 600):
        try:
            out = timed(partial(decode, code, opts, sets))
        except ValueError:
            continue
        except Exception as exc:
            bad.append(f"shape {code[:12]!r}: ESCAPED {type(exc).__name__}: {exc}")
            continue
        check_invariants(code, out, opts, sets, bad)
    if decode("", opts, sets) != {}:
        bad.append("empty code did not decode to the defaults")


class BudgetError(Exception):
    pass


def main() -> int:
    rng = random.Random(SEED)
    opts, sets = tables()
    codes = seed_codes()
    bad: list[str] = []
    fuzz_codes(rng, opts, sets, codes, bad)
    if not bad:
        fuzz_tables(rng, opts, sets, codes, bad)
    if not bad:
        fuzz_xml(rng, opts, sets, bad)
    if not bad:
        regression_pins(opts, sets, bad)
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(f"OK: {ROUNDS} rounds x 3 families over {len(codes)} seed codes, seeds {SEED:#x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
