WarbandTogether -- Quick Install
================================

Full step-by-step guide with troubleshooting:
https://github.com/Night1099/WarbandTogether/blob/main/docs/INSTALL.md

1. REQUIREMENTS
   You need Mount & Blade: Warband (Steam, v1.174) on Windows 10+.
   Do NOT install or update WSE2 yourself -- this zip already includes
   the pinned WSE2 rev 1145 engine with all coop patches applied. Do not
   replace mb_warband_wse2.exe.

2. INSTALL (EVERYONE)
   Extract this zip directly into your Warband folder (next to
   mb_warband.exe), e.g.:
      <SteamLibrary>\steamapps\common\MountBlade Warband\

   Upgrading? Extract over your existing install. The zip ships
   coop.ini.example (never coop.ini), so your config won't be overwritten.

   Key files installed:
   - mb_warband_wse2.exe + patched dedicated servers -> game root
   - CoopWSEPlugin.dll, winmm.dll, winmm_sys.dll, dinput8.dll,
     warband_coop.asi, coop.ini.example -> game root
   - coop_launch_all.bat, coop_launch_all_debug.bat,
     coop_campaign_server.bat, coop_battle_server_0..3.bat -> game root
   - Configs\*.txt, *.ini -> Configs\
   - Modules\NativeCoop\ -> Modules\

3. CONNECT VIA STEAM (RECOMMENDED -- NO PORT FORWARDING)
   Host only:
   - Rename coop.ini.example to coop.ini (first install only).
   - Under [Steam], uncomment:
        SteamHost=1
   - Optional: set a Password= under [Coop] or list AllowedSteamIDs=
     under [Steam] (by default anyone who clicks Join Game can connect).

   Joining players:
   - Do NOT edit coop.ini (unless the host set a password; see step 6).
   - Start Steam first, launch mb_warband_wse2.exe, pick NativeCoop.
   - Click "Join Game" on the host (or any friend already playing) in
     Steam, or accept an "Invite to Game".
   - Wait ~5-10 seconds -- the game opens the browser and joins
     automatically. (If already on a server, disconnect first; if in a
     singleplayer battle, auto-join waits until you leave it.)
   - Check warband_coop.log in the game root if an invite seems ignored.

4. CONNECT VIA LAN / DIRECT IP (SKIP IF USING STEAM)
   Host:
   - Run ipconfig in Command Prompt and share your IPv4 Address.
   - Leave your own coop.ini alone.
   - Open UDP ports 7240-7247 in Windows Firewall (Administrator PowerShell):
        netsh advfirewall firewall add rule name="Warband Coop" dir=in action=allow protocol=UDP localport=7240-7247 profile=any
     (profile=any matters on home Private networks. If joiners see the
     server but get "Unable to connect", check docs/INSTALL.md for how to
     clear leftover Windows Firewall block rules.)
   - Hosting over the internet without Steam? Also forward UDP 7240-7247
     on your router.

   Joining players:
   - Rename coop.ini.example to coop.ini (first install only).
   - Set HostIP=<host's IP> under [Coop] (leaving 127.0.0.1 breaks
     dedicated battle joins).
   - Launch mb_warband_wse2.exe, pick NativeCoop, go to Multiplayer ->
     Join a Game, and click the server on the LAN tab.

5. START THE SERVERS (HOST ONLY)
   Run from the Warband folder:
      coop_launch_all.bat

   Starts the campaign server, 2 battle servers (use "coop_launch_all.bat 4"
   for up to 4), and your game client. Keep the server console windows open.

   World saves:
   - Saved automatically at:
        Documents\Mount&Blade Warband WSE2\NativeCoop\Savegames\sg00.sav
   - Type "campaign_save" in the campaign server console before closing it
     (or wait for "[WORLD SAVE] finished" after the last player leaves).
   - Delete or move sg00.sav to start a fresh world or after major updates.
   - coop_launch_all_debug.bat reveals the whole map and saves to sg01.sav.

6. SERVER PASSWORD (OPTIONAL)
   - Host: set Password=<password> (max 47 chars) under [Coop] in coop.ini
     and restart the servers.
   - Joiners: add the exact same Password= line to your own coop.ini so
     Steam auto-join and dedicated battle-server hops stay authenticated.

NOTES
-----
- winmm.dll is a proxy loader forwarding to winmm_sys.dll. Keep both.
- Leave [NetTuning] in coop.ini unchanged for best connection quality.
- Port 7242 is local-only IPC; campaign uses 7240 and battle slots 0-3
  use 7241, 7243, 7245, 7247.
