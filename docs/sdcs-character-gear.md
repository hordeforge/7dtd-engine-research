# SDCS: skinned character system, archetypes and armor authoring (V3.1.0)

**Owns:** the **S**kinned **D**ynamic **C**haracter **S**ystem: the archetype data
model, the three XML/asset contracts a modder authors against (`items.xml` `SDCS`
property class, `archetypes.xml`, `Resources/sdcs.xml`), the asset-path grammar,
and the runtime rig-stitching pipeline that turns an equipped armor item into
skinned geometry on the player rig.  
**Not:** how armor *behaves* (`ItemClassArmor` stats, damage mitigation) — that is
[`items.md`](items.md) and [`combat-damage.md`](combat-damage.md). Not equipment
slot bookkeeping (`Equipment`) — [`items.md`](items.md).  
**Server relevance — read this first:** a dedicated server **never executes** the
rig pipeline. `SDCSUtils`, `SDCSDataUtils` and `SDCSArchetypesFromXml` stay
classified client-render in [`out-of-scope-surface.md`](out-of-scope-surface.md);
this doc narrates them. What *is* server-side is the **data**: `archetypes.xml` is
entry 22 of `WorldStaticData::xmlsToLoad` with `LoadAtStartup` + `SendToClients` +
`LoadClientFile` all true (see [`inventories/xmlsToLoad.md`](inventories/xmlsToLoad.md)),
and the `SDCS` property class is parsed by `ItemClass::Init` on **every** peer,
server included. A server operator shipping a custom-armor mod edits files the
server loads and pushes; this doc is the contract those files must satisfy.  
**Method:** [`re-methodology.md`](re-methodology.md). **Hub:** [`INDEX.md`](INDEX.md).

---

## 1. The shape of the system

A player model is not a prefab. It is **assembled at runtime** from a base rig
plus N independently-authored skinned meshes, all re-bound to the base rig's bone
transforms:

```text
baseRigPrefab.prefab            one skeleton: Origin/Hips/Spine.../Neck/Head, RigConstraints, IKRig
  + base parts                  head, body, hands, feet   (race/variant/sex-specific .fbx)
  + per-slot gear               one skinned mesh per equipped armor item
  + hair / facial hair          MeshMorph assets morphed onto the head
  = one Animator-driven avatar
```

Every added mesh is *stitched*: instantiated under the rig, then its
`SkinnedMeshRenderer.bones[]` array is rewritten to point at the **base rig's**
transforms of the same name. This is why bone naming is the single hardest
authoring constraint in SDCS — a name mismatch silently drops the bone.

Three type families do the work:

| Type | Base | Role |
|---|---|---|
| `Archetype` | Object | The character description: sex, race, variant, hair/facial-hair/eye names, plus a runtime `List<SlotData> Equipment` |
| `SDCSUtils` | Object | The rig assembly pipeline (59 methods): path resolution, load, stitch, bone allowlist, constraints, teardown |
| `SDCSDataUtils` | Object | The *catalog* of legal race/variant/hair/eye/hair-color values, from `Resources/sdcs.xml` |
| `SDCSArchetypesFromXml` | Object | `archetypes.xml` reader/writer |
| `EModelSDCS` | EModelPlayer | The entity model component that owns the rig and rebuilds it on equipment change |
| `AvatarSDCSController` | LegacyAvatarController | Binds the assembled rig's named bones to the animator |

---

## 2. Data model

### 2.1 `Archetype`

Fields (from `DumpType`): `s_Archetypes` (static `CaseInsensitiveStringDictionary<Archetype>`),
`Name`, `Race`, `Variant`, `Hair`, `HairColor`, `MustacheName`, `ChopsName`,
`BeardName`, `EyeColorName`, `IsMale`, `CanCustomize`, `Equipment`.

| Member | IL | Behaviour |
|---|---:|---|
| `Archetype::.ctor(String,Boolean,Boolean)` | 30 | Hair/HairColor/Mustache/Chops/Beard default to `""`; `EyeColorName` defaults to `"Blue01"` |
| `Archetype::get_Sex()` | 7 | `IsMale ? "Male" : "Female"` — this string is the `{sex}` substitution everywhere |
| `Archetype::set_Sex(String)` | 7 | `IsMale = value.ToLower() == "male"` |
| `Archetype::get_ShowInList()` | 12 | false for `BaseMale` / `BaseFemale` (the two reserved templates) |
| `Archetype::GetArchetype(String)` | 14 | lookup in `s_Archetypes` (case-insensitive), null when absent |
| `Archetype::SetArchetype(Archetype)` | 28 | upsert; if `CanCustomize == false`, also `ProfileSDF::SaveArchetype(Name, IsMale)` |
| `Archetype::AddEquipmentSlot(SlotData)` | 11 | lazily allocates `Equipment` |
| `Archetype::Clone()` | 48 | copies every field **except** `Equipment` (the clone starts with no equipment list) |
| `Archetype::InitializeStatics()` | 3 | allocates `s_Archetypes` |
| `Archetype::SaveArchetypesToFile()` | 6 | writes every registered archetype back through `SDCSArchetypesFromXml::Save` |

`Variant` is formatted **everywhere** as `Variant.ToString("00")` — a two-digit,
zero-padded folder name (`01`, `02`, ...). Authoring a variant `1` folder named
`1` will not resolve.

### 2.2 `SDCSUtils/SlotData`

The per-gear-piece record. Fields: `PrefabName`, `PartName`, `BaseToTurnOff`,
`HairMaskType`, `FacialHairMaskType`.

| Field | Meaning |
|---|---|
| `PrefabName` | Asset path of the gear prefab, **with substitution markers** (§4) |
| `PartName` | Which child transform inside that prefab is the mesh to stitch (`head`, `body`, `hands`, `feet`, `helmet`, `torso`, `gloves`, `boots`, ...) |
| `BaseToTurnOff` | Comma-separated list of rig child transforms to **destroy** when this piece is worn (hides the bare body under the armor) |
| `HairMaskType` | `Full` (0) / `Hat` (1) / `None` (2) — how head hair is masked while worn |
| `FacialHairMaskType` | same enum, for mustache/chops/beard |

`HairMaskTypes` is a nested enum of `SlotData`: `Full=0, Hat=1, None=2`. `Full` is
the default (no masking); the mask value becomes a **filename suffix** on the hair
asset (§4.4).

---

## 3. The three authoring contracts

### 3.1 `items.xml` — the `SDCS` property class (the armor authoring contract)

This is the one that matters for authoring a wearable. `ItemClass::Init` (IL=1196)
checks `Properties.Classes` for a class named `SDCS`; when present it allocates
`ItemClass::SDCSData` and reads five optional sub-properties:

| Sub-property | Target field | Parser |
|---|---|---|
| `Prefab` | `SlotData::PrefabName` | `DynamicProperties::GetString("SDCS","Prefab")` |
| `TransformName` | `SlotData::PartName` | string |
| `Excludes` | `SlotData::BaseToTurnOff` | string (comma-separated at use time) |
| `HairMaskType` | `SlotData::HairMaskType` | `Enum.Parse(typeof(HairMaskTypes), ...)` |
| `FacialHairMaskType` | `SlotData::FacialHairMaskType` | `Enum.Parse(typeof(HairMaskTypes), ...)` |

Shape in XML:

```xml
<item name="armorMilitaryHelmet">
    <property class="SDCS">
        <property name="Prefab" value="@:Entities/Player/{sex}/Gear/Military/military_helmet_{sex}.prefab"/>
        <property name="TransformName" value="helmet"/>
        <property name="Excludes" value="head"/>
        <property name="HairMaskType" value="Hat"/>
        <property name="FacialHairMaskType" value="Full"/>
    </property>
</item>
```

