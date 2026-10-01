# Flow: Battle Pipeline (dedicated battle end-to-end)

**Status:** AUDITED
**Validated against commit:** `7161f85` (docs refresh 2026-09-21: every
line anchor re-verified against the current tree — `module_coop_scripts.py`
scripts past ~7200 moved by +170..+2300 since the `0b2500a` numbering;
sequence + anchors updated for the wipe-proof battle-server identify and
the ch127 ev 55 auto-return (`e7eb400`; gates 1-3 + kill-XP win variant
passed 2026-08-29, retreat / no-Steam / siege / kill-XP-loss / save-cap
variants still open), the join-menu skip (`ebd4f64`; field gates 1+3
passed 2026-09-07, siege variant open) and the outcome-independent
kill-XP credit (`e28eacf`); no verdict changed. Prior stamp `79ec266`:
IPC single-owner fix `7afc290` runtime-verified 2026-09-07; `ce0e287`:
steamid persistence, runtime-verified 2026-08-23 — char dicts keyed by
Steam acctid (`coop_char_sid_<acctid>` via the `coop_char_store_dict_name`
key-builders), campaign result apply + Phase 2 XP moved into
`coop_player_hydrate` (ch49 identify ev 8 or a 5 s timeout), battle dict
gained `@battle_player_{i}_acctid` for reward keying; `9681486`: ev 14
freed by the packed char-sync; `0b2500a`: multiserver pass,
runtime-verified 2026-07-18; `632466c`: A9 row flip)

## Scope

The dedicated coop battle: a client on the campaign server requests a battle
from an encounter, the campaign server allocates a free slot from the battle
pool (up to `coop_battle_num_slots` = 4 dedicated battle servers), serializes
the encounter into that slot's `coop_battle_<slot>.wsedict` and announces it,
players B-key-join the assigned slot's battle server (port `7241 + 2*slot`),
fight one life, the battle server writes results back into the dict and
signals the campaign server over ENet IPC (slot-tagged), and rejoining
players get casualties + XP applied to their campaign parties. Entry point:
channel-49 `start_battle`/`request_siege` (client). Exit state: casualties
and XP applied, char dicts saved, `encounter_resolved` pushed to that
battle's participants, slot freed.
Local SP-style fights (events 16/17) share only the casualty core; they are
covered in `xp-sync.md`. Siege-specific mission behavior is in `siege.md`.

Module paths below are relative to `wse2work/Native-Coop-master/`; C paths
relative to repo root.

## Sequence diagram

```mermaid
sequenceDiagram
    participant C as Client (initiator)
    participant CS as Campaign Server (module + CoopWSEPlugin COOP_HOST)
    participant BS as Battle Server (module + CoopWSEPlugin COOP_BATTLE)

    Note over BS: at startup: persistent IPC connect to 127.0.0.1:7242,<br/>PKT_BATTLE_HELLO{slot} → campaign DLL maps peer→slot,<br/>publishes $g_coop_battle_slots_online bitmask
    C->>CS: ch49 start_battle (1) / request_siege (26)
    CS->>CS: coop_battle_launch_on_free_slot:<br/>coop_battle_find_free_slot (online mask ∧ not in progress;<br/>none → ch125 battle_rejected (44) param 0),<br/>coop_save_character (all players),<br/>coop_write_battle_data → dict_save coop_battle_{slot}<br/>(enemy parties marked slot_party_coop_battle_slot = slot+1)
    CS->>CS: $g_coop_battle_in_progress_{slot} = 1
    CS->>C: ch125 battle_available (10) to ALL players:<br/>(port 7241+2*slot, is_initiator, enemy party)
    Note over C: initiator: $g_coop_battle_connect_pending, deferred<br/>game-loop trigger connects; others: chooser table row,<br/>B key opens mnu_coop_join_battle
    C->>BS: join (port 7241 + 2*slot)
    BS->>BS: ti_server_player_joined: first join loads slot dict<br/>(coop_on_admin_panel_load); no join menus -- team 1 + own<br/>campaign troop assigned server-side; char load deferred
    C->>BS: ch126 identify (54): acctid lo16/hi16 -- handler only RECORDS<br/>acctid+1 in the wipe-proof troop-slot mirror
    BS->>BS: coop_battle_hydrate_timeout (1 s poll, sole hydrator):<br/>mirror set → coop_battle_player_hydrate(acctid); no identify<br/>after ~5 s → username fallback (acctid 0)
    BS->>BS: spawn gate (slot_player_spawned_this_round +<br/>hydration gate slot_player_join_time == 0),<br/>ti_on_agent_spawn: coop_equip_player_agent
    Note over BS: fight -- damage/4, one life,<br/>optional respawn-as-bot
    BS->>BS: coop_battle_check_round_end (A9: reserves,<br/>10s floor, 5s settle) → $g_round_ended=1
    BS->>C: ch127 return_to_campaign (55) to every player<br/>(also from the retreat arm)
    BS->>BS: coop_copy_parties_to_file_mp → dict_save<br/>(casualties, battle_result, xp_rand, player strengths,<br/>acctids, per-player kill-XP deltas) then $coop_battle_started = -1
    BS->>BS: kick all players
    Note over BS: DLL poll thread sees -1 edge
    BS->>CS: ENet IPC (7242) PKT_BATTLE_END + battle_end_signal_t{slot,...}
    CS->>CS: coop_on_ipc_packet: $g_coop_battle_ended_{slot} = 1<br/>(also set on IPC peer loss for an in-progress slot → abort path)
    C->>CS: auto-rejoin: ev 55 set $g_coop_return_to_campaign, the ASI<br/>arms the auto-join driver at the campaign address<br/>(manual browser rejoin still works)
    CS->>CS: multiplayer_campaign_player_joined: stamp hydration countdown,<br/>re-announce still-open (ended==0) slots via ev 10 (chooser rebuild)
    C->>CS: ch49 identify (8) — or 5 s timeout fallback
    CS->>CS: coop_player_hydrate: char load, then for EVERY slot with<br/>in_progress or ended set → coop_apply_battle_results<br/>(Phase 1 once per battle: victory pool + outcome-independent<br/>kill-XP credit) + per-player Phase 2 XP from char dict
    CS->>C: ch125 encounter_resolved (9) — participants only —<br/>char/inv/party pushes; slot freed (+ ev 45 battle_slot_closed)
```

