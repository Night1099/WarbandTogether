# Coop Flow Dossiers

One dossier per core flow. Each documents how the flow works (sequence,
anchors, invariants) and audits it against native/engine ground truth
(`OK`/`DIVERGES`/`UNKNOWN` verdicts). Template: `TEMPLATE.md`.

> **Note on citations:** these dossiers are authored in the private
> workbench repository this public repo is exported from. Evidence
> citations pointing at paths that don't exist here — `patches/…`
> (reverse-engineering findings and knowledge bases), `.claude/…`
> (project-state notes), and `docs/…` files outside `docs/flows/`
> (design specs, RE session notes) — refer to workbench documents.
> The dossier text always summarizes the relevant finding inline, so
> nothing here requires those files to follow the flow.

| Flow | Dossier | Status |
|------|---------|--------|
| Battle pipeline (dedicated battle end-to-end) | `battle-pipeline.md` | audited |
| Siege (coop siege battle types + local siege) | `siege.md` | audited |
| XP sync (char XP, stack XP, local-fight XP) | `xp-sync.md` | audited |
| Inventory sync (inv screen, equip pushes) | `inventory-sync.md` | audited |
| Party screen sync (roster, dismiss, upgrade) | `party-screen-sync.md` | audited |
| Steam P2P tunnel (internet transport, no port forwarding; + Join Game invites & server password since phase 4) | `steam-tunnel.md` | audited |
| Campaign server tick (frame loop, simple-trigger clock, party replication, per-client send pacing) | `campaign-server-tick.md` | audited (engine side); D1 done `562482c`, D2/D4 implemented-unverified, D3 apply-verified |

## Engine findings map

Which existing RE/audit material is relevant to each flow (workbench
documents — see the citation note above).

| Flow | Relevant findings / docs |
|------|--------------------------|
| Battle pipeline | `docs/archive/BATTLE_RESULTS_PIPELINE_AUDIT.md`, `patches/WarbandDedicated/findings.md`, `docs/archive/2026-03-22-warband-coop-campaign-sync-design.md` |
| Siege | `docs/plans/siege-coop-plan.md`, `battle-pipeline.md` shared tail |
| XP sync | `docs/archive/SYNC_REDESIGN.md`, `docs/sync-systems/`, `patches/Warband/findings.md` (kill-XP paths), `patches/WarbandBattleDed/kb.h` (kill-XP paths) |
| Inventory sync | `docs/archive/RE_NATIVE_SCREENS.md`, `docs/archive/SP_SCREEN_RECREATION.md` |
| Party screen sync | `docs/archive/RE_NATIVE_SCREENS.md`, `docs/archive/Screen_Session.md` |
| Campaign server tick | `patches/WarbandDedicated/findings.md` ("Campaign server periodic load"; "nettune patch sites", send-path Q1-Q7), `patches/WarbandDedicated/network_tick_rate.md`, `docs/wse2-binary-patches.md` |
| Steam P2P tunnel | `docs/archive/STEAM_P2P_FACTS.md`, `docs/archive/NETWORKING_AUDIT.md`, `docs/archive/TRAFFIC_OPTIMIZATION.md`, `patches/Warband_WSE2/findings.md` ("SteamAPI_RunCallbacks pump audit", "Loopback join classification", "Phase 4 invites+password RE" Q5–Q11) |

RE symbol knowledge lives in `patches/<project>/kb.h`; narratives in
`patches/<project>/findings*.md`. Dossiers link into those files — they are
the ground-truth store, this index is just the map. New engine RE from this
audit: `patches/Warband/findings.md` ("Native kill-vs-wound (surgery) rules",
"Engine mission kill-XP paths", "all_enemies_defeated opcode semantics");
`patches/Warband_WSE2/findings.md` and `patches/WarbandDedicated/findings.md`
(bootstrap: kb.h grown to 3094 / 2653 entries, Ghidra projects built).

## Consolidated fix list

> **History.** This list is closed. New `DIVERGES` findings become features in
> the parity ledger (`docs/parity/ledger/`) that link the dossier; open
> items from this list are tracked there too.

Every `DIVERGES` verdict across the seven dossiers, ranked by player impact.
"Src" points to the dossier fix-list row for full context.

