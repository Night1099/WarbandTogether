# Flow: Party Screen Sync (roster, dismiss, upgrade)

**Status:** AUDITED
**Validated against commit:** `7161f85` (doc refresh 2026-09-21: every
`module_coop_scripts.py` / `module_simple_triggers.py` anchor re-pointed
after the Plan 3/4 relation + quest scripts shifted them; row 8 now
records the stack XP-residual / upgrade-credit keys the codec carries
(`1380d4b`) and the rejoin stack-index fix (`f1cfc21`, runtime-verified
2026-08-29/30 -- see `xp-sync.md`); protocol and verdicts unchanged).
Prior stamp `2923381` (line anchors re-verified + ev-9
reuse documented in full static doc audit 2026-08-30; runtime-verified
behavior unchanged since `ce0e287`). Prior stamp `ce0e287` (steamid
persistence, runtime-verified 2026-08-23: char-dict naming is sid-keyed for
Steam-identified players — persistence reference only, the roster sync
protocol is unaffected. Prior stamp `9558722`: A4 residual — server-side
upgrade-credit consumption — fixed in the B2B3 merge, runtime smoke
2026-07-25; prior stamp `a68b8ae`)

## Scope

How player-party roster edits made in the native party screen (dismissals
and upgrades) reach the authoritative campaign-server party, and how the
client's view of its roster is populated. Entry points: native party window
open/close. Exit state: server party mutated, char dict saved. Recruitment
(ch49 ev 23 / ch125 ev 33–34) is center-flow territory; the battle-server
temp-party sorting is battle machinery — both only referenced here.

Module paths relative to `wse2work/Native-Coop-master/`.

## Sequence diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant CS as Campaign Server

    note over CS,C: Roster view: party stacks reach the client via the<br/>engine's native MP session replication,<br/>upgradeable counts via ch125 ev 22 (see xp-sync.md)
    C->>CS: ch49 9 request_party_upgradeable (post-connect, once<br/>party stacks are visible)
    CS->>C: ch125 22 party_stack_num_upgradeable (re-push)
    note over C: party window opens (wse_window_opened):<br/>snapshot troop/size per stack into snap slots;<br/>sends ch49 7 request_char_sync
    note over C: player dismisses/upgrades, window closes
    C->>C: 3-pass diff: decreases → match increases to<br/>upgrade trees → leftovers = dismissals
    C->>CS: ch49 11 party_upgrade (src, dst, n) per match
    C->>CS: ch49 10 party_dismiss (troop, n) per leftover
    CS->>CS: validate (bounds, non-hero, tree, have-count),<br/>apply remove/add, coop_save_character