## Code anchors

Line numbers verified 2026-09-21 against the current tree (`7161f85`).

| # | Step | File | Line | Symbol |
|---|------|------|------|--------|
| 1 | Client battle request arm (ch49 ev 1) | `module_coop_scripts.py` | 12895 | `multiplayer_campaign_client_events` (def `:12881`) → `coop_ev_cli_start_battle` (def `:11704`) |
| 2 | Siege request arm (ch49 ev 26) | `module_coop_scripts.py` | 12898 | same dispatcher → `coop_ev_cli_request_siege` (def `:11728`) |
| 3 | Shared launch tail: slot alloc + save-all + dict write + mark + announce | `module_coop_scripts.py` | 11646–11702 | `coop_battle_launch_on_free_slot` (field + siege callers `:11712`, `:11736`) |
| 4 | — free-slot pick (online mask ∧ not in progress; −1 = pool full → ch125 ev 44 param 0) | `module_coop_scripts.py` | 13283 | `coop_battle_find_free_slot`, `$g_coop_battle_slots_online` |
| 5 | Encounter serialization to the slot dict (scene/advantage/garrison/stacks; every rostered party marked `slot_party_coop_battle_slot = slot+1` at `:13373`, inside `coop_battle_dict_write_roster_party` def `:13326`) | `module_coop_scripts.py` | 13381 | `coop_write_battle_data` |
| 6 | Per-slot dict name (`coop_battle_<slot>.wsedict`) | `module_coop_scripts.py` | 13121 | `coop_battle_slot_dict_name` |
| 7 | battle_available broadcast (ch125 ev 10, 4-int: port `7241+2*slot`, is_initiator, enemy party) | `module_coop_scripts.py` | 11687–11699 | inside launch tail |
| 8 | Client recv ev 10: chooser row + initiator connect flag | `module_coop_scripts.py` | 11611 | `coop_ev_srv_battle_available` → `coop_battle_chooser_set` (`:11636`, def `:13213`), `$g_coop_battle_connect_pending` (`:11627`) |
| 9 | B-key chooser menu open | `module_simple_triggers.py` | 209–214 | `$g_coop_battle_available` → `mnu_coop_join_battle` (`module_game_menus.py`) |
| 10 | Deferred auto-connect trigger (game-loop context, not recv handler; `s57` = ASI-mirrored join password) | `module_simple_triggers.py` | 216–226 | `$g_coop_battle_connect_pending` → `multiplayer_connect_to_server` |
| 11 | Battle server slot identity: `COOP_BATTLE_SLOT` env → `$coop_battle_slot` (raw-written each poll) | `src/coop_campaign.c` | 80, 285–289 | `g_battle_slot` |
| 12 | Battle server IPC: persistent connect + HELLO{slot} on connect | `src/coop_campaign.c` | 449–452 (send), 589 (receive) | `PKT_BATTLE_HELLO` (`src/battle_ipc.h`) |
| 13 | Battle server: join handler — no join menus (`ebd4f64`): team 1 + own campaign troop assigned, `slot_player_coop_selected_troop` stamped, hydration window stamped; char load deferred | `module_coop_mission_templates.py` | 568–622 (field), 4747 (siege) | `ti_server_player_joined` |
| 14 | — dict load on first join | `module_coop_mission_templates.py` | 578 | `script_coop_on_admin_panel_load` (def `module_coop_scripts.py:85`) |
| 15 | — identify + hydration: the client sends ch126 ev 54 (lo16/hi16 acctid; `-1` ASI sentinel = no Steam → send acctid 0 at once); the server arm only RECORDS acctid+1 in the wipe-proof troop-slot mirror; the 1 s hydrate poll is the SOLE hydrator (mirror → `coop_battle_player_hydrate(acctid)`; no mirror after ~5 s → username fallback), re-runs after every `startMission` wipe; mirror cleared on exit | `module_coop_scripts.py` / `module_coop_mission_templates.py` | 1807–1834, 9224 / 94, 136, 188 | ch126 identify arm (`slot_troop_coop_battle_ident`), `coop_battle_player_hydrate`; `coop_battle_identify_send`, `coop_battle_hydrate_timeout`, `coop_battle_clear_ident_on_exit` |
| 16 | One-life spawn gate + hydration spawn gate (`slot_player_join_time == 0`) | `module_coop_mission_templates.py` | 723–746 (field), 4949–4972 (siege) | `slot_player_spawned_this_round`, `slot_player_join_time` |
| 17 | Bot reinforcement spawn | `module_coop_mission_templates.py` | 892 (field), 5097 (siege) | `script_coop_find_bot_troop_for_spawn` (def `module_coop_scripts.py:3881`) |
| 18 | Agent spawn: formation + campaign equip | `module_coop_mission_templates.py` | 1023, 1043 | `script_coop_spawn_formation` (def `module_coop_scripts.py:3562`), `script_coop_equip_player_agent` (def `module_coop_scripts.py:3126`) |
| 19 | Player damage quartered | `module_coop_mission_templates.py` | 301 (def), 554, 4734 (usage) | `coop_server_reduce_damage` |
| 20 | Death: respawn-as-bot (optional) | `module_coop_mission_templates.py` | 229 | `coop_respawn_as_bot` |
| 21 | Per-death casualty recording | `module_coop_mission_templates.py` | 1071 | `script_coop_server_on_agent_killed_or_wounded_common` (def `module_coop_scripts.py:3972`) |
| 22 | Round-end check (A9: reserves, 10s floor, 5s settle; both templates); on round end the server pushes ch127 ev 55 `return_to_campaign` to every player (`module_coop_scripts.py:4797`; retreat arm `:1801`) | `module_coop_mission_templates.py` | 1104 (field), 5386 (siege) | `script_coop_battle_check_round_end` (def `module_coop_scripts.py:4749`) |
| 23 | Dedicated end: results write + kick all | `module_coop_mission_templates.py` | 1113–1135 (field), 5418–5435 (siege) | `script_coop_copy_parties_to_file_mp` (def `module_coop_scripts.py:4806`, `$coop_battle_started = -1` after `dict_save` at `:4978`) |
| 24 | — per-player name/acctid/strength/kill-XP + casualty keys written | `module_coop_scripts.py` | 4918, 4929, 4940, 4959 | `@battle_player_{i}_name/acctid/strength/kill_xp`, `coop_battle_dict_put_stack_cas` (def `:6764`) |
| 25 | DLL: poll thread sees `$coop_battle_started == -1` | `src/coop_campaign.c` | 456 (def), 490–492 (-1 edge check) | `battle_poll_thread_func` |
| 26 | DLL: collect + IPC END (slot-tagged) | `src/coop_campaign.c` | 390 | `battle_collect_and_save`, `battle_end_signal_t` (`src/battle_ipc.h`) |
| 27 | Campaign DLL: HELLO → peer/slot map + online mask; END → per-slot ended flag; peer loss for an in-progress slot also sets the ended flag | `src/coop_campaign.c` | 586 (HELLO `:589`, END `:601`), 557, 570–583 | `coop_on_ipc_packet` sets `$g_coop_battle_ended_<slot>`; `update_slots_online_mask`; `coop_on_ipc_event` |
| 28 | Rejoin: apply pass loops ALL slots with in_progress or ended set — runs at HYDRATION (ch49 identify ev 8 or 5 s countdown fallback), not at join | `module_coop_scripts.py` | 9349–9356 | `coop_player_hydrate` (def `:9321`); identify arm `:12979–12988`; fallback `module_simple_triggers.py:4703–4724` |
| 29 | Join-time ev-10 re-announce of still-open slots (chooser rebuild; runs at join, BEFORE the hydrate-time apply loop — an `ended==0` filter keeps consumed/finished slots from being re-advertised; is_initiator=0) | `module_coop_scripts.py` | 9535–9558 | inside `multiplayer_campaign_player_joined` (def `:9497`) |
| 30 | Results core (once per battle, gated on `end_mp`; participant-gated via `@battle_player_{i}_name` at `:13879–13892`, ev 9 to the joiner only) | `module_coop_scripts.py` | 13861 | `coop_apply_battle_results` |
| 31 | — A7 victory consequences (gold/renown/prisoners/political) + Phase 1 XP pool (victory-gated, call at `:14177`) | `module_coop_scripts.py` | 13658 | `coop_victory_consequences_dedicated`, `coop_compute_sp_xp_pool_from_dict` (def `:14344`) |
| 32 | — ally casualties via casualty core; beaten-party release + marker clear | `module_coop_scripts.py` | 7711, 14114–14140, 14213–14248 | `coop_apply_player_stack_casualty` (single owner of loss rules) |
| 33 | — abort arm: ended without `end_mp` (battle server lost) → release parties, `abandoned`, slot freed, ev 45 broadcast + ev 44 param 1 to the joiner | `module_coop_scripts.py` | 14286–14330 | `coop_battle_broadcast_slot_closed` (def `:13271`) |
| 34 | Phase 1 kill-XP credit (outcome-independent, `e28eacf`): `@battle_player_{i}_kill_xp` added onto `@char_pending_hero_xp` — baseline snapshot at battle-server hydrate `:9245–9253`, delta at results write `:4950–4959` | `module_coop_scripts.py` | 14061–14088 | `slot_troop_coop_battle_xp_base` |
| 35 | Phase 2 per-player pending XP at hydration | `module_coop_scripts.py` | 9380 | `coop_apply_xp_shares` (def `:14382`, inside `coop_player_hydrate`) |
| 36 | Campaign join trigger | `module_simple_triggers.py` | 4614 | `ti_server_player_joined` → `multiplayer_campaign_player_joined` |
| 37 | Startup slot + marker sweep (post-load: all dicts → `none`, flags cleared, stale `slot_party_coop_battle_slot` markers swept — mid-battle autosave restart must not leave parties un-encounterable) | `module_simple_triggers.py` | 153–181 | startup block |
| 38 | Third-party encounter bounce off marked parties (both encounter params tested) | `module_scripts.py` | 2979–2983 | `game_event_party_encounter` |