Every sub-property is guarded by its own `DynamicProperties::Contains` check, so
all five are optional; a `SDCS` class with no `Prefab` yields a `SlotData` whose
`PrefabName` is null, and `GetPathForSlotData` then returns null and the piece
renders nothing (silently, for non-`head` parts).

`Enum.Parse` is **not** the try-parse form: an unrecognised `HairMaskType` value
throws during item load rather than falling back. Values are exactly `Full`,
`Hat`, `None`.

### 3.2 `archetypes.xml` — `SDCSArchetypesFromXml`

Loaded through `WorldStaticData::LoadSDCSArchetypes(XmlFile)` (IL=6; the state
machine's `MoveNext` IL=15 just calls `SDCSArchetypesFromXml::Load`).

`SDCSArchetypesFromXml::Load(XmlFile)` (IL=36) walks root children and calls
`parseArchetype` for every element named `archetype`.

`SDCSArchetypesFromXml::parseArchetype(XElement)` (IL=221) reads these attributes:

| Attribute | Field | Default | Parser |
|---|---|---|---|
| `name` | `Name` | `""` | string; see the `BaseMale`/`BaseFemale` note below |
| `male` | `IsMale` | `false` | `StringParsers::ParseBool` |
| `race` | `Race` | `"White"` | string |
| `variant` | `Variant` | `1` | `StringParsers::ParseSInt32` |
| `hair` | `Hair` | `""` | string |
| `hair_color` | `HairColor` | `""` | string |
| `mustache` | `MustacheName` | `""` | string |
| `chops` | `ChopsName` | `""` | string |
| `beard` | `BeardName` | `""` | string |
| `eye_color` | `EyeColorName` | `"Blue01"` | string |

`BaseMale` / `BaseFemale` are special-cased: matching either name presets
`CanCustomize = true`, `IsMale = (name == "BaseMale")`, `Race = "White"`,
`Variant = 1`, and **skips the `male` attribute read entirely**. The `race`,
`variant` and remaining attribute reads still run afterwards, so those presets can
still be overridden by explicit attributes on the same element.

The `eye_color` default is `"Blue01"`: the local is initialised to the lowercase
`"blue01"`, but the no-attribute branch overwrites it with `"Blue01"`, so the
lowercase initialiser is dead code.

Child elements named `equipment` go through `parseEquipment` (IL=57), which reads
`transform_name` → `PartName`, `prefab` → `PrefabName`, `excludes` →
`BaseToTurnOff`, and **returns null unless both `transform_name` and `prefab` are
non-empty**. Note the asymmetry with §3.1: the archetype form has no
`HairMaskType`/`FacialHairMaskType` attributes; those only reach `SlotData` via
items.

The parsed archetype is registered with `Archetype::SetArchetype`.

`SDCSArchetypesFromXml::Save(String,List<Archetype>)` (IL=69) writes
`GameIO::GetGameDir("Data/Config")/<name>.xml` with one self-closing line per
archetype and **only four attributes** — `name`, `male`, `race`, `variant`:

```text
<archetypes>
    <archetype name="{Name}" male="{isMale}" race="{Race}" variant="{Variant}" />
</archetypes>
```

The writer is therefore **lossy**: hair, facial hair, eye colour and every
`<equipment>` child are dropped on round-trip. Do not use in-game save as a way to
edit a hand-authored `archetypes.xml`.

### 3.3 `Resources/sdcs.xml` — `SDCSDataUtils` (the value catalog)

`SDCSDataUtils::Load()` (IL=260) reads the `sdcs` `TextAsset` out of Unity
`Resources`, clears all seven static dictionaries and dispatches per element name:

| Element | Attributes | Target |
|---|---|---|
| `variant` | `race`, `index`, `is_male` | `VariantData: Dictionary<GenderKey, List<int>>` |
| `eye_color` | `name` | `EyeColorList: List<string>` |
| `hair_color` | `index`, `name`, `prefab_name` | `HairColorDictionary: Dictionary<string, HairColorData>` |
| `hair` | `name`, `is_male` | `HairDictionary` |
| `mustache` | `name`, `is_male` | `MustacheDictionary` |
| `chops` | `name`, `is_male` | `ChopsDictionary` |
| `beard` | `name`, `is_male` | `BeardDictionary` |

`SDCSDataUtils::ParseHair(XElement)` (IL=38) is the shared reader for the four
hair-family elements (`name`, `is_male`). `GenderKey` is `(Name, IsMale)`, so the
same race or hair name can exist independently per sex.

`SDCSDataUtils::SetupData()` (IL=2) is just `Load()`. Read-side helpers:
`GetRaceList(Boolean)` (IL=39, sorted), `GetVariantList(Boolean,String)` (IL=52),
`GetHairNames(Boolean,HairTypes)` (IL=48), `GetHairColorNames()` (IL=23),
`GetEyeColorNames()` (IL=2). `HairTypes` is `Hair=0, Mustache=1, Chops=2, Beard=3`.

#### The editor-side generator

`sdcs.xml` is not hand-written upstream: `SDCSDataUtils::Save()` (IL=249) calls
`SetupDataFromResources()` (IL=18) and then serialises the dictionaries back out
to `Application.dataPath + "/Resources/sdcs.xml"`. The `*FromResources` family
**scans the project asset tree** and is therefore only meaningful in the Unity
project, not a shipped build:

| Method | IL | Scans |
|---|---:|---|
| `ParseRaceVariantFromResources(Boolean)` | 75 | `{dataPath}/AssetBundles/Player/{Male\|Female}/Heads/<race>/<variant>` — directory names become race + variant int |
| `GetHairNamesFromResources(Boolean,HairTypes)` | 55 | `{dataPath}/AssetBundles/Player/{sex}/` + `Hair/` (Hair) or `FacialHair/{HairTypes}/` (the other three) |
| `GetEyeColorNamesFromResources()` | 38 | `{dataPath}/AssetBundles/Player/Common/Eyes/Materials/*.mat` (skips `.meta`, strips `.mat`) |
| `GetHairColorNamesFromResources()` | 40 | `{dataPath}/AssetBundles/Player/Common/HairColorSwatches/*.asset` (skips `.meta`, strips `.asset`) |
| `LoadHairColorFromResources(Dictionary)` | 50 | splits each swatch filename as `Index = int(name.Substring(0,2))`, `Name = name.Substring(3)`, `PrefabName = name` — so a swatch file is named `NN<sep>Name` (two digits, one separator character, then the display name) |

The **directory layout is the schema**: adding a race means adding a
`Heads/<Race>/<NN>/` folder; adding a hair style means adding a folder under
`Hair/`. `SDCSDataUtils::get_baseHairColorLoc()` (IL=2) is
`AssetBundles/Player/Common/HairColorSwatches` — note it is the *editor* path form,
distinct from the runtime `@:`-prefixed `SDCSUtils::get_baseHairColorLoc()` (IL=2)
which is `@:Entities/Player/Common/HairColorSwatches`.

---

## 4. Asset path grammar

All runtime loads go through `DataLoader::LoadAsset<T>` / `LoadManager::LoadAsset<T>`
with the `@:` bundle-relative prefix. Paths are rebuilt from
`SDCSUtils::tmpArchetype`, the static "archetype currently being built" — set once
at the top of each `CreateViz*` call.

### 4.1 Fixed roots

| Property | IL | Value |
|---|---:|---|
| `SDCSUtils::get_baseRigPrefab()` | 2 | `@:Entities/Player/Common/BaseRigs/baseRigPrefab.prefab` |
| `SDCSUtils::get_baseRigFPPrefab()` | 2 | `@:Entities/Player/Common/BaseRigs/baseRigFPPrefab.prefab` |
| `SDCSUtils::get_FPAnimController()` | 4 | `@:Entities/Player/Common/AnimControllers/FPPlayerController.controller` |
| `SDCSUtils::get_TPAnimController()` | 14 | `@:Entities/Player/Common/AnimControllers/3PPlayer{Sex}Controller` + `.controller` (male) / `.overrideController` (female) |
| `SDCSUtils::get_UIAnimController()` | 14 | `@:Entities/Player/Common/AnimControllers/MenuSDCS{Sex}Controller` + same male/female suffix rule |
| `SDCSUtils::get_baseHairColorLoc()` | 2 | `@:Entities/Player/Common/HairColorSwatches` |
| `SDCSUtils::get_baseEyeColorMatLoc()` | 6 | `@:Entities/Player/Common/Eyes/Materials/{EyeColorName}.mat` |

The female controllers being `.overrideController` and the male ones plain
`.controller` is a hard branch on `Archetype::IsMale`, not a filename probe.

### 4.2 Base body/head meshes and materials

With `S = Sex` (`Male`/`Female`), `R = Race`, `V = Variant.ToString("00")`:

| Property | IL | Path |
|---|---:|---|
| `SDCSUtils::get_baseBodyLoc()` | 26 | `@:Entities/Player/{S}/Common/Meshes/player{S}.fbx` |
| `SDCSUtils::get_baseHeadLoc()` | 58 | `@:Entities/Player/{S}/Heads/{R}/{V}/Meshes/player{S}{R}{V}.fbx` |
| `SDCSUtils::get_baseBodyMatLoc()` | 58 | `@:Entities/Player/{S}/Heads/{R}/{V}/Materials/player{S}{R}{V}_Body.mat` |
| `SDCSUtils::get_baseHeadMatLoc()` | 58 | `.../player{S}{R}{V}_Head.mat` |
| `SDCSUtils::get_baseHandsMatLoc()` | 58 | `.../player{S}{R}{V}_Hand.mat` |

`SDCSUtils::BasePartsExist(Archetype)` (IL=48) is the preflight: body mesh, head
mesh, body material, head material. Each miss logs
`"base body not found at <path>"` (etc.) and returns false. `EModelSDCS::SetRace`
(IL=15), `SetSex` (IL=15) and `SetVariant` (IL=16) all gate the rebuild on it, so
an incomplete race/variant is a no-op rather than a broken model.

### 4.3 Hair and facial hair roots

| Property | IL | Path |
|---|---:|---|
| `SDCSUtils::get_baseHairLoc()` | 38 | `@:Entities/Player/{S}/Hair/{Hair}/HairMorphMatrix/{R}{V}` |
| `SDCSUtils::get_baseMustacheLoc()` | 38 | `@:Entities/Player/{S}/FacialHair/Mustache/{MustacheName}/HairMorphMatrix/{R}{V}` |
| `SDCSUtils::get_baseChopsLoc()` | 38 | `@:Entities/Player/{S}/FacialHair/Chops/{ChopsName}/HairMorphMatrix/{R}{V}` |
| `SDCSUtils::get_baseBeardLoc()` | 38 | `@:Entities/Player/{S}/FacialHair/Beard/{BeardName}/HairMorphMatrix/{R}{V}` |

The `HairMorphMatrix/{Race}{Variant}` level is why every hair style must be
authored **per race/variant head shape** — the loaded asset is a `MeshMorph`
pre-fitted to that skull, not a generic mesh.

### 4.4 The substitution markers

`SDCSUtils` declares four literal marker constants (`.field public static literal`):

| Constant | Value | Replaced with |
|---|---|---|
| `SEX_MARKER` | `{sex}` | `Archetype::get_Sex()` — `Male` / `Female` |
| `RACE_MARKER` | `{race}` | `Archetype::Race` |
| `VARIANT_MARKER` | `{variant}` | `Archetype::Variant.ToString("00")` |
| `HAIR_MARKER` | `{hair}` | `Bald` or `""` (see below) |

`SDCSUtils::GetPathForSlotData(SlotData,Boolean)` (IL=123) is the resolver:

1. null `SlotData`, or empty `PartName` → null.
2. If `PartName` equals `"head"` (ordinal-ignore-case):
   - if the static `ignoredParts` array contains `"head"` → null (FP suppression, §5.3);
   - else substitute `{sex}`, `{race}`, `{variant}`, then `{hair}`;
   - `{hair}` → `"Bald"` when the second argument (`_headgearShortHairMask`) is true **and**
     (`Archetype::Hair` is empty **or** the hair name is in `shortHairNames`);
     otherwise `{hair}` → `""`.
3. Otherwise: empty `PrefabName` → null; if `PartName` *contains* any entry of
   `ignoredParts` (ordinal-ignore-case) → null; else only `{sex}` is substituted
   (via `SDCSUtils::parseSexedLocation(String,String)`, IL=5).

So **`{race}`, `{variant}` and `{hair}` are only honoured on the `head` part.**
A body/torso/gloves/boots prefab path may use `{sex}` and nothing else.

`shortHairNames` (from `SDCSUtils::.cctor`, IL=93) is exactly:
`buzzcut`, `cornrows`, `flattop_fro`, `mohawk`, `small_fro`. These five are the
styles that survive under a hat; anything else forces the `Bald` head variant when
a headgear morph asks for the short-hair mask.

### 4.5 Headgear morph paths

`Morphable::MorphHeadgear(Archetype,Boolean)` (IL=111) loads
`{MorphSetPath}/{Race}{Variant:00}/{MorphName}.asset` as a `MeshMorph` — the
per-skull fitted version of a helmet mesh. `MorphSetPath` and `MorphName` are
serialised on the `Morphable` component inside the gear prefab, so they are set in
the Unity project, not in XML.

---

## 5. The build pipeline

### 5.1 Entry points

`EModelSDCS::GenerateMeshes()` (IL=34) is the single rebuild entry:

```text
EModelSDCS::GenerateMeshes
  SDCSUtils::CreateVizTP(archetype, ref baseRig,   ref boneCatalog,   playerEntity, IsFPV)
  if (playerEntity is EntityPlayerLocal)
      SDCSUtils::CreateVizFP(archetype, ref baseRigFP, ref boneCatalogFP, playerEntity, IsFPV)
  EModelBase::ClothSimInit()
  return baseRig.transform
```

It is called from `EModelSDCS::createModel` (IL=80), `SwitchModelAndView` (IL=23)
and `UpdateEquipment` (IL=17). `UpdateEquipment` is driven by the XUi event
`XUiM_PlayerEquipment::HandleRefreshEquipment`, subscribed in `EModelSDCS::Init`
(IL=58) and unsubscribed in `OnDestroy` (IL=5) — **equipping armor rebuilds the
entire rig**, it is not an incremental swap. `EModelSDCS::Init` also takes the
archetype from `PlayerProfile::CreateTempArchetype()`.

`SDCSUtils::CreateVizTP` (IL=57) — third person:

```text
RemoveAssetOwnerForRig(baseRig); DestroyViz(baseRig, keepRig: true)
tmpArchetype = _archetype
setupRig(ref baseRig, ref boneCatalog, baseRigPrefab, parent: null, TPAnimController)
tmpAssetsOwner = GetAssetOwnerForRig(baseRig)
if (!isFPV) {
    setupBase(baseRig, boneCatalog, baseParts, isFPV)
    setupEquipment(baseRig, boneCatalog, ignoredParts, entity, isUI: false,
                   ignoreDlcEntitlements: !(entity is EntityPlayerLocal), useTempCosmetics: false)
    setupHairObjects(baseRig, boneCatalog, ignoredParts, entity, isUI: false)
}
oldOwner?.ReleaseAssets()
```

`SDCSUtils::CreateVizFP` (IL=171) — first person — differs: it parents the rig
under `Camera/UFPSRoot` (erroring out with `"Unable to find first person camera!"`
if neither the entity's `Camera` child nor a global `GameObject.Find("Camera")`
resolves), uses `baseRigFPPrefab` + `FPAnimController`, uses `basePartsFP` and
`ignoredPartsFP`, renames the object to `baseRigFP`, adds an `AnimationEventBridge`,
sets every child `SkinnedMeshRenderer`'s layer to `HoldingItem`, disables any
`HingeJoint` with no connected body, and disables all `Cloth`.

`SDCSUtils::CreateVizUI` has two overloads for the character-menu preview: the
3-argument form (IL=112) drives the archetype's own `SlotData` list through the
entity-less `setupEquipment(GameObject,TransformCatalog,String[],Boolean,List,Boolean)`
(IL=158) overload, and the 5-argument form (IL=103) takes an `EntityAlive`. Both use
`baseRigPrefab` + `UIAnimController` with `isUI: true`, then:

- find the `IKRig` child and set its `Rig::weight = 0` — the UI preview runs with IK
  **off**, it does not "keep" that layer;
- disable (`SetActive(false)`) every `HingeJoint` whose `connectedBody` is null,
  warning
  `"SDCSUtils::CreateVizUI: No connected body for <x>'s HingeJoint! Disabling for UI until this is solved."`
  once per joint;
- finish with `fixCloths` (IL=37), which disables every `Cloth` GameObject and
  re-enables them a frame later via a `ThreadManager` coroutine.

### 5.2 The four static part arrays

From `SDCSUtils::.cctor` (IL=93):

| Array | Contents | Used by |
|---|---|---|
| `baseParts` | `head`, `body`, `hands`, `feet` | TP + UI `setupBase` |
| `basePartsFP` | `body`, `hands` | FP `setupBase` |
| `ignoredParts` | *(empty)* | TP + UI `setupEquipment` / `setupHairObjects` |
| `ignoredPartsFP` | `head`, `helmet`, `feet`, `boots` | FP |

`ignoredPartsFP` is why a helmet is invisible in first person: `GetPathForSlotData`
returns null for any `PartName` containing `head`, `helmet`, `feet` or `boots`
while the FP rig is being built.

The cctor also allocates the reusable scratch buffers `_smrBuf` (capacity 64),
`_hingeBuf` (32), `_bcBuf` (32) and the `tempCloths`/`tempMats`/`tempSMRs` lists —
SDCS assembles into shared static buffers, so it is not re-entrant.

### 5.3 `setupRig`

`SDCSUtils::setupRig(ref GameObject, ref TransformCatalog, String, Transform, RuntimeAnimatorController)`
(IL=80):

- If the rig object does not exist yet: `DataLoader::LoadAsset<GameObject>(prefabLocation)`
  → `Instantiate(parent)`, build a fresh `TransformCatalog`, and disable every
  `BoneRenderer` in the hierarchy.
- If it does exist: `cleanupEquipment` instead (§8) — the rig is reused.
- Set the `Animator`'s `runtimeAnimatorController` if it differs.
- **Female-only:** `GetOrAddComponent<CapsuleCollider>` on the `Hips` bone with
  `center = (0, 0, -0.03)`, `radius = 0.15`, `height = 0.375`. (This is the cloth
  collider for the female body; male rigs get none here.)

`SDCSUtils/TransformCatalog` is a `Dictionary<string, Transform>` built by
`AddRecursive` (IL=40) over the whole rig — **keyed by transform name only**, with
later duplicates overwriting earlier ones. Two bones with the same name anywhere in
the rig collapse to one entry. This dictionary is the sole bone-resolution
mechanism for the rest of the pipeline.

### 5.4 `setupBase`

`SDCSUtils::setupBase(GameObject,TransformCatalog,String[],Boolean)` (IL=219), per
part name in `baseParts`/`basePartsFP`:

- `head` → `baseHeadLoc`; `hands` **and** `body` → `baseBodyLoc` (hands are a child
  of the body FBX, not a separate asset); `feet` also falls through to `baseBodyLoc`.
- `getBodyPartContainingName(Transform,String)` (IL=35) finds the child whose
  lowercased name *contains* the part name, renames it to the part name, and
  `Stitch`es it with the eye material (`baseEyeColorMatLoc`) and `isGear: false`.
- When the part is `head`, it additionally wires two face controllers onto the
  rig's `Head` bone, resolved through the bone catalog:
  - `CharacterGazeController`: `rootTransform`=`Origin`, `neckTransform`=`Neck`,
    `headTransform`=`Head`, `leftEyeTransform`=`LeftEye`, `rightEyeTransform`=`RightEye`,
    `eyeSkinnedMeshRenderer` = the SMR on the `eyes` transform, plus tuned constants
    `eyeLookAtTargetAngle=35`, `eyeRotationSpeed=30`, `twitchSpeed=25`,
    `headLookAtTargetAngle=75`, `headRotationSpeed=7`, `maxLookAtDistance=5`.
  - `EyeLidController`: `LeftEyelidTop`, `LeftEyelidBot`, `RightEyelidTop`,
    `RightEyelidBot` transforms, each with its rest local position and rotation
    captured from the **source FBX**, not the rig.

Those eight bone names (`Origin`, `Neck`, `Head`, `LeftEye`, `RightEye`,
`LeftEyelidTop/Bot`, `RightEyelidTop/Bot`) plus `eyes` are indexed with
`Dictionary::get_Item`, so a head mesh missing any of them throws
`KeyNotFoundException` during assembly rather than degrading.

### 5.5 `setupEquipment` — equipment slots to `SlotData` list

`SDCSUtils::setupEquipment(GameObject,TransformCatalog,String[],EntityAlive,Boolean,Boolean,Boolean)`
(IL=289). Phase one, per equipment slot `i` in `0..Equipment::GetSlotCount()`:

```text
worn     = entity.equipment.GetSlotItem(i)                     // ItemValue
cosmetic = entity.equipment.GetCosmeticSlot(i, useTempCosmetics) // ItemClass
hasWorn  = worn?.ItemClass?.SDCSData != null

useCosmetic =
      cosmetic == null                                  -> false
    : useTempCosmetics                                  -> true
    : !hasWorn                                          -> false
    : _ignoreDlcEntitlements                            -> true
    : entity.equipment.HasCosmeticUnlocked(cosmetic).Item1
```

If neither `hasWorn` nor `useCosmetic`, or the **cosmetic** class is
`ItemClass::MissingItem`, the slot is skipped. If a cosmetic exists but
`useCosmetic` came out false (the usual cause: the entitlement is not unlocked),
the slot's cosmetic is cleared (`SetCosmeticSlot(i, 0)`) and
`EntityAlive::bPlayerStatsChanged` is set — i.e. the model rebuild is also where a
revoked entitlement gets scrubbed from the save.

The chosen `ItemClass`'s `SDCSData` is appended to `tmpArchetype.Equipment` (which
is cleared first). Additionally, if the class is an `ItemClassArmor` whose
`EquipSlot == EquipmentSlots.Head` (0), that piece's `HairMaskType` and
`FacialHairMaskType` are copied onto `EModelSDCS::HairMaskType` /
`FacialHairMaskType`. **Only head-slot armor can mask hair** — the fields are read
off any part's `SlotData` but only committed for `EquipSlot == Head`.

