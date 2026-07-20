# Coop Flow Dossiers

One dossier per core flow. Each documents how the flow works (sequence,
anchors, invariants) and audits it against native/engine ground truth
(`OK`/`DIVERGES`/`UNKNOWN` verdicts). Template: `TEMPLATE.md`.

| Flow | Dossier | Status |
|------|---------|--------|
| Battle pipeline (dedicated battle end-to-end) | `battle-pipeline.md` | audited |
| Siege (coop siege battle types + local siege) | `siege.md` | audited |
| XP sync (char XP, stack XP, local-fight XP) | `xp-sync.md` | audited |
| Inventory sync (inv screen, equip pushes) | `inventory-sync.md` | audited |
| Party screen sync (roster, dismiss, upgrade) | `party-screen-sync.md` | audited |

## Engine findings map

Which existing RE/audit material is relevant to each flow. Filled in as each
dossier is written.

| Flow | Relevant findings / docs |
|------|--------------------------|
| Battle pipeline | `docs/BATTLE_RESULTS_PIPELINE_AUDIT.md`, `patches/WarbandDedicated/findings.md`, `docs/superpowers/specs/2026-03-22-warband-coop-campaign-sync-design.md` |
| Siege | `docs/plans/siege-coop-plan.md`, `battle-pipeline.md` shared tail |
| XP sync | `docs/SYNC_REDESIGN.md`, `docs/sync-systems/`, `patches/Warband/findings.md` (kill-XP paths), `patches/WSE2Dedicated/kb.h` |
| Inventory sync | `docs/RE_NATIVE_SCREENS.md`, `docs/SP_SCREEN_RECREATION.md` |
| Party screen sync | `docs/RE_NATIVE_SCREENS.md`, `docs/Screen_Session.md` |

RE symbol knowledge lives in `patches/<project>/kb.h`; narratives in
`patches/<project>/findings*.md`. Dossiers link into those files — they are
the ground-truth store, this index is just the map. New engine RE from this
audit: `patches/Warband/findings.md` ("Native kill-vs-wound (surgery) rules",
"Engine mission kill-XP paths", "all_enemies_defeated opcode semantics");
`patches/Warband_WSE2/findings.md` and `patches/WarbandDedicated/findings.md`
(bootstrap: kb.h grown to 3094 / 2653 entries, Ghidra projects built).

## Consolidated fix list

Every `DIVERGES` verdict across the five dossiers, ranked by player impact.
"Src" points to the dossier fix-list row for full context.

**Status:** A1–A5 and B1 are **implemented** in commit `50f4ac1` (full
27-step module build green) and marked ✅ below. **B1 is runtime-verified
(2026-07-10)** — legit edits stick, no false `[INV GUARD]` rejects; its
dossier verdict is flipped to OK. Runtime testing of B1 also exposed and
fixed a join-push-ordering bug (char sync must precede inventory — see
inventory-sync.md invariants). A1–A5 are **not yet runtime-tested** —
validate them in the wave-2 smoke test before relying on them. Groups B2–B3
remain open. **Group C is done** — implemented in `1dc8fec` (module) +
`fd0e088` (C layer), runtime smoke passed 2026-07-11, all C verdicts
flipped to OK. That smoke also surfaced a pre-existing player-blocking
symptom of A7 (post-dedicated-battle stuck player — see the A7 row).

### A. Gameplay correctness (affects live play)