## State & events

- **Dict files:** `coop_battle_<slot>.wsedict`, one per pool slot 0–3
  (`coop_battle_slot_dict_name`; the battle server derives its own name
  from `$coop_battle_slot`) — keys: `@battle_state` (see states
  below), `@battle_host_party`, `@battle_host_player_name`, `@map_type`
  (battle type), `@map_scn/castle/street/party_id`, `@map_time/cloud/haze/rain`,
  `@battle_adv`, `@tm0_fac/@tm1_fac/@tm1_name`, `@p_garrison`,
  `@p_castle_lord`, `@p_garrison_banner`, `@srvr_set0..11`,
  `@num_parties_enemy/ally`, `@p_enemy{i}_partyid/numstacks/{j}_trp/{j}_num`
  (same for ally), `@num_bots_team_1/2`, `@cls{i}_name`; post-battle:
  `@p_enemy{i}_numstacks_cas` + per-stack cas keys (via
  `coop_battle_dict_put_stack_cas`), `@battle_result`, `@battle_xp_rand`,
  `@battle_num_players`, `@battle_player_{i}_name/acctid/strength/kill_xp`.
- **Char dicts:** `coop_char_sid_<acctid>.wsedict` (Steam-identified) /
  `coop_char_<name>.wsedict` (acctid 0) — naming owned by the
  `coop_char_store_dict_name[_raw]` key-builders. Phase 1 stashes
  `@char_battle_pending`, `@char_pending_party_xp`, `@char_pending_hero_xp`
  (+ A7's `@char_pending_gold/renown/pris_*`; all preserved across
  concurrent saves by `coop_save_character`, def `:7818`, preserve block
  `:7845–7892`).
