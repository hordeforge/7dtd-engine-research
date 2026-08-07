# Combat and damage application (dedicated V3.1.0)

**Owns:** the server-authoritative damage pipeline: `DamageSource` (the damage
descriptor), `EntityAlive.DamageEntity` (armor mitigation, modifiers, health,
crit/dismember), and the death/kill path. This consolidates the damage threads
that touch items, blocks, stats, buffs, and progression.
**Not:** the wire package body layout ([protocol-packages.md](protocol-packages.md)
section 6.11 / [protocol.md](protocol.md) section 6.5, `NetPackageDamageEntity`
write IL=172); item attack authoring ([items.md](items.md)); block
damage ([blocks.md](blocks.md)); the ragdoll/hit VFX (client).
**Evidence:** `DamageSource`, `EntityAlive.DamageEntity` /
`ProcessDamageResponse` IL (dump locally with `tools/src/DumpMethod`, git-ignored).
**Hub:** [`INDEX.md`](INDEX.md). **Method:** [`re-methodology.md`](re-methodology.md).

All damage is resolved on the authoritative server entity, so this is a core
dedicated codepath shared by melee, ranged, traps, explosions, and environment.

---

## 1. The damage descriptor (`DamageSource`)

A hit is described by a `DamageSource`: `EnumDamageSource` (only two members:
`External=0`, `Internal=1`), `EnumDamageTypes` (bashing, suffocation, ...; value 16 =
Suffocation, see [protocol.md](protocol.md) §6.5), direction, the attacker entity
id, and the hit transform. It resolves **where** a hit lands:
`GetEntityDamageBodyPart` / `GetEntityDamageBodyPartAndEquipmentSlot` map the hit
transform to an `EnumBodyPartHit` + `EquipmentSlots`, and `AffectedByArmor` decides
whether armor mitigates it.

Sources that build a `DamageSource`: melee/ranged item actions
([items.md](items.md)), powered traps and turrets
([tile-entities-power.md](tile-entities-power.md),
[vehicles-drones-turrets.md](vehicles-drones-turrets.md)), explosions, environment
(fall, suffocation, temperature), and MinEvent damage actions
([minevents.md](minevents.md)).

---

## 2. Damage application (state machine)

`EntityAlive.DamageEntity(damageSource, strength, criticalHit, impulseScale)`
(**IL=236**) is the server apply. Ordered gates from live IL:

1. Optional zombie limb cleanup on dismember types.
2. **Consecutive-damage ignore:** if `IsIgnoreConsecutiveDamages` and same
   `EnumDamageSource` still inside timeout window in `damageSourceTimeouts`
   (`GameTimer.ticks`), return 0.
3. Resolve attacker entity; **FriendlyFireCheck** may zero damage.
4. God mode (`IsGodMode`) or **already dead** -> return.
5. Passive/passive multipliers via `EffectManager.GetValue` on attacking item;
   may set `DamageSource.DamageMultiplier`; accumulate resistance.
6. Core apply: `damageEntityLocal(...)` builds `DamageResponse`.
7. If not remote world: emit `NetPackageDamageEntity.Setup(entityId, dr)` for
   observers (wire §6.11).

### 2.1 `damageEntityLocal` (IL=484) builds `DamageResponse`

Live IL order (V3.1.0 b14):

1. Init `DamageResponse`: Source, Strength, Critical, HitDirection default 5,
   MovementState, Random float, ImpulseScale; body part + ArmorSlot +
   ArmorSlotGroup from `DamageSource`.
2. If source has direction: set HitDirection via
   `Utils.Get4HitDirectionAsInt(dir, look)`.
3. If `AffectedByArmor`: `Equipment.CalcDamage` fills Strength and ArmorDamage.
4. `GetDamageFraction(Strength)` vs Health; Fatal when Strength >= Health.
5. Head-part (`HitBodyPart & 2`) and damage-fraction thresholds feed
   dismember chance (source-dependent 0.2 / max(0.5,0.3) / 0.12 / max(0.5,0.5)
   bands in IL).
