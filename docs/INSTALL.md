# Install Guide (Players & Hosts)

Step-by-step setup from a clean Warband install to playing coop. This
covers the **release zip** from the
[Releases page](https://github.com/Night1099/WarbandTogether/releases) —
if you want to build from source instead, see `docs/BUILD.md`.

## What you need

- **Mount & Blade: Warband** (Steam), version 1.174
- **Windows 10 or later**
- The latest **WarbandTogether release zip** — it contains everything
  else: the pinned WSE2 engine (rev 1145, coop patches pre-applied), the
  coop DLLs, the compiled NativeCoop module, server configs, and launch
  scripts. Do NOT install WSE2 yourself.

One player **hosts** (runs the servers); everyone, including the host,
also runs a game client. A mid-range PC comfortably runs the campaign
server, a couple of battle servers, and a client at the same time.

## Step 1 — Install Warband

1. Install Mount & Blade: Warband from Steam.
2. Launch it once and quit — this creates the game's config files.

## Step 2 — Extract the zip

1. Find your install folder: Steam → right-click Warband → Manage →
   Browse local files (usually
   `...\steamapps\common\MountBlade Warband\`).
2. Extract the release zip **directly into that folder**. No vanilla
   files are replaced; you get:
   - `mb_warband_wse2.exe` + the other WSE2 engine files (game root)
   - `CoopWSEPlugin.dll`, `warband_coop.asi`, `winmm.dll`,
     `winmm_sys.dll`, `dinput8.dll` (game root)
   - `coop.ini` (game root)
   - `Modules\NativeCoop\` (the mod itself)
   - `Configs\*.txt` / `*.ini` (server configs)
   - `coop_launch_all.bat`, `coop_campaign_server.bat`,
     `coop_battle_server_0..3.bat`, `coop_client2.bat` (game root)

## Step 3 — Point coop.ini at the host

Open `coop.ini` in the game root with any text editor:

```ini
[Coop]
Port=7240
HostIP=127.0.0.1
BattlePort=7241
Module=NativeCoop
```

- **Players:** set `HostIP` to the host's IP address (LAN IP on a LAN,
  public IP or VPN IP over the internet). This is the one setting you
  must change — a client left on `127.0.0.1` may still find the campaign
  server in the LAN browser, but **every battle join will silently bounce
  you back to the multiplayer menu**.
- **Host:** leave `HostIP=127.0.0.1`. Server roles are detected
  automatically from the exe names; there is nothing else to configure.

## Step 4 — Host: start the servers

From the game root:

- `coop_launch_all.bat` — starts the campaign server, 2 battle servers,
  and your game client in one go. Pass a number for more battle slots:
  `coop_launch_all.bat 4` (max 4 — that's how many simultaneous battles
  the pool can run).

Or start things individually:

- `coop_campaign_server.bat` — the campaign server (port 7240)
- `coop_battle_server_0.bat` … `coop_battle_server_3.bat` — one battle
  slot each (ports 7241/7243/7245/7247); run as many as you want, the
  pool adapts automatically

Allow the ports through Windows Firewall once (run as administrator):

```
netsh advfirewall firewall add rule name="Warband Coop" dir=in action=allow protocol=UDP localport=7240-7267
```

**Hosting over the internet:** forward UDP ports 7240–7247 on your
router to the host machine. Port 7242 is server-internal (campaign ↔
battle IPC) and never needs forwarding.

## Step 5 — Everyone: join the campaign

1. Launch `mb_warband_wse2.exe` (NOT `mb_warband.exe`) and pick the
   **NativeCoop** module. Tip: a shortcut with
   `mb_warband_wse2.exe -m NativeCoop` skips the module picker.
2. Multiplayer → Join a game. The campaign server is injected into the
   server list automatically from `coop.ini` — no LAN required. Join it.
3. On your first join you'll go through **character creation**; after
   that your character (stats, equipment, gold, XP, health) is saved on
   the server and survives disconnects and rejoins.

## Step 6 — Play

- **Campaign map:** everyone walks the same shared map — parties,
  encounters, and time are synced by the campaign server.
- **Battles:** when a player starts a battle, they auto-connect to a
  battle server. Everyone else can press **B** on the campaign map to
  open the battle chooser and join any open battle. You fight one life
  with your campaign character and gear, then return to the campaign —
  casualties and XP are applied to your party when you rejoin.
- **Local fights:** small fights and some sieges run locally on your
  client like singleplayer, and report the result back to the server.
- **Screens:** character, inventory, party, and trade screens work
  normally; your edits sync to the server when the screen closes.

## Two clients on one PC (testing)

Run `coop_client2.bat` for a second client with its own separate config
profile. Combined with `coop_launch_all.bat` you can test multiplayer
alone on one machine.

## Troubleshooting

| Problem | Likely cause / fix |
|---------|--------------------|
| Campaign server not in the server list | `HostIP` wrong in `coop.ini`, or host firewall blocking UDP 7240 |
| Clicking a battle bounces you to the MP menu | `HostIP` still `127.0.0.1` on a client — set it to the host's IP (Step 3) |
| Game crashes on launch | You launched `mb_warband.exe`, or replaced/updated `mb_warband_wse2.exe` — the mod only works with the exact shipped engine build |
| "Invalid Quick String ID" | Mixed module files — delete `Modules\NativeCoop` and re-extract the zip |
| B key does nothing on the campaign map | No battle is currently open, or you haven't fully joined the campaign server yet |
| Battles never become available | No battle server running on the host — start at least one `coop_battle_server_<n>.bat` |

Still stuck? Open an issue with your setup (slot count, client count,
LAN or internet) and the host's `warband_coop_host.log` from the game
root — see `CONTRIBUTING.md` for what to include.