- **Globals (per-slot campaign state):** `$g_coop_battle_in_progress_0..3`
  (module-owned), `$g_coop_battle_ended_0..3` (DLL sets on `PKT_BATTLE_END`
  or IPC peer loss for an in-progress slot; module consumes + clears),
  `$g_coop_battle_slots_online` (DLL-owned bitmask of connected battle-server
  IPC peers — slot allocation reads it, so the pool auto-adapts to how many
  instances are up). Client: `$g_coop_battle_available` (any chooser row),
  `$g_coop_battle_requested`/`$g_coop_battle_connect_pending` (initiator
  auto-connect), chooser table `$coop_avail_*`, `s58`/`s59`;
  `$g_coop_return_to_campaign` (set by the ch127 ev 55 arm, read by the
  ASI's modglobals thread to arm the return hop — survives until the
  reconnect it causes wipes it). Battle server:
  `$coop_battle_slot` (raw-written from `COOP_BATTLE_SLOT` env each poll),
  `$coop_battle_started` (0 idle, 1 running, -1 dict-flushed),
  `$g_round_ended`, `$coop_winner_team`, `$coop_alive_team1/2`,
  `$coop_battle_state`; per-player-troop mirrors that survive the
  engine's `startMission` player-slot wipe: `slot_troop_coop_battle_ident`
  (acctid+1), `slot_troop_coop_battle_nodict`, `slot_troop_coop_battle_xp_base`
  (`module_constants.py:1952–1963`). The scalar `$g_coop_battle_in_progress`/
  `$g_coop_battle_ended` from the single-server design are gone.
