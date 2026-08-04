# Docs and research findings audit (2026-08-03)

**Scope:** stock RE corpus (`7dtd-research`), EfficientServer evidence (`7dtd-optimizer`), zdtd product gates, loadgen/apm residuals.  
**Pin:** V **3.1.0 (b14)** Henpocalypse.  
**Method:** primary docs + TODO ledgers + live session IDs from this campaign. Not a full re-dump of Assembly-CSharp.

---

## Summary

| Domain | Verdict | Confidence |
|---|---|---|
| Managed RE stop condition | **Hold** (unaccounted 0; non-IL residuals only) | high |
| V3.1.0 pin across workspace | **Consistent** in AGENTS / MODDING / coverage / STATUS | high |
| EfficientServer on 3.1 | **Pays under moderate/heavy; mixed at 64p** | high (measured) |
| zdtd join + death/respawn | **PASS** after version + fixture work | high (playtest) |
| zdtd full demo green | **FAIL residual 8** | high (playtest) |
| Historical V3.0.1 dump path names | **Intentional** (`il/*-v3.0.1/`) | high |
| Some narrative titles still say V3.0.1 | **Cosmetic / historical**; pin banners added where high-traffic | medium |

---

## Strongest evidence

### Research (stock)

1. Coverage families 1-11 **Closed**; residuals.md §1 is non-IL only.
2. Live V3.1.0 census (campaign): types **4414**, methods-with-body **~44107**, gmUpdate **631**, SaveLoad **926**, NetPackage wire **193**.
3. Breaking deltas documented: TE outer `teBlockId:i32` + `payloadLen:i32`; PackageIds VersionInformation minor=10 build=14; WorldState CurrentSaveVersion=23 gate depth.
4. Origin FixedUpdate on dedicated is a no-op (residuals §4 correction).

### Optimizer

1. Moderate 16p ES A/B: ms/tick -7%, STW worst -91%, alloc -84% (`session_20260802_135519` / `_135942`).
2. Heavy 48p: ms/tick -35%, late-share -52%, STW worst -88% (`001826` / `003006`).
3. Canonical 64p: **mixed** - STW/late-share better ON; ms_per_tick worse ON (`004634` / `005248`). Do not overclaim.
4. Animator CullCompletely stress: frame 85->76 ms; root-motion mostly restored; default-on still needs human soak.

### zdtd

1. Unit tests **197/197**.
2. playtest-zdtd progression: 73/10 → fixtures on → **75/8** with kill/spawn/respawn PASS.
3. Residual 8 are product depth (dig pad, block dmg, loot VFX, craft/trader), not join.

---

## Contradictions / honesty fixes applied this audit

| Issue | Fix |
|---|---|
| STATUS "Full playable stock dedi PASS (core loop, clean)" vs demo 75/8 | Softened to **PASS core; demo partial** |
| TODO gates still 189/189 / 73 fail | Updated to **197/197** / **75/8** |
| MISSING_FEATURES tests 189/189 | → **197/197** |
| protocol.md / network.md titles V3.0.1 only | Pin banners for V3.1.0 + delta pointers |
| Optimizer Phase 2 "record session IDs" open | Marked done with V3.1 session list |
| Animator "stress open" | Stress done; residual = human soak |
| research residuals no product pointer | residuals.md **§5** sibling residual table |

### Remaining soft inconsistencies (not defects)

| Item | Note |
|---|---|
| `il/*-v3.0.1/` dump directory names | Historical regenerate names; content re-checked on 3.1.0 where delta docs say |
| Many family narratives still open with "V3.0.1" in H1 | Still true as derivation pin; current pin is coverage.md / INDEX |
| RESULTS.md campaign numbers mostly V3.0.1 | Explicit; V310_APM_BASELINE is the 3.1 layer |
| bag_add_item "PASS" with flat bag count | Weak pass; economy give still residual |
| playtest repo not a git tree | Orch fix lives on disk under `7dtd-playtest/scripts/` |

---

## Residual ledgers (single map)

| Project | Residual hub |
|---|---|
| Research non-IL | `7dtd-research/docs/residuals.md` §1 |
| Research product pointer | `residuals.md` §5 |
| zdtd open + playtest 8 | `zdtd/TODO.md` Open now + Residual playtest fails |
| zdtd gap inventory | `zdtd/docs/MISSING_FEATURES.md` |
| Optimizer | `7dtd-optimizer/TODO.md` Residual section |
| Loadgen | `7dtd-loadgen/TODO.md` Residual section |
| APM | `7dtd-apm/TODO.md` Residual section |
| Playtest evidence | `zdtd/docs/PLAYTEST_V310_20260803.md` |
| APM evidence | `7dtd-optimizer/docs/V310_APM_BASELINE.md` |

---

## Findings that should not be re-litigated without new evidence

1. Managed RE unaccounted=0 stop condition.
2. Safe Harmony largely exhausted for entity wall without fidelity risk.
3. Serialize-once already stock; do not re-propose as EfficientServer novelty.
4. Animator `enabled=false` refuted; CullCompletely is the path.
5. Path admission defaults stay vanilla (0/0).
6. Canonical 64p is not a clean ES ms/tick win story.
7. zdtd server-side `give` is loot-bag drop (client-authoritative inv).

---

## Recommended freeze policy

**Freeze** research + optim evidence loop + zdtd join/respawn gates.  
**Reopen** only for: TFP patch, a chosen residual fail from the 8, or animator human soak → default-on decision.

---

## Sources (workspace)

| Artifact | Path |
|---|---|
| Coverage | `7dtd-research/docs/coverage.md` |
| Residuals | `7dtd-research/docs/residuals.md` |
| Experimental delta | `7dtd-research/docs/experimental-delta.md` |
| V3.1 APM baseline | `7dtd-optimizer/docs/V310_APM_BASELINE.md` |
| RESULTS | `7dtd-optimizer/docs/RESULTS.md` |
| zdtd STATUS | `zdtd/docs/STATUS.md` |
| Playtest report | `zdtd/docs/PLAYTEST_V310_20260803.md` |
| Playtest log | `zdtd/server/logs/playtest_zdtd_demo_20260803f.log` |
| Workspace pin | `AGENTS.md`, `MODDING_BEST_PRACTICES.md` |

## Changelog

- **2026-08-03:** Initial campaign audit after V3.1 retarget + ES A/B + zdtd playtest.

## Leftover cleanup (2026-08-04)

| Leftover | Action |
|---|---|
| Stale unit-test counts 197 | Updated to **239/239** in STATUS/TODO/MISSING/PLAYTEST |
| Admin version `V3.x` | Now `V3.1.0 wire` |
| Dig/place no solid under feet | **spawnSurface** snaps join/respawn to DTM + terrDirt fill |
| STATUS full-playable overclaim | Already softened in prior audit |
| Playtest orch fixtures stock-only | Already fixed on disk (`want_fixtures` includes zdtd) |
| Economy residual 4 (food/craft/trader/loot VFX) | Still open product depth; not closed by spawn pad |
| Block damage residual | Still open; server SetBlock damage path present; needs re-measure after pad fix |

zdtd commit: `d5bfc77` Snap spawn to DTM surface.
