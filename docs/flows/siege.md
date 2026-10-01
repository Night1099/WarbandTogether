# Flow: Siege (coop siege battle types + local siege)

**Status:** AUDITED
**Validated against commit:** `7161f85` (docs refresh 2026-09-21: every
line anchor re-verified against the current tree — `module_coop_scripts.py`
scripts past ~7200 moved by +170..+2300, `module_coop_mission_templates.py`
siege template by ~+35; the dedicated-assault sequence no longer connects
to a fixed `{s59}:7241` — the ev-10 reply carries the slot port
(multiserver, `0b2500a`); the local-siege launcher's ASI request is
`$g_coop_asi_local_mission = coop_asi_local_mission_battle` (`294824b`);
no verdict changed. Still open on the siege template: the join-menu-skip
siege gate (`ebd4f64` gate 2) and the identify/auto-return siege gate
(`e7eb400` gate 6). Prior stamp `2923381`: anchors re-verified 2026-08-30;
`ce0e287`: steamid persistence, runtime-verified 2026-08-23 — the
`@char_siege_center` stash lives in the sid-or-username-keyed char dict;
`0b2500a`: A8 merge)

## Scope

How a coop player assaults a town/castle: the **dedicated siege** (battle
server runs the `coop_siege` mission) and the **local siege** (initiating
client fights an SP-style wall assault against AI, then reports the result).
Entry points: the coop center menu options `coop_center_assault` /
`coop_center_assault_local`. Exit state: garrison casualties applied (both
paths); on a win, both paths run the A7 victory applier plus the shared
capture-consequences script (`coop_siege_capture_consequences`).
The shared serialization/IPC/result tail is documented in
`battle-pipeline.md` — this dossier covers only the siege delta.

Module paths relative to `wse2work/Native-Coop-master/`; C paths relative to
repo root.

## Sequence diagram

```mermaid
sequenceDiagram
    participant C as Client (assaulting player)
    participant CS as Campaign Server
    participant BS as Battle Server

    rect rgb(235,235,245)
    note over C,BS: Dedicated siege
    C->>CS: ch49 request_siege (26) with center party<br/>($g_coop_battle_requested = 1)
    CS->>CS: coop_battle_launch_on_free_slot: free slot, save all chars,<br/>coop_write_battle_data(type=2): scene from center slots,<br/>garrison = center party as enemy0, @p_castle_lord/@p_garrison keys,<br/>attached parties enemy1..N, nearby allied lords ally1..N
    CS->>C: ch125 battle_available (10) to ALL players<br/>(port 7241+2*slot, is_initiator, center party)
    C->>BS: initiator: deferred auto-connect to {s59}:{port};<br/>others: chooser row, B key
    BS->>BS: coop_siege mission (no join menus): belfry/ladder setup,<br/>rounds (walls → street → hall) on listen,<br/>dedicated forced single-round
    BS->>CS: dict + $coop_battle_started=-1 → IPC END<br/>(shared tail, see battle-pipeline.md)
    CS->>CS: apply_battle_results: garrison casualties,<br/>A7 applier (win), then coop_siege_capture_consequences:<br/>capture + prosperity/war damage/renown +5
    end

    rect rgb(235,245,235)
    note over C,CS: Local siege
    C->>CS: ch49 request_siege_local (27) with center party
    CS->>CS: validate town/castle, wall scene from center slots,<br/>stash @char_siege_center in char dict, save char, freeze party
    CS->>C: ch125 start_siege_local (42): wall_scene, with_belfry
    C->>C: coop_client_start_siege_local:<br/>mt_coop_castle_attack_walls_{belfry|ladder},<br/>debrief menu, $g_coop_asi_local_mission = coop_asi_local_mission_battle
    C->>CS: ch49 local_fight_result (17): win/loss, casualties, xp delta
    CS->>CS: win: A7 applier (gold/renown/prisoners/political),<br/>then coop_siege_capture_consequences
    end
```

## Code anchors