- **Party marker:** enemy parties carry `slot_party_coop_battle_slot` (=600,
  value slot+1) from dict-write until result apply or abort — the third-party
  encounter bounce keys off it.
- **Battle types (dict `@map_type`):** `module_constants.py:2111–2116`
  (field=1, siege attack/defend=2/3, village=4/5, bandit lair=6).
- **Battle states:** `module_constants.py:2119–2125` — none=0, setup_sp=1,
  setup_mp=2, started=3, **end_mp=4** (gates result apply), end_sp=5,
  abandoned=6.
- **Network events:** ch49: `start_battle`=1, `request_siege`=26,
  `leave_encounter`=0 (`header_common.py`). ch125: `encounter_resolved`=9,
  `battle_available`=10 (port, is_initiator, enemy party),
  `battle_rejected`=44 (param 0 = pool full, param 1 = battle server lost
  mid-battle), `battle_slot_closed`=45 (clears a client chooser row);
  id 14, freed by the dead-`return_to_campaign` removal (audit row 7), was
  later reused by A7 as `char_sync_renown` — that per-value event was
  itself deleted by the net-optimizations packed char-sync (renown now
  travels in `packed_misc`, ev 40 — see `xp-sync.md`), so id 14 is free
  again. ch126 battle events:
  `coop_event_*` (`module_constants.py`), incl. A9's ev 52
  `coop_event_battle_retreat` and ev 54 `coop_event_identify` (`:2189`);
  ch127 ev 53 pushes initiator identity per-join and ev 55
  `coop_event_return_to_campaign` (`:2190`) tells every client the battle
  is over (auto-return hop, `e7eb400`). ENet IPC (7242) — the only C-layer
  wire since B8 (`a68b8ae`):
  `PKT_BATTLE_HELLO` (0x26, `{uint8 slot}`, sent on every (re)connect of a
  battle server's persistent IPC link so the campaign DLL can map
  peer→slot) + `PKT_BATTLE_END` (0x27) with `battle_end_signal_t` (leading
  `uint8 slot` identifies which slot finished; `src/battle_ipc.h`); the
  type byte alone determines wire shape; battle server connects to
  `127.0.0.1:7242` only (`src/shared/battle_net.c`). The campaign IPC
  `ENetHost` has ONE servicing thread, `ipc_thread_func` (60 Hz) —
  `enet_host_service` mutates peer/ack lists with no internal locking,
  and a second poller from the frameMove hook double-freed ack blocks
  (`STATUS_HEAP_CORRUPTION`, three WER dumps); fixed `7afc290`,
  runtime-verified 2026-09-07 (second client join survives).
- **Ports:** slot s: LAN `7241 + 2*s` (`coop_battle_port_base`,
  `module_constants.py:2129–2130`). The configs carry no Steam port —
  `set_steam_port` is a no-op on the WSE2 dedicated exe (no GameServer
  init) and was removed.

## Invariants

- `coop_apply_player_stack_casualty` (`module_coop_scripts.py:7711`) is the
  single owner of player-party battle-loss rules: MP-profile remap, clamp to
  what the party has, surgery saves, wound survivors, heroes never removed,
  `p_player_casualties` accounting. Both callers (dedicated ally loop,
  local-fight arm) must go through it.
- Result application runs **once per battle**: gated on
  `@battle_state == end_mp` and the state is cleared before applying. The
  apply pass loops **all** slots with in_progress or ended set
  (`:9349–9356`) — never just one battle — and runs at HYDRATION
  (`coop_player_hydrate`: ch49 identify or the 5 s countdown fallback),
  post-load, so casualties and spoils only ever touch a hydrated character.
- ev 9 `encounter_resolved` is **participant-gated**: pushed only if the
  joining player's name appears in that battle's `@battle_player_{i}_name`
  list — non-participants never receive a resolve for someone else's battle.
- The join-time ev-10 re-announce (`:9535–9558`) runs at join, BEFORE the
  hydrate-time apply loop; its `ended==0` filter keeps consumed/finished
  slots from being re-advertised. The chooser table is client-side and dies
  with every connection, so only this push can rebuild it on rejoin.
- On the battle server the ch126 identify arm never hydrates: it only
  records acctid+1 in `slot_troop_coop_battle_ident` on the player's
  campaign troop, and `coop_battle_hydrate_timeout` is the sole hydrator.
  Player slots are wiped by every `startMission` (scene restart) and the
  client's identify latch is one-send-per-connection, so a hydrate keyed
  from the event itself lost the acctid on the first wipe and stranded the
  Phase 1 stash in a username-keyed dict (`e7eb400`). The troop-slot
  mirror survives the wipe; `slot_troop_coop_battle_nodict` stops the
  non-idempotent starter-party load branch from running twice.
