# Flow: Steam P2P tunnel (internet transport)

**Status:** AUDITED (new subsystem — no native counterpart, so the audit
table records engine-interaction ground truth instead of ours-vs-native)
**Validated against commit:** `1ccc315` (phase-4 invites+password; runtime
gates passed 2026-07-28: LAN regression incl. role-OFF standby soak,
zero-config invite promotion, password apply. Previous stamp `c462970`,
steam-networking merge gates 2026-07-27)

## Scope

Carries all mbnet UDP (campaign 7240 + battle vports) over Steam
Datagram Relay / ICE so internet play needs no port forwarding. Entirely
client-side: everything lives in `warband_coop.asi` (host bridge runs in
the HOST machine's game client; plugin + dedicated exes are untouched).
Entry: ASI init starts one tunnel thread. Exit: process end (the thread
never gives up — any session death rebuilds from scratch).

## How it works

```
JOINER game (engine mbnet)          HOST game client (bridge)      HOST dedicated servers
  connects to 127.0.0.1:7240  --\
  (proxy = loopback listeners     +--Steam P2P (SDR relay/ICE)-->  per-(client x vport)
   on the REAL ports, lazy         |  5 listen vports (0-4)        ephemeral loopback
   ConnectP2P per vport)       ---/                                sockets -> 7240/7241+2s
```

- **Single tunnel thread owns all Steam calls** (`steam_tunnel_thread`).
  Role from coop.ini `[Steam]`: `SteamHost=1` -> host bridge, else
  `HostSteamID64` present -> client proxy, neither -> **role OFF =
  dormant invite standby** (phase 4): the thread still starts, waits for
  Steam up to 120 s (then exits quietly — invites dead that session),
  and idles pumping callbacks so a Join Game invite can arrive. OFF
  touches no sockets, publishes no client verdict, and never re-aims
  `g_host_ip` — but it DOES run the role-session preamble
  (`InitRelayNetworkAccess` relay warmup) and the 20 Hz
  `SteamAPI_RunCallbacks` pump process-wide for every Steam player.
  A `[Steam]` config error still means no thread at all.
- **Client proxy** exposes loopback listeners on the real ports and
  re-aims `g_host_ip` to 127.0.0.1 (reversible; also gates browser
  injection). Tri-state PENDING/UP/DOWN via
  `steam_tunnel_client_state()`; 90s PENDING watchdog so a hung Steam
  init can't hold injection forever.
- **Status callbacks are a pure enqueue** into a CS-guarded ring drained
  on the tunnel thread — they can be dispatched by the ENGINE's own
  SteamAPI_RunCallbacks pump, never assume the tunnel thread.
- **The tunnel thread pumps `SteamAPI_RunCallbacks` at 20 Hz** after a
  10 s grace: the engine's only pump call site is a Workshop spin in
  `mbCoreGame::findModules` run pre-WinMain, provably dead post-boot —
  SDR relay-config call-results ride this pump, so without it no
  rendezvous ever completes (both sides freeze at "only-if-cached").
- **Auto-recover loop**: any session end (SEH fault from a dying Steam
  client, setup failure, client retry exhaustion) publishes DOWN (LAN
  fallback live), runs SEH-guarded `steam_steamside_cleanup`, waits for
  Steam and rebuilds the role from scratch (backoff 5s -> 60s cap). If
  the engine's one-shot boot init never ran, the thread calls
  `SteamAPI_Init` itself after a 30 s grace (export ordinal 931).

## Invites + server password (phase 4, `1ccc315`)

**Invites are rich-presence only** (no Steam lobby): while the host
bridge is up, the HOST's game client publishes rich presence
`connect = coop:<host_id64>[:pw]` (`steam_host_run`, cleared in
`steam_steamside_cleanup`). That lights the **friend-side "Join Game"
button** — the host gets no right-click "Invite to Game" (lobby
feature, deliberately not built).

- **Delivery:** a `GameRichPresenceJoinRequested_t` callback object
  (`CCallbackBase` emulation in `steam_flat.h`; index **337**, payload
  264 B, and the vtable is **MSVC overload-reversed**: slot 0 = 3-arg
  Run, slot 1 = 1-arg Run — do not "fix" the order) registered via
  optional exports `SteamAPI_RegisterCallback`/`Unregister`. The
  callback body is enqueue-only (CS-guarded mailbox, last-writer-wins);
  `steam_drain_invite` on the tunnel thread parses (`steam_invite_parse`)
  and decides.
- **Refusals (all log-only — RE Q10 found no thread-safe on-screen
  print):** malformed string; this machine is the host; engine
  in-session (`ADDR_NET_RUN_FLAG` && `ADDR_NET_PROGRESS_STATE`==7 &&
  `ADDR_MAP_INTERACTION_MODE`==1 — "leave the current server first");
  tunnel to that host already up ("join via the MP browser" — the
  expected outcome for an ini-configured client clicking Join Game).
- **Accept = OFF->CLIENT promotion:** cfg.host_steamid/role are
  tunnel-thread-mutable; PENDING is re-published (watchdog tick
  re-anchored — a mid-session invite must not trip the 90 s watchdog),
  a live CLIENT session ends via `client_dead`, and the thread epilogue
  rebuilds as CLIENT with the new host id. Landing is **notify-only**
  ("COOP Direct is in the MP browser"); auto-join was RE'd (needs
  `m_switchingModule` 0xA8960D + both stored strings + table row 0) and
  deferred as upside.