6. If `canDisintegrate` and fraction high enough: `Disintegrate()`.
7. `CheckDismember(ref dr, chance)`.
8. Stun accumulators: body-part mask `207` adds to `StunProne`; leg hits add
   Strength * (crit?2:1) to `StunKnee` when `CanStun` and walkType != 21 and
   not already prone-stun (2).
9. Prone knockdown if `GetDamageFraction(StunProne) >= KnockdownProneDamageThreshold`
   (threshold > 0): Stun=2, duration random in `KnockdownProneStunDuration`.
10. Else kneel if fraction(StunKnee) >= `KnockdownKneelDamageThreshold`:
    Stun=1, duration from `KnockdownKneelStunDuration`.
11. Effective impact score `Strength + ArmorDamage/2`; PainHit / remaining
    health gates; Fatal if post-health would be <= 0; may `AddHealth(-Strength)`
    and `FireEvent` on the local apply path.

### 2.2 `ProcessDamageResponse` (IL=86) net fan-out

1. If `time - lastAliveTime < 1`: return (1 s post-spawn immunity).
2. Base `Entity.ProcessDamageResponse` then `ProcessDamageResponseLocal`.
3. If world not remote:
   - Local attacker + remote player victim: `SendPacketToTrackedPlayers`
     (`NetPackageDamageEntity`).
   - Else if `DamageSource.BuffClass` set: same tracked-players send.
   - Else: `SendPacketToTrackedPlayersAndTrackedEntity` (includes attacker).

### 2.3 `ProcessDamageResponseLocal` (IL=903) apply side effects

High-signal gates from live IL:

- Null emodel: return.
- Local primary-player bonus UI: BonusDamageType 1 = sneak notify, 2 = mult notify.
- Attacker `SetDamagedTarget`; sleeper noise wake + `ConditionalTriggerSleeperWakeUp`.
- Armor wear: split `ArmorDamage` across `Equipment.GetArmor()` pieces
  (`UseTimes += EffectManager.GetValue(PassiveEffects=7, ...) * ItemDegradationModifier`).
- `ApplyLocalBodyDamage`; store `lastDamageResponse`.
- Dismember resist passives 175/176 can zero dismember; else impact force +
  `ExecuteDismember`.
- Enemy headshot-only / headshot-finisher: non-head hits can zero Strength/Fatal
  when `IsHeadshotOnly` / `IsHeadshotFinisher` and no `nohead` tag.
- Stun type 2 (prone): ragdoll if crit bashing or rand < 0.6; else `BeginStun`;
  duration full or *0.5 if already stunned differently.
- Stun type 1 (kneel): ragdoll upgrade on crit or rand < 0.25; else BeginStun.
- PainHit: accumulate `painResistPercent` (cap 3) from
  `EntityClass.PainResistPerHit` (+ low-health variant); drive
  `StartAnimationHit` with resist-scaled intensity.
- Health subtract (god mode skip); wounded FireEvent type 7; on death set
  `entityThatKilledMe` and `Entity.Kill`; electrocute if damage type 10;
  revenge target + `EAIManager.DamagedByEntity`; FireEvent 106 on player attacker
  and victim.

```mermaid
stateDiagram-v2
  [*] --> Incoming
  Incoming --> Ignored: entity already dead / invulnerable -> return
  Incoming --> Resolve: DamageSource resolves body part + equipment slot
  Resolve --> Armor: AffectedByArmor -> mitigate, apply ArmorDamage to the slot
  Resolve --> NoArmor: not affected by armor
  Armor --> Modifiers: buff / passive-effect damage modifiers (buffs.md)
  NoArmor --> Modifiers
  Modifiers --> ApplyHealth: damageEntityLocal builds DR; health subtract in response
  ApplyHealth --> Response: ProcessDamageResponse (pain, crit, dismember, stun)
  Response --> Survives: Health > 0
  Response --> Dies: Health <= 0
  Survives --> [*]
  Dies --> Death
  Death --> [*]
```

