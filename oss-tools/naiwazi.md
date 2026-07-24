# NAIWAZI ServerKit research notes

**Purpose:** reconstruct what NAIWAZI (奶娃子 / naiwazi.com) actually shipped, especially the “network layer” story.  
**Date:** 2026-07-16  
**Scope:** public docs (Wayback) + reverse of **free** GitHub packages. **Paid ServerKit GS/GW binaries were not obtained** (login + authtoken required; no archive of the zip packages found).

---

## 1. Product map

| Product | Role | Availability |
|---|---|---|
| **NAIWAZI 优化插件** (V1) | In-process server optim; later rebranded | Paid / closed; public use from ~2020-11 |
| **NAIWAZI ServerKit V2** | GS + **Gateway** split; optim + seamless restart | Paid monthly (¥); Standard vs Plugin |
| **NAIWAZI AntiCheat** | Package/stat validation, grief blocks | Free on GitHub |
| **NaiwaziBot** | Web admin / scripting bot | Free on GitHub |

Author branding: **NAIWAZI_Rainyeve** (ModInfo). Site: naiwazi.com / cn.naiwazi.com.

### Timeline (from archived marketing, 2022)

| Date | Claim |
|---|---|
| 2020-07-01 | A19 lag; optim plugin born; their own server peak **105** players |
| 2020-11-17 | V1 public to third-party servers |
| 2021-05-01 | ServerKit V2 release (gateway separation + optim) |

Marketing claims (treat as **vendor claims**, not measured here):

- Fix dedicated stutter / “frame drops” and “stuck gun” lag at 20-30+ players  
- ~**2×** player capacity vs stock (vanilla reference)  
- Bandwidth ~**1/3** of stock; **60 players ≤ ~20 Mbps**  
- **Gateway split**: restart GS without kicking players; seamless restart **&lt;1 s** perceived  
- **Entity independent threads** (beta / “内测”): zombies not tied to low server FPS  
- Plugin edition: optim only, **no** gateway/thread split (for panel hosts)  
- Standard edition: full gateway + thread split  

EAC: docs state EAC may show as on in listing but **was not fully verified** in V2-era text.

---

## 2. Architecture of ServerKit V2 (from official help, Wayback 2023)

Core design: **split application and network**.

```text
Clients  ←→  Gateway (Naiwazi_ServerKit_Gateway.exe)
                 │  protocol, sessions, player saves (*.ttp under Gateway/data/players)
                 │  web panel (game port + 1, e.g. 26901)
                 │  admin/blacklist/mappings/mod sync files
                 ▼
              GS = stock 7DaysToDieServer + Mods/Naiwazi_ServerKit/
                    Naiwazi_ServerKit_Starter.dll   (IModApi entry)
                    bin/Naiwazi_Optimize_Helper.dll (GS-side helper)
                    bin/gateway.txt → usually 127.0.0.1
```

Official wording (help):

> GS = native dedicated: map, game logic.  
> GW = communication protocol, network, and global data (e.g. player saves) storage and forwarding.  
> After splitting network and application, GS restart is independent of the network; players do not go offline.

### Package layout (Standard)

```text
Naiwazi_ServerKit/
  Mods/Naiwazi_ServerKit/
    ModInfo.xml
    Naiwazi_ServerKit_Starter.dll
    bin/gateway.txt
    bin/Naiwazi_Optimize_Helper.dll
  Gateway/
    Naiwazi_ServerKit_Gateway.exe
    Web/                          # control panel UI
    serverconfig.xml              # listing/display config for GW
    steam_*.dll / steam_appid.txt # Steam pieces for listing/auth path
    data/players/                 # player saves (ttp + info)
    data/*.dat                    # admin, blacklist, mappings, whitelist, ...
```

### Operational model

1. Start **Gateway** first (tray icon, purple).  
2. Activate with account + **apitoken** + paid **authtoken**.  
3. Start **GS** as normal dedicated.  
4. Control panel: all wipe/stop/restart operations preferred via panel.  
5. Seamless restart: if RAM allows **two GS**, recommended; GW keeps clients.  
6. MOD change: restart GW + GS; pure GS restart for map/logic only if mods unchanged.  
7. Player profiles live under **GW**, not only under stock userdata (but ttp said compatible with stock).

### What “replaced the network layer” means here

Not “rewrote LiteNetLib inside Unity” in the open docs. It means:

1. **Process split:** client-facing protocol/session ownership moves to **Gateway.exe**.  
2. **GS becomes a sim backend** that talks to GW (via local plugin helper).  
3. **Player persistence** moved to GW so GS can recycle while sessions stay up.  
4. Likely **protocol translation / proxying** between clients and GS (exact wire format closed).  

That matches “分离网络层协议” (separate network-layer protocol) on the 2022 home page.

Plugin-only mode: **no gateway** → classic single-process optim DLL only (V1-style).

---

## 3. Free binaries obtained and reverse notes

### Downloads (public)

| Artifact | URL |
|---|---|
| AntiCheat V3.2.9 (7DTD V1.0) | https://github.com/Naiwazi/NAIWAZI-AntiCheat/releases/download/V3.2.9/NAIWAZI_Anticheat_V3_2_9_7DTDV1_0.zip |
| NaiwaziBot V4.1.13 | https://github.com/Naiwazi/NaiwaziBot/releases/download/V4.1.13/NaiwaziBot._4_1_13_7DTDV1_0.zip |
| Older AntiCheat / Bot tags | same GitHub repos |
| ServerKit Standard/Plugin zips | **Not public** (purchase + authtoken); **not** found on Wayback as free zip |

