# Flow: Campaign Server Tick (frame loop, simple triggers, party replication, per-client send)

**Status:** AUDITED (engine side); D1 done + runtime-verified
(`562482c` gate, `6a72f6b` config-dict naming; `$g_coop_debug_reveal`
read 1 live 2026-09-24), D2/D4 implemented (build/config, not
runtime-tested), D3 apply-verified (drain effect unmeasured)
**Validated against commit:** `6a72f6b` (RE 2026-09-20 against the deployed
1145 exes with their PDBs; the `patches/WSE2Dedicated` Ghidra project is
stale -- see Open questions)

## Scope

What the dedicated campaign server does every frame and how that work
reaches clients: the `mbCoreGame::frameMove` order, when module-system
simple triggers run and on what clock, how party state is replicated
(dirty position table vs. explicit events), and how `sendToPlayer` paces
each client -- including the backlog arm that pins a client to 10 Hz.
Entry point: the main loop at `iMaxFrameRate`. Exit state: one packet per
due client per frame. This dossier exists because "the campaign server
lags every so often" turned out to be a per-client event flood plus a
send-pacing bug, not server CPU.

Module paths relative to `wse2work/Native-Coop-master/`. Engine addresses
are preferred-base VAs of the deployed WSE2 1145
`mb_warband_wse2_dedicated_campaign.exe` (rebase by the live ASLR slide;
observed +0x560000 and other values in both directions).

## Sequence diagram

```mermaid
sequenceDiagram
    participant L as Main loop (iMaxFrameRate)
    participant G as mbGame::frameMove
    participant R as Replication
    participant P as sendToPlayer (per client)
    participant C as Client

    L->>L: listen + updatePacketDeliveryControl
    L->>G: frameMove(dt clamped to 0.1 s; skipped ~99% of frames with 0 players)
    G->>G: mbSimpleTriggerManager::execute -- every due trigger runs to completion
    note over G: party_set_flags (opcode 1603) inside a trigger:<br/>m_flags |= v (no already-set check), m_updateSpeed = 1,<br/>and on gameType 5 an mbnetEvent BROADCAST to every client
    G->>G: hour/day rollover, per-party frameMove (AI on game-hour timers)
    L->>R: updateReplicationData -- diff pos/target/behavior of ALL parties, stamp m_packetNo
    L->>P: send() sweeps players
    P->>P: period = m_packetSendPeriod, or backlog arm (see audit 4)
    P->>C: header + ACK + events (1300 B / 250 cap) + [replication rows only if events fully drained] + terminator
    note over C: while a backlog drains: no party position rows at all
```

## Code anchors

