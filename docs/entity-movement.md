# Entity movement: MoveHelper chain and physics surface

**Hub:** [`INDEX.md`](INDEX.md).

Stock entity movement for walkers (zombies, animals, traders): the AI
`MoveHelper` -> `Entity::Move` -> CharacterController chain the dedicated
server runs each tick, and the physics surface a clone must reproduce for the
client-visible result (positions, falls, wall collisions). `verified` from
full-v3.2.0 dumps unless marked.

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

The CharacterController (client+server Unity physics) does the rest: capsule
collide-and-slide against world blocks, `stepOffset` step-up (zombies climb a
full block; the CC step height is entity-class data), and ceiling/floor
contact. The server's client-visible output is the entity position per tick,
which the client interpolates.

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
