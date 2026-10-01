# Flow: XP Sync (char XP, stack upgrades, battle XP)

**Status:** AUDITED
**Validated against commit:** `7161f85` (docs refresh 2026-09-21: every
line anchor re-verified against the current tree — the packed-sync and
client-receive scripts below `module_coop_scripts.py:7360` are unmoved,
everything after moved by +170..+2300; the hero-XP push is now its own
script `coop_char_send_hero_xp`; the kill-XP credit (`e28eacf`, win
variant runtime-verified 2026-08-29, loss variant + save-cap regression
still open) is folded into the sequence, invariants and audit row 2/4
text; a stale `:6798–6809` "client undoes engine kill XP" citation that
pointed at nothing is replaced by the mechanism the code actually uses;
no verdict changed. Prior stamp `2923381`: anchors re-verified
2026-08-30; runtime-verified behavior unchanged since `2dd4f17`) (two
rejoin XP-integrity fixes,
both runtime-verified 2026-08-29/30: `f1cfc21` — the load-time party
rebuild resolves the REAL party stack index by troop id before restoring
stack-XP residuals/upgrade credits (the player's own stack survives
`party_clear` at index 0, so the dict index is shifted +1; a recruit
residual was landing on the player hero stack as free troop XP + engine
level-ups on every rejoin). `2dd4f17` — the client ev-40/ev-43 xp
delta-apply preserves the three point pools across `add_xp_to_troop`
(the fresh-connect replay from local xp 0 crossed every past level
threshold and re-minted level-up points, which ev-12 `sync_pools` then
made server-authoritative — phantom +1/+1/+10 per relog). Prior stamp
`ce0e287` (steamid persistence, runtime-verified 2026-08-23: rejoin-time
full char push fires from `coop_player_hydrate`, char dicts sid-keyed;
packed protocol unchanged). Prior stamp `97be801`: packed char sync
ch125 ev 36-40 replaces the per-value events this dossier used to cite —
XP travels in `packed_misc` (ev 40), not the old `char_sync_xp` (ev 21).
Prior stamp `632466c`, A7 loot-gold note closed — applier merged
`4ba5786`, runtime-verified 2026-07-24; A9 victory-gated XP pool noted)

## Scope

How experience reaches player characters and their troops, and how the
authoritative value stays on the campaign server: (A) the char-XP push
(ch125 ev 40 `packed_misc`, part of the 5-message packed full sync), (B)
the per-stack upgradeable push (ch125 ev 22 — despite the
event name, it carries upgradeable counts, not XP), and (C) battle XP from
both battle modes (dedicated Phase 1/2 pipeline; local-fight ch49 ev 17).
Entry points: player rejoin, `request_char_sync`, battle results. Exit
state: client troop XP/level/points mirror the server; pending battle XP
consumed. Point-spending (raise events 4/5/6, `sync_pools` 12) is the char
screen's concern and only appears here where it gates XP state.

Module paths relative to `wse2work/Native-Coop-master/`.

