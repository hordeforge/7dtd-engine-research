// MethodList: emit "TypeFullName::Method(paramTypeNames)" for every method-with-body.
// Used by drift-check to diff method surfaces across game builds.
//   mono MethodList.exe <asm> <outFile>
using System;using System.IO;using System.Linq;using Mono.Cecil;
class MethodList{static void Main(string[]a){
  if(a.Length<2){Console.Error.WriteLine("usage: MethodList <asm> <outFile>");Environment.Exit(2);}
  var r=new DefaultAssemblyResolver();r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
  var asm=AssemblyDefinition.ReadAssembly(a[0],new ReaderParameters{AssemblyResolver=r});
  var w=new StreamWriter(a[1]);
  foreach(var t in asm.MainModule.GetTypes().Where(t=>!t.Name.Contains("$")&&!t.Name.Contains("<")&&!t.Name.StartsWith("__")))
    foreach(var m in t.Methods.Where(m=>m.HasBody).OrderBy(m=>m.Name))
      w.WriteLine(t.FullName+"::"+m.Name+"("+string.Join(",",m.Parameters.Select(p=>p.ParameterType.Name))+")");
  w.Close();}}
