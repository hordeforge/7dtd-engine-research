# Entity movement: MoveHelper chain and physics surface

**Hub:** [`INDEX.md`](INDEX.md).

Stock entity movement for walkers (zombies, animals, traders): the AI
`MoveHelper` -> `Entity::Move` -> CharacterController chain the dedicated
server runs each tick, and the physics surface a clone must reproduce for the
client-visible result (positions, falls, wall collisions). It also owns the
one-time **setup** that builds that CharacterController: `Entity.InitPostCommon`
-> `AddCharacterController()` constructs the grounding capsule from the model
and drives it through a `KinematicCharacterMotor` (the Kinematic Character
Controller package), not Unity's built-in CC. Animal classes reach the engine's
movement through that motor, so a creature that moves erratically is usually a
motor/capsule interaction rather than a `moveSpeed` override. `verified` from
full-v3.2.0 dumps unless marked.

## CharacterController setup (once, at spawn)

`EntityAlive.Init` -> `InitPostCommon()` -> `AddCharacterController()`
(Entity.il.txt, IL=257) is where the grounding capsule is built and the motor
attached (see [`entity-ai.md`](entity-ai.md) D8.6c for the init chain):

```text
InitPostCommon()
 └─ AddCharacterController()                     IL=257
     ├─ PhysicsTransform must resolve, else returns (no CC at all)
     ├─ EntityPlayer: read the existing Unity CharacterController
     │   (center/height/radius), wrap it in CharacterControllerUnity,
     │   add ColliderHitCallForward (server side)
     ├─ animal / non-player: read-or-build a CapsuleCollider on the node
     │    - present: center/height/radius from the CapsuleCollider
     │    - absent:  AddComponent<CapsuleCollider> with defaults
     │                center=(0,0.9,0), height=1.8, radius=0.3
     │    - physicsCapsuleCollider set: height = physicsBaseHeight,
     │                center.y = height/2
     │    - an old CharacterController on the node: read its
     │                center/height/radius, Destroy it, warn "{0} has old CC"
     │    - m_characterController = new CharacterControllerKinematic(this)
     ├─ if height > 0: SetSize(center, height, radius) (height/center divided
     │    by physicsHeightScale), store physicsBaseHeight/physicsHeight,
     │    PhysicsSetHeight(height)
     ├─ SetStepOffset(stepHeight)                 (-> motor.MaxStepHeight = step + 0.01)
     ├─ scaledExtent = (radius*lsx, halfHeight*lsy, radius*lsz);
     │    boundingBox = BoundsForMinMax(-scaledExtent, scaledExtent)
     └─ nativeCollider.enabled = false
```

The node must be a **direct child of the model root named `Physics`** and it
must be **active**. `CharacterControllerKinematic` is only constructed when
`PhysicsTransform` resolves, and the motor it adds binds its own
`CapsuleCollider` in Awake: an inactive node defers that Awake forever, so the
capsule is never bound and `SetCapsuleDimensions` NREs on a null `Capsule`. A
generated creature therefore carries an **active** `Physics` node, which is the
real-animal standard (animalDeerStag has an active `Physics` child with a
`CapsuleCollider` at the root).

