// Reach: call-graph reachability from the dedicated boot + tick drivers.
// Seeds GameManager.StartAsServer/gmUpdate/UpdateTick/... + peer Updates + entity
// tick, walks call/callvirt/newobj (devirtualizing callvirt via an override map), and
// emits reached types (method-with-body count, tab-separated). Cross-filter against
// il/surface-v3.1.0/surface-types.md (Assembly-CSharp) to find reachable game types no
// doc references: the definitive coverage lens.
//   mono Reach.exe <asm> <outFile>
using System;using System.Collections.Generic;using System.IO;using System.Linq;
using Mono.Cecil;using Mono.Cecil.Cil;
class Reach {
  static Dictionary<string,List<MethodDefinition>> overrides = new Dictionary<string,List<MethodDefinition>>();
  static void Main(string[] a){
    var r=new DefaultAssemblyResolver();r.AddSearchDirectory(Path.GetDirectoryName(a[0]));
    var asm=AssemblyDefinition.ReadAssembly(a[0],new ReaderParameters{AssemblyResolver=r});
    var mod=asm.MainModule; var all=mod.GetTypes().ToList();
    foreach(var t in all) foreach(var m in t.Methods.Where(x=>x.IsVirtual && x.HasBody)){
      var bt=t.BaseType;
      while(bt!=null){ var btd=bt.Resolve(); if(btd==null)break;
        var bm=btd.Methods.FirstOrDefault(x=>x.Name==m.Name && x.Parameters.Count==m.Parameters.Count && x.IsVirtual);
        if(bm!=null){ var k=btd.FullName+"::"+m.Name+"/"+m.Parameters.Count; List<MethodDefinition> l;
          if(!overrides.TryGetValue(k,out l)){l=new List<MethodDefinition>();overrides[k]=l;} l.Add(m); }
        bt=btd.BaseType; }
    }
    foreach(var t in all){
      if(!t.HasInterfaces)continue;
      foreach(var ii in t.Interfaces){
        TypeDefinition itd=null; try{itd=ii.InterfaceType.Resolve();}catch{}
        if(itd==null)continue;
        foreach(var im in itd.Methods){
          var impl=t.Methods.FirstOrDefault(x=>x.HasBody && x.Name==im.Name && x.Parameters.Count==im.Parameters.Count);
          if(impl==null)continue;
          var k=itd.FullName+"::"+im.Name+"/"+im.Parameters.Count; List<MethodDefinition> l;
          if(!overrides.TryGetValue(k,out l)){l=new List<MethodDefinition>();overrides[k]=l;}
          if(!l.Contains(impl))l.Add(impl);
        }
      }
    }
    var visited=new HashSet<MethodDefinition>(); var work=new Queue<MethodDefinition>();
    Seeds.EnqueueSeeds(all, visited, work);
    var reflTypes = Seeds.ReflTargets(all);
    Seeds.IndexTypes(all);
    string lastLdstr=null;
    while(work.Count>0){ var m=work.Dequeue();
      foreach(var i in m.Body.Instructions){
        if(i.OpCode.Code==Code.Ldstr){ lastLdstr=i.Operand as string; }
        var mr=i.Operand as MethodReference; if(mr==null)continue;
        MethodDefinition md=null; try{md=mr.Resolve();}catch{}
        if(md!=null && md.HasBody && visited.Add(md)) work.Enqueue(md);
        if(i.OpCode.Code==Code.Callvirt){ var k=mr.DeclaringType.FullName+"::"+mr.Name+"/"+mr.Parameters.Count;
          List<MethodDefinition> ovs; if(overrides.TryGetValue(k,out ovs)) foreach(var ov in ovs) if(visited.Add(ov)) work.Enqueue(ov); }
        // Same reflection-following as Coverage.exe (shared seed contract).
        if(md!=null && md.DeclaringType.Name=="ReflectionHelpers" && md.Name=="GetTypeWithPrefix" && !string.IsNullOrEmpty(lastLdstr)){
          foreach(var tt in reflTypes.Where(t=>t.Name.StartsWith(lastLdstr)))
            foreach(var tm in tt.Methods.Where(x=>x.HasBody)) if(visited.Add(tm)) work.Enqueue(tm);
        }
        if(mr.DeclaringType.FullName=="System.Type" && (mr.Name=="GetType"||mr.Name=="GetTypeFromHandle") && !string.IsNullOrEmpty(lastLdstr)){
          var tt=Seeds.FindByConstantName(lastLdstr);
          if(tt!=null) foreach(var tm in tt.Methods.Where(x=>x.HasBody)) if(visited.Add(tm)) work.Enqueue(tm);
        }
        if(mr.DeclaringType.FullName=="System.Activator" && mr.Name=="CreateInstance" && !string.IsNullOrEmpty(lastLdstr)){
          var tt=Seeds.FindByConstantName(lastLdstr);
          if(tt!=null) foreach(var tm in tt.Methods.Where(x=>x.HasBody)) if(visited.Add(tm)) work.Enqueue(tm);
        }
      }
    }
    var reached=new HashSet<TypeDefinition>(visited.Select(m=>m.DeclaringType));
    Console.Error.WriteLine("reached methods="+visited.Count+" reached types="+reached.Count);
    var w=new StreamWriter(a[1]);
    foreach(var t in reached.Where(t=>!t.Name.Contains("<")&&!t.Name.Contains("$")&&!t.Name.StartsWith("__")).OrderByDescending(t=>t.Methods.Count(x=>x.HasBody)))
      w.WriteLine(t.Methods.Count(x=>x.HasBody)+"\t"+t.Name);
    w.Close();
  }
}