Clone location: external, not tracked in this repo.

### Packaging pattern (AntiCheat + Bot)

Obfuscated ship layout:

```text
Mods/Naiwazi_*/
  ModInfo.xml
  1v.dll          # launcher/updater (zip compressor namespaces)
  1w.dll / 1x.dll # tiny stub
  main.bin        # real payload: still a managed PE (MZ), heavy name obfuscation
  web/            # embedded admin UI
```

`main.bin` is a **.NET assembly** (`monodis` works). Types/methods use Unicode control-character obfuscation; some namespaces remain readable.

### AntiCheat (`main.bin` → assembly `Naiwazi_AntiCheat`)

Readable types / symbols:

| Symbol | Implication |
|---|---|
| `IModApi` / `InitMod` | Standard mod entry |
| `NAIWAZI.AntiCheat.Patch.*` | Custom patch IL helpers (`CodeInstruction`, `ExceptionBlockType`) + **Prefix/Postfix/Transpiler** strings |
| `ConnectionManager`, `NetPackageManager`, `SendPackage` | Hangs off stock net dispatch |
| `NetPackageSetBlock`, `NetPackageTELock`, `NetPackageTileEntity`, `NetPackageWaterSet`, `NetPackageChat` | Inspected package types |
| `PacketCheck_DamageEntity`, `PacketCheck_LandClaimDamage`, `PacketCheck_TileEntity`, `PacketCheck_Chat`, `PacketCheck_ACL` | Named package validators |
| `BlockDamage_Cheat`, `EntityDamage_Cheat`, `Multi_BlockDamage_Cheat` | Damage rate / multi-break heuristics |
| `TileEntity*` family, `SetBlocksOnClients`, `ChunkCluster` | World/container integrity |
| Inventory / skill / god-mode related player fields | Stat checks (matches public README) |

**Conclusion for AntiCheat:** it does **not** replace LiteNetLib. It **hooks package processing / world mutation paths** and can **reject** illegal multi-block / damage / container ops (README: reject sync for K-key / replace-tool grief). That is “network layer” in the **NetPackage validation** sense.

### NaiwaziBot (`main.bin`)

| Symbol | Implication |
|---|---|
| `IModApi` / `InitMod` | In-game mod host |
| `HttpListener*` / `Webapi` | Embedded HTTP admin API |
| Many `NetPackage*` (Chat, Chunk, Teleport, PlayerStats, ConsoleCmdClient, …) | Server-side command/effects via packages |
| `NaiwaziScript.*` (JS engine stack) | Scriptable admin extensions |
| Map iterator types | Live map support |

**Conclusion for Bot:** admin/control plane, not the GS/GW network split. Complements ServerKit (release notes even say ServerKit may zero ping display).

---

## 4. Mapping claims → likely implementation

| Claim | Likely mechanism | Verified? |
|---|---|---|
| Separate network layer | **Gateway process** owns client sockets/sessions; GS behind it | **Yes** (official docs) |
| Restart without kick | GW holds sessions; swap/restart GS process | **Yes** (docs + dual-GS seamless option) |
| Lower bandwidth | Package rate limits / compression / interest (closed); marketing “1/3” | **Claim only** |
| Higher player count | Combination of optim + net offload + CN hosting practices | **Claim only** (105 peak self-report) |
| Fix 20-30p stutter / gun lag | GS helper Harmony on hot sim/net send paths | **Plausible**; closed DLL |
| Entity threads | “内测” on Standard; **not** in Plugin edition | **Claim / beta** only |
| Anti-cheat package reject | Prefix on package handlers + world APIs | **Yes** (symbols + README) |
| EAC real | Explicitly weak/incomplete in V2 docs | **Docs admit incomplete** |

---

## 5. Relevance to this workspace

| NAIWAZI idea | Relation to EfficientServer / our research |
|---|---|
| GW/GS split | **Out of scope** for EfficientServer (ops product, not Harmony optim only) |
| Seamless restart | Requires external session owner; not a simple patch |
| Entity threads | Aligns with our “jobify AI” research; their marketing claimed it early (beta) |
| Package validation | Different product (security); EfficientServer should not mix with optim |
| Bandwidth optim | Interesting if ever measured; need APM + packet capture, not vendor numbers |
| Closed optim helper | Cannot audit without licensed Standard package |

Honest takeaway for research: NAIWAZI’s distinctive engineering was **not** “better AI LOD only.” It was **moving the client-facing network and player save ownership out of the Unity GS** so the sim process could restart and (claimed) scale, plus a closed optim DLL and free anti-cheat/bot ecosystem.

---

## 6. Legal / ethics

- Free GitHub mods: fine to store and RE for research.  
- Paid ServerKit: do **not** redistribute cracked authtoken builds.  
- This folder is research only; do not ship NAIWAZI code in EfficientServer.  
- EAC/auth behavior of old V2 docs is a red flag for public production use.

---

## 7. How to go further (if you obtain a licensed Standard zip)

1. Extract `Naiwazi_Optimize_Helper.dll` + `Naiwazi_ServerKit_Gateway.exe`.  
2. Decompile helper with ILSpy (expect obfuscation).  
3. List Harmony targets / reflection type names (same string pass as above).  
4. Capture GW↔GS traffic on loopback while two clients move.  
5. Diff stock vs GW bandwidth under identical loadgen.

Without that zip, architecture above is the best public reconstruction.

---

## Changelog

- **2026-07-16:** Initial notes from Wayback ServerKit V2 help/home + RE of AntiCheat 3.2.9 and NaiwaziBot 4.1.13.
