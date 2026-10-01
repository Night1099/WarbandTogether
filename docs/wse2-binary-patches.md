# WSE2 Binary Patches Reference

Patches applied to WSE2 binaries for coop development. All addresses are static VAs (preferred base 0x400000). Apply to on-disk exe files.

## Shipped patch set (rev 1145 client exe)

The release zip ships `mb_warband_wse2.exe` with exactly these four
on-disk patches; the dedicated exes ship unpatched (their tuning is
applied at runtime by `CoopWSEPlugin.dll`, see `nettune.c`).

| Patch | File offset | Effect |
|-------|-------------|--------|
| Opcode 3415 fix | 0x0D3D86 | NOP the `m_connectToServer` clear — auto-connect works |
| ASLR disabled | 0x1AE | DllCharacteristics 0x8140 -> 0x8100 |
| .text writable | 0x26C | Section characteristics 0x60000020 -> 0xE0000020 |
| Dual-port LAN scan | 0x14868D + 0x148803 + 0x3B7289 | Browser probes port and port+1 |

---

## mb_warband_wse2.exe (Game Client)

### Mutex — Allow Multiple Instances (not shipped)

**Status: development-only, NOT applied to the shipped client exe** (the
byte at 0x21DCB9 is the stock `75` in the deployed rev-1145 build,
checked 2026-09-21). Apply it locally to run two clients on one machine.

WSE2 creates a named mutex `"WSE2 Mutex"` at the top of `WinMain` and exits if it already exists.

| Field | Value |
|-------|-------|
| Function | `WinMain` (0x0061E880) |
| Check address | 0x0061E8B9 |
| File offset | 0x0021DCB9 |
| Original | `75` (jne — skip if mutex is new) |
| Patched | `EB` (jmp — always continue) |
| Effect | Allows multiple game instances to run simultaneously |

**How to apply:**
```python
data[0x21DCB9] = 0xEB  # jne → jmp
```

---

## mb_warband_wse2_dedicated_campaign.exe (Campaign Server)

### Network Send Rate — Increase Party Position Update Frequency

The server rate-limits per-player packet sends with an adaptive period clamped between 33ms (30Hz) and 100ms (10Hz). Campaign party positions update at this rate. Lowering the minimum period makes movement feel snappier.

**Status: Never applied on rev 1145** (stale pre-1145 entry — see
`docs/archive/TRAFFIC_OPTIMIZATION.md` F2). Superseded by the runtime
`[NetTuning] SendRateHz` knob in CoopWSEPlugin (`nettune.c`).

The `0x883B58 = Applied` VA below was never real for this binary — that
address holds ASCII text with zero code references, not the send-period
constant. The actual read/write sites (RE'd in the A9 session, see
`patches/WarbandDedicated/findings.md` "nettune patch sites"):

| Field | Value |
|-------|-------|
| Function | `computePacketValues` (0x4A70E0) — 0x4A70C0 is mbnetPlayer::pong; the 0x4A70C0 label was a prior mislabeling corrected during the WarbandDedicated RE pass |
| Constant VA | 0x887BC0 (`.rdata` float, sole reader `movss xmm1,[0x887BC0]` @ 0x4A712D) |
| File offset | 0x4867C0 |
| Original | `0.033333` (30 Hz max send rate) |
| Secondary default | `rglConfig::Network` defaults ctor writes the same 0.033333 as an immediate at VA 0x6A16A3 (file offset 0x2A0AA6) — both sites must agree for a static binary patch to hold |

**Related server_config.ini settings:**
```ini
[General]
iMaxFrameRate=100        # Server main loop cap (must be >= send rate; sends cap at 30 Hz, every frame walks all parties)

[Network]
iUdpSendBufferSize=1048576    # Larger send buffer for higher rates
iUdpReceiveBufferSize=1048576
```

### Send Rate Architecture

```
Main thread (iMaxFrameRate Hz):
  mbCoreGame::frameMove (0x43B6D0)
    → updateReplicationData (0x49D4F0)   # check dirty party positions
    → send (0x499B80)                     # per-player send decision
      → sendToPlayer (0x499D30)           # rate-limited by m_packetSendPeriod
        → sendPartyReplicationData (0x49B920)  # quantized 17-bit positions

Network thread (0x489280) — receive only:
  Sleep(1) loop → WSARecvFrom → dispatch to game thread
```

**Per-player adaptive rate:**
- `m_packetSendPeriod` at player struct +0x2F0
- Computed from upload bandwidth (3,000–100,000 bytes/sec per player)
- Clamped: min = `*(float*)0x887BC0` (unpatched, 0.033333), max = 0.1s (10Hz)

**Party position replication:**
- Dirty flag system: positions checked against last-sent values each frame
- Changed entries stamped with packet number
- Sent in round-robin order across players
- Position quantized to 17 bits (sufficient for campaign map precision)

### Backlog Send-Period Ceiling — Runtime (`[NetTuning] BacklogPeriodMs`)

