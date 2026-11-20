# Flow: Siege (coop siege battle types + local siege)

**Status:** AUDITED
**Source anchors audited at** `f2a639e` (not runtime-validated; 2026-11-18: every
anchor re-verified; both siege requests now require the requester within
`coop_tavern_transaction_range` of the center (`31cffdc`); the menu options
moved into the shared `coop_center_siege_options` helper (also offered on
the forbidden-entry locked menu, `f3ac58a`); capture frees the center's
player captives first and a total local-siege loss is a castle captivity
(captivity); no verdict changed. **Validated against commit:** `7161f85` (2026-09-21: slot
port via ev 10, `0b2500a`; ASI local-mission request, `294824b`).
Still open on the siege template: join-menu skip (`ebd4f64` gate 2),
identify/auto-return (`e7eb400` gate 6). Prior `2923381`: 2026-08-30;
`ce0e287`: steamid persistence, runtime-verified 2026-08-23 — the
`@char_siege_center` stash lives in the sid-or-username-keyed char dict;
`0b2500a`: A8 merge)

## Scope

How a coop player assaults a town/castle: the **dedicated siege** (battle
server runs the `coop_siege` mission) and the **local siege** (initiating
client fights an SP-style wall assault against AI, then reports the result).
Entry points: `coop_center_assault` / `coop_center_assault_local` (shared
`coop_center_siege_options`). Exit state: garrison casualties applied (both
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
    CS->>CS: requester within coop_tavern_transaction_range (else ev 44);<br/>coop_battle_launch_on_free_slot: free slot, save all chars,<br/>coop_write_battle_data(type=2): scene from center slots,<br/>garrison = center party as enemy0, @p_castle_lord/@p_garrison keys,<br/>attached parties enemy1..N, nearby allied lords ally1..N
    CS->>C: ch125 battle_available (10) to ALL players<br/>(port 7241+2*slot, is_initiator, center party)
    C->>BS: initiator: deferred auto-connect to {s59}:{port};<br/>others: chooser row, B key
    BS->>BS: coop_siege mission (no join menus): belfry/ladder setup,<br/>rounds (walls → street → hall) on listen,<br/>dedicated forced single-round
    BS->>CS: dict + $coop_battle_started=-1 → IPC END<br/>(shared tail, see battle-pipeline.md)
    CS->>CS: apply_battle_results: garrison casualties,<br/>A7 applier (win), then coop_siege_capture_consequences:<br/>capture + prosperity/war damage/renown +5
    end

    rect rgb(235,245,235)
    note over C,CS: Local siege
    C->>CS: ch49 request_siege_local (27) with center party
    CS->>CS: validate town/castle + requester in range, wall scene from center slots,<br/>stash @char_siege_center in char dict, save char, freeze party
    CS->>C: ch125 start_siege_local (42): wall_scene, with_belfry
    C->>C: coop_client_start_siege_local:<br/>mt_coop_castle_attack_walls_{belfry|ladder},<br/>debrief menu, $g_coop_asi_local_mission = coop_asi_local_mission_battle
    C->>CS: ch49 local_fight_result (17): win/loss, casualties, xp delta
    CS->>CS: win: A7 applier (gold/renown/prisoners/political),<br/>then coop_siege_capture_consequences;<br/>loss (-1, every troop fell): coop_player_defeat, captor = center (castle captivity)
    end
```

## Code anchors

| # | Step | File | Line | Symbol |
|---|------|------|------|--------|
| 1 | Dedicated assault menu option | `module_game_menus.py` | 43–54 (helper `coop_center_siege_options` `:41`, used by `coop_center_encounter` `:14960` and the forbidden-entry `coop_center_locked` `:15112`) | `coop_center_assault` (sets `$g_coop_battle_requested`, sends ch49 ev 26; the ev-10 reply carries the slot port and the deferred connect trigger joins it — see `battle-pipeline.md` anchors 8/10) |
| 2 | Local assault menu option | `module_game_menus.py` | 56–65 | `coop_center_assault_local` (sends ch49 ev 27) |
| 3 | Server arm: request_siege | `module_coop_scripts.py` | 14513–14530 | `coop_ev_cli_request_siege`: requester within `coop_tavern_transaction_range` of the center (else ev 44), then save chars, `coop_write_battle_data(type=2)`, battle_available, via shared `coop_battle_launch_on_free_slot` (`:14431–14485`) |
| 4 | Server arm: request_siege_local | `module_coop_scripts.py` | 14547–14592 | same range check; wall scene from `slot_town_walls`/`slot_castle_exterior`, `@char_siege_center` stash via `coop_char_siege_center_set` (`:8744`), freeze party, ch125 ev 42 |
| 5 | Client local-siege launcher | `module_coop_scripts.py` | 7772–7814 | `coop_client_start_siege_local` -> `mt_coop_castle_attack_walls_{belfry\|ladder}`, `$g_coop_asi_local_mission` request before `change_screen_mission` |
| 6 | Local siege client missions | `module_mission_templates.py` | 3232, 3320 | `coop_castle_attack_walls_ladder` / `_belfry` |
| 7 | Battle dict siege branch: scenes | `module_coop_scripts.py` | 16705–16720 | town: walls+castle+street slots; castle: exterior (field branch `:16762–16764`) |
| 8 | Battle dict siege branch: garrison keys | `module_coop_scripts.py` | 16787–16803 | `@p_castle_lord`, `@p_garrison` (=0: enemy-party index), `@p_garrison_banner` from town lord |
| 9 | Dict loader battle-type branches | `module_coop_scripts.py` | 85, 112–115, 154–156 | `coop_on_admin_panel_load` (`$coop_battle_type`, `$coop_map_party`) |
| 10 | Battle server siege template | `module_coop_mission_templates.py` | 4638 | `coop_siege` |
| 11 | — siege join/bootstrap, belfry wheel init | `module_coop_mission_templates.py` | 4729 (join, no menus), 4774–4855 | `$coop_use_belfry`, `multiplayer_initialize_belfry_wheel_rotations` |
| 12 | — round progression (listen mode) | `module_coop_mission_templates.py` | 5277–5312 | `$coop_round`, `coop_player_agent_save_items` (:5326), next scene by round (:5302–5306) |
| 13 | — dedicated forced single-round + end | `module_coop_mission_templates.py` | 5280–5284 (gate), 5405–5422 (end handler) | |
| 14 | — belfry placement block | `module_coop_mission_templates.py` | 5549–5550 | `script_coop_move_belfries_to_their_first_entry_point` (def `module_coop_scripts.py:3312`) |
| 15 | — belfry crew assignment | `module_coop_mission_templates.py` | 5609 | `script_cf_coop_siege_assign_men_to_belfry` (def `module_coop_scripts.py:3503`) |
| 16 | Round-type / reserve constants | `module_constants.py` | 2326–2334 | `coop_reserves_hall/street`, `coop_round_*` |
| 17 | Local siege aftermath (event 17 arm) | `module_coop_scripts.py` | 15709–15735; 15789–15807 | `coop_char_siege_center_get` + clear; win: `coop_victory_consequences_local` then `coop_siege_capture_consequences` + renown +5; loss (-1): `coop_player_defeat` with the center as captor, `coop_captive_kind_castle` |
| 18 | Dedicated siege result apply (shared) | `module_coop_scripts.py` | def 17159; 17475–17500 | `coop_apply_battle_results` — garrison casualties via `@p_enemy0_partyid` = center party; win: A7 applier first (`:17475`), then `coop_siege_capture_consequences` (`:17500`, captor = initiator via `@battle_host_player_name`, applier fallback) |
| 19 | Shared capture consequences | `module_coop_scripts.py` | 15629–15668 | `coop_siege_capture_consequences`: `coop_captivity_release_party_captives` (players held by the center go free), `party_clear`, `slot_center_last_taken_by_troop`, prosperity −5, war damage 40/20 vs old faction, full `give_center_to_faction` to `fac_player_faction` |

## State & events

- **Dict keys (siege delta):** `@map_type` ∈ {2 attack, 3 defend},
  `@map_scn` (walls), `@map_castle`, `@map_street`, `@map_party_id`
  (besieged center), `@p_castle_lord`/`@p_garrison` (enemy-party indices,
  0 for sieges, -1 for field), `@p_garrison_banner`.
- **Dict key:** `@char_siege_center` in the player's char dict — the
  locally-assaulted center; survives the client's disconnect AND the
  player_no/party reassignment on rejoin (preserved across
  `coop_save_character` rebuilds; helpers `coop_char_siege_center_set/_get`
  `module_coop_scripts.py:8768/:8759`; cleared by ev 16 and ev 17).
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
  (`module_constants.py:2330–2334`); reserves: hall 20, street 80
  (`:2326–2327`).
- **Network events:** ch49 `request_siege`=26 (`header_common.py:310`),
  `request_siege_local`=27 (`:313`), `local_fight_result`=17 (`:307`);
  ch125 `battle_available`=10 (`:181`), `start_siege_local`=42 (`:212`).
  Battle types: `module_constants.py:2208–2213`.

## Invariants

- The local-siege target lives in the **per-player char dict**
  (sid- or username-keyed since `ce0e287`; key-builder-owned naming)
  (`@char_siege_center`) because the client disconnects into its local
  mission and rejoins with a NEW player_no and slot-derived party — player
  and party ids identify nothing across that boundary (runtime-proven:
  player 3/party 6 at assault became player 5/party 8 at result). A field
  local fight (ev 16) clears any stale stash so an abandoned siege can't
  be misread as a capture.
- The wall scene must be sent from the server (`:14565–14588`) — center
  party slots are not synced to clients.
- Dedicated siege is single-round by design gate (`:5280–5284`); multi-round
  progression (walls -> street -> hall) exists only in listen mode.
- Local-siege party freeze (`disable_party` `:14581`) must be undone by
  rejoin/`enable_party` (`coop_player_hydrate:9675`) or exit
  save (`multiplayer_campaign_player_exit:10011`).
- For sieges the besieged center **is** the serialized enemy party 0;
  garrison casualty application therefore mutates the center party directly
  (`coop_apply_battle_results` via `@p_enemy0_partyid`).

## Audit: ours vs. native

| # | Behavior | Ours (anchor) | Native ground truth (evidence) | Verdict |
|---|----------|---------------|--------------------------------|---------|
| 1 | Siege scene + variant: walls scene from `slot_town_walls`/`slot_castle_exterior`, belfry vs ladder from `slot_center_siege_with_belfry` | `module_coop_scripts.py:16843–16720` (dedicated), `:14565–14572` + `:14586` (local: wall scene + belfry flag sent to the client), `:7804–7809` (client picks the variant) | Identical sources to native: assault menus read `slot_town_walls`/`slot_castle_exterior` (`module_game_menus.py:5489–5491`, `:5849–5854`) and the belfry flag is the same slot native seeds at game start (`module_scripts.py:346–365`). Local-siege missions are literal copies of native `castle_attack_walls_{belfry,ladder}` with only a side-flag swap (`module_mission_templates.py:3223–3232`, `:3313–3320`). | OK |
| 2 | Belfry (dedicated `coop_siege`): pre-positioned at first entry point with `slot_scene_prop_belfry_platform_moved=1`; no push/rotate phase | `module_coop_mission_templates.py:5532–5557` (native trigger commented out at `:5531`), `:5608`; `module_coop_scripts.py:3312` | Native uses `common_siege_init_ai_and_belfry`/`_move_belfry`/`_rotate_belfry`/`_assign_men_to_belfry` (`module_mission_templates.py:980–1002`) — soldiers push the belfry to the wall. Coop deliberately replaces this (native triggers commented out, replacement block inline): belfries start at the wall, movement phase skipped. Intentional MP simplification. | OK |
| 3 | Defender composition: center party as enemy0 (garrison keys point there) plus every non-player party attached to the center serialized as enemy1..N with per-party casualty round-trip via `@p_enemy{i}_partyid`; friendly AI parties within `coop_siege_join_radius` join as ally1..N (placeholder rule until a siege camp exists) | `coop_write_battle_data` roster sections + `script_coop_battle_dict_write_roster_party` | Native battles collect **attached parties** into the enemy side (`party_collect_attachments_to_party` -> `p_collective_enemy`, `module_game_menus.py:6079`, `:4281`). Coop now rosters them per-party (identity preserved for casualty apply-back — a collective party can't round-trip through the dict). Fixed `67239e5..d7955b7`, runtime-verified 2026-07-19 multi-client. Attacker-side filter tightened in A8 (`2845589`, verified 2026-07-25): lord-party whitelist + real-ally relation rule | OK |
| 4 | Multi-round siege (walls -> street -> hall) in listen mode; dedicated forced single-round | `module_coop_mission_templates.py:5277–5312`, `:5280–5284` | Dedicated single-round is documented in-code: "Dedicated siege v1 is single-round: the wall battle decides the siege" (`:5280–5284`). The multi-phase progression is inherited coop-mod (Banner Time) design, a deliberate extension over native's single-scene assault. | OK |
| 5 | Dedicated siege victory: capture fixed in `50f4ac1` (A5, runtime-verified 2026-07-10); A8 (`0b2500a`, runtime-verified 2026-07-25) moved it into the shared capture script and reordered it AFTER the A7 applier — political consequences now read the center's pre-transfer faction (latent A7-era ordering bug fixed) | `module_coop_scripts.py:17613–17500` | Native: successful assault transfers the center, handles lord capture/escape, prisoners, and post-siege menus — A7 applier + A8 capture script now cover the set | OK |
| 6 | Both capture paths run native `castle_taken` consequences via `coop_siege_capture_consequences`: release of the center's player captives, `party_clear`, `slot_center_last_taken_by_troop` (initiator), prosperity −5, renown +5 to every participant, war damage 40/20 vs the old owner, full `give_center_to_faction`; local siege additionally gained the previously-missing A7 applier call (gold/battle renown/garrison prisoners/lord fate/political). Fixed A8 (`8b45f2a..db4a815`, merged `0b2500a`), runtime-verified 2026-07-25 (Bulugha Castle smoke: gold+renown+capture; prisoners confirmed once prisoner_management > 0 — native cap) | `module_coop_scripts.py:15670–15668`, `:15709–15735` | Native `castle_taken` menu (`module_game_menus.py:6603–6670`). Deliberately dropped as N/A in coop: `lift_siege` (no siege-camp state), besieger guard order (no besieger AI), keep-or-give-to-vassal menu (players are not vassals; centers go to `fac_player_faction`). Known cosmetic: local path prints both "has fallen" and "has captured" | OK |
| 7 | Battle types `siege_player_defend` (3), `village_*` (4/5), `bandit_lair` (6) are defined and handled by the dict loader, but nothing ever launches them | `module_constants.py:2210–2213`; only callers pass types 1/2 (`module_coop_scripts.py:14538`, `:14525`) | Confirmed by exhaustive grep: no `coop_write_battle_data` caller uses types 3–6. Group-C resolution (`1dc8fec`): kept as future-feature scaffolding, documented as "defined, not yet launched" here and in project-state — the divergence was the docs overstating them, now corrected | OK |

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
`module_coop_mission_templates.py:4718–4720`), so this is a verification
gap, not a known divergence.

## Related docs

- `battle-pipeline.md` — shared serialization, IPC, and result-apply tail.

Workbench documents (not part of the public export — see the citation
note in `README.md`):

- `docs/plans/siege-coop-plan.md` — earlier siege planning notes.
- `docs/archive/2026-03-23-warband-coop-party-creation-design.md`
  — party-creation design notes.
