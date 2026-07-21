# Mount & Blade: Warband Co-op Campaign

Co-op campaign mod for Mount & Blade: Warband using WSE2's multiplayer campaign mode. Players join a shared campaign map with their own persistent characters, encounter enemies together, and fight battles in multiplayer — with casualties and XP flowing back into the campaign.

## Status — v0.0.x, early alpha

> **⚠️ Set your expectations:** this is **not a fully playable mod yet**. The
> core coop loops below work in testing, but do not expect a full campaign
> playthrough — battle loot/gold and political consequences are missing,
> some siege and economy behavior diverges from singleplayer, and longer
> sessions will hit bugs and desyncs. Grab the current build from the
> [Releases page](https://github.com/Night1099/WarbandTogether/releases)
> and report what breaks via Issues.

**Just want to play?** Follow the step-by-step [install guide](docs/INSTALL.md).

**Working:**
- WSE2 campaign server (dedicated, port 7240) with multiple players on the shared campaign map
- **Battle server pool** — up to 4 dedicated battle servers (ports 7241/7243/7245/7247, one per slot), allocated per encounter; the pool auto-adapts to however many slots are running
- **Battle chooser** — the battle initiator auto-connects; everyone else presses B on the campaign map to open a chooser listing every open battle (enemy + troop count) and can join any of them. Players fight one life with their campaign character and equipment, then rejoin the campaign
- Battle results applied to the campaign per slot: casualties, wounds, and XP shares
- **Persistent characters** — per-player `.wsedict` files on the campaign server; stats, equipment, gold, XP, and health survive reconnects
- **Native screens in coop** — character, inventory, and trade screens work against server-authoritative state (snapshot-diff sync on screen close)
- **Local fights** — singleplayer-style battles (including sieges) run locally on the client when no battle server round-trip is needed, with results reported back
- **Direct Connect** — the client ASI injects the campaign server into the MP browser from `coop.ini`; no LAN required
- Terrain-appropriate battle scenes (plain/steppe/snow/desert/forest variants)
- 5-minute autosave on the campaign server

See [docs/INSTALL.md](docs/INSTALL.md) for the player/host install guide, `docs/flows/` for how each core flow works (battle pipeline, siege, XP sync, inventory sync, party-screen sync), and `docs/BUILD.md` for the build chain.

## Requirements

- Mount & Blade: Warband 1.174
- [WSE2](https://forums.taleworlds.com/index.php?threads/wse2-warband-script-enhancer-2.371084/) **pinned at revision 1145** (v1.1.4.5, Mar 2026) — all binary patches (`docs/wse2-binary-patches.md`) and hook addresses are keyed to these exact binaries; upgrading WSE2 is a dedicated porting task, not a drop-in. Release zips ship these binaries pre-patched — you only need your own WSE2 install when building from source
- Python 2.7 (module system build)
- Visual Studio with MSVC x86 (DLL builds)

## Quick Start

1. Build everything (see `docs/BUILD.md`):
   - Module system: full 27-step chain — writes `.txt` output straight into `Modules/NativeCoop/`
   - C layer: `build\build.bat` (client ASI), `build\build_plugin.bat` (host plugin), `build\build_loader.bat` (winmm proxy)
   - Every successful C build ends with `build\deploy.bat`, which copies the artifacts into the game directory automatically
2. The client `mb_warband_wse2.exe` needs four small binary patches (auto-connect, ASLR off, writable .text, dual-port LAN scan) — see `docs/wse2-binary-patches.md`. The exe in a release zip is already patched
3. Launch servers from the game directory:
   - `coop_launch_all.bat` (campaign server + N battle slots in one go), or individually:
   - `coop_campaign_server.bat` (campaign, port 7240)
   - `coop_battle_server_<n>.bat` (battle slot n = 0–3, ports 7241/7243/7245/7247)
4. Launch client: WSE2 launcher → NativeCoop → Multiplayer → join the campaign server
5. **On each client machine, set `HostIP` in `coop.ini` to the server's IP.** The campaign join works without it (LAN browser), but battle joins build their address from `HostIP` — leaving the `127.0.0.1` default makes clicking a battle silently bounce you to the MP menu

## Architecture

Three processes cooperate:

```
CLIENT (mb_warband_wse2.exe + warband_coop.asi)
  |  MP browser join (port 7240)   |  B-key battle chooser (port 7241 + 2*slot)
  v                                 v
CAMPAIGN SERVER (dedicated campaign + CoopWSEPlugin.dll via winmm proxy)
  |  ENet IPC (port 7242, persistent per-slot connection)
  v
BATTLE SERVER POOL (up to 4x dedicated + CoopWSEPlugin.dll via winmm proxy)
  slot s (0-3): port 7241+2s, identity from COOP_BATTLE_SLOT env var
```

Repo layout:

```
src/asi/coop.c          — Client ASI: browser injection, engine hooks, auto-connect
src/                    — Host plugin: coop_campaign.c / plugin_main.cpp; battle_ipc.h (IPC wire)
src/shared/             — Shared C: hooks, battle-server ENet IPC, wsedict, module globals,
                          crash reporting, engine address tables (warband_addrs_wse2.c/h)
src/loader/             — winmm.dll proxy that loads the plugin on dedicated servers
asi_loader/             — dinput8.dll proxy ASI loader (client)
build/                  — Build scripts; deploy.bat runs after every successful build
bin/                    — Build outputs (not tracked)
enet/                   — Vendored ENet
wse2work/Native-Coop-master/   — Module system (the bulk of the mod's logic)
  module_scripts.py            — Vanilla campaign logic; forwards network events to the coop dispatchers
  module_coop_scripts.py       — All coop logic: persistence, lifecycle, dispatchers, battle pipeline, char sync
  module_coop_mission_templates.py — Coop battle mission template
  module_game_menus.py         — Encounter flow, battle launch
deploy/                 — Server configs, launch scripts, coop.ini template
docs/                   — INSTALL.md, BUILD.md, wse2-binary-patches.md, flows/ (per-flow dossiers)
```

## How It Works

1. **Campaign server** runs WSE2 dedicated campaign mode: parties, encounters, diplomacy, time. All persistent player state lives in per-player `.wsedict` dict files — the server is authoritative; clients receive pushes and send back deltas over the campaign event channels.
2. When players encounter an enemy, the campaign server allocates a free battle slot, writes battle data (scene, factions, troop stacks) to that slot's dict file, and signals the slot's battle server over ENet IPC. All clients are told which port the battle is on.
3. **Battle server** loads the battle; the initiator auto-connects, everyone else can press B and pick the battle from the chooser. Players spawn with their campaign stats and equipment and fight one life.
4. Battle end writes casualties back to the dict; when participants rejoin the campaign map, the server applies losses, wounds, and XP shares and frees the slot.
5. Small fights and sieges can instead run **locally** on the client as singleplayer missions, reporting the outcome through the same result pipeline.

## Config — coop.ini

```ini
[Coop]
Port=7240
HostIP=127.0.0.1
BattlePort=7241
Module=NativeCoop
```

Set `HostIP` to the campaign server's IP on each client machine (there is no mode key — server role comes from the exe name). The template lives at `deploy/coop.ini`; `build\deploy.bat` installs it into the game directory if missing.

`HostIP` matters on clients even when the campaign server is found via the LAN browser: the ASI writes it into string register s59, which the module uses to build the battle-server address. A client left on the `127.0.0.1` default joins the campaign fine but bounces to the MP menu on every battle join.

## Contributing

Issues and PRs are welcome — see `CONTRIBUTING.md` for build pointers, the issue-report template, and the contribution license grant. Third-party component licenses are collected in `THIRD_PARTY_LICENSES.md`.