- Enemy parties resolve via the dict `@p_enemy{i}_partyid`, never via
  `party_get_battle_opponent` — the rejoiner's party is REBUILT and has no
  engine battle association. The `slot_party_coop_battle_slot` marker is set
  at dict-write and must be cleared on every exit path (apply, abort, and
  the post-load startup sweep).
- Slot allocation reads `$g_coop_battle_slots_online` — a slot is usable
  only if its battle server's IPC peer is connected AND it is not in
  progress; a pool miss must answer ch125 ev 44 param 0.
- **Documented behavior:** result application is triggered by
  rejoin-then-hydrate, so a
  finished battle whose participants never rejoin holds its slot
  (in_progress stays set) until the campaign server restarts — the startup
  sweep (anchor 36) then resets every slot and clears stale party markers.
- Phase 1 (pool computation + stash) runs once per battle; Phase 2 (apply
  pending XP from char dict) runs on every hydration and clears the pending
  flags before `coop_save_character` re-reads them from disk (`:14382`).
  Phase 1 stashes for disconnected participants key their char dict via
  `@battle_player_{i}_acctid` (captured at results-write time from the
  troop-slot mirror) through `coop_char_store_dict_name_raw` — participant
  *matching* stays name-based. The kill-XP credit (`:14061–14088`) is a
  second Phase 1 pass, outside the victory gate, additive onto
  `@char_pending_hero_xp`.
- `coop_save_character` must preserve `@char_pending_*` keys it did not
  create — Phase 1 may stash for players who haven't rejoined.
- `$coop_battle_started = -1` must be assigned only **after** `dict_save`
  of the results (`module_coop_scripts.py:4978`, called from the end
  handlers `module_coop_mission_templates.py:1113–1135` / `:5418–5435`);
  the DLL treats the -1 edge as "dict is on disk".
- `pkt_write`/`pkt_read` frame ALL packets (`src/battle_ipc.h` since B8,
  `a68b8ae`): `[0]=type`, payload at `+PKT_HDR_SIZE`.
- The DLL never calls engine functions from the poll thread — raw reads with
  SEH guard (`src/coop_campaign.c`, battle poll thread).

## Audit: ours vs. native