Phase two, per collected `SlotData`:

- `PartName == "head"` **and** `PrefabName` contains `HeadGearMorphMatrix`
  (ordinal-ignore-case) → `setupHeadgearMorph` (IL=139).
- `PartName == "head"` and (`IsFPV` and not `isUI`) → skipped entirely.
- otherwise → `setupEquipmentSlot`, then `Stitch(..., isGear: true)`; if the
  stitched object has a `Morphable` in children, `MorphHeadgear(tmpArchetype, ...)`.
- Either way, a `ColorSwatchApplicator` found in the stitched children gets
  `ApplyColorSwatch(tmpArchetype.HairColor)` — this is how hair-colour-matched
  gear (wigs, hair sticking out of hats) works.

Before phase one it destroys every child of `Origin` whose name starts with
`RigConstraints` (`findStartsWith`, IL=32) — a full constraint teardown.

Finally `setupEquipmentCommon` (§7).

### 5.6 `setupEquipmentSlot` — one gear piece

`SDCSUtils::setupEquipmentSlot(GameObject,TransformCatalog,String[],SlotData,List<Transform>,Boolean)`
(IL=196):

1. `GetPathForSlotData(wornItem, _headgearShortHairMask: true)`; null/empty → return null.
2. `LoadManager::LoadAsset<GameObject>(path, ...)`. **Fallback:** if the asset is
   null *and* `PartName == "head"`, retry once with `_headgearShortHairMask: false`
   — i.e. try the non-`Bald` head. Still null → `Log::Warning`
   `"SDCSUtils::<path> not found for item <PrefabName>!"` and return null.