- The whole invite surface is one all-or-nothing optional export group
  (Friends v017 + SteamUser v023 + Register/Unregister); any missing
  export disables invites with one log line and never costs the tunnel.

**Password** is engine-native end to end; the value never crosses our
wire (ch125/49/126/127) or the Steam connect string (`:pw` is a flag):

```
coop.ini [Coop] Password=  (host game dir, max 47 chars)
  -> CoopWSEPlugin coop_load_ini -> WSE/<module>/coop_server_cfg.wsedict
     {server_password} (write_server_cfg_dict, BOTH dedicated
     personalities, ~+3 s: winmm loader sleeps 3 s before plugin load)
  -> module coop_apply_server_password: 0.5 s campaign trigger + battle
     template start hook retry until dict_load_file succeeds (latch
     AFTER load -- an early tick must not disarm), then
     server_set_password
```

Joiner side: the injected row's `m_passworded` (+0x158) has **one
writer** — `(steam_tunnel_invite_pw() || g_password[0])` — because the
engine's ping-reply path always constructs fresh rows (RE Q6, no
in-place refresh). There is **no native password dialog** (RE Q7): the
browser's always-present password textbox is the entry point for the
campaign join, and the joiner's own `Password=` is mirrored into string
register **s57** every 500 ms for the deferred battle-hop connect —
required because opcode 3415 assigns `m_storedPassword` unconditionally
(RE Q11: an empty arg wipes it). `m_storedPassword` is also prefilled
once (in-place capacity-guarded rglString write, RE Q8) but only covers
the direct-connect arm.

## Code anchors

| # | Step | File | Line | Symbol |
|---|------|------|------|--------|
| 1 | Flat-API resolver (GetProcAddress off loaded `steam_api_wse2.dll`, fail-closed, layout asserts) | `src/asi/steam_flat.c` | 1 | `steam_flat_resolve` |
| 2 | Tunnel thread entry + role loop + auto-recover | `src/asi/steam_tunnel.c` | 626 | `steam_tunnel_thread` |
| 3 | Steam-ready wait (retries export resolution; not-ready never fatal) | `src/asi/steam_tunnel.c` | 437 | `steam_wait_steam_ready` |
| 4 | Host bridge session (5 listen vports -> loopback sockets) | `src/asi/steam_tunnel.c` | 988 | `steam_host_run` |
| 5 | Client proxy session (real-port listeners, lazy ConnectP2P) | `src/asi/steam_tunnel.c` | 1081 | `steam_client_run` |
| 6 | Per-vport connect (identity `m_cbSize` MUST be 8) | `src/asi/steam_tunnel.c` | 942 | `steam_client_connect_vport` |
| 7 | Callback enqueue (any-thread) | `src/asi/steam_tunnel.c` | 252 | `steam_on_status_changed` |
| 8 | 20 Hz RunCallbacks pump | `src/asi/steam_tunnel.c` | 751 | `steam_pump_callbacks` |
| 9 | SEH-guarded Steam-side teardown | `src/asi/steam_tunnel.c` | 512 | `steam_steamside_cleanup` |
| 10 | Proxy state for coop.c (re-aim + inject gate) | `src/asi/steam_tunnel.c` | 204 | `steam_tunnel_client_state` |