| # | Behavior | Ours (anchor) | Native ground truth (evidence) | Verdict |
|---|----------|---------------|--------------------------------|---------|
| 1 | Player-party casualty math: surgery re-roll saves a dead unit as wounded at **`P = 0.25 + 0.04 × surgery`** (`:wound_pct = 25 + skl×4`, capped 100); wounded survive; player heroes never removed; enemy heroes wounded 40–70 HP loss. Fixed in `50f4ac1`, runtime-verified 2026-07-10 | `module_coop_scripts.py:7072–7077` (@ `fc1f204`; current location `:7745–7750`) | RE'd (`patches/Warband/findings.md` "Native kill-vs-wound (surgery) rules", resolver `0x4BB310`): native real-battle/encounter path saves each removed unit as wounded at **`P = 0.25 + 0.04 × surgery`** (constants `0.25`@0x7C1610, `0.04`@0x7C5408), and forces heroes to wounded (`tf_hero` at 0x4BC8EB). Coop now matches base, slope, and the hero rule. Separately, native's bulk `inflict_casualties_to_party_group` opcode (0x54FF80) uses a flat 35% wound / no surgery — coop does not route through it, so that rule is not the relevant baseline. | OK |
| 2 | Post-battle XP pool `(level+10)^2/10` per casualty, cap 40000, × `@battle_xp_rand`/100; split by per-player strength; host share -> `party_add_xp`, joiner share -> hero only. Since `e28eacf` each player's in-mission kill-XP delta is additionally credited as a personal hero share, win or lose (win variant runtime-verified 2026-08-29: `kill_xp=134` → `+134 hero XP`; loss variant + battle-server save-cap regression still open) | `module_coop_scripts.py:14344–14380` (pool), `:13970–14042` (strength split + stash), `:14061–14088` (kill-XP credit), `:14382–14420` (apply) | Native `party_give_xp_and_gold` (`module_scripts.py:15360–15410`) uses the same basis (`p_total_enemy_casualties`, victory call site `module_game_menus.py:4674`) and same per-stack formula + 40000 cap + rand 50–99 roll, and native SP also pays per-kill mission XP during the fight on top of the pool. Deltas: native scales by `$g_strength_contribution_of_player` **before** the cap, coop caps the raw pool before the strength split; coop's shared roll is 50–100 (`store_random_in_range 50,101` at `:4907`) vs native 50–99. Both are minor and the multi-player split is the intended design. **Native also pays gold (loot share × rand, split among heroes) — see row 6 (A7 applier pays hero gold shares).** | OK |
| 3 | Battle end via shared `coop_battle_check_round_end` (A9, merged `632466c`, runtime-verified 2026-07-25): effective strength = alive agents + temp-party reserves, 10s mission-time floor, 5s settle window since the last agent event (`$coop_last_agent_event_time`), called from 1s triggers in BOTH field-battle and siege templates (old inline instant-wipe checks deleted). Initiator retreat: Esc-menu button (gated on the battle-server-pushed `$g_coop_battle_is_initiator`, ch127 ev 53), request ch126 ev 52 server-verified against `@battle_host_player_name`, ends the round with result 0 (no XP pool). XP pool is victory-gated (`@battle_result == 1`). | `module_coop_scripts.py` `coop_battle_check_round_end`; `module_coop_mission_templates.py` 1s triggers | Native `common_battle_check_victory_condition` (`module_mission_templates.py:889–905`): mission time ≥ 10s + `all_enemies_defeated(5)` + `neg|main_hero_fallen`. RE'd (`patches/Warband/findings.md`, helper `0x00547FE0`): the opcode's parameter is a settle delay since the last agent status change, and it returns FALSE with no local player agent, so it cannot run server-side — the module-side reserve-aware recount mirrors its semantics. Retreat mirrors native's Tab-retreat (casualties applied, no rewards). Delivery caveat fixed en route: ev 126 client->server was dropped by the module's own `game_receive_network_message` client-events gate on dedicated servers (`ea60c7e`); engine RE confirmed no engine-side bound (7-bit wire id, `receiveEvent` 0x004971D0). Post-round the server also pushes ch127 ev 55 `return_to_campaign` (`e7eb400`) so clients rejoin the campaign server without a browser trip — LAN auto-return verified 2026-08-29; the retreat-arm and Steam-tunnel-joiner variants are still open. | OK (A9 merged `632466c`, runtime smoke 2026-07-25) |
| 4 | Spawn: no join menus — the server assigns team 1 + the player's own campaign troop at join (`ebd4f64`: team/troop chooser presentations deleted, welcome screen skipped; field gates 1+3 passed 2026-09-07, siege variant open); fixed entry-point table per battle type + optional line formation; campaign equip via `coop_equip_player_agent` | `module_coop_mission_templates.py:476–550` (entries), `:568–622` (join), `:723–746` (spawn gate), `:831–946` (bot spawn), `:998–1049` (agent spawn) | Native `lead_charge` uses `mtef_attackers`/`mtef_defenders` team entry flags and engine-standard entry points (`module_mission_templates.py:2206–2213`). Coop's explicit per-battle-type entries + `coop_spawn_formation` are an intentional, admin-panel-configurable MP feature (ch126 `coop_event_spawn_formation`). | OK |
| 5 | One life via spawn gate; death -> optional bot control; all players kicked at battle end | `module_coop_mission_templates.py:723–746`, `:229–300`, `:1128–1131` | Parked — see Open questions. | PARKED |
| 6 | Encounter resolution: `@battle_result` -> `$g_battle_result` + routed counts, `encounter_resolved` push; the A7 consequence applier pays hero gold shares, renown (enemy strength staged in the dict at write time, value computed at apply — `593fe52`), capacity-capped prisoners, and the political/quest hook on rejoin, dedicated + local paths. The battle-disengage half was FIXED + runtime-verified 2026-07-11 (`f85c30e` + `d865990`): the apply tail releases every dict enemy party from the stale battle association, and on victory clears + `remove_party`s non-center parties, then disengages the (rebuilt) player party. Key mechanism: the rejoining player gets a REBUILT party, so `party_get_battle_opponent` finds nothing — enemy parties must be resolved via the dict `@p_enemy{i}_partyid` | `module_coop_scripts.py` `coop_apply_battle_results` tail | Native victory chain (`module_game_menus.py:4664–4690`): `party_calculate_loot` + loot screen, `party_give_xp_and_gold` (XP **and** hero gold shares), `battle_political_consequences`, `event_player_defeated_enemy_party`, `clear_party_group`. Coop now mirrors it minus item loot and defeat-path consequences (deliberately deferred — `docs/DEFERRED.md`). | OK (A7 merged `4ba5786`, runtime smoke 2026-07-24) |
| 7 | ch125 event 14 `return_to_campaign` constant deleted (`1dc8fec`) — it was never sent or handled; project-state row corrected (ID 14 marked free). Smoke passed 2026-07-11 | `header_common.py` (ID 14 free note) | Confirmed by exhaustive grep of module + C source before removal | OK |
| 8 | Dead `s57` reconnect write deleted from the ASI (`fd0e088`) — nothing consumed it and vanilla scripts clobber `s57` as a scratch register. The live `s59` battle-server-IP write remains. Smoke passed 2026-07-11 | `src/asi/coop.c` `s59_writer_thread` | Confirmed by grep: no consumer in module or src before removal | OK |
| 9 | Legacy `coop_battle.c` orchestration excised (`fd0e088`): file deleted along with the WSELoaderServer spawn, `battle_result.txt` file IPC, Attack-click launch call-site patch, `PKT_BATTLE_START`/`RESULT`, and the party-slot 108–110 result delivery. One orchestration path remains: the ENet-IPC dedicated-server pipeline. Kept live at the time: campaign-ENet INVITE/ACCEPT/DECLINE/RESUME handshake + tick pause and the initiate/cleanup_battle hooks — since deleted in B8 (`a68b8ae`, verified inert); the surviving C layer is the COOP_BATTLE poll thread + `PKT_BATTLE_END` (IPC, 0x27 since `0153ecf`). Smoke 2026-07-11: full chain verified in logs (`battle_started -> -1` → `PKT_BATTLE_END` → `$g_coop_battle_ended = 1` → results applied) | `src/coop_campaign.c`; `src/battle_ipc.h` | The candidate-10 `coop_net`/`battle_net` twin question was closed by deletion in B8 (`a68b8ae`): `coop_net.c` is gone, `battle_net.c` is the sole ENet wrapper | OK |