3. Register the asset handle on `tmpAssetsOwner` (`AssetRefs::AddAssetHandle`) and
   `Release()` the request task — the rig now owns the reference (§8).
4. Find the *body* gear path: scan `tmpArchetype.Equipment` for the entry whose
   `PartName == "body"` and resolve its path (mask off). This becomes
   `targetBodyPath` for variant selection.
5. `getPartNameWithVariant(PartName, sourceGearPath, targetBodyPath)` (IL=34) →
   `getClothingPartWithName(prefab, name)` (IL=35, case-insensitive **exact** match
   over direct children only, not recursive).
6. `CollectRequiredNamesForSlot(prefab.transform, slotSubRoot)` → the allowed-bone
   set; cached under the slot transform via `SlotAllowedBonesCache::Set`.
7. Append the slot transform to `allGears`.
8. **`BaseToTurnOff`:** split on `,`, and for each token
   `Extensions::FindInChildren(rig.transform, token)` → `Object.Destroy(go)`. Note
   this destroys the found transform's GameObject anywhere in the rig, matched by
   name; it is applied to the *rig*, not the gear prefab.
9. `SetActive(true)` on the slot if inactive.
10. `MatchRigs(prefab.transform, rig.transform, catalog, allowedBones)`.

The returned `Transform` is the slot sub-root, which the caller then `Stitch`es.