```

## Code anchors

| # | Step | File | Line | Symbol |
|---|------|------|------|--------|
| 1 | Party snapshot at window open | `module_scripts.py` | 51231–51266 | `wse_window_opened` (window_party arm: flushes a still-open session 51232–51236, snapshots 51248–51264), `$g_coop_party_screen_open`; also sends ch49 ev 7 `request_char_sync` (`:51246–51247`) |
| 2 | Close-diff pass 1: decrease deltas | `module_coop_scripts.py` | 9667–9685 | `coop_party_client_diff_and_send` (def 9660–9743), snap slots `slot_coop_party_snap_begin` + stride |
| 3 | Close-diff pass 2: upgrades matched via `troop_get_upgrade_troop` | `module_coop_scripts.py` | 9687–9730 | sends ch49 ev 11 |
| 4 | Close-diff pass 3: leftover decreases -> dismissals | `module_coop_scripts.py` | 9732–9742 | sends ch49 ev 10 |
| — | Poller gate/dispatch into the diff pass | `module_simple_triggers.py` | 4731–4735 | screen-close flag transition 1->2, `call_script script_coop_party_client_diff_and_send` |
| — | Post-connect pull of upgradeable counts | `module_simple_triggers.py` | 4687–4701 | sends ch49 ev 9 `request_party_upgradeable` once party stacks are visible (one-shot, `$g_coop_upg_pull_sent`) |
| 5 | Server dismiss arm (validated) | `module_coop_scripts.py` | 11832–11847 | `coop_ev_cli_party_dismiss`; bounds 1–100, non-hero, have-count, save; dispatched 12996–12999 |
| 6 | Server upgrade arm (validated) | `module_coop_scripts.py` | 11850–11925 | `coop_ev_cli_party_upgrade`; upgrade-tree check, bounds, have-count, gold charge 11880–11885, credit consumption 11889–11919, ev-22 re-push 11922, save; dispatched 13001–13005 |
| 7 | Upgradeable counts push | `module_coop_scripts.py` | 14720–14735 | `coop_send_party_upgradeable_to_client` (ch125 ev 22, see `xp-sync.md`) |
| 8 | Char dict party codec (troop, size, wounded, stack XP residual, upgrade credits) | `module_coop_scripts.py` | 8030–8072 (save), 8378–8444 (load) | `coop_save_character` (def 7818, wounded write `:8066`); `coop_load_character` (def 8168) rebuilds with `party_clear` + re-add (`:8385–8407`), wounded read `:8395` / applied `:8410`, XP residual + credits restored at the real stack index resolved by troop id (`:8418–8442`, `f1cfc21`) |
| 9 | Battle-server temp-party sort (round transitions only) | `module_coop_scripts.py` | 4088–4118 | `coop_sort_party` (callers `module_coop_mission_templates.py:5354,5359`) |

## State & events

- **Events:** ch49 ID 8 was reclaimed for `identify` (steamid persistence —
  out of this flow's scope). ID 9 was reclaimed for
  `request_party_upgradeable`: the client pulls a re-push of ev-22
  upgradeable counts once its native-replicated party is visible, avoiding
  a hydrate-time race where the server's ev-22 push can arrive before the
  client roster exists (sender `module_simple_triggers.py:4687–4701`;
  handler `module_coop_scripts.py:12928–12932` ->
  `coop_send_party_upgradeable_to_client`). ch49 `party_dismiss`=10,
  `party_upgrade`=11; ch125: `party_stack_num_upgradeable`=22 (upgradeable
  counts; renamed from `party_stack_xp` in the C5 fix) (`header_common.py`).
- **Client globals/slots:** `$g_coop_party_screen_open` (0/1/2 lifecycle),
  party snapshot at `slot_coop_party_snap_begin` + 3-slot stride
  (troop, size, decrease-delta) on `trp_temp_troop`.
- **Roster source:** client party stacks are populated by the engine's
  native MP session replication — not by any ch49/ch125 event. (Earlier
  revisions credited the C-layer `PKT_SNAPSHOT`/`PKT_DELTA` stream; that
  channel never functioned in the dedicated topology and was retired in
  B8, `a68b8ae`.)
- **Persistence:** stacks with wounded counts, stack XP residuals and
  upgrade credits (`@char_party_troop/count/wound/xp/upg_{i}`) in the
  per-player char dict (`coop_char_sid_<acctid>` / `coop_char_<name>`,
  key-builder-owned naming since `ce0e287`). A rejoining player gets a
  REBUILT party (`party_clear` + re-add from the dict, `:8385–8407`):
  party ids do not survive the disconnect, and the player's own stack
  survives the clear at index 0, so every re-added stack sits one slot
  above its dict position (`f1cfc21`).

## Invariants

- The party diff never trusts raw increases: an increase is only sent if it
  matches a snapshot decrease through `troop_get_upgrade_troop` — anything
  else is silently dropped client-side (`module_coop_scripts.py:9687–9730`).
- Server arms re-validate independently (bounds 1–100, non-hero, upgrade
  tree, have-count) — client and server checks are intentionally redundant
  (`module_coop_scripts.py:11832–11925`).
- Every accepted dismiss/upgrade ends in `coop_save_character` — roster
  changes are never memory-only.
- Wounded counts survive the char-dict round trip (`:8066` save, `:8395` load).

## Audit: ours vs. native

| # | Behavior | Ours (anchor) | Native ground truth (evidence) | Verdict |
|---|----------|---------------|--------------------------------|---------|
| 1 | Upgrade structure: tree-validated (both branches), count-bounded, non-hero, have-count-checked on the server | `module_coop_scripts.py:11850–11925` | Same legality rules the native party screen enforces (`troop_get_upgrade_troop` is the same source of truth) | OK |
| 2 | Upgrade **cost**: server charges the native gold cost (`game_get_upgrade_cost` × count) before applying and rejects unaffordable requests, so the server gold push no longer refunds the client's local charge. Fixed in `50f4ac1`, runtime-verified 2026-07-10. Residual fixed in the A4 fold-in (`bdcfd8c`, merged `9558722`, runtime smoke 2026-07-25): the ev-11 arm now consumes the from-stack's `num_upgradeable` credits server-side via op 3906 and re-pushes ev 22 — engine RE proved stacks have no XP field, credits are the only currency | `module_coop_scripts.py:11880–11885` (gold charge), `:11889–11919` (credit consumption); ev-11 arm `coop_ev_cli_party_upgrade` (@ `bdcfd8c`) | Native upgrades consume stack upgrade XP and charge gold in the engine party screen. Coop now matches on both. | OK |
| 3 | Dismiss: non-hero, bounded, have-count-checked; no other consequences | `:11832–11847` | Native party-screen dismissal likewise has no gold/morale consequence for regulars; heroes can't be dismissed this way in native either | OK |
| 4 | ch49 ev 8/9 `party_sync_begin`/`party_sync_stack` constants deleted (`1dc8fec`) — they had no sender and no handler; project-state row corrected (IDs 8-9 marked free) at the time. Smoke passed 2026-07-11. Both IDs were later reclaimed for live traffic: 8 = `identify` (steamid persistence), 9 = `request_party_upgradeable` (this flow) | `header_common.py` | Roster syncs via the engine's native MP replication (the C-layer snapshot/delta stream was retired in B8); the reclaimed IDs carry unrelated, still-live traffic | OK |
| 5 | Roster injection: client cannot add stacks via the diff (drop rule, invariant 1); raw ev-11 forgeries are limited to legal upgrade edges by server validation | `module_coop_scripts.py:9687–9730`; `:11850–11925` | Matches the server-authoritative design intent (the row-2 free-cost hole is closed) | OK |
| 6 | Party size limit: server enforces no cap on upgrades/dismissals (they don't grow the party); recruit paths own the cap question | n/a for this flow | Native party size limit is leadership/renown-driven and enforced at recruitment time — out of this flow's scope, owned by the recruit/center flow | OK |
| 7 | `coop_sort_party` orders battle-server temp parties only (spawn priority at siege round transitions) | `module_coop_scripts.py:4088–4118`; callers `module_coop_mission_templates.py:5354,5359` | Cosmetic/battle-internal; native party ordering rules don't apply to temp parties | OK |

## Fix list

| # | From audit row | What diverges | Suggested owner/layer |
|---|----------------|---------------|------------------------|
| 1 | 2 | ~~Upgrades are free~~ **Done**: gold cost fixed (`50f4ac1`, runtime-verified 2026-07-10); server-side upgrade-credit consumption fixed in the A4 fold-in (`bdcfd8c`, merged `9558722`, runtime smoke 2026-07-25 — reopening the party screen reflects consumed credits via the ev-22 re-push). | `module_coop_scripts.py` ev-11 arm |
| 2 | 4 | ~~Dead ev 8/9~~ **Done** (`1dc8fec`, smoke 2026-07-11): constants removed, project-state table corrected. Note: the removal applied to the then-dead constants only — both IDs were later reclaimed for live traffic (8 = `identify`, 9 = `request_party_upgradeable`). | `header_common.py` + workbench project-state doc |

## Open questions

- Whether native upgrades preserve wounded status on upgraded units (coop's
  remove+add yields healthy upgrades). Parked: minor gameplay nuance,
  cheapest to answer in the wave-2 runtime smoke test rather than engine RE.

## Related docs

- `xp-sync.md` — ev 22 upgradeable push and snapshot-slot machinery.

Workbench documents (not part of the public export — see the citation
note in `README.md`):

- `docs/archive/RE_NATIVE_SCREENS.md`, `docs/archive/Screen_Session.md` — native window
  hooks behind `wse_window_opened`.
- project-state notes — C/DLL layer architecture (IPC-only since B8).