---

## 3. Death and kill (state machine)

When health reaches zero the entity dies: it awards the kill (XP to the attacker,
[progression.md](progression.md)), clears death buffs
([buffs.md](buffs.md) `RemoveDeathBuffs`), drops loot
([loot-economy.md](loot-economy.md)), and for players enters the respawn path
([server-lifecycle.md](server-lifecycle.md)).

### 3.1 `OnEntityDeath` (IL=146) / `dropItemOnDeath` (IL=105)

**`OnEntityDeath` order:** score bump; stop audio; detach; **`AwardKill(attacker)`**;
death particle via `SpawnParticleEffectServer`; optional death game message;
kill log; **`ModEvents.SEntityKilled`**; **`dropItemOnDeath()`**.

**`dropItemOnDeath`:** walk inventory slots; if `ItemClass.CanDrop`,
`ItemDropServer` with lifetime `Constants.cItemDroppedOnDeathLifetime` and clear
slot; flashlight off; `Equipment.DropItems()`; scale `lootDropProb` via
`EffectManager` and floor with `LootContainer.LootBagChance`; if not
`LootContainer.NoLoot` and random &lt; prob, **`Entity.DropBagServer()`**.

**`SetDead` (IL=8):** base `Entity.SetDead` + force `Health.Value = 0`.

**`AwardKill` (IL=66):** if killer is a distinct living player: count zombie vs
player kill by `entityType` (1 player / 2 zombie-ish); `GameManager.AwardKill`;
special score condition if holding `gunHandgunT2Magnum44`;
`GameManager.AddScoreServer(killerId, zombieKills, playerKills, team, conditions)`.

**`GameManager.AwardKill` (IL=27):** if killer remote →
`NetPackageEntityAwardKillServer` to killer (flags 192); else local
`QuestEventManager.EntityKilled`.

**`GameManager.AddScoreServer` (IL=56):** client →
`NetPackageEntityAddScoreServer` to server; server: if target remote →
`NetPackageEntityAddScoreClient` to that entity; else local
`EntityAlive.AddScore`.

**`EntityAlive.AddScore` (IL=97):** increment KilledZombies/Players/Died counters;
score from GameStats weights; clamp score ≥ 0; achievement stats hooks.

**`OnDeathUpdate` (IL=76):** while corpse remains, track `DeathHealth` vs
`EntityClass.DeadBodyHitPoints`; when depleted enough, death particle and unload
path (corpse cleanup after body HP exhausted).

```mermaid
stateDiagram-v2
  [*] --> Alive
  Alive --> Dying: Health <= 0 (from DamageEntity)
  Dying --> OnDeath: EntityAlive.OnEntityDeath / SetDead
  OnDeath --> AwardKill: attacker gains XP (progression.md)
  OnDeath --> DeathBuffs: EntityBuffs.RemoveDeathBuffs (buffs.md)
  OnDeath --> DropLoot: corpse / bag loot (loot-economy.md)
  AwardKill --> Gone
  DeathBuffs --> Gone
  DropLoot --> Gone
  Gone --> Despawn: zombie/animal -> removed
  Gone --> Respawn: player -> respawn flow (server-lifecycle.md)
  Despawn --> [*]
  Respawn --> [*]
```

External kills (suicide, admin, environment) arrive as `NetPackageDamageEntity`
([protocol.md](protocol.md) §6.5) and funnel into the same `DamageEntity` path, so
the server validates and applies them uniformly.

---

## 4. Dedicated relevance and residuals

- **Server-authoritative:** all mitigation, health changes, death, and kill
  awards are computed on the server; clients send hit requests and animate results.
- **Residual / content:** damage/armor numbers and body-part maps are XML content;
  hit VFX, ragdoll, and gore are client; block damage has its own path
  ([blocks.md](blocks.md)).

---

## Combat leaf types

Leaf types on the edges of the damage flow above:

