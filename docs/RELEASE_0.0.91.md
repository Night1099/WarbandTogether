# v0.0.91 — Launcher Fix

A small fix-up release for v0.0.9: the included launchers now start the game and battle servers in the right module on every PC.

> **Before you update:** This release only changes the launcher scripts. Your characters and world save carry over unchanged from v0.0.9.

## Bug Fixes

- **Launcher Starts the Wrong Module:** `coop_launch_all.bat` and `coop_battle_server_0.bat`–`coop_battle_server_3.bat` passed the module in a form the game ignores, so the client and battle servers loaded whichever module you had played last (often `Native`). Depending on your setup, the campaign server was missing from **Multiplayer → Join a Game → Local Area Network**, or joining a dedicated battle restarted the game in `Native` and the battle expired with nobody in it. The launchers now always start `NativeCoop`. If you made your own shortcuts or scripts, use `--module NativeCoop`, not `-m NativeCoop`.

  Thanks to **sketzhen** for the detailed report and the fix ([#3](https://github.com/Night1099/WarbandTogether/issues/3)).

## Known Issues

Everything listed under **Known Issues** in the [v0.0.9 release notes](https://github.com/Night1099/WarbandTogether/releases/tag/v0.0.9) still applies.
