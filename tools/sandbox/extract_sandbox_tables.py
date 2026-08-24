#!/usr/bin/env python3
"""Extract SandboxOptions value sets + option table from Assembly-CSharp.dll IL.

Reads SandboxOptionManager.SetupOptions IL (dncil) and metadata (dnfile) to
recover, for every registered sandbox option, its enum id, display/category
names, value-set name, default value, and the full numeric value set (from
<PrivateImplementationDetails> static arrays via the FieldRVA table, or from
inline stelem fills). Output: JSON written to stdout or --out.

Usage:
  python3 extract_sandbox_tables.py /path/to/Assembly-CSharp.dll --out out.json

Deps: dnfile, dncil; hash-pinned in requirements.txt next to this script
(uv pip install -r requirements.txt).

Evidence: docs/sandbox-options.md (this repo). The option ids and value sets
are the wire-visible contract of the sandbox code (see sandbox-options.md §3);
they must match the stock DLL exactly for zdtd's SandboxCode decode.
"""

import argparse
import json
import struct
import sys

import dnfile
from dncil.cil.body.reader import Token, read_method_body_from_bytes

IMPLICIT = {"ldc.i4.m1": -1}
for _i in range(9):
    IMPLICIT[f"ldc.i4.{_i}"] = _i

VALUES_FIELDS = (37607, 37608)  # SandboxOptionValueSet.FloatValues / IntValues
ELEM_TYPEREF = (52, 265)  # System.Int32 / System.Single type refs


def ldc4_val(ins):
    if ins.opcode.name in IMPLICIT:
        return IMPLICIT[ins.opcode.name]
    if ins.opcode.name in ("ldc.i4", "ldc.i4.s"):
        return ins.operand if isinstance(ins.operand, int) else None
    return None


def is_ldc4(ins):
    return ins.opcode.name.startswith("ldc.i4")


def is_ldcr4(ins):
    return ins.opcode.name == "ldc.r4" and isinstance(ins.operand, float)