## Fix list

| # | From audit row | What diverges | Suggested owner/layer |
|---|----------------|---------------|------------------------|
| 0 | 1 | ~~Surgery save omits native's 0.25 base~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10: `coop_apply_player_stack_casualty` rolls `25 + skl×4` percent, capped 100. | `module_coop_scripts.py:7072–7077` (current location `:7745–7750`) |
| 1 | 7 | ~~Dead ev 14 `return_to_campaign`~~ **Done** (`1dc8fec`, smoke 2026-07-11): constant removed, project-state row corrected. | `header_common.py` + workbench project-state doc |
| 2 | 8 | ~~Dead `s57` reconnect write~~ **Done** (`fd0e088`, smoke 2026-07-11): write deleted; auto-rejoin, if ever wanted, gets its own design. | `src/asi/coop.c` |
| 3 | 3 | ~~Round-end reserve-blind and instant; no retreat path~~ **Done** (A9, merged `632466c`, runtime smoke 2026-07-25): shared `coop_battle_check_round_end` (reserves + 10s floor + 5s settle) in both templates; victory-gated XP pool; initiator retreat (ch126 ev 52 / ch127 ev 53). Deferred: legacy `coop_event_end_battle` admin check, no retreat fallback on initiator disconnect (`docs/DEFERRED.md`). | `module_coop_scripts.py` + `module_coop_mission_templates.py` |
| 4 | 6 | ~~Victory pays XP only~~ **Done** (A7, merged `4ba5786`, runtime smoke 2026-07-24): hero gold shares, renown, capacity-capped prisoners, and the political/quest hook now applied on rejoin (dedicated + local). Item loot and defeat-path consequences deliberately deferred (`docs/DEFERRED.md`). ~~Urgent sub-piece: server-side battle disengage + beaten-party removal~~ **Done** (`f85c30e` + `d865990`, runtime-verified 2026-07-11) — resolved via dict party ids; the ev-17 local arm got the same `remove_party` treatment (`d82d879`). | `module_coop_scripts.py` BATTLE PIPELINE section |
| 5 | 9 | ~~Legacy `coop_battle.c` orchestration~~ **Done** (`fd0e088`, smoke 2026-07-11): excised (see audit row 9). Candidate 10 (`coop_net`/`battle_net` merge) remains deferred. | `src/coop_campaign.c` + `src/battle_ipc.h` |

## Open questions

- Audit row 5 (engine per-player mission state after the end-of-battle mass
  kick): parked — impact is bounded because the battle server immediately
  restarts its mission and clients fully reconnect to the campaign server;
  the wave-2 runtime smoke test exercises exactly this path and is the
  cheaper verification.
- Runtime gates still open for code that is merged and described above
  (ledger: `docs/NEXT_SESSION.md` battle-XP + join-menu-skip sections):
  `e7eb400` retreat-path auto-return, no-Steam (acctid 0) round trip, the
  siege template variant of identify/auto-return, Steam-tunnel joiner
  auto-return; `e28eacf` kill-XP loss variant and the battle-server
  `@char_xp` save-cap regression; `ebd4f64` siege join, Esc-menu entries,
  pre-spawn wait feel. Until they pass, those paths count as
  implemented-but-unverified.
- Plan 3/4 (relation and quest sync, 2026-09-19/20) did not touch this
  flow: `battle_political_consequences` still runs outside any player
  context on both appliers (`module_coop_scripts.py:13689`, `:12436`),
  and native's post-fight lord relation gains are not applied for the
  participants — ledgered as the first "world reacts per player" to-do in
  `docs/NEXT_SESSION.md`.

## Related docs

Workbench documents (not part of the public export — see the citation
note in `README.md`):

- `docs/archive/BATTLE_RESULTS_PIPELINE_AUDIT.md` — earlier results-pipeline audit.
- `docs/archive/2026-03-22-warband-coop-campaign-sync-design.md`
  — original campaign-sync design.
- `patches/WarbandDedicated/kb.h` / `findings.md` — campaign-server binary RE.
