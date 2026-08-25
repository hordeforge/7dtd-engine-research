// EnumList: emit "EnumName.Member=value" for every enum member.
// Used by drift-check to diff enum values across game builds.
//   mono EnumList.exe <asm> <outFile>
using System;using System.IO;using System.Linq;using Mono.Cecil;
class EnumList{static void Main(string[]a){
  if(a.Length<2){Console.Error.WriteLine("usage: EnumList <asm> <outFile>");Environment.Exit(2);}
  var r=new DefaultAssemblyResolver();r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
  var asm=AssemblyDefinition.ReadAssembly(a[0],new ReaderParameters{AssemblyResolver=r});
  var w=new StreamWriter(a[1]);
  foreach(var t in asm.MainModule.GetTypes().Where(t=>t.IsEnum&&!t.Name.Contains("<")))
    foreach(var f in t.Fields.Where(f=>f.HasConstant))w.WriteLine(t.Name+"."+f.Name+"="+f.Constant);
  w.Close();}}
