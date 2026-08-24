// Shared IL instruction formatter. Emits the corpus dump format:
//   IL_XXXX: opcode operand
// with fully-qualified method/field/type operands and IL_offset branch targets.
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

static class IlFmt {
  public static string Op(Instruction i) {
    var op = i.Operand;
    string os;
    if (op is Instruction ti) os = "IL_" + ti.Offset.ToString("X4");
    else if (op is Instruction[] arr) os = string.Join(",", arr.Select(x => "IL_" + x.Offset.ToString("X4")));
    else if (op is MethodReference mr) os = mr.FullName;
    else if (op is FieldReference fr) os = fr.FieldType.Name + " " + fr.DeclaringType.Name + "::" + fr.Name;
    else if (op is TypeReference tr) os = tr.FullName;
    else os = op == null ? "" : op.ToString();
    return ("IL_" + i.Offset.ToString("X4") + ": " + i.OpCode.Name + " " + os).TrimEnd();
  }

  public static string Sig(MethodDefinition m) =>
    string.Join(",", m.Parameters.Select(p => p.ParameterType.Name + " " + p.Name));

  // Filesystem-safe fragment for filenames derived from assembly-supplied
  // type/method names: a crafted assembly must not escape the output directory.
  // Dots survive (namespaces carry them), so a whole fragment of "." or ".."
  // would combine into a parent directory; prefix it to pin every fragment
  // strictly below the output root.
  public static string Safe(string s) {
    var t = string.Concat(s.Select(c => char.IsLetterOrDigit(c) || c == '_' || c == '.' ? c : '_'));
    return t == "." || t == ".." ? "_" + t : t;
  }
}
