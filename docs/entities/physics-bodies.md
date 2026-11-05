# Physics bodies: the ragdoll collider layout file

**Owns:** `Data/Config/physicsbodies.xml`, the per-bone collider layout every entity's ragdoll is built from: its record shape, the 21 shipped bodies, and how an entity class binds one.  
**Hub:** [`INDEX.md`](../INDEX.md).

The dedicated server loads this file (`xmlsToLoad.md`: `physicsbodies` →
`PhysicsBodiesFromXml::Load`), and `EntityClass.PhysicsBody` resolves through
`PhysicsBodyLayout.Find` ([`entity-ai.md`](entity-ai.md) §9, "Physics"). What the
file states is **which bones carry a collider** and the per-axis scale and offset
of each; it does not state a shape size. `verified` for the file's records and the
class bindings (read from the shipped XML), **not decoded** for how the engine
sizes a `Detail` collider at runtime.

## Record shape

The root is `<bodies>`, holding one `<body name="...">` per layout, and each body
holds `<collider>` entries of eight properties:

| Property | Meaning |
|---|---|
| `tag` | The collider's own name, `E_BP_<part>` (`E_BP_Body`, `E_BP_LLeg`, `E_BP_Head`, ...) |
| `path` | The bone's transform path from the rig root, `/`-separated (`Hips/LeftUpLeg/LeftLeg`) |
| `collisionLayer` | Unity layer the collider sits on while the body is a collided (standing) entity; `0` on every shipped record |
| `ragdollLayer` | Unity layer once the body is a ragdoll; `21` on every shipped record |
| `collisionScale`, `ragdollScale` | Per-axis multiplier on the collider, `x y z` |
| `collisionOffset`, `ragdollOffset` | Per-axis offset in the bone's own frame, `x y z` |
| `type` | Collider kind; **`Detail` on all 226 shipped records** |
| `flags` | Which modes the collider serves; **`collision;ragdoll` on all 226** |

Two facts follow and both matter to a reimplementation:

* the file pins the **bone set** and the **scale/offset**, not the shape. All 21
  bodies state `type="Detail"`, which is a fit the engine computes from the
  skinned mesh rather than a size the file carries. A port can reproduce which
  bones collide and how they are scaled; it cannot take capsule dimensions from
  here.
* the two modes are the same collider set with different scales and offsets, so a
  standing body and its ragdoll are one layout, not two.

## The shipped bodies

21 bodies, 226 colliders. A humanoid states 11 (hips, both upper and lower legs,
both upper and lower arms, torso, head, and the feet where the rig has them); the
animals differ with the rig:

| Body | Colliders | First path |
|---|---|---|
| `Player` | 11 | `Hips` |
| `PlayerSDCS` | 11 | `Hips` |
| `zombieUMA`, `zombieStandard`, `zombieStandardFemale`, `zombieFat`, `zombieFemaleFat`, `Bandit` | 11 each | `Hips` |
| `Stag`, `Doe` | 11, 12 | `Hips` |
| `rabbit`, `boar`, `pig` | 11 each | `Hips` (`pig`: `PIG_ Pelvis`) |
| `wolf`, `AWolf`, `MountainLion`, `bear`, `zombieDog` | 11 to 13 | `Hips` |
| `vulture` | 7 | `Hips` |
| `chicken` | 5 | `Hips` |
| `snake` | 13 | `head` (a 12-segment chain) |

Scales are mostly `1 1 1`; the deviations narrow a limb on one axis
(`0.82 1 1`, `0.54 1 1` for the lower legs, `0.5 1 1`, `0.7 1 1`, one `1 1.75 1`),
which is how stock keeps a thigh's capsule from swallowing the calf beside it.

## How an entity class binds a body

`entityclasses.xml` states `PhysicsBody` on **25 classes**: the player
(`playerMale` → `PlayerSDCS`), the zombie templates (`zombieTemplateMale` →
`zombieStandard`, `zombieFatHawaiian`/`zombieBowler`/`zombieFatCop` → `zombieFat`,
`zombieFemaleFat` → `zombieFemaleFat`), the animal templates and animals
(`animalTemplateTimid` → `Stag`, `animalStag` → `Doe`, `animalTemplateHostile` →
`bear`, `animalWolf`/`animalDireWolf`/`animalCoyote` → `AWolf`,
`animalMountainLion` → `MountainLion`, `animalZombieVulture` → `vulture`,
`animalZombieDog` → `zombieDog`, `animalSnake` → `snake`, `animalBoar` → `boar`,
`animalChicken`/`animalChickenHostile` → `chicken`, `animalRabbit` → `rabbit`),
and the traders (`npcTraderTemplate` → `Player`, `npcTraderJen` → `PlayerSDCS`).

Two classes state the property **empty** (`animalInsectSwarm`, `animalBeeSwarm`),
which is the file's way of saying the class has no collider layout at all: the
two swarm bodies that also carry no attack clip.

A class that states nothing resolves through `PhysicsBodyLayout.Find` at load
(`entity-ai.md` §9). Which name that lookup takes is **not decoded** here; the
class's own name is the obvious input and the shipped data never needs it, because
every class whose body could ragdoll states the property.

## What a reader should not assume

* `collisionLayer`/`ragdollLayer` are Unity layer indices. Their bit masks and the
  collision matrix are physics-project settings, not this file, and are **not
  decoded**.
* The paths are Unity transform paths, so they are the *rig's* spelling
  (`PIG_ Pelvis`, `head`, `Neck1`/`Neck2`/`Neck3`) and not a canonical bone name.
  A rig whose bone names differ from stock's cannot be matched against this file
  by name.
* Nothing here states mass, damping or joint limits. The corpus's earlier note
  that the file carries "joint limits per bone" overstates it: this build states
  none.
