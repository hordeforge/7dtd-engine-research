// Extract a small, stable JSON of stock hardcodes from Assembly-CSharp.dll.
// Regenerable source of truth for cross-repo pin checks (research docs, loadgen,
// zdtd). Does not ship game bytes; only numeric/string constants from metadata
// and a few well-known IL sites (GameTimer.get_Instance, WorldState cctor).
//
//   mono StockFacts.exe <Assembly-CSharp.dll> [out.json]
//
// Default out: stdout. Prefer writing tools/data/stock_facts.json via stock-sync.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

class StockFacts {
  static TypeDefinition Exact(ModuleDefinition mod, string name) {
    return mod.Types.FirstOrDefault(t => t.Name == name && (t.Namespace == "" || t.Namespace == null))
        ?? mod.Types.FirstOrDefault(t => t.Name == name)
        ?? throw new Exception("type not found: " + name);
  }

  static object FieldConst(TypeDefinition t, string name) {
    var f = t.Fields.FirstOrDefault(x => x.Name == name);
    if (f == null) throw new Exception(t.Name + "." + name + " missing");
    if (!f.HasConstant) throw new Exception(t.Name + "." + name + " has no metadata constant");
    return f.Constant;
  }

  static int AsInt(object o) {
    if (o is int i) return i;
    if (o is short s) return s;
    if (o is byte b) return b;
    if (o is sbyte sb) return sb;
    if (o is long l) return (int)l;
    if (o is uint u) return (int)u;
    if (o is Enum) return Convert.ToInt32(o);
    return Convert.ToInt32(o, CultureInfo.InvariantCulture);
  }

  static float AsFloat(object o) {
    if (o is float f) return f;
    if (o is double d) return (float)d;
    return Convert.ToSingle(o, CultureInfo.InvariantCulture);
  }

  static string JsonEsc(string s) {
    if (s == null) return "null";
    var sb = new StringBuilder("\"");
    foreach (var c in s) {
      if (c == '\\' || c == '"') sb.Append('\\').Append(c);
      else if (c == '\n') sb.Append("\\n");
      else if (c == '\r') sb.Append("\\r");
      else if (c == '\t') sb.Append("\\t");
      else if (c < 0x20) sb.AppendFormat("\\u{0:x4}", (int)c);
      else sb.Append(c);
    }
    sb.Append('"');
    return sb.ToString();
  }

  static int? LdcI4(Instruction i) {
    switch (i.OpCode.Code) {
      case Code.Ldc_I4_M1: return -1;
      case Code.Ldc_I4_0: return 0;
      case Code.Ldc_I4_1: return 1;
      case Code.Ldc_I4_2: return 2;
      case Code.Ldc_I4_3: return 3;
      case Code.Ldc_I4_4: return 4;
      case Code.Ldc_I4_5: return 5;
      case Code.Ldc_I4_6: return 6;
      case Code.Ldc_I4_7: return 7;
      case Code.Ldc_I4_8: return 8;
      case Code.Ldc_I4_S: return Convert.ToInt32(i.Operand);
      case Code.Ldc_I4: return Convert.ToInt32(i.Operand);
      default: return null;
    }
  }

  // Walk cctor; last integer pushed before stsfld Name wins (simple const init).
  static int? StsfldInt(TypeDefinition t, string fieldName) {
    var cctor = t.Methods.FirstOrDefault(m => m.IsConstructor && m.IsStatic && m.HasBody);
    if (cctor == null) return null;
    int? pending = null;
    int? found = null;
    foreach (var i in cctor.Body.Instructions) {
      var v = LdcI4(i);
      if (v.HasValue) pending = v;
      else if (i.OpCode.Code == Code.Stsfld) {
        var f = (FieldReference)i.Operand;
        if (f.Name == fieldName && pending.HasValue) found = pending;
        pending = null;
      } else if (i.OpCode.Code == Code.Ldc_R4 || i.OpCode.Code == Code.Ldc_R8) {
        pending = null;
      }
    }
    return found;
  }