## State & events

- **Config (`coop.ini [Steam]`):** `SteamHost=1` + optional
  `AllowedSteamIDs` (host; empty allowlist logs a set-a-password
  warning) / `HostSteamID64` (joiner) / `Debug=1` (GNS verbose; default
  warnings-only). **`[Coop] Password=`** (phase 4): pool-wide join
  password, max 47 chars (s57 mirror clamp; longer warns + truncates on
  the hop), value never logged.
- **Telemetry:** MTU at connect, 10 s stat rows
  (ping/quality/pend/steamid), >1300 B fragmentation counter,
  relay-network status lines, `[gns:]` channel.
- **No module/protocol surface:** the tunnel is transparent to mbnet and
  to all ch49/125/126/127 traffic.

## Invariants

- Only the tunnel thread makes Steam API calls; callbacks only enqueue.
- Proxy state never regresses UP -> PENDING on an mbnet disconnect (the
  browser-inject gate cannot black out after a join cycle).
- LAN behavior is untouched when `[Steam]` is absent (role OFF; verified
  by the LAN regression gate).
- `PacketMaxSize=1200` (nettune) keeps every mbnet datagram inside Steam's
  real per-packet budget — measured `MTU_DataSize=1200`, not the documented
  1300; verified `frag>1300=0` both ends at ~24 KB/s. It is default-on in
  the shipped ini templates (`deploy/coop.ini` for source builds,
  `deploy/coop_client.ini` -> `coop.ini.example` in the release zip), NOT
  in `nettune.c`, whose compiled-in fallback is still the stock 1350. A
  host running without a `[NetTuning]` section fragments.

## Audit: engine-interaction ground truth

| # | Behavior | Ours (anchor) | Ground truth (evidence) | Verdict |
|---|----------|---------------|--------------------------|---------|
| 1 | Post-boot callback pump is ours alone | anchor 8 | Engine's single `SteamAPI_RunCallbacks` site is pre-WinMain (`patches/Warband_WSE2/findings.md` "SteamAPI_RunCallbacks pump audit", pointer slot 0xA47B20) | OK |
| 2 | Identity equality needs `m_cbSize=8` | anchor 6 | GNS compares type+size+payload; wrong size = "wrong remote identity" + ICE abort 5003 (fixed pre-merge) | OK |
| 3 | Loopback join passes engine auth | proxy re-aim to 127.0.0.1 | `isAuthExempt` @0x54C330 whitelists 127.0.0.1 + RFC1918 (`findings.md` "Loopback join classification"); 127.0.0.2/0.0.0.0 NOT exempt | OK |
| 4 | ManualDispatch rejected | anchor 8 comment | Exclusive process-wide mode switch; engine already init'd normally | OK (documented decision) |

## Open questions

- **Host bridge SEH crash (diagnostics armed):** one occurrence of
  `0xC0000005 addr=00000000 phase=host:runcb` (null-pointer call inside
  the pump) ~10-20s after bridge-up with a joiner retrying pre-host;
  cleanup faulted too; auto-recover armed. Reproduced once more
  2026-07-27 ~20:46. Hypothesis: rendezvous processed while the host's
  SDR relay config is still pending. Workaround: start host before
  joiners. Next occurrence is diagnosable from the log (`235743a`).
- **Joiner retry exhaustion when host absent:** 3x reason-5003 burns the
  attempts and deactivates until the auto-recover rebuild; browser row
  exists either way (proxy-up is not host-up). Still open after phase 4
  (kept out of scope); related: invite promotion reuses the crash-retry
  epilogue, so the first invite pays a flat 5 s backoff (DEFERRED.md
  "Phase 4 deferrals").

## Related docs

- `docs/NETWORKING_AUDIT.md` §6-7 (architecture + roadmap),
  `docs/STEAM_P2P_FACTS.md`, spec
  `docs/superpowers/specs/2026-07-26-steam-networking-design.md`.