def extract(pe):
    md = pe.net.mdtables

    def s(x):
        return str(x) if x is not None else ""

    # method row -> declaring type name (MethodDef has no Parent column)
    mtype = {}
    for td in md.TypeDef.rows:
        tn = s(td.TypeName)
        for m in td.MethodList:
            mtype[m.row_index] = tn

    # field row -> RVA for <PrivateImplementationDetails> arrays
    frva = {}
    for r in md.FieldRva.rows:
        frva[r.Field.row_index] = r.Rva

    def us_str(tok):
        return pe.net.user_strings.get(tok.value & 0xFFFFFF).value

    def read_array(rid, count, fmt):
        rva = frva.get(rid)
        if rva is None:
            return None
        data = pe.get_data(rva, count * 4)
        return list(struct.unpack(f"<{count}{fmt}", data))

    # locate SandboxOptionManager.SetupOptions
    tgt = None
    for row in md.TypeDef.rows:
        if s(row.TypeName) == "SandboxOptionManager":
            tgt = row
            break
    if tgt is None:
        raise SystemExit("SandboxOptionManager not found")

    # enum member name by value (Constant table -> Field rows of SandboxOptions)
    enum_names = {}
    for row in md.TypeDef.rows:
        if s(row.TypeName) != "SandboxOptions":
            continue
        flds = row.FieldList
        # build field rid -> constant value
        field_const = {}
        for r in md.Constant.rows:
            p = r.Parent
            if p.table is md.Field:
                field_const[p.row_index] = r.Value.value
        for fidx in flds:
            rid = fidx.row_index
            nm = s(fidx.row.Name)
            if nm == "value__":
                continue
            cv = field_const.get(rid)
            if cv is not None:
                enum_names[int.from_bytes(cv, "little", signed=True)] = nm
        break

    mrow = None
    for m in tgt.MethodList:
        if s(m.row.Name) == "SetupOptions":
            mrow = m.row
            break
    if mrow is None:
        raise SystemExit("SetupOptions not found")

    data = pe.get_data(mrow.Rva, 0x10000)
    body = read_method_body_from_bytes(data)
    insns = body.instructions
    n = len(insns)

    def find_newarr_len(j):
        # First ldc.i4 constant walking back from the newarr (its element
        # count); stops at the nearest call/newobj/stfld boundary.
        m = j - 1
        while m >= 0 and insns[m].opcode.name not in ("newobj", "call", "callvirt", "stfld"):
            v = ldc4_val(insns[m])
            if v is not None:
                return v
            m -= 1
        return None

    def inline_stelem(j):
        pairs = []
        k = j
        while k < n:
            opk = insns[k].opcode.name
            if opk == "stelem.i4":
                val, idx = ldc4_val(insns[k - 1]), ldc4_val(insns[k - 2])
                if val is not None and idx is not None:
                    pairs.append((idx, val))
            elif opk == "stelem.r4":
                if is_ldcr4(insns[k - 1]):
                    idx = ldc4_val(insns[k - 2])
                    if idx is not None:
                        pairs.append((idx, insns[k - 1].operand))
            if opk == "stfld" or opk in ("call", "callvirt", "newobj"):
                break
            k += 1
        return pairs

    valuesets = {}
    options = []
    i = 0
    while i < n:
        ins = insns[i]
        if ins.opcode.name != "newobj" or not isinstance(ins.operand, Token):
            i += 1
            continue
        owner = mtype.get(ins.operand.value & 0xFFFFFF, "")
        if owner.startswith("SandboxOptionValueSet"):
            name = None
            k = i - 1
            while k >= 0 and insns[k].opcode.name not in ("newobj", "call", "callvirt"):
                if insns[k].opcode.name == "ldstr":
                    name = us_str(insns[k].operand)
                    break
                k -= 1
            vstype = "float" if "Float" in owner else "int" if "Int" in owner else "bool"
            arr = None
            if vstype != "bool":
                j = i + 1
                while j < min(i + 80, n):
                    opj = insns[j].opcode.name
                    if opj == "callvirt":
                        break
                    if (
                        opj == "stfld"
                        and isinstance(insns[j].operand, Token)
                        and (insns[j].operand.value & 0xFFFFFF) in VALUES_FIELDS
                    ):
                        break
                    if (
                        opj == "ldtoken"
                        and isinstance(insns[j].operand, Token)
                        and j + 1 < n
                        and insns[j + 1].opcode.name == "call"
                    ):
                        frid = insns[j].operand.value & 0xFFFFFF
                        m = j - 2
                        while m > i and insns[m].opcode.name not in (
                            "newarr",
                            "stfld",
                            "call",
                            "callvirt",
                            "newobj",
                        ):
                            m -= 1
                        cnt = (
                            find_newarr_len(m)
                            if m > i and insns[m].opcode.name == "newarr"
                            else None
                        )
                        arr = (
                            read_array(frid, cnt, "f" if vstype == "float" else "i")
                            if cnt
                            else None
                        )
                        break
                    j += 1
                if arr is None:
                    j = i + 1
                    while j < min(i + 80, n):
                        opj = insns[j].opcode.name
                        if opj == "newarr" and isinstance(insns[j].operand, Token):
                            elem = insns[j].operand.value & 0xFFFFFF
                            if elem in ELEM_TYPEREF:
                                cnt = find_newarr_len(j)
                                pairs = inline_stelem(j + 1)
                                if pairs and cnt:
                                    arr = [0] * cnt
                                    for idx, val in pairs:
                                        if 0 <= idx < cnt:
                                            arr[idx] = val
                                break
                        if opj == "callvirt":
                            break
                        j += 1
            if name:
                valuesets[name] = {"type": vstype, "values": arr}
        elif owner.startswith("SandboxOption") and "ValueSet" not in owner:
            args = []
            k = i - 1
            while k >= 0:
                opk = insns[k].opcode.name
                if opk == "ldarg.0":
                    break
                if opk in ("newobj", "call", "callvirt"):
                    break
                if opk == "ldstr":
                    args.append(("s", us_str(insns[k].operand)))
                elif is_ldcr4(insns[k]):
                    args.append(("f", insns[k].operand))
                elif is_ldc4(insns[k]):
                    v = ldc4_val(insns[k])
                    if v is not None:
                        args.append(("i", v))
                k -= 1
            args.reverse()
            idv = ldc4_val(insns[k + 1]) if k >= 0 and k + 1 < n else None
            strs = [a[1] for a in args if a[0] == "s"]
            default = None
            sc = 0
            for ai, a in enumerate(args):
                if a[0] == "s":
                    sc += 1
                    if sc == 3:
                        for a2 in args[ai + 1 :]:
                            if a2[0] in ("f", "i"):
                                default = a2[1]
                                break
                        break
            otype = "float" if "Float" in owner else "int" if "Int" in owner else "bool"
            if idv is not None and len(strs) >= 3:
                options.append(
                    {
                        "id": idv,
                        "name": enum_names.get(idv, ""),
                        "display": strs[0],
                        "category": strs[1],
                        "valueset": strs[2],
                        "type": otype,
                        "default": default,
                    }
                )
        i += 1

    opt_by_id = {o["id"]: o for o in options}
    if opt_by_id:
        missing = [x for x in range(max(opt_by_id) + 1) if x not in opt_by_id]
        if missing:
            print(f"warning: enum ids not registered: {missing}", file=sys.stderr)
    else:
        print("warning: no sandbox options recovered from SetupOptions", file=sys.stderr)
    return {"valuesets": valuesets, "options": [opt_by_id[k] for k in sorted(opt_by_id)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dll")
    ap.add_argument("--out")
    args = ap.parse_args()
    pe = dnfile.dnPE(args.dll)
    out = extract(pe)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    else:
        print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
