# Flow: Steam P2P tunnel (internet transport)

**Status:** AUDITED (new subsystem — no native counterpart, so the audit
table records engine-interaction ground truth instead of ours-vs-native)
**Validated against commit:** `7161f85` (doc refresh 2026-09-21: all
`steam_tunnel.c` / `steam_flat.c` anchors re-verified unchanged since
`2923381`; narrative adds the auto-join driver's reuse as the campaign
return hop after a local visit (`4676755`, runtime-verified 2026-09-19)
and a dedicated battle; runtime-verified tunnel behavior unchanged since
`09da2f7`). Prior stamp `2923381` (line anchors re-verified in full
static doc audit 2026-08-30; runtime-verified behavior unchanged since
`5ccf502`) -- prior stamp `5ccf502` (phase-5 chain/lobby invites +
auto-join; all runtime gates 1-12 passed 2026-08-23/24 incl. LAN
regression, chain invite, host + joiner right-click invites, ini-joiner
lobby join, host-shutdown cleanup, password gates, and the auto-join
matrix. Previous stamps: `1ccc315` phase-4 gates 2026-07-28, `c462970`
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
  the engine's one-shot boot init never ran, the thread self-inits after
  a 30 s grace — but ONLY when `SteamAPI_IsSteamRunning()` reports Steam
  up. This gate is load-bearing: a FAILED `SteamAPI_Init` leaks a ~32 MB
  GameNetworkingSockets relay arena, so the pre-gate 250 ms blind retry
  exhausted the 32-bit address space in ~25 s and raised
  `EXCEPTION_OUT_OF_MEMORY` (fixed `09da2f7`, 2026-08-29; runtime-verified
  VA-flat with Steam off). When a host/client role gives up finding Steam
  past the grace it publishes `$g_coop_steam_missing`, and the module
  shows the host a one-shot in-game warning (`mnu_coop_steam_warning`).

## Invites + server password (phase 4 `1ccc315`, phase 5 `5ccf502`)

**Two invite surfaces, both funneling into the same mailbox path:**

- **Rich presence** (phase 4 + phase-5 chain invites): the HOST's game
  client publishes `connect = coop:<host_id64>[:pw]` while the bridge is
  up, and since phase 5 **every joiner publishes the same string while
  its client session is UP** — so friends of joiners also get the
  friend-side "Join Game" button (chain invites, gate 2/3 verified).
- **Steam lobby** (phase 5): the host creates a **Public** lobby at
  bridge-up (`steam_host_lobby_tick`, `STEAM_LOBBY_TYPE` =
  `SF_LOBBY_TYPE_PUBLIC` — the spec's Invisible default was flipped by
  the pre-planned contingency `22c7248`: runtime proved Invisible
  lobbies are NOT returned to other users' `RequestLobbyList`), stamped
  with lobby data `host=<id64>` + the same connect string. Every joiner
  finds it via `RequestLobbyList` + worldwide distance filter + string
  filter on `host` and joins; lobby membership lights the right-click
  **"Invite to Game"** entry for host AND joiners (gates 3/4). Lobby is
  invite sugar, never transport: one join attempt per session, log-only
  failures. Host shutdown destroys it (gate 6). Known Steam limitation
  (accepted): lobby co-members lose their MUTUAL Join Game / Invite
  entries toward each other — the entries exist toward third parties.
- **Lobby-invite delivery** = `GameLobbyJoinRequested_t` (callback index
  **333**, 16 B payload) into the phase-4 mailbox/parse/refusal/
  promotion path. A host accepting a chain invite to its OWN server
  takes the **LOCAL auto-join kind** (`d96fbeb`, joins over LAN, no
  role change).

- **Delivery:** a `GameRichPresenceJoinRequested_t` callback object
  (`CCallbackBase` emulation in `steam_flat.h`; index **337**, payload
  264 B, and the vtable is **MSVC overload-reversed**: slot 0 = 3-arg
  Run, slot 1 = 1-arg Run — do not "fix" the order) registered via
  optional exports `SteamAPI_RegisterCallback`/`Unregister`. The
  callback body is enqueue-only (CS-guarded mailbox, last-writer-wins);
  `steam_drain_invite` on the tunnel thread parses (`steam_invite_parse`)
  and decides.
- **Refusals (all log-only — RE Q10 found no thread-safe on-screen
  print):** malformed string; this machine hosts a different server than
  the invite targets; engine in-session (`ADDR_NET_RUN_FLAG` && `ADDR_NET_PROGRESS_STATE`==7 &&
  `ADDR_MAP_INTERACTION_MODE`==1 — "leave the current server first");
  tunnel to that host already up ("join via the MP browser" — the
  expected outcome for an ini-configured client clicking Join Game).
- **Accept = OFF->CLIENT promotion:** cfg.host_steamid/role are
  tunnel-thread-mutable; PENDING is re-published (watchdog tick
  re-anchored — a mid-session invite must not trip the 90 s watchdog),
  a live CLIENT session ends via `client_dead`, and the thread epilogue
  rebuilds as CLIENT with the new host id.
- **Auto-join on landing (phase 5, gates 7-12):** at tunnel-UP an
  armed-bit handshake fires unless the invite carried `:pw` and the
  joiner has no local `[Coop] Password=` (`steam_autojoin_verdict` —
  that case stays notify-only, gate 10). A `mbGame::frameMove` hook
  (`ADDR_FRAMEMOVE` 0x483340, in `coop.c`) owns all engine writes:
  opcode-3415-style stores (`m_storedAddress`/`m_storedPassword` via
  `rglString::operator=`, `m_switchingModule` + `m_connectToServer`=1),
  forced navigation from dead-zone screens via mbStartingWindow's
  loading-window **mode-6** recipe (the route must yield `m_gameType=4`
  or the engine drops campaign ping replies, `5e2f9f6`; mode 4 is
  poison), WAIT while the stack holds map/tactical/conversation or a
  modal dialog, a WAIT_NATIVE kind that sets `m_connectToServer`
  just-in-time so the native main-menu arm can't win the same-frame
  race via its mode-4 route (`af1a722`), and ASI-owned flag cleanup
  (engine-consumed / 60 s timeout / tunnel down — mandatory because the
  7-NOP 3415 patch removed the initial menu's native clear; verified no
  stale-flag bounce, gate 11). With no `[Steam]` keys the hook idles
  (gate 12). The same driver is the ASI's **campaign return hop**: any
  mission a campaign client ends at gameType 4 drops the connection, so
  `arm_campaign_return` (`coop.c:189`) arms the hook at the campaign
  server's address -- TUNNEL kind while the client proxy is UP (a
  mid-wait tunnel death aborts the join), LOCAL otherwise -- after a
  dedicated battle (ch127 ev 55, `e7eb400`) and after a local visit
  (`4676755`, runtime-verified 2026-09-19). No `[Steam]` keys needed:
  the LOCAL kind runs on plain LAN.
- The whole invite surface is one all-or-nothing optional export group
  (Friends v017 + SteamUser v023 + Register/Unregister; phase 5 folds in
  the matchmaking accessor `SteamAPI_SteamMatchmaking_v009` + lobby
  thunks); any missing export disables invites with one log line and
  never costs the tunnel.

**Password** is engine-native end to end; the value never crosses our
wire (ch125/49/126/127) or the Steam connect string (`:pw` is a flag):

```
coop.ini [Coop] Password=  (host game dir, max 47 chars)
  -> CoopWSEPlugin coop_load_ini -> WSE/<module>/"coop server cfg <campaign|battle>.wsedict"
     {"server password"} (write_server_cfg_dict, BOTH dedicated
     personalities, ~+3 s: winmm loader sleeps 3 s before plugin load;
     spaces, not underscores -- the module's @strings lose their
     underscores at load)
  -> module coop_apply_server_cfg: 0.5 s campaign trigger + battle
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
| 1 | Flat-API resolver (GetProcAddress off loaded `steam_api_wse2.dll`, fail-closed, layout asserts) | `src/asi/steam_flat.c` | 18 | `steam_flat_resolve` |
| 2 | Tunnel thread entry + role loop + auto-recover | `src/asi/steam_tunnel.c` | 1041 | `steam_tunnel_thread` |
| 3 | Steam-ready wait (retries export resolution; not-ready never fatal) | `src/asi/steam_tunnel.c` | 779 | `steam_wait_steam_ready` |
| 4 | Host bridge session (5 listen vports -> loopback sockets) | `src/asi/steam_tunnel.c` | 1433 | `steam_host_run` |
| 5 | Client proxy session (real-port listeners, lazy ConnectP2P) | `src/asi/steam_tunnel.c` | 1542 | `steam_client_run` |
| 6 | Per-vport connect (identity `m_cbSize` MUST be 8) | `src/asi/steam_tunnel.c` | 1357 | `steam_client_connect_vport` |
| 7 | Callback enqueue (any-thread) | `src/asi/steam_tunnel.c` | 282 | `steam_on_status_changed` |
| 8 | 20 Hz RunCallbacks pump | `src/asi/steam_tunnel.c` | 1166 | `steam_pump_callbacks` |
| 9 | SEH-guarded Steam-side teardown | `src/asi/steam_tunnel.c` | 881 | `steam_steamside_cleanup` |
| 10 | Proxy state for coop.c (re-aim + inject gate) | `src/asi/steam_tunnel.c` | 234 | `steam_tunnel_client_state` |

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
- **Steam-missing warning:** a host/client role that can't find Steam
  past the self-init grace publishes `$g_coop_steam_missing` (DLL-written,
  republished by the s59 writer); the module pops `mnu_coop_steam_warning`
  once on the campaign map — invites off, LAN join still works.

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
| 5 | Self-init gated on `SteamAPI_IsSteamRunning` (no VA leak) | anchor 3 | A FAILED `SteamAPI_Init` leaks a ~32 MB GNS relay arena; pre-fix the 250 ms blind retry raised `EXCEPTION_OUT_OF_MEMORY` in ~25 s (live trace: `SteamAPI_Init` from `warband_coop.asi+0x58EE`, +32 MB/call, 12 calls = +385 MB). Gated on `IsSteamRunning()`; runtime-verified VA-flat with Steam off 2026-08-29 | OK |

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

- `docs/archive/NETWORKING_AUDIT.md` §6-7 (architecture + roadmap),
  `docs/archive/STEAM_P2P_FACTS.md`, spec
  `docs/superpowers/specs/2026-07-26-steam-networking-design.md`.
