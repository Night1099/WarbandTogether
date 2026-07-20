Warband Coop Mod -- Install
===========================

1. You need Mount & Blade: Warband (Steam). You do NOT need to install
   WSE2 yourself -- this zip ships the exact pinned WSE2 engine build
   (1.174 rev 1145) with the coop binary patches already applied. Do not
   update or replace mb_warband_wse2.exe; a different build will crash.

2. Extract the contents of this zip directly into your Warband install
   directory, e.g.:
      <SteamLibrary>\steamapps\common\MountBlade Warband\

   This will place files as follows:
   - CoopWSEPlugin.dll, winmm.dll, winmm_sys.dll, dinput8.dll,
     coop_loader.dll, warband_coop.asi, char_screen_hooks.asi
     -> game root directory
   - coop.ini -> game root directory
   - Configs\*.txt, *.ini -> game root Configs\ directory
   - Modules\NativeCoop\ -> game root Modules\ directory
   - coop_launch_all.bat, coop_*_server.bat, coop_client2.bat -> game root directory

3. JOINING as a player (most installs): the shipped coop.ini already
   points at the host's IP. Launch the game via mb_warband_wse2.exe
   (NOT mb_warband.exe), pick the NativeCoop module, and connect via
   the MP browser -- the ASI DLL auto-injects the server entry from
   coop.ini. If the host's IP changes, edit the HostIP line in coop.ini.

4. HOSTING (one machine only): no coop.ini change is needed -- the
   server exes auto-detect their role; only HostIP matters (players
   point it at the host). Launch the servers via the .bat files from
   the game root:
   - coop_launch_all.bat [N]           -- campaign server + N battle slots (default 2, max 4) + client
   - coop_campaign_server.bat          -- runs the campaign dedicated server
   - coop_battle_server_<n>.bat (0-3)  -- runs a battle server slot (run multiple for pool)
   - coop_client2.bat                  -- example client launcher
   Allow the battle-pool ports through Windows Firewall (once, as admin):
      netsh advfirewall firewall add rule name="Warband Coop" dir=in action=allow protocol=UDP localport=7240-7267

Notes
-----
- The winmm.dll is a proxy loader that forwards all exports to
  winmm_sys.dll (a copy of the system winmm). Do not replace winmm_sys.dll.
- WSE2 binary patches to mb_warband_wse2.exe are applied at runtime; you
  do not need to patch the game executable manually.
- Port forwarding: If running on a public server, forward UDP/TCP ports
  7240-7247. Port 7242 (ENet IPC) is local-only; battle slots use fixed
  ports (7241/7243/7245/7247, one per BattleServer_<n>.txt slot). The
  slot pool auto-adapts to which slots are RUNNING, not which ports they
  use -- each slot's port never changes.