### 5.7 `setupHairObjects` / `setupHair`

`SDCSUtils::setupHairObjects(GameObject,TransformCatalog,String[],EntityAlive,Boolean)`
(IL=44) is the thin entry: bails unless `isUI || !IsFPV`, clears
`EModelSDCS::ClipMaterialsFP` for the FP case, and forwards the archetype's four
hair names to the 10-argument overload (IL=241).

That overload:

- Loads the hair-colour swatch `{baseHairColorLoc}/{HairColor}.asset` as a
  `ScriptableObject`, casts to `HairColorSwatch`; a miss logs
  `"SDCSUtils::<path> not found for hair color <HairColor>!"` but is not fatal.
- For hair: when `_emodel` is null the plain no-suffix path is used; otherwise the
  piece is skipped when `EModelSDCS::HairMaskType == None`. The mask suffix is
  `""` for `Full`, `"_" + HairMaskType.ToString().ToLower()` otherwise (i.e.
  `_hat`). Asset path: `{baseHairLoc}/hair_{hairName}{suffix}.asset`.
- For mustache / chops / beard: skipped when `FacialHairMaskType == None`; paths
  `{baseMustacheLoc}/hair_facial_mustache{suffix}.asset`,
  `{baseChopsLoc}/hair_facial_sideburns{suffix}.asset`,
  `{baseBeardLoc}/hair_facial_beard{suffix}.asset`.
  Note the **filename does not carry the style name** — the style is already in the
  directory (`FacialHair/Beard/{BeardName}/...`), and `sideburns` is the on-disk
  name for what the XML calls `chops`.
- Finally `ApplySwatchToGameObject(rig, swatch)`.

`SDCSUtils::setupHair(...)` (IL=67) loads the path as a `MeshMorph`, calls
`MeshMorph::GetMorphedSkinnedMesh()`, warns `"SDCSUtils::<path> not found for hair
<name>!"` on failure, activates it, `Stitch`es it (`isGear: false`), and
`Object.Destroy`s the temporary morphed object.

`SDCSUtils::ApplySwatchToGameObject(GameObject,HairColorSwatch)` (IL=69) walks every
`Renderer` (including inactive) and applies the swatch to each material whose
**shader is named exactly `Game/SDCS/Hair`** and whose material name does not
contain `lashes`. A custom hair asset on any other shader silently keeps its
authored colours.

---

## 6. `Stitch` — the bone rebind

`SDCSUtils::Stitch(GameObject,GameObject,TransformCatalog,EModelSDCS,Boolean,Boolean,Material,Boolean)`
(IL=256). This is the core of the system.

```text
inst = Instantiate(sourceObj, parentObj.transform); inst.name = sourceObj.name
GetComponentsInChildren(tempSMRs); GetComponentsInChildren(tempCloths)
isBody = inst.name.StartsWith("body")

foreach (smr in tempSMRs) {
    smr.bones    = TranslateTransforms(smr.bones, boneCatalog)   // name -> rig transform
    smr.rootBone = Find(boneCatalog, smr.rootBone.name)
    smr.updateWhenOffscreen = true
    ... material handling ...
}
capsuleColliders of every Cloth = boneCatalog["Hips"].GetComponentsInChildren<CapsuleCollider>()
```

`SDCSUtils::TranslateTransforms(Transform[],TransformCatalog)` (IL=31) maps each
bone **by name** through the catalog; a null entry in the source bone array logs
`"Null transform in bone list"` and is left alone. `SDCSUtils::Find<TKey,TValue>`
(IL=7) is a `TryGetValue`-or-default helper, so an **unmatched bone name becomes
`null`** — the mesh loads, the bone silently does nothing. This is the failure mode
to look for when a custom armor piece deforms wrongly.

Material handling per SMR:

1. **Tint transfer.** For each shared material that `HasColor("_Tint")`: if its
   name contains `_Body` / `_Head` / `_Hand`, load the corresponding
   `baseBodyMatLoc` / `baseHeadMatLoc` / `baseHandsMatLoc`, and if that also has
   `_Tint`, clone the gear material and copy the base `_Tint` colour into it. This
   is the skin-tone match: gear authored with a `_Tint` property inherits the
   wearer's race/variant skin colour automatically.
2. **Eyes.** If the renderer's GameObject is named exactly `eyes` and an
   `eyeMat` was passed, `sharedMaterials[0] = eyeMat`.
3. Every material is then cloned (`new Material(m)`) and reassigned — SDCS never
   shares material instances between characters.