**Status:** A1–A5 and B1 were **implemented** in commit `50f4ac1` (full
29-step module build green) and are marked ✅ below. **B1 is runtime-verified
(2026-07-10)** — legit edits stick, no false `[INV GUARD]` rejects; its
dossier verdict is flipped to OK. Runtime testing of B1 also exposed and
fixed a join-push-ordering bug (char sync must precede inventory — see
inventory-sync.md invariants). A1–A4 were runtime-verified 2026-07-10, A5
in `13ebcad`; A6–A9 are verified per their rows (2026-07-19..25). **Groups
B2–B3 are done** (`9558722` merge, runtime smoke 2026-07-25, incl. the A4
residual). **B4–B8 are done** (WarbandTogether PR #1 port, runtime-verified
2026-09-18). **Group C is done** — implemented in `1dc8fec` (module) +
`fd0e088` (C layer), runtime smoke passed 2026-07-11, all C verdicts
flipped to OK. That smoke also surfaced a pre-existing player-blocking
symptom of A7 (post-dedicated-battle stuck player — see the A7 row).
**Group D** (campaign-server load, 2026-09-20): D1 done + runtime-verified
(`562482c`); D2/D4 implemented but not runtime-tested; D3 apply-verified on
both dedicated exes, drain effect not yet measured.

### A. Gameplay correctness (affects live play)