| # | Step | File | Line | Symbol |
|---|------|------|------|--------|
| 1 | Dedicated assault menu option | `module_game_menus.py` | 14794–14808 | `coop_center_assault` (sets `$g_coop_battle_requested`, sends ch49 ev 26; the ev-10 reply carries the slot port and the deferred connect trigger joins it — see `battle-pipeline.md` anchors 8/10) |
| 2 | Local assault menu option | `module_game_menus.py` | 14810–14822 | `coop_center_assault_local` (sends ch49 ev 27) |
| 3 | Server arm: request_siege | `module_coop_scripts.py` | 11728–11742 | `coop_ev_cli_request_siege`: save chars, `coop_write_battle_data(type=2)`, battle_available, via shared `coop_battle_launch_on_free_slot` (`:11646–11702`) |
| 4 | Server arm: request_siege_local | `module_coop_scripts.py` | 11758–11800 | wall scene from `slot_town_walls`/`slot_castle_exterior`, `@char_siege_center` stash via `coop_char_siege_center_set` (`:8482`), freeze party, ch125 ev 42 |
| 5 | Client local-siege launcher | `module_coop_scripts.py` | 7663–7701 | `coop_client_start_siege_local` -> `mt_coop_castle_attack_walls_{belfry\|ladder}`, `$g_coop_asi_local_mission` request before `change_screen_mission` |
| 6 | Local siege client missions | `module_mission_templates.py` | 3221, 3298 | `coop_castle_attack_walls_ladder` / `_belfry` |
| 7 | Battle dict siege branch: scenes | `module_coop_scripts.py` | 13413–13424 | town: walls+castle+street slots; castle: exterior (field branch `:13466–13468`) |
| 8 | Battle dict siege branch: garrison keys | `module_coop_scripts.py` | 13488–13506 | `@p_castle_lord`, `@p_garrison` (=0: enemy-party index), `@p_garrison_banner` from town lord |
| 9 | Dict loader battle-type branches | `module_coop_scripts.py` | 85, 112–115, 154–156 | `coop_on_admin_panel_load` (`$coop_battle_type`, `$coop_map_party`) |
| 10 | Battle server siege template | `module_coop_mission_templates.py` | 4656 | `coop_siege` |
| 11 | — siege join/bootstrap, belfry wheel init | `module_coop_mission_templates.py` | 4747 (join, no menus), 4792–4873 | `$coop_use_belfry`, `multiplayer_initialize_belfry_wheel_rotations` |
| 12 | — round progression (listen mode) | `module_coop_mission_templates.py` | 5290–5325 | `$coop_round`, `coop_player_agent_save_items` (:5339), next scene by round (:5315–5319) |
| 13 | — dedicated forced single-round + end | `module_coop_mission_templates.py` | 5293–5297 (gate), 5418–5435 (end handler) | |
| 14 | — belfry placement block | `module_coop_mission_templates.py` | 5562–5563 | `script_coop_move_belfries_to_their_first_entry_point` (def `module_coop_scripts.py:3288`) |
| 15 | — belfry crew assignment | `module_coop_mission_templates.py` | 5622 | `script_cf_coop_siege_assign_men_to_belfry` (def `module_coop_scripts.py:3479`) |
| 16 | Round-type / reserve constants | `module_constants.py` | 2229–2237 | `coop_reserves_hall/street`, `coop_round_*` |
| 17 | Local siege aftermath (event 17 arm) | `module_coop_scripts.py` | 12561–12587 | `coop_char_siege_center_get` + clear; win: `coop_victory_consequences_local` then `coop_siege_capture_consequences` + renown +5 |
| 18 | Dedicated siege result apply (shared) | `module_coop_scripts.py` | def 13861; 14177–14202 | `coop_apply_battle_results` — garrison casualties via `@p_enemy0_partyid` = center party; win: A7 applier first (`:14177`), then `coop_siege_capture_consequences` (`:14202`, captor = initiator via `@battle_host_player_name`, applier fallback) |
| 19 | Shared capture consequences | `module_coop_scripts.py` | 12484–12523 | `coop_siege_capture_consequences`: `party_clear`, `slot_center_last_taken_by_troop`, prosperity −5, war damage 40/20 vs old faction, full `give_center_to_faction` to `fac_player_faction` |

## State & events

- **Dict keys (siege delta):** `@map_type` ∈ {2 attack, 3 defend},
  `@map_scn` (walls), `@map_castle`, `@map_street`, `@map_party_id`
  (besieged center), `@p_castle_lord`/`@p_garrison` (enemy-party indices,
  0 for sieges, -1 for field), `@p_garrison_banner`.
- **Dict key:** `@char_siege_center` in the player's char dict — the
  locally-assaulted center; survives the client's disconnect AND the
  player_no/party reassignment on rejoin (preserved across
  `coop_save_character` rebuilds; helpers `coop_char_siege_center_set/_get`
  `module_coop_scripts.py:8482/:8497`; cleared by ev 16 and ev 17).
- **Slots:** `slot_center_coop_lock_player` — center encounter lock;
  `slot_center_siege_with_belfry` (`:261`) — picks belfry vs ladder variant;
  `slot_town_walls`/`slot_castle_exterior`/`slot_town_castle`/`slot_town_center`
  — scene sources.
- **Globals:** `$coop_round` (siege phase), `$coop_use_belfry`,
  `$belfry_positioned`, `$g_coop_asi_local_mission` (client; kind
  `coop_asi_local_mission_battle` for the local siege — the ASI holds
  gameType 0 for the mission), `$g_coop_battle_requested` (client,
  initiator flag consumed by the ev-10 arm),
  `$g_coop_center_party`/`$g_coop_center_type`/`$g_coop_center_scene`
  (client center-menu state).