Because the `Physics` node is active, the stock `GameObjectAnimalAnimation`
avatar controller cannot wrap this model. Its `Awake` (GameObjectAnimalAnimation.il.txt,
IL=61) finds its figure by `GetChild(reverse-first-active)`: it iterates the
model root's children from the last down to the first and takes the first active
one, so an active `Physics` sibling that is the highest-index active child is
picked as the figure, and that child carries no `Animation`. The stock
`Awake` then calls `anim.Play("Idle1")` and caches the `Attack1`/`Attack2`
states. A generated entity therefore drives a mod-owned controller that finds
the figure by name (the writer's `figure` node), not by active-child order.

### CharacterControllerKinematic (the kinematic motor wrapper)

`CharacterControllerKinematic.ctor` (IL=60) replaces the Unity CC for
non-player entities with the Kinematic Character Controller package:

- `KinematicCharacterSystem.EnsureCreation()`; cache `cs`; set
  `AutoSimulation = false`, `Interpolate = false`.
- `motor = PhysicsTransform.gameObject.AddComponent<KinematicCharacterMotor>()`,
  then configure it:
  - `StepHandling = 2` (StepHandlingMethod),
  - `AllowSteppingWithoutStableGrounding = true`,
  - `InteractiveRigidbodyHandling = false`,
  - `LedgeAndDenivelationHandling = false`,
  - `MaxStableSlopeAngle = 63.8`.
- bridge `cc = new CC()`; `cc.entity = entity`; `cc.motor = motor`;
  `motor.CharacterController = cc`; `motor.ForceUnground(0.1)`.

The size/step accessors all funnel into the motor: `SetSize(center, height,
radius)` -> `motor.SetCapsuleDimensions(radius, height, center.y)`
(`CharacterControllerKinematic::SetSize`, IL=8); `SetHeight(h)` clamps
`h = FastMax(h, radius*2)` then `SetCapsuleDimensions(radius, h, h*0.5)`;
`SetCenter` recomputes from the current radius/height; `SetStepOffset(s)` ->
`motor.MaxStepHeight = s + 0.01`; `GetRadius`/`GetHeight` read the motor's
`Capsule` collider directly.

`Move(dir)` (IL=17) is the per-tick drive: if `dir.y >= 0.011` the motor is
`ForceUnground(0.11)`; `cc.vel = dir / 0.05`; then `Update()` runs `CC.Move()`
and ORs `CollisionFlags.Down` (4) into the flags when
`GroundingStatus.FoundAnyGround` is set. `IsGrounded()` reads `flags & 4`.
`enableOverlapRecovery` throws `NotImplementedException`; `Rotate` is empty;
`SetSkinWidth` is a no-op (`GetSkinWidth` returns 0.08).

This is the surface the generated-creature walk-instability analysis targets:
an oversized capsule (radius/height derived from the model AABB) plus the
`MoveEntityHeaded` ground-friction lerp interact to fling and climb the entity,
so the correction is motor-configuration and capsule tuning, not a `moveSpeed`
override. The engine reads this capsule off an **active** `Physics` node and
the motor binds that same capsule in its Awake; see the asset-pipeline
walk-entity case for the measured instability.

## Call chain (per tick, `OnUpdateLive`)

```
OnUpdateLive
 └─ MoveHelper.UpdateMoveHelper()          IL=1236  (behavior: stuck/jump/dig/swim)
     └─ SetMoveForwardWithModifiers()      AI move input (per-class speeds, scaling)
EntityAlive.MoveEntityHeaded(dir, abs)     IL=292   (motion integration + gates)
 ├─ Entity.Move(dir, abs, velocity, max)   IL=138   (direction -> motion)
 └─ EntityAlive.DefaultMoveEntity()        IL=290   (friction, ground material)
Entity.ccMove(vel)                         (motion * dt -> hitMove)
 └─ CharacterControllerAbstract.Move(hitMove)       (Unity CC collide-and-slide,
                                                      stepOffset, gravity, onGround)
```

`EntityMoveHelper_UpdateMoveHelper_il.txt` (deeper-v3.2.0) maps the behavior
half: stuck checks (`ResetStuckCheck`), jump (`StartJump` when blocked up /
`CanEntityJump`), dig (`DigStart`/`DigUpdate`), `CheckAreaBlocked` /
`CheckBlockedUp` / `CheckEntityBlocked` / `CheckWorldBlocked`,
`CalcObstacleSideStep`, `Push`, `CheckForDoorAndOpen`, root-motion gates,
swim strokes, yaw slew (`SeekYaw` / `MoveTowardsAngle`), and 9
`GameRandom::get_RandomFloat` rolls for the stochastic branches.

## Motion integration

`Entity.Move` (Entity.il.txt:3694):

1. Zero the direction's y, normalize.
2. `velocity = Clamp(maxVelocity - Dot(motion, dir), 0, maxVelocity)`.
3. `motion += dir * velocity` (per axis, `ConditionalScalePhysicsAddConstant`).
   The non-absolute variant decomposes dir into transform forward/right/up.

`DefaultMoveEntity` (EntityAlive.il.txt:6101):

1. Default friction factor `0.91` (air).
2. If `onGround`, base `0.546`; for a live `EntityPlayer` on ground, resolve
   the block at the feet (`block = GetBlock(floor(x), floor(bb.min.y), z)`;
   if air or `MaterialBlock.IsGroundCover`, re-read one below), then
   `friction = Clamp(1 - blockMaterial.Friction, 0.01, 1)`.
3. Motion decay and gravity live in the per-tick integrator
   (EntityAlive.il.txt:6330-6355): `motion.x *= friction`, `motion.z *=
   friction`; `motion.y = (motion.y - World.Gravity) * 0.98` when not in an
   elevator. `World.Gravity` cctor default = **0.08** blocks/tick
   (World.il.txt:96). Effective vertical acceleration ~1.6 blocks/s^2 at 20
   TPS with a self-cap around -3.9 blocks/s (the 0.98 drag).

`ccMove` (Entity.il.txt:2780): `hitMove` scaled by `motionMultiplier` when
`isMotionSlowedDown`; `IsStuck` teleports via PhysicsTransform, else
`CharacterControllerAbstract.Move(hitMove)` returns `CollisionFlags` that
feed `onGround` / `isCollidedHorizontally` / `isCollidedVertically`.

Two CharacterController implementations carry the collide-and-slide. An
`EntityPlayer` gets `CharacterControllerUnity` (Unity's CC, read out of the
player prefab and wrapped); a non-player walker gets `CharacterControllerKinematic`
(the KCC motor that drives the capsule off an active `Physics` node, above).
Either way the collider does capsule collide-and-slide against world blocks,
`stepOffset` step-up (zombies climb a full block; the step height is
entity-class data), and ceiling/floor contact. The server's client-visible
output is the entity position per tick, which the client interpolates.

### MoveEntityHeaded motion-lerp (landMovementFactor)

`MoveEntityHeaded` (`EntityAlive::MoveEntityHeaded`, IL=292) is the
ground-motion filter on top of `Entity.Move`, and it is where the
generated-creature walk becomes erratic.
The relevant constants, ordered as they apply:

1. `landMovementFactor` is multiplied by **2.5** (IL_023E). When swimming the
   multiplier is **5** (IL_029D).
2. While `inWaterPercent > 0.3` (IL_024C), if `landMovementFactor > 0.01`
   (IL_0255) it is lerped toward 0.01 by `(inWaterPercent - 0.3) * 1.428571`
   (the partial-submersion water drag).
3. Direction magnitude is normalized (a scaled direction is reduced to unit
   length); `moveDirection.z * landMovementFactor` gives the forward speed.
4. If `lerpForwardSpeed`, the stored `speedForwardTarget` follows the commanded
   `moveDirection.z * landMovementFactor` with a step of
   `abs(target - speedForward) / 0.18` (the /0.18 at IL_0314), otherwise
   `speedForward` is set directly. `speedStrafe = moveDirection.x *
   landMovementFactor`. Before `Entity.Move`, the non-`NoCollision` branch also
   decays `motion *= ConditionalScalePhysicsMulConstant(0.546)` (IL_01DB).

The **0.546** in the asset-pipeline analysis is a friction constant, and it is
used in both methods: here in `MoveEntityHeaded` as the motion decay, and in
`DefaultMoveEntity` as the on-ground base (see above). The four constants
named there (0.546, 2.5, 0.3, 0.01) split across the two methods: 2.5 and
0.3/0.01 are the `landMovementFactor` water branches here, and 0.546 is the
friction constant (here and in `DefaultMoveEntity`). The instability the
walk-entity case measures is these lerps working on a motor whose capsule is
far larger than the creature's ground footprint, which is a motor/capsule
interaction, not a `moveSpeed` value.

## Consumed by zdtd (surface parity)

`ecs/systems.zig` `stepToward` + `applyGravity` (2026-08-20):

- Axis-separated collide-and-slide over the block grid via the Game
  `blockSolidAt` hook, with a body capsule ~(radius 0.35, height 1.8) and a
  1 mm inset so a face-tangent body slides along walls instead of gluing.
- Step-up of `step_height` (1.0) before declaring a move blocked.
- Gravity per the stock formula: `vy = (vy + gravity*dt) * 0.98` with
  `gravity = -1.6` blocks/s^2, ground snap onto the first solid cell below.

Not ported (documented gaps): jump, dig-through, swimming strokes, elevator,
entity-to-entity push, door-opening, root-motion gates, and the exact
per-class step height (rules floors are policy, entityclasses collider data
is not in the corpus).