## Sequence diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant CS as Campaign Server
    participant BS as Battle Server

    note over CS,C: A) char XP push (rejoin, ch49 request_char_sync,<br/>or re-push after local-fight XP apply) -- 5 packed messages,<br/>join always sends all 5; screen-close re-sync sends only dirty categories
    CS->>C: ch125 36 packed_core: attrs (6b x4) + level (6b), gold (31b raw),<br/>attr/skill/prof points (8/8/10b)
    CS->>C: ch125 37/38 packed_skills_a/b: 7 skills per int (4b each), 0-20 / 21-41
    CS->>C: ch125 39 packed_profs: 3 profs per int (10b each)
    CS->>C: ch125 40 packed_misc: xp (31b raw), health (7b) + renown (16b<<7)
    CS->>C: ch125 43 hero_sync_xp per companion hero stack (troop, xp)<br/>-- unconditional every batch, not dirty-gated
    CS->>C: ch125 20 char_sync_done (arms diff-poller baseline)
    note over C: ev40/ev43: apply delta via add_xp_to_troop with point<br/>pools preserved across the add (engine re-awards level-up points<br/>on every threshold crossed -- pool truth is ev 36/ev 12 only).<br/>Negative deltas are a NO-OP (engine clamps adds to >=0), so a<br/>client running AHEAD of the server is never corrected down.<br/>ev43 targets the companion's client-local troop copy

    note over CS,C: B) stack upgradeable push
    CS->>C: ch125 22 per stack: num_upgradeable
    note over C: party_stack_set_num_upgradeable (party screen display)

    note over CS,BS: C1) dedicated battle XP
    CS->>BS: @hero_{i}_xp snapshot in dict (pre-battle)
    BS->>BS: hydrate: player-troop XP baseline in the wipe-proof<br/>slot_troop_coop_battle_xp_base (engine pays per-kill XP in-mission)
    BS->>BS: post-battle: hero XP saved back + @battle_xp_rand roll(50-100),<br/>per-player strength + acctid + kill-XP delta snapshot;<br/>battle-side char saves cap @char_xp at the baseline
    BS->>CS: dict + IPC END (see battle-pipeline.md)
    CS->>CS: Phase 1 (victory only): pool=(lvl+10)^2/10 per casualty, cap 40k,<br/>x rand, stash share per player in char dict
    CS->>CS: Phase 1 (win or lose): @battle_player_{i}_kill_xp added onto<br/>@char_pending_hero_xp
    CS->>CS: Phase 2 (each hydration): coop_apply_xp_shares --<br/>host: party_add_xp, joiner: hero only; kill-XP always hero

    note over C,CS: C2) local fight XP
    C->>C: debrief: pool formula over actual enemy casualties,<br/>cap 40000, × rand(50,100)/100 after the cap, globals → ASI → coop_local_result.ini
    C->>CS: reconnect, ch49 17 win/cas/xp_delta (+ per-stack -2 packets)
    CS->>CS: coop_apply_xp_shares(player, xp, 0) as party share
    CS->>C: full char sync re-push (the join-time push predates ev 17)