| # | Flow (src) | What's wrong | Owner |
|---|------------|--------------|-------|
| A1 | ✅ **verified** battle-pipeline (1) | ~~Surgery save omits native's 0.25 base~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10 | `module_coop_scripts.py:7072–7077` |
| A2 | ✅ **verified** xp-sync (4) | ~~Heroes double-credited XP on dedicated battles~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10 (pool share is the sole hero credit) | `module_coop_scripts.py:5251`, `:9430–9432` |
| A3 | ✅ **verified** xp-sync (2) | ~~Local-fight XP overpays ~34% (no rand roll)~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10 (`pool 603 x roll 66% = 397` exact). Loot gold remains unpaid — owned by A7 | `module_game_menus.py` debrief |
| A4 | ✅ **verified** party-screen (2) | ~~Troop upgrades are free~~ Gold cost fixed (`50f4ac1`) + runtime-verified 2026-07-10; server-side upgrade-XP decrement remains a minor authority-hardening follow-up | `module_coop_scripts.py:8865–8875` ev-11 arm |
| A5 | ✅ siege (5) | Winning a **dedicated** siege never captures the center (the local path was also broken in practice — player_no-keyed mark; fixed + runtime-verified in `13ebcad`) | `module_coop_scripts.py` BATTLE PIPELINE |
| A6 | ✅ **verified** siege (3) | ~~Attached defender parties sit out the siege~~ Fixed (`67239e5..d7955b7`) + runtime-verified 2026-07-19 — attachments fight as enemy1..N, proximity AI allies as ally1..N, per-party casualty round-trip. Follow-up: tighten attacker selection filter (see NEXT_SESSION.md) | `module_coop_scripts.py` `coop_write_battle_data` |
| A7 | battle-pipeline (6) | Battle wins pay XP only — no gold/loot, prisoners, or `battle_political_consequences`. The player-blocking disengage sub-piece (stuck player + lingering 0-troop enemy) is **fixed + runtime-verified 2026-07-11** (`f85c30e`/`d82d879`/`d865990` — enemy parties resolved via dict ids, since the rejoiner's party is rebuilt); the economic/political consequences remain open | `module_coop_scripts.py` BATTLE PIPELINE |
| A8 | siege (6) | Local-siege capture skips native consequences (lord fate, prisoners, relations, renown, war damage) | `module_coop_scripts.py` |
| A9 | battle-pipeline (3) | Round-end is reserve-blind and instant (no settle delay); a team with unspawned waves loses when on-field agents hit zero; no retreat path | `module_coop_mission_templates.py:896–949` |

### B. Server authority / correctness

| # | Flow (src) | What's wrong | Owner |
|---|------------|--------------|-------|
| B1 | ✅ **verified** inventory (6) | ~~`inv_change` applied verbatim server-side~~ Fixed (`50f4ac1`) + runtime-verified 2026-07-10 | `module_coop_scripts.py` ev-14/15 arms |
| B2 | inventory (1) | No push-on-mutation: server-side inventory changes don't reach a live client until rejoin | `module_coop_scripts.py` ECONOMY/MISC push helpers |
| B3 | inventory (2) | Inventory close-diff baseline is an open-time client-troop snapshot with no ready-gate (char-sync's documented receive-handler pattern not applied) | `module_scripts.py` `wse_window_opened` + recv arms |

### C. Dead code / protocol-doc drift (`.claude/rules/project-state.md` fixes)

| # | Flow (src) | What's wrong | Owner |
|---|------------|--------------|-------|
| C1 | battle-pipeline (7) | ch125 ev 14 `return_to_campaign` — defined, documented, never sent/handled | `header_common.py` + project-state |
| C2 | battle-pipeline (8) | ASI writes `s57` reconnect address; nothing consumes it and vanilla formatting clobbers the register | `src/asi/coop.c` + `module_simple_triggers.py` |
| C3 | battle-pipeline (9) | Legacy `coop_battle.c` orchestration (WSELoaderServer + `battle_result.txt`) installed for HOST/CLIENT but superseded by ENet IPC | `src/coop_battle.c` + `src/coop_campaign.c` |
| C4 | siege (7) | Battle types 3–6 (defend siege, village raids, bandit lair) defined + loader-handled but never launched | `module_constants.py` + `module_coop_scripts.py` |
| C5 | xp-sync (5) | ch125 ev 22 pushes `num_upgradeable`, not XP — misnamed constant + wrong project-state row | `header_common.py` + project-state |
| C6 | inventory (4) | Orphaned raw-slot 0–19 mirror in ev-15 recv arm (real baseline is slots 160+) | `module_coop_scripts.py:8452–8454` |
| C7 | inventory (5) | ch49 ev 13 `request_inv_sync` — handler exists, no sender (inventory pre-warmed on join) | `header_common.py` + `module_coop_scripts.py` + project-state |
| C8 | party-screen (4) | ch49 ev 8/9 `party_sync_begin/stack` — defined, dead (roster syncs via C-layer snapshot/delta) | `header_common.py` + project-state |
