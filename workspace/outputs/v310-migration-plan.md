# V3.1.0 research migration plan

**Date:** 2026-08-02  
**From:** V3.0.1 (b4)  
**To:** V3.1.0 (b14) Henpocalypse  
**Assembly:** dedicated `Assembly-CSharp.dll` mtime 2026-08-02, Steam buildid 24436799  

## 0. Verified pin (IL)

| Field | Value |
|---|---|
| `Constants.cVersionMajor` | 3 |
| `Constants.cVersionMinor` | 10 (0x0a) |
| `Constants.cVersionBuild` | 14 (0x0e) |
| Display | `V 3.1.0 (b14)` / Compatibility `V 3.1.0` |
| Official | https://7daystodie.com/v3-1-0-henpocalypse-release-notes/ |

## 1. Census (3.0.1 -> 3.1.0 live)

| Metric | 3.0.1 | 3.1.0 live |
|---|---:|---:|
| TopLevelTypes | 4401 | **4414** |
| MethodsWithBody (top) | 43901 | **44107** |
| WorldState.SaveLoad(Stream) IL | 884 | **926** |
| GameManager.gmUpdate IL | 631 | **631** (unchanged) |
| NetPackage* wire types | 193 | **193** |

Matches prior `experimental-delta.md` (types 4414, SaveLoad 926). Experimental branch **shipped as stable 3.1.0**.

## 2. Behavioral delta (promote experimental-delta)

Already RE'd when experimental; re-verify on live 3.1.0:

1. **Wire:** `NetPackageTileEntity` adds `teBlockId:i32`, payload length **i32** (was u16).
2. **Held entities / grab:** activation on `EntityAlive`; `ItemClassHeldEntity`, wild chicken.
3. **WorldState.SaveLoad** 884->926.
4. **Analytics:** `PlayerJoinServerEventData` on join.
5. **Misc:** SetCustomVar forceSend flag; EnumGamePrefs Discord mute; ConsoleCmdLogEnvironment; EOS filters; spawn max-tier.

## 3. Coverage after first regen

- Unaccounted **5**: 4 XUi client UI (classify OOS) + `PlayerJoinServerEventData` (narrate).
- Goal: unaccounted **0**.

## 4. Execution order

A. Research pin + migration doc + promote experimental-delta  
B. Fix TE package narrative + held-entity / analytics cross-links  
C. Close unaccounted 5; regen coverage + inventories  
D. Workspace AGENTS + MODDING_BEST_PRACTICES  
E. Sibling pins (optimizer, loadgen, apm, server-guard, realworld, zdtd)  
F. Rebuild EfficientServer against 3.1.0 ASM; smoke Harmony match  
G. Commits per repo  

## 5. Dump policy

- Keep `il/*-v3.0.1/` labels as **historical** evidence names where already cited.
- New regenerable dumps: `il/*-v3.1.0/` when bulk-regenerated (git-ignored).
- Narratives pin **V3.1.0** as current target.