- **Round types:** `coop_round_battle`=1, `stop_reinforcing_wall`=2,
  `town_street`=3, `stop_reinforcing_street`=4, `castle_hall`=5
  (`module_constants.py:2233–2237`); reserves: hall 20, street 80
  (`:2229–2230`).
- **Network events:** ch49 `request_siege`=26 (`header_common.py:284`),
  `request_siege_local`=27 (`:287`), `local_fight_result`=17 (`:281`);
  ch125 `battle_available`=10 (`:181`), `start_siege_local`=42 (`:210`).
  Battle types: `module_constants.py:2111–2116`.

## Invariants

- The local-siege target lives in the **per-player char dict**
  (sid- or username-keyed since `ce0e287`; key-builder-owned naming)
  (`@char_siege_center`) because the client disconnects into its local
  mission and rejoins with a NEW player_no and slot-derived party — player
  and party ids identify nothing across that boundary (runtime-proven:
  player 3/party 6 at assault became player 5/party 8 at result). A field
  local fight (ev 16) clears any stale stash so an abandoned siege can't
  be misread as a capture.
- The wall scene must be sent from the server (`:11771–11795`) — center
  party slots are not synced to clients.
- Dedicated siege is single-round by design gate (`:5293–5297`); multi-round
  progression (walls -> street -> hall) exists only in listen mode.
- Local-siege party freeze (`disable_party` `:11787`) must be undone by
  rejoin/`enable_party` (`multiplayer_campaign_player_joined:9497`) or exit
  save (`multiplayer_campaign_player_exit:9578`).
- For sieges the besieged center **is** the serialized enemy party 0;
  garrison casualty application therefore mutates the center party directly
  (`coop_apply_battle_results` via `@p_enemy0_partyid`).

## Audit: ours vs. native