| # | Flow (src) | What's wrong | Owner |
|---|------------|--------------|-------|
| A1 | ✅ **verified** battle-pipeline (1) | ~~Surgery save omits native's 0.25 base~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10 | `module_coop_scripts.py:7072–7077` |
| A2 | ✅ **verified** xp-sync (4) | ~~Heroes double-credited XP on dedicated battles~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10 (pool share is the sole hero credit) | `module_coop_scripts.py:5251`, `:9430–9432` |
| A3 | ✅ **verified** xp-sync (2) | ~~Local-fight XP overpays ~34% (no rand roll)~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10 (`pool 603 x roll 66% = 397` exact). Loot gold now paid by A7's applier (merged `4ba5786`, runtime-verified 2026-07-24) | `module_game_menus.py` debrief |
| A4 | ✅ **verified** party-screen (2) | ~~Troop upgrades are free~~ Gold cost fixed (`50f4ac1`, verified 2026-07-10); residual upgrade-credit decrement fixed (`bdcfd8c`: ev-11 consumes the from-stack's `num_upgradeable` via op 3906 + ev-22 re-push — engine RE proved stacks have no XP field; smoke 2026-07-25) | `module_coop_scripts.py` ev-11 arm |
| A5 | ✅ siege (5) | Winning a **dedicated** siege never captures the center (the local path was also broken in practice — player_no-keyed mark; fixed + runtime-verified in `13ebcad`). A8 (`0b2500a`) later moved capture into the shared `coop_siege_capture_consequences`, ordered after the A7 applier | `module_coop_scripts.py` BATTLE PIPELINE |
| A6 | ✅ **verified** siege (3) | ~~Attached defender parties sit out the siege~~ Fixed (`67239e5..d7955b7`) + runtime-verified 2026-07-19 — attachments fight as enemy1..N, proximity AI allies as ally1..N, per-party casualty round-trip. Attacker-filter follow-up done in A8 (`2845589`, verified 2026-07-25): lord-party whitelist + real-ally relation rule. Residual (DEFERRED.md): local sieges never roster attachments (dedicated-only by construction) | `module_coop_scripts.py` `coop_write_battle_data` |
| A7 | ✅ **verified** battle-pipeline (6) | ~~Battle wins pay XP only — no gold/loot, prisoners, or `battle_political_consequences`~~ Fixed (branch `a7-battle-consequences`, merged `4ba5786`) + runtime-verified 2026-07-24: hero gold shares, renown, capacity-capped prisoners, political/quest hook on dedicated + local paths. Item loot + defeat-path consequences deferred (`docs/DEFERRED.md`). Disengage sub-piece was verified 2026-07-11 (`f85c30e`/`d82d879`/`d865990`) | `module_coop_scripts.py` BATTLE PIPELINE |
| A8 | ✅ **verified** siege (6) | ~~Siege capture skips native consequences (lord fate, prisoners, relations, renown, war damage)~~ Fixed (branch `a8-siege-consequences`, merged `0b2500a`) + runtime-verified 2026-07-25: shared `coop_siege_capture_consequences` (prosperity −5, war damage 40/20, `last_taken_by_troop`, full `give_center_to_faction`, renown +5 to every participant) on BOTH capture paths; the local path additionally gained the A7 applier call it never had. Dedicated ordering fixed: applier before capture (political consequences read the pre-transfer faction). Smoke deferrals in `docs/DEFERRED.md` | `module_coop_scripts.py` BATTLE PIPELINE |
| A9 | ✅ **verified** battle-pipeline (3) | ~~Round-end reserve-blind and instant; no retreat path~~ Fixed (branch `a9-reserve-round-end`, merged `632466c`) + runtime-verified 2026-07-25: reserve-aware `coop_battle_check_round_end` (10s floor, 5s settle) in both templates, victory-gated XP pool, initiator-only retreat (server-verified). Deferrals in `docs/DEFERRED.md` | `module_coop_scripts.py` + `module_coop_mission_templates.py` |

### B. Server authority / correctness

| # | Flow (src) | What's wrong | Owner |
|---|------------|--------------|-------|
| B1 | ✅ **verified** inventory (6) | ~~`inv_change` applied verbatim server-side~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10 | `module_coop_scripts.py` ev-14/15 arms |
| B2 | ✅ **verified** inventory (1) | ~~No push-on-mutation~~ Fixed (`87f4c82`: `coop_push_player_inventory` single push contract; trade purchases applied server-side `6c4db5c`); runtime smoke 2026-07-25 | `module_coop_scripts.py` ECONOMY/MISC push helpers |
| B3 | ✅ **verified** inventory (2) | ~~Open-time snapshot baseline, ungated~~ Fixed (`2f2f2bc`+`75e9a57`: ev 13 re-added, recv-arm baseline mirror + `snap_ready` gate); runtime smoke 2026-07-25 | `module_scripts.py` `wse_window_opened` + recv arms |
| B4 | ✅ **verified** inventory (7) | ~~Equip slot 9 not persisted~~ Fixed (`332ecfb`, `872353d`) + runtime-verified 2026-09-18 | `coop_save_character`/`coop_load_character`/INV GUARD |
| B5 | ✅ **verified** inventory (8) | ~~Client bag diff read past the IM-derived visible capacity (phantom clears every close)~~ Fixed (`de99f67`, `7f7e6e8`, `636da0d`; clamp is client-only, server guard covers all 106 slots) + runtime-verified 2026-09-18. Diagnosed in WarbandTogether PR #1 | `coop_inv_client_diff_and_send`, `coop_inv_bag_cap` |
| B6 | ✅ **verified** inventory (9) | ~~Async equip/bag push overwrote a live edit~~ Fixed (`adef0f9`, `6368c97`: `coop_inv_recv_mirror_ok`, armed after `snap_ready`) + runtime-verified 2026-09-18 | ev 15/25 recv arms |
| B7 | ✅ **verified** inventory (10) | ~~Fast close-then-reopen lost the close diff~~ Fixed (`0ec78f0`, `6368c97`: `wse_window_opened` flushes a still-open session, trade-aware) + runtime-verified 2026-09-18 | `module_scripts.py` `wse_window_opened` |
| B8 | ✅ **verified** inventory (11) | ~~`inv_change` accepted any item id~~ Fixed (`332ecfb`) + runtime-verified 2026-09-18 | ev 14 arm |

### C. Dead code / protocol-doc drift

| # | Flow (src) | What's wrong | Owner |
|---|------------|--------------|-------|
| C1 | ✅ battle-pipeline (7) | ~~ch125 ev 14 `return_to_campaign` — defined, documented, never sent/handled~~ Deleted (`1dc8fec`, smoke 2026-07-11). Id 14 was briefly reused for `char_sync_renown` (A7), then freed again by the packed char sync; `header_common.py` now lists 14 among the free ch125 ids | `header_common.py` + project-state |
| C2 | ✅ battle-pipeline (8) | ~~ASI writes `s57` reconnect address; nothing consumes it~~ Original write deleted (`fd0e088`); phase 4 then repurposed `s57` as the **join-password mirror** (`src/asi/coop.c:210`, rewritten every 500 ms, 47-char clamp) and `module_simple_triggers.py:224` consumes it as the deferred battle-connect password arg. The register is NOT private — native scratch writers exist and can clobber it between mirror ticks; tracked in `docs/DEFERRED.md` | `src/asi/coop.c:210` + `module_simple_triggers.py:224` |
| C3 | ✅ battle-pipeline (9) | ~~Legacy `coop_battle.c` orchestration (WSELoaderServer + `battle_result.txt`) installed for HOST/CLIENT but superseded by ENet IPC~~ `src/coop_battle.c`/`.h` deleted (`fd0e088`, smoke 2026-07-11); `src/` now holds only `coop_campaign.c` + `shared/`, and the campaign ENet channel it fed (port 7240) was retired later (project-state, IPC protocol) | `src/coop_campaign.c` |
| C4 | ✅ siege (7) | ~~Battle types 3–6 (defend siege, village raids, bandit lair) defined + loader-handled but never launched~~ Closed as documented, not removed (`1dc8fec`): `module_constants.py:2113–2116` keeps types 3–6 as defined-but-not-launched; only types 1/2 launch. The bandit-lair map entry point is parked in `docs/DEFERRED.md` (D2) | `module_constants.py` + `module_coop_scripts.py` |
| C5 | ✅ xp-sync (5) | ~~ch125 ev 22 pushes `num_upgradeable`, not XP — misnamed constant + wrong project-state row~~ Renamed `party_stack_num_upgradeable` (`header_common.py:188`) + `coop_send_party_upgradeable_to_client`; project-state row corrected (`1dc8fec`) | `header_common.py` + project-state |
| C6 | ✅ inventory (4) | ~~Orphaned raw-slot 0–19 mirror in ev-15 recv arm (real baseline is slots 160+)~~ Mirror deleted (`1dc8fec`); the ev-15 arm (`module_coop_scripts.py:12751`) now writes the troop only through `coop_inv_recv_mirror_ok` (B6) and updates the snap baseline slots | `module_coop_scripts.py` ev-15 recv arm |
| C7 | ✅ inventory (5) | ~~ch49 ev 13 `request_inv_sync` — handler exists, no sender (inventory pre-warmed on join)~~ Constant + handler deleted (`1dc8fec`), then **deliberately re-added for B3** (`2f2f2bc`) with a real sender: `wse_window_opened` (`module_scripts.py:51228`) requests the authoritative baseline re-push on inventory open. Superseded, not dead | `header_common.py:270` + `module_scripts.py` + `module_coop_scripts.py` |
| C8 | ✅ party-screen (4) | ~~ch49 ev 8/9 `party_sync_begin/stack` — defined, dead (roster syncs via C-layer snapshot/delta)~~ Deleted (`1dc8fec`); the ids were since reclaimed — 8 = `identify` (steamid persistence, `ce0e287`), 9 = `request_party_upgradeable` (`header_common.py:260–266`) | `header_common.py` + project-state |

### D. Campaign server load (dossier `campaign-server-tick.md`, 2026-09-20)

| # | Flow (src) | What's wrong | Owner |
|---|------------|--------------|-------|
| D1 | ✅ **verified** campaign-server-tick (1) | ~~`(6, ...)` DEBUG all-parties-visible trigger: `party_set_flags` broadcasts one net event per active party per fire to every client (opcode 1603 has no already-set check), and position replication is suppressed for a client until its event backlog drains~~ Gated off by default (`562482c`): fires only on a campaign server launched via `coop_launch_all_debug.bat` (`COOP_DEBUG_REVEAL=1` -> `coop server cfg campaign.wsedict{debug reveal}` -> `$g_coop_debug_reveal`). The 2026-09-20/21 "verified" was wrong: the plugin wrote the dict with underscores while the module's quick strings resolve to spaces, so the gate never opened (`6a72f6b` fixed the names; `$g_coop_debug_reveal` read 1 live on 2026-09-24 with a player connected). Residual: the debug launch still broadcasts per fire | `module_simple_triggers.py:263` + `src/coop_campaign.c` + `deploy/scripts/coop_launch_all_debug.bat` |
| D2 | ✅ campaign-server-tick (2) | ~~Vanilla bandit-lair reveal walked all parties against `p_main_party` on the server, broadcasting per hit~~ Gated SP-only (`b6b295b`, build green, not runtime-tested); coop reveal parked in `docs/DEFERRED.md` | `module_simple_triggers.py` 0.1-interval trigger |
| D3 | ✅ campaign-server-tick (4) | ~~Backlogged client pinned to 10 Hz by a miscompiled ping term in `sendToPlayer`~~ `[NetTuning] BacklogPeriodMs` re-points the ceiling load's operand at a plugin float (`226e956`); apply-verified on both dedicated exes 2026-09-20, drain effect not yet measured with a client | `src/shared/nettune.c` |
| D4 | ✅ campaign-server-tick (5) | ~~240 fps main loop~~ 100 (`197f230`, config only, not runtime-tested; the deployed game-dir copy must be updated by hand) | `deploy/configs/server_config.ini` |