  // Walk cctor; last float pushed before stsfld Name wins.
  static float? StsfldR4(TypeDefinition t, string fieldName) {
    var cctor = t.Methods.FirstOrDefault(m => m.IsConstructor && m.IsStatic && m.HasBody);
    if (cctor == null) return null;
    float? pending = null;
    float? found = null;
    foreach (var i in cctor.Body.Instructions) {
      if (i.OpCode.Code == Code.Ldc_R4) pending = AsFloat(i.Operand);
      else if (i.OpCode.Code == Code.Ldc_R8) pending = AsFloat(i.Operand);
      else if (i.OpCode.Code == Code.Stsfld) {
        var f = (FieldReference)i.Operand;
        if (f.Name == fieldName && pending.HasValue) found = pending;
        pending = null;
      } else if (LdcI4(i).HasValue) {
        pending = null;
      }
    }
    return found;
  }

  // Prefer metadata constant; else cctor stsfld int/float.
  static int FieldInt(TypeDefinition t, string name) {
    var f = t.Fields.FirstOrDefault(x => x.Name == name);
    if (f != null && f.HasConstant) return AsInt(f.Constant);
    var v = StsfldInt(t, name);
    if (v.HasValue) return v.Value;
    throw new Exception(t.Name + "." + name + " not a metadata const or simple cctor int");
  }

  static float FieldFloat(TypeDefinition t, string name) {
    var f = t.Fields.FirstOrDefault(x => x.Name == name);
    if (f != null && f.HasConstant) return AsFloat(f.Constant);
    var v = StsfldR4(t, name);
    if (v.HasValue) return v.Value;
    throw new Exception(t.Name + "." + name + " not a metadata const or simple cctor float");
  }

  static float? GameTimerTicksPerSecond(ModuleDefinition mod) {
    var gt = Exact(mod, "GameTimer");
    var m = gt.Methods.FirstOrDefault(x => x.Name == "get_Instance" && x.HasBody);
    if (m == null) return null;
    foreach (var i in m.Body.Instructions) {
      if (i.OpCode.Code == Code.Ldc_R4) return AsFloat(i.Operand);
    }
    return null;
  }

  // NetPackageTileEntity write: detect teBlockId (i32 after pos) + payload length width.
  // Heuristic from BinaryWriter.Write calls in write(): count Write(Int32) near end.
  static Dictionary<string, object> TileEntityWire(ModuleDefinition mod) {
    var t = mod.Types.FirstOrDefault(x => x.Name == "NetPackageTileEntity");
    var d = new Dictionary<string, object>();
    if (t == null) {
      d["present"] = false;
      return d;
    }
    d["present"] = true;
    var write = t.Methods.FirstOrDefault(m => m.Name == "write" && m.HasBody)
             ?? t.Methods.FirstOrDefault(m => m.Name == "Write" && m.HasBody);
    if (write == null) {
      d["write_il"] = 0;
      return d;
    }
    d["write_il"] = write.Body.Instructions.Count;
    int writeI32 = 0, writeU16 = 0, writeI16 = 0;
    foreach (var i in write.Body.Instructions) {
      if (i.OpCode.Code != Code.Call && i.OpCode.Code != Code.Callvirt) continue;
      var mr = i.Operand as MethodReference;
      if (mr == null || mr.DeclaringType.Name != "BinaryWriter" || mr.Name != "Write") continue;
      if (mr.Parameters.Count != 1) continue;
      var pn = mr.Parameters[0].ParameterType.FullName;
      if (pn == "System.Int32") writeI32++;
      else if (pn == "System.UInt16") writeU16++;
      else if (pn == "System.Int16") writeI16++;
    }
    d["write_i32_count"] = writeI32;
    d["write_u16_count"] = writeU16;
    d["write_i16_count"] = writeI16;
    // V3.1.0: teBlockId:i32 + payloadLen:i32 (among other i32s). Flag for docs.
    d["payload_len_likely_i32"] = writeI32 >= 2;
    return d;
  }

  static int? FieldConstInt(TypeDefinition t, string name) {
    var f = t.Fields.FirstOrDefault(x => x.Name == name && x.HasConstant);
    return f == null ? (int?)null : Convert.ToInt32(f.Constant);
  }

  static AssemblyDefinition LoadLiteNetLib(string managedDir) {
    var path = Path.Combine(managedDir, "LiteNetLib.dll");
    if (!File.Exists(path)) return null;
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(managedDir);
    return AssemblyDefinition.ReadAssembly(path, new ReaderParameters { AssemblyResolver = r });
  }

