# Live wire capture (2026-08-11) - join handshake evidence

Raw `RECV`/`STAGE` lines from a loadgen bot joining a **stock V3.1.0 (b14)
dedicated server** (Navezgane; port 26902 listener, ServerPort 26900), captured
with the client's hex-log window widened (temp patch, reverted after).

## Channel framing (verified byte-for-byte)

`00 BC 12 00 00  00 00  01 00  B8 12 00 00  00 00  01 03 00 00 00  0A 00 00 00  0E 00 00 00  BD 00 00 00  14 ...`
- `ch=0` (channel), `size=0x12BC=4796` (LE), `comp=0`, `enc=0`, `cnt=1`
- package framing: `content=0x12B8=4792` (LE u32) + `pkgId=0` (u16) = `NetPackagePackageIds`
- body: `VersionInformation` u8=1 + i32 major=3 + minor=10 + build=14 -> "V 3.1.0 (1.3.10.14)";
  map count i32 = 0xBD = 189; first mapping name len 0x14=20 "NetPackagePackageIds"; serverUseEAC=false

## Pre-auth stage order (observed)

1. LiteNet connect (challenge `0xCA` + 16-byte Guid: `50a31b65-b661-45ca-9c40-c4ac383c6e7b` echo)
2. `PackageIds` (id 0)
3. client sends `PlayerLogin` (id 121)
4. `AuthState` (21) `authstate_nativeplatform`
5. `AuthState` (21) `authstate_encryption`
6. `AuthConfirmation` (20, empty body)
7. `AuthState` (21) `authstate_authenticated`
8. traffic switches to encrypted (`enc=1`); then `PlayerLoginAnswer` (122, bodyLen 1699)
9. `DiscordIdMappings` (5, body 5 bytes = entityId:u32 + remove:bool shape)
10. PASS joined entity=171; wander + clean disconnect

## Raw evidence (from /tmp/join6.log, truncated hex windows)

```
[join#1] STAGE ChallengeReceived: 50a31b65-b661-45ca-9c40-c4ac383c6e7b
[join#1] RECV len=4805 hex=00BC12000000000100B8120000000001030000000A0000000E000000BD000000144E65745061636B6167655061636B61...
[join#1] STAGE PackageIdsReceived: ver=V 3.1.0 (1.3.10.14) maps=189 eac=False
[join#1] STAGE LoginSent: pkgId=121
[join#1] RECV type=NetPackageAuthState id=21 bodyLen=25
[join#1] RECV type=NetPackageAuthConfirmation id=20 bodyLen=0
[join#1] RECV type=NetPackagePlayerLoginAnswer id=122 bodyLen=1699
[join#1] RECV type=NetPackageDiscordIdMappings id=5 bodyLen=5
[join#1] PASS joined entity=171
```

Cross-refs: docs/protocol.md §3 (golden hex) + §8 (live-observed pre-auth order),
workspace/CHANGELOG.md batch 8.
