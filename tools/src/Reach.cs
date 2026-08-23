// Reach: call-graph reachability from the dedicated boot + tick drivers.
// Seeds GameManager.StartAsServer/gmUpdate/UpdateTick/... + peer Updates + entity
// tick, walks call/callvirt/newobj (devirtualizing callvirt via an override map), and
// emits reached types (method-with-body count, tab-separated). Cross-filter against
// il/surface-v3.1.0/surface-types.md (Assembly-CSharp) to find reachable game types no
// doc references: the definitive coverage lens.
//   mono Reach.exe <asm> <outFile>
using System;using System.Collections.Generic;using System.IO;using System.Linq;
using Mono.Cecil;
class Reach {
  static void Main(string[] a){
    if(a.Length<2){Console.Error.WriteLine("usage: Reach <asm> <outFile>");Environment.Exit(2);}
    var r=new DefaultAssemblyResolver();r.AddSearchDirectory(Path.GetDirectoryName(a[0]));
    var asm=AssemblyDefinition.ReadAssembly(a[0],new ReaderParameters{AssemblyResolver=r});
    var mod=asm.MainModule; var all=mod.GetTypes().ToList();
    var visited=new HashSet<MethodDefinition>(); var work=new Queue<MethodDefinition>();
    Seeds.EnqueueSeeds(all, visited, work);
    // Same graph walk as Coverage.exe: shared devirtualization map + BFS +
    // reflection-following (Seeds.WalkCallGraph), so both lenses cannot drift.
    Seeds.WalkCallGraph(all, visited, work, Seeds.BuildOverrideMap(all), Seeds.ReflTargets(all));
    var reached=new HashSet<TypeDefinition>(visited.Select(m=>m.DeclaringType));
    Console.Error.WriteLine("reached methods="+visited.Count+" reached types="+reached.Count);
    var w=new StreamWriter(a[1]);
    foreach(var t in reached.Where(t=>!t.Name.Contains("<")&&!t.Name.Contains("$")&&!t.Name.StartsWith("__")).OrderByDescending(t=>t.Methods.Count(x=>x.HasBody)))
      w.WriteLine(t.Methods.Count(x=>x.HasBody)+"\t"+t.Name);
    w.Close();
  }
}