| # | Step | File / binary | Line / VA | Symbol |
|---|------|---------------|-----------|--------|
| 1 | Main loop, frame period from `iMaxFrameRate` | campaign exe | 0x443BF4 | `runDedicatedServer` loop |
| 2 | Per-frame order: listen, delivery control, game tick, replication, send | campaign exe | 0x43B540 | `mbCoreGame::frameMove` |
| 3 | Pause gate, campaign clock advance, triggers, hour/day, party loop | campaign exe | 0x466EB0 | `mbGame::frameMove` |
| 4 | Runs every due simple trigger, no budget | campaign exe | 0x4E6420 | `mbSimpleTriggerManager::execute` |
| 5 | `interval <= (g_timersTotal[timerNo] - last) / 100000.0` | campaign exe | 0x4E5FF0 | `mbSimpleTrigger::execute` |
| 6 | `party_set_flags` case body: OR, m_updateSpeed, broadcast | campaign exe | 0x4B9702 | opcode 1603 in `mbStatement::execute` |
| 7 | Event builder (type 0x18, 81 bits) + broadcast | campaign exe | 0x492240 / 0x494A00 | `fillPartySetFlagsClientEvent` / `mbnetNetworkServer::sendEvent` |
| 8 | Full-party dirty diff every frame | campaign exe | 0x49D4F0 | `mbnetNetworkServer::updateReplicationData` |
| 9 | Round-robin dirty rows, 0x2A2F-bit cut | campaign exe | 0x49B920 | `sendPartyReplicationData` |
| 10 | Binary eligibility (disabled/static/dont-send), no distance | campaign exe | 0x4A7630 | `getPartyReplicationPriority` |
| 11 | Per-client pacing incl. backlog arm | campaign exe | 0x499D30 | `mbnetNetworkServer::sendToPlayer` |
| 12 | Backlog ceiling load (patched operand at +4) | campaign exe / battle exe | 0x499D89 / 0x4C56A9 | `movss xmm1,[0.1f]` |
| 13 | Backlog flag latch `= !fillPacket()` | campaign exe | 0x499FE4 | `mov [edi+0x19C], al` |
| 14 | Debug reveal trigger (D1), gated on `$g_coop_debug_reveal` | `module_simple_triggers.py` | 263 | `(6, [multiplayer_is_server, multiplayer_is_campaign, eq $g_coop_debug_reveal 1, ... party_set_flags pf_always_visible ...])` |
| 15 | Bandit-lair reveal block (D2, now SP-only) | `module_simple_triggers.py` | 2189 (lair gate 2231) | 0.1-interval attach-lords trigger |
| 16 | Backlog ceiling knob + disp32 re-point | `src/shared/nettune.c` | `backlog_site` | `BacklogPeriodMs` |
| 17 | Site addresses | `src/shared/warband_addrs_wse2.h` | `CAMP_/DED_NT_BACKLOG_CEIL_*` | |
| 18 | Frame cap (D4) | `deploy/configs/server_config.ini` | `iMaxFrameRate=100` | |
| 19 | Debug reveal plumbing: `COOP_DEBUG_REVEAL` env -> `coop server cfg campaign.wsedict{debug reveal}` -> `$g_coop_debug_reveal` (spaces on disk: the module's `@coop_server_cfg_campaign` / `@debug_reveal` lose their underscores at quick-string load) | `deploy/scripts/coop_launch_all_debug.bat`, `src/coop_campaign.c`, `module_coop_scripts.py` | 372 / 16677 | `wsedict_set_int(d, "debug reveal", ...)` / `coop_apply_server_cfg` |

## State & events

- **Per-client send state (`mbnetPlayer`, stride 0x348):** `+0x19C` backlog
  flag, `+0x2CE` ping (int16, ms), `+0x2F0` `m_packetSendPeriod`, `+0x2F4`
  byte-rate EWMA, `+0x2F8` packet max size, `+0x2FC` upload limit (AIMD),
  `+0x300` next-send time.
- **Replication table 2 (parties):** 4 rows per party -- position
  (+0x90/94/98), target (+0x210/214), behavior (+0x1C0), behavior object
  (+0x1C4). Flags, icon, name, faction and roster are NOT in the table;
  they travel as explicit events (spawn burst at join, `party_set_flags`
  broadcast on mutation).
- **Clock:** `g_timersTotal[1]` (0x8CC420) is the campaign date clock; the
  simple-trigger manager stamps every trigger with timer 1
  (`m_defaultTimerNo`, mbGame ctor 0x462103). It advances by
  `fTimeMultiplier` (0x8C1AE8, image default 0.25) x min(dt, 0.1 s).
- **Network events:** ch125/ch49 are not involved; the engine's own party
  events (join spawn burst from `syncPlayer` 0x49DEF0, set-flags type 0x18) and replication rows are.
- **Ini:** `[NetTuning] BacklogPeriodMs` (16-100, default 33, 100 = stock).
- **Env:** `COOP_DEBUG_REVEAL=1` (set only by `coop_launch_all_debug.bat`)
  is read by the host plugin and lands in `$g_coop_debug_reveal` via the
  server-cfg dict (anchor 19); unset = 0 = native fog of war.

## Invariants

- Every due simple trigger runs to completion inside the same frame, before
  `updateReplicationData` and `send` (anchors 2-4). Trigger time is send
  delay.
- `party_set_flags` on the campaign personality is a broadcast per call,
  even when the flag is already set (anchor 6). Any periodic caller must
  memoize module-side; the engine will not.
- A client receives replication rows only in a packet whose event section
  fully drained (anchor 11: `fillPacket == true && m_ready`); otherwise the
  packet ends with a `putRange(0)` marker and positions wait.
- The backlog ceiling site is a re-pointed operand: nettune compares the
  operand against `REBASE(stock .rdata VA)` and writes the address of
  `g_backlog_period_s`; the shared 0.1f dword is never rewritten (anchors
  12, 16-17).
- The 0.1 s clamp in `mbCoreGame::frameMove` is on real dt before scaling:
  a stalled server loses campaign time, it never fast-forwards.

## Audit: ours vs. native

| # | Behavior | Ours (anchor) | Native ground truth (evidence) | Verdict |
|---|----------|---------------|--------------------------------|---------|
| 1 | Debug trigger sets `pf_always_visible` on every active party every 6 units (anchor 14) | Gated (`562482c`): fires only on the campaign server with `$g_coop_debug_reveal` = 1, i.e. a `coop_launch_all_debug.bat` launch; the normal launch never runs it | Opcode 1603 case body 0x4B9702: no compare before the OR, unconditional `mbnetEvent` broadcast to every ready client when `m_gameType == 5`, plus `m_updateSpeed` -> next-frame speed script + label rebuild per party. 0x4000 is never read by the server exe (single `and *,0x4000` hit is `mbItem::isNotShield`); it is a client map-render flag (14 client sites). Per fire: ~N_parties events x N_clients (~7-8 KB wire per client), and replication rows suppressed for that client until drained -- still true whenever the debug launch is used (no memoize) | OK (D1, `562482c`, runtime-verified 2026-09-20/21: normal launch keeps fog of war, debug launch reveals) |
| 2 | Vanilla 0.1-interval trigger walks all parties for bandit lairs near `p_main_party` and calls `party_set_flags` on hits (anchor 15) | Gated `neg\|game_in_multiplayer_mode` (`b6b295b`) | Same broadcast cost per call; the server has no main party so the check was dead logic. Coop-side lair reveal parked in `docs/DEFERRED.md` | OK (D2, build-verified, not runtime-tested) |
| 3 | Party positions reach clients via replication | Engine native | `updateReplicationData` 0x49D4F0 diffs 4 rows per party by exact inequality every frame; `sendPartyReplicationData` 0x49B920 round-robin per client, cut at 0x2A2F bits; `getPartyReplicationPriority` 0x4A7630 is 1/0 on disabled (0x100), static (0x400), dont-send (0x8000). No visibility or distance cull exists | OK |
| 4 | Send pacing while a client has a backlog | Stock: `max(m_packetSendPeriod, min(0.1f, ping_ms / 0.001f * 0.7f))` -- `divss` where a `mulss` was meant (0x499D91), so the min saturates for any ping >= 1 ms and the client is pinned to 10 Hz exactly when it is behind | Fixed in `226e956`: `BacklogPeriodMs` re-points the disp32 of the single ceiling load (0x499D8D campaign / 0x4C56AD battle) at `g_backlog_period_s`; default 33 ms collapses the arm to `m_packetSendPeriod`. The 0.1f dword has 39 readers (campaign) / 103 (battle, incl. `mbCoreGame::frameMove`'s dt clamp) so it is not rewritten. Verified applying on both exes 2026-09-20 (host log `backlog_ceiling: 0x00DE7BEC -> ...`, battle log `0x0073B870 -> ...`); drain-time effect not yet measured with a client | OK (D3, implemented, apply-verified, effect unverified) |
| 5 | Main loop at 240 fps | `server_config.ini` 240 -> 100 (`197f230`) | Sends cap at 30 Hz per client (`computePacketValues` floor 0x887BC0); every frame still walks all parties (anchor 8) and runs per-party `frameMove`; campaign time integrates from dt so the cap is CPU only | OK (D4, config, not runtime-tested) |
| 6 | Simple-trigger interval unit on this personality | Module comments assume seconds (autosave `(300, ...)` "5 min") | `mbSimpleTrigger::execute` 0x4E5FF0 compares against timer 1 = the campaign date clock (same accumulator `mbGame::frameMove` divides by 100000 for `m_hour`), advanced at 0.25 h per real second -> 1 game hour = 4 s, so 300 = 20 min, 6 = 24 s, 24 = 96 s. A first-pass reading called it seconds; the deeper trace says hours | UNKNOWN (needs one live count) |
| 7 | `stop_time` pauses the campaign server clock | Console `campaign_pause` uses opcode 3608 | `mbGame::m_paused` (+0x39C) has one writer, the ctor (= 0); 3608 is a mission-pause op. The clock never stops on this personality | DIVERGES (documented, no fix requested) |
| 8 | Plugin per-frame work | `coop_on_frame` heartbeat + one global read | Negligible; IPC on its own thread | OK |

## Fix list

| # | From audit row | What diverges | Suggested owner/layer |
|---|----------------|---------------|------------------------|
| D1 | 1 | Debug all-visible trigger floods every client with one flags event per party per fire and starves position replication while it drains | Done `562482c` (module gate + `src/coop_campaign.c` env read + `coop_launch_all_debug.bat`), runtime-verified 2026-09-20/21. Residual: the debug launch still broadcasts per fire; if it ever needs to be cheap, set the flag once at server start or memoize per party |
| D2 | 2 | Bandit-lair reveal ran on the server against a nonexistent main party | Done `b6b295b` (module) |
| D3 | 4 | Backlogged client pinned to 10 Hz by a miscompiled ping term | Done `226e956` (`nettune.c`, both dedicated exes) |
| D4 | 5 | 240 fps main loop | Done `197f230` (`deploy/configs/server_config.ini`; deployed copy must be updated by hand) |

## Open questions

- Audit row 6: seconds vs. game hours. Resolve by counting hits of any
  known trigger over 60 s with a client connected, or reading
  `g_timersTotal[1]` twice 10 s apart (expect +250000 if hours).
- D3 effect: trace the backlog latch (0x499FE4) during a join and confirm
  `+0x300` advances at `m_packetSendPeriod`, not 0.1 s.
- D2/D4 have only been built/configured, not observed with players; the
  deployed game-dir `server_config.ini` must be copied over by hand (D4).
- `patches/WSE2Dedicated` (Ghidra project + index.db) was built from the
  Nov-2025 exe under `wse2work/WSE2 Coop Server/`, not the deployed 1145
  build; offsets differ non-uniformly (+0x10..+0x3920). Every address in
  this dossier was re-derived on the deployed file. Re-analyze before the
  next RE pass.

## Related docs

- `steam-tunnel.md` (nettune's other knobs, `PacketMaxSize` rationale)
- `party-screen-sync.md` (roster reaches clients via the join spawn burst)
- Workbench documents: `patches/WSE2Dedicated/findings_campaign_periodic_load.md`
  (this analysis), `patches/WarbandDedicated/findings.md` ("nettune patch
  sites", Q1-Q7 send-path anatomy), `patches/WarbandDedicated/network_tick_rate.md`,
  `docs/wse2-binary-patches.md` ("Backlog Send-Period Ceiling"),
  `docs/DEFERRED.md` ("Campaign server periodic load").
