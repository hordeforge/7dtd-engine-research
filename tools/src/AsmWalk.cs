// Shared assembly-walk helpers for the src/ dumpers: nested-type collection,
// outermost-declaring-type attribution, generic-arity stripping. These started
// as byte-identical private copies in Xref/RefScan (plus a third walker in
// DumpMethod); they live here next to IlFmt/Seeds so the scanners cannot drift
// apart on what "every type" or "the owning type" means.
using System.Collections.Generic;
using Mono.Cecil;

static class AsmWalk {
  // Every type under ts, depth-first, each declaring type before its nested types.
  public static void Collect(IEnumerable<TypeDefinition> ts, List<TypeDefinition> into) {
    foreach (var t in ts) { into.Add(t); if (t.HasNestedTypes) Collect(t.NestedTypes, into); }
  }

  // Every type of the assembly across all modules (nested types included).
  public static List<TypeDefinition> AllTypes(AssemblyDefinition asm) {
    var all = new List<TypeDefinition>();
    foreach (var mod in asm.Modules) Collect(mod.Types, all);
    return all;
  }

  // Outermost declaring type: sites inside lambda closures and iterator state
  // machines credit the real owner, not the '<>c__DisplayClass' artifact.
  public static TypeDefinition Outermost(TypeDefinition t) {
    while (t.DeclaringType != null) t = t.DeclaringType;
    return t;
  }

  // Simple name without the generic-arity backtick suffix (List`1 -> List),
  // which is how a type is written in docs and spelled in CLI arguments.
  public static string SimpleName(string name) {
    int i = name.IndexOf('`');
    return i >= 0 ? name.Substring(0, i) : name;
  }
}