4. **FP clipping.** When `isBody && isGear && emodel != null && !isUI && isFPV`:
   every material with a `_ClipFPV` float gets it set to `1`, its submesh index is
   collected, and `RemoveFPViewObstructingGearPolygons(smr, indices)` (IL=226) runs.

`RemoveFPViewObstructingGearPolygons` instantiates a private copy of the shared
mesh and, per listed submesh, rebuilds the triangle list keeping only triangles
where **at least one** of the three vertices has vertex-colour `r != 0`. So the
FP-visible portion of body gear is authored as a **vertex-colour red-channel mask**
in the mesh itself. A mesh with no vertex colours (`mesh.colors` empty) is left
untouched.

---

## 7. The bone allowlist and rig constraints

Gear prefabs ship with their own copies of aux bones (cloth chains, jiggle bones,
constraint drivers) that the base rig does not have. SDCS grafts exactly the ones a
slot needs and no more.

`SDCSUtils::CollectRequiredNamesForSlot(Transform root,Transform slotSubRoot)` (IL=236):

1. **Primary source — `GearBoneMap`.** `root.GetComponent<GearBoneMap>()`, then
   `GetPartBones(slotSubRoot.name)`; every returned transform's name enters the set.
2. **Fallback.** No `GearBoneMap` → `Debug.LogWarning`
   `"[SDCSUtils] No GearBoneMap found on root <name>, falling back to collecting all
   bones from SMRs under <slot>."` and every bone of every SMR under the slot is
   taken instead. This works but grafts far more bones than needed.
3. `BuildAllowedWithAncestors` (IL=49) closes the set upward: for each allowed name,
   walk parents to the source origin adding every ancestor, so the graft is a
   connected subtree.
4. Add every `HingeJoint` transform under the slot **and** its `connectedBody`
   transform.
5. Add the `sourceObjectA` / `sourceObjectB` of every `BlendConstraint` under the
   root **whose `constrainedObject` is already in the set**.
6. Close ancestors again and return.

`GearBoneMap` (MonoBehaviour, fields `parts`, `DefaultParts`) is a **baked** asset,
authored in the Unity project:

| Member | IL | Behaviour |
|---|---:|---|
| `GearBoneMap::.cctor()` | 20 | `DefaultParts = { head, body, feet, hands }` |
| `GearBoneMap::Bake()` | 208 | For each child transform whose name up to the first `_` is in `DefaultParts` and whose parent is this transform, read every SMR's bone weights (`GetBonesPerVertex` + `GetAllBoneWeights`) and collect every bone with `weight > 0`, plus `rootBone`; then `SetBones(child.name, ...)` |
| `GearBoneMap::GetPartBones(String)` | 62 | exact match first; on miss, retry with the name truncated at the first `_` |
| `GearBoneMap::SetBones(String,IEnumerable<Transform>)` | 71 | filters nulls, `Distinct`, orders by name then by hierarchy path |
| `GearBoneMap::GetHierarchyPath(Transform)` | 26 | `/`-joined transform path, used as the secondary sort key |
| `GearBoneMap::GetPartNames()` | 14 | the baked part names |
| `GearBoneMap::ClearAll()` | 4 | drop the bake |

The `_`-truncation in both `Bake` and `GetPartBones` is what lets a gear part be
named `body_02` while its bone map is keyed `body` — the same convention
`getPartNameWithVariant` produces (§9).

Grafting is `MatchRigs` → `AddRequiredChildren`:

`SDCSUtils::MatchRigs(Transform,Transform,TransformCatalog,HashSet<String>)` (IL=37)
resolves `Origin` on both sides, picks up the `AuxBoneTracker` from the catalog's
`Origin`, and recurses.

`SDCSUtils::AddRequiredChildren(Transform,Transform,TransformCatalog,HashSet<String>,AuxBoneTracker)`
(IL=124), per source child whose name is in `allowedBones`:

- Find a target child with the same name. If none: `Instantiate` the source child
  under the target (`worldPositionStays: false`), restore its name, local position,
  local rotation and local scale.
- Record it in `AuxBoneTracker::AuxBoneLookup` (name → transform) if new.
- Register it in the `TransformCatalog` if new.
- `TransferCharacterJoint(source, newBone, catalog)` (IL=31): if the source has a
  `CharacterJoint`, add one to the new bone and re-point its `connectedBody` through
  the catalog.
- Recurse into that child.

`SDCSUtils::setupEquipmentCommon(GameObject,TransformCatalog,List<Transform>)` (IL=91)
then finishes the rig, once, after all slots:

1. `GetOrAddComponent<RigBuilder>` and **disable** it.
2. Per gear slot, look up its cached allowed-bone set; an empty/absent set logs
   `"[SDCS] No required leaves cached for slot '<name>'. Skipping constraints."`
   Otherwise `SetupRigConstraints`.
3. Rewire every `HingeJoint` in the rig: re-resolve `connectedBody` through the bone
   catalog by name, and force `autoConfigureConnectedAnchor = true`.
4. Re-enable the `RigBuilder`.

`SDCSUtils::SetupRigConstraints(RigBuilder,Transform,Transform,TransformCatalog,HashSet<String>)`
(IL=173): finds `RigConstraints` under the source's parent, creates (or reuses) a
`RigConstraints_<slotName>` GameObject under the target root, `GetOrAddComponent<Rig>`,
registers a `RigLayer` on the builder, then clones every `BlendConstraint` whose
`constrainedObject` name is in `allowedBones`, re-pointing `constrainedObject`,
`sourceObjectA` and `sourceObjectB` through the bone catalog.

---

## 8. Teardown and asset ownership

SDCS reference-counts loaded assets per rig instance:

| Member | IL | Behaviour |
|---|---:|---|
| `SDCSUtils::GetAssetOwnerForRig(GameObject)` | 16 | `rigOwnedAssets[rig.GetInstanceID()]`, creating an `AssetRefs` on miss |
| `SDCSUtils::RemoveAssetOwnerForRig(GameObject)` | 16 | remove and return it (null-safe) |
| `SDCSUtils::UnloadViz(GameObject)` | 12 | remove owner, `DestroyViz(keepRig: false)`, `ReleaseAssets()` |

`SDCSUtils/AssetRefs` holds `List<LoadManager/IAssetHandle> trackedAssetHandles`.
The `CreateViz*` order matters: the **old** owner is detached *before* the rebuild
and released *after*, so assets shared between the old and new outfit are never
unloaded and immediately reloaded.

`SDCSUtils::DestroyViz(GameObject,Boolean)` (IL=69): for every child of the rig
**except `Origin`**, walk its SMRs; destroy any `sharedMesh` that
`MeshMorph::IsInstance` reports as a runtime instance, and run
`Utils::CleanupMaterials` over the shared materials. With `_keepRig: false` the rig
object itself is `DestroyImmediate`d.

`SDCSUtils::cleanupEquipment(GameObject,TransformCatalog)` (IL=57) — the reuse path:
clear `SlotAllowedBonesCache`, strip every `RigLayer` except `IKRig` from the
`RigBuilder`, `RigBuilder::Clear()`, `AnimatorJobExtensions::UnbindAllStreamHandles`,
`GameUtils::DestroyAllChildrenImmediatelyBut(rig, { "Origin", "IKRig" })`, then
`SanitizeRig`.