`sendToPlayer` (0x499D30) selects the period with a three-way branch on
`mbnetPlayer` state. The backlog arm is taken when the previous packet
overflowed (`+0x19C`, latched from `!fillPacket`) and computes
`max(m_packetSendPeriod, min(0.1f, ping_ms / 0.001f * 0.7f))`. The ping
term is miscompiled (`divss` by 0.001 where a multiply was intended), so
for any ping >= 1 ms it saturates and a backlogged player is pinned to
exactly 100 ms = 10 Hz — the moment it most needs draining (join burst,
character/inventory hydrate, replication catch-up).

The 0.1f dword (0x887BEC campaign / 0x8BB870 battle) is shared by ~40 /
~100 readers including `mbGame::updateHour`, `mbParty::frameMove` and the
battle exe's frame-dt clamp, so it is never rewritten. Instead the plugin
re-points the disp32 of the single `movss xmm1,[0.1f]` that loads the
ceiling at a plugin-owned float (verify-before-write on the slid operand):

| Field | Campaign | Battle |
|-------|----------|--------|
| Instruction | `movss xmm1,[0x887BEC]` @ 0x499D89 (`F3 0F 10 0D EC 7B 88 00`) | `movss xmm1,[0x8BB870]` @ 0x4C56A9 |
| disp32 operand VA | 0x499D8D | 0x4C56AD |
| Stock operand | 0x887BEC (slid at runtime) | 0x8BB870 (slid at runtime) |
| Replacement | `&g_backlog_period_s` in `nettune.c` | same |
| Knob | `BacklogPeriodMs` 16-100, default 33; 100 leaves the operand stock | same |

With 33 the backlog arm collapses to `m_packetSendPeriod`, i.e. a
backlogged player drains at its normal rate. It cannot go faster than
that period — `max()` dominates — so AIMD (`AimdFloor`/`AimdStep`) remains
the bandwidth authority. RE: `patches/WSE2Dedicated/findings_campaign_periodic_load.md`
and the 2026-09-20 backlog-period RE (deployed 1145 exes; the Ghidra
project under `patches/WSE2Dedicated` is stale).

---

## mb_warband_wse2.exe — multiplayer_connect_to_server Fix

WSE2 opcode 3415 sets `m_connectToServer` flag, but `mbInitialWindow::frameMove` clears it before the profile window reads it. NOPing the clear makes auto-connect work.

| Field | Value |
|-------|-------|
| Function | `mbInitialWindow::frameMove` (VA 0x4D4986) |
| File offset | 0x0D3D86 |
| Original | `C6 05 0F 96 A8 00 00` (mov byte [0xA8960F], 0) |
| Patched | `90 90 90 90 90 90 90` (NOP) |
| Effect | `m_connectToServer` flag persists, auto-connect works |

---

## mb_warband_wse2.exe — Dual-Port LAN Scanner

The LAN server browser probes only one port (default 7240). This patch makes it probe base port AND base port + 1, so servers on 7241 are also discovered.

**Requires two prerequisite PE header changes:**

| Field | Offset | Original | Patched | Effect |
|-------|--------|----------|---------|--------|
| DllCharacteristics (ASLR) | 0x1AE | `0x8140` | `0x8100` | Disable DYNAMIC_BASE — binary loads at its preferred base (0x400000) |
| .text Characteristics | 0x26C | `0x60000020` | `0xE0000020` | Add IMAGE_SCN_MEM_WRITE — cave flag byte is writable |

The code cave for this patch is applied by maintainer tooling; the release install package ships a client exe with all patches already applied.

| Site | VA | File offset | Original | Patched |
|------|----|-------------|----------|---------|
| Port load | 0x54928D | 0x14868D | `0F B7 05 40 4B A4 00` (`movzx eax, word ptr [0xA44B40]`) | `E9 F7 EB 26 00 90 90` (`jmp 0x7B7E89; nop; nop`) |
| Loop increment | 0x549403 | 0x148803 | `47 3B 7C 24 34` (`inc edi; cmp edi, [esp+0x34]`) | `E9 AA EA 26 00` (`jmp 0x7B7EB2`) |
| Code cave | 0x7B7E89 | 0x3B7289 | 71 bytes of `CC` inter-function padding | 66-byte trampoline |

**How it works:** A 66-byte code cave in .text inter-function padding at VA 0x7B7E89. The interface-loop runs twice per NIC — first probe on base port, second on base port + 1. A flag byte in the cave tracks first vs second pass.

---

## Applying Patches

### Python one-liner (mutex example)
```python
import struct
exe = 'path/to/mb_warband_wse2.exe'
with open(exe, 'rb') as f: data = bytearray(f.read())
pe = struct.unpack_from('<I', data, 0x3C)[0]
base = struct.unpack_from('<I', data, pe+0x34)[0]  # image base
# ... convert VA to file offset via sections ...
data[file_offset] = 0xEB
with open(exe, 'wb') as f: f.write(data)
```

### Verify before patching
Always check the original byte matches before writing. ASLR doesn't affect on-disk files — only runtime addresses.
