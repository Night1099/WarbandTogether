# Install Guide

> **Early Alpha:** WarbandTogether is still under active development and isn't ready for a full campaign playthrough yet — longer sessions can hit bugs or desyncs. Grab the latest build from the [Releases page](https://github.com/Night1099/WarbandTogether/releases) and report issues on GitHub.

This guide covers installing from the [release zip](https://github.com/Night1099/WarbandTogether/releases) on a clean Warband install. (To compile from source instead, see `docs/BUILD.md`.)

### What You Need
- **Mount & Blade: Warband** (Steam, v1.174) on Windows 10 or later
- The latest **WarbandTogether release zip** — it already includes the patched WSE2 engine, so **do not install or update WSE2 separately**

One player **hosts** (runs the campaign and battle servers in the background). Everyone — including the host — plays using the game client. Hosting and playing on the same PC works fine.

---

## Step 1 — Install the Mod (Everyone)

1. Install Warband from Steam, launch it once, and close it.
2. In Steam, right-click Warband → **Manage** → **Browse local files**.
3. Extract the release zip **directly into that Warband folder** (next to `mb_warband.exe`).
   - *Upgrading from an older release?* Just extract over your existing folder — the zip ships `coop.ini.example`, so your `coop.ini` won't be overwritten.

> **Joining a friend over Steam?** You're already done with configuration — skip straight to **Step 5** (unless the host set a password in **Step 4**).

---

## Step 2 — Choose How You'll Connect

| Method | Best for | Router / port setup? |
|---|---|---|
| **A. Steam** *(recommended)* | Playing with friends over the internet | **None** |
| **B. LAN / Direct IP** | Same home network, or a VPN like Tailscale / Hamachi | Firewall rule (and port forwarding if over the internet) |

Follow **either A or B**, then continue to Step 3.

### Option A — Steam *(recommended)*

- **Host only:**
  1. Rename `coop.ini.example` to `coop.ini` *(first install only — keep your existing `coop.ini` when updating)*.
  2. Open `coop.ini`, find the `[Steam]` section, and uncomment `SteamHost=1` (remove the leading `;`):
     ```ini
     SteamHost=1
     ```
  3. While your game is running, Steam friends will see a **Join Game** button on your profile, and you can right-click friends → **Invite to Game**.

  > **Security note:** By default, anyone who can click **Join Game** can connect. Set a password (Step 4) or list allowed players under `AllowedSteamIDs` in `coop.ini` if you want to restrict access.

- **Joining players:** Don't edit `coop.ini`. Jump to **Step 5** (or **Step 4** if the host set a password).

### Option B — LAN / Direct IP *(skip if using Steam)*

- **Host:**
  1. Open Command Prompt and run `ipconfig`. Note your **IPv4 Address** (for example, `192.168.1.20`) and share it with your friends. Leave your own `coop.ini` untouched.
  2. Open UDP ports `7240–7247` in Windows Firewall by running this in an **Administrator PowerShell**:
     ```powershell
     netsh advfirewall firewall add rule name="Warband Coop" dir=in action=allow protocol=UDP localport=7240-7247 profile=any
     ```
  *(Hosting over the internet without Steam? Also forward **UDP 7240–7247** on your router — or switch to Option A to avoid port forwarding completely.)*

- **Joining players:**
  1. Rename `coop.ini.example` to `coop.ini` (if you don't already have one).
  2. Open `coop.ini` and set `HostIP` to the host's IP address:
     ```ini
     HostIP=192.168.1.20
     ```
  *(Important: leaving `HostIP` at `127.0.0.1` lets you join the campaign map, but dedicated battles will kick you back to the multiplayer menu.)*

---

## Step 3 — Start the Servers (Host Only)

From your Warband folder, run:

```bat
coop_launch_all.bat
```

This launches the campaign server, 2 battle servers, and your game client. Leave the black server console windows open while you play. *(Need more simultaneous battles? Run `coop_launch_all.bat 4` — up to 4 battle servers are supported.)*

### World Saves
- The campaign server automatically saves and reloads the shared world at:
  `Documents\Mount&Blade Warband WSE2\NativeCoop\Savegames\sg00.sav`
- Autosaves run every 20 minutes while anyone is online, and automatically when the last player disconnects.
- **Before closing the campaign server window:** Type `campaign_save` in the server console (or wait for `[WORLD SAVE] finished` after everyone leaves), otherwise progress since the last save is lost.
- **Starting a fresh world / updating to a new release:** Move or delete `sg00.sav` before launching. World saves from older mod releases may not load cleanly in newer builds.
- *(The debug launcher `coop_launch_all_debug.bat` uses its own separate save slot, `sg01.sav`.)*

---

## Step 4 — Set a Server Password *(Optional)*

- **Host:** In `coop.ini` under `[Coop]`, set a password (max 47 characters) and restart the servers:
  ```ini
  Password=mypassword
  ```
- **Joining players:** Rename `coop.ini.example` to `coop.ini` (if needed) and add the **exact same `Password=` line**.
  - With it set, Steam auto-join and dedicated battle-server hops send the password automatically.
  - Without it, Steam invites stop at the multiplayer browser (where you can type the password manually), and joining a dedicated battle will kick you back to the server list.
  - *Known issue:* On a passworded server, joiners can occasionally still fail the hop to a battle server even with `Password=` set. If that happens, leave `Password=` blank for now.

---

## Step 5 — Join and Play

Launch **`mb_warband_wse2.exe`** (not `mb_warband.exe`) and select the **NativeCoop** module. *(The host's client is already launched by `coop_launch_all.bat`.)*

### Joining via Steam (Option A)
1. Make sure **Steam is running** before you launch the game, and that the host's game is running.
2. Click **Join Game** on the host (or any friend already in the session) in your Steam friends list — or accept an **Invite to Game**.
3. Wait ~5–10 seconds: the game will automatically open the multiplayer browser and connect with zero clicks.
   - *If you're in a singleplayer battle*, auto-join waits until you leave the mission.
   - *If the server has a password and you didn't put it in `coop.ini`*, you'll land in the browser — select the **COOP Direct** row and enter the password manually.

*(Steam invites work both ways and chain through any player in the session. One Steam quirk: players already in the same session won't see Join/Invite buttons for each other, only for friends outside the session.)*

### Joining via LAN / Direct IP (Option B)
Go to **Multiplayer → Join a Game**. The campaign server appears automatically on the LAN list — click it to join.

---

## How Co-op Gameplay Works

- **Persistent Characters:** On your first join you'll create a character. Your character, stats, equipment, gold, XP, and party save on the host server across disconnects.
- **Shared Map & Battles:** Everyone plays on one live campaign map. Starting a battle moves you into it automatically; other players can press **B** on the map to see open battles and jump in.
- **One Life & Battle Transitions:** You get one life per battle. When a battle ends, the game briefly returns through the menu/rejoin flow and applies your casualties, prisoners, and XP automatically once you're back on the map.
- **Screens & Trading:** Character, inventory, party, and trade screens save when you close them.
- **Towns, Villages, Castles & Taverns:** Walk around scenes, visit the lord's hall, hire mercenaries in taverns, trade face-to-face with merchants, and take quests from guild masters and village elders. Leaving a visit automatically reconnects you to the campaign map.
  - *Verified quests:* Escort Caravan, Move Cattle Herd, Deliver Wine, Deal with Looters, Rescue Kidnapped Girl (ransom), and Deal with Night Bandits. Other quests are in-progress (see the release notes).

---

## Troubleshooting

| Problem | Fix |
|---|---|
| **Clicking Join Game / accepting an invite does nothing** | Both **Steam** and **`mb_warband_wse2.exe`** must already be running (Steam invites won't launch the game, and WSE2 can run without Steam open). If you're already on a server, disconnect first and retry. Check `warband_coop.log` in the game folder for the exact reason. |
| **No server shows up in the list** | **Steam:** wait 10 seconds and click **Search**. **LAN:** check `HostIP` in your `coop.ini`, and make sure the host added the Windows Firewall rule (Step 2B). |
| **"Unable to connect"** | Confirm the host's server console windows are open, and check for a Windows Firewall **block** rule on the host (see below). |
| **Dedicated battles kick you back to the menu** | Your `HostIP` in `coop.ini` is missing, wrong, or still set to `127.0.0.1` (Step 2B). |
| **Battles never start** | No battle servers are running on the host — launch with `coop_launch_all.bat`. |
| **Password rejected / invite stops at browser** | Add the host's exact `Password=` line to your own `coop.ini`, or type it into the multiplayer browser's password box. |
| **Crash on launch** | You launched `mb_warband.exe` instead of `mb_warband_wse2.exe`, or Steam verified/overwrote the modded files — re-extract the release zip. |
| **"Invalid Quick String ID" error** | Delete `Modules\NativeCoop\` and re-extract the release zip cleanly. |
| **Pressing `B` does nothing** | No dedicated battle is currently open (or you're currently a prisoner). |
| **Character reset after updating from v0.0.6 or older** | Steam players' characters are now tied to their Steam account ID instead of display name, so your first join creates a fresh character. Your old name-keyed file is still on disk, just no longer loaded. |

### Removing a Windows Firewall Block Rule (Host)

If joiners can see the server but get **"Unable to connect"**, Windows Firewall may have saved an inbound block rule. Run this in an **Administrator PowerShell** on the host to list suspect rules:

```powershell
Get-NetFirewallRule -Direction Inbound -Action Block -Enabled True | ForEach-Object {
  $ports = ($_ | Get-NetFirewallPortFilter).LocalPort -join ','
  $prog  = ($_ | Get-NetFirewallApplicationFilter).Program
  if ($ports -match '72[46]' -or $prog -match 'warband') { $_.DisplayName }
}
```

Then disable each rule name it prints:

```powershell
Disable-NetFirewallRule -DisplayName "<rule name>"
```

---

## About `coop.ini`

You only ever need to edit three things in `coop.ini`: `HostIP`, `Password`, and the `[Steam]` section (and Steam joiners on unpassworded servers don't need to touch `coop.ini` at all). **Leave `[NetTuning]` alone** — removing or changing it degrades connection quality.

Still stuck? Open an issue on GitHub with your setup (Steam or LAN, player count) and attach the host's `warband_coop_host.log` from the game folder. See `CONTRIBUTING.md`.