  // Decode NetConstants.PossibleMtu from the cctor's InitializeArray token
  // (the int32[] lives in <PrivateImplementationDetails> RVA data).
  static int[] PossibleMtu(AssemblyDefinition ln, TypeDefinition nc) {
    var cctor = nc.Methods.FirstOrDefault(m => m.IsConstructor && m.IsStatic && m.HasBody);
    if (cctor == null) return null;
    // find the PrivateImplementationDetails field the cctor initializes
    foreach (var i in cctor.Body.Instructions) {
      if (i.OpCode.Code == Code.Ldtoken && i.Operand is FieldReference fr) {
        var fdef = fr.Resolve();
        if (fdef != null && fdef.InitialValue != null && fdef.InitialValue.Length >= 24) {
          var outv = new int[fdef.InitialValue.Length / 4];
          for (int k = 0; k < outv.Length; k++)
            outv[k] = BitConverter.ToInt32(fdef.InitialValue, k * 4);
          return outv;
        }
      }
    }
    return null;
  }

  static void Main(string[] a) {
    if (a.Length < 1) {
      Console.Error.WriteLine("usage: StockFacts <asm> [out.json]");
      Environment.Exit(2);
    }
    var asmPath = Path.GetFullPath(a[0]);
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(Path.GetDirectoryName(asmPath));
    var asm = AssemblyDefinition.ReadAssembly(asmPath, new ReaderParameters { AssemblyResolver = r });
    var mod = asm.MainModule;

    var c = Exact(mod, "Constants");
    var wc = Exact(mod, "WorldConstants");

    int major = AsInt(FieldConst(c, "cVersionMajor"));
    int minor = AsInt(FieldConst(c, "cVersionMinor"));
    int build = AsInt(FieldConst(c, "cVersionBuild"));
    int releaseType = AsInt(FieldConst(c, "cReleaseType"));
    int ticksConst = AsInt(FieldConst(c, "cTicksPerSecond"));
    float tickDur = AsFloat(FieldConst(c, "cTickDuration"));
    int maxMp = AsInt(FieldConst(c, "cMaxMPPlayers"));
    int gameReset = AsInt(FieldConst(c, "cGameResetRevision"));
    string product = Convert.ToString(FieldConst(c, "cProduct"));
    // cDefaultPort is cctor-init (not a metadata constant on this build).
    int defaultPort = StsfldInt(c, "cDefaultPort") ?? 26900;

    // High-value dedicated behaviour hardcodes (const or simple cctor stsfld).
    int maxEntitiesPerMobSpawner = FieldInt(c, "cMaxEntitiesPerMobSpawner");
    int enemySenseMemory = FieldInt(c, "cEnemySenseMemory");
    float defaultMonsterSeeDistance = FieldFloat(c, "cDefaultMonsterSeeDistance");
    float sendWorldTickTimeToClients = FieldFloat(c, "cSendWorldTickTimeToClients");
    // WorldConstants.WaterLevel is cctor-initialized from Block.cWaterLevel
    // (Block cctor ldc.r4 62.88). Pin the float so zdtd/realworld can compare.
    float worldWaterLevel = StsfldR4(Exact(mod, "Block"), "cWaterLevel") ?? 62.88f;
    // Death-loot lifetime (s) and per-frame XML load budget (ms), both
    // Constants cctor-initialized (ldc.r4 300 / ldc.i4.s 50).
    float itemDroppedOnDeathLifetime = StsfldR4(c, "cItemDroppedOnDeathLifetime") ?? 300f;
    int maxLoadTimePerFrameMillis = StsfldInt(c, "cMaxLoadTimePerFrameMillis") ?? 50;
    // Party fields may be metadata const on some builds; optional.
    int? maxPartySize = null;
    float? partyActivationRange = null;
    try { maxPartySize = FieldInt(c, "cMaxPartySize"); } catch { /* optional */ }
    try { partyActivationRange = FieldFloat(c, "cPartyActivationRange"); } catch { /* optional */ }

    // Display: stock LongStringNoBuild style for Minor>=10: V {Major}.{Minor/10}.{Minor%10}
    // Matches loadgen PackageCodec.VersionLongString for EGameReleaseType.V=1.
    string display;
    if (minor >= 10)
      display = string.Format(CultureInfo.InvariantCulture, "V {0}.{1}.{2}", major, minor / 10, minor % 10);
    else
      display = string.Format(CultureInfo.InvariantCulture, "V {0}.{1}.{2}", major, minor, 0);
    // zdtd stock_wire form: "V{display without space} b{build}"
    string stockWire = string.Format(CultureInfo.InvariantCulture, "V{0}.{1}.{2} b{3}",
      major, minor >= 10 ? minor / 10 : minor, minor >= 10 ? minor % 10 : 0, build);

    float? gtTps = GameTimerTicksPerSecond(mod);
    int? saveVer = null;
    try {
      var ws = Exact(mod, "WorldState");
      // field may be const or cctor
      var f = ws.Fields.FirstOrDefault(x => x.Name == "CurrentSaveVersion");
      if (f != null && f.HasConstant) saveVer = AsInt(f.Constant);
      else saveVer = StsfldInt(ws, "CurrentSaveVersion");
    } catch { /* optional */ }

    int netPkg = mod.Types.Count(t => t.Name.StartsWith("NetPackage") && t.Name != "NetPackageManager");
    int topTypes = mod.Types.Count();
    int methodsBody = mod.Types.SelectMany(t => t.Methods).Count(m => m.HasBody);
    int gmUpdateIl = 0, saveLoadIl = 0;
    foreach (var t in mod.GetTypes()) {
      foreach (var m in t.Methods.Where(m => m.HasBody)) {
        if (t.Name == "GameManager" && m.Name == "gmUpdate") gmUpdateIl = m.Body.Instructions.Count;
        if (t.Name == "WorldState" && m.Name == "SaveLoad" && m.Parameters.Count >= 1 &&
            m.Parameters[0].ParameterType.Name.Contains("Stream"))
          saveLoadIl = m.Body.Instructions.Count;
      }
    }

    var te = TileEntityWire(mod);

    // Pre-auth challenge is not a Constants field; fixed in ConnectionManager / loadgen.
    // Document as research-confirmed wire fact (0xCA), not extracted from Constants.
    const int challengeMarker = 0xCA;
    const int challengeSize = 17;

    var sb = new StringBuilder();
    sb.AppendLine("{");
    sb.AppendLine("  \"schema\": 1,");
    sb.AppendLine("  \"generated_by\": \"tools/src/StockFacts.cs\",");
    sb.AppendLine("  \"asm\": " + JsonEsc(Path.GetFileName(asmPath)) + ",");
    sb.AppendLine("  \"extracted_utc\": " + JsonEsc(DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture)) + ",");
    sb.AppendLine("  \"version\": {");
    sb.AppendLine("    \"release_type\": " + releaseType + ",");
    sb.AppendLine("    \"major\": " + major + ",");
    sb.AppendLine("    \"minor\": " + minor + ",");
    sb.AppendLine("    \"build\": " + build + ",");
    sb.AppendLine("    \"display\": " + JsonEsc(display) + ",");
    sb.AppendLine("    \"stock_wire\": " + JsonEsc(stockWire) + ",");
    sb.AppendLine("    \"product\": " + JsonEsc(product) + ",");
    sb.AppendLine("    \"game_reset_revision\": " + gameReset);
    sb.AppendLine("  },");
    sb.AppendLine("  \"sim\": {");
    sb.AppendLine("    \"constants_ticks_per_second\": " + ticksConst + ",");
    sb.AppendLine("    \"tick_duration_sec\": " + tickDur.ToString(CultureInfo.InvariantCulture) + ",");
    sb.AppendLine("    \"gametimer_instance_tps\": " + (gtTps.HasValue ? gtTps.Value.ToString(CultureInfo.InvariantCulture) : "null"));
    sb.AppendLine("  },");
    sb.AppendLine("  \"network\": {");
    sb.AppendLine("    \"default_port\": " + defaultPort + ",");
    sb.AppendLine("    \"max_mp_players_constant\": " + maxMp + ",");
    sb.AppendLine("    \"netpackage_top_level_count\": " + netPkg + ",");
    sb.AppendLine("    \"challenge_marker\": " + challengeMarker + ",");
    sb.AppendLine("    \"challenge_size\": " + challengeSize + ",");
    sb.AppendLine("    \"challenge_marker_hex\": \"0xCA\",");
    sb.AppendLine("    \"challenge_note\": \"0xCA not a Constants field; wire/loadgen pin (ConnectionManager pre-auth)\"");
    sb.AppendLine("  },");
    sb.AppendLine("  \"chunk\": {");
    sb.AppendLine("    \"block_x_dim\": " + AsInt(FieldConst(wc, "ChunkBlockXDim")) + ",");
    sb.AppendLine("    \"block_y_dim\": " + AsInt(FieldConst(wc, "ChunkBlockYDim")) + ",");
    sb.AppendLine("    \"block_z_dim\": " + AsInt(FieldConst(wc, "ChunkBlockZDim")) + ",");
    sb.AppendLine("    \"block_layers\": " + AsInt(FieldConst(wc, "ChunkBlockLayers")) + ",");
    sb.AppendLine("    \"layer_height\": " + AsInt(FieldConst(wc, "ChunkBlockLayerHeight")));
    sb.AppendLine("  },");
    sb.AppendLine("  \"save\": {");
    sb.AppendLine("    \"current_save_version\": " + (saveVer.HasValue ? saveVer.Value.ToString() : "null") + ",");
    sb.AppendLine("    \"worldstate_saveload_stream_il\": " + saveLoadIl);
    sb.AppendLine("  },");
    sb.AppendLine("  \"census\": {");
    sb.AppendLine("    \"top_level_types\": " + topTypes + ",");
    sb.AppendLine("    \"methods_with_body_top_level\": " + methodsBody + ",");
    sb.AppendLine("    \"gmupdate_il\": " + gmUpdateIl);
    sb.AppendLine("  },");
    sb.AppendLine("  \"tile_entity_package\": {");
    sb.AppendLine("    \"present\": " + ((bool)te["present"] ? "true" : "false") + ",");
    if ((bool)te["present"]) {
      sb.AppendLine("    \"write_il\": " + te["write_il"] + ",");
      sb.AppendLine("    \"write_i32_count\": " + te["write_i32_count"] + ",");
      sb.AppendLine("    \"write_u16_count\": " + te["write_u16_count"] + ",");
      sb.AppendLine("    \"write_i16_count\": " + te["write_i16_count"] + ",");
      sb.AppendLine("    \"payload_len_likely_i32\": " + ((bool)te["payload_len_likely_i32"] ? "true" : "false"));
    }
    sb.AppendLine("  },");
    sb.AppendLine("  \"consumers\": {");
    sb.AppendLine("    \"research_docs\": [\"docs/coverage.md\", \"docs/protocol.md\", \"docs/closed-gaps.md\", \"docs/save-region.md\"],");
    sb.AppendLine("    \"loadgen\": [\"src/LoadGen/PackageCodec.cs GameVersion\", \"tests golden-wire\"],");
    sb.AppendLine("    \"zdtd\": [\"src/version.zig stock_wire\", \"src/protocol.zig challenge/ticks\"]");
    sb.AppendLine("  },");
    // Post-update orchestration metadata (not extracted from IL; pin path for agents).
    string dumpSuf = string.Format(CultureInfo.InvariantCulture, "v{0}.{1}.{2}",
      major, minor >= 10 ? minor / 10 : minor, minor >= 10 ? minor % 10 : 0);
    sb.AppendLine("  \"update\": {");
    sb.AppendLine("    \"entrypoint\": \"tools/post-update.sh\",");
    sb.AppendLine("    \"stock_sync\": \"tools/stock-sync.sh\",");
    sb.AppendLine("    \"drift_check\": \"tools/parity/drift-check.sh\",");
    sb.AppendLine("    \"dump_label_suffix\": " + JsonEsc(dumpSuf) + ",");
    sb.AppendLine("    \"dump_sets\": [\"deep\", \"deeper\", \"gaps\", \"loop-complete\", \"terrain\", \"realearth-surfaces\", \"dedi-complete\"],");
    sb.AppendLine("    \"note\": \"After TFP patch: post-update.sh then re-Dump* into il/<set>-<dump_label_suffix>/\"");
    sb.AppendLine("  },");
    // Machine-checked pin sites (mirrors check_stock_facts.py consumers).
    sb.AppendLine("  \"pins\": {");
    sb.AppendLine("    \"research\": [\"docs/coverage.md\", \"docs/protocol.md\", \"docs/closed-gaps.md\", \"docs/save-region.md\", \"README.md\", \"docs/tile-entities-power.md\", \"docs/protocol-packages.md\"],");
    sb.AppendLine("    \"siblings\": [\"7dtd-loadgen/src/LoadGen/PackageCodec.cs\", \"zdtd/src/version.zig\", \"zdtd/src/protocol.zig\", \"zdtd/src/world/store.zig\"]");
    sb.AppendLine("  },");
    sb.AppendLine("  \"behaviour\": {");
    sb.AppendLine("    \"max_entities_per_mob_spawner\": " + maxEntitiesPerMobSpawner + ",");
    sb.AppendLine("    \"enemy_sense_memory\": " + enemySenseMemory + ",");
    sb.AppendLine("    \"default_monster_see_distance\": " + defaultMonsterSeeDistance.ToString(CultureInfo.InvariantCulture) + ",");
    sb.AppendLine("    \"send_world_tick_time_to_clients\": " + sendWorldTickTimeToClients.ToString(CultureInfo.InvariantCulture) + ",");
    sb.AppendLine("    \"world_water_level\": " + worldWaterLevel.ToString(CultureInfo.InvariantCulture) + ",");
    sb.AppendLine("    \"item_dropped_on_death_lifetime_s\": " + itemDroppedOnDeathLifetime.ToString(CultureInfo.InvariantCulture) + ",");
    sb.AppendLine("    \"max_load_time_per_frame_ms\": " + maxLoadTimePerFrameMillis +
      (maxPartySize.HasValue || partyActivationRange.HasValue ? "," : ""));
    if (maxPartySize.HasValue)
      sb.AppendLine("    \"max_party_size\": " + maxPartySize.Value +
        (partyActivationRange.HasValue ? "," : ""));
    if (partyActivationRange.HasValue)
      sb.AppendLine("    \"party_activation_range\": " + partyActivationRange.Value.ToString(CultureInfo.InvariantCulture));
    sb.AppendLine("  },");
    sb.AppendLine("  \"litenet\": {");
    try {
      var ln = LoadLiteNetLib(Path.GetDirectoryName(asmPath));
      if (ln != null) {
        var nc = Exact(ln.MainModule, "NetConstants");
        int? proto = FieldConstInt(nc, "ProtocolId");
        int? hdr = FieldConstInt(nc, "HeaderSize");
        int? chan = FieldConstInt(nc, "ChanneledHeaderSize");
        int? frag = FieldConstInt(nc, "FragmentHeaderSize");
        int? seq = FieldConstInt(nc, "MaxSequence");
        int? win = FieldConstInt(nc, "DefaultWindowSize");
        int[] mtu = PossibleMtu(ln, nc);
        sb.AppendLine("    \"protocol_id\": " + (proto ?? 13) + ",");
        sb.AppendLine("    \"header_size\": " + (hdr ?? 1) + ",");
        sb.AppendLine("    \"channeled_header_size\": " + (chan ?? 4) + ",");
        sb.AppendLine("    \"fragment_header_size\": " + (frag ?? 6) + ",");
        sb.AppendLine("    \"max_sequence\": " + (seq ?? 32768) + ",");
        sb.AppendLine("    \"default_window_size\": " + (win ?? 64) + ",");
        if (mtu != null) {
          sb.AppendLine("    \"possible_mtu\": [" + string.Join(",", mtu) + "],");
          sb.AppendLine("    \"initial_mtu\": " + mtu[0] + ",");
          sb.AppendLine("    \"max_packet_size\": " + mtu[mtu.Length - 1]);
        } else {
          sb.AppendLine("    \"possible_mtu\": []");
        }
      } else {
        sb.AppendLine("    \"protocol_id\": 13");
      }
    } catch (Exception e) {
      sb.AppendLine("    \"protocol_id\": 13");
      Console.Error.WriteLine("stock-facts: litenet extraction failed: " + e.Message);
    }
    sb.AppendLine("  }");
    sb.AppendLine("}");

    var json = sb.ToString();
    if (a.Length >= 2) {
      var outPath = a[1];
      Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(outPath)) ?? ".");
      File.WriteAllText(outPath, json);
      Console.Error.WriteLine("wrote " + outPath);
    } else {
      Console.Write(json);
    }
  }
}