`SDCSUtils::SanitizeRig(GameObject,TransformCatalog)` (IL=103) destroys every bone
recorded in `AuxBoneTracker::AuxBoneLookup` (the previous outfit's grafted bones),
removes them from the catalog, clears the tracker, and finally prunes every catalog
entry whose `Transform` is now a destroyed Unity object.

`SDCSUtils::SetVisible(GameObject,Boolean)` (IL=48) toggles `SetActive` on every SMR
GameObject under every non-`Origin` child — used by `EModelSDCS::SetVisible` (IL=15).

---

## 9. Gear variants: `GearVariantMatrixSO`

A gear mesh often needs a different cut depending on which *body* mesh it sits over
(e.g. a jacket over a bulky torso vs a bare one). That mapping is a serialised
matrix, not code.

`GearVariants.GearVariantMatrixSO::get_Instance()` (IL=13) loads
`@:Entities/Player/Common/GearVariantMatrix.asset` (calling `LoadManager::InitSync()`
first when not playing).

Structure:

```text
GearVariantMatrixSO
  male, female : SexGearTables
      gearPaths  : List<string>     // both the row and the column key space
      gearGuids  : List<string>
      head, hands, feet : StringTable2D
          rowKeys, columnKeys : List<string>
          rows : List<Row>          // Row { rowKey, rowGuid, cellValues : List<string> }
```

`SDCSUtils::getPartNameWithVariant(String partName,String sourceGearPath,String targetBodyPath)`
(IL=34) asks for the cell, and returns `partName` unchanged when the lookup is
empty; otherwise it returns **`partName + "_" + variant`**. That is the string
handed to `getClothingPartWithName`, so the gear prefab must contain a child named
`<part>_<variant>` for every variant the matrix can produce. A missing
`GearVariantMatrixSO` logs
`"SDCSUtils::getPartNameWithVariant: No GearVariantMatrixSO instance found!"` and
falls back to the plain part name.

| Member | IL | Behaviour |
|---|---:|---|
| `GearVariantMatrixSO::TryParseSex(String,Sex&)` | 27 | lowercased `male`/`female`; `Sex` is `Male=0, Female=1` |
| `GearVariantMatrixSO::TryParsePart(String,GearPart&)` | 69 | `head`/`hands`/`feet`, exact then trimmed-lowercase; `GearPart` is `Head=0, Hands=1, Feet=2` |
| `GearVariantMatrixSO::EnsureIndex(Sex)` | 95 | build/refresh `gearPaths[i] -> i` (ordinal), invalidated by row-count change |
| `GearVariantMatrixSO::TryGetIndices(Sex,String,String,Int32&,Int32&)` | 43 | both row and column resolve through the **same** `gearPaths` index |
| `GearVariantMatrixSO::GetTable(Sex,GearPart)` | 11 | `SexGearTables::GetTable(GearPart)` (IL=15) — switch, defaulting to `hands` |
| `GearVariantMatrixSO::GetVariantOrEmpty(Sex,GearPart,String,String)` | 61 | bounds-checked cell fetch, `""` on any miss |
| `GearVariantMatrixSO::GetVariantOrEmpty(String,String,String,String)` | 19 | string-keyed wrapper used by `SDCSUtils` |
| `GearVariantMatrixSO::TryGetVariant(Sex,GearPart,String,String,String&)` | 64 | bool-returning form |
| `StringTable2D::Get(Int32,Int32)` | 8 | `rows[row].cellValues[col]` |

Note the part space here is only `head`/`hands`/`feet` — there is no `body` table,
because the body *is* the column key.

---

## 10. Animator binding: `AvatarSDCSController`

`AvatarSDCSController::assignParts(Boolean _bFPV)` (IL=167) resolves the named bones
the animation layer needs off the assembled rig:

- Third person: `Hips` (recursive find) → `Spine` → `Spine1` → `Spine2` → `Spine3`
  → `Neck/Head` → `CameraNode` (all `Transform::Find`, i.e. exact child paths), plus
  `RightWeapon` (recursive) as `rightHand`.
- First person: `bNewModel = FindInChilds(bipedTransform,"Origin") != null`. On a new
  (SDCS) model, only `rightHand` is resolved and every spine/head/cameraNode field is
  **nulled**; on a legacy model the full chain is resolved, with `cameraNode`
  overwritten by `spine3`.
- `meshTransform` = recursive `body`, falling back to `TraderBob`.

So the FP SDCS rig deliberately runs with no spine chain bound — FP animation comes
entirely from `FPPlayerController`.

`AvatarSDCSController::SwitchModelAndView(String,Boolean,Boolean)` (IL=148) swaps the
active biped between `modelTransform` and its `baseRigFP` child, re-runs
`assignParts`, sets the `IsMale` animator bool when `HasParameter("IsMale")`
(IL=27), re-parents `rightHandItemTransform` under `rightHand` and applies the
`AnimationGunjointOffsetData` offset for the held item's `HoldType`.

`AvatarSDCSController::assignStates()` (IL=30) hashes `Base Layer.Jump` and
`Base Layer.FPVFemaleJump` and fills the death/reload/hit state sets from
`AvatarCharacterController`. Per-frame work is `LateUpdate` (IL=271) and
`setLayerWeights` (IL=88); see [`entity-ai.md`](entity-ai.md) §animator anatomy for
the cost framing.

`EModelSDCS::LateUpdate()` (IL=32) pushes `_ClipCenter` (the FP head world position)
into every material in `ClipMaterialsFP` each frame — the runtime half of the
`_ClipFPV` mechanism from §6.

---

## 11. The editor-side catalog: `CharacterConfigurator/SDCSGearXmlCatalog`

A separate reader over the *same* `items.xml` data, used by the character
configurator tooling rather than by item load. It matters here because it documents
the intended **naming conventions** more explicitly than `ItemClass::Init` does.

`SDCSGearXmlCatalog::BuildFromXml(String)` (IL=124): for every `<item>` descendant,
take the first child `<property>` whose `class` attribute equals `SDCS`
(case-insensitive), then:

| Entry field | Source |
|---|---|
| `ItemName` | `<item name="...">` |
| `PrefabName` | `SDCS` block, `Prefab` (required — item skipped when empty) |
| `PartName` | `NormalizePart(SDCS/TransformName, item/EquipSlot)` (required) |
| `EquipSlot` | item-level `EquipSlot` property |
| `GearKey` | `NormalizeGearKey(item/ArmorGroup, item/DisplayType, item name)` (required) |
| `BaseToTurnOff` | `NormalizeBaseToTurnOff(SDCS/Excludes, PartName)` |
| `HairMaskType`, `FacialHairMaskType` | `SDCS` block, trimmed or null |

Note `EquipSlot`, `ArmorGroup` and `DisplayType` are read from the **item** element,
while `Prefab`/`TransformName`/`Excludes`/`*MaskType` come from the nested `SDCS`
block.

| Normalizer | IL | Rule |
|---|---:|---|
| `NormalizePart(String,String)` | 65 | `TransformName` lowercased must be one of `head`/`body`/`hands`/`feet`; else fall back to `EquipSlot` lowercased mapped `head→head`, `chest→body`, `hands→hands`, `feet→feet`; else null |
| `NormalizeGearKey(String,String,String)` | 30 | non-empty `ArmorGroup` → `Trim()` then strip a leading `group`, returned as-is. Otherwise take `DisplayType` (or the item name when `DisplayType` is empty) and strip a leading `armor` plus one trailing `Helmet`/`Outfit`/`Gloves`/`Boots`, then `NormalizeOptional` |
| `NormalizeBaseToTurnOff(String,String)` | 60 | split `Excludes` on `,`; prefer the token normalising to `preferredPart`, else the first token that normalises to a legal part name |
| `NormalizePartName(String)` | 31 | lowercase and accept only `head`/`body`/`hands`/`feet` |
| `NormalizeOptional(String)` | 10 | null for null/whitespace, else `Trim()` |
| `StripPrefix` / `StripSuffix` | 15 / 19 | ordinal-ignore-case |

`Add(Entry)` (IL=42) groups entries into `GearSet { Key, Parts }` keyed
case-insensitively, preserving first-seen key order in `orderedKeys`;
`TryGetPart(String,String,Entry&)` (IL=23) is the lookup.

The naming rules encoded here — the four canonical part names, the
`group`/`armor` prefix and `Helmet|Outfit|Gloves|Boots` suffix conventions on
`ArmorGroup`/`DisplayType` — are the de-facto authoring style for stock armor.

---

## 12. Console: `sdcs`

`ConsoleCmdSDCS` (`getCommands()` IL=7 → `sdcs`; `getDescription()` IL=2 →
"Control entity sex, race, and variant"). `Execute` (IL=166) operates on
`GetLocalPlayers()[0]`'s `EModelSDCS`, so it is **local-client only** — on a
dedicated server there are no local players and it prints `"No local players found"`.

```text
sdcs                            show current sex / race / variant
sdcs sex <male|female>          EModelSDCS::SetSex
sdcs race <white|black|asian|native>   EModelSDCS::SetRace
sdcs variant <1|2|3|4>          EModelSDCS::SetVariant (rejected outside 1..4)
```

The three argument enums are hardcoded: `cTypes { Sex, Race, Variant }`,
`sTypes { Male, Female }`, `rTypes { White, Black, Asian, Native }`. Adding a race
via `sdcs.xml` and asset folders does **not** extend this command — the console
parse is a closed enum even though `SetRace` takes an arbitrary string. The variant
bound `1..4` is likewise a literal range check, not derived from `SDCSDataUtils`.

---

## 13. Authoring checklist: a new skinned armor piece

1. **Model + skin** the mesh to the stock skeleton. Bone *names* must match the base
   rig exactly; unmatched names become `null` bones in `TranslateTransforms` with no
   error (§6).
2. **Prefab layout:** one root, one child per part named exactly `head`, `body`,
   `hands`, `feet` (or `<part>_<variant>` when the piece participates in the gear
   variant matrix, §9). `getClothingPartWithName` matches direct children only,
   case-insensitively, exactly.
3. **`GearBoneMap`** on the prefab root, baked (`Bake()`), or accept the
   all-SMR-bones fallback and its warning.
4. **Materials:** give any skin-adjacent material a `_Tint` colour property to
   inherit the wearer's skin tone; name it with `_Body` / `_Head` / `_Hand` so the
   right base material is consulted (§6). Hair-coloured parts need the
   `Game/SDCS/Hair` shader and a `ColorSwatchApplicator`.
5. **First-person body gear:** paint the vertex-colour **red channel** non-zero on
   the triangles that should survive in FP, and give the material a `_ClipFPV` float.
6. **Headgear:** if it needs per-skull fitting, add a `Morphable` with `MorphSetPath`
   / `MorphName` and ship `{MorphSetPath}/{Race}{VV}/{MorphName}.asset` per
   race/variant; put `HeadGearMorphMatrix` in the prefab path so `setupEquipment`
   takes the morph branch.
7. **`items.xml`:**

```xml
<property class="SDCS">
    <property name="Prefab" value="@:Entities/Player/{sex}/Gear/.../piece_{sex}.prefab"/>
    <property name="TransformName" value="body"/>
    <property name="Excludes" value="body"/>
</property>
```

   Remember: `{race}`, `{variant}` and `{hair}` only substitute on the `head` part
   (§4.4); everything else gets `{sex}` only.
8. **Hair masking** only takes effect for `ItemClassArmor` with
   `EquipSlot == Head`; supply a `_hat` hair asset variant for every hair style, or
   accept the `Bald` fallback for styles outside `shortHairNames`.
9. **Restart, don't reload.** `archetypes.xml` has no reload delegate and no cleanup
   delegate in `xmlsToLoad`; equipment changes rebuild the rig, but archetype and
   item data are boot-time.

---

## 14. IL evidence index

| Method | IL |
|---|---:|
| `SDCSUtils::.cctor()` | 93 |
| `SDCSUtils::GetPathForSlotData(SlotData,Boolean)` | 123 |
| `SDCSUtils::CreateVizTP(Archetype,GameObject&,TransformCatalog&,EntityAlive,Boolean)` | 57 |
| `SDCSUtils::CreateVizFP(Archetype,GameObject&,TransformCatalog&,EntityAlive,Boolean)` | 171 |
| `SDCSUtils::setupRig(GameObject&,TransformCatalog&,String,Transform,RuntimeAnimatorController)` | 80 |
| `SDCSUtils::setupBase(GameObject,TransformCatalog,String[],Boolean)` | 219 |
| `SDCSUtils::setupEquipment(GameObject,TransformCatalog,String[],EntityAlive,Boolean,Boolean,Boolean)` | 289 |
| `SDCSUtils::setupEquipmentSlot(GameObject,TransformCatalog,String[],SlotData,List,Boolean)` | 196 |
| `SDCSUtils::setupEquipmentCommon(GameObject,TransformCatalog,List)` | 91 |
| `SDCSUtils::setupHairObjects(GameObject,TransformCatalog,EModelSDCS,Boolean,String[],Boolean,String,String,String,String)` | 241 |
| `SDCSUtils::setupHeadgearMorph(GameObject,TransformCatalog,EModelSDCS,Boolean,Boolean,SlotData,Boolean)` | 139 |
| `SDCSUtils::Stitch(GameObject,GameObject,TransformCatalog,EModelSDCS,Boolean,Boolean,Material,Boolean)` | 256 |
| `SDCSUtils::CollectRequiredNamesForSlot(Transform,Transform)` | 236 |
| `SDCSUtils::AddRequiredChildren(Transform,Transform,TransformCatalog,HashSet,AuxBoneTracker)` | 124 |
| `SDCSUtils::SetupRigConstraints(RigBuilder,Transform,Transform,TransformCatalog,HashSet)` | 173 |
| `SDCSUtils::RemoveFPViewObstructingGearPolygons(SkinnedMeshRenderer,Int32[])` | 226 |
| `SDCSUtils::SanitizeRig(GameObject,TransformCatalog)` | 103 |
| `SDCSUtils::DestroyViz(GameObject,Boolean)` | 69 |
| `SDCSDataUtils::Load()` | 260 |
| `SDCSDataUtils::Save()` | 249 |
| `SDCSArchetypesFromXml::parseArchetype(XElement)` | 221 |
| `SDCSArchetypesFromXml::parseEquipment(XElement)` | 57 |
| `SDCSArchetypesFromXml::Save(String,List)` | 69 |
| `SDCSGearXmlCatalog::BuildFromXml(String)` | 124 |
| `GearBoneMap::Bake()` | 208 |
| `GearVariantMatrixSO::EnsureIndex(Sex)` | 95 |
| `EModelSDCS::GenerateMeshes()` | 34 |
| `AvatarSDCSController::assignParts(Boolean)` | 167 |
| `ConsoleCmdSDCS::Execute(List,CommandSenderInfo)` | 166 |

---

## Changelog

- **2026-08-24:** First edition. Closes the last SDCS gap: `SDCSUtils`,
  `SDCSDataUtils` and `SDCSArchetypesFromXml` were catalogued but not researched in
  [`out-of-scope-surface.md`](out-of-scope-surface.md) / [`client-side-surface.md`](client-side-surface.md);
  they are now narrated. Derived from a full IL dump of the SDCS type family against
  the V3.1.0 (b14) dedicated `Assembly-CSharp.dll`.