```

## Code anchors

| # | Step | File | Line | Symbol |
|---|------|------|------|--------|
| 1 | Full char sync push: 5 packed messages + hero-xp + done | `module_coop_scripts.py` | 7186–7198 | `coop_send_char_sync_to_client` (calls `coop_char_pack_send_core/skills/profs/misc` then `coop_char_send_hero_xp` in sequence) |
| 1b | Packed-message builders (core/skills/profs/misc) | `module_coop_scripts.py` | 7031–7064 (core), 7066–7111 (skills), 7113–7140 (profs), 7142–7163 (misc) | `coop_char_pack_send_core` (ev 36), `_skills` (ev 37/38), `_profs` (ev 39), `_misc` (ev 40) |
| 2 | — XP value honors pending DLL set_xp | `module_coop_scripts.py` | 7148–7152 | `$g_coop_set_xp_go/troop/value` (in `coop_char_pack_send_misc`) |
| 3 | Client receive: signed-delta XP apply | `module_coop_scripts.py` | 7299–7321 | `coop_char_client_receive` (ev 40 `packed_misc` arm) |
| 3b | Companion hero XP push + client apply (ev 43) | `module_coop_scripts.py` | 7165–7184, 7332–7351 | `coop_char_send_hero_xp`: one ev 43 per hero stack (player-troop range excluded), called by the full sync (`:7192`) and the ev-7 arm (`:12968`); client signed-delta apply on the hero troop |
| 3c | Post-local-fight char sync re-push | `module_coop_scripts.py` | 12626, 12629 | ev-17 arm after `coop_apply_xp_shares` + save — without it client player/companion XP is stale until the next rejoin or C-screen open; the ev-22 re-push follows for the credits `party_add_xp` just minted |
| 3d | Selective push-back on screen close: category bitfield gates which packed messages re-send | `module_coop_scripts.py` | 12934–12976 | `request_char_sync` (ch49 ev 7) arm — `coop_char_dirty_*` bits (attrs/gold/points→core, skills→skills, profs→profs, xp/health/renown→misc); hero-xp + done always sent, even with a clean (0) dirty mask |
| 4 | Client receive: snapshot mirror per field | `module_coop_scripts.py` | 7217–7218, 7269–7270, 7295–7296 | `slot_coop_char_snap_*` on `trp_temp_troop`, written in each packed arm of `coop_char_client_receive` |
| 5 | Sync-done gate for diff poller | `module_coop_scripts.py` | 7353–7357 | `$g_coop_char_snap_ready` |
| 6 | Push triggers at hydration (identify / 5 s fallback after rejoin) | `module_coop_scripts.py` | 9484, 9489 | `coop_send_char_sync_to_client`, `coop_send_party_upgradeable_to_client` (inside `coop_player_hydrate`, def `:9321`) |
| 7 | Stack upgradeable push (ev 22 sender) | `module_coop_scripts.py` | 14720 | `coop_send_party_upgradeable_to_client` (`party_stack_get_num_upgradeable`) |
| 8 | Stack upgradeable client apply | `module_coop_scripts.py` | 11745–11756 (ev 22 arm), 8430–8441 (load-time restore, real stack index resolved by troop id — `f1cfc21`) | `party_stack_set_num_upgradeable` |
| 9 | Battle XP pool (dedicated) | `module_coop_scripts.py` | 14344–14380 | `coop_compute_sp_xp_pool_from_dict` |
| 10 | Shared rand roll + player strength snapshot (battle server) | `module_coop_scripts.py` | 4806 (def), 4907–4908 (`@battle_xp_rand` roll + set), 4940 (strength snapshot) | in `coop_copy_parties_to_file_mp` |
| 11 | Phase 1 stash / Phase 2 apply | `module_coop_scripts.py` | 13861 (Phase 1, `coop_apply_battle_results` def; skip-flag block 13905–13911), 14382 (Phase 2, `coop_apply_xp_shares` def) | see `battle-pipeline.md` |
| 12 | Canonical XP application | `module_coop_scripts.py` | 14382–14420 | `coop_apply_xp_shares` |
| 13 | Hero XP dict codecs (chunked delta apply) | `module_coop_scripts.py` | 5145, 5230, 5348 | `coop_copy_register_to_hero_xp`, `coop_copy_hero_to_file`/`_file_to_hero` (`@hero_{i}_xp`) |
| 14 | Hero snapshot round-trip call sites | `module_coop_scripts.py` | 4622, 4652, 4893, 5006, 13910 | campaign save -> battle load -> battle save -> campaign restore |
| 15 | Local debrief XP computation | `module_game_menus.py` | 15149 (def), 15210–15225 (pool formula + cap) | `coop_local_battle_debrief` (pool formula, cap 40000, × rand(50,100)/100 after the cap at 15230–15232) |
| 16 | Debrief -> ASI handoff | `module_game_menus.py` | 15244–15246 (`$g_coop_result_*` writes), 15262 (`$g_coop_result_ready`) | `$g_coop_result_*`, `$g_coop_result_ready` |
| 17 | Pending local result push on reconnect | `module_simple_triggers.py` | 296–363 | `$g_coop_pending_*` -> ch49 ev 17 packets |
| 18 | Server arm: local XP apply | `module_coop_scripts.py` | 12551 | `coop_apply_xp_shares(player, xp, 0)` |
| 19 | Personal kill-XP credit (battle-server per-kill XP, outcome-independent) | `module_coop_scripts.py` | 9245–9253 (`coop_battle_player_hydrate` kill-xp-base snapshot, def `:9224`), 4950–4959 (post-battle `@battle_player_{i}_kill_xp` snapshot in `coop_copy_parties_to_file_mp`), 7926–7929 (battle-side save caps `@char_xp` at the baseline), 14061–14088 (Phase 1 kill-XP credit block, additive onto `@char_pending_hero_xp`) | `slot_troop_coop_battle_xp_base` (`module_constants.py:1963`); introduced by `e28eacf` |

## State & events

- **Events:** ch125 (net-optimizations packed sync, replaces the old
  per-value events 14/16-19/21/23/24, which are deleted and free):
  `char_sync_packed_core`=36 (attrs 6b×4 + level 6b, gold 31b raw, attr/skill/
  prof points 8/8/10b), `char_sync_packed_skills_a`=37 / `_skills_b`=38
  (7 skills per int, 4b each, ranges 0-20/21-41), `char_sync_packed_profs`=39
  (3 profs per int, 10b each), `char_sync_packed_misc`=40 (xp 31b raw,
  health 7b | renown 16b<<7), `char_sync_done`=20 (unchanged),
  `party_stack_num_upgradeable`=22 (unchanged, renamed from `party_stack_xp`
  in C5), `hero_sync_xp`=43 (companion troop id + xp, signed-delta apply,
  unconditional every sync batch). A full sync is 5 packed messages + ev 43
  per companion hero + ev 20 done (~7-10 messages vs the pre-packing 59+).
  ch49: `request_char_sync`=7 (screen-close re-sync: server flushes the
  deferred save then re-sends only the packed messages whose
  `coop_char_dirty_*` category bit is set — an unchanged char screen close
  sends hero-xp + done only, no packed message), `local_fight_result`=17
  (`header_common.py`).
- **Dict keys:** char dicts: `@char_battle_pending`, `@char_pending_party_xp`,
  `@char_pending_hero_xp`; battle dict: `@battle_xp_rand`,
  `@battle_num_players`, `@battle_player_{i}_name/acctid/strength/kill_xp`,
  `@hero_{i}_xp`.
- **Globals:** `$g_coop_set_xp_go/troop/value` (DLL pending XP set),
  `$g_coop_char_snap_ready` (client), `$g_coop_result_*` (client debrief),
  `$g_coop_pending_*` (client reconnect push).
- **Client snapshot slots:** `slot_coop_char_snap_*` on `trp_temp_troop` —
  the diff-poller baseline, written only by receive handlers.

## Invariants

- **Server XP is authoritative; the client applies signed deltas**
  (`:7304–7321`, ev 40 `packed_misc` arm) — this is what cancels the client
  engine's local kill-XP inflation. Never push absolute XP by `troop_set_*`
  on the client.
- **Companion troop XP reaches the client ONLY via ev 43** (runtime-verified
  2026-07-10, `13ebcad`; still true after the net-optimizations packing):
  ev 40 (`packed_misc`) is player-troop-only, ev 22 carries
  upgradeable counts, and the C-layer snapshot has no troop XP — without
  ev 43 the sheet shows an unsynced local copy that inflates in local
  missions and resets on rejoin.
- **The diff-poller baseline comes from receive handlers, not the client
  troop** (snap-mirror writes, `:7217–7357` region, and project-state
  lesson) — snapshot-diff is racy otherwise.
- `coop_apply_xp_shares` is the single XP application path for both battle
  modes; both shares are base-safe against a pending DLL `set_xp`
  (`:14382–14420`).
- `coop_copy_register_to_hero_xp` applies XP as a delta chunked by 29999 per
  `add_xp_to_troop` call (`:5160–5164`).
- One shared `@battle_xp_rand` roll per battle (`:4907`) keeps
  multi-player relative shares deterministic.
- The dedicated Phase 1 pool is **victory-gated** since A9 (`632466c`):
  it is computed only when `@battle_result == 1` — losses and retreats
  pay no XP pool. The kill-XP credit (`e28eacf`, `:14061–14088`) is a
  separate, outcome-independent Phase 1 pass: the battle server's
  in-mission per-kill XP is measured against the hydrate-time baseline
  (`slot_troop_coop_battle_xp_base`, wipe-proof troop slot), written as
  `@battle_player_{i}_kill_xp`, and added onto the pending hero share;
  battle-side char saves cap `@char_xp` at that baseline (`:7926–7929`)
  so the pending credit is the single payer.
- Engine lessons (project-state): variable proficiency cost — client engine
  is cost authority; `troop_raise_proficiency` does not consume WP; AGI +5 WP
  bonus is native-UI-only.

## Audit: ours vs. native

| # | Behavior | Ours (anchor) | Native ground truth (evidence) | Verdict |
|---|----------|---------------|--------------------------------|---------|
| 1 | Dedicated battle XP pool: `(level+10)^2/10` per enemy casualty, cap 40000, × shared rand 50–100; plus, since `e28eacf`, each player's in-mission kill-XP delta as a personal hero share, win or lose (win variant runtime-verified 2026-08-29; loss variant + save-cap regression still open) | `module_coop_scripts.py:14344–14380`, `:4907`, `:14061–14088` | Matches native `party_give_xp_and_gold` basis and formula (`module_scripts.py:15360–15392`, called with `p_total_enemy_casualties` at `module_game_menus.py:4674`), and native SP also pays per-kill mission XP during the fight; minor deltas documented in `battle-pipeline.md` audit row 2 | OK |
| 2 | Local-fight XP: same pool formula over actual casualties, cap 40000, **× rand(50,100)/100 after the cap** (native parity). Fixed in `50f4ac1`, runtime-verified 2026-07-10 (victory screen `pool 603 x roll 66% = 397`, exact integer match). Loot gold is now paid by the A7 consequence applier (merged `4ba5786`, runtime-verified 2026-07-24) | `module_game_menus.py` debrief (roll after `val_min` cap) | Native applies × rand(50,100)/100 after the cap (`module_scripts.py:15388–15390`) and also pays loot gold via `party_give_xp_and_gold` | OK |
| 3 | Local-fight XP applied entirely as party share (`party_add_xp` distribution) | `module_coop_scripts.py:12551`, `:14395` | Native SP applies the whole pool via `party_add_xp` to the main party (`module_scripts.py:15392`) — same semantics | OK |
| 4 | One XP-credit path reaches companion heroes on the dedicated battle path: the campaign-side hero restore skips the `@hero_{i}_xp` re-apply (`$g_coop_skip_hero_xp_restore` set around the restore in `coop_apply_battle_results`, `:13909–13911` @ `50f4ac1`), so the computed Phase 1/2 pool share is the sole companion credit — SP parity. Fixed in `50f4ac1`, runtime-verified 2026-07-10 (companion gained a normal SP-sized share once; not double, not zero). The player's OWN per-kill XP is the one exception, by design since `e28eacf`: it is measured against a hydrate-time baseline and paid once through the pending hero share (row 1) | `module_coop_scripts.py:5462`, `:13909–13911` (@ `50f4ac1`) | RE-confirmed (`patches/Warband/findings.md` "Engine mission kill-XP paths", `patches/WSE2Dedicated/kb.h`): the WSE2 dedicated server writes hero `m_experience` per kill for game types 11/12 (writer `0x487A90`), with **no game-type gate**. The same engine path inflates the CLIENT's local troop copies in a local fight; that side is not undone but cancelled by the server-authoritative signed-delta re-push after ev 17 (ev 40 for the player, ev 43 for companions, `:12626`). The dedicated path previously round-tripped it through `@hero_{i}_xp` AND added the pool share on top (heroes paid twice); the skip flag makes the pool share canonical. | OK |
| 5 | Event 22 renamed `party_stack_num_upgradeable` (constant + script `coop_send_party_upgradeable_to_client`) and project-state row corrected — the name now matches the payload. Fixed in `1dc8fec`, runtime smoke passed 2026-07-11 | `module_coop_scripts.py` sender/recv arm; `header_common.py` | Sender uses `party_stack_get_num_upgradeable`, receiver `party_stack_set_num_upgradeable` — misnaming was doc/constant drift only | OK |
| 6 | Level + points: level derived from XP by the client engine; point pools pushed server-authoritatively (packed into ev 36 `packed_core`, int3); AGI WP bonus intentionally absent outside native UI | `module_coop_scripts.py:7031–7064` (pack, bits at 7057–7062), client apply `:7232–7238` | Engine derives level from XP identically on both sides; the AGI/WP and proficiency-cost deviations are known, documented engine lessons (workbench project-state notes) | OK |

## Fix list

| # | From audit row | What diverges | Suggested owner/layer |
|---|----------------|---------------|------------------------|
| 1 | 2 | ~~Local debrief omits the native rand(50,100)/100 scaling~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10. ~~Loot gold unpaid~~ **Done** by the A7 consequence applier (merged `4ba5786`, runtime-verified 2026-07-24 — see `battle-pipeline.md` row 6). | `module_game_menus.py` debrief |
| 2 | 5 | ~~Event 22 misnamed/misdocumented~~ **Done** (`1dc8fec`, smoke 2026-07-11): renamed `party_stack_num_upgradeable` (constant + script + project-state row). | `header_common.py` + workbench project-state doc |
| 3 | 4 | ~~Hero XP double-credited on the dedicated battle path~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10 — `$g_coop_skip_hero_xp_restore` suppresses the `@hero_{i}_xp` re-apply; the pool share is the canonical (sole) companion credit. | `module_coop_scripts.py:5462`, `:13909–13911` |

## Open questions

- ~~Exact per-player hero attribution of the double-credit~~ Settled by the
  row-4 fix (`50f4ac1`): the `@hero_{i}_xp` restore is skipped, making the
  Phase 1/2 pool share the single canonical credit path.
- Kill-XP credit (`e28eacf`): the loss variant (kills, then lose — credit
  paid, pool skipped) and the battle-server save-cap regression (dict
  `@char_xp` must not inflate between battle end and rejoin after a
  mid-battle stat raise) are merged but not yet runtime-verified
  (ledger: `docs/NEXT_SESSION.md` battle-XP section, gate 7).
- Honor is not synced: `troop_get_player_relation`
  (`module_scripts.py:24669–24695`) adds a `$player_honor` bonus that the
  client's zeroed copy omits; scheduled as a packed-misc extension in the
  "world reacts per player" to-dos, not part of this flow yet.

## Related docs

- `battle-pipeline.md` — Phase 1/2 mechanics, casualty basis, xp_rand source.

Workbench documents (not part of the public export — see the citation
note in `README.md`):

- `docs/archive/SYNC_REDESIGN.md`, `docs/sync-systems/` — original char-sync design.
- `docs/superpowers/plans/2026-04-10-sp-xp-battle-parity.md` — the SP-parity
  work this flow implements.
