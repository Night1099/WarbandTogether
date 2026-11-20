# v0.0.9

Release notes for WarbandTogether v0.0.9: everything committed on the
Workbench `main` since the v0.0.82 sync (`30dea55`). The maintainer has
runtime-verified everything under Added and Fixed. Code listed under
**Future release** ships in this build too, but it is not verified
yet; treat it as a preview that may not work.

## Read this first

- **Back up your character before testing captivity.** Being taken
  prisoner costs gold and items, as in singleplayer. Characters are the
  `coop char sid <id>.wsedict` files (and their `coop char bak sid
  <id>.wsedict` twins) in the campaign server's
  `WSE\NativeCoop\` folder.
- **A world saved by an older build** has not been tested with this
  one. If anything looks wrong after the update, move `sg00.sav` out of
  `Documents\Mount&Blade Warband WSE2\NativeCoop\Savegames\` and start a
  fresh world.
- **LAN joiners must set `HostIP`** to the host PC's LAN address in their
  own `coop.ini` (see Known issues). Check it with `ipconfig` on the
  host.

## Added

- **Defeat, captivity and escape** (verified 2026-10-10 to 2026-11-20).
  Losing a battle can now make you a prisoner, as in singleplayer:
  - You lose some gold and maybe items, and your troops and prisoners
    are gone.
  - Your party disappears from the map for every player while you are
    held, and the map camera follows your captor smoothly. Clicking the
    map, opening a screen or rejoining does not pull it away.
  - You escape after a while. In a castle you get native's rolls instead:
    an exchange, another night in the cell, or a ransom offer that you
    can refuse or pay.
  - **Another player can rescue you** by beating your captor, in a local
    fight or on a battle server. You are set free on the spot with your
    party, and only the captor's own troops fight.
  - Captivity survives a disconnect and rejoin.
  - The battle key (B) and entering towns do nothing while you are
    captive.
- **Party morale** (verified 2026-10-28 and 2026-11-18). Your party has
  native's morale: it drifts toward the target in the morale report
  (food variety, party size, leadership, wage debt), it survives a
  rejoin, and battle-server bots get their courage from it.
- **Food and supplies** (verified 2026-10-28 to 2026-10-31). Your party
  eats from your inventory and meat spoils, as in singleplayer, counted
  over the time you are online. A party with nothing to eat shows the red
  "Party has nothing to eat!" line and loses morale. Food amounts survive
  a rejoin, moving items around and a battle-server battle.
- **A battle nobody reaches is called off** (verified 2026-11-20). If no
  player gets onto the battle server, the battle is released after about
  a minute of play (15 game hours): the enemy party moves on, the battle
  server slot is freed for the next battle, and the initiator gets a
  message. A battle that started is never released, however long it
  runs.
- **The weekly budget report opens on payday** (verified 2026-11-20), as
  in singleplayer, with the week before the payment: earlier debts, your
  gold before paying, and the wages the server charged.

## Fixed

- **New characters start with their background's kit** (verified
  2026-10-10 and 2026-10-28). A new character gets native's starting gold
  and items for the chosen background, equipped, and no free troops,
  companion or gold. Two players no longer share the same starting
  companion.
- **A new character starts from a clean troop** (`2e69a24`; verified
  2026-10-27). A player slot reused by a new character no longer keeps the
  previous player's skills, proficiencies, experience or renown.
- **Recruited volunteers were added twice** (`6baddb8`; verified
  2026-10-27). Your client showed the recruits on top of the ones the
  server had already added.

## Changed

- `coop_client2.bat` (a developer tool that never worked from a release
  install) is no longer shipped.
- Removed an unused Lua reporter and an unused battle server ini file.

## Future release

In this build but not verified yet. Expect these to change; report what
you see.

- **The enemy party is held while you fight it** (`b685f48`). The party
  you attack no longer wanders off the map during the fight. Seen working
  for a battle-server fight in the 2026-11-20 captivity test; the local
  fight is unverified.
- **Battle servers reset the experience a slot kept from the previous
  player** (`b2bf3c3`), so a battle cannot pay leftover experience as kill
  XP.
- Everything listed under "Future release" in the v0.0.82 notes that is
  not above is still unverified.

## Known issues

### LAN joiners need the host's address in `HostIP`

The battle hop goes to the `HostIP` in the joiner's own `coop.ini`, not
to the server they joined from the list. A joiner with no `HostIP`, the
default `127.0.0.1` or a wrong address can play on the campaign map, but
every dedicated battle sends them back to the multiplayer menu. They may
then need to restart the game to rejoin. The battle is called off after
about a minute, so the enemy party is not stuck any more. Set `HostIP` to
the host PC's LAN address.

### A companion protects you from capture in a dedicated battle

A party with a companion is never taken prisoner after losing a
battle-server fight, because the battle server never wounds a hero far
enough for the defeat check. A local fight captures you as expected.
Only the player who started a battle-server fight can be captured by it.

### A captive is not listed in the captor's party

While you are held, your captor's party does not show you as a prisoner.

### Bots never flee a lost battle

Battle-server troops get their courage from party morale but never rout.

### Joining a dedicated battle on a passworded server

With `Password=` set in `coop.ini`, every player must also put the same
password in their own `coop.ini`, or the hop to a dedicated battle drops
them to the multiplayer server list.

### Closing the inventory as food spoils

Closing the inventory window at the moment meat spoils can undo that
spoiling.

### Carried over from v0.0.82

Village elders' gold does not rise when you sell to them, mayors keep
offering the caravan escort, and enemy towns still look neutral on the
map after a war starts (they still refuse you).
