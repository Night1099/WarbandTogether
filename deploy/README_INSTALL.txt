Warband Coop Mod -- Install
===========================

Full step-by-step guide with troubleshooting:
https://github.com/Night1099/WarbandTogether/blob/main/docs/INSTALL.md

1. You need Mount & Blade: Warband (Steam). You do NOT need to install
   WSE2 yourself -- this zip ships the exact pinned WSE2 engine build
   (1.174 rev 1145) with the coop binary patches already applied. Do not
   update or replace mb_warband_wse2.exe; a different build will crash.

2. Extract the contents of this zip directly into your Warband install
   directory, e.g.:
      <SteamLibrary>\steamapps\common\MountBlade Warband\

   This will place files as follows:
   - CoopWSEPlugin.dll, winmm.dll, winmm_sys.dll, dinput8.dll,
     warband_coop.asi
     -> game root directory
   - coop.ini.example -> game root directory (the zip never ships a
     coop.ini so an upgrade extract can't wipe your configured one)
   - Configs\*.txt, *.ini -> game root Configs\ directory
   - Modules\NativeCoop\ -> game root Modules\ directory
   - coop_launch_all*.bat, coop_*_server.bat, coop_client2.bat -> game root directory

3. JOINING as a player (most installs): FIRST INSTALL ONLY, rename
   coop.ini.example to coop.ini (it already points at the host's IP).
   On upgrades, keep your existing coop.ini -- the zip deliberately
   does not overwrite it. Launch the game via mb_warband_wse2.exe
   (NOT mb_warband.exe), pick the NativeCoop module, and connect via
   the MP browser -- the ASI DLL auto-injects the server entry from
   coop.ini. If the host's IP changes, edit the HostIP line in coop.ini.

4. HOSTING (one machine only): no coop.ini change is needed -- the
   server exes auto-detect their role; only HostIP matters (players
   point it at the host). Launch the servers via the .bat files from
   the game root:
   - coop_launch_all.bat [N]           -- campaign server + N battle slots (default 2, max 4) + client
   - coop_launch_all_debug.bat [N]     -- same, every party visible on the map (no fog of war; debugging)
   - coop_campaign_server.bat          -- runs the campaign dedicated server
   - coop_battle_server_<n>.bat (0-3)  -- runs a battle server slot (run multiple for pool)
   - coop_client2.bat                  -- example client launcher
   Allow the battle-pool ports through Windows Firewall (once, as admin):
      netsh advfirewall firewall add rule name="Warband Coop" dir=in action=allow protocol=UDP localport=7240-7247 profile=any
   IMPORTANT: profile=any matters. The allow rules Windows creates from
   its "allow access?" popups are often scoped to the Public profile
   only; on a Private (home) network they do nothing and remote clients
   get "Unable to connect" while local play still works. If remote joins
   ever break and the servers are running, re-check this rule exists and
   covers all profiles -- firewall resets and Windows updates have been
   known to remove it.
   If joiners SEE the server row but get "Unable to connect", look for a
   leftover BLOCK rule (clicking "Cancel" on a firewall popup creates
   one). From an admin PowerShell, list suspects and disable them:
      Get-NetFirewallRule -Direction Inbound -Action Block -Enabled True | ForEach-Object { $p = ($_ | Get-NetFirewallPortFilter).LocalPort -join ','; $a = ($_ | Get-NetFirewallApplicationFilter).Program; if ($p -match '72[46]' -or $a -match 'warband') { $_.DisplayName } }
      Disable-NetFirewallRule -DisplayName "<name from the list>"

5. JOINING VIA STEAM INVITE: the host must have their game running with the
   Steam bridge up (SteamHost=1 in their coop.ini). Click "Join Game" on
   the host's Steam friends entry -- or on anyone already playing on
   that server (invites chain). The host or any joiner can also
   right-click a friend -> "Invite to Game". Your friend does not need to
   configure anything in coop.ini. Accepting an invite auto-joins: once
   the tunnel comes up (first invite takes ~5-10 seconds) the game
   navigates itself into the multiplayer browser and connects to the
   "COOP Direct" row on the LAN tab, zero clicks. If the server has a
   [Coop] Password= and your own coop.ini does not carry the same line,
   the auto-join stops at the browser -- type the password in the
   browser's password box and join the COOP Direct row by hand.
   Notes: your game AND Steam must ALREADY be running (the invite won't
   launch the game, and Steam must be up before/within 2 minutes of the
   game starting). If you were already connected to a server, leave it
   first and click the invite again; in a singleplayer battle the
   auto-join waits until the mission ends. One Steam quirk: two people
   already in the same session lose the Join Game / Invite to Game
   entries toward each other (they still show toward everyone else).
   Invite feedback goes to warband_coop.log in the game root, not the
   screen; if a click seems to do nothing, the log says why (usually:
   still connected to a server, or the tunnel is already up -- just
   join COOP Direct).

6. SETTING A PASSWORD: the host sets one line, Password=..., in the [Coop]
   section of their coop.ini -- it applies to the campaign server and every
   battle server in the pool. Joiners type the password into the MP
   browser's password field when connecting; a wrong password gets the
   engine's normal reject. Joiners should ALSO put the same Password= line
   in their own coop.ini so automatic battle-server hops carry it (the hop
   can't reuse what you typed into the browser).

Notes
-----
- The winmm.dll is a proxy loader that forwards all exports to
  winmm_sys.dll (a copy of the system winmm). Do not replace winmm_sys.dll.
- The binary patches (see docs\wse2-binary-patches.md) are on-disk
  changes to mb_warband_wse2.exe; the shipped exe is already patched.
  No manual patching is needed.
- Port forwarding: If running on a public server, forward UDP/TCP ports
  7240-7247. Port 7242 (ENet IPC) is local-only; battle slots use fixed
  ports (7241/7243/7245/7247, one per BattleServer_<n>.txt slot). The
  slot pool auto-adapts to which slots are RUNNING, not which ports they
  use -- each slot's port never changes.