| # | Behavior | Ours (anchor) | Native ground truth (evidence) | Verdict |
|---|----------|---------------|--------------------------------|---------|
| 1 | Siege scene + variant: walls scene from `slot_town_walls`/`slot_castle_exterior`, belfry vs ladder from `slot_center_siege_with_belfry` | `module_coop_scripts.py:13413–13424` (dedicated), `:11771–11778` + `:11791` (local: wall scene + belfry flag sent to the client), `:7689–7696` (client picks the variant) | Identical sources to native: assault menus read `slot_town_walls`/`slot_castle_exterior` (`module_game_menus.py:5455–5457`, `:5815–5820`) and the belfry flag is the same slot native seeds at game start (`module_scripts.py:346–365`). Local-siege missions are literal copies of native `castle_attack_walls_{belfry,ladder}` with only a side-flag swap (`module_mission_templates.py:3212–3221`, `:3291–3298`). | OK |
| 2 | Belfry (dedicated `coop_siege`): pre-positioned at first entry point with `slot_scene_prop_belfry_platform_moved=1`; no push/rotate phase | `module_coop_mission_templates.py:5545–5570` (native trigger commented out at `:5544`), `:5621`; `module_coop_scripts.py:3288` | Native uses `common_siege_init_ai_and_belfry`/`_move_belfry`/`_rotate_belfry`/`_assign_men_to_belfry` (`module_mission_templates.py:980–1002`) — soldiers push the belfry to the wall. Coop deliberately replaces this (native triggers commented out, replacement block inline): belfries start at the wall, movement phase skipped. Intentional MP simplification. | OK |
| 3 | Defender composition: center party as enemy0 (garrison keys point there) plus every party attached to the center serialized as enemy1..N with per-party casualty round-trip via `@p_enemy{i}_partyid`; friendly AI parties within `coop_siege_join_radius` join as ally1..N (placeholder rule until a siege camp exists) | `coop_write_battle_data` roster sections + `script_coop_battle_dict_write_roster_party` | Native battles collect **attached parties** into the enemy side (`party_collect_attachments_to_party` -> `p_collective_enemy`, `module_game_menus.py:6045`, `:4247`). Coop now rosters them per-party (identity preserved for casualty apply-back — a collective party can't round-trip through the dict). Fixed `67239e5..d7955b7`, runtime-verified 2026-07-19 multi-client. Attacker-side filter tightened in A8 (`2845589`, verified 2026-07-25): lord-party whitelist + real-ally relation rule | OK |
| 4 | Multi-round siege (walls -> street -> hall) in listen mode; dedicated forced single-round | `module_coop_mission_templates.py:5290–5325`, `:5293–5297` | Dedicated single-round is documented in-code: "Dedicated siege v1 is single-round: the wall battle decides the siege" (`:5293–5297`). The multi-phase progression is inherited coop-mod (Banner Time) design, a deliberate extension over native's single-scene assault. | OK |
| 5 | Dedicated siege victory: capture fixed in `50f4ac1` (A5, runtime-verified 2026-07-10); A8 (`0b2500a`, runtime-verified 2026-07-25) moved it into the shared capture script and reordered it AFTER the A7 applier — political consequences now read the center's pre-transfer faction (latent A7-era ordering bug fixed) | `module_coop_scripts.py:14177–14202` | Native: successful assault transfers the center, handles lord capture/escape, prisoners, and post-siege menus — A7 applier + A8 capture script now cover the set | OK |
| 6 | Both capture paths run native `castle_taken` consequences via `coop_siege_capture_consequences`: `party_clear`, `slot_center_last_taken_by_troop` (initiator), prosperity −5, renown +5 to every participant, war damage 40/20 vs the old owner, full `give_center_to_faction`; local siege additionally gained the previously-missing A7 applier call (gold/battle renown/garrison prisoners/lord fate/political). Fixed A8 (`8b45f2a..db4a815`, merged `0b2500a`), runtime-verified 2026-07-25 (Bulugha Castle smoke: gold+renown+capture; prisoners confirmed once prisoner_management > 0 — native cap) | `module_coop_scripts.py:12484–12523`, `:12561–12587` | Native `castle_taken` menu (`module_game_menus.py:6569–6636`). Deliberately dropped as N/A in coop: `lift_siege` (no siege-camp state), besieger guard order (no besieger AI), keep-or-give-to-vassal menu (players are not vassals; centers go to `fac_player_faction`). Known cosmetic: local path prints both "has fallen" and "has captured" | OK |
| 7 | Battle types `siege_player_defend` (3), `village_*` (4/5), `bandit_lair` (6) are defined and handled by the dict loader, but nothing ever launches them | `module_constants.py:2113–2116`; only callers pass types 1/2 (`module_coop_scripts.py:11712`, `:11736`) | Confirmed by exhaustive grep: no `coop_write_battle_data` caller uses types 3–6. Group-C resolution (`1dc8fec`): kept as future-feature scaffolding, documented as "defined, not yet launched" here and in project-state — the divergence was the docs overstating them, now corrected | OK |

## Fix list

| # | From audit row | What diverges | Suggested owner/layer |
|---|----------------|---------------|------------------------|
| 1 | 5 | ~~Winning a dedicated siege does not capture the center~~ **Done**: capture in `50f4ac1` (A5); A8 (`0b2500a`) moved it into `coop_siege_capture_consequences`, ordered after the A7 applier. | `module_coop_scripts.py` BATTLE PIPELINE section |
| 2 | 6 | ~~Local-siege capture skips native consequences~~ **Done** (A8, `8b45f2a..db4a815`, merged `0b2500a`, runtime-verified 2026-07-25): shared capture script + A7 applier call on the local path. Residual (DEFERRED.md): local sieges never roster defender attachments; garrison stacks leak through the ev-17 `-2` path. | `module_coop_scripts.py` |
| 3 | 7 | ~~Dead battle types 3–6~~ **Done** (`1dc8fec`): kept as future-feature scaffolding, documented as "defined, not yet launched" (code untouched). Wire launch paths when the features are built. | `module_constants.py` + `module_coop_scripts.py` |
| 4 | 3 | ~~Attached defender parties excluded from the battle roster~~ **Done** (`67239e5..d7955b7`, runtime-verified 2026-07-19): attachments serialized as enemy1..N, proximity AI allies as ally1..N, casualties routed per party, markers on all rostered parties + startup sweep. Attacker-filter refinement **done** (A8 `2845589`, runtime-verified 2026-07-25): `spt_kingdom_hero_party` whitelist + same-faction-or-relation>0 rule; farmer/third-faction parties excluded, allied lords still join. | `module_coop_scripts.py` `coop_write_battle_data` |

## Open questions

None — all audit rows resolved module-side (no engine RE was required for
this flow). Two runtime gates for shared battle-pipeline changes are still
owed on the siege template specifically (ledger `docs/NEXT_SESSION.md`):
the join-menu skip on `coop_siege` (`ebd4f64` gate 2 — the field variant
passed 2026-09-07) and the wipe-proof identify + ch127 ev 55 auto-return
on `coop_siege` (`e7eb400` gate 6 — field gates 1-3 passed 2026-08-29).
The siege template carries the same triggers (`coop_battle_identify_send`,
`coop_battle_hydrate_timeout`, `coop_battle_clear_ident_on_exit` at
`module_coop_mission_templates.py:4736–4738`), so this is a verification
gap, not a known divergence.

## Related docs

- `battle-pipeline.md` — shared serialization, IPC, and result-apply tail.

Workbench documents (not part of the public export — see the citation
note in `README.md`):

- `docs/plans/siege-coop-plan.md` — earlier siege planning notes.
- `docs/archive/2026-03-23-warband-coop-party-creation-design.md`
  — party-creation design notes.
