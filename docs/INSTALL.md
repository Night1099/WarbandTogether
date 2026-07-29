# Install Guide

> **⚠️ Disclaimer** this is **not a fully playable mod yet**. The
> core coop loops below work in testing, but do not expect a full campaign
> playthrough — campaign is not persisitent yet
> some siege and economy behavior diverges from singleplayer, and longer
> sessions will hit bugs and desyncs. Grab the current build from the
> [Releases page](https://github.com/Night1099/WarbandTogether/releases)
> and report what breaks via Issues.

How to get playing, from a clean Warband install. Building from source is
a different document (`docs/BUILD.md`) — this one covers the
[release zip](https://github.com/Night1099/WarbandTogether/releases).

**You need:** Mount & Blade: Warband (Steam, v1.174), Windows 10 or
later, and the release zip. The zip contains everything else — do **not**
install WSE2 yourself.

One person **hosts** (runs the servers in the background); everyone,
host included, also plays on a normal game client. Hosting and playing on
the same PC is fine.

---

## Step 1 — Install the mod

1. Install Warband from Steam, launch it once, and quit.
2. Steam → right-click Warband → Manage → **Browse local files**.
3. Extract the release zip **directly into the Warband folder next to the game exe**.
4. In that folder, rename **`coop.ini.example`** to **`coop.ini`**.
   *(Only on a first install. When you upgrade later, keep the `coop.ini`
   you already configured.)*

Everyone does Step 1

---

## Step 2 — Pick how you'll connect

| | Use this if | Router setup? |
|---|---|---|
| **A. Steam** *(recommended)* | Playing with friends over the internet | **None** |
| **B. LAN / direct IP** | Same house/network, or you already run a VPN like Hamachi or Tailscale

Do **A** or **B**, not both. Then continue to Step 3.

### A. Steam

**Host** — open `coop.ini` and, in the `[Steam]` section, uncomment this
line (delete the leading `;`):

```ini
SteamHost=1
```

That's it. While your game is running, your Steam friends will see a
**Join Game** button next to your name.

> ⚠️ By default **anyone** who can click that button can connect. Set a
> password (Step 4) unless you're fine with that.

**Players** — change nothing. You'll join by clicking your friend's
Join Game button in Step 5.

### B. LAN / direct IP (**Skip if using Steam**)

**Host** — ask Windows for your IP (`ipconfig` in a Command Prompt; use
the `IPv4 Address` line, e.g. `192.168.1.20`) and give it to your
friends. Leave your own `coop.ini` alone.

**Players** — open `coop.ini` and set the host's IP:

```ini
HostIP=192.168.1.20
```

host will have to open a firewall rule as well (admin powershell)
```
netsh advfirewall firewall add rule name="Warband Coop" dir=in action=allow protocol=UDP localport=7240-7267 profile=any
```

*(Playing over the internet without Steam? The host must forward UDP
ports **7240–7247** on their router. Option A avoids this entirely.)*

---

## Step 3 — Host: start the servers

From the game folder, run:

```
coop_launch_all.bat
```

This starts the campaign server, 2 battle servers, and your game client.
Want more simultaneous battles? `coop_launch_all.bat 4` (4 is the max).
Leave the black console windows open while you play.

---

## Step 4 — Optional: set a password

**Host** — in `coop.ini`, under `[Coop]`:

```ini
Password=mypassword
```

Max 47 characters. Restart the servers after changing it.

**Players** — you need it in **two** places:
1. Typed into the password box in the multiplayer browser when you join.
2. Written into your own `coop.ini` (`Password=mypassword`), or battles
   will reject you partway through the session.

---

## Step 5 — Join and play

Joiners Launch **`mb_warband_wse2.exe`** — *not* `mb_warband.exe` — and pick the
**NativeCoop** module.

**If you're using Steam (A):**

1. Make sure Steam is running **before** you start the game.
2. The Hosts game must be running too.
3. Click **Join Game** on their Steam friends list entry.
4. Wait ~5–10 seconds. A **COOP Direct** server appears in the
   multiplayer browser's **LAN** tab — join it. (If the multiplayer browser was
   already open, hit **Search**.)

The button is one-directional: *you* click Join Game on *the host*. The
host has no "invite" option to send you.

**If you're using LAN / direct IP (B):**

Multiplayer → Join a game. The server shows up automatically after lan scan — join it.

**Then, everyone:** first time in, you'll make a character. After that
your character, gear, gold and XP are saved on the host's server and
survive disconnects.

**Playing:**
- You all share one campaign map.
- Start a battle and you're taken to it automatically. Anyone else can
  press **B** on the map to see open battles and jump in.
- You get one life per battle. Casualties and XP land on your party when
  you return to the map.
- Yes the battles kcik you back to menu at end of play this will be more seamless in future but results are applied on rejoin
- Character, inventory, party and trade screens all work — changes save
  when you close the screen.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| **Clicking Join Game does nothing** | Normal — there's no on-screen message. Your game and Steam must both already be running (the invite can't launch the game). With WSE2 its possible to be running game without steam in background so make sure its on. If you're already in a server, leave it first and click again. `warband_coop.log` in the game folder says exactly what happened |
| **No server in the list** | *Steam:* wait 10 s and press Search. *LAN:* wrong `HostIP`, or the host skipped the firewall step |
| **"Unable to connect"** | A firewall **block** rule on the host — see below. Also check the host's server consoles are actually open |
| **Battles kick you to the menu** | Your `HostIP` is still `127.0.0.1` (Step 2B) |
| **Battles never start** | Host has no battle server running — use `coop_launch_all.bat` |
| **Password rejected** | Retype it in the browser's password box, and make sure the same `Password=` line is in your own `coop.ini` |
| **Crash on launch** | You ran `mb_warband.exe`, or Steam updated Warband over the modded engine — re-extract the zip |
| **"Invalid Quick String ID"** | Delete `Modules\NativeCoop` and re-extract the zip |
| **B key does nothing** | No battle is open right now |

**Clearing a firewall block rule (host).** In PowerShell as
administrator:

```powershell
Get-NetFirewallRule -Direction Inbound -Action Block -Enabled True | ForEach-Object {
  $ports = ($_ | Get-NetFirewallPortFilter).LocalPort -join ','
  $prog  = ($_ | Get-NetFirewallApplicationFilter).Program
  if ($ports -match '72[46]' -or $prog -match 'warband') { $_.DisplayName }
}
```

Then for each name it prints:

```powershell
Disable-NetFirewallRule -DisplayName "<name>"
```

---

## A note on `coop.ini`

Only three things in that file are meant for you: `HostIP`, `Password`,
and the `[Steam]` section. **Leave `[NetTuning]` alone** — deleting it
makes the connection worse.

Still stuck? Open an issue with your setup (LAN or Steam, how many
players) and the host's `warband_coop_host.log` from the game folder.
See `CONTRIBUTING.md`.
