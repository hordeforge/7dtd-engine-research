// Extract the zdtd-relevant wire surface from an Assembly-CSharp.dll into a
// stable JSON snapshot: every NetPackage's read/write BinaryReader/Writer call
// sequence (the wire layout), package directions, and selected enum values.
// Diff two snapshots to see exactly what TFP changed between server versions.
using System; using System.IO; using System.Linq; using System.Text;
using System.Collections.Generic;
using Mono.Cecil; using Mono.Cecil.Cil;

class ParitySurface {
    static string Seq(MethodDefinition m) {
        if (m == null || !m.HasBody) return "";
        var sb = new StringBuilder();
        foreach (var i in m.Body.Instructions) {
            if (i.OpCode.Code != Code.Call && i.OpCode.Code != Code.Callvirt) continue;
            var mr = i.Operand as MethodReference; if (mr == null) continue;
            var dt = mr.DeclaringType.Name;
            // Only capture wire-relevant primitive IO + nested type Read/Write.
            if (dt == "BinaryReader" || dt == "BinaryWriter") sb.Append(mr.Name).Append(';');
            else if (mr.Name == "Read" || mr.Name == "Write" || mr.Name == "write" || mr.Name == "read")
                sb.Append(dt).Append('.').Append(mr.Name).Append(';');
            else if (dt == "StreamUtils") sb.Append("SU.").Append(mr.Name).Append(';');
        }
        return sb.ToString();
    }
    static int Dir(TypeDefinition t) {
        var d = t.Methods.FirstOrDefault(x => x.Name == "get_PackageDirection");
        if (d == null || !d.HasBody) return -1;
        foreach (var i in d.Body.Instructions) {
            switch (i.OpCode.Code) {
                case Code.Ldc_I4_0: return 0;
                case Code.Ldc_I4_1: return 1;
                case Code.Ldc_I4_2: return 2;
                case Code.Ldc_I4_3: return 3;
                case Code.Ldc_I4: return (int)i.Operand;
                case Code.Ldc_I4_S: return (sbyte)i.Operand;
            }
        }
        return -1;
    }
    static void Main(string[] a) {
        var r = new DefaultAssemblyResolver(); r.AddSearchDirectory(Path.GetDirectoryName(a[0]));
        var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
        var sb = new StringBuilder(); sb.Append("{\n");
        // Packages
        sb.Append("  \"packages\": {\n");
        var pkgs = asm.MainModule.Types.Where(t => t.Name.StartsWith("NetPackage") && !t.IsAbstract)
                     .OrderBy(t => t.Name).ToList();
        for (int k = 0; k < pkgs.Count; k++) {
            var t = pkgs[k];
            var rd = Seq(t.Methods.FirstOrDefault(x => x.Name == "read"));
            var wr = Seq(t.Methods.FirstOrDefault(x => x.Name == "write"));
            sb.Append("    \"").Append(t.Name).Append("\": {\"dir\":").Append(Dir(t))
              .Append(",\"read\":\"").Append(rd).Append("\",\"write\":\"").Append(wr).Append("\"}");
            sb.Append(k < pkgs.Count - 1 ? ",\n" : "\n");
        }
        sb.Append("  },\n");
        // Selected enums (reasons, TE types, stats) that our wire depends on
        sb.Append("  \"enums\": {\n");
        var wantEnums = new[]{"EnumRemoveEntityReason","TileEntityType","EnumGameStats","EnumPersistentPlayerDataReason","RespawnType","NetPackageDirection"};
        var elist = new List<string>();
        foreach (var en in wantEnums) {
            var t = asm.MainModule.Types.FirstOrDefault(x => x.Name == en);
            if (t == null || !t.IsEnum) continue;
            var vals = string.Join(",", t.Fields.Where(f => f.HasConstant)
                        .Select(f => "\"" + f.Name + "=" + f.Constant + "\""));
            elist.Add("    \"" + en + "\": [" + vals + "]");
        }
        sb.Append(string.Join(",\n", elist)).Append("\n  }\n");
        sb.Append("}\n");
        Console.Write(sb.ToString());
    }
}