- **`AttackHitInfo`** (nested in `ItemActionAttack`): the mutable hit-result
  carrier an attack fills in as it resolves, with a block half
  (`blockBeingDamaged`, `hitRef`, `bBlockHit`, `hardnessScale`, `itemsToDrop`,
  `bHarvestTool`) and an entity half (`entityHit`, `damageGiven`, `bKilled`,
  `isCriticalHit`), plus `materialCategory` / `WeaponTypeTag` for surface
  effects; it is threaded through `Block.DamageBlock` / `OnBlockDamaged`, so
  traps (`BlockBarbed`, `BlockBladeTrap`, `BlockMine`) report through the same
  struct the server damage path reads.
- **`BodyParts`** (nested in `BodyAnimator`): a two-field holder (`BodyObj`
  model root + `RightHandT` transform) the avatar controllers use to attach
  held items and locate the active model
  (`AvatarMultiBodyController.GetRightHandTransform`); pure render-rig
  plumbing, **client-only** in practice.
- **`ApplyExplosionForce`**: a MonoBehaviour whose `Explode(pos, power, radius)`
  runs `Physics.OverlapSphereNonAlloc` (1024-collider cap) and applies
  `Rigidbody.AddExplosionForce` with power x20, radius x1.75, upwards
  modifier 3; its only caller is `GameManager.ExplosionClient`, so it is the
  cosmetic debris/ragdoll knockback, **client-only** (explosion damage itself
  is the server path in §2).
- **`StunBeamWeapon`** (nested in `DroneWeapons`, subclass of
  `DroneWeapons.Weapon`, not an `EModel` type): the robotic drone's stun-beam
  mod, constructed in `EntityDrone.LoadMods`; `Fire(target)` writes the
  target's `_droneStunDamage` cvar from the mod item's Quality and applies
  `buffShocked` (the server-relevant gameplay effect, resolved through
  [buffs.md](buffs.md)), then spawns muzzle flash/smoke particles and audio
  (the client render half).

---

## Related docs

| Doc | Role |
|---|---|
| [items.md](items.md) | Attack item actions that build a DamageSource |
| [entity-stats.md](entity-stats.md) | Health the damage is applied to |
| [buffs.md](buffs.md) | On-hit / death buffs, damage modifiers |
| [progression.md](progression.md) | Kill XP award |
| [protocol.md](protocol.md) | `NetPackageDamageEntity` wire body (§6.5) |
| [blocks.md](blocks.md) | Block damage (separate but parallel) |

## Changelog

- **2026-08-07:** damageEntityLocal IL=484 DR build (armor, dismember chance,
  StunProne/StunKnee thresholds, Fatal); ProcessDamageResponse net fan-out;
  ProcessDamageResponseLocal IL=903 (armor wear, headshot gates, stun/pain,
  kill/revenge/FireEvent).
- **2026-08-07:** OnDeathUpdate corpse HP; AwardKill/AddScoreServer; SetDead;
  OnEntityDeath / dropItemOnDeath.
- **2026-08-07:** DamageEntity IL=236 gate order (consecutive timeout, FF, god,
  dead, EffectManager mult, damageEntityLocal, S2C package).
- **2026-08-07:** NetPackageDamageEntity Process IL=172 local-player early outs
  (damageTyp 15 discard; ambient src0 + typ 1/25 + attacker -1 discard).
- **2026-07-28:** Wire pointer to protocol-packages 6.11; ProcessPackage apply entry.

- **2026-07-23:** Initial combat/damage reversal (DamageSource, DamageEntity apply, death/kill path) consolidating the cross-system damage flow, with state machines.
- **2026-07-24:** Added combat leaf narration (`AttackHitInfo`, `BodyParts`, `ApplyExplosionForce`, `StunBeamWeapon`); of these only `BodyParts` and `ApplyExplosionForce` are client-only (`AttackHitInfo` is server damage state and `StunBeamWeapon` applies a server buff).
