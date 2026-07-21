# WSE2 Binary Patches Reference

Patches applied to WSE2 binaries for coop development. All addresses are static VAs (preferred base 0x400000). Apply to on-disk exe files.

---

## mb_warband_wse2.exe (Game Client)

### Mutex — Allow Multiple Instances

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

| Field | Value |
|-------|-------|
| Function | `computePacketValues` (0x4A70C0) |
| Constant VA | 0x883B58 |
| File offset | 0x2A0AA6 |
| Type | float (4 bytes, little-endian IEEE 754) |
| Original | `0.033333` (30 Hz max send rate) |
| Patched | `0.016` (62.5 Hz) |
| Backup | `.bak_30hz` |
| Effect | Doubles max party position update rate to clients |
| Status | **Applied** |

**How to apply:**
```python
import struct
struct.pack_into('<f', data, file_offset, 0.016)  # 62.5 Hz
```

**File offset calculation:** VA 0x883B58, preferred base 0x400000, RVA 0x483B58. Convert via PE section table.

**Related server_config.ini settings:**
```ini
[General]
iMaxFrameRate=240        # Server main loop cap (must be >= send rate)

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
- Clamped: min = `*(float*)0x883B58` (patched), max = 0.1s (10Hz)

**Party position replication:**
- Dirty flag system: positions checked against last-sent values each frame
- Changed entries stamped with packet number
- Sent in round-robin order across players
- Position quantized to 17 bits (sufficient for campaign map precision)

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
